"""Local descriptor sanity test, no Max/MIDIMIX required.

Usage:
    cd Codex
    python tools/test_descriptors.py

This verifies that the core boids descriptors react in the expected direction:
- aligned velocities -> high direction_coherence
- opposite/random velocities -> low direction_coherence
- compact flock -> high density / low spread
- spread flock -> low density / high spread
- left/right positions -> center_x changes
- slow/fast velocities -> mean_speed changes
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pygame.math import Vector2

from aquarium_boids.boids import Boid
from aquarium_boids.descriptors import compute_descriptors

WIDTH = 1200
HEIGHT = 750


def make_boid(idx: int, x: float, y: float, vx: float, vy: float, max_speed: float = 4.0) -> Boid:
    return Boid(
        id=idx,
        position=Vector2(x, y),
        velocity=Vector2(vx, vy),
        acceleration=Vector2(0, 0),
        size=8.0,
        color=(100, 200, 255),
        max_speed=max_speed,
    )


def print_case(name: str, descriptors: dict[str, float]) -> None:
    keys = ["mean_speed", "center_x", "center_y", "spread", "density", "nearest_distance", "direction_coherence"]
    values = " | ".join(f"{key}={descriptors[key]:.3f}" for key in keys)
    print(f"{name:16s} {values}")


def assert_range(name: str, value: float) -> None:
    assert 0.0 <= value <= 1.0, f"{name} out of normalized range: {value}"


def main() -> None:
    aligned = [make_boid(i, 480 + i * 6, 360 + (i % 3) * 5, 4, 0) for i in range(16)]
    opposite = [make_boid(i, 480 + i * 6, 360 + (i % 3) * 5, 4 if i % 2 == 0 else -4, 0) for i in range(16)]
    compact = [make_boid(i, 590 + (i % 4) * 8, 365 + (i // 4) * 8, 2, 0) for i in range(16)]
    spread = [make_boid(i, 120 + (i % 4) * 300, 120 + (i // 4) * 170, 2, 0) for i in range(16)]
    left = [make_boid(i, 120 + (i % 4) * 20, 300 + (i // 4) * 20, 2, 0) for i in range(16)]
    right = [make_boid(i, 920 + (i % 4) * 20, 300 + (i // 4) * 20, 2, 0) for i in range(16)]
    slow = [make_boid(i, 480 + i * 6, 360, 0.4, 0) for i in range(16)]
    fast = [make_boid(i, 480 + i * 6, 360, 4.0, 0) for i in range(16)]

    cases = {
        "aligned": compute_descriptors(aligned, WIDTH, HEIGHT),
        "opposite": compute_descriptors(opposite, WIDTH, HEIGHT),
        "compact": compute_descriptors(compact, WIDTH, HEIGHT),
        "spread": compute_descriptors(spread, WIDTH, HEIGHT),
        "left": compute_descriptors(left, WIDTH, HEIGHT),
        "right": compute_descriptors(right, WIDTH, HEIGHT),
        "slow": compute_descriptors(slow, WIDTH, HEIGHT),
        "fast": compute_descriptors(fast, WIDTH, HEIGHT),
    }

    for name, desc in cases.items():
        print_case(name, desc)
        for key, value in desc.items():
            assert_range(f"{name}.{key}", value)

    assert cases["aligned"]["direction_coherence"] > 0.95, "aligned flock should have high coherence"
    assert cases["opposite"]["direction_coherence"] < 0.15, "opposite flock should have low coherence"
    assert cases["compact"]["density"] > cases["spread"]["density"], "compact flock should have higher density"
    assert cases["compact"]["spread"] < cases["spread"]["spread"], "compact flock should have lower spread"
    assert cases["left"]["center_x"] < 0.25, "left flock center_x should be low"
    assert cases["right"]["center_x"] > 0.75, "right flock center_x should be high"
    assert cases["slow"]["mean_speed"] < cases["fast"]["mean_speed"], "fast flock should have higher mean_speed"

    print("\nOK: descriptor sanity checks passed.")


if __name__ == "__main__":
    main()
