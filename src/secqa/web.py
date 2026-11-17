"""HTTP API and the built web front end (web/, React).

    secqa web            # http://127.0.0.1:7860  (build the front end once: cd web && npm install && npm run build)

GET  /api/meta       companies, years, examples, models
POST /api/ask        the same structured Answer the CLI and Gradio demo show, plus the answer split into segments
                     with each figure linked to the fact it matches
POST /api/compare    two consecutive 10-Ks (compare_view.build)
"""
import re

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agent, cli, compare_view, config, guards, response
from .edgar import FILERS
from .engine import llm as engine_llm
from .facts import INDEXED_FY

DIST = config.REPO_ROOT / "web" / "dist"


class AskBody(BaseModel):
    question: str
    company: str | None = None
    fiscal_year: str | None = None
    engine: str = "auto"
    mode: str = "verify"
    model: str | None = None


class CompareBody(BaseModel):
    ticker: str
    to_fy: str
    item1a: str = "cached"


def segments(answer, facts):
    """The answer as [{text, fact}] pieces: a figure that matches a fact's value (to 0.06%, in any scale) points
    to that fact's index. Only exact matches are linked; other numbers stay plain text."""
    spans = []
    for v, raw, pct in agent.numbers_in(answer):
        if pct:
            continue
        hit = next((i for i, f in enumerate(facts) if f["value"] and abs(abs(v) - abs(f["value"])) <= 0.0006 * abs(f["value"])), None)
        if hit is None:
            continue
        start = 0
        while True:
            k = answer.find(raw, start)
            if k < 0:
                break
            if not any(a <= k < b for a, b, _ in spans):
                spans.append((k, k + len(raw), hit))
                break
            start = k + 1
    spans.sort()
    out, pos = [], 0
    for a, b, i in spans:
        if a > pos:
            out.append({"text": answer[pos:a]})
        out.append({"text": answer[a:b], "fact": i})
        pos = b
    if pos < len(answer):
        out.append({"text": answer[pos:]})
    return out


def create_app():
    api = FastAPI(title="SEC filings QA", docs_url="/api/docs", openapi_url="/api/openapi.json")

    @api.get("/api/meta")
    def meta():
        try:
            models = sorted(set(cli.ollama_models()) | {config.DEFAULT_MODEL})
        except requests.RequestException:
            models = [config.DEFAULT_MODEL]
        return {"companies": [{"ticker": t, "name": guards.NAMES[t]} for t in FILERS],
                "years": [f"FY{y}" for y in INDEXED_FY], "target_years": [f"FY{y}" for y in INDEXED_FY[1:]],
                "examples": [{"label": lab, "question": q} for lab, q in cli.EXAMPLES],
                "models": models, "default_model": config.DEFAULT_MODEL, "snapshot": config.SNAPSHOT}

    @api.post("/api/ask")
    def ask(body: AskBody):
        try:
            a = response.ask(body.question, company=body.company or None, fiscal_year=body.fiscal_year or "Any",
                             model=body.model or None, mode=body.mode, engine=body.engine)
        except guards.InputError as e:
            raise HTTPException(400, str(e)) from e
        except (agent.OllamaUnavailable, engine_llm.OllamaUnavailable, FileNotFoundError) as e:
            raise HTTPException(503, f"{e} Run `secqa doctor` for details.") from e
        d = a.to_dict()
        d["segments"] = segments(a.answer, d["facts"])
        return d

    @api.post("/api/compare")
    def compare(body: CompareBody):
        t = body.ticker.upper()
        if t not in FILERS or not re.fullmatch(r"FY\d{4}", body.to_fy.upper()):
            raise HTTPException(400, "Choose one of the eight companies and FY2024 or FY2025.")
        try:
            return compare_view.build(t, body.to_fy.upper(), item1a=body.item1a)
        except (agent.OllamaUnavailable, engine_llm.OllamaUnavailable) as e:
            raise HTTPException(503, f"{e} The figures work without the model; Item 1A needs it.") from e
        except (FileNotFoundError, KeyError, ValueError) as e:
            raise HTTPException(500, f"Could not build the comparison: {e}") from e

    if (DIST / "index.html").exists():
        api.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

        @api.get("/{path:path}")
        def spa(path: str):
            f = DIST / path
            return FileResponse(f if path and f.is_file() else DIST / "index.html")
    return api


def launch(port=7860):
    import uvicorn
    if not (DIST / "index.html").exists():
        print("The front end is not built yet: cd web && npm install && npm run build  (the API still runs)")
    uvicorn.run(create_app(), host="127.0.0.1", port=port)
