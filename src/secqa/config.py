"""Settings, read from the environment and an optional `.env` file.

Every setting has a default except SEC_USER_AGENT, which the SEC requires for downloads
("Your Name your@email.com"). Nothing personal is hard-coded in the source.

    SEC_USER_AGENT   contact string sent to EDGAR (required only for `secqa setup`)
    SECQA_DATA_DIR   where downloaded data and the index live (default: ./data)
    SECQA_SNAPSHOT   ignore anything filed after this date (default: 2026-10-16), so a fresh
                     download reproduces the evaluated data even after new 10-Ks appear
    OLLAMA_HOST      Ollama server (default: http://localhost:11434)
    SECQA_MODEL      default chat model (default: qwen3:8b)
"""
import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent.parent


def _load_dotenv():
    """Minimal .env reader (KEY=VALUE lines); real environment variables win."""
    for path in (Path.cwd() / ".env", REPO_ROOT / ".env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
        return


_load_dotenv()


def _default_data_dir():
    # Running from a checkout: data/ next to src/. Installed elsewhere: ./data.
    if (REPO_ROOT / "pyproject.toml").exists():
        return REPO_ROOT / "data"
    return Path.cwd() / "data"


DATA_DIR = Path(os.environ.get("SECQA_DATA_DIR") or _default_data_dir()).resolve()
RAW = DATA_DIR / "raw"            # EDGAR cache, filing text, embedding index (not committed)
EVAL_DIR = REPO_ROOT / "data" / "eval"   # gold question sets (committed)
RESULTS_DIR = REPO_ROOT / "results"

SNAPSHOT = os.environ.get("SECQA_SNAPSHOT", "2026-10-16")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
if not OLLAMA_HOST.startswith("http"):
    OLLAMA_HOST = "http://" + OLLAMA_HOST
DEFAULT_MODEL = os.environ.get("SECQA_MODEL", "qwen3:8b")


def user_agent():
    return os.environ.get("SEC_USER_AGENT", "").strip()
