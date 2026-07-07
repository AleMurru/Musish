from __future__ import annotations

import math
from collections.abc import Iterable

from pygame.math import Vector2

from .boids import Boid


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


class OnePoleSmoother:
    """Simple low-pass filter to avoid jitter in OSC/Max."""

    def __init__(self, alpha: float = 0.18):
        self.alpha = alpha
        self.state: dict[str, float] = {}

    def process(self, values: dict[str, float]) -> dict[str, float]:
        out: dict[str, float] = {}
        for key, value in values.items():
            if key not in self.state:
                self.state[key] = value
            else:
                self.state[key] += self.alpha * (value - self.state[key])
            out[key] = self.state[key]
        return out


def compute_descriptors(boids: Iterable[Boid], width: int, height: int) -> dict[str, float]:
    boids = list(boids)
    count = len(boids)
    if count == 0:
        return {
            "fish_count": 0.0,
            "mean_speed": 0.0,
            "energy": 0.0,
            "center_x": 0.5,
            "center_y": 0.5,
            "spread": 0.0,
            "density": 0.0,
            "nearest_distance": 1.0,
            "direction_coherence": 0.0,
            "cluster_count": 0.0,
        }

    positions = [b.position for b in boids]
    velocities = [b.velocity for b in boids]
    max_speed = max((b.max_speed for b in boids), default=4.0)
    diagonal = math.hypot(width, height)

    center = sum(positions, Vector2(0, 0)) / count
    speeds = [v.length() for v in velocities]
    mean_speed = clamp01((sum(speeds) / count) / max_speed)

    mean_distance_to_center = sum(p.distance_to(center) for p in positions) / count
    spread = clamp01(mean_distance_to_center / (diagonal * 0.28))

    nearest_values: list[float] = []
    for i, pos in enumerate(positions):
        nearest = diagonal
        for j, other in enumerate(positions):
            if i == j:
                continue
            nearest = min(nearest, pos.distance_to(other))
        nearest_values.append(nearest)
    nearest_distance = clamp01((sum(nearest_values) / count) / 120.0)

    avg_heading = Vector2(0, 0)
    for vel in velocities:
        if vel.length_squared() > 0:
            avg_heading += vel.normalize()
    direction_coherence = clamp01(avg_heading.length() / count)

    # Lightweight cluster estimate: count occupied coarse grid zones, normalized.
    # It is not a real DBSCAN, but gives a useful live descriptor for day 1/2.
    cell = 180
    occupied = {(int(p.x // cell), int(p.y // cell)) for p in positions}
    cluster_count = clamp01(len(occupied) / 12.0)

    return {
        "fish_count": clamp01(count / 160.0),
        "mean_speed": mean_speed,
        "energy": mean_speed,
        "center_x": clamp01(center.x / width),
        "center_y": clamp01(center.y / height),
        "spread": spread,
        "density": clamp01(1.0 - nearest_distance),
        "nearest_distance": nearest_distance,
        "direction_coherence": direction_coherence,
        "cluster_count": cluster_count,
    }


DESCRIPTOR_ORDER = [
    "fish_count",
    "mean_speed",
    "energy",
    "center_x",
    "center_y",
    "spread",
    "density",
    "nearest_distance",
    "direction_coherence",
    "cluster_count",
]
