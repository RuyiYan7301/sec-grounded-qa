"""Part B packet schema (draft 2): conditional rules on a small valid packet and broken variants."""
import copy
import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "data" / "eval" / "v0.2" / "packet.schema.json").read_text(encoding="utf-8"))
ACC = "0001045810-25-000023"
FACT = {"ticker": "NVDA", "metric": "revenue", "fy": "FY2025", "role": "current_year", "value": 130497000000,
        "unit": "USD", "concept": "Revenues", "period_start": "2024-01-29", "period_end": "2025-01-26",
        "accession": ACC, "filed": "2025-02-26"}
LOC = {"accession": ACC, "section": "1A", "paragraph_index": 3, "text_sha256": "a" * 64}
PACKET = {
    "schema_version": "packet-0.2-draft2", "case": "NVDA_FY2025", "system": "v0.2", "ticker": "NVDA",
    "from_fy": "FY2024", "to_fy": "FY2025", "value_policy": "as_of_filing",
    "target_filing": {"accession": ACC, "filed": "2025-02-26"},
    "numeric_changes": [
        {"id": "NVDA_FY2025:revenue:numeric_change", "metric": "revenue", "status": "large_numeric_change",
         "facts": [FACT, {**FACT, "fy": "FY2024", "role": "comparative_year", "value": 60922000000}],
         "absolute_change": 69575000000, "percent_change": 114.2, "change_basis": "percent", "direction": "increase",
         "warnings": []},
        {"id": "NVDA_FY2025:goodwill:numeric_change", "metric": "goodwill", "status": "abstain",
         "abstain_reason": "not_reported", "facts": [], "warnings": []}],
    "revision_checks": [
        {"id": "NVDA_FY2025:revenue:FY2024:revision_control", "metric": "revenue", "period": "FY2024",
         "as_presented": {**FACT, "fy": "FY2024", "role": "prior_year_as_presented"},
         "first_reported": {**FACT, "fy": "FY2024", "role": "first_reported"}, "revised": False, "cause": None}],
    "item1a_changes": [{"label": "material_modified", "earlier": LOC, "later": {**LOC, "paragraph_index": 4}}],
}


def errors(p):
    return list(jsonschema.Draft202012Validator(SCHEMA).iter_errors(p))


def test_valid_packet():
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    assert not errors(PACKET)


def _bend(path_value):
    p = copy.deepcopy(PACKET)
    path_value(p)
    return p


@pytest.mark.parametrize("name,bend", [
    ("abstain with a change value", lambda p: p["numeric_changes"][1].update(absolute_change=5.0)),
    ("abstain without reason", lambda p: p["numeric_changes"][1].pop("abstain_reason")),
    ("large without facts", lambda p: p["numeric_changes"][0].update(facts=[])),
    ("large without direction", lambda p: p["numeric_changes"][0].pop("direction")),
    ("free-text direction", lambda p: p["numeric_changes"][0].update(direction="went up a lot")),
    ("percentage on a magnitude-only basis", lambda p: p["numeric_changes"][0].update(change_basis="magnitude_only")),
    ("old status name 'unchanged'", lambda p: p["numeric_changes"][0].update(status="unchanged")),
    ("revised without cause", lambda p: p["revision_checks"][0].update(revised=True)),
    ("old cause name 'stock_split'", lambda p: p["revision_checks"][0].update(revised=True, cause="stock_split")),
    ("modified with one locator", lambda p: p["item1a_changes"][0].pop("later")),
    ("fact without filed", lambda p: p["numeric_changes"][0]["facts"][0].pop("filed")),
    ("concept_change with a value", lambda p: p["numeric_changes"][0].update(status="concept_change")),
    ("value policy", lambda p: p.update(value_policy="latest_in_snapshot")),
])
def test_invalid_variants(name, bend):
    assert errors(_bend(bend)), name
