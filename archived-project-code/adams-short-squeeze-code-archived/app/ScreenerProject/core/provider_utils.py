import math
from datetime import datetime, timezone

# Small helpers shared across market-data providers (core/ib_api.py, core/schwab_api.py, ...) so
# each provider module doesn't reimplement the same numeric/date-parsing edge cases.


def is_valid_number(value):
    """True for a real, non-NaN number - guards against provider fields that come back as
    None or float('nan') instead of simply being omitted."""
    return value is not None and not (isinstance(value, float) and math.isnan(value))


def epoch_to_iso_date(epoch_seconds):
    """Unix epoch (seconds) -> ISO 8601 date string, or None if invalid. Used for
    provider-reported settlement/as-of dates (e.g. yfinance's dateShortInterest)."""
    if not is_valid_number(epoch_seconds):
        return None
    try:
        return datetime.fromtimestamp(epoch_seconds, timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None
