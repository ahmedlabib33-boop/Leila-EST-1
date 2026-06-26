import json
import time
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"
SHARED_SESSION_FILE = DATA_DIR / "shared_session.json"
SHARED_NOTES_FILE = DATA_DIR / "shared_explanation_notes.txt"


def _read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_shared_page(default_page="Home"):
    data = _read_json(SHARED_SESSION_FILE, {})
    page = data.get("active_page") or default_page
    updated_at = float(data.get("updated_at") or 0)
    return page, updated_at


def write_shared_page(page):
    DATA_DIR.mkdir(exist_ok=True)
    payload = {
        "active_page": page,
        "updated_at": time.time(),
    }
    SHARED_SESSION_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload["updated_at"]


def read_shared_notes():
    try:
        return SHARED_NOTES_FILE.read_text(encoding="utf-8")
    except Exception:
        return ""


def write_shared_notes(value):
    DATA_DIR.mkdir(exist_ok=True)
    SHARED_NOTES_FILE.write_text(value or "", encoding="utf-8")
