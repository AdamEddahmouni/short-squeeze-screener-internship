from tkinter import Tk
from controller.controller import Controller
from ui.view import View

def main():
    root = Tk()
    controller = Controller()
    view = View(root, controller)
    root.mainloop()

if __name__ == "__main__":
    main()