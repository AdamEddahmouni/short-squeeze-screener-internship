"""Spawn the screener server in a new console window."""
import subprocess, os, sys

bat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "START_SERVER.bat")
subprocess.Popen(
    ["cmd", "/c", "start", "Short Squeeze Screener", bat],
    creationflags=subprocess.CREATE_NEW_CONSOLE,
    shell=False,
)
print("Server starting in new window. Open http://127.0.0.1:8787")
