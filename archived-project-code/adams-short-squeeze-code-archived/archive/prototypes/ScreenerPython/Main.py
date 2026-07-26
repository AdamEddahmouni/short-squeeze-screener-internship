if __name__ == '__main__':
    import tkinter as tk
    from Model import ScreenerModel
    from View import ScreenerView
    from Controller import ScreenerController

    root = tk.Tk()
    model = ScreenerModel()
    view = ScreenerView(root)
    controller = ScreenerController(view, model)

    root.mainloop()
