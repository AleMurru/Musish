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

# Fish silhouette, upper half from nose to tail notch, in units of boid.size, pointing +x
# (mirrored for the lower half). Same overall length as the classic triangle (1.8 .. -1.3).
FISH_OUTLINE = [
    (1.8, 0.0), (1.55, 0.26), (1.1, 0.46), (0.5, 0.54), (-0.1, 0.44),
    (-0.55, 0.2), (-0.8, 0.1), (-1.3, 0.56), (-1.08, 0.0),
]
# Thin bright core along the spine (ellipse), in the same units.
CORE_CENTER, CORE_HALF_LENGTH, CORE_HALF_WIDTH = 0.55, 0.8, 0.18
HALO_GROWTH = 1.3  # halo extent relative to the body
HEADINGS = 64
HEAT_LEVELS = 8
SIZE_BINS = (6.8, 8.5, 10.2)  # boid.size is uniform 6..11 (boids.py:40)
SIZE_EDGES = (7.67, 9.33)
SUPERSAMPLE = 4

# Heat palette (heat = speed / max_speed): colour stops at heat 0, 0.5, 1.
# Body is blitted with MAX, so overlapping fish never add up. Its blue stays low and the
# core is dim, so the hottest fish peak around (255, 225, 45): warm yellow, never white.
BODY_STOPS = ((70, 20, 110), (210, 50, 50), (255, 140, 30))
CORE_STOPS = ((10, 5, 15), (30, 40, 10), (0, 85, 15))
# Halo is additive (dense areas glow). Green kept near zero, so piled-up halos saturate
# toward magenta instead of white.
HALO_STOPS = ((16, 3, 32), (34, 5, 30), (45, 8, 24))


# Trails: each frame the previous picture is multiplied by fade/256, then TRAIL_FLOOR is
# subtracted (an 8-bit multiply alone never reaches black; it stalls at a dim residue).
# Persistence follows flock energy (agitation): calm = short trails, agitated = long.
TRAIL_FADE_CALM = 205  # x0.80 per frame
TRAIL_FADE_AGITATED = 245  # x0.96 per frame (~0.25 s)
TRAIL_ENERGY_FULL = 0.45  # energy at which trails reach full length (live logs: p50 ~0.2, p95 ~0.4)
TRAIL_FLOOR = 2


def trail_fade(energy: float) -> int:
    t = max(0.0, min(1.0, energy / TRAIL_ENERGY_FULL))
    return int(round(TRAIL_FADE_CALM + (TRAIL_FADE_AGITATED - TRAIL_FADE_CALM) * t))


def _lerp_stops(stops: tuple[tuple[int, int, int], ...], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t)) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    f = t - i
    a, b = stops[i], stops[i + 1]
    return tuple(int(round(a[c] + (b[c] - a[c]) * f)) for c in range(3))


def _rotated(points: list[tuple[float, float]], angle: float, scale: float, center: float) -> list[tuple[float, float]]:
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [(center + (x * cos_a - y * sin_a) * scale, center + (x * sin_a + y * cos_a) * scale) for x, y in points]


def _fish_polygon() -> list[tuple[float, float]]:
    lower = [(x, -y) for x, y in reversed(FISH_OUTLINE[1:-1])]
    return FISH_OUTLINE + lower


def _core_polygon(steps: int = 20) -> list[tuple[float, float]]:
    return [
        (CORE_CENTER + CORE_HALF_LENGTH * math.cos(a), CORE_HALF_WIDTH * math.sin(a))
        for a in (math.tau * i / steps for i in range(steps))
    ]


def _mask(points: list[tuple[float, float]], angle: float, unit: float, side: int, render_side: int) -> pygame.Surface:
    """White-on-black anti-aliased coverage mask: drawn at render_side, smooth-scaled to side."""
    k = render_side / side
    surface = pygame.Surface((render_side, render_side))
    pygame.draw.polygon(surface, (255, 255, 255), _rotated(points, angle, unit * k, render_side / 2))
    return pygame.transform.smoothscale(surface, (side, side))


def _soft(mask: pygame.Surface, factor: int = 4) -> pygame.Surface:
    """Cheap blur: average down by `factor`, then bilinear back up."""
    side = mask.get_width()
    small = pygame.transform.smoothscale(mask, (max(2, side // factor), max(2, side // factor)))
    return pygame.transform.smoothscale(small, (side, side))


class FishSprites:
    """Pre-rendered fish for one view scale: [size_bin][heat_level][heading] -> Surface."""

    def __init__(self, scale: float):
        fish = _fish_polygon()
        core = _core_polygon()
        halo = [(x * HALO_GROWTH, y * HALO_GROWTH * 1.4) for x, y in fish]
        body_colors = [_lerp_stops(BODY_STOPS, (h + 0.5) / HEAT_LEVELS) for h in range(HEAT_LEVELS)]
        core_colors = [_lerp_stops(CORE_STOPS, (h + 0.5) / HEAT_LEVELS) for h in range(HEAT_LEVELS)]
        halo_colors = [_lerp_stops(HALO_STOPS, (h + 0.5) / HEAT_LEVELS) for h in range(HEAT_LEVELS)]

        self.half: list[int] = []
        self.body: list[list[list[pygame.Surface]]] = []
        self.halo: list[list[list[pygame.Surface]]] = []
        for size in SIZE_BINS:
            unit = size * scale
            half = int(math.ceil(1.85 * HALO_GROWTH * unit)) + 2
            side = 2 * half
            self.half.append(half)
            body_by_heat = [[] for _ in range(HEAT_LEVELS)]
            halo_by_heat = [[] for _ in range(HEAT_LEVELS)]
            for k in range(HEADINGS):
                angle = math.tau * k / HEADINGS
                body_mask = _mask(fish, angle, unit, side, side * SUPERSAMPLE)
                core_mask = _mask(core, angle, unit, side, side * SUPERSAMPLE)
                halo_mask = _soft(_mask(halo, angle, unit, side, side * 2))
                for h in range(HEAT_LEVELS):
                    body = body_mask.copy()
                    body.fill(body_colors[h], special_flags=pygame.BLEND_RGB_MULT)
                    tinted_core = core_mask.copy()
                    tinted_core.fill(core_colors[h], special_flags=pygame.BLEND_RGB_MULT)
                    body.blit(tinted_core, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                    glow = halo_mask.copy()
                    glow.fill(halo_colors[h], special_flags=pygame.BLEND_RGB_MULT)
                    body_by_heat[h].append(body.convert())
                    halo_by_heat[h].append(glow.convert())
            self.body.append(body_by_heat)
            self.halo.append(halo_by_heat)


class ThermalRenderer:
    """Dark "thermal" look, drawn directly at canvas resolution through the view.

    Modes: "art" (no text, for recording) and "data" (same picture + HUD), toggled with H.
    """

    MODES = ("art", "data")

    def __init__(self, font: pygame.font.Font, mode: str = "art", trails: bool = True):
        self.font = font
        self.mode = mode
        self.trails = trails
        self._sprite_cache: dict[float, FishSprites] = {}
        # Persistent picture of the world area: faded each frame instead of cleared (trails).
        # Only fish go in here; rings and HUD are drawn on the canvas so they never smear.
        self._scene: pygame.Surface | None = None
        self._fade_surface: pygame.Surface | None = None
        self._fade_value = -1
        self._floor_surface: pygame.Surface | None = None

    def handle_key(self, key: int) -> bool:
        if key == pygame.K_h:
            self.mode = "data" if self.mode == "art" else "art"
            return True
        if key == pygame.K_t:
            self.trails = not self.trails
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
        scale = view.scale
        ox, oy = view.rect.topleft
        scene = self._scene
        if scene is None or scene.get_size() != view.rect.size:
            scene = self._scene = pygame.Surface(view.rect.size).convert()
            scene.fill(THERMAL_BACKGROUND)
            # Fade via blits from constant surfaces: blit blending has SIMD paths, while
            # Surface.fill(special_flags=...) is scalar (measured ~0.2 ms vs ~11 ms).
            self._fade_surface = scene.copy()
            self._fade_value = -1
            self._floor_surface = scene.copy()
            self._floor_surface.fill((TRAIL_FLOOR,) * 3)
        with _stage("thermal.trails"):
            if self.trails:
                fade = trail_fade(descriptors.get("energy", 0.0))
                if fade != self._fade_value:
                    self._fade_surface.fill((fade, fade, fade))
                    self._fade_value = fade
                scene.blit(self._fade_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                scene.blit(self._floor_surface, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            else:
                scene.fill(THERMAL_BACKGROUND)
        canvas.fill(THERMAL_BACKGROUND)
        canvas.set_clip(view.rect)
        with _stage("thermal.fish"):
            halos, bodies, scene_bodies = self._fish_blits(flock, self._sprites_for(scale), scale, ox, oy)
            canvas.blits(halos, doreturn=False)
        with _stage("thermal.compose"):
            # The scene holds only the past (faded). MAX keeps every pixel at
            # max(halo glow, trail, body): trails never stack on top of the glow.
            canvas.blit(scene, view.rect.topleft, special_flags=pygame.BLEND_RGB_MAX)
        with _stage("thermal.fish"):
            canvas.blits(bodies, doreturn=False)
            if self.trails:
                # Trails hold bodies only, with MAX: however long the trail, a pixel never gets
                # brighter than one sprite (additive halos in a fading buffer would pile up).
                scene.blits(scene_bodies, doreturn=False)
        with _stage("thermal.events"):
            if attractor is not None:
                pygame.draw.circle(canvas, (80, 255, 150), (ox + attractor.x * scale, oy + attractor.y * scale), 18 * scale, 2)
            if repeller is not None:
                pygame.draw.circle(canvas, (255, 80, 90), (ox + repeller.x * scale, oy + repeller.y * scale), 34 * scale, 2)
        canvas.set_clip(None)
        if self.mode == "data":
            draw_hud(canvas, self.font, controls, descriptors, origin=view.rect.topleft)

    def _sprites_for(self, scale: float) -> FishSprites:
        key = round(scale, 4)
        sprites = self._sprite_cache.get(key)
        if sprites is None:
            sprites = FishSprites(scale)
            self._sprite_cache[key] = sprites
        return sprites

    @staticmethod
    def _fish_blits(
        flock: list[Boid],
        sprites: FishSprites,
        scale: float,
        ox: int,
        oy: int,
    ) -> tuple[list, list, list]:
        """Blit lists: halos (additive, canvas), bodies (MAX, canvas), bodies (MAX, scene).

        Halos go first so dense areas glow; bodies use MAX so overlapping fish never sum.
        """
        halos = []
        bodies = []
        scene_bodies = []
        for boid in flock:
            velocity = boid.velocity
            heat = min(1.0, velocity.length() / boid.max_speed + 0.6 * boid.flash)
            heat_i = min(HEAT_LEVELS - 1, int(heat * HEAT_LEVELS))
            heading_i = round(math.atan2(velocity.y, velocity.x) * HEADINGS / math.tau) % HEADINGS
            size_i = 0 if boid.size < SIZE_EDGES[0] else (1 if boid.size < SIZE_EDGES[1] else 2)
            half = sprites.half[size_i]
            body = sprites.body[size_i][heat_i][heading_i]
            x = boid.position.x * scale - half
            y = boid.position.y * scale - half
            halos.append((sprites.halo[size_i][heat_i][heading_i], (ox + x, oy + y), None, pygame.BLEND_RGB_ADD))
            bodies.append((body, (ox + x, oy + y), None, pygame.BLEND_RGB_MAX))
            scene_bodies.append((body, (x, y), None, pygame.BLEND_RGB_MAX))
        return halos, bodies, scene_bodies
