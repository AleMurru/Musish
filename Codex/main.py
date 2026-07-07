from __future__ import annotations

import csv
import random
import sys
import time
from pathlib import Path

import pygame
from pygame.math import Vector2

from aquarium_boids.boids import Boid
from aquarium_boids.config import (
    BACKGROUND,
    BOID_COUNT,
    BPM,
    CONTROL_PORT,
    ENABLE_MIDI_INPUT,
    FPS,
    HEIGHT,
    MIDI_CC_MAPPING,
    MIDI_DEBUG,
    MIDI_INPUT_NAME,
    OSC_HOST,
    OSC_PORT,
    SEND_DESCRIPTOR_HZ,
    TEXT,
    WIDTH,
)
from aquarium_boids.control_in import ControlReceiver
from aquarium_boids.controls import RuntimeControls, clamp01
from aquarium_boids.descriptors import DESCRIPTOR_ORDER, OnePoleSmoother, compute_descriptors
from aquarium_boids.markov import LAYERS, SECTIONS, SymbolicGenerator
from aquarium_boids.midi_in import MidiControllerInput
from aquarium_boids.osc_io import OscSender


BASE_DIR = Path(__file__).resolve().parent


def create_flock(count: int) -> list[Boid]:
    return [Boid.create(i, WIDTH, HEIGHT) for i in range(count)]


def write_log_header(path: Path) -> None:
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["time", *DESCRIPTOR_ORDER, "density_fader", "section"])


def append_log(path: Path, now: float, descriptors: dict[str, float], controls: RuntimeControls) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            f"{now:.3f}",
            *[f"{descriptors.get(key, 0.0):.5f}" for key in DESCRIPTOR_ORDER],
            f"{controls.density_fader:.5f}",
            controls.section_name,
        ])


def handle_key(event: pygame.event.Event, controls: RuntimeControls, flock: list[Boid]) -> list[Boid]:
    step = 0.05
    if event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit(0)
    if event.key == pygame.K_SPACE:
        controls.paused = not controls.paused
    elif event.key == pygame.K_UP:
        controls.density_fader = clamp01(controls.density_fader + step)
    elif event.key == pygame.K_DOWN:
        controls.density_fader = clamp01(controls.density_fader - step)
    elif event.key == pygame.K_a:
        controls.alignment_weight += 0.1
    elif event.key == pygame.K_z:
        controls.alignment_weight = max(0.0, controls.alignment_weight - 0.1)
    elif event.key == pygame.K_s:
        controls.cohesion_weight += 0.1
    elif event.key == pygame.K_x:
        controls.cohesion_weight = max(0.0, controls.cohesion_weight - 0.1)
    elif event.key == pygame.K_d:
        controls.separation_weight += 0.1
    elif event.key == pygame.K_c:
        controls.separation_weight = max(0.0, controls.separation_weight - 0.1)
    elif event.key == pygame.K_n:
        controls.noise_weight += 0.03
    elif event.key == pygame.K_m:
        controls.noise_weight = max(0.0, controls.noise_weight - 0.03)
    elif event.key == pygame.K_r:
        return create_flock(BOID_COUNT)
    elif pygame.K_1 <= event.key <= pygame.K_6:
        controls.section_id = event.key - pygame.K_1
    return flock


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, controls: RuntimeControls, descriptors: dict[str, float]) -> None:
    lines = [
        "Acquario / Boids -> Max | MIDIMIX direct + Max control ready",
        f"density_fader UP/DOWN: {controls.density_fader:.2f} | section 1-6: {controls.section_name}",
        f"A/Z align {controls.alignment_weight:.2f} | S/X cohesion {controls.cohesion_weight:.2f} | D/C separation {controls.separation_weight:.2f} | N/M noise {controls.noise_weight:.2f}",
        f"food_amount {controls.food_amount:.2f} | predator_amount {controls.predator_amount:.2f} | mouse food/pred {controls.food_strength:.2f}/{controls.predator_strength:.2f}",
        "Mouse left = food/attractor | mouse right = predator/repeller | SPACE pause | R reset",
        f"OSC out: {OSC_HOST}:{OSC_PORT} | plain out: 7401 | control in: {CONTROL_PORT}",
        f"mean_speed {descriptors.get('mean_speed', 0):.2f} | density {descriptors.get('density', 0):.2f} | spread {descriptors.get('spread', 0):.2f} | coherence {descriptors.get('direction_coherence', 0):.2f}",
    ]
    y = 10
    for line in lines:
        img = font.render(line, True, TEXT)
        surface.blit(img, (12, y))
        y += 20


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Aquarium Boids OSC -> Max")
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    controls = RuntimeControls()
    flock = create_flock(BOID_COUNT)
    smoother = OnePoleSmoother(alpha=0.16)
    osc = OscSender(OSC_HOST, OSC_PORT)
    generator = SymbolicGenerator()
    control_receiver = ControlReceiver(port=CONTROL_PORT)
    control_receiver.start()
    print(f"Listening for Max/MIDIMIX controls on UDP {CONTROL_PORT}")

    midi_input = MidiControllerInput(
        device_name=MIDI_INPUT_NAME,
        mapping=MIDI_CC_MAPPING,
        debug=MIDI_DEBUG,
    )
    if ENABLE_MIDI_INPUT:
        midi_input.start()

    log_path = BASE_DIR / "logs" / f"descriptors_{int(time.time())}.csv"
    write_log_header(log_path)

    last_descriptor_send = 0.0
    last_log = 0.0
    next_event_time = 0.0
    descriptors: dict[str, float] = {}

    while True:
        dt = clock.tick(FPS) / (1000.0 / FPS)
        now = time.time()

        applied_controls = control_receiver.drain(controls)
        for command in applied_controls:
            print(f"[control] {command.name} = {command.value}")

        midi_controls = midi_input.poll(controls)
        for command in midi_controls:
            print(f"[midi-map] cc={command.cc} -> {command.parameter} = {command.scaled_value}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                flock = handle_key(event, controls, flock)

        mouse_buttons = pygame.mouse.get_pressed(num_buttons=3)
        mouse_pos = Vector2(pygame.mouse.get_pos())
        attractor = mouse_pos if mouse_buttons[0] else None
        repeller = mouse_pos if mouse_buttons[2] else None
        if attractor is None and controls.food_amount > 0.01:
            attractor = Vector2(WIDTH * 0.5, HEIGHT * 0.5)
        if repeller is None and controls.predator_amount > 0.01:
            repeller = Vector2(WIDTH * 0.5, HEIGHT * 0.5)

        if not controls.paused:
            for boid in flock:
                boid.flock(flock, controls, WIDTH, HEIGHT, attractor=attractor, repeller=repeller)
            for boid in flock:
                boid.update(dt_scale=dt)

        descriptors = smoother.process(compute_descriptors(flock, WIDTH, HEIGHT))

        if now - last_descriptor_send >= 1.0 / SEND_DESCRIPTOR_HZ:
            osc.send_descriptors(descriptors)
            osc.send_controls(controls)
            osc.send_direct_mapping(descriptors, controls)
            last_descriptor_send = now

        if now - last_log >= 0.25:
            append_log(log_path, now, descriptors, controls)
            last_log = now

        # Event rate: collective/slow at low density, granular/fast at high density and high fish speed.
        if now >= next_event_time:
            burst = 1 + int(controls.density_fader * 3.2)
            for _ in range(burst):
                event = generator.generate(descriptors, controls)
                osc.send_music_event(event)
                if event.event_type == "note" and flock:
                    random.choice(flock).flash = 1.0
                print(
                    f"/music/{event.event_type} id={event.event_id} degree={event.degree} oct={event.octave} "
                    f"dur={event.duration_beats} vel={event.velocity} layer={LAYERS[event.layer_id]} "
                    f"section={SECTIONS[event.section_id]}"
                )
            events_per_second = 0.45 + controls.density_fader * 5.5 + descriptors.get("mean_speed", 0.0) * 2.0
            next_event_time = now + max(0.08, 1.0 / events_per_second)

        surface.fill(BACKGROUND)
        if attractor is not None:
            pygame.draw.circle(surface, (80, 255, 150), attractor, 18, 2)
        if repeller is not None:
            pygame.draw.circle(surface, (255, 80, 90), repeller, 34, 2)
        for boid in flock:
            boid.draw(surface)
        draw_hud(surface, font, controls, descriptors)
        pygame.display.flip()


if __name__ == "__main__":
    main()
