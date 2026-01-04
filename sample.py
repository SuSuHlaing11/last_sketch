import tkinter as tk
from tkinter import simpledialog

root = tk.Tk()
root.withdraw()  # Hide main window

text = simpledialog.askstring("Test Input", "Enter something:")
print(f"User entered: {text}")

root.mainloop()
