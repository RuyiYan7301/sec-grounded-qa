import pytest
import requests

from secqa import config, edgar


class Resp:
    def __init__(self, status, payload=None):
        self.status_code, self._payload = status, payload or {}
        self.text = "body"

    def json(self):
        return self._payload

    def raise_for_status(self):
        raise requests.HTTPError(str(self.status_code))


class Session:
    def __init__(self, *responses):
        self.responses, self.headers = list(responses), []

    def get(self, url, headers, timeout):
        self.headers.append(headers)
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


@pytest.fixture
def no_sleep(monkeypatch):
    waits = []
    monkeypatch.setattr(edgar.time, "sleep", waits.append)
    return waits


@pytest.fixture
def ua(monkeypatch):
    monkeypatch.setenv("SEC_USER_AGENT", "Test Person test@example.com")


def test_requires_user_agent(monkeypatch):
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    with pytest.raises(edgar.MissingUserAgent):
        edgar._get("https://data.sec.gov/x", session=Session())


def test_backs_off_on_throttling_then_succeeds(ua, no_sleep):
    s = Session(Resp(429), Resp(403), requests.ConnectionError("reset"), Resp(200, {"ok": 1}))
    assert edgar._get("https://data.sec.gov/x", session=s) == {"ok": 1}
    backoff = [w for w in no_sleep if w >= 1]
    assert backoff == [1, 2, 4]                       # exponential
    assert s.headers[0]["User-Agent"] == "Test Person test@example.com"


def test_gives_up_after_retries(ua, no_sleep):
    with pytest.raises(RuntimeError, match="gave up"):
        edgar._get("https://data.sec.gov/x", retries=2, session=Session(Resp(503), Resp(503)))


def test_does_not_retry_client_errors(ua, no_sleep):
    with pytest.raises(requests.HTTPError):
        edgar._get("https://data.sec.gov/x", session=Session(Resp(404)))


def test_cache_is_read_offline_and_missing_file_is_explained(monkeypatch, tmp_path):
    assert edgar.companyfacts("NVDA")["facts"]            # from the fixture cache, no network
    monkeypatch.setattr(config, "RAW", tmp_path)
    with pytest.raises(edgar.NotDownloaded, match="secqa setup"):
        edgar.companyfacts("NVDA")


def test_filing_url():
    assert edgar.filing_url("NVDA", "0001045810-24-000029") == (
        "https://www.sec.gov/Archives/edgar/data/1045810/000104581024000029/0001045810-24-000029-index.htm")
