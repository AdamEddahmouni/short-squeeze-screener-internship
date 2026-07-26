# One-time manual OAuth bootstrap for Schwab's Trader API. Run this directly:
#
#   python core/schwab_auth.py    (from app/ScreenerProject)
#
# Prerequisites: SCHWAB_APP_KEY/SCHWAB_APP_SECRET/SCHWAB_CALLBACK_URL set in .env, and the app's
# status on the Dev Portal is "Ready For Use" (see PROJECT_NOTES.md §7 for the full registration
# walkthrough). Re-run this whenever core/schwab_api.py's health() reports "needs_reauth" -
# Schwab's refresh tokens hard-expire after 7 days and cannot be silently renewed past that; there
# is no way around a fresh browser login at that point.
#
# Nothing is written to disk until step 3 succeeds - a mistyped or abandoned attempt leaves no
# partial/corrupt token file behind.
import os
import sys

# Running this file directly (python core/schwab_auth.py) puts this file's own directory
# (core/) on sys.path, not the project root - "from core import schwab_api" would otherwise
# fail with ModuleNotFoundError since there's no "core" package inside core/ itself.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import schwab_api


def main():
    if not schwab_api.is_configured():
        print("SCHWAB_APP_KEY / SCHWAB_APP_SECRET are not set in .env - copy them from the app "
              "you created on developer.schwab.com first (see .env.example).")
        sys.exit(1)

    print("1. Open this URL in a browser and log in with your Schwab brokerage credentials:\n")
    print(f"   {schwab_api.build_authorize_url()}\n")
    print("2. After granting consent, Schwab redirects to your callback URL. The browser will")
    print("   likely show a connection error there (nothing is actually listening on")
    print("   127.0.0.1) - that's expected. Copy the full URL from the browser's address bar")
    print("   anyway; it contains the authorization code Schwab needs.\n")

    redirect_url = input("3. Paste that full redirected URL here: ").strip()

    try:
        schwab_api.bootstrap_tokens_from_redirect_url(redirect_url)
    except Exception as e:
        print(f"⚠️ Authorization failed: {e}")
        sys.exit(1)

    print("\nSchwab authorized - tokens saved, core/schwab_api.py can now be used.")
    print("Refresh tokens last 7 days; re-run this script when health() reports 'needs_reauth'.")


if __name__ == "__main__":
    main()
