# main.py
import tkinter as tk
from tkinter import colorchooser, filedialog,ttk
from tkinter import simpledialog

from cv2 import transform
import cv2
import numpy as np
from linear_algebra import rotation_matrix, scale_matrix, multiply_matrix_vector
from shape import Stroke
from Tooltip import Tooltip  # Import the Tooltip class
from PIL import Image, ImageGrab, ImageTk
import math
import os
import random

class SketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Sketcher with Linear Algebra")
        self.canvas_width = 800
        self.canvas_height = 600
        self.shape_history = []
        # Get the absolute path for the icons directory
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ICON_DIR = os.path.join(BASE_DIR, "icons")

        # Function to resize icons without breaking layout
        def load_resized_icon(filename, size=(24, 24)):  # Adjust size as needed
            path = os.path.join(ICON_DIR, filename)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)  # Resize while maintaining quality
                return ImageTk.PhotoImage(img)
            else:
                print(f"❌ Missing icon: {filename}")  # Debugging
                return None  # Return None if the file is missing

        # Load icons
        # Store icons as instance variables to prevent garbage collection
        self.icon_draw = load_resized_icon("draw.png")
        self.icon_eyedrop = load_resized_icon("eyedropper.png")
        self.icon_text = load_resized_icon("text.png")
        self.icon_select_text = load_resized_icon("select_text.png")
        self.icon_select = load_resized_icon("select.png")
        self.icon_eraser = load_resized_icon("eraser.png")
        self.icon_color = load_resized_icon("color.png")
        self.icon_clear = load_resized_icon("clear.png")
        self.icon_save = load_resized_icon("save.png")
        self.icon_rectangle = load_resized_icon("rectangle.png")
        self.icon_circle = load_resized_icon("circle.png")
        self.icon_line = load_resized_icon("line.png")
        self.icon_rotate = load_resized_icon("rotate.png")
        self.icon_zoom_in = load_resized_icon("zoom_in.png")
        self.icon_zoom_out = load_resized_icon("zoom_out.png")
        self.icon_import = load_resized_icon("import.png")
        self.icon_brush = load_resized_icon("brush.png")
        self.icon_ref = load_resized_icon("ref.png")
        self.icon_perspective = load_resized_icon("perspective.png")

        # Toolbar frame (full width)
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Navigation tools frame (Centered)
        self.nav_tools = tk.Frame(self.toolbar)
        self.nav_tools.pack(expand=True)  # Centers the tools

        # LEFT PANEL (For Shape Tools & Sliders)
        self.left_panel = tk.Frame(self.root, padx=70, pady=50)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
                   
        # RIGHT PANEL (For Rotate & Zoom Controls)
        self.right_panel = tk.Frame(self.root, padx=70, pady=50)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Main canvas
        self.canvas = tk.Canvas(root, bg="white", width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(pady=30)  # Adds 10 pixels of space below the canvas

        # Default drawing settings
        self.current_tool = "draw"  # Options: "draw", "eyedrop"
        self.current_color = "black"
        self.brush_thickness = 2
        self.opacity = 1.0
        self.brush_style = "round"  # Options: round, butt, projecting
        self.last_x, self.last_y = None, None
        self.current_shape = None
        # === CANVAS WILL BE PLACED IN THE CENTER ===

        # === Update Buttons to Use Icons ===
        self.btn_draw = tk.Button(self.nav_tools, image=self.icon_draw, command=lambda: self.set_tool("draw"))
        self.btn_draw.pack(side=tk.LEFT, padx=3)

        # Color chooser button
        self.btn_color = tk.Button(self.nav_tools, image=self.icon_color, command=self.choose_color)
        self.btn_color.pack(side=tk.LEFT, padx=3)
         # Color display label
        self.color_label = tk.Label(self.nav_tools, text="Color", width=10)
        self.color_label.pack(side=tk.LEFT, padx=3)

        self.btn_brush = tk.Button(self.nav_tools, image=self.icon_brush, command=self.show_brush_options)
        self.btn_brush.pack(side=tk.LEFT, padx=3)
        self.brush_selector = ttk.Combobox(self.nav_tools, values=["round", "watercolor", "charcoal", "pencil", "marker"], state="readonly")
        self.brush_selector.current(0)
        self.brush_selector.bind("<<ComboboxSelected>>", self.choose_brush)
        self.brush_selector.pack(side=tk.LEFT, padx=3)
        self.btn_eyedrop = tk.Button(self.nav_tools, image=self.icon_eyedrop, command=lambda: self.set_tool("eyedrop"))
        self.btn_eyedrop.pack(side=tk.LEFT, padx=3)
        
        # Undo and Redo stacks
        self.undo_stack = []  # Stores (item_id, coords)
        self.redo_stack = []

        # Bind keyboard shortcuts for undo/redo
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)

        self.btn_text = tk.Button(self.nav_tools, image=self.icon_text, command=lambda: self.set_tool("text"))
        self.btn_text.pack(side=tk.LEFT, padx=3)

        self.btn_select_text = tk.Button(self.nav_tools, image=self.icon_select_text, command=lambda: self.set_tool("select_text"))
        self.btn_select_text.pack(side=tk.LEFT, padx=3)

        self.btn_select = tk.Button(self.nav_tools, image=self.icon_select, command=lambda: self.set_tool("select"))
        self.btn_select.pack(side=tk.LEFT, padx=3)

        self.btn_eraser = tk.Button(self.nav_tools, image=self.icon_eraser, command=lambda: self.set_tool("eraser"))
        self.btn_eraser.pack(side=tk.LEFT, padx=3)

        self.btn_clear = tk.Button(self.nav_tools, image=self.icon_clear, command=self.clear_canvas)
        self.btn_clear.pack(side=tk.LEFT, padx=3)

        self.btn_save = tk.Button(self.nav_tools, image=self.icon_save, command=self.save_canvas)
        self.btn_save.pack(side=tk.LEFT, padx=3)

        self.btn_import = tk.Button(self.nav_tools, image=self.icon_import, command=self.import_image)
        self.btn_import.pack(side=tk.LEFT, padx=3)
        
        self.btn_reference = tk.Button(self.nav_tools, image=self.icon_ref, command=self.open_reference_window)
        self.btn_reference.pack(side=tk.LEFT, padx=3)

        self.btn_perspective = tk.Button(self.nav_tools, image=self.icon_perspective, command=lambda: self.set_tool("perspective"))
        self.btn_perspective.pack(side=tk.LEFT, padx=3)

        # === LEFT PANEL: Shape Tools ===
        self.btn_rectangle = tk.Button(self.left_panel, image=self.icon_rectangle, command=lambda: self.set_tool("rectangle"))
        self.btn_rectangle.pack(pady=10)

        self.btn_circle = tk.Button(self.left_panel, image=self.icon_circle, command=lambda: self.set_tool("circle"))
        self.btn_circle.pack(pady=10)

        self.btn_line = tk.Button(self.left_panel, image=self.icon_line, command=lambda: self.set_tool("line"))
        self.btn_line.pack(pady=10)

        # Sliders Frame (Inside Left Panel)
        self.slider_frame = tk.Frame(self.left_panel)
        self.slider_frame.pack(pady=5, fill=tk.X)

        # Brush Thickness Slider
        self.thickness_slider = tk.Scale(self.slider_frame, from_=1, to=20, orient=tk.HORIZONTAL, label="Thickness", command=self.update_thickness)
        self.thickness_slider.set(self.brush_thickness)
        self.thickness_slider.pack(pady=5, fill=tk.X)

        # === RIGHT PANEL: Transform Tools ===
        self.btn_rotate = tk.Button(self.right_panel, image=self.icon_rotate, command=self.rotate_strokes)
        self.btn_rotate.pack(pady=5, fill=tk.X)

        self.btn_zoom_in = tk.Button(self.right_panel, image=self.icon_zoom_in, command=self.scale_strokes)
        self.btn_zoom_in.pack(pady=5, fill=tk.X)

        self.btn_zoom_out = tk.Button(self.right_panel, image=self.icon_zoom_out, command=self.zoom_out_strokes)
        self.btn_zoom_out.pack(pady=5, fill=tk.X)
        # Zoom settings
        self.scale_factor = 1.0  # Initial zoom level
        
        # Add tooltips for buttons
        Tooltip(self.btn_draw, "Freehand Drawing Tool")
        Tooltip(self.btn_color, "Choose Color")
        Tooltip(self.btn_brush, "Select Brush Style")
        Tooltip(self.btn_eyedrop, "Eyedropper Tool")
        Tooltip(self.btn_text, "Insert Text")
        Tooltip(self.btn_select_text, "Select and Move Text")
        Tooltip(self.btn_select, "Select and Move Shapes")
        Tooltip(self.btn_eraser, "Eraser Tool")
        Tooltip(self.btn_clear, "Clear Canvas")
        Tooltip(self.btn_save, "Save Drawing")
        Tooltip(self.btn_import, "Import Image")
        Tooltip(self.btn_rectangle, "Draw Rectangle")
        Tooltip(self.btn_circle, "Draw Circle")
        Tooltip(self.btn_line, "Draw Line")
        Tooltip(self.btn_rotate, "Rotate Shapes")
        Tooltip(self.btn_zoom_in, "Zoom In")
        Tooltip(self.btn_zoom_out, "Zoom Out")
        Tooltip(self.btn_reference, "Open Reference Image")
        Tooltip(self.btn_perspective, "Perspective Transform")

        
        # Dictionary to track text and shape items
        self.text_items = {}
        self.shape_items = {}
        self.strokes = []  # List of stroke objects
        self.initial_coords = []  # Initialize as an empty list
        
        # Variables for dragging and resizing
        self.selected_item = None
        self.start_x = 0
        self.start_y = 0
        
        # Variables for dragging text
        self.selected_text = None
        self.start_x = 0
        self.start_y = 0

        # Variable for Perspective Transform
        self.perspective_points = []
        self.point_ids = []
        
        # Bind a **single dispatcher** for each mouse event
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def set_tool(self, tool):
        self.current_tool = tool
        print(f"Tool selected: {self.current_tool}")  # Debugging print statement

    def on_mouse_press(self, event):
        """Handles all mouse press events based on the current tool."""
        print(f"Mouse clicked at ({event.x}, {event.y}), Tool: {self.current_tool}")

        if self.current_tool == "draw":
            self.start_drawing(event)
        elif self.current_tool == "eyedrop":
            self.use_eyedropper(event)
        elif self.current_tool == "text":
            self.add_text(event)
        elif self.current_tool == "select_text":
            self.select_text_press(event)
        elif self.current_tool in ["rectangle", "circle", "line"]:
            self.start_shape(event)
        elif self.current_tool == "perspective":
            self.collect_points(event)

    def on_mouse_drag(self, event):
        """Handles all mouse drag events based on the current tool."""
        if self.current_tool == "draw":
            self.draw_motion(event) 
        elif self.current_tool == "select_text":
            self.select_text_drag(event)
        elif self.current_tool in ["rectangle", "circle", "line"]:
            self.shape_motion(event)
        elif self.current_tool == "eraser":
            self.erase_drawing(event)

    def on_mouse_release(self, event):
        """Handles all mouse release events based on the current tool."""
        if self.current_tool == "draw":
            self.draw_release(event)
        elif self.current_tool in ["rectangle", "circle", "line"]:
            self.draw_shapes(event)
        elif self.current_tool == "select_text":
            self.select_text_release(event)

    def start_drawing(self, event):
        if self.current_tool == "draw":
            self.last_x, self.last_y = event.x, event.y
            self.current_stroke = Stroke(color=self.current_color, thickness=self.brush_thickness, brush=self.brush_style)
            self.current_stroke.add_point(event.x, event.y)

    def start_shape(self, event):
        """Handles the start of a shape (rectangle, circle, line)."""
        print(f"Starting {self.current_tool} drawing at ({event.x}, {event.y})")
        self.start_x, self.start_y = event.x, event.y
        self.current_shape = None  # Reset any previous shape

    def shape_motion(self, event):
        if self.current_tool in ["rectangle", "circle", "line"]:
            if self.current_shape:
                self.canvas.delete(self.current_shape)
            if self.current_tool == "rectangle":
                self.current_shape = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline=self.current_color, width=self.brush_thickness)
            elif self.current_tool == "circle":
                self.current_shape = self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y, outline=self.current_color, width=self.brush_thickness)
            elif self.current_tool == "line":
                self.current_shape = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill=self.current_color, width=self.brush_thickness)
        
            print(f"Drawing {self.current_tool} preview...")
    
    def draw_motion(self, event):
        if self.current_tool == "draw" and self.last_x is not None and self.last_y is not None:
            brush_options = {
                "round": {"cap": tk.ROUND, "fill": self.current_color},
                "watercolor": {"cap": tk.ROUND, "fill": self._adjust_opacity(self.current_color, 0.3)},
                "charcoal": {"cap": tk.BUTT, "fill": self.current_color},
                "pencil": {"cap": tk.ROUND, "fill": self.current_color, "texture": "pencil"},
                "marker": {"cap": tk.PROJECTING, "fill": self.current_color},
            }
            
            options = brush_options.get(self.brush_style, brush_options["round"])
            
            if self.brush_style == "watercolor":
                for _ in range(4):
                    offset_x, offset_y = random.randint(-3, 3), random.randint(-3, 3)
                    thickness = self.brush_thickness * random.uniform(0.3, 1.2)
                    color = self._adjust_opacity(self.current_color, random.uniform(0.5, 0.8))
                    self.canvas.create_line(
                        self.last_x + offset_x, self.last_y + offset_y, event.x + offset_x, event.y + offset_y,
                        width=thickness,
                        capstyle=options["cap"],
                        fill=color
                    )
                    self.canvas.lower("all")
            elif self.brush_style == "pencil":
                for _ in range(2):
                    offset_x, offset_y = random.randint(-1, 1), random.randint(-1, 1)
                    self.canvas.create_line(self.last_x + offset_x, self.last_y + offset_y, event.x + offset_x, event.y + offset_y, width=self.brush_thickness * 0.7, capstyle=options["cap"], fill=options["fill"])
            elif self.brush_style == "charcoal":
                for _ in range(3):
                    offset_x, offset_y = random.randint(-2, 2), random.randint(-2, 2)
                    self.canvas.create_line(self.last_x + offset_x, self.last_y + offset_y, event.x + offset_x, event.y + offset_y, width=self.brush_thickness, capstyle=options["cap"], fill=options["fill"])
            else:
                self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, width=self.brush_thickness, capstyle=options["cap"], fill=options["fill"])
            
            self.current_stroke.add_point(event.x, event.y)
            self.last_x, self.last_y = event.x, event.y

    def erase_drawing(self, event):
        if self.current_tool == "eraser":
            # Find overlapping items and erase them
            overlapping_items = self.canvas.find_overlapping(
                event.x - 10, event.y - 10, event.x + 10, event.y + 10
            )
            for item in overlapping_items:
                self.canvas.delete(item)
                # Remove the item from stored strokes
                for stroke in self.strokes:
                    if item in stroke.canvas_ids:
                        stroke.canvas_ids.remove(item)

    def zoom_shape(self, event):
        thickness = self.brush_thickness.get()

        # Adjust coordinates based on zoom level
        zoomed_size = 50 * self.scale_factor
        zoomed_thickness = max(1, int(thickness * self.scale_factor))

        if self.current_tool == "rectangle":
            self.canvas.create_rectangle(event.x, event.y, event.x + zoomed_size, event.y + zoomed_size, outline=self.current_color, width=zoomed_thickness)

        elif self.current_tool == "circle":
            self.canvas.create_oval(event.x, event.y, event.x + zoomed_size, event.y + zoomed_size, outline=self.current_color, width=zoomed_thickness)

        elif self.current_tool == "line":
            self.canvas.create_line(event.x, event.y, event.x + zoomed_size, event.y, fill=self.current_color, width=zoomed_thickness)
    
    def use_eyedropper(self, event):
        if self.current_tool == "eyedrop":
            print("Using eyedropper tool...")
            x = self.canvas.winfo_rootx() + event.x
            y = self.canvas.winfo_rooty() + event.y
            try:
                img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
                pixel = img.getpixel((0, 0))
                self.current_color = '#%02x%02x%02x' % pixel[:3]
                print(f"Picked color: {self.current_color}")
            except Exception as e:
                print("Eyedrop error:", e)
            self.current_tool = "draw"

    def add_text(self, event):
        if self.current_tool == "text":
            print(f"Text created at ({event.x}, {event.y}) with tag 'draggable_text'")
            text = self.ask_for_text()
            if text:
                self.canvas.create_text(event.x, event.y, text=text, fill=self.current_color, font=("Arial", 12), tags=("draggable_text",))

    def show_brush_options(self):
        self.brush_selector.pack(side=tk.LEFT, padx=3)

    def choose_brush(self, event=None):
        self.brush_style = self.brush_selector.get()
        print(f"Brush style changed to: {self.brush_style}")

    def zoom_in_strokes(self):
        """Scale all strokes and shapes up by a factor of 1.5."""
        self.scale_factor *= 1.5
        self.apply_zoom()

    def zoom_out_strokes(self):
        """Scale all strokes and shapes down by a factor of 0.67."""
        self.scale_factor *= 0.67
        self.apply_zoom()
    
    def apply_zoom(self):
        """Redraw all strokes and shapes based on the current zoom level."""
        self.canvas.delete("all")  # Clear canvas before redrawing
        bg = self.canvas.cget("bg")
        self.canvas.config(bg=bg)

        # Redraw strokes
        new_strokes = []
        for stroke in self.strokes:
            new_points = [(x * self.scale_factor, y * self.scale_factor) for x, y in stroke.points]
            new_stroke = Stroke(new_points, color=stroke.color, thickness=int(stroke.thickness * self.scale_factor), opacity=stroke.opacity, brush=stroke.brush)
            new_strokes.append(new_stroke)
            pts = new_stroke.points
            if len(pts) > 1:
                for i in range(1, len(pts)):
                    self.canvas.create_line(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1], 
                                            fill=new_stroke.color, width=new_stroke.thickness, capstyle=new_stroke.brush)
        self.strokes = new_strokes  # Update stored strokes

        # Redraw shapes
        new_shape_items = {}
        for item, original_coords in self.shape_items.items():
            new_coords = [c * self.scale_factor for c in original_coords]
            new_item = self.canvas.create_rectangle(*new_coords, outline=self.current_color, width=self.brush_thickness) if "rectangle" in self.canvas.gettags(item) else \
                    self.canvas.create_oval(*new_coords, outline=self.current_color, width=self.brush_thickness) if "circle" in self.canvas.gettags(item) else \
                    self.canvas.create_line(*new_coords, fill=self.current_color, width=self.brush_thickness)
            new_shape_items[new_item] = new_coords
        self.shape_items = new_shape_items  # Update stored shapes

    def ask_for_text(self):
        """Ensure the text input dialog appears correctly."""
        self.root.after(100, lambda: self.root.focus_force())  # Force focus after a delay
        self.root.update_idletasks()  # Process pending tasks

        text = simpledialog.askstring("Input", "Enter your text:", parent=self.root)

        if text is None or text.strip() == "":
            return None  # Prevent inserting empty text

        return text

    def select_text_press(self, event):
        """Detect if a text item is clicked for dragging."""
        print("It's selecting text.")
        if self.current_tool == "select_text":
            item = self.canvas.find_closest(event.x, event.y)
            print(f"Item found: {item}, Tags: {self.canvas.gettags(item)}")  # Debug print
            if item and "draggable_text" in self.canvas.gettags(item):
                self.selected_text = item[0]
                self.start_x = event.x
                self.start_y = event.y
                print(f"Text selected: {self.selected_text}")

    def select_text_drag(self, event):
        """Move the selected text when dragged."""
        print("It's moving text.")
        if self.current_tool == "select_text" and self.selected_text:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.canvas.move(self.selected_text, dx, dy)
            print(f"Text moved by ({dx}, {dy})")
            self.start_x = event.x
            self.start_y = event.y

    def select_text_release(self, event):
        """Release the selected text after dragging."""
        print("It's releasing text.")
        if self.current_tool == "select_text":
            self.selected_text = None

    # Choose color method
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose color", initialcolor=self.current_color)
        if color[1]:
            self.current_color = color[1]
            self.color_label.config(bg=self.current_color)  # Update color label

    def update_thickness(self, value):
        self.brush_thickness = int(value)

    def update_opacity(self, value):
        self.opacity = int(value) / 100.0

    def update_brush(self, value):
        self.brush_style = value

    def draw(self, event):
        """Draws on the canvas."""
        self.save_canvas_state()  # Save before drawing
        x, y = event.x, event.y
        self.canvas.create_line(x, y, x+1, y+1, fill=self.current_color, width=self.brush_thickness)

    def _adjust_opacity(self, hex_color, alpha):
        """Adjusts the opacity of a hex color by blending it with white."""
        # Ensure the color is valid and has 7 characters (e.g., #RRGGBB)
        if not isinstance(hex_color, str) or not hex_color.startswith("#") or len(hex_color) != 7:
            print(f"Invalid color format: {hex_color}")  # Debugging output
            return "#d3d3d3"  # Default to light gray if invalid
        
        try:
            # Convert HEX to RGB
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)

            # Blend color with white based on alpha
            r = int(r + (255 - r) * alpha)
            g = int(g + (255 - g) * alpha)
            b = int(b + (255 - b) * alpha)

            # Convert back to HEX
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError:
            print(f"Error processing color: {hex_color}")  # Debugging output
            return "#d3d3d3"  # Return a default color on error

    def save_canvas_state(self):
        """Saves the current canvas as an image for undo/redo."""
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        
        # Capture the canvas state
        image = ImageGrab.grab(bbox=(x, y, x1, y1))
        self.undo_stack.append(image)  # Save to undo stack
        self.redo_stack.clear()  # Clear redo stack after new action

    def undo(self, event=None):
        """Undo the last drawn stroke or shape"""
        if self.undo_stack:
            last_action = self.undo_stack.pop()  # Remove last action
            self.redo_stack.append(last_action)  # Save for redo

            # If it's a stroke, remove it
            if isinstance(last_action, Stroke):
                self.strokes.remove(last_action)
            else:  # If it's a shape, delete from canvas
                self.canvas.delete(last_action["id"])

            self.redraw_canvas()  # Redraw everything
        else:
            print("Nothing to undo")

    def redo(self, event=None):
        """Redo the last undone action"""
        if self.redo_stack:
            last_action = self.redo_stack.pop()  # Get last undone action
            self.undo_stack.append(last_action)  # Store it back in undo stack

            # If it's a stroke, restore it
            if isinstance(last_action, Stroke):
                self.strokes.append(last_action)
            else:  # If it's a shape, redraw it
                shape = last_action
                new_id = None
                if shape["type"] == "rectangle":
                    # Get the center of the canvas
                    cx, cy = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2

                    # Convert rectangle into four corners before transformation
                    x1, y1, x2, y2 = shape["coords"]
                    
                    # Define the four corners of the rectangle
                    corners = [
                        (x1, y1),  # Top-left
                        (x2, y1),  # Top-right
                        (x2, y2),  # Bottom-right
                        (x1, y2)   # Bottom-left
                    ]
                    
                    # Rotate each corner
                    new_corners = []
                    for x, y in corners:
                        x_shifted, y_shifted = x - cx, y - cy
                        if transform:
                            new_x, new_y = multiply_matrix_vector(transform, [x_shifted, y_shifted])
                            new_x += cx
                            new_y += cy
                        else:
                            new_x, new_y = x, y
                        new_corners.append((new_x, new_y))
                    
                    # Use create_polygon instead of create_rectangle to maintain rotation
                    new_id = self.canvas.create_polygon(new_corners, outline=shape["color"], fill="", width=shape["thickness"])

                elif shape["type"] == "circle":
                    new_id = self.canvas.create_oval(*shape["coords"], outline=shape["color"], width=shape["thickness"])
                elif shape["type"] == "line":
                    new_id = self.canvas.create_line(*shape["coords"], fill=shape["color"], width=shape["thickness"])
                shape["id"] = new_id  # Update ID with new shape
                self.undo_stack.append(shape)  # Store back in undo

            self.redraw_canvas()
        else:
            print("Nothing to redo")

    def display_canvas_image(self, image):
        """Displays an image on the canvas."""
        self.canvas.delete("all")  # Clear current canvas
        self.imported_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imported_image)

    def zoom_out_strokes(self):
        """Scale all strokes down by a factor of 0.67 around the canvas center."""
        factor = 0.67  # Inverse of 1.5x
        sc_mat = scale_matrix(factor, factor)
        self.redraw_strokes(transform=sc_mat)

    def redraw_canvas(self):
        """Redraw the entire canvas with current strokes and shapes"""
        self.canvas.delete("all")  # Clear everything

        # Preserve background color
        bg = self.canvas.cget("bg")
        self.canvas.config(bg=bg)

        # Redraw strokes
        for stroke in self.strokes:
            points = stroke.points
            if len(points) > 1:
                for i in range(1, len(points)):
                    self.canvas.create_line(
                        points[i-1][0], points[i-1][1], points[i][0], points[i][1],
                        fill=stroke.color, width=stroke.thickness, capstyle=stroke.brush
                    )

        # Redraw shapes from `undo_stack`
        for action in self.undo_stack:
            if isinstance(action, dict):  # Only process shapes, not strokes
                shape = action
                new_id = None
                if shape["type"] == "rectangle":
                    new_id = self.canvas.create_rectangle(*shape["coords"], outline=shape["color"], width=shape["thickness"])
                elif shape["type"] == "circle":
                    new_id = self.canvas.create_oval(*shape["coords"], outline=shape["color"], width=shape["thickness"])
                elif shape["type"] == "line":
                    new_id = self.canvas.create_line(*shape["coords"], fill=shape["color"], width=shape["thickness"])
                shape["id"] = new_id  # Store new shape ID

    def open_reference_window(self):
        """Opens a separate window to display a reference image."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not file_path:
            return

        ref_window = tk.Toplevel(self.root)
        ref_window.title("Reference Window")
        ref_window.geometry("400x400")

        img = Image.open(file_path)
        img = ImageTk.PhotoImage(img)

        label = tk.Label(ref_window, image=img)
        label.image = img  # Keep reference
        label.pack(expand=True, fill=tk.BOTH)

        ref_window.resizable(True, True)

    def draw_shapes(self, event):
        print(f"Mouse released at ({event.x}, {event.y}), Finalizing {self.current_tool}")

        if self.current_tool in ["rectangle", "circle", "line"]:
            shape = None
            if self.current_tool == "rectangle":
                shape = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                    outline=self.current_color, width=self.brush_thickness)
            elif self.current_tool == "circle":
                shape = self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y,
                                                outline=self.current_color, width=self.brush_thickness)
            elif self.current_tool == "line":
                shape = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                                fill=self.current_color, width=self.brush_thickness)

            if shape:
                shape_info = {
                    "id": shape,
                    "coords": self.canvas.coords(shape),
                    "type": self.current_tool,
                    "color": self.current_color,
                    "thickness": self.brush_thickness
                }
                self.undo_stack.append(shape_info)
                self.redo_stack.clear()  # Clear redo stack on new action
                print("Shape saved to undo stack:", shape_info)

    def draw_release(self, event):
        print(f"Mouse released at ({event.x}, {event.y}), Finalizing {self.current_tool}")
        if self.current_tool == "draw" and self.current_stroke:
            self.strokes.append(self.current_stroke)
            self.undo_stack.append(self.current_stroke)  # Store stroke for undo
            self.redo_stack.clear()  # Clear redo history after new action
            self.current_stroke = None

    def rotate_strokes(self):
        """Rotate all strokes 90° around the canvas center."""
        angle = 90  # degrees
        rot_mat = rotation_matrix(angle)
        self.redraw_strokes(transform=rot_mat)

    def scale_strokes(self):
        """Scale all strokes by a factor of 1.5 around the canvas center."""
        factor = 1.5
        sc_mat = scale_matrix(factor, factor)
        self.redraw_strokes(transform=sc_mat)

    def redraw_strokes(self, transform=None):
        """Redraw strokes and shapes, applying optional transformation."""
        self.canvas.delete("all")  # Clear everything before redrawing

        # Preserve the current background colors
        bg = self.canvas.cget("bg")
        self.canvas.config(bg=bg)

        # Transform and redraw strokes
        new_strokes = []
        for stroke in self.strokes:
            new_points = []
            for point in stroke.points:
                cx, cy = self.canvas_width / 2, self.canvas_height / 2
                x_shifted = point[0] - cx
                y_shifted = point[1] - cy

                if transform:
                    new_point = multiply_matrix_vector(transform, [x_shifted, y_shifted])
                    new_x = new_point[0] + cx
                    new_y = new_point[1] + cy
                else:
                    new_x, new_y = point[0], point[1]

                new_points.append((new_x, new_y))

            new_stroke = Stroke(new_points, color=stroke.color, thickness=stroke.thickness,
                                opacity=stroke.opacity, brush=stroke.brush)
            new_strokes.append(new_stroke)

            pts = new_stroke.points
            if len(pts) > 1:
                for i in range(1, len(pts)):
                    self.canvas.create_line(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1],
                                            fill=new_stroke.color, width=new_stroke.thickness, capstyle=new_stroke.brush)
        self.strokes = new_strokes  # Update stored strokes

        # Transform and redraw shapes
        new_shape_items = {}
        for action in self.undo_stack:
            if isinstance(action, dict):  # Process only shapes
                shape = action
                new_coords = []
                cx, cy = self.canvas_width / 2, self.canvas_height / 2

                for i in range(0, len(shape["coords"]), 2):
                    x_shifted = shape["coords"][i] - cx
                    y_shifted = shape["coords"][i+1] - cy

                    if transform:
                        new_point = multiply_matrix_vector(transform, [x_shifted, y_shifted])
                        new_x = new_point[0] + cx
                        new_y = new_point[1] + cy
                    else:
                        new_x, new_y = shape["coords"][i], shape["coords"][i+1]

                    new_coords.append(new_x)
                    new_coords.append(new_y)

                new_id = None
                if shape["type"] == "rectangle":
                    new_id = self.canvas.create_rectangle(*new_coords, outline=shape["color"], width=shape["thickness"])
                elif shape["type"] == "circle":
                    new_id = self.canvas.create_oval(*new_coords, outline=shape["color"], width=shape["thickness"])
                elif shape["type"] == "line":
                    new_id = self.canvas.create_line(*new_coords, fill=shape["color"], width=shape["thickness"])

                shape["id"] = new_id  # Update shape ID
                shape["coords"] = new_coords  # Store new coordinates
                new_shape_items[new_id] = new_coords

        self.shape_items = new_shape_items  # Update stored shapes

    def clear_canvas(self):
        self.canvas.delete("all")
        self.strokes = []

    def save_canvas(self):
        # Open a file dialog for saving the image
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Dynamically calculate the canvas coordinates
                x = self.canvas.winfo_rootx()
                y = self.canvas.winfo_rooty()

                # Define the bounding box based on the canvas size (800x600)
                x1 = x + 800  # width of canvas
                y1 = y + 600  # height of canvas

                # Print the coordinates for debugging
                print(f"Canvas coordinates: ({x}, {y}, {x1}, {y1})")

                # Capture the canvas area using ImageGrab
                img = ImageGrab.grab(bbox=(x, y, x1, y1))

                # Convert to RGB if saving as JPEG
                if file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg"):
                    img = img.convert("RGB")

                # Save the image
                img.save(file_path)
                print(f"Canvas saved successfully to {file_path}")

            except Exception as e:
                print(f"Error saving canvas: {e}")

    def import_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not file_path:
            return 

        # Open and resize image (optional)
        img = Image.open(file_path)
        img = img.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)

        # Convert image to Tkinter format
        self.imported_image = ImageTk.PhotoImage(img)

        # Display image on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imported_image)

            
    def collect_points(self, event):
        """Collects four points from user clicks."""
        if len(self.perspective_points) < 4:
            self.perspective_points.append((event.x, event.y))
            print(f"Point {len(self.perspective_points)}: {event.x}, {event.y}")

            # Draw a red circle at the clicked location (radius 5 for visibility)
            point_id = self.canvas.create_oval(event.x - 4, event.y - 4, event.x + 4, event.y + 4, outline="red", fill="red", width=1)
            self.point_ids.append(point_id)
            print(f"Deleting point: {point_id}") 


        if len(self.perspective_points) == 4:
            print("Four points selected:", self.perspective_points)
            self.apply_perspective_transform()

    def apply_perspective_transform(self):
        """Applies a perspective transformation to the canvas as an image."""

        for point_id in self.point_ids:
            print(f"Deleting point: {point_id}") 
            self.canvas.delete(point_id)

        self.canvas.update()
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        # Grab the canvas content as an image
        img = ImageGrab.grab((x, y, x1, y1))
        img_np = np.array(img)  # Convert to NumPy array for OpenCV

        # Define source and destination points
        pts1 = np.float32(self.perspective_points)
        pts2 = np.float32([[0, 0], [self.canvas_width, 0], [0, self.canvas_height], [self.canvas_width, self.canvas_height]])

        # Compute the transformation matrix
        M = cv2.getPerspectiveTransform(pts1, pts2)
        
        # Apply the transformation
        transformed = cv2.warpPerspective(img_np, M, (self.canvas_width, self.canvas_height))

        # Convert the transformed NumPy array back to an image
        transformed_img = Image.fromarray(transformed)

        # Convert the transformed image to a Tkinter-compatible image
        transformed_tk = ImageTk.PhotoImage(transformed_img)

        # Update the canvas with the transformed image
        self.canvas.create_image(0, 0, anchor="nw", image=transformed_tk)

        # Keep a reference to the image to prevent it from being garbage collected
        self.canvas.image = transformed_tk

        print("Applying perspective transform...")

        # Reset for next selection
        self.perspective_points = []

if __name__ == "__main__":
    root = tk.Tk()
    app = SketchApp(root)
    root.mainloop()
