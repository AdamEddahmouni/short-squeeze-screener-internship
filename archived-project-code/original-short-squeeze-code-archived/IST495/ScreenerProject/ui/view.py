import yfinance as yf
import matplotlib.pyplot as plt
from tkinter import Frame, Label, Button, Canvas, Scrollbar, StringVar, Entry, VERTICAL, RIGHT, LEFT, Y, BOTH, ttk
from tkinter.font import Font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.root.after(10000, self.refresh_screener_panel)

    # Refreshes the screener tab with new filtered stock data
    def refresh_screener_panel(self):
        for widget in self.screener_container.winfo_children():
            widget.destroy()

        prime, subprime = self.controller.get_screener_results()

        def add_section(title, data, tag):
            Label(self.screener_container, text=title, font=("Arial", 14, "bold")).pack(pady=(10, 0))
            tree = ttk.Treeview(self.screener_container, columns=["Ticker", "Price", "Float (M)", "Rel Volume", "Change From Prev Close", "Target (%)", "Stop Loss (%)"], show="headings")
            for col in ["Ticker", "Price", "Float (M)", "Rel Volume", "Change From Prev Close", "Target (%)", "Stop Loss (%)"]:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=100)

            tree.tag_configure("prime", background="#d4edda") #Light Green
            tree.tag_configure("subprime", background="#fff3cd") #Light Yellow

            for row in data:
                tree.insert("", "end", values=row, tags=(tag,))

            tree.pack(expand=True, fill="both", padx=10, pady=5)

        add_section("⭐ Prime Setup", prime, tag="prime")
        add_section("⚠️ Subprime Setup", subprime, tag="subprime")

        self.root.after(15000, self.refresh_screener_panel)

    # Builds the breaking news tab
    def build_breaking_news_tab(self, parent):
        self.breaking_news_container = parent
        self.refresh_breaking_news_tab()
        self.root.after(15000, self.refresh_breaking_news_tab)

    # Refreshes the breaking news tab with new headlines
    def refresh_breaking_news_tab(self):
        for widget in self.breaking_news_container.winfo_children():
            widget.destroy()

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

        headlines = self.controller.get_positive_news()

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
        
        plt.close('all')  # Close any open matplotlib figures
        self.root.destroy()  # Cleanly close the Tkinter window
