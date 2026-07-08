"""Smoke test headless del core: gira 300 frame, verifica descrittori ed eventi.

Uso (dalla cartella Claude/):  ../.venv/Scripts/python.exe smoke_test.py
"""
import numpy as np

from aquarium.boids import Flock, World
from aquarium.descriptors import DescriptorExtractor
from aquarium.osc_out import OSCSender
from aquarium.markov import HierarchicalGenerator

CHORDS = ["i", "II", "III", "iv", "V", "VI", "VII"]


def main():
    flock = Flock(seed=1)
    world = World(food=0.0, predator=0.0, turbulence=0.15, density=0.3)
    desc = DescriptorExtractor()
    osc = OSCSender(enabled=False, verbose=False)  # niente rete, solo logica
    gen = HierarchicalGenerator(seed=1)

    dt = 1 / 60
    ev_counts = {"dart": 0, "turn": 0, "collision": 0}
    notes = rests = 0
    chords_seen = []
    sample = []
    d = {}

    for frame in range(300):
        # a meta' esperimento accendo food per aggregare, poi un predatore + densita' su
        if frame == 100:
            world.food = 0.9
            world.food_pos = np.array([640.0, 360.0])
            world.density = 0.7
        if frame == 200:
            world.food = 0.0
            world.predator = 1.0
            world.predator_pos = np.array([640.0, 360.0])

        events = flock.update(world, dt)
        d = desc.compute(flock, world)
        for e in events:
            ev_counts[e[0]] += 1

        music, chord_change = gen.tick(dt, d, world)
        if chord_change is not None:
            chords_seen.append(chord_change)
        for m in music:
            if m.kind == "note":
                notes += 1
                assert 0 <= m.degree <= 6, f"grado fuori range: {m.degree}"
                if len(sample) < 8:
                    sample.append(f"note deg={m.degree} oct={m.octave} dur={m.duration_beats} "
                                  f"vel={m.velocity} accordo={CHORDS[m.chord_root]}")
            else:
                rests += 1

    # --- verifiche ---
    assert np.all(np.isfinite(flock.pos)), "posizioni non finite!"
    assert np.all(flock.pos[:, 0] >= 0) and np.all(flock.pos[:, 0] <= 1280)
    assert np.all(flock.pos[:, 1] >= 0) and np.all(flock.pos[:, 1] <= 720)
    for k, v in d.items():
        assert 0.0 <= v <= 1.0, f"descrittore {k} fuori range: {v}"

    print("=== SMOKE TEST OK ===")
    print(f"eventi movimento: {ev_counts}")
    print(f"eventi musicali: note={notes} rest={rests}")
    print(f"progressione accordi: {' -> '.join(CHORDS[c] for c in chords_seen)}")
    print("descrittori finali (0..1):")
    for k, v in d.items():
        print(f"  {k:12s} {v:.3f}")
    print("campione note:")
    for s in sample:
        print("  " + s)


if __name__ == "__main__":
    main()
