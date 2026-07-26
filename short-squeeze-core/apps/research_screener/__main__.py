"""One-command launcher: ``python -m apps.research_screener``."""

from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from . import APP_TITLE, DISCLAIMER
from .deployment import DeploymentMode, RuntimeConfig, resolve_runtime
from .config import resolve_application_config
from .paths import FrozenLayout
from .live_providers import configure_application
from .providers import provider_health
from .server import DEFAULT_PORT, HOST, build_server, default_export_dir, find_free_port


def _preflight(runtime_config: RuntimeConfig) -> tuple[bool, list[str]]:
    """Report what is available before the browser opens. Never blocks startup."""
    lines: list[str] = []
    if runtime_config.use_frozen_demo:
        from .frozen_demo import load_frozen_demo

        frozen_ok = bool(load_frozen_demo()["rows"])
        source_label = "sanitized frozen demo"
    else:
        layout = FrozenLayout()
        frozen_ok = layout.available
        source_label = "private canonical freeze"
    lines.append(
        f"  Frozen Research artifacts : {'FOUND' if frozen_ok else 'NOT FOUND'}"
        f"  ({source_label})"
    )
    if runtime_config.enable_local_ibkr:
        for entry in provider_health(frozen_available=frozen_ok):
            lines.append(f"  {entry['name']:<26}: {entry['state']}")
    else:
        lines.extend([
            "  IB Gateway                : UNAVAILABLE (cloud/frozen mode; not probed)",
            "  Market Data               : UNAVAILABLE",
            "  Historical Bars           : UNAVAILABLE",
        ])
    return frozen_ok, lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apps.research_screener",
        description=f"{APP_TITLE} — {DISCLAIMER}",
    )
    parser.add_argument("--port", type=int, default=None, help="preferred port")
    parser.add_argument(
        "--mode",
        choices=[str(mode) for mode in DeploymentMode],
        default=None,
        help="deployment mode (default: SQUEEZE_APP_MODE or LOCAL_FULL)",
    )
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser")
    parser.add_argument(
        "--export-dir", type=Path, default=None, help="where research snapshots are written"
    )
    parser.add_argument("--verbose", action="store_true", help="log every HTTP request")
    parser.add_argument(
        "--provider-config", type=Path, default=None,
        help="explicit private provider configuration path (production opt-in)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="explicit non-secret application configuration file",
    )
    parser.add_argument(
        "--check", action="store_true", help="print availability and exit without serving"
    )
    return parser


def _default_private_config() -> Path | None:
    """Auto-detect the repository-private providers file when not given explicitly."""
    candidate = Path(__file__).resolve().parents[2] / ".private" / "providers.env"
    return candidate if candidate.is_file() else None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    private_file = args.provider_config or _default_private_config()
    application_config = resolve_application_config(
        cli={
            "SQUEEZE_APP_MODE": args.mode,
            "PORT": str(args.port) if args.port is not None else None,
        },
        config_file=args.config,
        private_file=private_file,
    )
    runtime_config = RuntimeConfig(
        mode=application_config.deployment.mode,
        host=application_config.deployment.host,
        port=application_config.deployment.port,
        load_private=application_config.deployment.mode is DeploymentMode.LOCAL_FULL,
        enable_local_ibkr=application_config.providers.ibkr.enabled,
        use_frozen_demo=application_config.deployment.mode is not DeploymentMode.LOCAL_FULL,
    )
    runtime = configure_application(application_config)
    if runtime_config.enable_local_ibkr:
        from .session_state import ScreenerSession, reset_session
        reset_session(ScreenerSession(external_providers=runtime))
    else:
        from .provider_session import CloudUnavailableProvider
        from .session_state import ScreenerSession, reset_session

        reset_session(ScreenerSession(
            provider=CloudUnavailableProvider(), external_providers=runtime,
        ))

    print(f"\n{APP_TITLE}")
    print(DISCLAIMER)
    print("\nAvailability:")
    frozen_ok, lines = _preflight(runtime_config)
    for line in lines:
        print(line)

    if not frozen_ok:
        print(
            "\n  Frozen Research mode is unavailable on this machine. The application "
            "will still start; it will report the artifacts as missing rather than "
            "showing anything in their place."
        )
    if args.check:
        return 0

    port = (
        find_free_port(runtime_config.port)
        if runtime_config.mode is DeploymentMode.LOCAL_FULL
        else runtime_config.port
    )
    export_dir = args.export_dir or default_export_dir()
    server = build_server(
        port,
        export_dir=export_dir,
        verbose=args.verbose,
        host=runtime_config.host,
        deployment_mode=runtime_config.mode,
    )
    display_host = HOST if runtime_config.host == "0.0.0.0" else runtime_config.host
    url = f"http://{display_host}:{port}/"

    print(f"\n  Exports        : {export_dir}")
    print(f"\n  Screener ready : {url}")
    print("  Press Ctrl+C to stop.\n")

    if not args.no_browser and runtime_config.mode is DeploymentMode.LOCAL_FULL:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
