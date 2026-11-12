"""
Main application loop using GLUT for window and event management.

GLUT is used instead of Pygame for broad Python version compatibility.
"""

from __future__ import annotations

import sys
import time

from OpenGL.GL import glViewport
from OpenGL.GLUT import (
    GLUT_DEPTH,
    GLUT_DOUBLE,
    GLUT_RGB,
    glutCreateWindow,
    glutDisplayFunc,
    glutIdleFunc,
    glutInit,
    glutInitDisplayMode,
    glutInitWindowSize,
    glutKeyboardFunc,
    glutMainLoop,
    glutMotionFunc,
    glutMouseFunc,
    glutPassiveMotionFunc,
    glutPostRedisplay,
    glutReshapeFunc,
    glutSpecialFunc,
    glutSwapBuffers,
)

from src.camera import Camera
from src.hud import draw_text_overlay
from src.renderer import Renderer
from src.solar_system import SolarSystem


class Application:
    """GLUT + OpenGL application targeting 60 FPS with delta-time animation."""

    TARGET_FPS = 60
    WINDOW_TITLE = b"Hierarchical Solar System Simulator"
    INITIAL_SIZE = (1280, 720)

    def __init__(self) -> None:
        self.last_time = time.perf_counter()
        self.camera = Camera()
        self.solar_system = SolarSystem()
        width, height = self.INITIAL_SIZE
        self.renderer: Renderer | None = None
        self._pending_size = (width, height)
        self._show_hud = True
        self._mouse_left_down = False
        self._last_mouse = (0, 0)

    def run(self) -> None:
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(*self.INITIAL_SIZE)
        glutCreateWindow(self.WINDOW_TITLE)

        self.renderer = Renderer(*self._pending_size)

        glutDisplayFunc(self._display)
        glutIdleFunc(self._idle)
        glutReshapeFunc(self._reshape)
        glutKeyboardFunc(self._keyboard)
        glutSpecialFunc(self._special)
        glutMouseFunc(self._mouse)
        glutMotionFunc(self._mouse_motion)
        glutPassiveMotionFunc(self._mouse_motion)

        glutMainLoop()

    def _idle(self) -> None:
        now = time.perf_counter()
        delta_time = now - self.last_time
        self.last_time = now
        delta_time = min(delta_time, 0.05)
        self.solar_system.update(delta_time)
        glutPostRedisplay()

    def _display(self) -> None:
        assert self.renderer is not None
        self.renderer.begin_frame(self.camera)
        self.renderer.render(self.solar_system)
        self._draw_hud()
        glutSwapBuffers()

    def _reshape(self, width: int, height: int) -> None:
        glViewport(0, 0, width, height)
        if self.renderer is not None:
            self.renderer.resize(width, height)

    def _keyboard(self, key: bytes, _x: int, _y: int) -> None:
        char = key.decode("utf-8", errors="ignore").lower()
        if char == "\x1b":  # ESC
            sys.exit(0)
        elif char == " ":
            self.solar_system.toggle_pause()
        elif char == "r":
            self.solar_system.toggle_reverse()
        elif char in ("+", "="):
            self.solar_system.increase_selected_size()
        elif char == "-":
            self.solar_system.decrease_selected_size()
        elif char == "c":
            self.camera.reset()
        elif char == "h":
            self._show_hud = not self._show_hud

    def _special(self, key: int, _x: int, _y: int) -> None:
        # GLUT key codes
        GLUT_KEY_UP = 101
        GLUT_KEY_DOWN = 103
        GLUT_KEY_LEFT = 100
        GLUT_KEY_RIGHT = 102

        if key == GLUT_KEY_UP:
            self.solar_system.increase_speed()
        elif key == GLUT_KEY_DOWN:
            self.solar_system.decrease_speed()
        elif key == GLUT_KEY_LEFT:
            self.solar_system.select_previous_planet()
        elif key == GLUT_KEY_RIGHT:
            self.solar_system.select_next_planet()

    def _mouse(self, button: int, state: int, x: int, y: int) -> None:
        GLUT_LEFT_BUTTON = 0
        GLUT_DOWN = 0
        GLUT_UP = 1

        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self._mouse_left_down = True
                self._last_mouse = (x, y)
                self.camera.on_mouse_down((x, y))
            else:
                self._mouse_left_down = False
                self.camera.on_mouse_up()
        elif state == GLUT_DOWN:
            if button == 3:
                self.camera.on_mouse_wheel(1)
            elif button == 4:
                self.camera.on_mouse_wheel(-1)

    def _mouse_motion(self, x: int, y: int) -> None:
        if self._mouse_left_down:
            self.camera.on_mouse_motion((x, y))

    def _draw_hud(self) -> None:
        if not self._show_hud or self.renderer is None:
            return
        planet = self.solar_system.selected_planet
        status = "PAUSED" if self.solar_system.paused else "RUNNING"
        direction = "REVERSE" if self.solar_system.reverse_orbit else "FORWARD"
        lines = [
            f"Status: {status} | Direction: {direction} | Speed: {self.solar_system.speed_multiplier:.2f}x",
            f"Selected: {planet.name} (size {planet.size_multiplier:.1f}x)  [Left/Right cycle]",
            "Up/Down speed | SPACE pause | R reverse | +/- size | C reset camera | H HUD | ESC quit",
            "Drag mouse to rotate view | Scroll to zoom",
        ]
        draw_text_overlay(self.renderer.width, self.renderer.height, lines)


def main() -> None:
    Application().run()


if __name__ == "__main__":
    main()
