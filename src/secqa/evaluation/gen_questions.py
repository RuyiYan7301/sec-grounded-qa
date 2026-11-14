"""Generate the held-out test set's numeric and period queries from the XBRL fact store.

The 28 queries in data/gold.json were used while building the system, so they are a
development set. This script writes data/gold_test.json: queries generated from fixed
templates and a fixed seed, with gold values taken from the fact store, so the set can be
large and its strata balanced. Narrative and behavior queries are written by hand
(data/gold_test_hand.json) and merged in.

Gold values come from the same fact store the tools read. A bug in facts.py would therefore
be copied into the gold answers; verify_gold.py checks every gold value against the 10-K text.

Strata (question_type):
  single_fy       one filer, one metric, one fiscal year
  tag_trap        the filer reports the metric under a less common tag
  restated        the figure was later recast (stock split); gold is the latest value
  yoy             percentage change between two fiscal years of one filer
  cross_mismatch  two filers, same fiscal-year label, periods more than a month apart (flag required)
  cross_aligned   two December filers (Intel, AMD), no mismatch
  bare_year       "in 2024": clarify for non-calendar filers, answer for December filers
  out_of_range    fiscal year outside FY2023-2025: decline
  not_reported    metric the filer does not report: decline

    secqa gen-questions   # rewrites data/eval/gold_test.json; same seed and data -> same file
"""
import json
import random
from collections import Counter

from .. import config, tools
from ..facts import INDEXED_FY

SEED = 259

NAMES = {"AAPL": "Apple", "NVDA": "Nvidia", "MSFT": "Microsoft", "ORCL": "Oracle", "CSCO": "Cisco",
         "AVGO": "Broadcom", "INTC": "Intel", "AMD": "AMD"}
# metric -> (phrase, balance-sheet?, tags to look for)
METRICS = {
    "revenue": ("total revenue", False, ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"]),
    "net_income": ("net income", False, ["NetIncomeLoss", "ProfitLoss"]),
    "operating_income": ("operating income", False, ["OperatingIncomeLoss"]),
    "rd": ("research and development expense", False, ["ResearchAndDevelopmentExpense"]),
    "gross_profit": ("gross profit", False, ["GrossProfit"]),
    "ocf": ("net cash provided by operating activities", False, ["NetCashProvidedByUsedInOperatingActivities"]),
    "capex": ("capital expenditures (purchases of property and equipment)", False,
              ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"]),
    "eps": ("diluted earnings per share", False, ["EarningsPerShareDiluted"]),
    "assets": ("total assets", True, ["Assets"]),
    "cash": ("cash and cash equivalents", True, ["CashAndCashEquivalentsAtCarryingValue"]),
    "equity": ("total stockholders' equity", True,
               ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]),
}
# The most common tag across the eight filers; a filer that uses another one is a tag trap.
COMMON_TAG = {m: v[2][0] for m, v in METRICS.items()}
# Already asked in the development set (gold.json): not repeated here.
DEV = {("AAPL", "revenue", 2024), ("INTC", "operating_income", 2023), ("NVDA", "revenue", 2024)}

CLARIFY_MUST = ["\\?|please (specify|clarify|provide|confirm|tell)|could you (specify|clarify|tell)|i need to know|need (more|to know)|let me know",
                "fiscal", "calendar"]
OOR_MUST = ["outside|not (in|within|covered|indexed|available)|only (covers?|indexe?s?)|fy ?2023"]


def fact(t, metric, fy):
    """(value, unit, record, tags that give this value) or None."""
    for tag in METRICS[metric][2]:
        r = tools.get_fact(t, tag, f"FY{fy}")
        if r.get("found"):
            f = r["facts"][0]
            return f["val"], f["unit"], f, equivalent_tags(t, f)
    return None


def equivalent_tags(t, f):
    """Every tag of this filer with the same value for the same period: all count as a correct tag choice."""
    out = []
    for tag, recs in tools.store().facts[t].items():
        if any(r["unit"] == f["unit"] and r["start"] == f["start"] and r["end"] == f["end"]
               and abs(r["val"] - f["val"]) <= 0.001 * max(abs(f["val"]), 1e-9) for r in recs):
            out.append(tag)
    return sorted(out)


def fy_q(fy):
    return f"fiscal {fy}"


def main(out=None):
    rng = random.Random(SEED)
    qs = []

    def add(**q):
        q["id"] = 101 + len(qs)
        q["set"] = "test"
        qs.append(q)

    def numeric(stratum, query, t, metric, fy, f):
        val, unit, rec, tags = f
        add(question_type=stratum, query=query, check="numeric", gold=[val], gold_tags=[tags],
            company=t, metric=metric, period=f"FY{fy}", gold_period_end=rec["end"], gold_unit=unit,
            gold_accn=rec["accn"], expected_behavior="answer")

    # --- tag traps (hand-picked from the coverage survey, values from the store) ---
    traps = [("NVDA", "capex", 2024), ("NVDA", "capex", 2025), ("AVGO", "net_income", 2025),
             ("AVGO", "equity", 2024), ("NVDA", "revenue", 2023)]
    for t, m, fy in traps:
        f = fact(t, m, fy)
        assert f, (t, m, fy)
        when = f"at the end of {fy_q(fy)}" if METRICS[m][1] else f"in {fy_q(fy)}"
        numeric("tag_trap", f"What was {NAMES[t]}'s {METRICS[m][0]} {when}?", t, m, fy, f)
    used = set(traps) | DEV

    # --- restated (split-adjusted EPS) ---
    for t, fy in [("NVDA", 2024), ("AVGO", 2023)]:
        f = fact(t, "eps", fy)
        assert f and f[2]["other_values"], (t, fy)
        numeric("restated", f"What was {NAMES[t]}'s diluted earnings per share for {fy_q(fy)}?", t, "eps", fy, f)
        qs[-1]["other_values"] = [o["val"] for o in f[2]["other_values"]]
        qs[-1]["note"] = "Recast after a 10-for-1 stock split; gold is the latest (split-adjusted) value."
        used.add((t, "eps", fy))

    # --- single fiscal year: 4 per filer, standard tags only, no restated values ---
    for t in NAMES:
        pool = []
        for m in METRICS:
            for fy in INDEXED_FY:
                if (t, m, fy) in used:
                    continue
                f = fact(t, m, fy)
                if f and COMMON_TAG[m] in f[3] and not f[2]["other_values"]:
                    pool.append((m, fy, f))
        picks, seen_m = [], set()
        for m, fy, f in rng.sample(pool, len(pool)):
            if m not in seen_m:
                picks.append((m, fy, f))
                seen_m.add(m)
            if len(picks) == 4:
                break
        for m, fy, f in picks:
            phrase, bs, _ = METRICS[m]
            q = (f"What was {NAMES[t]}'s {phrase} at the end of {fy_q(fy)}?" if bs else
                 f"What was {NAMES[t]}'s {phrase} in {fy_q(fy)}?")
            numeric("single_fy", q, t, m, fy, f)
            used.add((t, m, fy))

    # --- year over year: 12, flow metrics, standard tags ---
    flows = ["revenue", "net_income", "operating_income", "rd", "gross_profit", "ocf"]
    cands = []
    for t in NAMES:
        for m in flows:
            for y1 in (2023, 2024):
                a, b = fact(t, m, y1), fact(t, m, y1 + 1)
                if a and b and COMMON_TAG[m] in a[3] and COMMON_TAG[m] in b[3] and a[0] > 0 and b[0] > 0:  # no sign flips
                    cands.append((t, m, y1, a, b))
    rng.shuffle(cands)
    per_t = {}
    for t, m, y1, a, b in cands:
        if per_t.get(t, 0) >= 2 or sum(per_t.values()) >= 12:
            continue
        per_t[t] = per_t.get(t, 0) + 1
        pct = round((b[0] - a[0]) / abs(a[0]) * 100, 2)
        add(question_type="yoy", check="numeric",
            query=f"By what percentage did {NAMES[t]}'s {METRICS[m][0]} change from {fy_q(y1)} to {fy_q(y1 + 1)}? Give both figures.",
            gold=[a[0], b[0]], gold_pct=[pct], gold_tags=[sorted(set(a[3]) & set(b[3]))],
            company=t, metric=m, period=f"FY{y1}-FY{y1 + 1}", gold_unit=a[1], expected_behavior="answer")

    # --- cross company ---
    cross_metrics = ["revenue", "net_income", "operating_income", "rd"]
    pairs = [(a, b) for a in NAMES for b in NAMES if a < b and {a, b} != {"INTC", "AMD"}]
    rng.shuffle(pairs)
    n_mis = 0
    for a, b in pairs:
        if n_mis >= 10:
            break
        m, fy = rng.choice(cross_metrics), rng.choice(INDEXED_FY)
        fa, fb = fact(a, m, fy), fact(b, m, fy)
        if not (fa and fb):
            continue
        cmp = tools.compare([a, b], {a: fa[3][0], b: fb[3][0]}, f"FY{fy}")
        if not cmp["period_mismatch"]:
            continue
        n_mis += 1
        add(question_type="cross_mismatch", check="numeric", needs_flag=True,
            query=f"Compare {NAMES[a]}'s and {NAMES[b]}'s {METRICS[m][0]} for {fy_q(fy)}.",
            gold=[fa[0], fb[0]], gold_tags=[fa[3], fb[3]], company=f"{a},{b}", metric=m, period=f"FY{fy}",
            gold_period_end=f"{fa[2]['end']},{fb[2]['end']}", gold_unit="USD", expected_behavior="answer",
            mismatch_reason=cmp["mismatch_reason"])
    for m, fy in [("revenue", 2023), ("net_income", 2024), ("rd", 2025), ("operating_income", 2025)]:
        fa, fb = fact("INTC", m, fy), fact("AMD", m, fy)
        cmp = tools.compare(["INTC", "AMD"], {"INTC": fa[3][0], "AMD": fb[3][0]}, f"FY{fy}")
        assert not cmp["period_mismatch"], cmp
        add(question_type="cross_aligned", check="numeric",
            query=f"Compare Intel's and AMD's {METRICS[m][0]} for {fy_q(fy)}.",
            gold=[fa[0], fb[0]], gold_tags=[fa[3], fb[3]], company="INTC,AMD", metric=m, period=f"FY{fy}",
            gold_period_end=f"{fa[2]['end']},{fb[2]['end']}", gold_unit="USD", expected_behavior="answer")

    # --- bare year ---
    for t, m, y in [("AAPL", "net_income", 2023), ("MSFT", "revenue", 2025), ("ORCL", "operating_income", 2024),
                    ("CSCO", "rd", 2023), ("AVGO", "revenue", 2025), ("NVDA", "net_income", 2025)]:
        add(question_type="bare_year", check="clarify", must=CLARIFY_MUST, no_numbers=True,
            query=f"What was {NAMES[t]}'s {METRICS[m][0]} in {y}?", company=t, metric=m, period=str(y),
            expected_behavior="clarify", note=f"{t}'s fiscal year does not end in December.")
    for t, m, y in [("INTC", "net_income", 2023), ("AMD", "net_income", 2023), ("INTC", "rd", 2024), ("AMD", "ocf", 2025)]:
        f = fact(t, m, y)
        numeric("bare_year", f"What was {NAMES[t]}'s {METRICS[m][0]} in {y}?", t, m, y, f)
        qs[-1]["note"] = f"{t}'s fiscal year ends in late December, so {y} means fiscal {y}."

    # --- out of range ---
    for t, m, fy in [("MSFT", "net_income", 2021), ("CSCO", "revenue", 2022), ("AMD", "rd", 2020), ("AVGO", "operating_income", 2019)]:
        add(question_type="out_of_range", check="decline", must=OOR_MUST, no_numbers=True,
            query=f"What was {NAMES[t]}'s {METRICS[m][0]} in {fy_q(fy)}?", company=t, metric=m, period=f"FY{fy}",
            expected_behavior="decline", refusal_reason="outside indexed fiscal years")

    # --- not reported ---
    assert fact("ORCL", "gross_profit", 2024) is None
    add(question_type="not_reported", check="decline", company="ORCL", metric="gross_profit", period="FY2024",
        query="What was Oracle's gross profit in fiscal 2024?", expected_behavior="decline",
        refusal_reason="Oracle does not report gross profit",
        must=["not (directly )?(report|tag|disclose|present|provide)|no (xbrl )?(tag|concept|gross profit)|does not (report|tag|disclose|present|break out)|doesn't (report|tag|disclose|present)|isn't (reported|tagged)|not (separately )?(reported|available|disclosed|presented)"],
        must_not=["gross profit (was|of|totaled|amounted to) \\$"])
    add(question_type="not_reported", check="decline", company="AMD", metric="dividends", period="FY2024",
        query="How much did AMD pay in dividends in fiscal 2024?", expected_behavior="decline",
        refusal_reason="AMD paid no dividends",
        must=["(not|no|n't) (pay|paid|declare|declared|report|any)|no (cash )?dividends?|did not pay|didn't pay|does not pay|doesn't pay"],
        must_not=["paid \\$\\d"])

    hand = json.loads((config.EVAL_DIR / "gold_test_hand.json").read_text(encoding="utf-8"))
    qs += hand
    out = out or config.EVAL_DIR / "gold_test.json"
    out.write_text(json.dumps(qs, indent=1), encoding="utf-8")
    print(len(qs), "queries ->", out)
    print(dict(Counter(q["question_type"] for q in qs)))
    return qs
