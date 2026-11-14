"""10-K text: download, convert to plain text, split out Item 1A and Item 7.

The filings are inline-XBRL HTML. Headings are marked up differently by every filer
(bold spans, tables, all-caps paragraphs), so the splitter does not rely on markup.
It works on the plain text and looks for lines that *start* with "Item 1A." / "Item 7."
etc. Every such heading appears at least twice (table of contents, then the body), so
for each item it takes the occurrence whose section is longest, which is the body.

Run through `secqa setup`, which fetches, splits and reports section sizes.
"""
import re
import warnings
from datetime import date

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from . import config, edgar
from .facts import INDEXED_FY, fiscal_year

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
ITEMS = ["1", "1A", "1B", "1C", "2", "3", "4", "5", "6", "7", "7A", "8", "9", "9A", "9B", "9C",
         "10", "11", "12", "13", "14", "15", "16"]
KEEP = {"1A": "Risk Factors", "7": "Management's Discussion and Analysis"}
HEAD = re.compile(r"^\s*item\s*(\d{1,2}[a-c]?)\s*[.:\-—–]?\s*(.{0,120})$", re.I | re.M)


def annual_reports(ticker):
    """In-scope original 10-Ks: one per indexed fiscal year (10-K/A amendments skipped)."""
    s = edgar.submissions(ticker)
    r, fye = s["filings"]["recent"], s.get("fiscalYearEnd") or "1231"
    out = {}
    for i, form in enumerate(r["form"]):
        if form != "10-K" or not r["reportDate"][i] or r["filingDate"][i] > config.SNAPSHOT:
            continue
        fy = fiscal_year(date.fromisoformat(r["reportDate"][i]), fye)
        if fy in INDEXED_FY and fy not in out:
            out[fy] = {"ticker": ticker, "fiscal_year": fy, "form": form,
                       "accn": r["accessionNumber"][i], "filed": r["filingDate"][i],
                       "report_date": r["reportDate"][i], "doc": r["primaryDocument"][i]}
    return [out[fy] for fy in sorted(out)]


def html_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "head"]):
        t.decompose()
    for t in soup.find_all(style=re.compile(r"display:\s*none", re.I)):
        t.decompose()  # hidden inline-XBRL header block
    for t in soup.find_all(["p", "div", "tr", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table"]):
        t.insert_before("\n")
    for t in soup.find_all(["td", "th"]):
        t.insert_before(" ")
    text = soup.get_text()
    text = text.replace("\xa0", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln)


def fetch_text(f):
    path = text_dir() / f"{f['ticker']}_FY{f['fiscal_year']}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    if not edgar.ALLOW_FETCH:
        raise edgar.NotDownloaded(f"{path} is missing. Run `secqa setup` to download the 10-K text.")
    cik = edgar.FILERS[f["ticker"]]
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{f['accn'].replace('-', '')}/{f['doc']}"
    html = edgar.get_text(url)
    text = html_to_text(html)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def split_items(text):
    """{item: text} for every item heading found; body occurrence chosen by section length."""
    heads = [(m.start(), m.group(1).upper()) for m in HEAD.finditer(text) if m.group(1).upper() in ITEMS]
    best = {}
    for i, (pos, item) in enumerate(heads):
        # the section runs to the next heading of a *different*, later item
        later = ITEMS[ITEMS.index(item) + 1:]
        end = next((p for p, it in heads[i + 1:] if it in later), len(text))
        body = text[pos:end]
        if len(body) > len(best.get(item, "")):
            best[item] = body
    return best


# Fallback for filers that do not organize the 10-K by Item (Intel uses its own layout plus a
# "Form 10-K Cross-Reference Index", so "Item 1A" only appears in that index with a page range).
# Sections are found by their exact heading line in the body; running page headers such as
# "Risk Factors and Other Key Information" are not exact matches for "Risk Factors".
TITLE_SECTIONS = {
    "7": (["Management's Discussion and Analysis"],
          ["Risk Factors and Other Key Information", "Risk Factors",
           "Quantitative and Qualitative Disclosures About Market Risk"]),
    "1A": (["Risk Factors"],
           ["Other Key Information", "Financial Statements and Supplemental Details", "Financial Statements"]),
}


def split_by_title(text, item, skip_lines=100):
    """Body section by exact heading line; the first `skip_lines` lines (cover page, contents) are skipped."""
    lines = text.split("\n")
    starts, ends = TITLE_SECTIONS[item]
    i = next((k for k in range(skip_lines, len(lines)) if lines[k] in starts), None)
    if i is None:
        return ""
    j = next((k for k in range(i + 1, len(lines)) if lines[k] in ends and lines[k] not in starts), len(lines))
    return "\n".join(lines[i:j])


def sections():
    """All kept sections of all in-scope 10-Ks, with source metadata."""
    out = []
    for t in edgar.FILERS:
        for f in annual_reports(t):
            text = fetch_text(f)
            items = split_items(text)
            for item, title in KEEP.items():
                body = items.get(item, "")
                if len(body) < 2000:  # only an index entry found: filer not organized by Item
                    body = split_by_title(text, item)
                out.append({**f, "item": item, "item_title": title, "text": body})
    return out


def text_dir():
    return config.RAW / "filings"


def download_all(log=print):
    """Fetch the in-scope 10-Ks, convert them to text and report the size of each kept section."""
    edgar.ALLOW_FETCH = True
    secs = sections()
    for s in secs:
        log(f"{s['ticker']:5s} FY{s['fiscal_year']} Item {s['item']:2s} {len(s['text']):8,d} chars")
    return secs
