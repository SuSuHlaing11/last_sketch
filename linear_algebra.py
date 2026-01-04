# linear_algebra.py
import math
import random

def multiply_matrix_vector(matrix, vector):
    """
    Multiply a 2x2 matrix by a 2-element vector.
    """
    result = [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1]
    ]
    return result

def rotation_matrix(angle_degrees):
    """
    Return a 2x2 rotation matrix for the given angle in degrees.
    """
    angle_rad = math.radians(angle_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return [
        [cos_a, -sin_a],
        [sin_a, cos_a]
    ]

def scale_matrix(sx, sy):
    """
    Return a 2x2 scaling matrix with factors sx and sy.
    """
    return [
        [sx, 0],
        [0, sy]
    ]

def shear_matrix(shx, shy):
    """
    Return a 2x2 shearing matrix.
    """
    return [
        [1, shx],
        [shy, 1]
    ]

def apply_transformation(matrix, points):
    """
    Apply a transformation matrix to a list of points.
    """
    return [multiply_matrix_vector(matrix, point) for point in points]

def generate_pencil_texture():
    """
    Generates a random grainy effect for pencil strokes.
    """
    return [(random.randint(-1, 1), random.randint(-1, 1)) for _ in range(5)]