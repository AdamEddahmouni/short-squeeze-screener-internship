import asyncio
import os
import sys
import tempfile
import threading
import time
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx

import api_server
from core import mongo_client, snapshot_store


def _get(path):
    async def request():
        transport = httpx.ASGITransport(app=api_server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path)
    return asyncio.run(request())


def test_atomic_store_and_api_accept_valid_empty_result():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "snapshot.json")
        snapshot_store.write_snapshot([], path)

        assert snapshot_store.read_snapshot(path) == []
        assert not [name for name in os.listdir(directory) if name.endswith(".tmp")]

        with patch.object(api_server, "SNAPSHOT_PATH", path):
            health = _get("/health")
            response = _get("/screener")

        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        assert health.json()["schema_version"] == 1
        assert response.status_code == 200
        assert response.json() == []


def test_failed_atomic_write_preserves_previous_snapshot():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "snapshot.json")
        original = [{"schema_version": 1, "ticker": "KEEP"}]
        snapshot_store.write_snapshot(original, path)

        def fail_during_dump(snapshot, file, **kwargs):
            file.write("[")
            raise OSError("simulated disk failure")

        with patch.object(snapshot_store.json, "dump", fail_during_dump):
            try:
                snapshot_store.write_snapshot([{"ticker": "DROP"}], path)
                raise AssertionError("Expected the simulated write failure")
            except OSError:
                pass

        assert snapshot_store.read_snapshot(path) == original
        assert not [name for name in os.listdir(directory) if name.endswith(".tmp")]


def test_local_health_reports_stale_snapshot():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "snapshot.json")
        snapshot_store.write_snapshot([], path)
        modified_at = os.path.getmtime(path)
        health = snapshot_store.snapshot_health(path, now=modified_at + 61)

        assert health["status"] == "stale"
        assert health["snapshot_age_seconds"] == 61


def test_api_reports_starting_and_rejects_malformed_snapshot():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "snapshot.json")
        with patch.object(api_server, "SNAPSHOT_PATH", path):
            assert _get("/health").status_code == 503
            assert _get("/health").json()["status"] == "starting"
            assert _get("/screener").json() == []

            with open(path, "w", encoding="utf-8") as file:
                file.write("not json")
            health = _get("/health")
            response = _get("/screener")

        assert health.status_code == 503
        assert health.json()["status"] == "unavailable"
        assert response.status_code == 503
        assert response.json()["detail"].startswith("Snapshot unavailable:")


def test_mongo_async_delivery_keeps_only_latest_pending_snapshot():
    started = threading.Event()
    release = threading.Event()
    finished = threading.Event()
    calls = []

    def fake_push(snapshot):
        calls.append(snapshot)
        if len(calls) == 1:
            started.set()
            assert release.wait(timeout=2)
        if len(calls) == 2:
            finished.set()

    with patch.object(mongo_client, "MONGODB_URI", "mongodb://configured"), \
            patch.object(mongo_client, "push_snapshot", fake_push):
        with mongo_client._pending_lock:
            mongo_client._pending_snapshot = None
            mongo_client._worker_running = False

        mongo_client.push_snapshot_async([{"cycle": 1}])
        assert started.wait(timeout=2)
        mongo_client.push_snapshot_async([{"cycle": 2}])
        mongo_client.push_snapshot_async([{"cycle": 3}])
        release.set()
        assert finished.wait(timeout=2)

        deadline = time.time() + 2
        while mongo_client._worker_running and time.time() < deadline:
            time.sleep(0.01)

    assert calls == [[{"cycle": 1}], [{"cycle": 3}]]
    assert mongo_client._worker_running is False


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
