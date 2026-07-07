from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame
from pygame.math import Vector2

from .controls import RuntimeControls


def limit_vector(vector: Vector2, max_length: float) -> Vector2:
    if vector.length_squared() > max_length * max_length:
        vector.scale_to_length(max_length)
    return vector


@dataclass
class Boid:
    id: int
    position: Vector2
    velocity: Vector2
    acceleration: Vector2
    size: float
    color: tuple[int, int, int]
    max_speed: float = 4.0
    max_force: float = 0.055
    flash: float = 0.0

    @classmethod
    def create(cls, boid_id: int, width: int, height: int) -> "Boid":
        angle = random.uniform(0.0, math.tau)
        speed = random.uniform(2.0, 4.0)
        return cls(
            id=boid_id,
            position=Vector2(random.uniform(width * 0.2, width * 0.8), random.uniform(height * 0.2, height * 0.8)),
            velocity=Vector2(math.cos(angle), math.sin(angle)) * speed,
            acceleration=Vector2(0, 0),
            size=random.uniform(6.0, 11.0),
            color=random.choice([(80, 210, 255), (105, 255, 190), (255, 190, 95), (220, 160, 255)]),
        )

    def _steer_towards(self, desired: Vector2) -> Vector2:
        if desired.length_squared() == 0:
            return Vector2(0, 0)
        desired = desired.normalize() * self.max_speed
        steer = desired - self.velocity
        return limit_vector(steer, self.max_force)

    def align(self, boids: list["Boid"], radius: float = 90.0) -> Vector2:
        steering = Vector2(0, 0)
        total = 0
        r2 = radius * radius
        for other in boids:
            if other is self:
                continue
            if self.position.distance_squared_to(other.position) < r2:
                steering += other.velocity
                total += 1
        if total == 0:
            return Vector2(0, 0)
        steering /= total
        return self._steer_towards(steering)

    def cohesion(self, boids: list["Boid"], radius: float = 105.0) -> Vector2:
        center = Vector2(0, 0)
        total = 0
        r2 = radius * radius
        for other in boids:
            if other is self:
                continue
            if self.position.distance_squared_to(other.position) < r2:
                center += other.position
                total += 1
        if total == 0:
            return Vector2(0, 0)
        center /= total
        return self._steer_towards(center - self.position)

    def separation(self, boids: list["Boid"], radius: float = 38.0) -> Vector2:
        steering = Vector2(0, 0)
        total = 0
        r2 = radius * radius
        for other in boids:
            if other is self:
                continue
            delta = self.position - other.position
            d2 = delta.length_squared()
            if 0 < d2 < r2:
                # Stronger repulsion when very close.
                steering += delta / max(d2, 0.001)
                total += 1
        if total == 0:
            return Vector2(0, 0)
        steering /= total
        return self._steer_towards(steering)

    def avoid_walls(self, width: int, height: int, border: float = 80.0) -> Vector2:
        desired = Vector2(0, 0)
        if self.position.x < border:
            desired.x += 1
        elif self.position.x > width - border:
            desired.x -= 1
        if self.position.y < border:
            desired.y += 1
        elif self.position.y > height - border:
            desired.y -= 1
        return self._steer_towards(desired) * 2.5 if desired.length_squared() > 0 else desired

    def flock(
        self,
        boids: list["Boid"],
        controls: RuntimeControls,
        width: int,
        height: int,
        attractor: Vector2 | None = None,
        repeller: Vector2 | None = None,
    ) -> None:
        alignment = self.align(boids) * controls.alignment_weight
        cohesion = self.cohesion(boids) * controls.cohesion_weight
        separation = self.separation(boids) * controls.separation_weight
        noise = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * self.max_force * controls.noise_weight
        walls = self.avoid_walls(width, height)

        self.acceleration = alignment + cohesion + separation + noise + walls

        # Performance gestures: left mouse = food/attractor, right mouse = predator/repeller.
        if attractor is not None:
            self.acceleration += self._steer_towards(attractor - self.position) * (0.9 * controls.food_strength)
        if repeller is not None:
            delta = self.position - repeller
            distance = max(delta.length(), 1.0)
            if distance < 220:
                self.acceleration += self._steer_towards(delta) * (2.8 * controls.predator_strength * (1.0 - distance / 220.0))

    def update(self, dt_scale: float = 1.0) -> None:
        self.velocity += self.acceleration * dt_scale
        limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity * dt_scale
        self.flash = max(0.0, self.flash - 0.045 * dt_scale)

    def draw(self, surface: pygame.Surface) -> None:
        heading = math.atan2(self.velocity.y, self.velocity.x)
        tip = Vector2(self.size * 1.8, 0).rotate_rad(heading)
        left = Vector2(-self.size, self.size * 0.75).rotate_rad(heading)
        right = Vector2(-self.size, -self.size * 0.75).rotate_rad(heading)
        points = [self.position + tip, self.position + left, self.position + right]

        color = self.color
        if self.flash > 0:
            color = tuple(min(255, int(c + 140 * self.flash)) for c in color)
            pygame.draw.circle(surface, (255, 255, 255), self.position, int(self.size * (1.4 + self.flash)), 1)
        pygame.draw.polygon(surface, color, points)
