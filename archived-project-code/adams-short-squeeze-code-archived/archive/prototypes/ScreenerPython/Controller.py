class ScreenerController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.bind_events()

    def bind_events(self):
        self.view.search.bind("<Return>", self.on_search)

    def on_search(self, event):
        symbol = self.view.search.get().strip().upper()
        self.model.set_ticker_symbol(symbol)

        self.model.fetch_finviz_data()
        data = self.model.get_stock_data()

        self.view.price.config(text=f"Share Price: ${data.get('Price', 'N/A')}")
        self.view.change.config(text=f"Percent Change: {data.get('Change', 'N/A')}")
        self.view.rel_vol.config(text=f"Relative Volume: {data.get('Rel Vol', 'N/A')}")
        self.view.float_amount.config(text=f"Float Amount: {data.get('Float', 'N/A')}")

        # Run news sentiment analysis
        sentiment_summary = self.model.analyze_news()
        self.view.news_result_var.set(sentiment_summary['overall_prediction'])
        self.view.news_dropdown['values'] = [
            f"Net Score: {sentiment_summary['net_score']}",
            f"Confidence: {sentiment_summary['confidence_level']}"
        ]
        self.view.news_dropdown.current(0)

