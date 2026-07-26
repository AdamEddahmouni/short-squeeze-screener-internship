# Cloud-hosted screener read API

A small, separate FastAPI app that serves the screener's latest results from
MongoDB over a public URL, so the integration team can read them from
anywhere instead of only `localhost:8000` (the existing
`app/ScreenerProject/api_server.py`).

**This does not run the screener itself.** The actual scanner (IB Gateway
connection, background scan loop, FinBERT sentiment) has to keep running on
your machine — it needs a persistent connection to your local IB Gateway and
a continuous background loop, neither of which a Vercel serverless function
can do (stateless, short-lived, no local network access). This app is just
the read-only half: it reads whatever `app/ScreenerProject` last pushed into
MongoDB and returns it as JSON.

The upstream screener's built-in sentiment fields are optional because the integration team is
developing its own sentiment component. Set `INCLUDE_SENTIMENT_OUTPUT=false` in the local
`ScreenerProject/.env` to omit those fields before the snapshot reaches MongoDB; this read API
requires no corresponding code change.

Same `/screener` + `/health` contract as `app/ScreenerProject/api_server.py`,
so a downstream consumer doesn't need to know or care which one they're
hitting.

`GET /health` returns `200` only when MongoDB has a snapshot no more than 60 seconds old. It
returns `503` with `misconfigured`, `starting`, `unavailable`, or `stale` otherwise. `GET /screener`
may validly return `[]` when a fresh scan has no qualifying stocks, so consumers should
use `/health` to distinguish that from a missing/stale producer. Every non-empty row includes
`schema_version: 1`.

## What you need to do (steps only you can do — account creation/deploys
aren't something I can do on your behalf)

### 1. Create a free MongoDB Atlas cluster
1. Sign up at [mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)
   (free tier, no card required for the M0 tier in most regions).
2. Create a free **M0** cluster.
3. Under **Database Access**, create a database user (username + password).
4. Under **Network Access**, add `0.0.0.0/0` (allow access from anywhere) —
   simplest for now since both your local machine and Vercel's servers need
   to reach it, and there's no sensitive data in this snapshot (public
   screener results, not credentials).
5. Click **Connect → Drivers**, copy the connection string. It looks like:
   `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority`

### 2. Wire the connection string into the local screener
In `app/ScreenerProject/.env`, add:
```
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```
That's it — `core/mongo_client.py` picks it up automatically next run and
starts pushing each cycle's snapshot into MongoDB alongside the existing
local `data/screener_snapshot.json` file. No key means it just no-ops, so
nothing breaks if you skip this step.

### 3. Deploy this folder to Vercel
1. Install the CLI once: `npm install -g vercel` (needs Node.js).
2. From inside `app/vercel-api/`, run:
   ```
   vercel login
   vercel deploy
   ```
3. When prompted, set the `MONGODB_URI` environment variable to the same
   connection string from step 1 (you can also add it later under the
   project's Settings → Environment Variables on vercel.com, then redeploy).
4. Vercel gives you a public URL (e.g. `https://your-project.vercel.app`) —
   `GET /screener` and `GET /health` work the same as the local API, just
   reachable from anywhere.

## Notes
- The MongoDB mirror was verified against a real Atlas cluster. The Vercel read API is not yet
  deployed; its deployment steps still need to be completed by whoever owns the target account.
- The local JSON snapshot remains the primary source of truth; this is an
  additional, optional sink. If MongoDB is ever unreachable, the screener
  app itself is unaffected: delivery uses a non-blocking latest-wins worker plus a bounded retry
  cooldown, so cloud latency never blocks the UI or builds a stale queue.
