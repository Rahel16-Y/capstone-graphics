"""
Matrix stack for hierarchical 3D transformations.

Uses NumPy 4x4 homogeneous matrices (column vectors) and syncs with OpenGL.
Equivalent to glPushMatrix / glPopMatrix with explicit matrix math.
"""

from __future__ import annotations

import numpy as np
from OpenGL.GL import glLoadMatrixf, glMultMatrixf


def identity() -> np.ndarray:
    """Return a 4x4 identity matrix."""
    return np.identity(4, dtype=np.float32)


def rotation_y(angle_degrees: float) -> np.ndarray:
    """
    Build a rotation matrix around the Y axis.

    For angle θ (radians):
        x' = x·cos(θ) + z·sin(θ)
        z' = -x·sin(θ) + z·cos(θ)

    Used for orbital motion and planet self-rotation.
    """
    theta = np.radians(angle_degrees)
    c, s = np.cos(theta), np.sin(theta)
    m = identity()
    m[0, 0] = c
    m[0, 2] = s
    m[2, 0] = -s
    m[2, 2] = c
    return m


def translation(x: float, y: float, z: float) -> np.ndarray:
    """
    Build a translation matrix.

    Moves a point by (x, y, z):
        p' = p + (x, y, z)
    """
    m = identity()
    m[0, 3] = x
    m[1, 3] = y
    m[2, 3] = z
    return m


def scale_uniform(s: float) -> np.ndarray:
    """Build a uniform scale matrix."""
    m = identity()
    m[0, 0] = s
    m[1, 1] = s
    m[2, 2] = s
    return m


class MatrixStack:
    """
    Stack of 4x4 model matrices for hierarchical modeling.

    Each push/pop pair saves and restores a parent transform so child
    objects inherit the parent's position and orientation.
    """

    def __init__(self) -> None:
        self._stack: list[np.ndarray] = [identity()]

    @property
    def current(self) -> np.ndarray:
        return self._stack[-1]

    def push(self) -> None:
        """Save current matrix (glPushMatrix equivalent)."""
        self._stack.append(self.current.copy())

    def pop(self) -> None:
        """Restore previous matrix (glPopMatrix equivalent)."""
        if len(self._stack) > 1:
            self._stack.pop()

    def load_identity(self) -> None:
        """Reset current matrix to identity."""
        self._stack[-1] = identity()

    def multiply(self, matrix: np.ndarray) -> None:
        """Post-multiply: M ← M · T (column-vector convention)."""
        self._stack[-1] = self.current @ matrix

    def rotate_y(self, angle_degrees: float) -> None:
        self.multiply(rotation_y(angle_degrees))

    def translate(self, x: float, y: float, z: float) -> None:
        self.multiply(translation(x, y, z))

    def scale(self, s: float) -> None:
        self.multiply(scale_uniform(s))

    def apply_to_gl(self) -> None:
        """Upload current matrix to OpenGL modelview stack."""
        glLoadMatrixf(self.current.T)

    def apply_and_multiply_gl(self, matrix: np.ndarray) -> None:
        """Multiply OpenGL matrix by the given transform."""
        glMultMatrixf(matrix.T)
