from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal

from .config import BPM, ROOT_MIDI, SCALE_INTERVALS
from .controls import RuntimeControls, clamp01
from .markov import WeightedMarkov

VoiceName = Literal["bass", "lead", "keys"]
HitVoice = Literal["grain", "glitch", "noise"]
ClockKind = Literal["step", "beat", "bar"]

VOICE_LAYER_ID = {
    "bass": 1,
    "lead": 2,
    "keys": 2,
}


@dataclass
class BeatClock:
    """Simple musical clock quantized to a 16th-note grid."""

    bpm: float = BPM
    steps_per_beat: int = 4
    accumulator_s: float = 0.0
    step: int = 0

    @property
    def step_duration_s(self) -> float:
        return 60.0 / self.bpm / self.steps_per_beat

    def tick(self, dt_s: float) -> list[int]:
        """Return all grid steps that fire during this frame."""
        self.accumulator_s += max(0.0, dt_s)
        fired: list[int] = []
        while self.accumulator_s >= self.step_duration_s:
            self.accumulator_s -= self.step_duration_s
            fired.append(self.step)
            self.step += 1
        return fired


@dataclass
class ClockEvent:
    kind: ClockKind
    index: int
    step: int
    step_in_bar: int
    beat_in_bar: int
    bar: int
    bpm: float = BPM


@dataclass
class ChordEvent:
    root: int
    third: int
    fifth: int
    chord_degree: int
    scene_id: int
    bar: int


@dataclass
class NoteEventV2:
    event_id: int
    voice: VoiceName
    midi_note: int
    velocity: int
    duration_ms: int
    degree: int
    octave: int
    layer_id: int
    scene_id: int
    chord_degree: int


@dataclass
class HitEvent:
    event_id: int
    voice: HitVoice
    sample_id: int
    velocity: int
    duration_ms: int
    scene_id: int


MarkovV2Event = ClockEvent | ChordEvent | NoteEventV2 | HitEvent


def clamp_midi(value: int) -> int:
    return max(0, min(127, int(value)))


def degree_to_midi(degree: int, octave: int = 0, root_midi: int = ROOT_MIDI) -> int:
    """Convert a scale degree to MIDI without destroying octave information.

    Unlike the old v1 conversion, degrees outside 0..6 move through octaves
    instead of wrapping back into the same octave.
    """
    octave_offset, scale_index = divmod(int(degree), len(SCALE_INTERVALS))
    return clamp_midi(root_midi + SCALE_INTERVALS[scale_index] + 12 * (octave + octave_offset))


def chord_notes(chord_degree: int, octave: int = 0) -> tuple[int, int, int]:
    """Diatonic triad: root + third + fifth above chord_degree."""
    return (
        degree_to_midi(chord_degree, octave),
        degree_to_midi(chord_degree + 2, octave),
        degree_to_midi(chord_degree + 4, octave),
    )


@dataclass
class MarkovV2Generator:
    """Quantized symbolic generator for Max.

    The generator emits a small, practical set of musical events:
    clock, chord, note and hit. Descriptors and performance controls shape
    probability, velocity, range and chaos.
    """

    event_id: int = 0
    chord_degree: int = 0
    lead_pitch: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
        0: [(0, 0.25), (1, 0.08), (2, 0.30), (4, 0.25), (5, 0.12)],
        1: [(0, 0.20), (2, 0.32), (3, 0.20), (4, 0.18), (6, 0.10)],
        2: [(0, 0.22), (1, 0.12), (3, 0.23), (4, 0.30), (5, 0.13)],
        3: [(1, 0.16), (2, 0.24), (4, 0.30), (5, 0.18), (6, 0.12)],
        4: [(0, 0.32), (2, 0.24), (3, 0.14), (5, 0.16), (6, 0.14)],
        5: [(0, 0.16), (2, 0.24), (3, 0.20), (4, 0.30), (6, 0.10)],
        6: [(0, 0.38), (1, 0.14), (2, 0.18), (4, 0.22), (5, 0.08)],
    }))
    rhythm_steps: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
        1: [(1, 0.55), (2, 0.30), (4, 0.15)],
        2: [(1, 0.30), (2, 0.45), (4, 0.25)],
        4: [(1, 0.22), (2, 0.38), (4, 0.40)],
    }))
    chord_chain: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
        0: [(0, 0.08), (5, 0.36), (3, 0.24), (4, 0.32)],
        5: [(3, 0.40), (4, 0.28), (0, 0.24), (5, 0.08)],
        3: [(4, 0.46), (0, 0.28), (5, 0.18), (3, 0.08)],
        4: [(0, 0.55), (5, 0.20), (3, 0.15), (4, 0.10)],
    }))
    bass_degrees: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
        0: [(0, 0.50), (4, 0.28), (7, 0.14), (2, 0.08)],
        4: [(0, 0.45), (4, 0.25), (7, 0.20), (2, 0.10)],
        7: [(0, 0.52), (4, 0.26), (7, 0.12), (2, 0.10)],
        2: [(0, 0.42), (4, 0.26), (2, 0.18), (7, 0.14)],
    }))
    hit_samples: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
        0: [(0, 0.35), (1, 0.28), (2, 0.20), (3, 0.17)],
        1: [(1, 0.28), (2, 0.30), (3, 0.22), (0, 0.20)],
        2: [(2, 0.30), (3, 0.30), (0, 0.22), (1, 0.18)],
        3: [(3, 0.30), (0, 0.32), (1, 0.20), (2, 0.18)],
    }))

    def generate_step(self, step: int, descriptors: dict[str, float], controls: RuntimeControls) -> list[MarkovV2Event]:
        step_in_bar = step % 16
        beat_in_bar = step_in_bar // 4
        bar = step // 16

        events: list[MarkovV2Event] = [
            ClockEvent("step", step, step, step_in_bar, beat_in_bar, bar, BPM)
        ]
        if step_in_bar % 4 == 0:
            events.append(ClockEvent("beat", step // 4, step, step_in_bar, beat_in_bar, bar, BPM))
        if step_in_bar == 0:
            events.append(ClockEvent("bar", bar, step, step_in_bar, beat_in_bar, bar, BPM))
            events.append(self._next_chord(descriptors, controls, bar))

        # Bass: simple structural pulse, mostly on beat 1/3, busier when the system is dense.
        if step_in_bar in {0, 8} or (controls.grain_density > 0.68 and step_in_bar in {4, 12}):
            if random.random() < self._bass_probability(descriptors, controls, step_in_bar):
                events.append(self._make_bass(descriptors, controls))

        # Lead: Markov melody quantized to 16ths; density controls how many slots are filled.
        if random.random() < self._lead_probability(descriptors, controls, step_in_bar):
            events.append(self._make_lead(descriptors, controls))

        # Hits/grains: appear mostly with chaos/distortion and high grain density.
        if random.random() < self._hit_probability(descriptors, controls, step_in_bar):
            events.append(self._make_hit(descriptors, controls))

        return events

    def _next_chord(self, descriptors: dict[str, float], controls: RuntimeControls, bar: int) -> ChordEvent:
        chaos = controls.alignment_chaos
        spread = descriptors.get("spread", 0.0)
        temperature = 0.35 + chaos * 0.55 + spread * 0.25
        self.chord_degree = int(self.chord_chain.next(temperature=temperature))
        root, third, fifth = chord_notes(self.chord_degree, octave=0)
        return ChordEvent(root, third, fifth, self.chord_degree, controls.section_id, bar)

    def _bass_probability(self, descriptors: dict[str, float], controls: RuntimeControls, step_in_bar: int) -> float:
        density = descriptors.get("density", 0.0)
        base = 0.92 if step_in_bar in {0, 8} else 0.42
        return clamp01(base + density * 0.12 - controls.alignment_chaos * 0.18)

    def _lead_probability(self, descriptors: dict[str, float], controls: RuntimeControls, step_in_bar: int) -> float:
        speed = descriptors.get("mean_speed", 0.0)
        coherence = descriptors.get("direction_coherence", 0.0)
        chaos = controls.alignment_chaos
        density = controls.grain_density

        # Ordered states prefer stronger grid positions. Chaotic states can fill any 16th.
        strong_grid_bonus = 0.12 if step_in_bar in {0, 4, 8, 12} else 0.0
        offbeat_bonus = 0.10 * chaos if step_in_bar in {2, 6, 10, 14} else 0.0
        fragmented_bonus = 0.12 * (1.0 - coherence)

        return clamp01(0.03 + density * 0.42 + speed * 0.16 + strong_grid_bonus + offbeat_bonus + fragmented_bonus)

    def _hit_probability(self, descriptors: dict[str, float], controls: RuntimeControls, step_in_bar: int) -> float:
        chaos = controls.alignment_chaos
        distortion = controls.noise_distortion
        speed = descriptors.get("mean_speed", 0.0)
        offbeat = step_in_bar in {3, 7, 11, 15, 6, 14}
        downbeat = step_in_bar in {0, 8}
        base = 0.02 + controls.grain_density * 0.08 + chaos * 0.12 + distortion * 0.22 + speed * 0.05
        if offbeat:
            base += 0.10 * max(chaos, distortion)
        if downbeat and distortion > 0.72:
            base += 0.10
        return clamp01(base)

    def _make_bass(self, descriptors: dict[str, float], controls: RuntimeControls) -> NoteEventV2:
        self.event_id += 1
        relative = int(self.bass_degrees.next(temperature=0.45 + controls.alignment_chaos * 0.35))
        degree = self.chord_degree + relative
        midi_note = degree_to_midi(degree, octave=-1)
        velocity = clamp_midi(62 + int(descriptors.get("energy", 0.0) * 38) + int(controls.noise_distortion * 12))
        duration_ms = int((420 + controls.grain_density * 220) * (60.0 / BPM) / 0.5)
        return NoteEventV2(self.event_id, "bass", midi_note, velocity, duration_ms, degree, -1, VOICE_LAYER_ID["bass"], controls.section_id, self.chord_degree)

    def _make_lead(self, descriptors: dict[str, float], controls: RuntimeControls) -> NoteEventV2:
        self.event_id += 1
        chaos = controls.alignment_chaos
        spread = descriptors.get("spread", 0.0)
        density = descriptors.get("density", 0.0)
        temperature = 0.35 + chaos * 0.75 + controls.grain_density * 0.20
        degree = int(self.lead_pitch.next(temperature=temperature))

        # Compact swarms bias to chord tones; spread/chaos can widen register.
        if density > 0.70 and random.random() < 0.45:
            degree = random.choice([self.chord_degree, self.chord_degree + 2, self.chord_degree + 4])
        octave_span = 1 + int(spread * 2.5 + chaos * 1.5)
        octave = random.randint(0, octave_span)
        if chaos > 0.75 and random.random() < 0.25:
            octave -= 1

        midi_note = degree_to_midi(degree + self.chord_degree, octave=octave)
        velocity = clamp_midi(42 + int(descriptors.get("energy", 0.0) * 55) + int(chaos * 20) + random.randint(-6, 10))
        duration_steps = int(self.rhythm_steps.next(temperature=0.55 + chaos * 0.55))
        duration_ms = int(duration_steps * (60.0 / BPM / 4.0) * 1000)
        return NoteEventV2(self.event_id, "lead", midi_note, velocity, duration_ms, degree, octave, VOICE_LAYER_ID["lead"], controls.section_id, self.chord_degree)

    def _make_hit(self, descriptors: dict[str, float], controls: RuntimeControls) -> HitEvent:
        self.event_id += 1
        distortion = controls.noise_distortion
        chaos = controls.alignment_chaos
        if distortion > 0.72:
            voice: HitVoice = "noise"
        elif chaos > 0.62:
            voice = "glitch"
        else:
            voice = "grain"
        sample_id = int(self.hit_samples.next(temperature=0.55 + chaos * 0.55 + distortion * 0.35))
        velocity = clamp_midi(38 + int(descriptors.get("energy", 0.0) * 42) + int(distortion * 38) + random.randint(-5, 8))
        duration_ms = int(80 + controls.grain_density * 180 + chaos * 90)
        return HitEvent(self.event_id, voice, sample_id, velocity, duration_ms, controls.section_id)
