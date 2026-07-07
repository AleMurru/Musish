"""Simulazione boids vettorizzata (numpy) con controlli-ecosistema.

Il mondo e' un "acquario" a bordi fissi. La classe `World` contiene i controlli
live (food, predator, turbulence, density) che il musicista manipolera'.
`Flock.update()` avanza la simulazione e restituisce gli eventi discreti del
frame (dart, turn, collision) usati per il mapping diretto.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

from . import config as C


@dataclass
class World:
    """Controlli live dell'ecosistema. Tutti 0..1 tranne le posizioni (px)."""
    food: float = 0.0            # attrazione verso food_pos (aggregazione -> consonanza)
    predator: float = 0.0        # repulsione da predator_pos (fuga -> dissonanza)
    turbulence: float = 0.15     # rumore sul movimento
    density: float = 0.3         # densita' musicale (non influenza la fisica)
    food_pos: np.ndarray = field(default_factory=lambda: np.array([C.WIDTH * 0.5, C.HEIGHT * 0.5]))
    predator_pos: np.ndarray = field(default_factory=lambda: np.array([C.WIDTH * 0.5, C.HEIGHT * 0.5]))

    def clamp(self):
        self.food = float(np.clip(self.food, 0.0, 1.0))
        self.predator = float(np.clip(self.predator, 0.0, 1.0))
        self.turbulence = float(np.clip(self.turbulence, 0.0, 1.0))
        self.density = float(np.clip(self.density, 0.0, 1.0))


def _limit(vecs: np.ndarray, max_mag: float) -> np.ndarray:
    """Clampa la magnitudine di ogni riga (N,2) a max_mag."""
    mag = np.linalg.norm(vecs, axis=1, keepdims=True)
    scale = np.where(mag > max_mag, max_mag / np.maximum(mag, 1e-9), 1.0)
    return vecs * scale


class Flock:
    def __init__(self, n=C.N_FISH, bounds=C.BOUNDS, seed=0):
        self.bounds = np.array(bounds, dtype=float)
        self.rng = np.random.default_rng(seed)
        self.n = n
        self.pos = self.rng.uniform([0, 0], bounds, size=(n, 2))
        ang = self.rng.uniform(0, 2 * np.pi, n)
        self.vel = np.column_stack([np.cos(ang), np.sin(ang)]) * (C.MAX_SPEED * 0.5)
        self.size = self.rng.uniform(0.6, 1.4, n)          # scala visiva + peso musicale
        # cooldown per-pesce per gli eventi discreti (in secondi rimanenti)
        self._cd_dart = np.zeros(n)
        self._cd_turn = np.zeros(n)
        self._coll_cd = 0.0
        # cooldown globali (limitano la raffica complessiva di eventi)
        self._dart_gcd = 0.0
        self._turn_gcd = 0.0

    # -- API ------------------------------------------------------------------
    def update(self, world: World, dt: float) -> list[tuple]:
        """Avanza di un frame. Ritorna lista di eventi discreti.

        Ogni evento e' una tupla: (kind, *args) dove kind in {"dart","turn","collision"}.
        """
        p, v = self.pos, self.vel
        n = self.n

        # --- distanze pairwise (N,N) ---
        diff = p[:, None, :] - p[None, :, :]         # (N,N,2) da j verso i
        dist = np.linalg.norm(diff, axis=2)          # (N,N)
        np.fill_diagonal(dist, np.inf)

        neigh = dist < C.PERCEPTION                   # vicini in percezione
        sep_mask = dist < C.SEPARATION_R              # vicini troppo vicini

        acc = np.zeros((n, 2))

        # Separation: allontanati dai vicini vicini, pesato per 1/dist
        with np.errstate(divide="ignore", invalid="ignore"):
            inv = np.where(sep_mask, 1.0 / np.maximum(dist, 1e-6), 0.0)  # (N,N)
        sep = np.einsum("ij,ijk->ik", inv, diff)      # somma pesata delle direzioni di fuga
        acc += C.W_SEPARATION * _limit(sep, C.MAX_FORCE)

        # Alignment: allineati alla velocita' media dei vicini
        cnt = neigh.sum(axis=1, keepdims=True)
        safe = np.maximum(cnt, 1)
        mean_vel = (neigh @ v) / safe
        align = np.where(cnt > 0, mean_vel - v, 0.0)
        acc += C.W_ALIGNMENT * _limit(align, C.MAX_FORCE)

        # Cohesion: muoviti verso il centro locale dei vicini
        mean_pos = (neigh @ p) / safe
        coh = np.where(cnt > 0, mean_pos - p, 0.0)
        acc += C.W_COHESION * _limit(coh, C.MAX_FORCE)

        # Food: attrazione verso food_pos (aggregazione)
        if world.food > 0:
            to_food = world.food_pos[None, :] - p
            acc += (2.2 * world.food) * _limit(to_food, C.MAX_FORCE)

        # Predator: repulsione forte da predator_pos (fuga)
        if world.predator > 0:
            from_pred = p - world.predator_pos[None, :]
            d_pred = np.linalg.norm(from_pred, axis=1, keepdims=True)
            influence = np.clip(1.0 - d_pred / 260.0, 0.0, 1.0)  # raggio di paura
            flee = np.where(d_pred > 1e-6, from_pred / np.maximum(d_pred, 1e-6), 0.0)
            acc += (5.0 * world.predator) * flee * influence

        # Border steering: spingi verso l'interno vicino ai bordi
        acc += C.W_BORDER * self._border_force(p)

        # Turbulence: rumore
        if world.turbulence > 0:
            acc += (world.turbulence * C.MAX_FORCE * 3.0) * self.rng.uniform(-1, 1, (n, 2))

        # --- integrazione ---
        prev_v = v.copy()
        v = _limit(v + acc, C.MAX_SPEED)
        p = p + v * (dt * C.FPS)                       # dt*FPS ~ 1 a 60fps
        p = np.clip(p, [0, 0], self.bounds)            # hard clamp di sicurezza
        self.pos, self.vel = p, v

        return self._detect_events(prev_v, v, dist, dt)

    # -- interni --------------------------------------------------------------
    def _border_force(self, p):
        f = np.zeros_like(p)
        m = C.BORDER_MARGIN
        f[:, 0] += np.where(p[:, 0] < m, (m - p[:, 0]) / m, 0.0)
        f[:, 0] -= np.where(p[:, 0] > self.bounds[0] - m,
                            (p[:, 0] - (self.bounds[0] - m)) / m, 0.0)
        f[:, 1] += np.where(p[:, 1] < m, (m - p[:, 1]) / m, 0.0)
        f[:, 1] -= np.where(p[:, 1] > self.bounds[1] - m,
                            (p[:, 1] - (self.bounds[1] - m)) / m, 0.0)
        return f

    def _detect_events(self, prev_v, v, dist, dt):
        events = []
        self._cd_dart = np.maximum(0.0, self._cd_dart - dt)
        self._cd_turn = np.maximum(0.0, self._cd_turn - dt)
        self._coll_cd = max(0.0, self._coll_cd - dt)
        self._dart_gcd = max(0.0, self._dart_gcd - dt)
        self._turn_gcd = max(0.0, self._turn_gcd - dt)

        speed = np.linalg.norm(v, axis=1)

        # DART: outlier di velocita' (un pesce che scatta fuori dal branco).
        # Soglia relativa alla distribuzione del branco -> resta raro anche a
        # branco veloce. Emetto solo il piu' veloce per frame, con cooldown globale.
        if self._dart_gcd <= 0:
            thr = max(speed.mean() + C.DART_SIGMA * speed.std(),
                      C.DART_SPEED_FLOOR * C.MAX_SPEED)
            cand = (speed > thr) & (self._cd_dart <= 0)
            idx = np.nonzero(cand)[0]
            if idx.size:
                i = idx[np.argmax(speed[idx])]        # solo il piu' estremo
                events.append(("dart", int(i),
                               float(speed[i] / C.MAX_SPEED),
                               float(self.pos[i, 1] / self.bounds[1])))
                self._cd_dart[i] = C.DART_COOLDOWN
                self._dart_gcd = C.DART_GLOBAL_COOLDOWN

        # TURN: inversione netta di direzione, solo per pesci non lenti.
        if self._turn_gcd <= 0:
            pmag = np.linalg.norm(prev_v, axis=1)
            cmag = speed
            cos = np.einsum("ij,ij->i", prev_v, v) / np.maximum(pmag * cmag, 1e-9)
            cand = (cos < C.TURN_DOT) & (cmag > C.TURN_SPEED_FLOOR * C.MAX_SPEED) \
                & (self._cd_turn <= 0)
            idx = np.nonzero(cand)[0]
            if idx.size:
                i = idx[np.argmin(cos[idx])]          # l'inversione piu' netta
                events.append(("turn", int(i),
                               float(self.pos[i, 0] / self.bounds[0]),
                               float(self.pos[i, 1] / self.bounds[1])))
                self._cd_turn[i] = C.TURN_COOLDOWN
                self._turn_gcd = C.TURN_GLOBAL_COOLDOWN

        # COLLISION: coppia piu' vicina di COLLISION_R (una per frame, rate-limited)
        if self._coll_cd <= 0:
            iu = np.triu_indices(self.n, k=1)
            close = dist[iu] < C.COLLISION_R
            if np.any(close):
                k = np.argmin(dist[iu])
                i, j = iu[0][k], iu[1][k]
                mx = (self.pos[i, 0] + self.pos[j, 0]) * 0.5 / self.bounds[0]
                my = (self.pos[i, 1] + self.pos[j, 1]) * 0.5 / self.bounds[1]
                strength = float(np.clip((C.COLLISION_R - dist[i, j]) / C.COLLISION_R, 0, 1))
                events.append(("collision", float(mx), float(my), strength))
                self._coll_cd = C.COLLISION_COOLDOWN

        return events
