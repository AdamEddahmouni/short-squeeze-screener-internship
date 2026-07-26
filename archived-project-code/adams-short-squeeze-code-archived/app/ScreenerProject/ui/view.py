import yfinance as yf
from core import mongo_client, snapshot_store
from tkinter import Frame, Label, Button, Canvas, Scrollbar, StringVar, Entry, VERTICAL, RIGHT, LEFT, Y, BOTH, ttk
from tkinter.font import Font
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    plt = None
    FigureCanvasTkAgg = None

REFRESH_INTERVAL_MS = 15000

_SQUEEZE_SCORE_BREAKDOWN_LABELS = {"short_float": "SF", "borrow_fee": "BF", "days_to_cover": "DTC"}


# Compact single-cell rendering of core/squeeze_score.py's compute_squeeze_score_breakdown() dict
# (e.g. {"short_float": 60.0, "borrow_fee": 80.0, "days_to_cover": 80.0}) for the flat Treeview -
# "SF 60 · BF 80 · DTC 80", "—" for any component that was missing that cycle.
def _format_squeeze_score_breakdown(breakdown):
    if not breakdown:
        return "—"
    parts = []
    for key, label in _SQUEEZE_SCORE_BREAKDOWN_LABELS.items():
        value = breakdown.get(key)
        parts.append(f"{label} {value:.0f}" if value is not None else f"{label} —")
    return " · ".join(parts)


class View:
    # Initializes the GUI layout and all tabs
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Stock Screener")
        self.root.geometry("1000x700")

        self.tab_control = ttk.Notebook(self.root)
        self.screener_tab = Frame(self.tab_control)
        self.chart_tab = Frame(self.tab_control)
        self.breaking_tab = Frame(self.tab_control)

        self.tab_control.add(self.screener_tab, text="📈 Stock Screener")
        self.tab_control.add(self.chart_tab, text="📊 Stock Chart")
        self.tab_control.add(self.breaking_tab, text="📢 Breaking News")
        self.tab_control.pack(expand=1, fill="both")

        self.build_screener_panel(self.screener_tab)
        self.build_chart_panel(self.chart_tab)
        self.build_breaking_news_tab(self.breaking_tab)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle proper shutdown

    # Builds and populates the screener tab
    def build_screener_panel(self, parent):
        self.screener_container = parent
        self.refresh_screener_panel()

    # Refreshes the screener tab with new filtered stock data
    def refresh_screener_panel(self):
        # get_screener_results() must never be allowed to raise past this point: this method is
        # the sole owner of the screener's 15s timer chain (root.after() below), and an uncaught
        # exception here means Tkinter prints it and simply never reschedules - the window keeps
        # responding to input, but the snapshot silently freezes forever with no crash to notice.
        # Caught live 2026-07-16 via a corrupted data/prime_log.csv; this is the second layer of
        # defense (log_prime_ticker() itself is now tolerant of a malformed row too) so any other
        # future failure in this path degrades to "keep last cycle's data, retry in 15s" instead
        # of a silent, permanent freeze.
        try:
            prime, subprime = self.controller.get_screener_results()
        except Exception as e:
            print(f"⚠️ Error fetching screener results: {e}")
            self.root.after(REFRESH_INTERVAL_MS, self.refresh_screener_panel)
            return

        for widget in self.screener_container.winfo_children():
            widget.destroy()

        self._write_snapshot(prime, subprime)

        def add_section(title, data, tag):
            Label(self.screener_container, text=title, font=("Arial", 14, "bold")).pack(pady=(10, 0))
            columns = ["Ticker", "Price", "Float (M)", "Rel Volume", "Change From Prev Close",
                       "Target (%)", "Stop Loss (%)", "Sentiment", "Short Interest (%)",
                       "Shares Short", "Days to Cover", "Short Int. As Of", "Short Int. Source",
                       "Float As Of", "Float Source", "IB Shortable Shares", "IB Shortable As Of",
                       "Schwab HTB Qty", "Schwab HTB Rate", "Schwab Hard-to-Borrow",
                       "Schwab HTB As Of", "TTM Squeeze", "Squeeze Momentum",
                       "IB Borrow Fee Rate", "IB Borrow Rebate Rate", "IB Borrow Rate As Of",
                       "Squeeze Score", "Squeeze Score Breakdown", "Corroboration Score",
                       "Corroborated By", "Quality Flags", "Squeeze Confirmed", "TTM Squeeze Fired"]
            tree = ttk.Treeview(self.screener_container, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=100)

            tree.tag_configure("prime", background="#d4edda") #Light Green
            tree.tag_configure("subprime", background="#fff3cd") #Light Yellow

            for row in data:
                # corroborated_by/quality_flags are lists and squeeze_score_breakdown is a dict in
                # the underlying row (also used as-is for the JSON snapshot in _write_snapshot
                # below) - format every non-scalar cell in the display copy only, so Treeview
                # doesn't just render Python's str(list)/str(dict) repr.
                display_row = [
                    "; ".join(value) if isinstance(value, list)
                    else _format_squeeze_score_breakdown(value) if isinstance(value, dict)
                    else value
                    for value in row
                ]
                tree.insert("", "end", values=display_row, tags=(tag,))

            tree.pack(expand=True, fill="both", padx=10, pady=5)

        add_section("⭐ Prime Setup", prime, tag="prime")
        add_section("⚠️ Subprime Setup", subprime, tag="subprime")

        # This method owns the sole screener timer chain. A second startup callback previously
        # created overlapping 10s/15s loops that rewrote snapshots without fresher IB data.
        self.root.after(REFRESH_INTERVAL_MS, self.refresh_screener_panel)

    # Writes the current cycle's screener results to disk in the integration data contract shape
    # (PROJECT_NOTES.md §9) - api_server.py's /screener endpoint just reads this file, so the file
    # snapshot is the actual source of truth and the REST layer is a thin read-only wrapper around
    # it. Reuses this cycle's already-fetched prime/subprime instead of triggering a second
    # IB/Finviz poll. Failure here (e.g. disk full, permissions) shouldn't take down the UI.
    def _write_snapshot(self, prime, subprime):
        try:
            snapshot = self.controller.get_snapshot(prime, subprime)
            snapshot_store.write_snapshot(snapshot)
        except Exception as e:
            print(f"⚠️ Error writing screener snapshot: {e}")
            return

        # Opportunistic second sink for a cloud-hosted integration API
        # (deploy/vercel-api/) to read from anywhere, not just localhost. No-ops
        # if MONGODB_URI isn't set; local JSON above remains primary either way.
        mongo_client.push_snapshot_async(snapshot)

    # Builds the breaking news tab. self.news_search_var is created here, once, rather than in
    # _render_breaking_news() - that method destroys/rebuilds every widget in this tab on every
    # call (15s auto-refresh, and now also on every search), so a StringVar created there would
    # get thrown away with the old Entry widget. Keeping it here means whatever the user has typed
    # survives both kinds of rebuild instead of being silently cleared out from under them.
    def build_breaking_news_tab(self, parent):
        self.breaking_news_container = parent
        self.news_search_var = StringVar()
        self._cached_headlines = []
        self.refresh_breaking_news_tab()

    # Re-fetches headlines from the controller and re-renders. Only this method calls
    # get_positive_news() - _render_breaking_news() re-filters/re-draws from the cache instead, so
    # searching doesn't trigger extra classifier/network work on every keystroke or click.
    def refresh_breaking_news_tab(self):
        self._cached_headlines = self.controller.get_positive_news()
        self._render_breaking_news()
        self._write_news_snapshot(self._cached_headlines)
        # This method owns the sole Breaking News timer chain; the builder only invokes it once.
        self.root.after(REFRESH_INTERVAL_MS, self.refresh_breaking_news_tab)

    # Persists this cycle's headlines so api_server.py's GET /news has something to serve - same
    # atomic-write primitive and same "never let a write failure take down the UI" pattern as
    # _write_snapshot() above, just a second file (core/snapshot_store.py's NEWS_SNAPSHOT_PATH).
    @staticmethod
    def _write_news_snapshot(headlines):
        try:
            snapshot_store.write_snapshot(headlines, snapshot_store.NEWS_SNAPSHOT_PATH)
        except Exception as e:
            print(f"⚠️ Error writing news snapshot: {e}")

    # Destroys and rebuilds the tab's widgets from self._cached_headlines, filtered by
    # self.news_search_var if it's non-empty. Search is button/Enter-triggered rather than
    # live-on-keystroke deliberately: since this rebuilds every widget including the search Entry
    # itself, filtering on every keypress would destroy and recreate the Entry the user is
    # actively typing into, resetting focus after a single character.
    def _render_breaking_news(self):
        for widget in self.breaking_news_container.winfo_children():
            widget.destroy()

        search_frame = Frame(self.breaking_news_container)
        search_frame.pack(fill="x", padx=10, pady=(10, 0))
        Label(search_frame, text="🔍 Filter by ticker:").pack(side=LEFT)
        search_entry = Entry(search_frame, textvariable=self.news_search_var, width=12)
        search_entry.pack(side=LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: self._render_breaking_news())
        Button(search_frame, text="Search", command=self._render_breaking_news).pack(side=LEFT)
        Button(search_frame, text="Clear", command=self._clear_news_search).pack(side=LEFT, padx=(5, 0))

        canvas = Canvas(self.breaking_news_container)
        scrollbar = Scrollbar(self.breaking_news_container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        query = self.news_search_var.get().strip().upper()
        headlines = [
            item for item in self._cached_headlines
            if not query or query in [t.upper() for t in item.get("tickers", [])]
        ]

        for item in headlines:
            frame = Frame(scrollable_frame, borderwidth=1, relief="solid", padx=5, pady=5)
            frame.pack(fill="x", pady=4, padx=5)

            headline = item['headline']
            ticker = ", ".join(item['tickers'])
            url = item['url']
            confidence = int(item['confidence_score'] * 100)

            lbl = Label(frame, text=f"📰 {headline}\n📊 {ticker} | Confidence: {confidence}%",
                        justify="left", wraplength=800, fg="blue", cursor="hand2", font=Font(weight="bold"))
            lbl.pack(anchor="w")

            lbl.bind("<Button-1>", lambda e, url=url: self.controller.open_url(url))

    def _clear_news_search(self):
        self.news_search_var.set("")
        self._render_breaking_news()

    """# Adds a box to manually enter and classify a custom headline
    def build_manual_input_box(self, parent):
        frame = Frame(parent)
        frame.pack(pady=10)

        Label(frame, text="Enter a custom headline:").pack(anchor="w")

        self.custom_headline_var = StringVar()
        entry = Entry(frame, textvariable=self.custom_headline_var, width=100)
        entry.pack(padx=5, pady=5)

        self.prediction_output = StringVar()
        Label(frame, textvariable=self.prediction_output, fg="blue").pack(anchor="w")

        Button(frame, text="🔍 Classify", command=self.classify_custom_headline).pack(pady=5)

    # Classifies the user-inputted headline and shows sentiment/confidence
    def classify_custom_headline(self):
        headline = self.custom_headline_var.get()
        if not headline:
            self.prediction_output.set("⚠️ Please enter a headline.")
            return

        result = self.controller.classify_single_headline(headline)
        if result:
            label = result['prediction']
            confidence = int(result['confidence_score'] * 100)
            self.prediction_output.set(f"Prediction: {label} ({confidence}% confidence)")
        else:
            self.prediction_output.set("⚠️ Model not ready or headline invalid.")

    # Adds a button to trigger retraining the sentiment model
    def add_retrain_button(self, parent):
        Button(
            parent,
            text="🔁 Retrain Model from Labels",
            command=self.controller.retrain_model,
            bg="#4CAF50", fg="white", padx=10, pady=5
        ).pack(pady=10)"""

    # Builds the stock chart tab UI
    def build_chart_panel(self, parent):
        frame = Frame(parent)
        frame.pack(pady=20)

        Label(frame, text="Enter a stock ticker:").pack()

        self.ticker_var = StringVar()
        Entry(frame, textvariable=self.ticker_var, width=20).pack(pady=5)

        Button(frame, text="📈 Load Chart", command=self.plot_chart).pack()

        self.chart_frame = Frame(parent)
        self.chart_frame.pack(expand=True, fill="both")

    # Uses yfinance to plot a 5-day intraday stock chart
    def plot_chart(self):
        if plt is None or FigureCanvasTkAgg is None:
            print("Chart dependencies are not installed; the live screener remains available.")
            return
        ticker = self.ticker_var.get().upper().strip()
        if not ticker:
            return

        try:
            df = yf.download(ticker, period="5d", interval="30m")
            if df.empty:
                raise ValueError("No data returned")

            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(6, 4))
            df['Close'].plot(ax=ax)
            ax.set_title(f"{ticker} - 5 Day Price Chart")
            ax.set_ylabel("Price")

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            print(f"⚠️ Failed to load chart: {e}")
    
    def on_close(self):
        """
        Gracefully handles the app window being closed.
        Closes all Matplotlib figures and destroys the Tkinter window to prevent process hang.
        """
        
        if plt is not None:
            plt.close('all')  # Close any open matplotlib figures
        self.controller.shutdown_ib()  # Cleanly disconnect the IB scanner thread
        self.root.destroy()  # Cleanly close the Tkinter window
