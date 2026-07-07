from __future__ import annotations

import random
from dataclasses import dataclass, field

from .controls import RuntimeControls

LAYERS = ["drone", "bass", "lead", "perc", "granular", "noise"]
SECTIONS = ["intro", "growth", "dense", "chaos", "release", "outro"]


class WeightedMarkov:
    def __init__(self, transitions: dict):
        self.transitions = transitions
        self.state = next(iter(transitions.keys()))

    def next(self, temperature: float = 1.0) -> object:
        choices = self.transitions.get(self.state) or self.transitions[next(iter(self.transitions.keys()))]
        temperature = max(0.05, temperature)
        states = [state for state, _weight in choices]
        weights = [max(0.0001, float(weight)) ** (1.0 / temperature) for _state, weight in choices]
        self.state = random.choices(states, weights=weights, k=1)[0]
        return self.state


@dataclass
class MusicEvent:
    event_id: int
    event_type: str
    degree: int = 0
    octave: int = 0
    duration_beats: float = 1.0
    velocity: int = 64
    layer_id: int = 0
    chord_degree: int = 0
    section_id: int = 0

    def osc_payload(self) -> list:
        return [
            self.event_id,
            1 if self.event_type == "note" else 0,
            self.degree,
            self.octave,
            self.duration_beats,
            self.velocity,
            self.layer_id,
            self.chord_degree,
            self.section_id,
        ]


@dataclass
class SymbolicGenerator:
    event_id: int = 0
    pitch_chain: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
        0: [(0, 0.20), (1, 0.12), (2, 0.35), (4, 0.25), (5, 0.08)],
        1: [(0, 0.25), (2, 0.30), (3, 0.20), (4, 0.15), (6, 0.10)],
        2: [(0, 0.30), (1, 0.15), (3, 0.20), (4, 0.25), (5, 0.10)],
        3: [(1, 0.18), (2, 0.24), (4, 0.28), (5, 0.20), (6, 0.10)],
        4: [(0, 0.28), (2, 0.25), (3, 0.18), (5, 0.16), (6, 0.13)],
        5: [(0, 0.18), (2, 0.22), (3, 0.20), (4, 0.30), (6, 0.10)],
        6: [(0, 0.35), (1, 0.15), (2, 0.20), (4, 0.20), (5, 0.10)],
    }))
    rhythm_chain: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
        "half": [("half", 0.20), ("quarter", 0.40), ("eighth", 0.20), ("rest", 0.20)],
        "quarter": [("half", 0.16), ("quarter", 0.34), ("eighth", 0.34), ("sixteenth", 0.06), ("rest", 0.10)],
        "eighth": [("quarter", 0.24), ("eighth", 0.42), ("sixteenth", 0.22), ("rest", 0.12)],
        "sixteenth": [("eighth", 0.40), ("sixteenth", 0.42), ("quarter", 0.08), ("rest", 0.10)],
        "rest": [("half", 0.20), ("quarter", 0.35), ("eighth", 0.25), ("rest", 0.20)],
    }))
    chord_index: int = 0

    def generate(self, descriptors: dict[str, float], controls: RuntimeControls) -> MusicEvent:
        self.event_id += 1

        speed = descriptors.get("mean_speed", 0.0)
        energy = descriptors.get("energy", 0.0)
        spread = descriptors.get("spread", 0.0)
        density = descriptors.get("density", 0.0)
        coherence = descriptors.get("direction_coherence", 0.0)

        temperature = 0.25 + controls.density_fader * 0.9 + speed * 0.35
        degree = int(self.pitch_chain.next(temperature=temperature))
        rhythm_state = str(self.rhythm_chain.next(temperature=temperature + (1.0 - coherence) * 0.25))

        duration_map = {
            "sixteenth": 0.25,
            "eighth": 0.5,
            "quarter": 1.0,
            "half": 2.0,
            "rest": 1.0,
        }
        duration_beats = duration_map[rhythm_state]

        # Direct density control: low fader creates more silence, high fader lets events pass.
        rest_probability = max(0.05, 0.62 - controls.density_fader * 0.52 - speed * 0.22)
        is_rest = rhythm_state == "rest" or random.random() < rest_probability * 0.28

        octave_span = 1 + int(spread * 3)
        octave = random.randint(-octave_span // 2, octave_span // 2)
        velocity = int(max(20, min(127, 35 + energy * 78 + random.uniform(-8, 10))))

        chord_progression = [0, 5, 3, 4]  # relative scale degrees: i - VI - iv - V-ish in minor context.
        if self.event_id % 16 == 0:
            self.chord_index = (self.chord_index + 1) % len(chord_progression)
        chord_degree = chord_progression[self.chord_index]

        if controls.section_name == "intro":
            layer_id = random.choices([0, 1, 2], weights=[0.60, 0.25, 0.15], k=1)[0]
        elif controls.section_name == "chaos":
            layer_id = random.choices([2, 3, 4, 5], weights=[0.25, 0.30, 0.25, 0.20], k=1)[0]
        elif controls.density_fader > 0.75:
            layer_id = random.choices([2, 3, 4, 5], weights=[0.30, 0.32, 0.25, 0.13], k=1)[0]
        elif controls.density_fader > 0.42:
            layer_id = random.choices([1, 2, 3, 4], weights=[0.22, 0.38, 0.25, 0.15], k=1)[0]
        else:
            layer_id = random.choices([0, 1, 2], weights=[0.48, 0.32, 0.20], k=1)[0]

        if density > 0.72 and controls.section_name in {"dense", "chaos"}:
            # Compact swarm: bias toward harmonically strong notes.
            degree = random.choices([0, 2, 4, degree], weights=[0.30, 0.25, 0.30, 0.15], k=1)[0]

        return MusicEvent(
            event_id=self.event_id,
            event_type="rest" if is_rest else "note",
            degree=degree,
            octave=octave,
            duration_beats=duration_beats,
            velocity=velocity,
            layer_id=layer_id,
            chord_degree=chord_degree,
            section_id=controls.section_id,
        )
