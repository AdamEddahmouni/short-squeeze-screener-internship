import os
import re
import time

from curl_cffi import requests as curl_requests
from dotenv import load_dotenv

# Loaded here for the same reason as the other core/*_api.py modules.
_ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(_ENV_PATH)

FINVIZ_USERNAME = os.environ.get("FINVIZ_USERNAME", "")
FINVIZ_PASSWORD = os.environ.get("FINVIZ_PASSWORD", "")

# Real endpoint/POST format, confirmed against a working open-source Finviz
# client (github.com/ppaanngggg/finviz-proxy's EliteLogin) rather than guessed -
# Finviz's own login form isn't documented anywhere official. A plain
# requests.post() here gets blocked (TLS-fingerprint bot detection); curl_cffi
# (already a transitive yfinance dependency in this project, so no new package)
# impersonates a real Chrome TLS fingerprint to get through, matching what a
# real browser's login looks like at the network level - this isn't bypassing
# any auth check, just avoiding a fingerprint-based block on non-browser clients
# hitting your own account with your own credentials.
_LOGIN_URL = "https://finviz.com/login_submit.ashx"

# Confirmed 2026-07-09 against the real page (a user screenshot, not a guess):
# Finviz's own "How to automate exports" walkthrough lives at /api_explanation
# and displays the account's export token directly - both as a "userToken"
# field and inline in an example URL's "&auth=" parameter. The token itself is
# a UUID (e.g. "00000000-0000-0000-0000-000000000000"), not a plain hex string -
# the original regex only matched contiguous hex, which is why it silently
# missed the hyphenated UUID format on every earlier page checked.
_CANDIDATE_PAGES = [
    "https://elite.finviz.com/api_explanation",
]

_AUTH_TOKEN_RE = re.compile(
    r"[?&]auth=([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
    re.IGNORECASE,
)


def _login(session):
    resp = session.post(
        _LOGIN_URL,
        data={"email": FINVIZ_USERNAME, "password": FINVIZ_PASSWORD},
        impersonate="chrome",
        timeout=15,
    )
    # A successful login redirects to elite.finviz.com - same success check the
    # reference implementation uses. Wrong credentials keep you on finviz.com.
    return resp.status_code == 200 and "elite.finviz.com" in str(resp.url)


def _find_auth_token(session):
    for url in _CANDIDATE_PAGES:
        try:
            resp = session.get(url, impersonate="chrome", timeout=15)
        except Exception as e:
            print(f"⚠️ Finviz token lookup failed for {url}: {e}")
            continue

        match = _AUTH_TOKEN_RE.search(resp.text)
        if match:
            return match.group(1)

    return None


def _write_token_to_env(token):
    lines = []
    if os.path.exists(_ENV_PATH):
        with open(_ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.startswith("FINVIZ_API_KEY="):
            lines[i] = f"FINVIZ_API_KEY={token}\n"
            updated = True
            break

    if not updated:
        lines.append(f"FINVIZ_API_KEY={token}\n")

    with open(_ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


# Logs into Finviz Elite with FINVIZ_USERNAME/FINVIZ_PASSWORD (set in .env, never
# passed as arguments so nothing prints them to a terminal/log), scrapes the
# account's export API token off a logged-in page, and writes it to .env as
# FINVIZ_API_KEY. Returns the token on success, None on any failure - deliberately
# a manual/on-demand script (see __main__ below), not wired into automatic app
# startup, since repeated automated logins against a real account risk tripping
# Finviz's own bot/lockout protections. Re-run this by hand if the token ever
# needs refreshing.
def fetch_finviz_api_token():
    if not FINVIZ_USERNAME or not FINVIZ_PASSWORD:
        print("⚠️ FINVIZ_USERNAME/FINVIZ_PASSWORD not set in .env - nothing to do.")
        return None

    session = curl_requests.Session()

    if not _login(session):
        print("⚠️ Finviz login failed - check FINVIZ_USERNAME/FINVIZ_PASSWORD in .env.")
        return None

    token = _find_auth_token(session)
    if token is None:
        print(
            "⚠️ Logged in, but couldn't find the export auth token on any checked page. "
            "Log into elite.finviz.com manually and copy it from the Export/Elite account "
            "page, then set FINVIZ_API_KEY in .env by hand."
        )
        return None

    return token


if __name__ == "__main__":
    found = fetch_finviz_api_token()
    if found:
        _write_token_to_env(found)
        print(f"✅ FINVIZ_API_KEY updated in .env (token ends in ...{found[-6:]}).")
