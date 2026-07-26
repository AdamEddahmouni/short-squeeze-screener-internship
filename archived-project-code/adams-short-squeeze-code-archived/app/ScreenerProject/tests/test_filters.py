import sys
import os
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.finviz_api as finviz_api
from core.filters import apply_filters, rank_and_group_stocks

# Hand-built CSV matching the real Finviz export's column names (core/filters.py reads these
# directly: Price/Prev Close feed the computed Change%, Shares Float is Finviz's "already in
# millions" shorthand so clean_float() multiplies by 1e6, Short Float is a "N%" string).
_MOCK_CSV = """Ticker,Price,Prev Close,Relative Volume,Shares Float,Short Float,Volatility (Week),Relative Strength Index (14),Change
PRIM,5.00,4.30,6.0,5,10%,10%,40,+16.3%
SUBP,8.00,7.14,2.0,5,8%,5%,55,+12.0%
FAIL,50.00,49.50,1.0,5,1%,0%,50,+1.0%
"""


class _FakeResponse:
    status_code = 200
    text = _MOCK_CSV


def _with_mocked_finviz(test_fn):
    with patch.object(finviz_api.requests, "get", return_value=_FakeResponse()):
        test_fn()


def test_apply_filters_keeps_only_stocks_passing_every_criterion():
    def run():
        df = finviz_api.fetch_finviz_data()
        filtered = apply_filters(df)
        assert list(filtered["Ticker"]) == ["PRIM"]  # SUBP fails RelVolume, FAIL fails everything
    _with_mocked_finviz(run)


def test_rank_and_group_stocks_returns_flat_candidate_list():
    # 2026-07-17 redesign (SQUEEZE_FORMULA_REDESIGN_HANDOFF.md): rank_and_group_stocks() no
    # longer scores/splits with core/scoring.py::score_setup() - it returns every candidate as a
    # flat list, and controller.py classifies Prime/Subprime off the composite squeeze score
    # (core/squeeze_score.py::classify_tier()) once corroboration/TTM Squeeze are available
    # cross-provider. See tests/test_controller_snapshot.py for tier-classification coverage.
    def run():
        candidates = rank_and_group_stocks()
        assert [s["Ticker"] for s in candidates] == ["PRIM", "SUBP", "FAIL"]
    _with_mocked_finviz(run)


def test_rank_and_group_stocks_shape():
    def run():
        candidates = rank_and_group_stocks()
        expected_keys = {"Ticker", "Price", "Float", "RelVolume", "ChangePercent",
                          "ShortFloat", "Target", "StopLoss", "Headline",
                          "SharesShort", "DaysToCover", "ShortInterestAsOf", "ShortInterestSource",
                          "FloatAsOf", "FloatSource", "IbShortableShares", "IbShortableSharesAsOf",
                          "SchwabHtbQuantity", "SchwabHtbRate", "SchwabIsHardToBorrow",
                          "SchwabHtbAsOf", "TtmSqueezeOn", "TtmSqueezeMomentum",
                      "IbBorrowFeeRate", "IbBorrowRebateRate", "IbBorrowRateAsOf", "QualityFlags"}
        assert set(candidates[0].keys()) == expected_keys
    _with_mocked_finviz(run)


def test_rank_and_group_stocks_flags_finviz_shares_short_as_unavailable():
    # Finviz's export supplies Short Float% directly but not a raw shares_short count this app
    # parses - shares_short must stay None (not fabricated from the percentage), and the reason
    # must be recorded rather than silently omitted.
    def run():
        candidates = rank_and_group_stocks()
        assert candidates[0]["SharesShort"] is None
        assert candidates[0]["ShortInterestSource"] is None
        assert "shares_short_unavailable_finviz_export" in candidates[0]["QualityFlags"]
    _with_mocked_finviz(run)


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")


if __name__ == "__main__":
    main()
