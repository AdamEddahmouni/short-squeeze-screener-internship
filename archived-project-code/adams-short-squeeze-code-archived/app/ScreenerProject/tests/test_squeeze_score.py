import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.squeeze_score import (
    compute_squeeze_score,
    compute_squeeze_score_breakdown,
    classify_tier,
    is_squeeze_confirmed,
    is_ttm_squeeze_fired,
)


def test_all_inputs_at_half_saturation_average_to_fifty():
    # short_float=25 (of 50 saturation), borrow_fee=25 (of 50), days_to_cover=5 (of 10) - all
    # three land at exactly 50/100, so the weighted average is 50 regardless of the weights.
    assert compute_squeeze_score(25, 25, 5) == 50.0


def test_all_zero_inputs_score_zero():
    assert compute_squeeze_score(0, 0, 0) == 0.0


def test_all_missing_inputs_returns_none():
    assert compute_squeeze_score(None, None, None) is None


def test_single_saturated_input_alone_scores_one_hundred():
    # Only short_float provided, at exactly its saturation point - weight renormalizes to 1.0
    # across the single available input, so the composite is 100, not diluted by missing inputs.
    assert compute_squeeze_score(50, None, None) == 100.0


def test_value_beyond_saturation_point_clamps_at_one_hundred():
    assert compute_squeeze_score(100, None, None) == 100.0


def test_negative_input_clamps_at_zero():
    assert compute_squeeze_score(-10, None, None) == 0.0


def test_hand_computed_typical_squeeze_setup():
    # short_float=30 -> sub-score 60; borrow_fee=40 -> sub-score 80; days_to_cover=8 -> sub-score
    # 80. Weighted: 60*(25/55) + 80*(20/55) + 80*(10/55) = 70.909... -> 70.9
    assert compute_squeeze_score(30, 40, 8) == 70.9


def test_missing_borrow_fee_renormalizes_remaining_weights():
    # Only short_float and days_to_cover available - the score should be a weighted average of
    # just those two (weights 25 and 10, renormalized), not diluted by treating the missing
    # borrow_fee as zero.
    score = compute_squeeze_score(50, None, 10)  # both saturated -> both sub-scores are 100
    assert score == 100.0


def test_breakdown_returns_per_component_sub_scores():
    # 2026-07-17 redesign added ttm_squeeze as a 4th component (None here since no TTM args were
    # passed) - see the ttm_squeeze-specific tests below for its own behavior.
    breakdown = compute_squeeze_score_breakdown(30, 40, 8)
    assert breakdown == {
        "short_float": 60.0, "borrow_fee": 80.0, "days_to_cover": 80.0, "ttm_squeeze": None,
    }


def test_breakdown_preserves_none_for_missing_input():
    breakdown = compute_squeeze_score_breakdown(50, None, 10)
    assert breakdown == {
        "short_float": 100.0, "borrow_fee": None, "days_to_cover": 100.0, "ttm_squeeze": None,
    }


def test_breakdown_all_missing_returns_all_none():
    assert compute_squeeze_score_breakdown(None, None, None) == {
        "short_float": None, "borrow_fee": None, "days_to_cover": None, "ttm_squeeze": None,
    }


# --- ttm_squeeze as a 4th composite component (2026-07-17 redesign,
# SQUEEZE_FORMULA_REDESIGN_HANDOFF.md) - state-based, not saturating-linear, since only
# compute_ttm_squeeze()'s squeeze_on/momentum sign are reliable, not momentum's magnitude. ---

def test_ttm_squeeze_on_saturates_that_component_at_one_hundred():
    breakdown = compute_squeeze_score_breakdown(
        None, None, None, ttm_squeeze_on=True, ttm_squeeze_momentum=None
    )
    assert breakdown["ttm_squeeze"] == 100.0


def test_ttm_squeeze_off_with_positive_momentum_scores_sixty():
    breakdown = compute_squeeze_score_breakdown(
        None, None, None, ttm_squeeze_on=False, ttm_squeeze_momentum=0.5
    )
    assert breakdown["ttm_squeeze"] == 60.0


def test_ttm_squeeze_off_with_non_positive_or_missing_momentum_scores_zero():
    assert compute_squeeze_score_breakdown(
        None, None, None, ttm_squeeze_on=False, ttm_squeeze_momentum=-0.2
    )["ttm_squeeze"] == 0.0
    assert compute_squeeze_score_breakdown(
        None, None, None, ttm_squeeze_on=False, ttm_squeeze_momentum=None
    )["ttm_squeeze"] == 0.0


def test_ttm_squeeze_none_is_excluded_from_the_composite_not_zeroed():
    # ttm_squeeze_on=None (not enough bar history yet) must renormalize the other three weights,
    # matching this exact three-input case's already-hand-verified result.
    with_absent_ttm = compute_squeeze_score(30, 40, 8, ttm_squeeze_on=None, ttm_squeeze_momentum=None)
    assert with_absent_ttm == compute_squeeze_score(30, 40, 8) == 70.9


def test_squeeze_on_alone_scores_one_hundred_like_any_other_saturated_single_input():
    score = compute_squeeze_score(None, None, None, ttm_squeeze_on=True, ttm_squeeze_momentum=None)
    assert score == 100.0


# --- classify_tier() (2026-07-17 redesign, replaces core/scoring.py::score_setup() for tier
# classification - score_setup() itself is unchanged, only used for corroboration now) ---

def test_classify_tier_prime_requires_score_and_short_float_floor():
    assert classify_tier(70.0, 5.0) == "prime"
    assert classify_tier(90.0, 20.0) == "prime"


def test_classify_tier_high_score_without_short_float_floor_is_subprime_not_prime():
    assert classify_tier(90.0, 1.0) == "subprime"


def test_classify_tier_subprime_range_has_no_short_float_floor():
    assert classify_tier(40.0, 0) == "subprime"
    assert classify_tier(69.9, 0) == "subprime"


def test_classify_tier_below_subprime_floor_is_none():
    assert classify_tier(39.9, 50.0) is None
    assert classify_tier(0.0, 50.0) is None


def test_classify_tier_none_score_is_none():
    assert classify_tier(None, 50.0) is None


def test_classify_tier_missing_short_float_treated_as_zero_for_the_prime_floor():
    assert classify_tier(90.0, None) == "subprime"


# --- is_squeeze_confirmed() (2026-07-17 redesign) - independent of Prime/Subprime tier ---

def test_is_squeeze_confirmed_true_when_all_thresholds_met():
    assert is_squeeze_confirmed(rel_volume=6, change_percent=80, ttm_squeeze_momentum=0.5) is True


def test_is_squeeze_confirmed_true_with_negative_change_of_sufficient_magnitude():
    # Uses |change%|, not raw change% - a sharp drop is just as "actively squeezing" a signal of
    # the underlying volatility release as a sharp rise for this flag's purpose.
    assert is_squeeze_confirmed(rel_volume=6, change_percent=-80, ttm_squeeze_momentum=None) is True


def test_is_squeeze_confirmed_false_when_relvolume_too_low():
    assert is_squeeze_confirmed(rel_volume=4, change_percent=80, ttm_squeeze_momentum=0.5) is False


def test_is_squeeze_confirmed_false_when_change_too_small():
    # LBGJ-style move (advisor 2026-07-17: "the change is 13%... should be closer to 80, 90, 100").
    assert is_squeeze_confirmed(rel_volume=6, change_percent=13, ttm_squeeze_momentum=0.5) is False


def test_is_squeeze_confirmed_false_when_ttm_momentum_contradicts_the_move():
    assert is_squeeze_confirmed(rel_volume=6, change_percent=80, ttm_squeeze_momentum=-0.1) is False


def test_is_squeeze_confirmed_false_when_required_inputs_missing():
    assert is_squeeze_confirmed(rel_volume=None, change_percent=80, ttm_squeeze_momentum=0.5) is False
    assert is_squeeze_confirmed(rel_volume=6, change_percent=None, ttm_squeeze_momentum=0.5) is False


# --- is_ttm_squeeze_fired() (2026-07-17) - leading "compression just released" transition,
# independent of Prime/Subprime tier and squeeze_score, and of is_squeeze_confirmed() above ---

def test_is_ttm_squeeze_fired_true_on_a_real_on_to_off_transition():
    assert is_ttm_squeeze_fired(prev_squeeze_on=True, current_squeeze_on=False, current_momentum=0.5) is True


def test_is_ttm_squeeze_fired_true_with_momentum_none():
    # Momentum's exact value isn't always available/reliable - None must not block a real fire.
    assert is_ttm_squeeze_fired(prev_squeeze_on=True, current_squeeze_on=False, current_momentum=None) is True


def test_is_ttm_squeeze_fired_false_when_not_previously_on():
    # No prior compression to release from - can't have "just fired" without having been "on."
    assert is_ttm_squeeze_fired(prev_squeeze_on=False, current_squeeze_on=False, current_momentum=0.5) is False


def test_is_ttm_squeeze_fired_false_when_still_on():
    # Still compressed - hasn't released yet, nothing to flag.
    assert is_ttm_squeeze_fired(prev_squeeze_on=True, current_squeeze_on=True, current_momentum=0.5) is False


def test_is_ttm_squeeze_fired_false_when_momentum_contradicts():
    assert is_ttm_squeeze_fired(prev_squeeze_on=True, current_squeeze_on=False, current_momentum=-0.1) is False


def test_is_ttm_squeeze_fired_false_when_missing_prior_observation():
    # No prior cycle to compare against (first time seeing this ticker, or state was reset by a
    # provider switch) - never a fabricated True from absent data.
    assert is_ttm_squeeze_fired(prev_squeeze_on=None, current_squeeze_on=False, current_momentum=0.5) is False
