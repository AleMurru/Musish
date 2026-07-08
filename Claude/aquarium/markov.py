"""Generatore musicale simbolico GERARCHICO per la versione Claude.

Differenza chiave vs le catene indipendenti: qui c'e' un motore armonico.
- una catena LENTA sceglie l'accordo corrente (progressione in tonalita' minore);
- una catena VELOCE sceglie il grado melodico, poi lo BIASA verso le note
  dell'accordo corrente (consonanza) tanto piu' quanto il branco e' ordinato.

Cosi' la melodia non e' scorrelata dall'armonia e non resta piatta su scala fissa.
Genera GRADI DI SCALA (0..6), non note assolute: il musicista sceglie scala/tonalita' in Max.

I descrittori del branco condizionano temperatura, ritmo, velocity, ottava, dissonanza;
il controllo `world.density` regola quanti eventi al secondo e la probabilita' di pausa.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field

from . import config as C


class WeightedMarkov:
    """Catena di Markov pesata con 'temperatura' (appiattisce/accentua le probabilita')."""

    def __init__(self, transitions: dict):
        self.transitions = transitions
        self.state = next(iter(transitions))

    def next(self, temperature: float = 1.0):
        choices = self.transitions.get(self.state) or next(iter(self.transitions.values()))
        temperature = max(0.05, temperature)
        states = [s for s, _ in choices]
        weights = [max(1e-4, float(w)) ** (1.0 / temperature) for _, w in choices]
        self.state = random.choices(states, weights=weights, k=1)[0]
        return self.state


@dataclass
class MusicEvent:
    event_id: int
    kind: str            # "note" | "rest"
    degree: int = 0      # grado di scala 0..6
    octave: int = 0
    duration_beats: float = 1.0
    velocity: int = 64
    chord_root: int = 0  # grado di scala su cui e' costruito l'accordo corrente

    def note_payload(self):
        return [self.event_id, self.degree, self.octave,
                self.duration_beats, self.velocity, self.chord_root]

    def rest_payload(self):
        return [self.event_id, self.duration_beats]


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


class HierarchicalGenerator:
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
        self.event_id = 0
        self.chord_root = 0
        self.events_since_chord = 0
        self._acc = 0.0
        self.last_chord = -1

        # Catena melodica: gradi 0..6 (i pesi favoriscono passi di grado/terza)
        self.pitch = WeightedMarkov({
            0: [(0, .18), (1, .12), (2, .32), (4, .26), (5, .10)],
            1: [(0, .26), (2, .30), (3, .20), (4, .14), (6, .10)],
            2: [(0, .30), (1, .14), (3, .22), (4, .24), (5, .10)],
            3: [(1, .18), (2, .26), (4, .28), (5, .18), (6, .10)],
            4: [(0, .30), (2, .24), (3, .16), (5, .16), (6, .14)],
            5: [(0, .20), (2, .22), (3, .20), (4, .28), (6, .10)],
            6: [(0, .38), (1, .14), (2, .20), (4, .18), (5, .10)],
        })
        # Catena ritmica
        self.rhythm = WeightedMarkov({
            "half":     [("half", .18), ("quarter", .42), ("eighth", .20), ("rest", .20)],
            "quarter":  [("half", .16), ("quarter", .34), ("eighth", .34), ("sixteenth", .06), ("rest", .10)],
            "eighth":   [("quarter", .24), ("eighth", .42), ("sixteenth", .22), ("rest", .12)],
            "sixteenth":[("eighth", .40), ("sixteenth", .42), ("quarter", .08), ("rest", .10)],
            "rest":     [("half", .20), ("quarter", .35), ("eighth", .25), ("rest", .20)],
        })
        # Catena LENTA degli accordi (radici come gradi di scala, contesto minore: i-VI-iv-V-ish)
        self.chords = WeightedMarkov({
            0: [(5, .34), (3, .30), (4, .24), (0, .12)],   # i -> VI / iv / V
            5: [(3, .34), (4, .30), (0, .24), (5, .12)],   # VI -> iv / V / i
            3: [(4, .40), (0, .28), (5, .20), (3, .12)],   # iv -> V / i
            4: [(0, .48), (5, .22), (3, .18), (4, .12)],   # V -> i (risoluzione)
        })

    @staticmethod
    def _chord_tones(root: int) -> set[int]:
        # triade diatonica: fondamentale, terza, quinta (per gradi di scala)
        return {root % 7, (root + 2) % 7, (root + 4) % 7}

    def tick(self, dt: float, desc: dict, world) -> tuple[list[MusicEvent], int | None]:
        """Avanza il tempo di dt. Ritorna (eventi_da_emettere, nuovo_accordo|None)."""
        speed = desc.get("mean_speed", 0.0)
        eps = 0.4 + world.density * 5.5 + speed * 2.0   # eventi al secondo
        interval = max(0.08, 1.0 / eps)

        self._acc += dt
        events: list[MusicEvent] = []
        guard = 0
        while self._acc >= interval and guard < 16:
            self._acc -= interval
            events.append(self._generate(desc, world))
            guard += 1

        chord_change = self.chord_root if self.chord_root != self.last_chord else None
        self.last_chord = self.chord_root
        return events, chord_change

    def _generate(self, desc: dict, world) -> MusicEvent:
        self.event_id += 1
        speed = desc.get("mean_speed", 0.0)
        energy = desc.get("energy", 0.0)
        spread = desc.get("spread", 0.0)
        density = desc.get("density", 0.0)
        coherence = desc.get("coherence", 0.0)

        temperature = 0.25 + world.density * 0.9 + speed * 0.35 + (1.0 - coherence) * 0.2

        # --- catena lenta: cambio accordo ogni CHORD_EVERY_EVENTS eventi ---
        self.events_since_chord += 1
        if self.events_since_chord >= C.CHORD_EVERY_EVENTS:
            self.chord_root = int(self.chords.next(temperature=0.6))
            self.events_since_chord = 0

        # --- ritmo / pausa ---
        rhythm = self.rhythm.next(temperature=temperature)
        dur = C.DURATIONS[rhythm]
        rest_prob = max(0.05, 0.60 - world.density * 0.50 - speed * 0.20)
        if rhythm == "rest" or self.rng.random() < rest_prob * 0.3:
            return MusicEvent(self.event_id, "rest", duration_beats=dur, chord_root=self.chord_root)

        # --- melodia condizionata sull'accordo ---
        degree = int(self.pitch.next(temperature=temperature))
        tones = self._chord_tones(self.chord_root)
        # branco compatto/disordinato -> piu' dissonanza ammessa; ordinato -> aggancia le note dell'accordo
        consonance = _clamp(1.0 - density * 0.5, 0.0, 1.0)
        if self.rng.random() < 0.55 * consonance:
            degree = min(tones, key=lambda t: min(abs(t - degree), 7 - abs(t - degree)))

        octave = self.rng.randint(-1, 1) + int(round((spread - 0.5) * 2))
        octave = int(_clamp(octave, -3, 3))
        velocity = int(_clamp(35 + energy * 80 + self.rng.uniform(-8, 8), 20, 127))

        return MusicEvent(self.event_id, "note", degree, octave, dur, velocity, self.chord_root)
