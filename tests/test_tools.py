from secqa import tools


def test_get_fact_fiscal_year():
    r = tools.get_fact("NVDA", "Revenues", "FY2024")
    assert r["found"]
    f = r["facts"][0]
    assert f["val"] == 60_922_000_000 and f["end"] == "2024-01-28"
    assert f["display"] == "$60.922 billion (= $60,922 million)"
    assert f["accn"] and f["form"].startswith("10-K")


def test_get_fact_is_case_insensitive_on_ticker():
    assert tools.get_fact(" nvda ", "Revenues", "FY2024")["found"]


def test_bare_year_is_ambiguous_for_non_calendar_filer():
    r = tools.get_fact("NVDA", "Revenues", "2024")
    assert r == {**r, "found": False, "reason": "ambiguous_year"}
    assert "2024-01-28" in r["detail"]


def test_bare_year_answers_for_december_filer():
    r = tools.get_fact("AMD", "NetIncomeLoss", "2024")
    assert r["found"] and r["period"] == "FY2024"


def test_out_of_range_year():
    assert tools.get_fact("AAPL", "NetIncomeLoss", "FY2021")["reason"] == "out_of_range"


def test_unknown_company():
    r = tools.get_fact("TSLA", "Revenues", "FY2024")
    assert r["reason"] == "not_indexed_filer" and "AAPL" in r["detail"]


def test_bad_period_and_unused_tag():
    assert tools.get_fact("AAPL", "NetIncomeLoss", "last year")["reason"] == "bad_period"
    assert tools.get_fact("AAPL", "NoSuchTag", "FY2024")["reason"] == "tag_not_used"


def test_restated_fact_carries_other_value():
    f = tools.get_fact("AMD", "SellingGeneralAndAdministrativeExpense", "FY2024")["facts"][0]
    assert f["val"] == 2_735_000_000
    assert f["other_values"][0]["display"] == "$2.783 billion (= $2,783 million)"


def test_compare_flags_period_mismatch():
    r = tools.compare(["AAPL", "NVDA"], "OperatingIncomeLoss", "FY2024")
    assert r["period_mismatch"]
    assert "AAPL 2024-09-28" in r["mismatch_reason"] and "NVDA 2024-01-28" in r["mismatch_reason"]


def test_compare_aligned_december_filers():
    r = tools.compare(["INTC", "AMD"], "NetIncomeLoss", "FY2024")
    assert all(row["found"] for row in r["rows"])
    assert not r["period_mismatch"]


def test_compare_accepts_tag_list():
    r = tools.compare(["AAPL", "NVDA"], ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"], "FY2024")
    assert [row["tag"] for row in r["rows"]] == ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"]


def test_list_concepts_maps_plain_words_to_tags():
    r = tools.list_concepts("AAPL", "revenue")
    assert r["found"]
    assert "RevenueFromContractWithCustomerExcludingAssessedTax" in [c["tag"] for c in r["candidates"]]
    assert tools.list_concepts("AAPL", "zzzz")["found"] is False


def test_display_scales():
    assert tools.display(93_000_000, "USD") == "$93 million"
    assert tools.display(-11_678_000_000, "USD").startswith("-$11.678 billion")
    assert tools.display(6.11, "USD/shares") == "$6.11 per share"


def test_filer_info_fiscal_year_ends():
    r = tools.filer_info("NVDA")
    assert r["filers"][0]["fiscal_year_end_dates"]["FY2024"] == "2024-01-28"
    assert tools.filer_info("XYZ")["found"] is False


def test_search_filings_validates_before_touching_the_index():
    assert tools.search_filings("NVDA", "export", fiscal_year=2021)["reason"] == "out_of_range"
    assert tools.search_filings("NVDA", "export", item="8")["reason"] == "item_not_indexed"
    assert tools.search_filings("NVDA", "export", fiscal_year="next")["reason"] == "bad_period"
    assert tools.search_filings("IBM", "export")["reason"] == "not_indexed_filer"
