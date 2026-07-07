"""Estrazione descrittori collettivi/geometrici dal branco, normalizzati 0..1.

I descrittori sono il "ponte" verso la musica. Sono smussati con EMA per togliere
il jitter dei boids prima di essere mappati o inviati via OSC.
"""
from __future__ import annotations
import numpy as np

from . import config as C
from .boids import Flock, World


class DescriptorExtractor:
    def __init__(self, bounds=C.BOUNDS, alpha=C.EMA_ALPHA, nominal_max_fish=200):
        self.bounds = np.array(bounds, dtype=float)
        self.diag = float(np.linalg.norm(self.bounds))
        self.alpha = alpha
        self.nominal_max_fish = nominal_max_fish
        self._smoothed: dict[str, float] = {}

    def compute(self, flock: Flock, world: World) -> dict[str, float]:
        p, v = flock.pos, flock.vel
        n = flock.n
        speed = np.linalg.norm(v, axis=1)

        center = p.mean(axis=0)
        # dispersione: deviazione standard delle distanze dal centro, / mezza diagonale
        spread = float(np.linalg.norm(p - center, axis=1).std() / (0.5 * self.diag))

        # nearest-neighbor medio (compattezza)
        if n > 1:
            d = np.linalg.norm(p[:, None, :] - p[None, :, :], axis=2)
            np.fill_diagonal(d, np.inf)
            nearest = float(d.min(axis=1).mean() / (0.25 * self.diag))
        else:
            nearest = 1.0

        # coherence = order parameter (magnitudine della media dei versori velocita')
        with np.errstate(invalid="ignore"):
            units = v / np.maximum(speed[:, None], 1e-9)
        coherence = float(np.linalg.norm(units.mean(axis=0)))

        raw = {
            "fish_count": n / self.nominal_max_fish,
            "mean_speed": speed.mean() / C.MAX_SPEED,
            "energy":     speed.sum() / (n * C.MAX_SPEED),
            "center_x":   center[0] / self.bounds[0],
            "center_y":   center[1] / self.bounds[1],
            "spread":     spread,
            "density":    1.0 - np.clip(nearest, 0, 1),   # vicini vicini = densita' alta
            "nearest":    np.clip(nearest, 0, 1),
            "coherence":  coherence,
            "turbulence": world.turbulence,
        }
        raw = {k: float(np.clip(val, 0.0, 1.0)) for k, val in raw.items()}
        return self._ema(raw)

    def _ema(self, raw: dict[str, float]) -> dict[str, float]:
        a = self.alpha
        for k, val in raw.items():
            prev = self._smoothed.get(k, val)
            self._smoothed[k] = a * val + (1 - a) * prev
        return dict(self._smoothed)
