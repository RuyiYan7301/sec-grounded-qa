"""Engine planner: schema validation, the one-repair policy and what the prompts may contain.
No model is called: a fake `post` returns scripted replies."""
import json

from secqa.engine import llm, plan

GOOD = {"intent": "fact_lookup", "metric": "revenue", "companies": ["CSCO"], "periods": ["FY2024"]}


class FakePost:
    """Returns scripted replies and records every request body."""

    def __init__(self, replies):
        self.replies, self.bodies = list(replies), []

    def __call__(self, url, json=None, timeout=None):
        self.bodies.append(json)
        text = self.replies.pop(0)

        class R:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self, _t=text):
                return {"message": {"content": _t}, "prompt_eval_count": 10, "eval_count": 5}
        return R()


def test_valid_plan_first_pass():
    post = FakePost([json.dumps(GOOD)])
    log = llm.CallLog()
    r = plan.make_plan("What was Cisco's revenue in fiscal 2024?", log, post=post)
    assert r["status"] == "valid" and r["first_pass_valid"] and not r["repaired"] and r["plan"] == GOOD
    assert log.summary()["model_calls"] == 1
    body = post.bodies[0]
    assert body["options"] == {"temperature": 0, "num_ctx": 16384} and body["think"] is False
    assert body["format"] == plan.schema()


def test_one_repair_then_valid():
    post = FakePost([json.dumps({"intent": "forecast"}), json.dumps(GOOD)])
    r = plan.make_plan("q", post=post)
    assert r["status"] == "valid" and r["repaired"] and len(r["attempts"]) == 2


def test_still_invalid_after_one_repair():
    post = FakePost(["not json", json.dumps({"intent": "forecast"})])
    r = plan.make_plan("q", post=post)
    assert r["status"] == "invalid_plan" and r["plan"] is None and len(post.bodies) == 2   # exactly one repair


def test_repair_prompt_holds_only_question_plan_errors():
    post = FakePost([json.dumps({"intent": "forecast"}), json.dumps(GOOD)])
    plan.make_plan("What was Cisco's revenue in fiscal 2024?", post=post)
    repair_user = post.bodies[1]["messages"][-1]["content"]
    assert "What was Cisco's revenue in fiscal 2024?" in repair_user and "forecast" in repair_user
    assert "does not match the plan schema" in repair_user
    for word in ("gold", "score", "evidence", "accession", "value"):
        assert word not in repair_user.lower(), word


def test_system_prompt_has_no_question_or_scorer_content():
    p = plan.system_prompt()
    for word in ("gold", "scorer", "warning", "mismatch", "A-test", "A-dev"):
        assert word.lower() not in p.lower(), word
    assert "EBITDA" in p                      # from the ontology's own out-of-ontology list


def test_validate_rejects_bad_plans():
    assert plan.validate(GOOD) == []
    assert plan.validate({"refuse": "unsupported", "reason": "advice"}) == []
    assert plan.validate({**GOOD, "periods": ["2024"]})
    assert plan.validate({**GOOD, "companies": ["TSLA"]})
