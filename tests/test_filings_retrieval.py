import json

import numpy as np

from secqa import config, filings, retrieval

HTML = """<html><head><style>p{}</style></head><body>
<div style="display:none">hidden xbrl header</div>
<p>Table of Contents</p>
<p>Item 1A. Risk Factors ........ 12</p>
<p>Item 1B. Unresolved Staff Comments ........ 30</p>
<p>Item 7. Management&#8217;s Discussion and Analysis ........ 40</p>
<p>Item 7A. Quantitative and Qualitative Disclosures ........ 60</p>
<p>Item 1A. Risk Factors</p>
<p>Our business depends on suppliers in Asia.</p>
<p>Export controls may limit sales of data center products.</p>
<p>Item 1B. Unresolved Staff Comments</p>
<p>None.</p>
<p>Item 7. Management&#8217;s Discussion and Analysis</p>
<table><tr><td>Revenue</td><td>$60,922</td></tr></table>
<p>Item 7A. Quantitative and Qualitative Disclosures</p>
</body></html>"""


def test_html_to_text_drops_hidden_blocks_and_normalizes_quotes():
    text = filings.html_to_text(HTML)
    assert "hidden xbrl header" not in text
    assert "Management's Discussion" in text
    assert "Revenue $60,922" in text


def test_split_items_takes_the_body_not_the_table_of_contents():
    items = filings.split_items(filings.html_to_text(HTML))
    assert "Export controls may limit sales" in items["1A"]
    assert "Unresolved" not in items["1A"]
    assert "Revenue" in items["7"] and "........" not in items["7"]


def test_split_by_title_for_filers_without_item_headings():
    lines = ["cover"] * 3 + ["Risk Factors", "Supply risk.", "Other Key Information", "x"]
    assert filings.split_by_title("\n".join(lines), "1A", skip_lines=2) == "Risk Factors\nSupply risk."


def test_chunks_keep_source_metadata():
    sec = {"ticker": "NVDA", "fiscal_year": 2025, "item": "1A", "item_title": "Risk Factors",
           "accn": "0001045810-25-000023", "form": "10-K", "filed": "2025-02-26",
           "text": "\n".join(f"Paragraph {i} about supply and export licenses for products." * 3 for i in range(40))}
    chunks = retrieval.chunk_section(sec)
    assert len(chunks) > 1
    assert all(len(c["text"]) <= retrieval.TARGET + 400 for c in chunks)
    assert chunks[0]["chunk_id"] == "NVDA-2025-1A-000" and chunks[0]["accn"] == sec["accn"]


def test_bm25_prefers_documents_with_the_query_term():
    bm = retrieval.BM25(["general overview of results", "supply constraints on wafers", "results overview again"])
    s = bm.scores("supply constraints", [0, 1, 2])
    assert int(np.argmax(s)) == 1


def test_rrf_merges_rankings():
    assert retrieval.rrf([0, 1, 2], [2, 1, 0])[0] == 1 or retrieval.rrf([0, 1, 2], [1, 0, 2])[0] in (0, 1)
    assert retrieval.rrf([3, 1], [3, 2])[0] == 3


class HashEncoder:
    """Deterministic bag-of-words embedding, so the index can be tested without a model download."""

    def encode(self, texts, normalize_embeddings=True, **kw):
        out = np.zeros((len(texts), 64), np.float32)
        for i, t in enumerate(texts):
            for w in retrieval.words(t):
                out[i, sum(map(ord, w)) % 64] += 1
        return out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)


def test_index_search_filters_and_ranks(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "RAW", tmp_path)
    monkeypatch.setattr(retrieval, "_encoder", HashEncoder())
    chunks = [
        {"ticker": "NVDA", "fiscal_year": 2025, "item": "1A", "chunk_id": "NVDA-2025-1A-000", "text": "export controls on data center chips"},
        {"ticker": "NVDA", "fiscal_year": 2025, "item": "7", "chunk_id": "NVDA-2025-7-000", "text": "revenue grew in data center"},
        {"ticker": "AMD", "fiscal_year": 2025, "item": "1A", "chunk_id": "AMD-2025-1A-000", "text": "export controls on chips"},
    ]
    d = tmp_path / "index"
    d.mkdir()
    (d / "chunks.json").write_text(json.dumps(chunks), encoding="utf-8")
    np.save(d / "emb.npy", HashEncoder().encode([c["text"] for c in chunks]))
    ix = retrieval.Index()
    hits = ix.search("export controls", ticker="NVDA", k=2)
    assert [h["chunk_id"] for h in hits][0] == "NVDA-2025-1A-000"
    assert all(h["ticker"] == "NVDA" for h in hits)
    assert ix.search("export", ticker="NVDA", fiscal_year=2023) == []


def test_missing_index_is_explained(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "RAW", tmp_path)
    try:
        retrieval.Index()
    except FileNotFoundError as e:
        assert "secqa setup" in str(e)
    else:
        raise AssertionError("expected FileNotFoundError")
