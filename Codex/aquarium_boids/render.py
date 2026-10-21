"""Display-only rendering.

Rule for everything in this module: read the flock, controls and descriptors, never
write to them, and never call the global `random` module (it shares its stream with
the simulation and the Markov generator, so any extra call would change the OSC output).
"""
from __future__ import annotations

import math
import time
from contextlib import contextmanager

import pygame
from pygame.math import Vector2

from .boids import Boid
from .config import BACKGROUND, CONTROL_PORT, OSC_HOST, OSC_PORT, TEXT
from .controls import RuntimeControls

# Optional per-stage timing: an external profiler may set this to a dict; stays None otherwise.
STAGE_ACC: dict[str, float] | None = None


@contextmanager
def _stage(name: str):
    if STAGE_ACC is None:
        yield
        return
    start = time.perf_counter()
    try:
        yield
    finally:
        STAGE_ACC[name] = STAGE_ACC.get(name, 0.0) + time.perf_counter() - start


class View:
    """Maps the fixed simulation world into a canvas: uniform scale, centred, letterboxed.

    The simulation always runs at the world size (config WIDTH x HEIGHT); only the
    picture is scaled. With canvas == world size this is the identity mapping.
    """

    def __init__(self, world_size: tuple[int, int], canvas_size: tuple[int, int]):
        ww, wh = world_size
        cw, ch = canvas_size
        self.world_size = (ww, wh)
        self.canvas_size = (cw, ch)
        self.is_identity = (cw, ch) == (ww, wh)
        self.scale = min(cw / ww, ch / wh)
        vw, vh = round(ww * self.scale), round(wh * self.scale)
        self.rect = pygame.Rect((cw - vw) // 2, (ch - vh) // 2, vw, vh)

    def to_world(self, pos: tuple[int, int]) -> Vector2:
        """Canvas pixel (e.g. mouse) -> world coordinates, clamped to the world."""
        if self.is_identity:
            return Vector2(pos)
        ww, wh = self.world_size
        x = (pos[0] - self.rect.x) / self.scale
        y = (pos[1] - self.rect.y) / self.scale
        return Vector2(max(0.0, min(ww - 1.0, x)), max(0.0, min(wh - 1.0, y)))


class Display:
    """Owns the window: windowed size, fullscreen toggle, current canvas and view."""

    def __init__(
        self,
        world_size: tuple[int, int],
        window_size: tuple[int, int],
        caption: str,
        fullscreen: bool = False,
    ):
        self.world_size = world_size
        self.window_size = window_size
        self.caption = caption
        self.fullscreen = False
        self.canvas: pygame.Surface
        self.view: View
        desktop = pygame.display.get_desktop_sizes()[0]
        if window_size[0] > desktop[0] or window_size[1] > desktop[1]:
            print(f"[display] window {window_size[0]}x{window_size[1]} is larger than the desktop "
                  f"{desktop[0]}x{desktop[1]}; press F11 for fullscreen")
        self._set_mode(fullscreen)

    def _set_mode(self, fullscreen: bool) -> None:
        # "Fullscreen" is a borderless window covering the desktop, not exclusive
        # fullscreen: no display-mode switch, and it is not minimised when focus moves
        # to another app (e.g. Max) during a recording.
        pygame.display.set_caption(self.caption)
        if fullscreen:
            self.canvas = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0], pygame.NOFRAME)
            self._move_window((0, 0))
        else:
            self.canvas = pygame.display.set_mode(self.window_size)
            if self.fullscreen:
                self._move_window(None)
        self.fullscreen = fullscreen
        self.view = View(self.world_size, self.canvas.get_size())

    @staticmethod
    def _move_window(position: tuple[int, int] | None) -> None:
        """Move the window (None = centre). Best effort: pygame._sdl2 ships with pygame."""
        try:
            from pygame._sdl2.video import WINDOWPOS_CENTERED, Window

            window = Window.from_display_module()
            window.position = WINDOWPOS_CENTERED if position is None else position
        except Exception:
            pass

    def toggle_fullscreen(self) -> None:
        self._set_mode(not self.fullscreen)


def draw_hud(
    surface: pygame.Surface,
    font: pygame.font.Font,
    controls: RuntimeControls,
    descriptors: dict[str, float],
    origin: tuple[int, int] = (0, 0),
) -> None:
    lines = [
        "Acquario / Boids -> Max | MIDIMIX direct + Max control ready",
        f"density_fader UP/DOWN: {controls.density_fader:.2f} | section 1-6: {controls.section_name}",
        f"A/Z align {controls.alignment_weight:.2f} | S/X cohesion {controls.cohesion_weight:.2f} | D/C separation {controls.separation_weight:.2f} | N/M noise {controls.noise_weight:.2f}",
        f"food_amount {controls.food_amount:.2f} | predator_amount {controls.predator_amount:.2f} | mouse food/pred {controls.food_strength:.2f}/{controls.predator_strength:.2f}",
        f"fish -/= : {controls.population} (fish_count {descriptors.get('fish_count', 0):.2f}) -> granular density",
        "Mouse left = food/attractor | mouse right = predator/repeller | SPACE pause | R reset",
        f"OSC out: {OSC_HOST}:{OSC_PORT} | plain out: 7401 | control in: {CONTROL_PORT}",
        f"mean_speed {descriptors.get('mean_speed', 0):.2f} | density {descriptors.get('density', 0):.2f} | spread {descriptors.get('spread', 0):.2f} | coherence {descriptors.get('direction_coherence', 0):.2f}",
    ]
    x0, y = origin[0] + 12, origin[1] + 10
    for line in lines:
        img = font.render(line, True, TEXT)
        surface.blit(img, (x0, y))
        y += 20


class ClassicRenderer:
    """The original look: flat background, triangle fish, rings, text HUD.

    At the native size it draws straight onto the canvas (pixel-identical to the
    original). Otherwise it draws the world at native size and smooth-scales it into
    the view, so the classic look stays exactly the same, only bigger.
    """

    def __init__(self, font: pygame.font.Font):
        self.font = font
        self._world: pygame.Surface | None = None

    def handle_key(self, key: int) -> bool:
        """Display keys; the classic look has none (H stays a no-op, as before)."""
        return False

    def draw(
        self,
        canvas: pygame.Surface,
        view: View,
        flock: list[Boid],
        attractor: Vector2 | None,
        repeller: Vector2 | None,
        controls: RuntimeControls,
        descriptors: dict[str, float],
    ) -> None:
        if view.is_identity:
            self._draw_world(canvas, flock, attractor, repeller)
            draw_hud(canvas, self.font, controls, descriptors)
            return
        if self._world is None or self._world.get_size() != view.world_size:
            self._world = pygame.Surface(view.world_size)
        self._draw_world(self._world, flock, attractor, repeller)
        canvas.fill(BACKGROUND)
        pygame.transform.smoothscale(self._world, view.rect.size, canvas.subsurface(view.rect))
        draw_hud(canvas, self.font, controls, descriptors, origin=view.rect.topleft)

    @staticmethod
    def _draw_world(
        surface: pygame.Surface,
        flock: list[Boid],
        attractor: Vector2 | None,
        repeller: Vector2 | None,
    ) -> None:
        surface.fill(BACKGROUND)
        if attractor is not None:
            pygame.draw.circle(surface, (80, 255, 150), attractor, 18, 2)
        if repeller is not None:
            pygame.draw.circle(surface, (255, 80, 90), repeller, 34, 2)
        for boid in flock:
            boid.draw(surface)


THERMAL_BACKGROUND = (0, 0, 0)
PLACEHOLDER_FISH = (255, 170, 60)  # replaced by heat-mapped sprites in a later commit


class ThermalRenderer:
    """Dark "thermal" look, drawn directly at canvas resolution through the view.

    Modes: "art" (no text, for recording) and "data" (same picture + HUD), toggled with H.
    """

    MODES = ("art", "data")

    def __init__(self, font: pygame.font.Font, mode: str = "art"):
        self.font = font
        self.mode = mode

    def handle_key(self, key: int) -> bool:
        if key == pygame.K_h:
            self.mode = "data" if self.mode == "art" else "art"
            return True
        return False

    def draw(
        self,
        canvas: pygame.Surface,
        view: View,
        flock: list[Boid],
        attractor: Vector2 | None,
        repeller: Vector2 | None,
        controls: RuntimeControls,
        descriptors: dict[str, float],
    ) -> None:
        with _stage("thermal.background"):
            canvas.fill(THERMAL_BACKGROUND)
        canvas.set_clip(view.rect)
        scale = view.scale
        ox, oy = view.rect.topleft
        with _stage("thermal.fish"):
            for boid in flock:
                self._draw_fish(canvas, boid, scale, ox, oy)
        with _stage("thermal.events"):
            if attractor is not None:
                pygame.draw.circle(canvas, (80, 255, 150), (ox + attractor.x * scale, oy + attractor.y * scale), 18 * scale, 2)
            if repeller is not None:
                pygame.draw.circle(canvas, (255, 80, 90), (ox + repeller.x * scale, oy + repeller.y * scale), 34 * scale, 2)
        canvas.set_clip(None)
        if self.mode == "data":
            draw_hud(canvas, self.font, controls, descriptors, origin=view.rect.topleft)

    @staticmethod
    def _draw_fish(canvas: pygame.Surface, boid: Boid, scale: float, ox: int, oy: int) -> None:
        """Placeholder: the classic triangle in one warm colour (sprites come next)."""
        heading = math.atan2(boid.velocity.y, boid.velocity.x)
        cos_h, sin_h = math.cos(heading), math.sin(heading)
        size = boid.size * scale
        cx, cy = ox + boid.position.x * scale, oy + boid.position.y * scale
        points = []
        for fx, fy in ((1.8, 0.0), (-1.0, 0.75), (-1.0, -0.75)):
            x, y = fx * size, fy * size
            points.append((cx + x * cos_h - y * sin_h, cy + x * sin_h + y * cos_h))
        color = PLACEHOLDER_FISH
        if boid.flash > 0:
            color = tuple(min(255, int(c + 140 * boid.flash)) for c in color)
        pygame.draw.polygon(canvas, color, points)
