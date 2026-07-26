import json
import os
import threading
import time
from datetime import datetime, timezone


SNAPSHOT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "screener_snapshot.json")
# Breaking News (2026-07-16): same atomic-write/read/health primitives below, just a second file -
# view.py's refresh_breaking_news_tab() already computes this list every 15s on its own
# independent timer chain, this just persists it so api_server.py has something to serve.
NEWS_SNAPSHOT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "news_snapshot.json")
SCHEMA_VERSION = 1
STALE_AFTER_SECONDS = 60


def write_snapshot(snapshot, path=SNAPSHOT_PATH):
    """Atomically replace the current JSON snapshot without exposing a partial file to readers."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    temp_path = f"{path}.{os.getpid()}.{threading.get_ident()}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(snapshot, file, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def read_snapshot(path=SNAPSHOT_PATH):
    """Return the current list snapshot; absence is a valid not-yet-produced state."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as file:
        snapshot = json.load(file)
    if not isinstance(snapshot, list):
        raise ValueError("Screener snapshot must be a JSON list.")
    return snapshot


def snapshot_health(path=SNAPSHOT_PATH, stale_after_seconds=STALE_AFTER_SECONDS, now=None):
    """Describe snapshot readiness and freshness without treating a valid empty list as failure."""
    if not os.path.exists(path):
        return {
            "status": "starting",
            "schema_version": SCHEMA_VERSION,
            "snapshot_available": False,
            "snapshot_age_seconds": None,
            "last_updated": None,
        }

    try:
        read_snapshot(path)
    except (OSError, ValueError):
        return {
            "status": "unavailable",
            "schema_version": SCHEMA_VERSION,
            "snapshot_available": False,
            "snapshot_age_seconds": None,
            "last_updated": None,
        }

    now = time.time() if now is None else now
    modified_at = os.path.getmtime(path)
    age = max(0.0, now - modified_at)
    return {
        "status": "ok" if age <= stale_after_seconds else "stale",
        "schema_version": SCHEMA_VERSION,
        "snapshot_available": True,
        "snapshot_age_seconds": round(age, 1),
        "last_updated": datetime.fromtimestamp(modified_at, timezone.utc).isoformat(),
    }
