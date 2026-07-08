"""Aquarium as Instrument - VERSIONE CLAUDE (visual + controlli live).

Tenuta SEPARATA dalla base ufficiale in Codex/. Usa il package `aquarium/`.
Differenze chiave vs Codex: boids vettorizzati (numpy) + EVENTI DISCRETI diretti
(dart/turn/collision via OSC) per la percepibilita' del legame visual<->audio.
Nessuna Markov qui (per ora): emette descrittori continui + eventi.

Avvio (dalla cartella Claude/):
    cd Claude
    ../.venv/Scripts/python.exe run_claude_version.py

Controlli:
    Mouse SX tenuto = CIBO (aggregazione)   Mouse DX tenuto = PREDATORE (fuga)
    Q/A food  W/S predator  E/D turbulence  R/F density
    T scie  H hud  O osc on/off  SPACE pausa  BACKSPACE reset  ESC esci
"""
from __future__ import annotations
import os
import numpy as np
import pygame

from aquarium import config as C
from aquarium.boids import Flock, World
from aquarium.descriptors import DescriptorExtractor
from aquarium.osc_out import OSCSender
from aquarium.markov import HierarchicalGenerator

BG = (12, 16, 22)
TRAIL_FADE = (12, 16, 22, 34)


def speed_color(frac: float) -> pygame.Color:
    c = pygame.Color(0)
    hue = float(np.clip(210 - 210 * frac, 0, 210))
    c.hsva = (hue, 80, 100, 100)
    return c


class EventFlash:
    __slots__ = ("x", "y", "t", "kind")

    def __init__(self, x, y, kind):
        self.x, self.y, self.kind, self.t = x, y, kind, 1.0

    def step(self, dt):
        self.t -= dt * 2.6
        return self.t > 0


def draw_fish(surf, pos, vel, size):
    v = np.array(vel)
    sp = np.linalg.norm(v)
    d = v / sp if sp > 1e-6 else np.array([1.0, 0.0])
    perp = np.array([-d[1], d[0]])
    L = 6.0 * size + 4.0
    W = 2.6 * size + 1.5
    tip = pos + d * L
    a = pos - d * L * 0.5 + perp * W
    b = pos - d * L * 0.5 - perp * W
    pygame.draw.polygon(surf, speed_color(min(sp / C.MAX_SPEED, 1.0)), [tip, a, b])


def draw_hud(screen, font, d, world, fps, osc_on, note_count=0, cur_chord=0, music_on=True):
    x0, y0 = 16, 14
    CHORDS = ["i", "II", "III", "iv", "V", "VI", "VII"]
    labels = ["mean_speed", "energy", "density", "spread",
              "coherence", "nearest", "center_x", "center_y"]
    screen.blit(font.render("DESCRIPTORS (OSC ->:%d)" % C.OSC_PORT, True, (150, 200, 230)), (x0, y0))
    y = y0 + 22
    for k in labels:
        val = d.get(k, 0.0)
        pygame.draw.rect(screen, (40, 48, 58), (x0, y + 5, 160, 8))
        pygame.draw.rect(screen, (90, 200, 160), (x0, y + 5, int(160 * val), 8))
        screen.blit(font.render(f"{k:11s} {val:0.2f}", True, (200, 210, 220)), (x0 + 172, y))
        y += 20
    y += 8
    screen.blit(font.render("WORLD CONTROLS", True, (230, 180, 150)), (x0, y)); y += 22
    for k, val in [("food", world.food), ("predator", world.predator),
                   ("turbulence", world.turbulence), ("density", world.density)]:
        pygame.draw.rect(screen, (40, 48, 58), (x0, y + 5, 160, 8))
        pygame.draw.rect(screen, (220, 150, 90), (x0, y + 5, int(160 * val), 8))
        screen.blit(font.render(f"{k:11s} {val:0.2f}", True, (210, 200, 190)), (x0 + 172, y))
        y += 20
    y += 8
    mus = f"MUSIC {'ON' if music_on else 'OFF'}  accordo: {CHORDS[cur_chord % 7]}  note inviate: {note_count}"
    screen.blit(font.render(mus, True, (170, 160, 230)), (x0, y))
    info = f"{fps:4.0f} fps  OSC {'ON' if osc_on else 'OFF'}  [H]ud [T]rails [O]sc [M]usic  SX=cibo DX=predatore"
    screen.blit(font.render(info, True, (120, 130, 140)), (x0, C.HEIGHT - 24))


def main():
    headless = os.environ.get("SDL_VIDEODRIVER") == "dummy"
    pygame.init()
    screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
    pygame.display.set_caption("Aquarium as Instrument - Claude version")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 15)

    trails = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    fade = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    fade.fill(TRAIL_FADE)

    flock = Flock(seed=7)
    world = World()
    desc = DescriptorExtractor()
    osc = OSCSender(enabled=True, verbose=False)
    gen = HierarchicalGenerator(seed=7)

    flashes: list[EventFlash] = []
    show_trails = show_hud = osc_on = music_on = True
    note_count = 0
    cur_chord = 0
    paused = False
    desc_interval = 1.0 / C.DESC_SEND_HZ
    desc_acc = 0.0
    d = {}
    max_frames = int(os.environ.get("AQ_MAX_FRAMES", "0"))
    frame = 0

    running = True
    while running:
        dt = min(clock.tick(C.FPS) / 1000.0, 1 / 30)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_SPACE:
                    paused = not paused
                elif e.key == pygame.K_t:
                    show_trails = not show_trails
                elif e.key == pygame.K_h:
                    show_hud = not show_hud
                elif e.key == pygame.K_o:
                    osc_on = not osc_on
                elif e.key == pygame.K_m:
                    music_on = not music_on
                elif e.key == pygame.K_BACKSPACE:
                    flock = Flock(seed=np.random.randint(1_000_000))

        keys = pygame.key.get_pressed()
        step = 1.2 * dt
        if keys[pygame.K_q]: world.food += step
        if keys[pygame.K_a]: world.food -= step
        if keys[pygame.K_w]: world.predator += step
        if keys[pygame.K_s]: world.predator -= step
        if keys[pygame.K_e]: world.turbulence += step
        if keys[pygame.K_d]: world.turbulence -= step
        if keys[pygame.K_r]: world.density += step
        if keys[pygame.K_f]: world.density -= step

        mx, my = pygame.mouse.get_pos()
        mb = pygame.mouse.get_pressed()
        if mb[0]:
            world.food_pos = np.array([float(mx), float(my)])
            world.food = min(1.0, world.food + step * 1.5)
        else:
            world.food = max(0.0, world.food - step * 0.8)
        if mb[2]:
            world.predator_pos = np.array([float(mx), float(my)])
            world.predator = min(1.0, world.predator + step * 2.0)
        else:
            world.predator = max(0.0, world.predator - step * 1.2)
        world.clamp()

        if not paused:
            events = flock.update(world, dt)
            d = desc.compute(flock, world)
            for ev in events:
                if ev[0] == "collision":
                    flashes.append(EventFlash(ev[1] * C.WIDTH, ev[2] * C.HEIGHT, "collision"))
                else:
                    i = ev[1]
                    flashes.append(EventFlash(flock.pos[i, 0], flock.pos[i, 1], ev[0]))
            if osc_on:
                osc.send_events(events)
                osc.send_world(world)
                desc_acc += dt
                if desc_acc >= desc_interval and d:
                    osc.send_descriptors(d)
                    desc_acc = 0.0
            if music_on and d:
                music_events, chord_change = gen.tick(dt, d, world)
                note_count += sum(1 for m in music_events if m.kind == "note")
                cur_chord = gen.chord_root
                if osc_on:
                    osc.send_music(music_events, chord_change)

        if show_trails:
            trails.blit(fade, (0, 0))
            for i in range(flock.n):
                draw_fish(trails, flock.pos[i], flock.vel[i], flock.size[i])
            screen.fill(BG)
            screen.blit(trails, (0, 0))
        else:
            screen.fill(BG)
            for i in range(flock.n):
                draw_fish(screen, flock.pos[i], flock.vel[i], flock.size[i])

        if world.food > 0.02:
            pygame.draw.circle(screen, (90, 220, 140), world.food_pos.astype(int),
                               int(8 + 22 * world.food), 2)
        if world.predator > 0.02:
            pygame.draw.circle(screen, (230, 80, 80), world.predator_pos.astype(int),
                               int(10 + 40 * world.predator), 2)

        colors = {"dart": (255, 240, 120), "turn": (120, 220, 255), "collision": (255, 130, 200)}
        for fl in flashes:
            r = int(6 + 26 * (1 - fl.t))
            pygame.draw.circle(screen, colors[fl.kind], (int(fl.x), int(fl.y)), r, 2)
        flashes = [fl for fl in flashes if fl.step(dt)]

        if show_hud:
            draw_hud(screen, font, d, world, clock.get_fps(), osc_on,
                     note_count, cur_chord, music_on)

        pygame.display.flip()
        frame += 1
        if max_frames and frame >= max_frames:
            running = False

    pygame.quit()
    if headless:
        print(f"HEADLESS DRY-RUN OK: {frame} frame renderizzati senza errori.")


if __name__ == "__main__":
    main()
