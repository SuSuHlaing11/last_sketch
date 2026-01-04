import tkinter as tk
import math

class ShapeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Shape Selector & Transformer")

        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()

        self.shapes = {}  # Store shape ID and properties
        self.selected_shape = None
        self.start_x = 0
        self.start_y = 0

        # Add Shapes
        self.add_rectangle(100, 100, 200, 200)
        self.add_circle(300, 100, 50)

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.select_shape)
        self.canvas.bind("<B1-Motion>", self.move_shape)
        self.canvas.bind("<ButtonRelease-1>", self.deselect_shape)

    def add_rectangle(self, x1, y1, x2, y2):
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=2, tags="shape")
        self.shapes[rect] = {"type": "rectangle", "coords": (x1, y1, x2, y2)}

    def add_circle(self, x, y, radius):
        oval = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="black", width=2, tags="shape")
        self.shapes[oval] = {"type": "circle", "coords": (x, y, radius)}

    def select_shape(self, event):
        shape_id = self.canvas.find_closest(event.x, event.y)[0]
        if shape_id in self.shapes:
            self.selected_shape = shape_id
            self.start_x = event.x
            self.start_y = event.y
            self.canvas.itemconfig(shape_id, outline="red")  # Highlight selection

    def move_shape(self, event):
        if self.selected_shape:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.canvas.move(self.selected_shape, dx, dy)

            # Update stored coordinates
            shape_data = self.shapes[self.selected_shape]
            if shape_data["type"] == "rectangle":
                x1, y1, x2, y2 = shape_data["coords"]
                self.shapes[self.selected_shape]["coords"] = (x1 + dx, y1 + dy, x2 + dx, y2 + dy)
            elif shape_data["type"] == "circle":
                x, y, r = shape_data["coords"]
                self.shapes[self.selected_shape]["coords"] = (x + dx, y + dy, r)

            self.start_x = event.x
            self.start_y = event.y

    def deselect_shape(self, event):
        if self.selected_shape:
            self.canvas.itemconfig(self.selected_shape, outline="black")  # Remove highlight
            self.selected_shape = None

root = tk.Tk()
app = ShapeEditor(root)
root.mainloop()