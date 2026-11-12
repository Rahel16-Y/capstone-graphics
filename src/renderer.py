"""
OpenGL renderer with hierarchical matrix transformations.

Transformation hierarchy (per planet):
    Sun
      └── Planet: Rotate(orbit) → Translate(distance) → Rotate(self)
            └── Moon: Rotate(moon_orbit) → Translate(moon_distance)
"""

from __future__ import annotations

from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_SMOOTH,
    glClear,
    glClearColor,
    glEnable,
    glLoadIdentity,
    glMatrixMode,
    glShadeModel,
)
from OpenGL.GLU import gluPerspective

from src.camera import Camera
from src.celestial_body import Moon, Planet
from src.matrix_stack import MatrixStack
from src.solar_system import SolarSystem
from src.sphere import draw_orbit_path


class Renderer:
    """Handles OpenGL state, projection, and hierarchical drawing."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.matrix_stack = MatrixStack()
        self._setup_gl()

    def _setup_gl(self) -> None:
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        self.resize(self.width, self.height)

    def resize(self, width: int, height: int) -> None:
        self.width = max(width, 1)
        self.height = max(height, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width / self.height
        gluPerspective(45.0, aspect, 0.1, 500.0)
        glMatrixMode(GL_MODELVIEW)

    def begin_frame(self, camera: Camera) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        camera.apply_view()

    def render(self, solar_system: SolarSystem) -> None:
        self._draw_sun(solar_system)
        for planet in solar_system.planets:
            self._draw_planet_orbit(planet)
            self._draw_planet_hierarchy(planet)

    def _draw_sun(self, solar_system: SolarSystem) -> None:
        sun = solar_system.sun
        self.matrix_stack.load_identity()
        self.matrix_stack.apply_to_gl()
        sun.mesh.draw_solid(sun.color)

    def _draw_planet_orbit(self, planet: Planet) -> None:
        """Draw orbital path at world origin (before planet transform)."""
        self.matrix_stack.load_identity()
        self.matrix_stack.apply_to_gl()
        draw_orbit_path(planet.orbit_distance, color=(0.25, 0.25, 0.35))

    def _draw_planet_hierarchy(self, planet: Planet) -> None:
        """
        Hierarchical transform chain for a planet and its moons.

        1. Rotate by orbit angle around Sun (Y axis)
        2. Translate to orbital distance
        3. Rotate for self-rotation
        4. For each moon: push, rotate, translate, draw, pop
        """
        self.matrix_stack.load_identity()

        # Step 1: orbital rotation around Sun
        self.matrix_stack.rotate_y(planet.orbit_angle)

        # Step 2: move to orbital radius
        # Equivalent to: x = distance * cos(angle), z = distance * sin(angle)
        self.matrix_stack.translate(planet.orbit_distance, 0.0, 0.0)

        # Draw moon orbital paths relative to planet position
        for moon in planet.moons:
            self.matrix_stack.push()
            self.matrix_stack.apply_to_gl()
            draw_orbit_path(moon.orbit_distance, segments=64, color=(0.35, 0.35, 0.45))
            self.matrix_stack.pop()

        # Step 3: self-rotation
        self.matrix_stack.rotate_y(planet.self_rotation_angle)

        # Step 4: scale for user-adjusted size
        scale = planet.display_radius / planet.radius
        self.matrix_stack.scale(scale)

        self.matrix_stack.apply_to_gl()
        planet.mesh.draw_solid(planet.color)

        # Moons inherit planet transform via matrix stack push/pop
        for moon in planet.moons:
            self._draw_moon_hierarchy(moon)

    def _draw_moon_hierarchy(self, moon: Moon) -> None:
        """
        Moon transform relative to host planet:
            Planet transform → Rotate(moon_angle) → Translate(moon_distance)
        """
        self.matrix_stack.push()
        self.matrix_stack.rotate_y(moon.orbit_angle)
        self.matrix_stack.translate(moon.orbit_distance, 0.0, 0.0)
        self.matrix_stack.apply_to_gl()
        moon.mesh.draw_solid(moon.color)
        self.matrix_stack.pop()
