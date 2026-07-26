import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Separate, minimal deployable app - NOT part of the ScreenerProject submodule.
# The actual screener (IB Gateway connection, background scan loop, FinBERT
# sentiment) has to keep running locally; it can't run as a Vercel serverless
# function (no persistent background process, no ability to reach a local IB
# Gateway from the cloud). This is just the read-only half: ScreenerProject's
# ui/view.py pushes each cycle's results into MongoDB (core/mongo_client.py),
# and this app serves that same data to the integration team from a public URL
# instead of only localhost:8000. Same /screener + /health contract as
# ScreenerProject/api_server.py (PROJECT_NOTES.md §9) so a downstream consumer
# doesn't need to care which one they're hitting.
MONGODB_URI = os.environ.get("MONGODB_URI", "")
# `or` (not just a .get() default) - MONGODB_DB is present-but-blank in the
# usual .env state, and .get()'s default only applies when the key is absent
# entirely, not when it's set to an empty string.
MONGODB_DB = os.environ.get("MONGODB_DB") or "short_squeeze_screener"
MONGODB_COLLECTION = "screener_snapshot"
SCHEMA_VERSION = 1
STALE_AFTER_SECONDS = 60

app = FastAPI()

_client = None


def _get_collection():
    global _client
    if not MONGODB_URI:
        raise HTTPException(
            status_code=500,
            detail="MONGODB_URI is not configured on this deployment.",
        )
    if _client is None:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return _client[MONGODB_DB][MONGODB_COLLECTION]


@app.get("/health")
def health():
    if not MONGODB_URI:
        return JSONResponse({
            "status": "misconfigured",
            "schema_version": SCHEMA_VERSION,
            "snapshot_available": False,
            "snapshot_age_seconds": None,
            "last_updated": None,
        }, status_code=503)

    try:
        doc = _get_collection().find_one({"_id": "latest"}, {"updated_at": 1, "results": 1})
    except PyMongoError:
        return JSONResponse({
            "status": "unavailable",
            "schema_version": SCHEMA_VERSION,
            "snapshot_available": False,
            "snapshot_age_seconds": None,
            "last_updated": None,
            "detail": "MongoDB health check failed.",
        }, status_code=503)

    if doc is None:
        return JSONResponse({
            "status": "starting",
            "schema_version": SCHEMA_VERSION,
            "snapshot_available": False,
            "snapshot_age_seconds": None,
            "last_updated": None,
        }, status_code=503)

    if not isinstance(doc.get("results"), list):
        return JSONResponse({
            "status": "unavailable",
            "schema_version": SCHEMA_VERSION,
            "snapshot_available": False,
            "snapshot_age_seconds": None,
            "last_updated": None,
            "detail": "MongoDB snapshot has an invalid result shape.",
        }, status_code=503)

    updated_at = doc.get("updated_at")
    if not isinstance(updated_at, (int, float)):
        return JSONResponse({
            "status": "stale",
            "schema_version": SCHEMA_VERSION,
            "snapshot_available": True,
            "snapshot_age_seconds": None,
            "last_updated": None,
        }, status_code=503)

    age = max(0.0, time.time() - updated_at)
    payload = {
        "status": "ok" if age <= STALE_AFTER_SECONDS else "stale",
        "schema_version": SCHEMA_VERSION,
        "snapshot_available": True,
        "snapshot_age_seconds": round(age, 1),
        "last_updated": datetime.fromtimestamp(updated_at, timezone.utc).isoformat(),
    }
    return JSONResponse(payload, status_code=200 if payload["status"] == "ok" else 503)


# Returns the latest snapshot ui/view.py pushed via core/mongo_client.py's
# push_snapshot() - empty list if nothing has been pushed yet (matches
# ScreenerProject/api_server.py's behavior when its local file doesn't exist
# yet), not an error, since "no data pushed yet" is a normal startup state.
@app.get("/screener")
def screener():
    collection = _get_collection()
    try:
        doc = collection.find_one({"_id": "latest"})
    except PyMongoError as e:
        raise HTTPException(status_code=502, detail=f"MongoDB read failed: {e}")

    if doc is None:
        return []

    return doc.get("results", [])
