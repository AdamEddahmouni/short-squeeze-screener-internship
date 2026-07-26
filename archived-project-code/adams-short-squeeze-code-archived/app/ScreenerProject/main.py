import sys
from tkinter import Tk
from controller.controller import Controller
from ui.view import View
from api_server import start_api_server

# This app's status prints use emoji (⚠️/❌/✅) throughout core/controller/ui. Python only
# guarantees UTF-8 stdout/stderr on Windows for an attached interactive console (PEP 528) - the
# moment output is redirected/piped (a log file, a process supervisor, this exact crash caught
# live 2026-07-13 when run non-interactively), it falls back to the OS locale encoding (cp1252 on
# this machine), which can't encode those characters and raises UnicodeEncodeError - uncaught,
# that kills the whole app on the very first warning it tries to print. errors="replace" means a
# still-broken encoding degrades to "?" in the log instead of crashing the screener.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

def main():
    start_api_server()
    root = Tk()
    controller = Controller()
    view = View(root, controller)
    root.mainloop()

if __name__ == "__main__":
    main()