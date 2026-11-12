"""
Celestial body classes: Sun, Planet, and Moon.

Each body stores orbital parameters updated each frame with:
    angle += speed * delta_time
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.sphere import SphereMesh


@dataclass
class Moon:
    """A moon orbiting a host planet."""

    name: str
    radius: float
    orbit_distance: float
    orbit_speed: float  # degrees per second
    color: tuple[float, float, float] = (0.75, 0.75, 0.75)
    orbit_angle: float = 0.0
    mesh: SphereMesh = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.mesh = SphereMesh(self.radius, slices=12, stacks=10)

    def update(self, delta_time: float, speed_multiplier: float, reverse: bool) -> None:
        direction = -1.0 if reverse else 1.0
        self.orbit_angle += direction * self.orbit_speed * delta_time * speed_multiplier
        self.orbit_angle %= 360.0


@dataclass
class Planet:
    """A planet orbiting the Sun with optional moons."""

    name: str
    radius: float
    orbit_distance: float
    orbit_speed: float
    self_rotation_speed: float
    color: tuple[float, float, float]
    moons: list[Moon] = field(default_factory=list)
    orbit_angle: float = 0.0
    self_rotation_angle: float = 0.0
    size_multiplier: float = 1.0
    mesh: SphereMesh = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.mesh = SphereMesh(self.radius, slices=20, stacks=14)

    @property
    def display_radius(self) -> float:
        return self.radius * self.size_multiplier

    def update(self, delta_time: float, speed_multiplier: float, reverse: bool) -> None:
        direction = -1.0 if reverse else 1.0
        self.orbit_angle += direction * self.orbit_speed * delta_time * speed_multiplier
        self.orbit_angle %= 360.0
        self.self_rotation_angle += (
            direction * self.self_rotation_speed * delta_time * speed_multiplier
        )
        self.self_rotation_angle %= 360.0
        for moon in self.moons:
            moon.update(delta_time, speed_multiplier, reverse)


@dataclass
class Sun:
    """Central star at the origin."""

    name: str = "Sun"
    radius: float = 2.5
    color: tuple[float, float, float] = (1.0, 0.85, 0.2)
    mesh: SphereMesh = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.mesh = SphereMesh(self.radius, slices=28, stacks=18)
