"""Integration: the tool-calling loop and the verify arm, with a scripted model and real fixture data."""
from conftest import call, say

from secqa import agent, response

Q = "What was Nvidia's total revenue in fiscal 2024?"
GOOD = "Nvidia's total revenue in fiscal 2024 was $60.922 billion (10-K, accession {accn})."


def nvda_steps():
    return [call("list_concepts", ticker="NVDA", keyword="revenue"),
            call("get_fact", ticker="NVDA", tag="Revenues", period="FY2024")]


def concept_ok(prompt):
    return {"facts": [{"n": 1, "matches": True, "why": "revenue"}]}


def test_verified_answer_has_facts_and_trace(fake_chat):
    accn = agent.tools.get_fact("NVDA", "Revenues", "FY2024")["facts"][0]["accn"]
    fake_chat(nvda_steps() + [say(GOOD.format(accn=accn))], judge=concept_ok)
    a = response.ask(Q, mode="verify")
    assert a.status == "verified" and a.grounded and a.checks == []
    assert [t.tool for t in a.tool_calls] == ["list_concepts", "get_fact"]
    f = a.facts[0]
    assert (f.ticker, f.concept, f.period, f.value, f.period_end) == ("NVDA", "Revenues", "FY2024", 60_922_000_000, "2024-01-28")
    assert f.accession == accn and f.url.endswith(f"{accn}-index.htm")
    # The value comes from the latest 10-K that shows FY2024; the provenance says so.
    assert f.filing_fiscal_year == 2026 and f.first_filing_fiscal_year == 2024 and f.first_filed == "2024-02-21"
    assert "prior-year comparative" in f.provenance and "unchanged since" in f.provenance


def test_compare_values_get_the_same_filing_details(fake_chat):
    fake_chat([call("list_concepts", ticker="AAPL", keyword="operating income"),
               call("list_concepts", ticker="NVDA", keyword="operating income"),
               call("compare", tickers=["AAPL", "NVDA"], tag="OperatingIncomeLoss", period="FY2024"),
               say("Apple's FY2024 operating income was $123.216 billion and Nvidia's was $32.972 billion; "
                   "the fiscal periods do not line up.")],
              judge=lambda p: {"facts": [{"n": 1, "matches": True}, {"n": 2, "matches": True}]})
    a = response.ask("Compare Apple's and Nvidia's operating income for fiscal 2024.", mode="verify")
    assert a.status == "verified_with_warnings"
    assert [w["mentioned_in_answer"] for w in a.warnings if w["code"] == "period_mismatch"] == [True]
    for f in a.facts:
        assert f.form == "10-K" and f.filed and f.filing_fiscal_year and f.first_filed and f.provenance


def test_guessed_tag_returns_candidates_instead_of_a_value(fake_chat):
    fake_chat([call("get_fact", ticker="NVDA", tag="Revenue", period="FY2024"),
               call("get_fact", ticker="NVDA", tag="Revenues", period="FY2024"),
               say("Nvidia's total revenue in fiscal 2024 was $60.922 billion.")], judge=concept_ok)
    raw = agent.ask(Q, arm="single")
    first = raw["trace"][0]["result"]
    assert first["reason"] == "tag_not_looked_up" and "Revenues" in [c["tag"] for c in first["candidates"]["NVDA"]]
    assert raw["trace"][1]["result"]["found"]       # candidates count as looked up


def test_verify_withholds_an_answer_that_stays_ungrounded(fake_chat):
    bad = say("Nvidia's total revenue in fiscal 2024 was $61.5 billion.")
    fc = fake_chat(nvda_steps() + [bad, bad], judge=concept_ok)
    a = response.ask(Q, mode="verify")
    assert a.status == "withheld" and a.answer == agent.FALLBACK
    assert "$61.5 billion" not in a.answer                         # nothing from the rejected draft leaks
    assert any("do not appear in any get_fact/compare result" in c for c in a.checks)
    revise = [c["last"]["content"] for c in fc.calls if c["tools_on"] and "Verification of your draft" in str(c["last"].get("content"))]
    assert revise, "the model was asked to revise"


def test_verify_lets_the_model_fix_its_draft(fake_chat):
    accn = agent.tools.get_fact("NVDA", "Revenues", "FY2024")["facts"][0]["accn"]
    fake_chat(nvda_steps() + [say("It was $61.5 billion."), say(GOOD.format(accn=accn))], judge=concept_ok)
    a = response.ask(Q, mode="verify")
    assert a.status == "verified" and a.draft == "It was $61.5 billion."


def test_single_mode_returns_answer_but_marks_it_unverified(fake_chat):
    fake_chat(nvda_steps() + [say("Revenue was $61.5 billion.")], judge=concept_ok)
    a = response.ask(Q, mode="single")
    assert a.status == "unverified" and a.answer == "Revenue was $61.5 billion."
    assert any(w["code"] == "ungrounded_numbers" for w in a.warnings)


def test_concept_judge_rejection_is_reported(fake_chat):
    fake_chat([call("list_concepts", ticker="NVDA", keyword="revenue"),
               call("get_fact", ticker="NVDA", tag="Revenues", period="FY2024"),
               say("Nvidia's customer acquisition cost in fiscal 2024 was $60.922 billion.")] * 2,
              judge=lambda p: {"facts": [{"n": 1, "matches": False, "why": "revenue is not a cost"}]})
    a = response.ask("What was Nvidia's customer acquisition cost in fiscal 2024?", mode="verify")
    assert a.status == "withheld"
    assert any("does not measure what the question asks" in c for c in a.checks)


def test_bare_year_adds_a_system_hint_before_the_model_runs(fake_chat):
    fc = fake_chat([say("Do you mean fiscal 2024 (ended 2024-01-28) or calendar 2024?")])
    a = response.ask("What was Nvidia's revenue in 2024?", mode="single")
    system = [m["content"] for m in fc.calls[0]["msgs"] if m["role"] == "system"]
    assert any("fiscal 2024 ended 2024-01-28" in s for s in system)
    assert any(w["code"] == "ambiguous_year" for w in a.warnings)


def test_period_mismatch_warning_without_compare(fake_chat):
    # The model fetches each company separately and never mentions the mismatch (the 14B failure mode).
    steps = [call("list_concepts", ticker="AAPL", keyword="operating income"),
             call("list_concepts", ticker="NVDA", keyword="operating income"),
             call("get_fact", ticker="AAPL", tag="OperatingIncomeLoss", period="FY2024"),
             call("get_fact", ticker="NVDA", tag="OperatingIncomeLoss", period="FY2024")]
    fake_chat(steps + [say("Apple's FY2024 operating income was $123.216 billion and Nvidia's was $32.972 billion.")])
    a = response.ask("Compare Apple's and Nvidia's operating income for fiscal 2024.", mode="single")
    w = [x for x in a.warnings if x["code"] == "period_mismatch"]
    assert w and "AAPL ends 2024-09-28" in w[0]["message"] and "NVDA ends 2024-01-28" in w[0]["message"]
    # Every number traces, but the answer never mentions the mismatch: not VERIFIED.
    assert w[0]["mentioned_in_answer"] is False and a.status == "traceable"


def test_restatement_warning(fake_chat):
    fake_chat([call("list_concepts", ticker="AMD", keyword="selling general administrative"),
               call("get_fact", ticker="AMD", tag="SellingGeneralAndAdministrativeExpense", period="FY2024"),
               say("AMD's FY2024 SG&A was $2.735 billion, recast from $2.783 billion originally reported.")])
    a = response.ask("What was AMD's SG&A in fiscal 2024?", mode="single")
    assert a.grounded
    assert any(w["code"] == "restated" and "$2.783 billion" in w["message"] for w in a.warnings)
    assert a.status == "verified_with_warnings"
    old = next(f for f in a.facts if f.restated)
    assert old.value == 2_783_000_000 and old.provenance.startswith("Earlier reported value")


def test_stalled_model_is_nudged_to_call_the_tool(fake_chat):
    accn = agent.tools.get_fact("NVDA", "Revenues", "FY2024")["facts"][0]["accn"]
    fc = fake_chat([call("list_concepts", ticker="NVDA", keyword="revenue"),
                    say("Let me retrieve the revenue figure now."),
                    call("get_fact", ticker="NVDA", tag="Revenues", period="FY2024"),
                    say(GOOD.format(accn=accn))])
    a = response.ask(Q, mode="single")
    assert a.status == "verified"
    assert any(c["last"].get("content", "").startswith("Go ahead") for c in fc.calls)
