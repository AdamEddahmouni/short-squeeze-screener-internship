import tkinter as tk
from tkinter import ttk
from tkinter import StringVar

class ScreenerView:
    def __init__(self, root):
        self.root = root
        self.root.title("Screener")
        self.root.geometry("500x250")

        self.search = tk.Entry(root, width=30)
        self.news_result_var = StringVar()
        self.news_dropdown_var = StringVar()

        self.news_result = tk.Entry(root, textvariable=self.news_result_var, state="readonly", width=25)
        self.news_dropdown = ttk.Combobox(root, textvariable=self.news_dropdown_var, state="readonly", width=35)
        self.price = tk.Label(root, text="Price:")
        self.change = tk.Label(root, text="Percent Change:")
        self.rel_vol = tk.Label(root, text="Relative Volume:")
        self.float_amount = tk.Label(root, text="Float:")

        self.layout_widgets()

    def layout_widgets(self):
        tk.Label(self.root, text="Ticker Symbol ID").grid(row=0, column=2)
        self.search.grid(row=1, column=2, columnspan=2, sticky="we")

        self.price.grid(row=2, column=0, sticky="w")
        self.change.grid(row=3, column=0, sticky="w")
        self.rel_vol.grid(row=4, column=0, sticky="w")

        self.float_amount.grid(row=2, column=3, sticky="w")
        self.news_result.grid(row=3, column=3, sticky="w")
        self.news_dropdown.grid(row=4, column=3, sticky="w")