"""
Interactive camera for orbiting and zooming around the solar system.

Mouse drag rotates the view; scroll wheel zooms; C resets to default.
"""

from __future__ import annotations

import math

import numpy as np
from OpenGL.GL import glLoadIdentity
from OpenGL.GLU import gluLookAt


class Camera:
    """Spherical orbit camera centered on the solar system origin."""

    def __init__(self) -> None:
        self.yaw: float = 35.0
        self.pitch: float = 25.0
        self.distance: float = 70.0
        self.min_distance: float = 15.0
        self.max_distance: float = 150.0
        self._dragging: bool = False
        self._last_mouse: tuple[int, int] = (0, 0)
        self._default_yaw = self.yaw
        self._default_pitch = self.pitch
        self._default_distance = self.distance

    def reset(self) -> None:
        """Restore default camera orientation and zoom."""
        self.yaw = self._default_yaw
        self.pitch = self._default_pitch
        self.distance = self._default_distance

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        self._dragging = True
        self._last_mouse = pos

    def on_mouse_up(self) -> None:
        self._dragging = False

    def on_mouse_motion(self, pos: tuple[int, int]) -> None:
        if not self._dragging:
            return
        dx = pos[0] - self._last_mouse[0]
        dy = pos[1] - self._last_mouse[1]
        self.yaw += dx * 0.4
        self.pitch = max(-89.0, min(89.0, self.pitch - dy * 0.4))
        self._last_mouse = pos

    def on_mouse_wheel(self, direction: int) -> None:
        """direction: +1 zoom in, -1 zoom out."""
        self.distance -= direction * 4.0
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))

    def apply_view(self) -> None:
        """
        Position the camera using spherical coordinates.

        eye = (distance · cos(pitch) · sin(yaw),
               distance · sin(pitch),
               distance · cos(pitch) · cos(yaw))
        """
        glLoadIdentity()
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        eye_x = self.distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        eye_y = self.distance * math.sin(pitch_rad)
        eye_z = self.distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        gluLookAt(eye_x, eye_y, eye_z, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    def get_view_matrix(self) -> np.ndarray:
        """Return a 4x4 view matrix (for educational / debugging use)."""
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        eye = np.array(
            [
                self.distance * math.cos(pitch_rad) * math.sin(yaw_rad),
                self.distance * math.sin(pitch_rad),
                self.distance * math.cos(pitch_rad) * math.cos(yaw_rad),
            ],
            dtype=np.float32,
        )
        target = np.zeros(3, dtype=np.float32)
        up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        forward = target - eye
        forward /= np.linalg.norm(forward)
        right = np.cross(forward, up)
        right /= np.linalg.norm(right)
        up_corrected = np.cross(right, forward)

        view = np.identity(4, dtype=np.float32)
        view[0, :3] = right
        view[1, :3] = up_corrected
        view[2, :3] = -forward
        view[0, 3] = -np.dot(right, eye)
        view[1, 3] = -np.dot(up_corrected, eye)
        view[2, 3] = np.dot(forward, eye)
        return view
