"""The typed engine behind `secqa ask` and the web demo, and the router in front of it. No model is called:
every engine call goes through an injected `post` that returns scripted replies."""
import json

import pytest

from secqa import response, typed_answer
from secqa.engine import router


class Reply:
    status_code = 200

    def __init__(self, content):
        self.content = content

    def raise_for_status(self):
        pass

    def json(self):
        return {"message": {"content": self.content}, "prompt_eval_count": 10, "eval_count": 5}


def scripted(*contents):
    queue = list(contents)
    seen = []

    def post(url, json, timeout):
        seen.append(json)
        return Reply(queue.pop(0))
    post.seen = seen
    return post


def test_router_sends_questions_without_a_covered_company_to_the_agent_without_a_model_call():
    post = scripted()
    r = router.route("What was their revenue in 2024?", post=post)
    assert r["route"] == "agent" and post.seen == []


@pytest.mark.parametrize("reply,expected", [('{"route": "narrative", "reason": "risk factors"}', "agent"),
                                            ('{"route": "numeric", "reason": "a figure"}', "typed"),
                                            ("not json", "typed")])
def test_router_reads_the_model_reply(reply, expected):
    assert router.route("What does Nvidia say about export controls?", post=scripted(reply))["route"] == expected


@pytest.mark.data
def test_typed_answer_has_facts_from_evidence_and_is_verified():
    plan = {"intent": "fact_lookup", "metric": "revenue", "companies": ["NVDA"], "periods": ["FY2024"]}
    post = scripted(json.dumps(plan), "Nvidia's revenue in fiscal 2024 was $60,922 million.")
    a = typed_answer.ask("What was Nvidia's revenue in fiscal 2024?", post=post)
    assert a.mode == "typed" and a.status == "verified" and a.grounded
    assert a.facts[0].ticker == "NVDA" and a.facts[0].concept == "Revenues" and a.facts[0].value == 60922000000
    assert a.facts[0].url.endswith("-index.htm")
    assert [t.tool for t in a.tool_calls] == ["plan", "execute", "render"] and a.llm_calls == 2


@pytest.mark.data
def test_a_renderer_number_with_no_evidence_is_flagged():
    plan = {"intent": "fact_lookup", "metric": "revenue", "companies": ["NVDA"], "periods": ["FY2024"]}
    post = scripted(json.dumps(plan), "Nvidia's revenue in fiscal 2024 was $61,500 million.")
    a = typed_answer.ask("What was Nvidia's revenue in fiscal 2024?", post=post)
    assert a.status == "unverified" and a.ungrounded_numbers and "not traced" in a.checks[0]


@pytest.mark.data
def test_a_refusal_plan_gives_no_figure():
    post = scripted(json.dumps({"refuse": "unsupported", "reason": "investment advice"}),
                    "I can't give investment advice; the filings report figures, not recommendations.")
    a = typed_answer.ask("Should I buy Nvidia stock?", post=post)
    assert a.status == "verified" and a.facts == [] and a.tool_calls[1].summary.startswith("outcome unsupported")


def test_untraced_numbers_accepts_millions_billions_and_changes():
    ex = {"evidence": [{"value": 60922000000}, {"value": 130497000000}],
          "result": {"absolute_change": 69575000000, "percent_change": 114.2034}}
    ok = "Revenue rose from $60,922 million to $130.497 billion, up $69,575 million or 114.2%."
    assert typed_answer.untraced_numbers(ok, ex) == []
    assert typed_answer.untraced_numbers("Revenue was $70,000 million.", ex) == ["$70,000 million"]


def test_engine_choice_is_validated_by_the_cli():
    from secqa import cli
    with pytest.raises(SystemExit):
        cli.main(["ask", "x", "--engine", "nope"])
    assert response.ENGINES == ("auto", "typed", "agent")
