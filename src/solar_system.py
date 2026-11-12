"""
Solar system model containing the Sun, planets, and moons.

Distances and speeds are scaled for visual clarity, not physical accuracy.
"""

from __future__ import annotations

from src.celestial_body import Moon, Planet, Sun


class SolarSystem:
    """Manages all celestial bodies and simulation state."""

    def __init__(self) -> None:
        self.sun = Sun()
        self.planets: list[Planet] = self._create_planets()
        self.selected_planet_index: int = 2  # Earth by default
        self.speed_multiplier: float = 1.0
        self.paused: bool = False
        self.reverse_orbit: bool = False

    def _create_planets(self) -> list[Planet]:
        """Create 8 planets with at least 3 moons across the system."""
        return [
            Planet(
                name="Mercury",
                radius=0.35,
                orbit_distance=6.0,
                orbit_speed=12.0,
                self_rotation_speed=8.0,
                color=(0.65, 0.60, 0.55),
            ),
            Planet(
                name="Venus",
                radius=0.55,
                orbit_distance=9.0,
                orbit_speed=9.0,
                self_rotation_speed=5.0,
                color=(0.90, 0.75, 0.45),
            ),
            Planet(
                name="Earth",
                radius=0.60,
                orbit_distance=12.0,
                orbit_speed=7.0,
                self_rotation_speed=20.0,
                color=(0.25, 0.45, 0.85),
                moons=[
                    Moon(
                        name="Moon",
                        radius=0.18,
                        orbit_distance=1.4,
                        orbit_speed=30.0,
                        color=(0.70, 0.70, 0.72),
                    ),
                ],
            ),
            Planet(
                name="Mars",
                radius=0.45,
                orbit_distance=15.0,
                orbit_speed=5.5,
                self_rotation_speed=18.0,
                color=(0.80, 0.35, 0.25),
                moons=[
                    Moon(
                        name="Phobos",
                        radius=0.10,
                        orbit_distance=1.0,
                        orbit_speed=45.0,
                        color=(0.55, 0.50, 0.48),
                    ),
                    Moon(
                        name="Deimos",
                        radius=0.08,
                        orbit_distance=1.6,
                        orbit_speed=35.0,
                        color=(0.50, 0.48, 0.46),
                    ),
                ],
            ),
            Planet(
                name="Jupiter",
                radius=1.40,
                orbit_distance=22.0,
                orbit_speed=3.5,
                self_rotation_speed=35.0,
                color=(0.85, 0.70, 0.55),
                moons=[
                    Moon(
                        name="Io",
                        radius=0.22,
                        orbit_distance=2.5,
                        orbit_speed=25.0,
                        color=(0.95, 0.85, 0.40),
                    ),
                ],
            ),
            Planet(
                name="Saturn",
                radius=1.20,
                orbit_distance=28.0,
                orbit_speed=2.8,
                self_rotation_speed=30.0,
                color=(0.90, 0.82, 0.60),
            ),
            Planet(
                name="Uranus",
                radius=0.85,
                orbit_distance=34.0,
                orbit_speed=2.0,
                self_rotation_speed=15.0,
                color=(0.55, 0.80, 0.85),
            ),
            Planet(
                name="Neptune",
                radius=0.82,
                orbit_distance=40.0,
                orbit_speed=1.5,
                self_rotation_speed=14.0,
                color=(0.30, 0.45, 0.90),
            ),
        ]

    @property
    def selected_planet(self) -> Planet:
        return self.planets[self.selected_planet_index]

    def select_next_planet(self) -> None:
        self.selected_planet_index = (self.selected_planet_index + 1) % len(self.planets)

    def select_previous_planet(self) -> None:
        self.selected_planet_index = (self.selected_planet_index - 1) % len(self.planets)

    def increase_speed(self) -> None:
        self.speed_multiplier = min(self.speed_multiplier + 0.25, 10.0)

    def decrease_speed(self) -> None:
        self.speed_multiplier = max(self.speed_multiplier - 0.25, 0.0)

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def toggle_reverse(self) -> None:
        self.reverse_orbit = not self.reverse_orbit

    def increase_selected_size(self) -> None:
        planet = self.selected_planet
        planet.size_multiplier = min(planet.size_multiplier + 0.1, 3.0)

    def decrease_selected_size(self) -> None:
        planet = self.selected_planet
        planet.size_multiplier = max(planet.size_multiplier - 0.1, 0.3)

    def update(self, delta_time: float) -> None:
        if self.paused:
            return
        for planet in self.planets:
            planet.update(delta_time, self.speed_multiplier, self.reverse_orbit)
