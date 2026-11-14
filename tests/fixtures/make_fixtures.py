"""Build the small offline test fixture from a full `secqa setup` download.

Keeps a few XBRL concepts per filer (fiscal years 2022-2026) and the 10-K rows of each
filing list, so the tests run on real EDGAR data without network access or the 60 MB cache.

    SECQA_DATA_DIR=/path/to/full/data python tests/fixtures/make_fixtures.py
"""
import json
from pathlib import Path

from secqa import config
from secqa.edgar import FILERS

TAGS = {"Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "OperatingIncomeLoss", "NetIncomeLoss",
        "SellingGeneralAndAdministrativeExpense", "EarningsPerShareDiluted", "Assets", "LongTermDebt",
        "ResearchAndDevelopmentExpense", "PaymentsToAcquireProductiveAssets"}
OUT = Path(__file__).parent / "data" / "raw"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for t in FILERS:
        cf = json.loads((config.RAW / f"companyfacts_{t}.json").read_text(encoding="utf-8"))
        facts = {}
        for tax, concepts in cf["facts"].items():
            for tag, c in concepts.items():
                if tag not in TAGS:
                    continue
                units = {u: [r for r in rows if "2021-06-01" <= r["end"] <= "2026-12-31"] for u, rows in c["units"].items()}
                facts.setdefault(tax, {})[tag] = {"label": c.get("label"), "description": (c.get("description") or "")[:200],
                                                  "units": units}
        (OUT / f"companyfacts_{t}.json").write_text(json.dumps({"cik": cf.get("cik"), "entityName": cf.get("entityName"),
                                                                "facts": facts}), encoding="utf-8")
        sub = json.loads((config.RAW / f"submissions_{t}.json").read_text(encoding="utf-8"))
        r = sub["filings"]["recent"]
        keep = [i for i, f in enumerate(r["form"]) if f == "10-K"]
        recent = {k: [r[k][i] for i in keep] for k in ("form", "accessionNumber", "filingDate", "reportDate", "primaryDocument")}
        (OUT / f"submissions_{t}.json").write_text(json.dumps({"name": sub["name"], "fiscalYearEnd": sub.get("fiscalYearEnd"),
                                                               "filings": {"recent": recent}}), encoding="utf-8")
    print("fixture written to", OUT, f"({sum(p.stat().st_size for p in OUT.iterdir()) / 1e3:.0f} kB)")


if __name__ == "__main__":
    main()
