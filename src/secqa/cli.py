"""Command-line interface.

    secqa doctor                      check Python packages, data, Ollama and the model
    secqa setup                       download SEC data and build the search index
    secqa ask "question" [--company AAPL] [--fy FY2024] [--mode verify|single] [--json] [--trace]
    secqa ask --example 2             run one of the built-in demo questions
    secqa examples                    list the demo questions
    secqa app                         start the Gradio web demo
    secqa eval / report / gen-questions / verify-gold    evaluation (see README)
    secqa ontology                    metric ontology checks and coverage
"""
import argparse
import importlib.util
import json
import platform
import sys

import requests

from . import __version__, config

EXAMPLES = [
    ("Fiscal calendar", "What was Nvidia's total revenue in fiscal 2024?"),
    ("Period mismatch", "Compare Apple's and Nvidia's operating income for fiscal 2024."),
    ("Restatement", "What was AMD's selling, general and administrative expense in fiscal 2024?"),
    ("Ambiguous year", "What was Apple's revenue in 2024?"),
    ("Narrative with citations", "How does Nvidia describe export controls as a risk in its fiscal 2025 10-K?"),
    ("Out of range", "What was Microsoft's net income in fiscal 2021?"),
    ("No advice", "Is Intel a safe investment right now?"),
]

OK, WARN, FAIL = "ok  ", "warn", "FAIL"


# ---------------------------------------------------------------- doctor

def ollama_models():
    r = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=5)
    r.raise_for_status()
    return [m["name"] for m in r.json().get("models", [])]


def model_available(model, models):
    want = model if ":" in model else model + ":latest"
    return want in models


def data_status():
    from .edgar import FILERS
    raw = config.RAW
    facts = [t for t in FILERS if (raw / f"companyfacts_{t}.json").exists() and (raw / f"submissions_{t}.json").exists()]
    texts = sorted((raw / "filings").glob("*_FY*.txt")) if (raw / "filings").exists() else []
    index = (raw / "index" / "emb.npy").exists() and (raw / "index" / "chunks.json").exists()
    return {"filers": len(facts), "of": len(FILERS), "filings": len(texts), "index": index}


def doctor(model=None, out=print):
    """Print a readiness report; return True when questions can be answered."""
    model = model or config.DEFAULT_MODEL
    rows, ready = [], True

    def row(state, what, detail=""):
        nonlocal ready
        ready = ready and state != FAIL
        rows.append(f"[{state}] {what}" + (f": {detail}" if detail else ""))

    v = sys.version_info
    row(OK if v >= (3, 10) else FAIL, "Python", platform.python_version())
    for mod, pkg, required in (("requests", "requests", True), ("bs4", "beautifulsoup4", True), ("lxml", "lxml", True),
                               ("numpy", "numpy", True), ("sentence_transformers", "sentence-transformers", True),
                               ("gradio", "gradio (web demo only)", False)):
        found = importlib.util.find_spec(mod) is not None
        row(OK if found else (FAIL if required else WARN), f"package {pkg}", "" if found else "not installed")
    ua = config.user_agent()
    row(OK if ua else WARN, "SEC_USER_AGENT", "set" if ua else "not set (needed only for `secqa setup`)")
    d = data_status()
    row(OK if d["filers"] == d["of"] else FAIL, "XBRL facts", f"{d['filers']}/{d['of']} filers in {config.RAW}")
    row(OK if d["filings"] >= 24 else FAIL, "10-K text", f"{d['filings']}/24 filings")
    row(OK if d["index"] else FAIL, "search index", "built" if d["index"] else "missing")
    try:
        models = ollama_models()
        row(OK, "Ollama", config.OLLAMA_HOST)
        row(OK if model_available(model, models) else FAIL, f"model {model}",
            "available" if model_available(model, models) else f"not pulled (run `ollama pull {model}`)")
    except requests.RequestException:
        row(FAIL, "Ollama", f"not reachable at {config.OLLAMA_HOST} (install from https://ollama.com, then `ollama serve`)")
    for r in rows:
        out(r)
    if d["filers"] < d["of"] or d["filings"] < 24 or not d["index"]:
        out("\nData is missing: run `secqa setup`.")
    out("\nReady." if ready else "\nNot ready: fix the FAIL lines above.")
    return ready


# ---------------------------------------------------------------- printing

def render(a, trace=False):
    lines = [a.answer, "", f"Status: {a.status_label} - {a.status_text}"]
    if a.warnings:
        lines.append("\nWarnings:")
        for w in a.warnings:
            said = {True: " (mentioned in the answer)", False: " (NOT mentioned in the answer)"}.get(w["mentioned_in_answer"], "")
            lines.append(f"  ! [{w['code']}]{said} {w['message']}")
    if a.facts:
        lines.append("\nXBRL facts used:")
        for f in a.facts:
            lines.append(f"  - {f.ticker} {f.concept} {f.period}: {f.display} (period ends {f.period_end})")
            lines.append(f"    {f.provenance}")
            lines.append(f"    {f.accession}  {f.url}")
    if a.sources:
        lines.append("\nFiling passages retrieved:")
        for s in a.sources:
            lines.append(f"  - {s.citation}")
    if a.checks:
        lines.append("\nCheck results:")
        lines += [f"  x {c}" for c in a.checks]
    if trace:
        lines.append("\nTool calls:")
        for i, t in enumerate(a.tool_calls, 1):
            lines.append(f"  {i}. {t.tool}({json.dumps(t.args)})")
            lines.append(f"     -> {t.summary}")
    kind = "typed engine" if a.mode == "typed" else f"{a.mode} mode"
    lines.append(f"\n{kind}, {a.model}, {a.latency_s}s, {a.llm_calls} model calls, {a.tokens:,} tokens")
    return "\n".join(lines)


# ---------------------------------------------------------------- commands

def cmd_ask(args):
    from . import agent, guards, response
    from .engine import llm as engine_llm
    if args.example:
        if not 1 <= args.example <= len(EXAMPLES):
            print(f"--example must be 1-{len(EXAMPLES)}; see `secqa examples`.", file=sys.stderr)
            return 2
        question = EXAMPLES[args.example - 1][1]
    else:
        question = " ".join(args.question)
    try:
        a = response.ask(question, company=args.company, fiscal_year=args.fy, model=args.model, mode=args.mode,
                         engine=args.engine)
    except guards.InputError as e:
        print(f"Input error: {e}", file=sys.stderr)
        return 2
    except (agent.OllamaUnavailable, engine_llm.OllamaUnavailable, FileNotFoundError) as e:
        print(f"Not ready: {e}\nRun `secqa doctor` for details.", file=sys.stderr)
        return 3
    print(a.to_json() if args.json else render(a, trace=args.trace))
    return 0


def cmd_setup(args):
    from . import edgar, filings, retrieval
    try:
        print("1/3 XBRL company facts and filing lists")
        edgar.download_all(refresh=args.refresh)
        print("\n2/3 10-K text (24 filings), split into Item 1A and Item 7")
        filings.download_all()
        print("\n3/3 search index (downloads the embedding model on first run)")
        chunks, emb = retrieval.build()
        print(f"{len(chunks):,} chunks, embeddings {emb.shape}")
    except edgar.MissingUserAgent as e:
        print(f"Setup stopped: {e}\nCopy .env.example to .env and set SEC_USER_AGENT.", file=sys.stderr)
        return 3
    print()
    return 0 if doctor(args.model) else 3


def cmd_eval(args):
    from .evaluation import run_eval
    run_eval.main(args.model or config.DEFAULT_MODEL, args.mode, only=args.ids or None, gold=args.gold, tag=args.tag)
    return 0


def cmd_report(args):
    from .evaluation import report
    return 0 if report.main(args.gold, args.tag) else 1


def cmd_web(args):
    if importlib.util.find_spec("fastapi") is None or importlib.util.find_spec("uvicorn") is None:
        print('The web app needs FastAPI: pip install -e ".[web]"', file=sys.stderr)
        return 3
    from . import web
    web.launch(port=args.port, host=args.host)
    return 0


def cmd_fetch_facts(args):
    """XBRL company facts and filing lists only (no 10-K text, no index): enough for the public demo."""
    from . import edgar
    try:
        edgar.download_all()
    except edgar.MissingUserAgent as e:
        print(f"Stopped: {e}", file=sys.stderr)
        return 3
    return 0


def cmd_export_static(args):
    from . import demo
    demo.export_static(args.out)
    return 0


def cmd_demo_build(args):
    from . import demo
    demo.build(args.model)
    return 0


def cmd_app(args):
    if importlib.util.find_spec("gradio") is None:
        print('The web demo needs Gradio: pip install -e ".[demo]"', file=sys.stderr)
        return 3
    from . import app
    app.launch(port=args.port, share=False)
    return 0


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(prog="secqa", description="Auditable question answering over SEC 10-K filings.")
    p.add_argument("--version", action="version", version=f"secqa {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("ask", help="answer one question")
    s.add_argument("question", nargs="*")
    s.add_argument("--company", help="ticker or name, e.g. NVDA")
    s.add_argument("--fy", help="fiscal year, e.g. FY2024")
    s.add_argument("--model", help=f"Ollama model (default {config.DEFAULT_MODEL})")
    s.add_argument("--mode", choices=["verify", "single"], default="verify",
                   help="verify: check the draft and revise or withhold it (default); single: one pass")
    s.add_argument("--engine", choices=["auto", "typed", "agent"], default="auto",
                   help="auto (default): figures go to the typed engine, filing-text questions to the agent; "
                        "typed: v0.2 plan + deterministic execution; agent: v0.1 tool-calling agent (uses --mode)")
    s.add_argument("--example", type=int, help="run demo question N (see `secqa examples`)")
    s.add_argument("--json", action="store_true", help="print the structured answer as JSON")
    s.add_argument("--trace", action="store_true", help="also print every tool call")
    s.set_defaults(fn=cmd_ask)

    s = sub.add_parser("examples", help="list the demo questions")
    s.set_defaults(fn=lambda a: print("\n".join(f"{i}. [{k}] {q}" for i, (k, q) in enumerate(EXAMPLES, 1))) or 0)

    s = sub.add_parser("doctor", help="check that everything needed is in place")
    s.add_argument("--model")
    s.set_defaults(fn=lambda a: 0 if doctor(a.model) else 3)

    s = sub.add_parser("setup", help="download SEC data and build the index")
    s.add_argument("--refresh", action="store_true", help="download again even if cached")
    s.add_argument("--model")
    s.set_defaults(fn=cmd_setup)

    s = sub.add_parser("web", help="start the web app (FastAPI + the built front end in web/)")
    s.add_argument("--port", type=int, default=7860)
    s.add_argument("--host", default="127.0.0.1")
    s.set_defaults(fn=cmd_web)

    s = sub.add_parser("fetch-facts", help="download only the XBRL facts and filing lists (what the public demo needs)")
    s.set_defaults(fn=cmd_fetch_facts)

    s = sub.add_parser("export-static", help="write the public demo's data as static JSON (for a static host)")
    s.add_argument("out", nargs="?", default=str(config.REPO_ROOT / "web" / "dist"))
    s.set_defaults(fn=cmd_export_static)

    s = sub.add_parser("demo-build", help="precompute the public demo's answers and copy Item 1A results to data/demo/")
    s.add_argument("--model")
    s.set_defaults(fn=cmd_demo_build)

    s = sub.add_parser("app", help="start the Gradio demo")
    s.add_argument("--port", type=int, default=7860)
    s.set_defaults(fn=cmd_app)

    s = sub.add_parser("eval", help="run an evaluation set through one model and mode")
    s.add_argument("--gold", default="test", help="test (96 held-out queries), dev (28), or a path")
    s.add_argument("--mode", choices=["verify", "single"], default="verify")
    s.add_argument("--model")
    s.add_argument("--tag", default="", help="run label used in the result file name")
    s.add_argument("--ids", type=int, nargs="*", help="only these query ids")
    s.set_defaults(fn=cmd_eval)

    s = sub.add_parser("report", help="table of saved evaluation runs")
    s.add_argument("--gold", default="test")
    s.add_argument("--tag", default="t2")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("gen-questions", help="regenerate the test set from the fact store")
    s.set_defaults(fn=lambda a: __import__("secqa.evaluation.gen_questions", fromlist=["x"]).main() and 0)

    s = sub.add_parser("verify-gold", help="check test-set gold values against the 10-K text")
    s.add_argument("--sample", type=int, default=20)
    s.set_defaults(fn=lambda a: __import__("secqa.evaluation.verify_gold", fromlist=["x"]).main(a.sample) or 0)

    s = sub.add_parser("ontology", help="check the metric ontology and show which metrics each filer reports")
    s.add_argument("--validate-only", action="store_true", help="structure and hash only; no downloaded data needed")
    s.set_defaults(fn=lambda a: 0 if __import__("secqa.ontology", fromlist=["x"]).report(validate_only=a.validate_only) else 1)

    s = sub.add_parser("diff", help="v0.2 change packet for one target 10-K (as of that filing)")
    s.add_argument("ticker")
    s.add_argument("--from", dest="from_fy", required=True, help="earlier fiscal year, e.g. FY2023")
    s.add_argument("--to", dest="to_fy", required=True, help="target fiscal year, e.g. FY2024")
    s.add_argument("--out", help="write the packet to this JSON file")
    s.add_argument("--no-item1a", action="store_true", help="numeric and revision items only (no model calls)")
    s.add_argument("--item1a-method", choices=["v0.3", "v0.2"], default="v0.3",
                   help="Item 1A classifier: v0.3 (default; word diff, small edits skip the model) or the v0.2 one")
    s.set_defaults(fn=lambda a: __import__("secqa.engine.diff", fromlist=["x"]).main(a))

    args = p.parse_args(argv)
    if args.cmd == "ask" and not args.question and not args.example:
        p.error("ask needs a question or --example N")
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
