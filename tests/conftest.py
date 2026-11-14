"""Shared test setup. Tests run offline: no EDGAR, no Ollama, no embedding model.

Data comes from tests/fixtures/data (a trimmed copy of real EDGAR responses, see
make_fixtures.py). The model is replaced by FakeChat, which plays back a script.
"""
import json
import os
from pathlib import Path

FIXTURE_DATA = Path(__file__).parent / "fixtures" / "data"
os.environ["SECQA_DATA_DIR"] = str(FIXTURE_DATA)   # before secqa.config is imported
os.environ.setdefault("SECQA_SNAPSHOT", "2026-10-16")

import pytest  # noqa: E402

from secqa import agent, tools  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_store():
    tools._store = None
    yield
    tools._store = None


def call(name, **args):
    return {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": name, "arguments": args}}]}


def say(text):
    return {"role": "assistant", "content": text}


class FakeChat:
    """Stands in for agent._chat. `script` is the list of replies to tool-enabled calls, in order;
    `judge` answers the JSON judge calls (concept and support checks)."""

    def __init__(self, script, judge=None):
        self.script = list(script)
        self.judge = judge or (lambda prompt: {"facts": [], "passages_address_question": True, "unsupported_claims": []})
        self.calls = []

    def __call__(self, model, msgs, sess, tools_on=True, fmt=None):
        sess["llm_calls"] += 1
        self.calls.append({"tools_on": tools_on, "fmt": fmt, "last": msgs[-1], "msgs": list(msgs)})
        if fmt == "json":
            return {"role": "assistant", "content": json.dumps(self.judge(msgs[-1]["content"]))}
        if not self.script:
            raise AssertionError("FakeChat script exhausted")
        return self.script.pop(0)


@pytest.fixture
def fake_chat(monkeypatch):
    def install(script, judge=None):
        fc = FakeChat(script, judge)
        monkeypatch.setattr(agent, "_chat", fc)
        return fc
    return install
