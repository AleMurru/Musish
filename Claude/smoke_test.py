"""Smoke test headless del core: gira 300 frame, verifica descrittori ed eventi.

Uso (dalla cartella Claude/):  ../.venv/Scripts/python.exe smoke_test.py
"""
import numpy as np

from aquarium.boids import Flock, World
from aquarium.descriptors import DescriptorExtractor
from aquarium.osc_out import OSCSender


def main():
    flock = Flock(seed=1)
    world = World(food=0.0, predator=0.0, turbulence=0.15, density=0.3)
    desc = DescriptorExtractor()
    osc = OSCSender(enabled=False, verbose=False)  # niente rete, solo logica

    dt = 1 / 60
    ev_counts = {"dart": 0, "turn": 0, "collision": 0}
    d = {}

    for frame in range(300):
        # a meta' esperimento accendo food per aggregare, poi un predatore
        if frame == 100:
            world.food = 0.9
            world.food_pos = np.array([640.0, 360.0])
        if frame == 200:
            world.food = 0.0
            world.predator = 1.0
            world.predator_pos = np.array([640.0, 360.0])

        events = flock.update(world, dt)
        d = desc.compute(flock, world)
        for e in events:
            ev_counts[e[0]] += 1

    # --- verifiche ---
    assert np.all(np.isfinite(flock.pos)), "posizioni non finite!"
    assert np.all(flock.pos[:, 0] >= 0) and np.all(flock.pos[:, 0] <= 1280)
    assert np.all(flock.pos[:, 1] >= 0) and np.all(flock.pos[:, 1] <= 720)
    for k, v in d.items():
        assert 0.0 <= v <= 1.0, f"descrittore {k} fuori range: {v}"

    print("=== SMOKE TEST OK ===")
    print(f"eventi: {ev_counts}")
    print("descrittori finali (0..1):")
    for k, v in d.items():
        print(f"  {k:12s} {v:.3f}")


if __name__ == "__main__":
    main()
