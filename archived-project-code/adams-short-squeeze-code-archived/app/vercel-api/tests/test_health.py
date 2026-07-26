import json
import os
import sys
from unittest.mock import patch

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from api import index


class _Collection:
    def __init__(self, document):
        self.document = document

    def find_one(self, *args, **kwargs):
        return self.document


def _payload(response):
    return json.loads(response.body)


def test_health_reports_missing_configuration():
    with patch.object(index, "MONGODB_URI", ""):
        response = index.health()
    assert response.status_code == 503
    assert _payload(response)["status"] == "misconfigured"


def test_health_reports_fresh_snapshot():
    with patch.object(index, "MONGODB_URI", "mongodb://configured"), \
            patch.object(index, "_get_collection", return_value=_Collection({"updated_at": 1000, "results": []})), \
            patch.object(index.time, "time", return_value=1015):
        response = index.health()
    assert response.status_code == 200
    assert _payload(response)["status"] == "ok"
    assert _payload(response)["snapshot_age_seconds"] == 15


def test_health_reports_stale_snapshot():
    with patch.object(index, "MONGODB_URI", "mongodb://configured"), \
            patch.object(index, "_get_collection", return_value=_Collection({"updated_at": 1000, "results": []})), \
            patch.object(index.time, "time", return_value=1061):
        response = index.health()
    assert response.status_code == 503
    assert _payload(response)["status"] == "stale"


def test_health_rejects_invalid_snapshot_shape():
    with patch.object(index, "MONGODB_URI", "mongodb://configured"), \
            patch.object(index, "_get_collection", return_value=_Collection({"updated_at": 1000})), \
            patch.object(index.time, "time", return_value=1015):
        response = index.health()
    assert response.status_code == 503
    assert _payload(response)["status"] == "unavailable"


def main():
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except Exception as error:
            print(f"FAIL {test.__name__}: {error}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
