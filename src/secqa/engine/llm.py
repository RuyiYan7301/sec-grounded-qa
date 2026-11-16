"""Model calls for the v0.2 engine, with the same options as v0.1 and per-call accounting.

Options (docs/engine-v0.2-decisions.md): qwen3:8b through Ollama /api/chat, think false, temperature 0,
num_ctx 16384, no automatic model switch. Every call is recorded with its role, latency and the token
counts Ollama reports.
"""
import json
import re
import time

import requests

from .. import config

OPTIONS = {"temperature": 0, "num_ctx": 16384}


class OllamaUnavailable(RuntimeError):
    pass


class CallLog:
    """Model calls of one item: role, latency, tokens."""

    def __init__(self):
        self.calls = []

    def add(self, role, seconds, data):
        self.calls.append({"role": role, "seconds": round(seconds, 3),
                           "prompt_tokens": data.get("prompt_eval_count"), "output_tokens": data.get("eval_count")})

    def summary(self):
        return {"model_calls": len(self.calls), "seconds": round(sum(c["seconds"] for c in self.calls), 3),
                "by_role": [c["role"] for c in self.calls]}


def strip_think(text):
    """Remove reasoning blocks some builds emit despite think=false (as v0.1 does)."""
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S)
    return text.split("</think>")[-1].strip()


def chat(messages, role, log, model=None, fmt=None, post=requests.post):
    """One model call. `fmt` is an Ollama structured-output format (a JSON schema) or None.
    `post` is injectable so tests never reach a model."""
    model = model or config.DEFAULT_MODEL
    body = {"model": model, "messages": messages, "stream": False, "think": False, "options": dict(OPTIONS)}
    if fmt is not None:
        body["format"] = fmt
    t0 = time.perf_counter()
    try:
        r = post(f"{config.OLLAMA_HOST}/api/chat", json=body, timeout=900)
    except requests.ConnectionError as e:
        raise OllamaUnavailable(f"Cannot reach Ollama at {config.OLLAMA_HOST}. Start it with `ollama serve`.") from e
    if getattr(r, "status_code", 200) == 404:
        raise OllamaUnavailable(f"Ollama has no model {model!r}. Pull it with `ollama pull {model}`.")
    r.raise_for_status()
    data = r.json()
    log.add(role, time.perf_counter() - t0, data)
    return strip_think(data.get("message", {}).get("content", ""))


def parse_json(text):
    """The first JSON object in a model reply, or None."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        m = re.search(r"\{.*\}", text or "", flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None
