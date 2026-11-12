"""
Programmatic sphere mesh generation and drawing.

Vertices are generated using parametric spherical coordinates:
    x = r · sin(φ) · cos(θ)
    y = r · cos(φ)
    z = r · sin(φ) · sin(θ)

where φ ∈ [0, π] (latitude) and θ ∈ [0, 2π] (longitude).
"""

from __future__ import annotations

import math

import numpy as np
from OpenGL.GL import GL_LINE_LOOP, GL_TRIANGLES, glBegin, glColor3f, glEnd, glVertex3f


class SphereMesh:
    """Precomputed sphere vertices for flat-shaded rendering."""

    def __init__(self, radius: float = 1.0, slices: int = 24, stacks: int = 16) -> None:
        self.radius = radius
        self.slices = slices
        self.stacks = stacks
        self._vertices = self._generate_vertices()

    def _generate_vertices(self) -> np.ndarray:
        """Generate unit-sphere vertices scaled by radius."""
        vertices: list[tuple[float, float, float]] = []
        for i in range(self.stacks + 1):
            phi = math.pi * i / self.stacks
            sin_phi = math.sin(phi)
            cos_phi = math.cos(phi)
            for j in range(self.slices + 1):
                theta = 2.0 * math.pi * j / self.slices
                x = self.radius * sin_phi * math.cos(theta)
                y = self.radius * cos_phi
                z = self.radius * sin_phi * math.sin(theta)
                vertices.append((x, y, z))
        return np.array(vertices, dtype=np.float32)

    def draw_solid(self, color: tuple[float, float, float]) -> None:
        """Draw filled sphere using GL_TRIANGLES between latitude bands."""
        glColor3f(*color)
        stride = self.slices + 1
        for i in range(self.stacks):
            for j in range(self.slices):
                v00 = self._vertices[i * stride + j]
                v01 = self._vertices[i * stride + j + 1]
                v10 = self._vertices[(i + 1) * stride + j]
                v11 = self._vertices[(i + 1) * stride + j + 1]
                glBegin(GL_TRIANGLES)
                glVertex3f(v00[0], v00[1], v00[2])
                glVertex3f(v10[0], v10[1], v10[2])
                glVertex3f(v11[0], v11[1], v11[2])
                glVertex3f(v00[0], v00[1], v00[2])
                glVertex3f(v11[0], v11[1], v11[2])
                glVertex3f(v01[0], v01[1], v01[2])
                glEnd()

    def draw_wireframe(self, color: tuple[float, float, float]) -> None:
        """Draw wireframe sphere using latitude/longitude loops."""
        glColor3f(*color)
        for i in range(self.stacks + 1):
            glBegin(GL_LINE_LOOP)
            for j in range(self.slices):
                idx = i * (self.slices + 1) + j
                v = self._vertices[idx]
                glVertex3f(v[0], v[1], v[2])
            glEnd()

        for j in range(self.slices):
            glBegin(GL_LINE_LOOP)
            for i in range(self.stacks + 1):
                idx = i * (self.slices + 1) + j
                v = self._vertices[idx]
                glVertex3f(v[0], v[1], v[2])
            glEnd()


def draw_orbit_path(radius: float, segments: int = 128, color: tuple[float, float, float] = (0.4, 0.4, 0.4)) -> None:
    """
    Draw a circular orbital path in the XZ plane using GL_LINE_LOOP.

    Parametric circle:
        x = r · cos(θ)
        z = r · sin(θ)
    """
    glColor3f(*color)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        glVertex3f(x, 0.0, z)
    glEnd()
