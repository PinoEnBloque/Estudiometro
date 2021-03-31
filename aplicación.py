import tkinter as tk
from clase_Estudiometro import *
from clase_Editor import *


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title("Estudiómetro")
    root.iconbitmap("Estudiometro.ico")
    root.lift()
    app = Estudiometro(master=root)
    app.mainloop()