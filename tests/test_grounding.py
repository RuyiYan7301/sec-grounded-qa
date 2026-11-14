"""The deterministic number check: every figure in an answer must trace to a tool result."""
from secqa import agent, tools


def trace_for(*calls):
    return [{"tool": name, "args": args, "result": getattr(tools, name)(**args)} for name, args in calls]


NVDA_REV = trace_for(("get_fact", {"ticker": "NVDA", "tag": "Revenues", "period": "FY2024"}))


def values(text):
    return [v for v, _, _ in agent.numbers_in(text)]


def test_numbers_in_scales_and_skips_non_figures():
    text = ("Revenue was $60.922 billion in FY2024 (accession 0001045810-24-000029, filed 2024-02-21), "
            "up from $26,974 million. EPS was $6.11. It has 3 segments; see Item 7 and Microsoft 365.")
    assert values(text) == [60.922e9, 26_974e6, 6.11]


def test_numbers_in_ignores_urls_and_percent_calculations():
    assert values("https://www.sec.gov/Archives/edgar/data/1045810/000104581024000029/x.htm") == []
    assert values("(60,922 - 26,974) / 26,974 \\times 100 = 125.85\\%") == [60922, 26974, 26974, 125.85]


def test_grounded_accepts_tool_figures():
    assert agent.grounded("Nvidia's revenue in fiscal 2024 was $60.922 billion.", NVDA_REV) == (True, [])
    assert agent.grounded("That is $60,922 million.", NVDA_REV)[0]


def test_grounded_rejects_invented_or_misscaled_figures():
    ok, bad = agent.grounded("Nvidia's revenue was $60.9 trillion, and margin hit $12 billion.", NVDA_REV)
    assert not ok and bad == ["$60.9 trillion", "$12 billion"]
    assert not agent.grounded("Revenue was $930 million.", NVDA_REV)[0]


def test_grounded_ignores_sign_wording():
    tr = [{"tool": "get_fact", "args": {}, "result": {"found": True, "facts": [{"val": -11_678_000_000}]}}]
    assert agent.grounded("an operating loss of $11.678 billion", tr)[0]


def test_percentages_must_be_ratio_or_change_of_tool_numbers():
    tr = trace_for(("get_fact", {"ticker": "NVDA", "tag": "Revenues", "period": "FY2024"}),
                   ("get_fact", {"ticker": "NVDA", "tag": "Revenues", "period": "FY2023"}))
    assert agent.grounded("Revenue grew 125.85% year over year.", tr)[0]
    assert not agent.grounded("Revenue grew 140% year over year.", tr)[0]


def test_facts_used_links_answer_numbers_to_facts():
    used = agent.facts_used("Revenue was $60.922 billion.", NVDA_REV)
    assert [(u["ticker"], u["tag"], u["period"], u["val"]) for u in used] == [("NVDA", "Revenues", "FY2024", 60_922_000_000)]


def test_period_hint_only_for_non_calendar_filers():
    assert "fiscal 2024 ended 2024-01-28" in agent.period_hint("What was Nvidia's revenue in 2024?")
    assert agent.period_hint("What was AMD's revenue in 2024?") is None
    assert agent.period_hint("What was Nvidia's revenue in fiscal 2024?") is None


def test_drop_claims_removes_only_the_flagged_sentence():
    ans = ("Nvidia lists export controls on data center products as a risk. Licenses may be denied or delayed. "
           "Nvidia expects to win every export license next year.")
    out = agent._drop_claims(ans, ["Nvidia expects to win every export license next year"])
    assert "win every export license" not in out and "Licenses may be denied" in out
    assert agent._drop_claims(ans, ["a claim about something else entirely"]) is None
