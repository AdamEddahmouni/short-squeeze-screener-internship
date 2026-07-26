import copy
import os
import threading
import time

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

# Loaded here for the same reason as the other core/*_api.py modules.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Blank by default - this whole module no-ops until a real connection string
# (e.g. a free MongoDB Atlas cluster) is set. Lets the integration team read
# results from anywhere instead of only localhost, without requiring MongoDB
# to run this app at all - the local JSON snapshot (ui/view.py's
# _write_snapshot()) remains the primary source of truth either way.
MONGODB_URI = os.environ.get("MONGODB_URI", "")
# `or` (not just a .get() default) - MONGODB_DB is present-but-blank in
# .env.example/.env's usual state, and .get()'s default only applies when the
# key is absent entirely, not when it's set to an empty string.
MONGODB_DB = os.environ.get("MONGODB_DB") or "short_squeeze_screener"
MONGODB_COLLECTION = "screener_snapshot"

CONNECT_TIMEOUT_MS = 3000

# The background latest-wins worker calls push_snapshot() at most once at a time. A hung or
# unreachable cluster therefore never blocks Tkinter, and this cooldown avoids retrying on every
# 15-second cycle after a failure.
RETRY_COOLDOWN_SECONDS = 60

_client = None
_last_failure = 0.0
_pending_lock = threading.Lock()
_pending_snapshot = None
_worker_running = False


def _get_client():
    global _client
    if _client is None:
        _client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=CONNECT_TIMEOUT_MS,
            connectTimeoutMS=CONNECT_TIMEOUT_MS,
        )
    return _client


def _push_worker():
    global _pending_snapshot, _worker_running

    while True:
        with _pending_lock:
            snapshot = _pending_snapshot
            _pending_snapshot = None
            if snapshot is None:
                _worker_running = False
                return
        push_snapshot(snapshot)


def push_snapshot_async(snapshot):
    """Queue a non-blocking Mongo push, collapsing any backlog to the newest snapshot."""
    global _pending_snapshot, _worker_running

    if not MONGODB_URI:
        return

    with _pending_lock:
        _pending_snapshot = copy.deepcopy(snapshot)
        if _worker_running:
            return
        _worker_running = True

    threading.Thread(target=_push_worker, daemon=True).start()


# Mirrors the same snapshot shape ui/view.py already writes to
# data/screener_snapshot.json (PROJECT_NOTES.md §9 contract) into MongoDB, as a
# single replaced document under _id "latest" - same "one current mirrored
# snapshot" semantics as the JSON file, not a growing history/time-series
# collection (a different feature, not built here). No-ops quietly if
# MONGODB_URI isn't set, matching every other optional integration in this
# codebase (FINNHUB_KEY, NEWSAPI_KEY, FINVIZ_API_KEY).
def push_snapshot(snapshot):
    global _last_failure

    if not MONGODB_URI:
        return

    now = time.time()
    if now - _last_failure < RETRY_COOLDOWN_SECONDS:
        return

    try:
        client = _get_client()
        db = client[MONGODB_DB]
        db[MONGODB_COLLECTION].replace_one(
            {"_id": "latest"},
            {"_id": "latest", "updated_at": now, "results": snapshot},
            upsert=True,
        )
    except PyMongoError as e:
        _last_failure = now
        print(f"⚠️ MongoDB snapshot push failed: {e}")
