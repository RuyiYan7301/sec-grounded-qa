"""Part B scorer: the reference packet (built from the gold) scores full marks; each mutation costs exactly
where the rules say. CSCO is the dev case; the AMD micro-case carries only revision checks."""
import copy

import pytest

from secqa.evaluation.v2 import partb_score as B

G = B.load_gold()
IG = B.load_item1a()
CASES = ["CSCO_FY2024", "NVDA_FY2025", "INTC_FY2025", "AVGO_FY2024"]


def score(p):
    return B.score_packet(p, G, IG)


def ref(case="CSCO_FY2024"):
    return B.reference_packet(case, G, IG)


def first_large(p):
    return next(i for i, x in enumerate(p["numeric_changes"]) if x["status"] == "large_numeric_change")


@pytest.mark.parametrize("case", CASES)
def test_reference_packet_scores_full(case):
    r = score(ref(case))
    n = r["numeric"]
    assert r["packet_metadata_ok"] and n["verified_recall"]["value"] == 1 and n["verified_precision"]["value"] == 1
    assert n["evidence_item_level"]["value"] == 1 and n["evidence_packet_all_pass"] is True
    assert n["silent_numeric_errors"] == 0 and n["unknown_item_count"] == 0 and n["over_abstention"] == 0
    assert n["correct_abstention"]["value"] in (1, None)
    assert n["unchanged_control_false_positives"]["num"] == 0
    rv = r["revisions"]
    assert rv["revision_stability_false_positives"]["num"] == 0 and rv["silent_numeric_errors"] == 0
    for k in ("split_recast_recall", "accounting_recast_recall"):
        assert rv[k]["den"] == 0 or rv[k]["value"] == 1
    assert rv["stable_claims_without_two_sided_evidence"] == 0
    ia = r["item1a"]
    assert ia["recall"]["value"] == 1 and ia["precision"]["value"] == 1 and ia["boilerplate_fpr"]["num"] == 0
    assert ia["subtype_agreement"]["value"] == 1


def test_amd_micro_case_revisions():
    r = score(ref("AMD_FY2025"))
    assert r["packet_metadata_ok"] and r["revisions"]["accounting_recast_recall"] == {"num": 2, "den": 2, "value": 1.0}


def test_stable_denominator_is_57():
    assert sum(score(ref(c))["revisions"]["revision_stability_false_positives"]["den"] for c in CASES[1:]) == 57


def test_empty_packet():
    p = ref()
    p["numeric_changes"], p["revision_checks"], p["item1a_changes"] = [], [], []
    r = score(p)["numeric"]
    assert r["verified_recall"]["num"] == 0 and r["verified_precision"]["den"] == 0 and r["verified_precision"]["value"] is None
    assert r["evidence_packet_all_pass"] is None and r["evidence_item_level"]["den"] == 0


@pytest.mark.parametrize("field,value", [("ticker", "INTC"), ("to_fy", "FY2025"), ("value_policy", "latest_in_snapshot")])
def test_wrong_metadata_blocks_hits(field, value):
    p = ref()
    p[field] = value
    r = score(p)
    assert not r["packet_metadata_ok"] and r["numeric"]["verified_recall"]["num"] == 0 and not r["item1a"]["scored"]


def test_wrong_target_accession_blocks_hits():
    p = ref()
    p["target_filing"]["accession"] = "0000000000-00-000000"
    assert not score(p)["packet_metadata_ok"]


def test_identical_duplicate_folds():
    p = ref()
    p["numeric_changes"].append(copy.deepcopy(p["numeric_changes"][first_large(p)]))
    base, r = score(ref())["numeric"], score(p)["numeric"]
    assert r["verified_recall"] == base["verified_recall"] and r["verified_precision"] == base["verified_precision"]


def test_conflicting_duplicate_marks_whole_id():
    p = ref()
    i = first_large(p)
    dup = copy.deepcopy(p["numeric_changes"][i])
    dup["facts"][0]["value"] *= 1.2
    p["numeric_changes"].insert(0, dup)          # order must not matter
    base, r = score(ref())["numeric"], score(p)["numeric"]
    assert r["verified_recall"]["num"] == base["verified_recall"]["num"] - 1
    assert r["verified_precision"]["den"] == base["verified_precision"]["den"]
    assert r["verified_precision"]["num"] == base["verified_precision"]["num"] - 1
    assert r["inconsistent_duplicate_ids"] == 1


def test_look_ahead_same_value():
    p = ref()
    i = first_large(p)
    p["numeric_changes"][i]["facts"][0]["filed"] = "2030-01-01"
    r = score(p)["numeric"]
    assert r["look_ahead_facts"] == 1 and r["silent_numeric_errors"] == 0
    assert r["verified_recall"]["num"] == score(ref())["numeric"]["verified_recall"]["num"] - 1


def test_look_ahead_different_value_counts_twice():
    p = ref()
    i = first_large(p)
    p["numeric_changes"][i]["facts"][0]["filed"] = "2030-01-01"
    p["numeric_changes"][i]["facts"][0]["value"] *= 1.2
    assert score(p)["numeric"]["silent_numeric_errors"] == 2


def test_other_accession_same_value_is_not_verified():
    p = ref()
    i = first_large(p)
    p["numeric_changes"][i]["facts"][0]["accession"] = "0000858877-23-000014"
    r = score(p)["numeric"]
    assert r["verified_recall"]["num"] == score(ref())["numeric"]["verified_recall"]["num"] - 1
    assert r["detection_recall"] == score(ref())["numeric"]["detection_recall"]


def test_extra_fact_breaks_exact_set():
    p = ref()
    i = first_large(p)
    p["numeric_changes"][i]["facts"].append({**p["numeric_changes"][i]["facts"][0], "metric": "goodwill"})
    assert score(p)["numeric"]["verified_recall"]["num"] == score(ref())["numeric"]["verified_recall"]["num"] - 1


def test_warning_does_not_offset_a_wrong_value():
    p = ref()
    i = first_large(p)
    p["numeric_changes"][i]["facts"][0]["value"] *= 1.2
    p["numeric_changes"][i]["warnings"] = ["scope", "concept_change"]
    r = score(p)["numeric"]
    assert r["silent_numeric_errors"] >= 1 and r["verified_recall"]["num"] < score(ref())["numeric"]["verified_recall"]["num"]


def test_unknown_id_is_a_false_prediction():
    p = ref()
    x = copy.deepcopy(p["numeric_changes"][first_large(p)])
    x["id"], x["metric"] = "CSCO_FY2024:ebitda:numeric_change", "ebitda"
    p["numeric_changes"].append(x)
    base, r = score(ref())["numeric"], score(p)["numeric"]
    assert r["unknown_item_count"] == 1 and r["verified_precision"]["den"] == base["verified_precision"]["den"] + 1
    assert r["silent_numeric_errors"] == base["silent_numeric_errors"]


def test_id_with_wrong_case_is_unknown():
    p = ref()
    p["numeric_changes"][first_large(p)]["id"] = p["numeric_changes"][first_large(p)]["id"].replace("CSCO_FY2024", "NVDA_FY2025")
    assert score(p)["numeric"]["unknown_item_count"] == 1


def test_unchanged_control_reported_gray_is_a_false_positive():
    p = ref()
    i = next(i for i, x in enumerate(p["numeric_changes"]) if x["status"] == "unchanged_control")
    p["numeric_changes"][i]["status"] = "gray_zone"
    assert score(p)["numeric"]["unchanged_control_false_positives"]["num"] == 1


def test_missing_scope_warning():
    p = ref("AVGO_FY2024")
    scoped = [x for x in p["numeric_changes"] if "scope" in x["warnings"]]
    if not scoped:
        pytest.skip("no scope item in this case")
    scoped[0]["warnings"] = []
    r = score(p)["numeric"]["scope_warning"]
    assert r["num"] == r["den"] - 1


def test_stable_reported_revised_is_a_false_positive():
    p = ref("NVDA_FY2025")
    i = next(i for i, x in enumerate(p["revision_checks"]) if x["status"] == "stable")
    p["revision_checks"][i]["status"] = "revised"
    p["revision_checks"][i]["cause"] = "accounting_recast"
    assert score(p)["revisions"]["revision_stability_false_positives"]["num"] == 1


def test_stable_claim_without_first_reported():
    p = ref("NVDA_FY2025")
    i = next(i for i, x in enumerate(p["revision_checks"]) if x["status"] == "stable")
    p["revision_checks"][i]["first_reported"] = None
    assert score(p)["revisions"]["stable_claims_without_two_sided_evidence"] == 1


def test_omitted_stable_control_is_not_a_false_positive():
    p = ref("NVDA_FY2025")
    p["revision_checks"] = [x for x in p["revision_checks"] if x["status"] != "stable"]
    assert score(p)["revisions"]["revision_stability_false_positives"]["num"] == 0


def test_split_recast_wrong_cause():
    p = ref("NVDA_FY2025")
    i = next(i for i, x in enumerate(p["revision_checks"]) if x["cause"] == "stock_split_recast")
    p["revision_checks"][i]["cause"] = "accounting_recast"
    r = score(p)["revisions"]["split_recast_recall"]
    assert r["num"] == r["den"] - 1


def _modified_units(case):
    return [u for u in IG[0]["cases"][case]["units"] if u["type"] == "modified"
            and IG[1].get(u["id"], {}).get("label", "").startswith("material")]


def test_item1a_locators_mapping_to_two_units_are_inconsistent():
    p = ref()
    m = _modified_units("CSCO_FY2024")
    i = next(i for i, x in enumerate(p["item1a_changes"]) if "earlier" in x and "later" in x)
    other = next(u for u in IG[0]["cases"]["CSCO_FY2024"]["units"] if "later" in u and u["id"] != m[0]["id"]
                 and p["item1a_changes"][i]["later"]["paragraph_index"] != u["later"]["paragraph_index"])
    p["item1a_changes"][i]["later"] = {k: other["later"][k] for k in ("accession", "section", "paragraph_index", "text_sha256")}
    r = score(p)["item1a"]
    assert r["inconsistent_locators"] == 1 and r["recall"]["num"] == score(ref())["item1a"]["recall"]["num"] - 1


def test_item1a_subtype_error_is_still_a_hit():
    p = ref()
    i = next(i for i, x in enumerate(p["item1a_changes"]) if x["label"] == "material_modified")
    p["item1a_changes"][i]["label"] = "material_added"
    p["item1a_changes"][i].pop("earlier", None)
    r, base = score(p)["item1a"], score(ref())["item1a"]
    assert r["recall"] == base["recall"] and r["subtype_agreement"]["num"] == base["subtype_agreement"]["num"] - 1


def test_item1a_conflicting_duplicate_labels_are_not_folded():
    p = ref()
    x = copy.deepcopy(p["item1a_changes"][0])
    x["label"] = "material_removed" if x["label"] != "material_removed" else "material_added"
    p["item1a_changes"].append(x)
    r, base = score(p)["item1a"], score(ref())["item1a"]
    assert r["conflicting_duplicate_units"] == 1 and r["recall"]["num"] == base["recall"]["num"] - 1


def test_item1a_unmatched_prediction_costs_precision():
    p = ref()
    p["item1a_changes"].append({"label": "material_added", "later": {"accession": "0000000000-00-000000", "section": "1A",
                                                                     "paragraph_index": 9999, "text_sha256": "0" * 64}})
    r = score(p)["item1a"]
    assert r["unmatched_predictions"] == 1 and r["precision"]["value"] < 1


@pytest.mark.parametrize("bend", [
    lambda p: p.update(numeric_changes="none"),
    lambda p: p["numeric_changes"].append("a string"),
    lambda p: p["numeric_changes"][0].update(facts="see filing"),
    lambda p: p["numeric_changes"][0].update(facts=[None, 3]),
    lambda p: p.update(revision_checks=[{"id": None}]),
    lambda p: p.update(item1a_changes=[{"label": "material_added", "later": "x"}]),
    lambda p: p.update(target_filing=None),
])
def test_malformed_packets_never_crash(bend):
    p = ref()
    bend(p)
    r = score(p)
    assert r["packet_valid"] is False


def test_non_dict_packet():
    assert score(None)["packet_metadata_ok"] is False


@pytest.mark.parametrize("case", CASES + ["AMD_FY2025"])
def test_reference_packets_are_schema_valid(case):
    assert B.packet_valid(ref(case))


def test_item1a_locator_completeness_follows_gold_unit_type():
    p = ref("NVDA_FY2025")
    i = next(i for i, x in enumerate(p["item1a_changes"]) if "earlier" in x and "later" in x)
    p["item1a_changes"][i].pop("later")
    r, base = score(p)["item1a"], score(ref("NVDA_FY2025"))["item1a"]
    assert r["recall"] == base["recall"] and r["locator_complete"]["num"] == base["locator_complete"]["num"] - 1
