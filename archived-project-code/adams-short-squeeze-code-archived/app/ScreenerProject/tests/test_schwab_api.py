import os
import sys
import tempfile
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.schwab_api as schwab_api


def _configured():
    return patch.multiple(schwab_api, APP_KEY="test-key", APP_SECRET="test-secret")


def _fake_response(json_body, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_body
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return response


def _with_temp_token_store(test_fn):
    with tempfile.TemporaryDirectory() as directory:
        token_path = os.path.join(directory, "schwab_tokens.json")
        with patch.object(schwab_api, "TOKEN_STORE_PATH", token_path):
            test_fn()


# --- configuration / URL building ---

def test_is_configured_false_when_keys_blank():
    with patch.multiple(schwab_api, APP_KEY="", APP_SECRET=""):
        assert schwab_api.is_configured() is False


def test_is_configured_true_when_keys_set():
    with _configured():
        assert schwab_api.is_configured() is True


def test_build_authorize_url_contains_client_id_and_callback():
    with patch.multiple(schwab_api, APP_KEY="abc123", CALLBACK_URL="https://127.0.0.1:8182"):
        url = schwab_api.build_authorize_url()
    assert "client_id=abc123" in url
    assert "redirect_uri=https://127.0.0.1:8182" in url


def test_extract_code_from_redirect_url_parses_code():
    url = "https://127.0.0.1:8182/?code=abc.def-ghi&session=xyz"
    assert schwab_api._extract_code_from_redirect_url(url) == "abc.def-ghi"


def test_extract_code_from_redirect_url_raises_without_code():
    try:
        schwab_api._extract_code_from_redirect_url("https://127.0.0.1:8182/?session=xyz")
        raise AssertionError("Expected a ValueError for a missing 'code' parameter")
    except ValueError:
        pass


# --- token bootstrap / refresh ---

def test_bootstrap_tokens_from_redirect_url_saves_tokens():
    def run():
        with patch.object(schwab_api.requests, "post",
                           return_value=_fake_response({"access_token": "AT1", "refresh_token": "RT1"})):
            schwab_api.bootstrap_tokens_from_redirect_url("https://127.0.0.1:8182/?code=CODE1")

        tokens = schwab_api._load_tokens()
        assert tokens["access_token"] == "AT1"
        assert tokens["refresh_token"] == "RT1"
    _with_temp_token_store(run)


def test_get_valid_access_token_raises_without_tokens():
    def run():
        try:
            schwab_api._get_valid_access_token()
            raise AssertionError("Expected a RuntimeError when never authorized")
        except RuntimeError as e:
            assert "not yet authorized" in str(e)
    _with_temp_token_store(run)


def test_get_valid_access_token_raises_when_refresh_token_expired():
    def run():
        stale = time.time() - schwab_api.REFRESH_TOKEN_LIFETIME_SECONDS - 1
        schwab_api._save_tokens({
            "access_token": "AT1", "refresh_token": "RT1",
            "access_token_fetched_at": stale, "refresh_token_fetched_at": stale,
        })
        try:
            schwab_api._get_valid_access_token()
            raise AssertionError("Expected a RuntimeError for an expired refresh token")
        except RuntimeError as e:
            assert "7-day limit" in str(e)
    _with_temp_token_store(run)


def test_get_valid_access_token_reuses_fresh_access_token_without_refresh():
    def run():
        now = time.time()
        schwab_api._save_tokens({
            "access_token": "STILL_FRESH", "refresh_token": "RT1",
            "access_token_fetched_at": now, "refresh_token_fetched_at": now,
        })
        with patch.object(schwab_api.requests, "post") as mock_post:
            token = schwab_api._get_valid_access_token()
        assert token == "STILL_FRESH"
        mock_post.assert_not_called()
    _with_temp_token_store(run)


def test_get_valid_access_token_refreshes_when_near_expiry():
    def run():
        now = time.time()
        stale_access = now - schwab_api.ACCESS_TOKEN_LIFETIME_SECONDS  # past the refresh buffer
        schwab_api._save_tokens({
            "access_token": "OLD", "refresh_token": "RT1",
            "access_token_fetched_at": stale_access, "refresh_token_fetched_at": now,
        })
        with patch.object(schwab_api.requests, "post",
                           return_value=_fake_response({"access_token": "NEW", "refresh_token": "RT1"})):
            token = schwab_api._get_valid_access_token()
        assert token == "NEW"
    _with_temp_token_store(run)


# --- is_available() / health() ---

def test_is_available_false_when_not_configured():
    with patch.multiple(schwab_api, APP_KEY="", APP_SECRET=""):
        assert schwab_api.is_available() is False


def test_is_available_false_when_no_tokens_file():
    def run():
        with _configured():
            assert schwab_api.is_available() is False
    _with_temp_token_store(run)


def test_is_available_true_when_refresh_token_fresh():
    def run():
        now = time.time()
        schwab_api._save_tokens({
            "access_token": "AT1", "refresh_token": "RT1",
            "access_token_fetched_at": now, "refresh_token_fetched_at": now,
        })
        with _configured():
            assert schwab_api.is_available() is True
    _with_temp_token_store(run)


def test_health_reports_not_configured():
    with patch.multiple(schwab_api, APP_KEY="", APP_SECRET=""):
        assert schwab_api.health()["status"] == "not_configured"


def test_health_reports_not_yet_authorized():
    def run():
        with _configured():
            assert schwab_api.health()["status"] == "not_yet_authorized"
    _with_temp_token_store(run)


def test_health_reports_needs_reauth():
    def run():
        stale = time.time() - schwab_api.REFRESH_TOKEN_LIFETIME_SECONDS - 1
        schwab_api._save_tokens({
            "access_token": "AT1", "refresh_token": "RT1",
            "access_token_fetched_at": stale, "refresh_token_fetched_at": stale,
        })
        with _configured():
            assert schwab_api.health()["status"] == "needs_reauth"
    _with_temp_token_store(run)


def test_health_reports_ready():
    def run():
        now = time.time()
        schwab_api._save_tokens({
            "access_token": "AT1", "refresh_token": "RT1",
            "access_token_fetched_at": now, "refresh_token_fetched_at": now,
        })
        with _configured():
            health = schwab_api.health()
        assert health["status"] == "ready"
        assert health["refresh_token_expires_in_seconds"] > 0
    _with_temp_token_store(run)


# --- market data clients ---

def test_fetch_movers_parses_screeners():
    def run():
        now = time.time()
        schwab_api._save_tokens({
            "access_token": "AT1", "refresh_token": "RT1",
            "access_token_fetched_at": now, "refresh_token_fetched_at": now,
        })
        body = {"screeners": [{"symbol": "PRIM", "lastPrice": 5.0, "netChange": 15.0}]}
        with patch.object(schwab_api.requests, "get", return_value=_fake_response(body)) as mock_get:
            movers = schwab_api.fetch_movers()
        assert movers == body["screeners"]
        called_url = mock_get.call_args[0][0]
        assert "/movers/EQUITY_ALL" in called_url
    _with_temp_token_store(run)


def test_fetch_quotes_empty_symbols_returns_empty_dict_without_network_call():
    with patch.object(schwab_api.requests, "get") as mock_get:
        assert schwab_api.fetch_quotes([]) == {}
    mock_get.assert_not_called()


def test_fetch_quotes_joins_symbols():
    def run():
        now = time.time()
        schwab_api._save_tokens({
            "access_token": "AT1", "refresh_token": "RT1",
            "access_token_fetched_at": now, "refresh_token_fetched_at": now,
        })
        with patch.object(schwab_api.requests, "get", return_value=_fake_response({"PRIM": {}})) as mock_get:
            schwab_api.fetch_quotes(["PRIM", "SUBP"])
        assert mock_get.call_args[1]["params"]["symbols"] == "PRIM,SUBP"
    _with_temp_token_store(run)


def test_fetch_price_history_returns_candles():
    def run():
        now = time.time()
        schwab_api._save_tokens({
            "access_token": "AT1", "refresh_token": "RT1",
            "access_token_fetched_at": now, "refresh_token_fetched_at": now,
        })
        candles = [{"close": 4.0, "volume": 100}, {"close": 5.0, "volume": 200}]
        with patch.object(schwab_api.requests, "get", return_value=_fake_response({"candles": candles})):
            result = schwab_api.fetch_price_history("PRIM")
        assert result == candles
    _with_temp_token_store(run)


# --- historical-stats derivation/caching ---

def test_hist_stats_from_candles_hand_computed():
    candles = [{"close": c, "high": c + 0.5, "low": c - 0.5, "volume": 1000}
               for c in [10, 10, 10, 10, 10, 10, 20]]
    stats = schwab_api._hist_stats_from_candles(candles)
    assert stats["last_close"] == 20
    assert stats["prev_close"] == 10
    assert stats["avg_volume"] == 1000


def test_hist_stats_from_candles_none_on_insufficient_bars():
    assert schwab_api._hist_stats_from_candles([{"close": 10, "volume": 100}]) is None


def test_get_hist_stats_caches_within_ttl():
    schwab_api._hist_cache.clear()
    candles = [{"close": 4.0, "high": 4.2, "low": 3.8, "volume": 100},
               {"close": 5.0, "high": 5.2, "low": 4.8, "volume": 200}]
    with patch.object(schwab_api, "fetch_price_history", return_value=candles) as mock_fetch:
        first = schwab_api._get_hist_stats("CACHED")
        second = schwab_api._get_hist_stats("CACHED")
    assert first == second
    mock_fetch.assert_called_once()


# --- row building / scoring ---

def _fake_hist(rsi=40.0, vol_w=10.0, avg_volume=1_000_000, last_volume=6_000_000,
               last_close=5.0, prev_close=4.35, ttm_squeeze_on=False, ttm_squeeze_momentum=0.1):
    return {
        "rsi": rsi, "vol_w": vol_w, "avg_volume": avg_volume,
        "last_volume": last_volume, "last_close": last_close, "prev_close": prev_close,
        "ttm_squeeze_on": ttm_squeeze_on, "ttm_squeeze_momentum": ttm_squeeze_momentum,
    }


def test_build_row_computes_change_percent_and_rel_volume():
    quote = {"quote": {"lastPrice": 5.0, "closePrice": 4.35}}
    hist = _fake_hist()
    float_stats = {"float_shares": 5_000_000, "short_percent": 10.0, "shares_short": 500_000,
                   "short_interest_as_of": "2026-06-30", "_fetched_at": time.time()}

    with patch.object(schwab_api, "get_float_stats", return_value=float_stats):
        row = schwab_api._build_row("PRIM", quote, hist)

    assert row["ticker"] == "PRIM"
    assert row["_change_num"] == round(((5.0 - 4.35) / 4.35) * 100, 2)
    assert row["_relvol_num"] == round(6_000_000 / 1_000_000, 2)
    assert row["shares_short"] == 500_000
    assert row["days_to_cover"] == round(500_000 / 1_000_000, 2)
    assert row["ib_shortable_shares"] is None
    assert "ib_shortable_shares_not_applicable_schwab" in row["quality_flags"]


def test_build_row_falls_back_to_historical_close_when_quote_missing():
    quote = {"quote": {}}
    hist = _fake_hist(last_close=5.0, prev_close=4.35)
    float_stats = {"float_shares": None, "short_percent": None, "shares_short": None,
                   "short_interest_as_of": None, "_fetched_at": time.time()}

    with patch.object(schwab_api, "get_float_stats", return_value=float_stats):
        row = schwab_api._build_row("PRIM", quote, hist)

    assert row["price"] == "5.0"
    assert "shares_short_unavailable" in row["quality_flags"]
    assert "days_to_cover_unavailable" in row["quality_flags"]


# Regression tests for the Schwab hard-to-borrow signal (found live 2026-07-13 in the real
# /quotes response, reference.isHardToBorrow/htbQuantity/htbRate) - a borrow-availability signal
# similar to IB's tick 236, kept under its own schwab_htb_* name since it's a different
# provider's inventory figure, never substituted for shares_short.

def test_build_row_extracts_schwab_htb_fields_when_present():
    quote = {
        "quote": {"lastPrice": 5.0, "closePrice": 4.35},
        "reference": {"isHardToBorrow": True, "htbQuantity": 125000, "htbRate": 0.0825},
    }
    hist = _fake_hist()
    float_stats = {"float_shares": None, "short_percent": None, "shares_short": None,
                   "short_interest_as_of": None, "_fetched_at": time.time()}

    with patch.object(schwab_api, "get_float_stats", return_value=float_stats):
        row = schwab_api._build_row("PRIM", quote, hist)

    assert row["schwab_htb_quantity"] == 125000
    assert row["schwab_htb_rate"] == 0.0825
    assert row["schwab_is_hard_to_borrow"] is True
    assert row["schwab_htb_as_of"] is not None
    assert "schwab_htb_unavailable" not in row["quality_flags"]


def test_build_row_flags_schwab_htb_unavailable_when_reference_missing():
    quote = {"quote": {"lastPrice": 5.0, "closePrice": 4.35}}  # no "reference" key at all
    hist = _fake_hist()
    float_stats = {"float_shares": None, "short_percent": None, "shares_short": None,
                   "short_interest_as_of": None, "_fetched_at": time.time()}

    with patch.object(schwab_api, "get_float_stats", return_value=float_stats):
        row = schwab_api._build_row("PRIM", quote, hist)

    assert row["schwab_htb_quantity"] is None
    assert row["schwab_htb_as_of"] is None
    assert "schwab_htb_unavailable" in row["quality_flags"]


# 2026-07-17 redesign (SQUEEZE_FORMULA_REDESIGN_HANDOFF.md): rank_and_group_stocks_schwab() no
# longer scores/splits with core/scoring.py::score_setup() - it returns every candidate as a
# flat list, and controller.py classifies Prime/Subprime off the composite squeeze score
# (core/squeeze_score.py::classify_tier()) once corroboration/TTM Squeeze are available
# cross-provider. score_setup() is still used, unchanged, by score_tickers_for_corroboration()
# below - see tests/test_controller_snapshot.py for tier-classification coverage.
def test_rank_and_group_stocks_schwab_returns_flat_candidate_list():
    def fabricated_snapshot():
        return [
            {"ticker": "PRIM", "price": "5.00", "float_shares": "5000000", "rel_volume": "6.0",
             "change_percent": "15.0", "short_float_percent": "10.0", "shares_short": 500000,
             "days_to_cover": 2.5, "short_interest_as_of": "2026-06-30",
             "short_interest_source": "yfinance", "float_as_of": "2026-07-13T12:00:00+00:00",
             "float_source": "yfinance", "ib_shortable_shares": None,
             "ib_shortable_shares_as_of": None, "quality_flags": [],
             "_price_num": 5.0, "_change_num": 15.0, "_relvol_num": 6.0, "_shortfloat_num": 10.0,
             "_vol_w": 10.0, "_rsi": 40.0},
            {"ticker": "FAIL", "price": "50.00", "float_shares": "5000000", "rel_volume": "1.0",
             "change_percent": "1.0", "short_float_percent": "1.0", "shares_short": None,
             "days_to_cover": None, "short_interest_as_of": None, "short_interest_source": None,
             "float_as_of": "2026-07-13T12:00:00+00:00", "float_source": "yfinance",
             "ib_shortable_shares": None, "ib_shortable_shares_as_of": None,
             "quality_flags": ["shares_short_unavailable"],
             "_price_num": 50.0, "_change_num": 1.0, "_relvol_num": 1.0, "_shortfloat_num": 1.0,
             "_vol_w": 0.0, "_rsi": 50.0},
        ]

    with schwab_api._state_lock:
        schwab_api._latest_snapshot.clear()
        schwab_api._latest_snapshot.extend(fabricated_snapshot())

    with patch.object(schwab_api, "run_scan_cycle"):  # skip the live network scan
        candidates = schwab_api.rank_and_group_stocks_schwab()

    assert [s["Ticker"] for s in candidates] == ["PRIM", "FAIL"]


def test_rank_and_group_stocks_schwab_shape_matches_other_providers():
    with schwab_api._state_lock:
        schwab_api._latest_snapshot.clear()
        schwab_api._latest_snapshot.append({
            "ticker": "PRIM", "price": "5.00", "float_shares": "5000000", "rel_volume": "6.0",
            "change_percent": "15.0", "short_float_percent": "10.0", "shares_short": 500000,
            "days_to_cover": 2.5, "short_interest_as_of": "2026-06-30",
            "short_interest_source": "yfinance", "float_as_of": "2026-07-13T12:00:00+00:00",
            "float_source": "yfinance", "ib_shortable_shares": None,
            "ib_shortable_shares_as_of": None, "quality_flags": [],
            "_price_num": 5.0, "_change_num": 15.0, "_relvol_num": 6.0, "_shortfloat_num": 10.0,
            "_vol_w": 10.0, "_rsi": 40.0,
        })

    with patch.object(schwab_api, "run_scan_cycle"):
        candidates = schwab_api.rank_and_group_stocks_schwab()

    expected_keys = {"Ticker", "Price", "Float", "RelVolume", "ChangePercent",
                      "ShortFloat", "Target", "StopLoss", "Headline",
                      "SharesShort", "DaysToCover", "ShortInterestAsOf", "ShortInterestSource",
                      "FloatAsOf", "FloatSource", "IbShortableShares", "IbShortableSharesAsOf",
                      "SchwabHtbQuantity", "SchwabHtbRate", "SchwabIsHardToBorrow",
                      "SchwabHtbAsOf", "TtmSqueezeOn", "TtmSqueezeMomentum",
                      "IbBorrowFeeRate", "IbBorrowRebateRate", "IbBorrowRateAsOf", "QualityFlags"}
    assert set(candidates[0].keys()) == expected_keys


# Regression test for a real bug caught during live validation (2026-07-13): the movers price
# field is "lastPrice", not "last" as the public OpenAPI spec's schema names it. run_scan_cycle()
# briefly filtered on the wrong key, silently discarding every candidate.
def test_run_scan_cycle_filters_by_price_band_using_real_lastprice_field():
    movers_body = [
        {"symbol": "INBAND", "lastPrice": 5.0},
        {"symbol": "TOOLOW", "lastPrice": 1.0},
        {"symbol": "TOOHIGH", "lastPrice": 50.0},
    ]
    quotes_body = {"INBAND": {"quote": {"lastPrice": 5.0, "closePrice": 4.35}}}
    float_stats = {"float_shares": None, "short_percent": None, "shares_short": None,
                   "short_interest_as_of": None, "_fetched_at": time.time()}

    with schwab_api._state_lock:
        schwab_api._latest_snapshot.clear()

    with patch.object(schwab_api, "fetch_movers", return_value=movers_body), \
         patch.object(schwab_api, "fetch_quotes", return_value=quotes_body) as mock_fetch_quotes, \
         patch.object(schwab_api, "_get_hist_stats", return_value=_fake_hist()), \
         patch.object(schwab_api, "get_float_stats", return_value=float_stats):
        schwab_api.run_scan_cycle()

    # Only the in-band candidate should ever have been quoted - proves the $2-$20 filter actually
    # ran against real data, not silently matching zero/everything.
    assert mock_fetch_quotes.call_args[0][0] == ["INBAND"]
    with schwab_api._state_lock:
        snapshot = list(schwab_api._latest_snapshot)
    assert [s["ticker"] for s in snapshot] == ["INBAND"]


# --- score_tickers_for_corroboration() (cross-provider corroboration) ---

def test_score_tickers_for_corroboration_empty_list_returns_empty_dict_without_network_call():
    with patch.object(schwab_api, "fetch_quotes") as mock_fetch_quotes:
        assert schwab_api.score_tickers_for_corroboration([]) == {}
    mock_fetch_quotes.assert_not_called()


def test_score_tickers_for_corroboration_scores_each_ticker_independently():
    # PRIME clears all 4 criteria; WEAK clears none - proves the rubric is recomputed per-ticker
    # against Schwab's own numbers, not just copied from whatever IB already decided.
    quotes_body = {
        "PRIME": {"quote": {"lastPrice": 5.0, "closePrice": 4.35}},
        "WEAK": {"quote": {"lastPrice": 50.0, "closePrice": 49.9}},
    }
    strong_hist = _fake_hist(avg_volume=1_000_000, last_volume=6_000_000)
    weak_hist = _fake_hist(avg_volume=1_000_000, last_volume=1_000_000)
    strong_float = {"float_shares": 10_000_000, "short_percent": 8.0, "shares_short": 800_000,
                     "short_interest_as_of": "2026-06-30", "_fetched_at": time.time()}
    weak_float = {"float_shares": 10_000_000, "short_percent": 1.0, "shares_short": 100_000,
                  "short_interest_as_of": "2026-06-30", "_fetched_at": time.time()}

    def fake_hist_stats(ticker):
        return strong_hist if ticker == "PRIME" else weak_hist

    def fake_float_stats(ticker):
        return strong_float if ticker == "PRIME" else weak_float

    with patch.object(schwab_api, "fetch_quotes", return_value=quotes_body), \
         patch.object(schwab_api, "_get_hist_stats", side_effect=fake_hist_stats), \
         patch.object(schwab_api, "get_float_stats", side_effect=fake_float_stats):
        results = schwab_api.score_tickers_for_corroboration(["PRIME", "WEAK"])

    assert results["PRIME"]["score"] == 4
    assert results["WEAK"]["score"] == 0


# Regression test for the bug found live 2026-07-16: score_tickers_for_corroboration() computes
# Schwab's hard-to-borrow fields as part of building each row (same _build_row() the standalone
# Schwab-as-source path uses) but used to discard everything except the bare score, so the signal
# never reached IB-sourced rows even when corroboration successfully ran for that ticker.
def test_score_tickers_for_corroboration_carries_schwab_htb_fields_through():
    quotes_body = {
        "PRIME": {
            "quote": {"lastPrice": 5.0, "closePrice": 4.35},
            "reference": {"isHardToBorrow": True, "htbQuantity": 125000, "htbRate": 0.0825},
        },
    }
    hist = _fake_hist(avg_volume=1_000_000, last_volume=6_000_000)
    float_stats = {"float_shares": 10_000_000, "short_percent": 8.0, "shares_short": 800_000,
                    "short_interest_as_of": "2026-06-30", "_fetched_at": time.time()}

    with patch.object(schwab_api, "fetch_quotes", return_value=quotes_body), \
         patch.object(schwab_api, "_get_hist_stats", return_value=hist), \
         patch.object(schwab_api, "get_float_stats", return_value=float_stats):
        results = schwab_api.score_tickers_for_corroboration(["PRIME"])

    assert results["PRIME"]["schwab_htb_quantity"] == 125000
    assert results["PRIME"]["schwab_htb_rate"] == 0.0825
    assert results["PRIME"]["schwab_is_hard_to_borrow"] is True
    assert results["PRIME"]["schwab_htb_as_of"] is not None


def test_score_tickers_for_corroboration_omits_ticker_missing_from_quotes():
    with patch.object(schwab_api, "fetch_quotes", return_value={}):
        results = schwab_api.score_tickers_for_corroboration(["MISSING"])
    assert results == {}


def test_score_tickers_for_corroboration_omits_ticker_when_hist_unavailable():
    quotes_body = {"NOHIST": {"quote": {"lastPrice": 5.0, "closePrice": 4.35}}}
    with patch.object(schwab_api, "fetch_quotes", return_value=quotes_body), \
         patch.object(schwab_api, "_get_hist_stats", return_value=None):
        results = schwab_api.score_tickers_for_corroboration(["NOHIST"])
    assert results == {}


def test_score_tickers_for_corroboration_survives_fetch_quotes_failure():
    with patch.object(schwab_api, "fetch_quotes", side_effect=RuntimeError("boom")):
        results = schwab_api.score_tickers_for_corroboration(["ANY"])
    assert results == {}


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0

    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
