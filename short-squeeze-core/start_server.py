"""Start the Short Squeeze Research Screener server.

Usage: .venv\\Scripts\\python.exe start_server.py
"""
from apps.research_screener.__main__ import main
import sys
sys.exit(main(["--no-browser"]))
