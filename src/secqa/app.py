"""Gradio web demo: ask a question and see the evidence behind the answer, or compare two consecutive 10-Ks.

    secqa app            # http://127.0.0.1:7860
"""
import html
import json

import gradio as gr
import requests

from . import agent, cli, compare_view, config, guards, response
from .edgar import FILERS
from .engine import llm as engine_llm
from .facts import INDEXED_FY

COMPANIES = ["Any"] + [f"{guards.NAMES[t]} ({t})" for t in FILERS]
YEARS = ["Any"] + [f"FY{y}" for y in INDEXED_FY]
TARGET_YEARS = [f"FY{y}" for y in INDEXED_FY[1:]]
BADGE = {"verified": "#1f7a3a", "verified_with_warnings": "#2e6b4f", "traceable": "#9a6700",
         "unverified": "#b54708", "withheld": "#b42318"}
FACT_COLS = ["fact", "value", "value taken from", "provenance"]
TRACE_COLS = ["#", "tool", "arguments", "result"]
CHANGE_COLS = ["metric", "earlier year", "later year", "change", "size"]
REVISION_COLS = ["metric", "period", "first reported", "shown in the later 10-K", "status"]
SIZE = {"large_numeric_change": "large", "gray_zone": "moderate", "unchanged_control": "small"}
LABEL_1A = {"material_added": "Added", "material_removed": "Removed", "material_modified": "Modified"}

CSS = """
.gradio-container { max-width: 1180px !important; margin: 0 auto !important; }
#hero h1 { font-size: 1.9rem; margin: 0 0 .25rem; letter-spacing: -.01em; }
#hero p { margin: 0; color: var(--body-text-color-subdued); max-width: 760px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.chip { font-size: .8rem; padding: 3px 10px; border-radius: 999px; border: 1px solid var(--border-color-primary);
        color: var(--body-text-color-subdued); background: var(--block-background-fill); }
#ask-row { align-items: stretch; }
#ask-btn { min-height: 100%; }
.example-btn { font-size: .82rem !important; text-align: left !important; justify-content: flex-start !important; }
.example-label { font-size: .72rem; text-transform: uppercase; letter-spacing: .06em;
                 color: var(--body-text-color-subdued); margin: 4px 0 -4px; }
.status-card { display: flex; flex-direction: column; gap: 6px; }
.status-line { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.badge { color: #fff; border-radius: 6px; padding: 3px 10px; font-weight: 600; font-size: .85rem; letter-spacing: .02em; }
.meta { color: var(--body-text-color-subdued); font-size: .85rem; }
#answer { border: 1px solid var(--border-color-primary); border-radius: 10px; padding: 14px 18px;
          background: var(--block-background-fill); font-size: 1.05rem; line-height: 1.6; min-height: 64px; }
.callout { border-left: 4px solid #d29922; background: rgba(210,153,34,.10); border-radius: 6px;
           padding: 8px 12px; margin: 6px 0; font-size: .92rem; }
.callout.missed { border-left-color: #b42318; background: rgba(180,35,24,.08); }
.callout code { font-size: .8rem; }
.empty { color: var(--body-text-color-subdued); font-size: .92rem; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 6px 0 4px; }
.stat { border: 1px solid var(--border-color-primary); border-radius: 10px; padding: 10px 14px;
        background: var(--block-background-fill); }
.stat b { display: block; font-size: 1.5rem; line-height: 1.2; }
.stat span { color: var(--body-text-color-subdued); font-size: .82rem; }
.para { border: 1px solid var(--border-color-primary); border-radius: 8px; padding: 10px 14px; margin: 8px 0; }
.para .tag { font-size: .75rem; font-weight: 600; padding: 2px 8px; border-radius: 999px; margin-right: 6px;
             background: rgba(99,102,241,.14); color: var(--body-text-color); }
.para details { margin-top: 6px; font-size: .9rem; }
.para blockquote { margin: 6px 0; padding-left: 10px; border-left: 3px solid var(--border-color-primary);
                   color: var(--body-text-color-subdued); }
footer { display: none !important; }
"""

THEME = gr.themes.Soft(primary_hue="indigo", neutral_hue="slate",
                       font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"])


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
    how = "typed engine (plan + code)" if a.mode == "typed" else f"agent, {a.mode} mode"
    return (f'<div class="status-card"><div class="status-line">'
            f'<span class="badge" style="background:{color}">{label}</span>'
            f'<span>{html.escape(a.status_text)}</span></div>'
            f'<div class="meta">{how} · {html.escape(a.model)} · {a.latency_s}s · {a.llm_calls} model calls · '
            f'{a.tokens:,} tokens</div></div>')


def _warnings(a):
    if not a.warnings:
        return '<div class="empty">No warnings.</div>'
    out = []
    for w in a.warnings:
        missed = w["mentioned_in_answer"] is False
        note = " · <b>not mentioned in the answer</b>" if missed else " · mentioned in the answer" if w["mentioned_in_answer"] else ""
        out.append(f'<div class="callout{" missed" if missed else ""}"><code>{html.escape(w["code"])}</code>{note}<br>'
                   f'{html.escape(w["message"])}</div>')
    return "".join(out)


def _sources(a):
    if not a.sources:
        return "No filing passages were used for this answer (figures come from XBRL facts; see the first tab)."
    parts = []
    for s in a.sources:
        link = f" · [open filing]({s.url})" if s.url else ""
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


# ---------- compare two 10-Ks ----------

_fmt, _metric_value, _change, _name = compare_view.fmt, compare_view.metric_value, compare_view.change_text, compare_view.name


def _item1a_html(detail):
    if detail is None:
        return '<div class="empty">Item 1A was not compared. Tick “Include Item 1A” to run it (it calls the model; a few minutes).</div>'
    rows = [c for c in detail.get("candidates", []) if str(c.get("label", "")).startswith("material")]
    if not rows:
        return '<div class="empty">No material Item 1A changes were flagged.</div>'
    out = []
    for c in rows:
        earlier = html.escape(c.get("earlier") or "")
        later = html.escape(c.get("later") or "")
        body = ""
        if earlier:
            body += f"<b>Earlier 10-K</b><blockquote>{earlier}</blockquote>"
        if later:
            body += f"<b>Later 10-K</b><blockquote>{later}</blockquote>"
        out.append(f'<div class="para"><span class="tag">{LABEL_1A.get(c["label"], c["label"])}</span>'
                   f'{html.escape(c.get("reason") or "")}<details><summary>Show the paragraphs</summary>{body}</details></div>')
    return ('<p class="empty">Flagged by the model; about a quarter of wording-only edits are still flagged on held-out '
            'companies, so read the paragraphs before relying on a label.</p>' + "".join(out))


def compare(company, to_fy, include_item1a):
    """Packet for one target 10-K against the year before, as of that filing."""
    from . import ontology
    from .engine import diff
    blank = ([], [], "", None)
    if not company or company == "Any":
        return ("<b>Choose a company.</b>", *blank)
    ticker = company.split("(")[-1].rstrip(")")
    y2 = int(to_fy[2:])
    try:
        p, detail = diff.build_packet(ticker, y2 - 1, y2, item1a=bool(include_item1a))
    except (agent.OllamaUnavailable, engine_llm.OllamaUnavailable) as e:
        return (f"<b>Not ready.</b> {html.escape(str(e))} Untick Item 1A to see the figures without the model.", *blank)
    except (FileNotFoundError, KeyError, ValueError) as e:
        return (f"<b>Could not build the comparison.</b> {html.escape(str(e))}", *blank)
    o = ontology.load()
    f1, f2 = f"FY{y2 - 1}", f"FY{y2}"
    changes = []
    for it in sorted(p["numeric_changes"], key=lambda x: list(SIZE).index(x["status"]) if x["status"] in SIZE else 9):
        v1, u = _metric_value(it, f1, o)
        v2, u2 = _metric_value(it, f2, o)
        u = u or u2
        changes.append([_name(it["metric"], o), _fmt(v1, u), _fmt(v2, u), _change(it, u), SIZE.get(it["status"], it["status"])])
    revisions = []
    for r in sorted(p["revision_checks"], key=lambda x: x["status"] != "revised"):
        first, now = r.get("first_reported") or {}, r.get("as_presented") or {}
        u = first.get("unit") or now.get("unit")
        cause = f" ({r['cause'].replace('_', ' ')})" if r.get("cause") else ""
        status = {"stable": "unchanged", "revised": "revised" + cause}.get(r["status"], r["status"].replace("_", " ") + cause)
        revisions.append([_name(r["metric"], o), r["period"], _fmt(first.get("value"), u), _fmt(now.get("value"), u), status])
    large = sum(x["status"] == "large_numeric_change" for x in p["numeric_changes"])
    revised = sum(x["status"] == "revised" for x in p["revision_checks"])
    n1a = "—" if detail is None else str(sum(str(c.get("label", "")).startswith("material") for c in detail.get("candidates", [])))
    tf = p["target_filing"]
    summary = (f'<div class="meta">{html.escape(guards.NAMES.get(ticker, ticker))} {f2} 10-K (filed {tf["filed"]}, '
               f'accession {tf["accession"]}) against {f1}; values as shown in the later filing.</div>'
               f'<div class="stats"><div class="stat"><b>{large}</b><span>metrics changed by 10% or more '
               f'(5 pp for ratios)</span></div>'
               f'<div class="stat"><b>{revised}</b><span>{f1} figures revised since first reported</span></div>'
               f'<div class="stat"><b>{n1a}</b><span>Item 1A paragraphs flagged as material changes</span></div></div>')
    return summary, changes, revisions, _item1a_html(detail), p


def build():
    inputs_note = "auto: figures go to the typed engine (plan + code), filing-text questions to the agent"
    with gr.Blocks(title="SEC filings QA") as demo:
        gr.HTML('<div id="hero"><h1>SEC filings QA</h1>'
                '<p>Answers about the 10-Ks of eight large tech companies, with every figure traced to the XBRL fact and '
                'the filing it came from. Figures are computed by code, not by the model.</p>'
                '<div class="chips">' + "".join(f'<span class="chip">{c}</span>' for c in
                ["Apple · Microsoft · Nvidia · Oracle", "Cisco · Broadcom · Intel · AMD", "Fiscal 2023–2025",
                 "Annual GAAP figures, 28 metrics", "Local model via Ollama"]) + "</div></div>")
        with gr.Tabs():
            with gr.Tab("Ask a question"):
                with gr.Row(elem_id="ask-row"):
                    question = gr.Textbox(show_label=False, lines=2, scale=6, autofocus=True,
                                          placeholder="e.g. Compare Apple's and Nvidia's operating income for fiscal 2024.")
                    ask = gr.Button("Ask", variant="primary", scale=1, min_width=110, elem_id="ask-btn")
                gr.HTML('<div class="example-label">Try one (each shows a trap the system handles)</div>')
                example_buttons = []
                with gr.Row():
                    for label, q in cli.EXAMPLES:
                        example_buttons.append((gr.Button(f"{label}: {q}", size="sm", variant="secondary",
                                                          elem_classes="example-btn", min_width=220), q))
                with gr.Accordion("Settings", open=False):
                    with gr.Row():
                        company = gr.Dropdown(COMPANIES, value="Any", label="Company (optional)")
                        fy = gr.Dropdown(YEARS, value="Any", label="Fiscal year (optional)")
                        models = _models()
                        model = gr.Dropdown(models, value=config.DEFAULT_MODEL, label="Model", allow_custom_value=True)
                    with gr.Row():
                        engine = gr.Radio(["auto", "typed", "agent"], value="auto", label="Engine", info=inputs_note)
                        mode = gr.Radio(["verify", "single"], value="verify", label="Agent mode",
                                        info="agent only: verify checks the draft and revises or withholds it")
                status = gr.HTML()
                answer = gr.Markdown(elem_id="answer", value="*The answer will appear here.*")
                warnings = gr.HTML()
                with gr.Tabs():
                    with gr.Tab("Figures and filings"):
                        facts = gr.Dataframe(headers=FACT_COLS, datatype=["markdown", "str", "markdown", "str"],
                                             interactive=False, wrap=True, column_widths=["28%", "14%", "20%", "38%"])
                    with gr.Tab("Filing passages"):
                        sources = gr.Markdown()
                    with gr.Tab("How it was answered"):
                        trace = gr.Dataframe(headers=TRACE_COLS, interactive=False, wrap=True,
                                             column_widths=["5%", "13%", "37%", "45%"])
                        checks = gr.Markdown()
                        draft = gr.Textbox(label="Rejected draft", lines=3, interactive=False)
                    with gr.Tab("JSON"):
                        raw = gr.JSON()
                outputs = [status, answer, warnings, facts, trace, sources, checks, draft, raw]
                ins = [question, company, fy, engine, mode, model]
                ask.click(run, ins, outputs)
                question.submit(run, ins, outputs)
                for btn, q in example_buttons:
                    btn.click(lambda q=q: q, None, question).then(run, ins, outputs)

            with gr.Tab("Compare two 10-Ks"):
                gr.Markdown("What changed between a company's 10-K and the one a year earlier: every metric, any "
                            "earlier figure the later filing revised, and (optionally) the risk-factor paragraphs.")
                with gr.Row():
                    c_company = gr.Dropdown(COMPANIES[1:], value=COMPANIES[3], label="Company")
                    c_year = gr.Dropdown(TARGET_YEARS, value=TARGET_YEARS[-1], label="Later 10-K")
                    c_1a = gr.Checkbox(value=False, label="Include Item 1A (risk factors; calls the model, a few minutes)")
                    c_go = gr.Button("Compare", variant="primary", min_width=110)
                c_summary = gr.HTML()
                with gr.Tabs():
                    with gr.Tab("Figures"):
                        c_changes = gr.Dataframe(headers=CHANGE_COLS, interactive=False, wrap=True,
                                                 column_widths=["30%", "18%", "18%", "22%", "12%"])
                    with gr.Tab("Revised earlier figures"):
                        c_revisions = gr.Dataframe(headers=REVISION_COLS, interactive=False, wrap=True)
                    with gr.Tab("Risk factors (Item 1A)"):
                        c_item1a = gr.HTML()
                    with gr.Tab("JSON"):
                        c_raw = gr.JSON()
                c_go.click(compare, [c_company, c_year, c_1a], [c_summary, c_changes, c_revisions, c_item1a, c_raw])
        gr.HTML('<div class="meta" style="margin-top:18px">Data: SEC EDGAR XBRL and 10-K text, snapshot 2026-10-16. '
                'Not investment advice. Source: github.com/RuyiYan7301/sec-grounded-qa</div>')
    return demo


def launch(port=7860, share=False):
    build().queue(default_concurrency_limit=1).launch(server_port=port, share=share, theme=THEME, css=CSS)
