"""EDGAR client: declared User-Agent, rate limiting, retries, local cache.

The SEC asks for a User-Agent with a contact address and at most 10 requests per second.
Everything is cached under data/raw, so answering questions and running the evaluation
never call EDGAR; only `secqa setup` does.
"""
import json
import time

import requests

from . import config

MIN_INTERVAL = 0.25  # seconds between requests, well under the 10/s limit
RETRY_STATUS = (403, 429, 500, 502, 503, 504)  # EDGAR answers 403 when throttling

FILERS = {
    "AAPL": 320193,
    "NVDA": 1045810,
    "MSFT": 789019,
    "ORCL": 1341439,
    "CSCO": 858877,
    "AVGO": 1730168,
    "INTC": 50863,
    "AMD": 2488,
}


class MissingUserAgent(RuntimeError):
    pass


class NotDownloaded(FileNotFoundError):
    """A cached file is missing and fetching was not allowed."""


_last = 0.0


def _get(url, retries=4, as_text=False, session=requests):
    global _last
    ua = config.user_agent()
    if not ua:
        raise MissingUserAgent('Set SEC_USER_AGENT="Your Name your@email.com" (in .env or the environment) '
                               "before downloading from EDGAR.")
    last = None
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.time() - _last)
        if wait > 0:
            time.sleep(wait)
        _last = time.time()
        try:
            r = session.get(url, headers={"User-Agent": ua, "Accept-Encoding": "gzip"}, timeout=60)
        except (requests.ConnectionError, requests.Timeout) as e:
            last = type(e).__name__
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 200:
            return r.text if as_text else r.json()
        last = r.status_code
        if r.status_code in RETRY_STATUS:  # throttled or transient: back off exponentially
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
    raise RuntimeError(f"gave up on {url} after {retries} attempts (last: {last})")


def get_text(url):
    """Raw text of a filing document (www.sec.gov/Archives). Same throttle as the JSON API."""
    return _get(url, as_text=True)


# Reading is offline by default; `secqa setup` turns fetching on.
ALLOW_FETCH = False


def _cached(name, url, refresh=False):
    path = config.RAW / name
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    if not (ALLOW_FETCH or refresh):
        raise NotDownloaded(f"{path} is missing. Run `secqa setup` to download the SEC data.")
    data = _get(url)
    config.RAW.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


def companyfacts(ticker, refresh=False):
    cik = FILERS[ticker]
    return _cached(f"companyfacts_{ticker}.json",
                   f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", refresh)


def submissions(ticker, refresh=False):
    cik = FILERS[ticker]
    return _cached(f"submissions_{ticker}.json",
                   f"https://data.sec.gov/submissions/CIK{cik:010d}.json", refresh)


def filing_url(ticker, accn):
    """Index page of one filing on sec.gov, for citations."""
    return (f"https://www.sec.gov/Archives/edgar/data/{FILERS[ticker]}/"
            f"{accn.replace('-', '')}/{accn}-index.htm")


def download_all(refresh=False, log=print):
    """Fetch submissions and XBRL company facts for every filer."""
    global ALLOW_FETCH
    ALLOW_FETCH = True
    for t in FILERS:
        s = submissions(t, refresh)
        f = companyfacts(t, refresh)
        n = sum(len(u) for tax in f["facts"].values() for c in tax.values() for u in c["units"].values())
        log(f"{t:5s} {s['name']:<32s} fiscal year ends {s.get('fiscalYearEnd')}  facts={n:,}")
