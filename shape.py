# shape.py

class Stroke:
    """
    Represents a freehand stroke with additional attributes.
    """
    def __init__(self, points=None, color="black", thickness=2, opacity=1.0, brush="round"):
        self.points = points if points is not None else []
        self.color = color
        self.thickness = thickness
        self.opacity = opacity
        self.brush = brush
        self.canvas_ids = []  # Track drawn elements for erasing

    def add_point(self, x, y):
        self.points.append((x, y))
