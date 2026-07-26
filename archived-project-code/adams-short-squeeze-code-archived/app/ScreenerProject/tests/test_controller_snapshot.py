import os
import sys
from types import ModuleType
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _module(name, **attributes):
    module = ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    return module


# Isolate the snapshot contract from model, network, and broker dependencies. The method under
# test is pure post-processing, so importing those large integrations would only make this
# offline regression test slower and less reliable.
_stubs = {
    "core.sentiment": _module(
        "core.sentiment", train_or_load_model=lambda: (None, None), classify_headlines=lambda *a: None
    ),
    "core.finviz_api": _module(
        "core.finviz_api", fetch_all_finviz_api_news=lambda: [], FINVIZ_API_KEY=""
    ),
    "core.yfinance_news_api": _module(
        "core.yfinance_news_api", fetch_yfinance_news=lambda tickers: []
    ),
    "core.newsapi_news_api": _module(
        "core.newsapi_news_api", fetch_newsapi_news=lambda tickers: [], NEWSAPI_KEY=""
    ),
    "core.filters": _module("core.filters", rank_and_group_stocks=lambda: []),
    "core.ib_api": _module(
        "core.ib_api",
        start_ib_connection=lambda: None,
        stop_ib_connection=lambda: None,
        is_ib_available=lambda: False,
        rank_and_group_stocks_ib=lambda: [],
    ),
    "core.schwab_api": _module(
        "core.schwab_api",
        is_available=lambda: False,
        rank_and_group_stocks_schwab=lambda: [],
        score_tickers_for_corroboration=lambda tickers: {},
        health=lambda: {"status": "not_configured", "detail": None},
    ),
}

with patch.dict(sys.modules, _stubs):
    from controller.controller import Controller
    from controller import controller as controller_module


_PRIM_ROW = ["PRIM", "5.0", "5000000", "6.0", "15.0", "20.0", "5.0",
             "Positive (84%)", "10.5",
             500000, 2.5, "2026-06-30", "yfinance",
             "2026-07-13T12:00:00+00:00", "yfinance",
             1000, "2026-07-13T12:00:15+00:00",
             None, None, None, None,
             None, None,
             None, None, None,
             None,
             None, None, [], [],
             False,
             False]  # squeeze_score, squeeze_score_breakdown, corroboration_score, corroborated_by, quality_flags, squeeze_confirmed, ttm_squeeze_fired


def test_snapshot_carries_short_float_as_number():
    controller = Controller.__new__(Controller)
    rows = [_PRIM_ROW]

    with patch.dict(os.environ, {"INCLUDE_SENTIMENT_OUTPUT": "true"}):
        snapshot = controller.get_snapshot(rows, [])

    assert len(snapshot) == 1
    assert snapshot[0]["schema_version"] == 1
    assert snapshot[0]["short_float_percent"] == 10.5
    assert snapshot[0]["sentiment_label"] == "Positive"
    assert snapshot[0]["sentiment_confidence"] == 0.84


def test_snapshot_carries_short_interest_provenance():
    controller = Controller.__new__(Controller)
    snapshot = controller.get_snapshot([_PRIM_ROW], [])

    entry = snapshot[0]
    assert entry["shares_short"] == 500000
    assert entry["days_to_cover"] == 2.5
    assert entry["short_interest_as_of"] == "2026-06-30"
    assert entry["short_interest_source"] == "yfinance"
    assert entry["float_as_of"] == "2026-07-13T12:00:00+00:00"
    assert entry["float_source"] == "yfinance"
    assert entry["ib_shortable_shares"] == 1000
    assert entry["ib_shortable_shares_as_of"] == "2026-07-13T12:00:15+00:00"
    assert entry["quality_flags"] == []


def test_snapshot_carries_schwab_htb_fields():
    controller = Controller.__new__(Controller)
    row = ["SCHW", "5.0", "5000000", "6.0", "15.0", "20.0", "5.0", "", "10.5",
           500000, 2.5, "2026-06-30", "yfinance", "2026-07-13T12:00:00+00:00", "yfinance",
           None, None,
           125000, 0.0825, True, "2026-07-13T20:38:11+00:00",
           None, None,
           None, None, None,
           None,
           None, None, [], [],
           False,
           False]

    snapshot = controller.get_snapshot([row], [])
    entry = snapshot[0]
    assert entry["schwab_htb_quantity"] == 125000
    assert entry["schwab_htb_rate"] == 0.0825
    assert entry["schwab_is_hard_to_borrow"] is True
    assert entry["schwab_htb_as_of"] == "2026-07-13T20:38:11+00:00"


def test_snapshot_can_omit_replaceable_sentiment_output():
    controller = Controller.__new__(Controller)
    rows = [_PRIM_ROW]

    with patch.dict(os.environ, {"INCLUDE_SENTIMENT_OUTPUT": "false"}):
        snapshot = controller.get_snapshot(rows, [])

    assert "sentiment_label" not in snapshot[0]
    assert "sentiment_confidence" not in snapshot[0]
    assert snapshot[0]["ticker"] == "PRIM"


def test_snapshot_uses_null_for_missing_short_float():
    controller = Controller.__new__(Controller)
    rows = [["SUBP", "8.0", "?", "2.0", "12.0", "10.0", "5.0", "", "N/A",
             None, None, None, None, None, None, None, None,
             None, None, None, None,
             None, None,
             None, None, None,
             None,
             None, None, [],
             ["shares_short_unavailable_finviz_export"],
             False,
             False]]

    snapshot = controller.get_snapshot([], rows)

    assert snapshot[0]["short_float_percent"] is None
    assert snapshot[0]["setup_tier"] == "subprime"
    assert snapshot[0]["shares_short"] is None
    assert snapshot[0]["quality_flags"] == ["shares_short_unavailable_finviz_export"]


# Regression tests for a real bug caught during live testing (2026-07-13): a Finviz key can be
# present in .env but dead (401 Unauthorized) - refresh_news_cache() must fall through to
# yfinance/NewsAPI whenever Finviz's call comes back empty, not only when no key is configured.

def test_refresh_news_cache_uses_finviz_when_it_actually_returns_data():
    controller = Controller.__new__(Controller)
    finviz_news = [{"headline": "Finviz headline", "tickers": ["PRIM"]}]

    with patch.object(Controller, "_should_use_finviz", staticmethod(lambda: True)), \
         patch.object(controller_module, "fetch_all_finviz_api_news", return_value=finviz_news) as mock_finviz, \
         patch.object(controller_module, "fetch_yfinance_news") as mock_yfinance:
        controller.refresh_news_cache(["PRIM"])

    assert controller.news_cache == finviz_news
    mock_finviz.assert_called_once()
    mock_yfinance.assert_not_called()


def test_refresh_news_cache_falls_back_to_yfinance_when_finviz_key_configured_but_empty():
    controller = Controller.__new__(Controller)
    yfinance_news = [{"headline": "Real yfinance headline", "tickers": ["PRIM"]}]

    with patch.object(Controller, "_should_use_finviz", staticmethod(lambda: True)), \
         patch.object(controller_module, "fetch_all_finviz_api_news", return_value=[]), \
         patch.object(controller_module, "fetch_yfinance_news", return_value=yfinance_news) as mock_yfinance:
        controller.refresh_news_cache(["PRIM"])

    assert controller.news_cache == yfinance_news
    mock_yfinance.assert_called_once_with(["PRIM"])


def test_refresh_news_cache_falls_back_to_newsapi_when_finviz_and_yfinance_both_empty():
    controller = Controller.__new__(Controller)
    newsapi_news = [{"headline": "NewsAPI headline", "tickers": ["PRIM"]}]

    with patch.object(Controller, "_should_use_finviz", staticmethod(lambda: True)), \
         patch.object(Controller, "_should_use_newsapi", staticmethod(lambda: True)), \
         patch.object(controller_module, "fetch_all_finviz_api_news", return_value=[]), \
         patch.object(controller_module, "fetch_yfinance_news", return_value=[]), \
         patch.object(controller_module, "fetch_newsapi_news", return_value=newsapi_news) as mock_newsapi:
        controller.refresh_news_cache(["PRIM"])

    assert controller.news_cache == newsapi_news
    mock_newsapi.assert_called_once_with(["PRIM"])


def test_provider_priority_defaults_to_ib_schwab_finviz():
    with patch.dict(os.environ, {"SCREENER_PROVIDER_PRIORITY": ""}):
        assert Controller._provider_priority() == ["ib", "schwab", "finviz"]


def test_provider_priority_respects_env_var_override():
    with patch.dict(os.environ, {"SCREENER_PROVIDER_PRIORITY": "schwab, ib"}):
        assert Controller._provider_priority() == ["schwab", "ib"]


def test_select_provider_prefers_earlier_available_provider_in_priority_order():
    controller = Controller.__new__(Controller)
    with patch.object(controller_module.ib_api, "is_ib_available", return_value=False), \
         patch.object(controller_module.schwab_api, "is_available", return_value=True), \
         patch.dict(os.environ, {"SCREENER_PROVIDER_PRIORITY": "ib,schwab,finviz"}):
        name, _is_available, _rank_fn = controller._select_provider()
    assert name == "schwab"


def test_select_provider_falls_back_to_finviz_when_none_available():
    controller = Controller.__new__(Controller)
    with patch.object(controller_module.ib_api, "is_ib_available", return_value=False), \
         patch.object(controller_module.schwab_api, "is_available", return_value=False), \
         patch.dict(os.environ, {"SCREENER_PROVIDER_PRIORITY": "ib,schwab,finviz"}):
        name, _is_available, _rank_fn = controller._select_provider()
    assert name == "finviz"


# --- _apply_corroboration() / corroborated_by, corroboration_score in the snapshot contract ---
# (CROSS_PROVIDER_CORROBORATION_PLAN.md §3: a label, not a filter - only attempted when IB won
# the cycle and Schwab is independently available, otherwise fields stay None/[] rather than
# fabricated.)

def test_apply_corroboration_skips_when_source_is_not_ib():
    controller = Controller.__new__(Controller)
    stock = {"Ticker": "PRIM"}
    with patch.object(controller_module.schwab_api, "is_available", return_value=True), \
         patch.object(controller_module.schwab_api, "score_tickers_for_corroboration") as mock_score:
        controller._apply_corroboration("schwab", [stock])
    mock_score.assert_not_called()
    assert stock["CorroborationScore"] is None
    assert stock["CorroboratedBy"] == []


def test_apply_corroboration_skips_when_schwab_unavailable():
    controller = Controller.__new__(Controller)
    stock = {"Ticker": "PRIM"}
    with patch.object(controller_module.schwab_api, "is_available", return_value=False), \
         patch.object(controller_module.schwab_api, "score_tickers_for_corroboration") as mock_score:
        controller._apply_corroboration("ib", [stock])
    mock_score.assert_not_called()
    assert stock["CorroborationScore"] is None
    assert stock["CorroboratedBy"] == []


def test_apply_corroboration_marks_confirmed_when_schwab_score_at_least_three():
    controller = Controller.__new__(Controller)
    prime_stock = {"Ticker": "PRIM"}
    subprime_stock = {"Ticker": "SUBP"}
    with patch.object(controller_module.schwab_api, "is_available", return_value=True), \
         patch.object(controller_module.schwab_api, "score_tickers_for_corroboration",
                      return_value={
                          "PRIM": {"score": 4, "schwab_htb_quantity": 125000,
                                   "schwab_htb_rate": 0.0825, "schwab_is_hard_to_borrow": True,
                                   "schwab_htb_as_of": "2026-07-16T00:00:00+00:00"},
                          "SUBP": {"score": 2, "schwab_htb_quantity": None,
                                   "schwab_htb_rate": None, "schwab_is_hard_to_borrow": None,
                                   "schwab_htb_as_of": None},
                      }) as mock_score:
        controller._apply_corroboration("ib", [prime_stock, subprime_stock])
    mock_score.assert_called_once_with(["PRIM", "SUBP"])
    assert prime_stock["CorroborationScore"] == 4
    assert prime_stock["CorroboratedBy"] == ["schwab"]
    assert subprime_stock["CorroborationScore"] == 2
    assert subprime_stock["CorroboratedBy"] == []
    # Regression for the bug found live 2026-07-16: Schwab's HTB fields, already fetched as part
    # of scoring, used to be discarded instead of reaching the IB-sourced row.
    assert prime_stock["SchwabHtbQuantity"] == 125000
    assert prime_stock["SchwabHtbRate"] == 0.0825
    assert prime_stock["SchwabIsHardToBorrow"] is True
    assert prime_stock["SchwabHtbAsOf"] == "2026-07-16T00:00:00+00:00"


def test_apply_corroboration_leaves_fields_empty_when_schwab_could_not_score_ticker():
    controller = Controller.__new__(Controller)
    stock = {"Ticker": "UNSCORED"}
    with patch.object(controller_module.schwab_api, "is_available", return_value=True), \
         patch.object(controller_module.schwab_api, "score_tickers_for_corroboration", return_value={}):
        controller._apply_corroboration("ib", [stock])
    assert stock["CorroborationScore"] is None
    assert stock["CorroboratedBy"] == []


def test_snapshot_carries_corroboration_fields():
    controller = Controller.__new__(Controller)
    row = list(_PRIM_ROW)
    row[-4] = ["schwab"]  # corroborated_by
    row[-5] = 4  # corroboration_score

    snapshot = controller.get_snapshot([row], [])

    assert snapshot[0]["corroboration_score"] == 4
    assert snapshot[0]["corroborated_by"] == ["schwab"]


def test_snapshot_defaults_corroboration_fields_when_absent():
    snapshot = Controller.__new__(Controller).get_snapshot([_PRIM_ROW], [])
    assert snapshot[0]["corroboration_score"] is None
    assert snapshot[0]["corroborated_by"] == []


# --- _apply_squeeze_score() / squeeze_score in the snapshot contract ---

def test_apply_squeeze_score_combines_available_inputs():
    stock = {"ShortFloat": "30", "IbBorrowFeeRate": 40, "DaysToCover": 8}
    Controller._apply_squeeze_score([stock])
    assert stock["SqueezeScore"] == 70.9  # hand-verified in tests/test_squeeze_score.py
    assert stock["SqueezeScoreBreakdown"] == {
        "short_float": 60.0, "borrow_fee": 80.0, "days_to_cover": 80.0, "ttm_squeeze": None,
    }


def test_apply_squeeze_score_none_when_all_inputs_missing():
    stock = {"ShortFloat": "?", "IbBorrowFeeRate": None, "DaysToCover": None}
    Controller._apply_squeeze_score([stock])
    assert stock["SqueezeScore"] is None


def test_apply_squeeze_score_covers_a_mixed_batch():
    prime_stock = {"ShortFloat": "50", "IbBorrowFeeRate": None, "DaysToCover": None}
    subprime_stock = {"ShortFloat": "0", "IbBorrowFeeRate": None, "DaysToCover": None}
    Controller._apply_squeeze_score([prime_stock, subprime_stock])
    assert prime_stock["SqueezeScore"] == 100.0
    assert subprime_stock["SqueezeScore"] == 0.0


def test_apply_squeeze_score_feeds_ttm_squeeze_into_the_composite():
    stock = {"ShortFloat": None, "IbBorrowFeeRate": None, "DaysToCover": None,
              "TtmSqueezeOn": True, "TtmSqueezeMomentum": 0.5}
    Controller._apply_squeeze_score([stock])
    assert stock["SqueezeScore"] == 100.0
    assert stock["SqueezeScoreBreakdown"]["ttm_squeeze"] == 100.0


def test_snapshot_carries_squeeze_score():
    controller = Controller.__new__(Controller)
    row = list(_PRIM_ROW)
    row[-7] = 70.9  # squeeze_score

    snapshot = controller.get_snapshot([row], [])
    assert snapshot[0]["squeeze_score"] == 70.9


def test_snapshot_defaults_squeeze_score_to_none_when_absent():
    snapshot = Controller.__new__(Controller).get_snapshot([_PRIM_ROW], [])
    assert snapshot[0]["squeeze_score"] is None


def test_snapshot_carries_squeeze_score_breakdown():
    controller = Controller.__new__(Controller)
    row = list(_PRIM_ROW)
    row[-6] = {"short_float": 60.0, "borrow_fee": 80.0, "days_to_cover": 80.0, "ttm_squeeze": None}  # squeeze_score_breakdown

    snapshot = controller.get_snapshot([row], [])
    assert snapshot[0]["squeeze_score_breakdown"] == {
        "short_float": 60.0, "borrow_fee": 80.0, "days_to_cover": 80.0, "ttm_squeeze": None,
    }


def test_snapshot_defaults_squeeze_score_breakdown_to_none_when_absent():
    snapshot = Controller.__new__(Controller).get_snapshot([_PRIM_ROW], [])
    assert snapshot[0]["squeeze_score_breakdown"] is None


# --- squeeze_confirmed in the snapshot contract (2026-07-17 redesign) ---

def test_snapshot_carries_squeeze_confirmed():
    controller = Controller.__new__(Controller)
    row = list(_PRIM_ROW)
    row[-2] = True  # squeeze_confirmed

    snapshot = controller.get_snapshot([row], [])
    assert snapshot[0]["squeeze_confirmed"] is True


def test_snapshot_defaults_squeeze_confirmed_to_false_when_absent():
    snapshot = Controller.__new__(Controller).get_snapshot([_PRIM_ROW], [])
    assert snapshot[0]["squeeze_confirmed"] is False


# --- ttm_squeeze_fired in the snapshot contract (2026-07-17, leading counterpart to
# squeeze_confirmed above) ---

def test_snapshot_carries_ttm_squeeze_fired():
    controller = Controller.__new__(Controller)
    row = list(_PRIM_ROW)
    row[-1] = True  # ttm_squeeze_fired

    snapshot = controller.get_snapshot([row], [])
    assert snapshot[0]["ttm_squeeze_fired"] is True


def test_snapshot_defaults_ttm_squeeze_fired_to_false_when_absent():
    snapshot = Controller.__new__(Controller).get_snapshot([_PRIM_ROW], [])
    assert snapshot[0]["ttm_squeeze_fired"] is False


# --- _apply_squeeze_confirmed() (core/squeeze_score.py::is_squeeze_confirmed(), 2026-07-17) ---

def test_apply_squeeze_confirmed_true_when_thresholds_met():
    stock = {"RelVolume": "6", "ChangePercent": "80", "TtmSqueezeMomentum": 0.5}
    Controller._apply_squeeze_confirmed([stock])
    assert stock["SqueezeConfirmed"] is True


def test_apply_squeeze_confirmed_false_when_move_too_small():
    stock = {"RelVolume": "6", "ChangePercent": "13", "TtmSqueezeMomentum": 0.5}
    Controller._apply_squeeze_confirmed([stock])
    assert stock["SqueezeConfirmed"] is False


# --- _apply_ttm_fired() (core/squeeze_score.py::is_ttm_squeeze_fired(), 2026-07-17) - the first
# in-memory cross-cycle per-ticker state this codebase has needed, so these tests call it twice
# in sequence to exercise real transitions rather than a single pure-function call. ---

def test_apply_ttm_fired_detects_a_real_transition_across_two_cycles():
    controller = Controller.__new__(Controller)
    cycle_one = [{"Ticker": "PRIM", "TtmSqueezeOn": True, "TtmSqueezeMomentum": 0.5}]
    controller._apply_ttm_fired("ib", cycle_one)
    assert cycle_one[0]["TtmSqueezeFired"] is False  # no prior observation yet

    cycle_two = [{"Ticker": "PRIM", "TtmSqueezeOn": False, "TtmSqueezeMomentum": 0.5}]
    controller._apply_ttm_fired("ib", cycle_two)
    assert cycle_two[0]["TtmSqueezeFired"] is True


def test_apply_ttm_fired_resets_state_on_a_provider_switch():
    # A same-ticker True->False flip across an IB<->Schwab failover isn't a real release - each
    # provider caches/fetches its own 30-day bars independently.
    controller = Controller.__new__(Controller)
    cycle_one = [{"Ticker": "PRIM", "TtmSqueezeOn": True, "TtmSqueezeMomentum": 0.5}]
    controller._apply_ttm_fired("ib", cycle_one)

    cycle_two = [{"Ticker": "PRIM", "TtmSqueezeOn": False, "TtmSqueezeMomentum": 0.5}]
    controller._apply_ttm_fired("schwab", cycle_two)
    assert cycle_two[0]["TtmSqueezeFired"] is False


def test_apply_ttm_fired_does_not_leak_state_for_a_ticker_that_drops_off_and_reappears():
    controller = Controller.__new__(Controller)
    controller._apply_ttm_fired("ib", [{"Ticker": "PRIM", "TtmSqueezeOn": True, "TtmSqueezeMomentum": 0.5}])
    controller._apply_ttm_fired("ib", [{"Ticker": "OTHER", "TtmSqueezeOn": False, "TtmSqueezeMomentum": 0.5}])

    reappeared = [{"Ticker": "PRIM", "TtmSqueezeOn": False, "TtmSqueezeMomentum": 0.5}]
    controller._apply_ttm_fired("ib", reappeared)
    assert reappeared[0]["TtmSqueezeFired"] is False


def test_apply_ttm_fired_preserves_prior_state_across_a_transient_none_gap():
    controller = Controller.__new__(Controller)
    controller._apply_ttm_fired("ib", [{"Ticker": "PRIM", "TtmSqueezeOn": True, "TtmSqueezeMomentum": 0.5}])
    # One cycle where TTM Squeeze couldn't be computed (e.g. fewer than 21 daily bars that cycle)
    # must not erase memory of the real prior "on" state.
    controller._apply_ttm_fired("ib", [{"Ticker": "PRIM", "TtmSqueezeOn": None, "TtmSqueezeMomentum": None}])

    cycle_three = [{"Ticker": "PRIM", "TtmSqueezeOn": False, "TtmSqueezeMomentum": 0.5}]
    controller._apply_ttm_fired("ib", cycle_three)
    assert cycle_three[0]["TtmSqueezeFired"] is True


def test_apply_ttm_fired_works_without_init_via_new():
    # Controller.__new__(Controller) skips __init__ (this whole file's established pattern) - the
    # method must not assume self._ttm_state/_ttm_state_source already exist.
    controller = Controller.__new__(Controller)
    stock = {"Ticker": "PRIM", "TtmSqueezeOn": True, "TtmSqueezeMomentum": 0.5}
    controller._apply_ttm_fired("ib", [stock])
    assert stock["TtmSqueezeFired"] is False


# --- _split_by_tier() (core/squeeze_score.py::classify_tier(), 2026-07-17 redesign) ---

def test_split_by_tier_classifies_off_squeeze_score_not_score_setup():
    prime_stock = {"Ticker": "PRIM", "ShortFloat": "10", "SqueezeScore": 75.0}
    subprime_stock = {"Ticker": "SUBP", "ShortFloat": "10", "SqueezeScore": 50.0}
    dropped_stock = {"Ticker": "DROP", "ShortFloat": "10", "SqueezeScore": 10.0}

    prime, subprime = Controller._split_by_tier([prime_stock, subprime_stock, dropped_stock])

    assert [s["Ticker"] for s in prime] == ["PRIM"]
    assert [s["Ticker"] for s in subprime] == ["SUBP"]


def test_split_by_tier_drops_prime_candidate_below_short_float_floor():
    # High composite score driven entirely by borrow fee/days-to-cover on a low-short-interest
    # name shouldn't alone qualify for Prime (core/squeeze_score.py::classify_tier()'s floor).
    stock = {"Ticker": "LOWSHORT", "ShortFloat": "1", "SqueezeScore": 90.0}
    prime, subprime = Controller._split_by_tier([stock])
    assert prime == []
    assert subprime == [stock]


# --- _apply_quality_flags() (2026-07-17 redesign - observational, never a scoring input) ---

def test_apply_quality_flags_marks_sentiment_mismatch_for_prime_with_neutral_sentiment():
    prime_stock = {"Ticker": "PRIM", "IbBorrowFeeRate": 5.0}
    Controller._apply_quality_flags("ib", [prime_stock], [], sentiment_for=lambda t: "Neutral (60%)")
    assert "sentiment_mismatch" in prime_stock["QualityFlags"]


def test_apply_quality_flags_no_mismatch_for_prime_with_positive_sentiment():
    prime_stock = {"Ticker": "PRIM", "IbBorrowFeeRate": 5.0}
    Controller._apply_quality_flags("ib", [prime_stock], [], sentiment_for=lambda t: "Positive (90%)")
    assert "sentiment_mismatch" not in prime_stock.get("QualityFlags", [])


def test_apply_quality_flags_no_mismatch_check_for_subprime():
    subprime_stock = {"Ticker": "SUBP", "IbBorrowFeeRate": 5.0}
    Controller._apply_quality_flags("ib", [], [subprime_stock], sentiment_for=lambda t: "Neutral (60%)")
    assert "sentiment_mismatch" not in subprime_stock.get("QualityFlags", [])


def test_apply_quality_flags_marks_borrow_fee_feed_down_when_every_ib_row_missing_it():
    stock_a = {"Ticker": "A", "IbBorrowFeeRate": None}
    stock_b = {"Ticker": "B", "IbBorrowFeeRate": None}
    Controller._apply_quality_flags("ib", [stock_a], [stock_b], sentiment_for=lambda t: "")
    assert "borrow_fee_feed_down" in stock_a["QualityFlags"]
    assert "borrow_fee_feed_down" in stock_b["QualityFlags"]


def test_apply_quality_flags_no_feed_down_when_some_rows_have_borrow_fee():
    stock_a = {"Ticker": "A", "IbBorrowFeeRate": None}
    stock_b = {"Ticker": "B", "IbBorrowFeeRate": 5.0}
    Controller._apply_quality_flags("ib", [stock_a], [stock_b], sentiment_for=lambda t: "")
    assert "borrow_fee_feed_down" not in stock_a.get("QualityFlags", [])


def test_apply_quality_flags_extends_rather_than_overwrites_existing_flags():
    # core/filters.py's Finviz path already populates QualityFlags (e.g.
    # "shares_short_unavailable_finviz_export") - this must be preserved, not clobbered.
    prime_stock = {"Ticker": "PRIM", "IbBorrowFeeRate": 5.0,
                   "QualityFlags": ["short_float_percent_provider_supplied"]}
    Controller._apply_quality_flags("ib", [prime_stock], [], sentiment_for=lambda t: "Negative (70%)")
    assert "short_float_percent_provider_supplied" in prime_stock["QualityFlags"]
    assert "sentiment_mismatch" in prime_stock["QualityFlags"]


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except AssertionError as error:
            print(f"FAIL {test.__name__}: {error}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
