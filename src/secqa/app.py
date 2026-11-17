"""Gradio web demo: one question, its answer, and the evidence behind it.

    secqa app            # http://127.0.0.1:7860
"""
import html
import json

import gradio as gr
import requests

from . import agent, cli, config, guards, response
from .engine import llm as engine_llm
from .edgar import FILERS
from .facts import INDEXED_FY

COMPANIES = ["Any"] + [f"{guards.NAMES[t]} ({t})" for t in FILERS]
YEARS = ["Any"] + [f"FY{y}" for y in INDEXED_FY]
BADGE = {"verified": "#1f7a3a", "verified_with_warnings": "#2e6b4f", "traceable": "#9a6700",
         "unverified": "#b54708", "withheld": "#b42318"}
FACT_COLS = ["fact", "value", "value taken from", "provenance"]
TRACE_COLS = ["#", "tool", "arguments", "result"]


def _models():
    try:
        names = cli.ollama_models()
    except requests.RequestException:
        names = []
    return sorted(set(names) | {config.DEFAULT_MODEL})


def _filing(form, fy, filed):
    return f"{'FY' + str(fy) + ' ' if fy else ''}{form}, filed {filed}"


def _status(a):
    color, label = BADGE[a.status], a.status_label
    return (f'<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">'
            f'<span style="background:{color};color:#fff;border-radius:6px;padding:3px 10px;font-weight:600">{label}</span>'
            f'<span>{html.escape(a.status_text)}</span></div>'
            f'<div style="opacity:.7;font-size:.9em;margin-top:6px">{a.mode} {"engine" if a.mode == "typed" else "mode"} · {html.escape(a.model)} · '
            f'{a.latency_s}s · {a.llm_calls} model calls · {a.tokens:,} tokens</div>')


def _warnings(a):
    if not a.warnings:
        return "No warnings."
    said = {True: " · mentioned in the answer", False: " · **not mentioned in the answer**"}
    return "\n".join(f"- **{w['code']}**{said.get(w['mentioned_in_answer'], '')}: {w['message']}" for w in a.warnings)


def _sources(a):
    if not a.sources:
        return "No filing passages were retrieved for this answer."
    parts = []
    for s in a.sources:
        link = f" · [filing]({s.url})" if s.url else ""
        excerpt = s.excerpt if len(s.excerpt) < 1200 else s.excerpt[:1200] + " ..."
        parts.append(f"**{s.citation}**{link}\n\n> " + excerpt.replace("\n", "\n> "))
    return "\n\n---\n\n".join(parts)


def _checks(a):
    if not a.checks:
        return "All checks passed."
    head = "The draft that was rejected is not shown to the user; these are the reasons.\n\n" if a.status == "withheld" else ""
    return head + "\n".join(f"- {c}" for c in a.checks)


def run(question, company, fiscal_year, engine, mode, model):
    empty = ([], [], "", "", "", None)
    ticker = None if company == "Any" else company.split("(")[-1].rstrip(")")
    try:
        a = response.ask(question, company=ticker, fiscal_year=fiscal_year, model=model, mode=mode, engine=engine)
    except guards.InputError as e:
        return (f"<b>Input error.</b> {html.escape(str(e))}", "", "", *empty)
    except (agent.OllamaUnavailable, engine_llm.OllamaUnavailable, FileNotFoundError) as e:
        return (f"<b>Not ready.</b> {html.escape(str(e))} Run <code>secqa doctor</code> for details.", "", "", *empty)
    facts = [[f"**{f.ticker}** {f.concept}<br>{f.period}, period ends {f.period_end}",
              f.display.split(" (=")[0] + (" (earlier reported)" if f.restated else ""),
              f"[{_filing(f.form, f.filing_fiscal_year, f.filed)}]({f.url})", f.provenance] for f in a.facts]
    trace = [[i, t.tool, json.dumps(t.args, separators=(", ", ": ")), ("" if t.ok else "✗ ") + t.summary]
             for i, t in enumerate(a.tool_calls, 1)]
    return (_status(a), a.answer, _warnings(a), facts, trace, _sources(a), _checks(a),
            a.draft or "No rejected draft (typed engine, single mode, or the first draft passed).", a.to_dict())


def build():
    with gr.Blocks(title="SEC filings QA") as demo:
        gr.Markdown(
            "# SEC filings QA\n"
            "Ask about the 10-Ks of Apple, Nvidia, Microsoft, Oracle, Cisco, Broadcom, Intel and AMD (FY2023-FY2025). "
            "Figures come from XBRL through a typed plan executed by code, narrative answers from the filing text, and every answer "
            "shows the facts, passages and tool calls it was built from.")
        with gr.Row():
            with gr.Column(scale=2, min_width=320):
                question = gr.Textbox(label="Question", lines=3, placeholder="Compare Apple's and Nvidia's operating income for fiscal 2024.")
                with gr.Row():
                    company = gr.Dropdown(COMPANIES, value="Any", label="Company (optional)")
                    fy = gr.Dropdown(YEARS, value="Any", label="Fiscal year (optional)")
                engine = gr.Radio(["auto", "typed", "agent"], value="auto", label="Engine",
                                  info="auto: figures go to the typed engine (plan + code), filing-text questions to the agent")
                with gr.Row():
                    mode = gr.Radio(["verify", "single"], value="verify", label="Agent mode",
                                    info="agent only: verify checks the draft and revises or withholds it")
                    models = _models()
                    model = gr.Dropdown(models, value=config.DEFAULT_MODEL, label="Model", allow_custom_value=True)
                ask = gr.Button("Ask", variant="primary")
                gr.Examples([[q] for _, q in cli.EXAMPLES], inputs=[question], label="Examples (each shows one trap)")
            with gr.Column(scale=3, min_width=360):
                status = gr.HTML()
                answer = gr.Markdown(label="Answer")
                with gr.Accordion("Warnings", open=True):
                    warnings = gr.Markdown()
                with gr.Tabs():
                    with gr.Tab("XBRL facts"):
                        facts = gr.Dataframe(headers=FACT_COLS, datatype=["markdown", "str", "markdown", "str"],
                                             interactive=False, wrap=True, column_widths=["30%", "14%", "18%", "38%"])
                    with gr.Tab("Filing sources"):
                        sources = gr.Markdown()
                    with gr.Tab("Tool trace"):
                        trace = gr.Dataframe(headers=TRACE_COLS, interactive=False, wrap=True,
                                             column_widths=["5%", "15%", "35%", "45%"])
                    with gr.Tab("Checks"):
                        checks = gr.Markdown()
                        draft = gr.Textbox(label="First draft (verify mode)", lines=3, interactive=False)
                    with gr.Tab("JSON"):
                        raw = gr.JSON()
        outputs = [status, answer, warnings, facts, trace, sources, checks, draft, raw]
        ask.click(run, [question, company, fy, engine, mode, model], outputs)
        question.submit(run, [question, company, fy, engine, mode, model], outputs)
    return demo


def launch(port=7860, share=False):
    build().queue(default_concurrency_limit=1).launch(server_port=port, share=share)
