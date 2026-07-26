import os
import threading

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from core import (
    chart_data, corroboration_track_record, snapshot_store,
    squeeze_score_history, squeeze_score_track_record,
)

# Local integration API (PROJECT_NOTES.md §9): a thin, read-only wrapper around the same JSON
# file snapshot ui/view.py already writes every screener refresh cycle
# (data/screener_snapshot.json is the actual source of truth, not this server's own state) -
# so there's no cross-thread state sharing with Tkinter or the IB connection to get wrong, just a
# file read. Deliberately no auth/rate limiting/HTTPS - matches §9's original "local API, not a
# public one" scope; add those if this ever needs to serve outside localhost.
SNAPSHOT_PATH = snapshot_store.SNAPSHOT_PATH
NEWS_SNAPSHOT_PATH = snapshot_store.NEWS_SNAPSHOT_PATH
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
PORT = 8000

app = FastAPI(title="Short Squeeze Screener - Integration API")


# Web UI files change often during development, and neither StaticFiles nor FileResponse send a
# Cache-Control header by default - they do set ETag/Last-Modified, but without an explicit
# directive some browsers still serve an already-cached copy without ever asking the server
# whether it's stale (observed live 2026-07-17: a fixed app.js kept rendering the old, unfixed
# behavior in a real browser after being confirmed correct via curl). no-cache forces a cheap
# revalidation request on every load instead of trusting the browser's own heuristic freshness
# window - the browser still caches the bytes, it just always re-checks the ETag first.
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path == "/" or request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-cache"
        return response


app.add_middleware(NoCacheMiddleware)


@app.get("/health")
def health():
    health_data = snapshot_store.snapshot_health(SNAPSHOT_PATH)
    status_code = 200 if health_data["status"] == "ok" else 503
    return JSONResponse(health_data, status_code=status_code)


@app.get("/screener")
def screener():
    try:
        return JSONResponse(snapshot_store.read_snapshot(SNAPSHOT_PATH))
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=503, detail=f"Snapshot unavailable: {error}") from error


# Breaking News (2026-07-16): same read-only file-backed pattern as /screener, just a second
# snapshot - ui/view.py's refresh_breaking_news_tab() writes this one on its own independent 15s
# timer chain. An empty list is a valid "nothing high-confidence yet" state, same as /screener.
@app.get("/news")
def news():
    try:
        return JSONResponse(snapshot_store.read_snapshot(NEWS_SNAPSHOT_PATH))
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=503, detail=f"News snapshot unavailable: {error}") from error


# Chart (2026-07-16): web equivalent of the Tkinter Chart tab's plot_chart() (ui/view.py) - same
# 5-day/30-min yfinance series, fetched on demand rather than through the snapshot files since
# it's per-ticker and user-initiated, not part of the 15s scan cycle.
@app.get("/chart/{ticker}")
def chart(ticker: str):
    try:
        return JSONResponse(chart_data.fetch_chart_data(ticker.upper().strip()))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


# Squeeze Score history (2026-07-16): controller.py logs one row per Prime/Subprime ticker every
# scan cycle to data/squeeze_score_history.csv - this just serves it back per ticker so the web
# UI's Chart tab can overlay it against price. An empty list is valid ("no history logged for this
# ticker yet"), same convention as /news - not an error, so no 404 here unlike /chart.
@app.get("/squeeze-score-history/{ticker}")
def squeeze_score_history_route(ticker: str):
    return JSONResponse(squeeze_score_history.read_score_history(ticker))


# Track Record (2026-07-16): serves tests/evaluate_squeeze_score_outcomes.py's graded results
# (data/squeeze_score_outcomes.csv) as a band-level summary, so the evidence that script produces
# is something you can pull up in the web UI during a meeting rather than only existing as
# terminal output someone has to remember to run and paste in. An empty list is valid ("nothing
# graded yet" - picks need to age a day before the evaluator scores them), not an error.
@app.get("/squeeze-score-track-record")
def squeeze_score_track_record_route():
    return JSONResponse(squeeze_score_track_record.summarize_outcomes())


# Corroboration Track Record (2026-07-17): same evidence pattern as the Squeeze Score one, but for
# cross-provider corroboration specifically - the advisor's own explicit ask from a 2026-07-12
# call ("if TD Ameritrade is telling me... and interactive broker is telling me... then we know we
# have the right to invest"), which shipped as a label on every row but was never checked against
# real outcomes until tests/evaluate_corroboration_outcomes.py.
@app.get("/corroboration-track-record")
def corroboration_track_record_route():
    return JSONResponse(corroboration_track_record.summarize_outcomes())


# Web UI (2026-07-16): a read-only viewer on top of the routes above, nothing else - polls
# /health then /screener from the browser via fetch(), so there's no new server-side state or
# cross-thread coordination to get wrong here either. Route registered before the /static mount
# so FastAPI doesn't try to resolve "/" against StaticFiles first.
@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Runs the API in a background daemon thread so it doesn't block Tkinter's mainloop() - same
# background-thread pattern core/ib_api.py already uses for its own connection. Daemon=True means
# it exits automatically when the main process does; no explicit shutdown wiring needed for a
# local dev tool like this one.
def start_api_server(port=PORT):
    thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning"),
        daemon=True
    )
    thread.start()
    return thread
