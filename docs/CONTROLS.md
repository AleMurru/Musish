# Controls

Keyboard and mouse, MIDI and the UDP control port all work at the same time. Every one of them writes to the same live state (`RuntimeControls` in `src/aquarium_boids/controls.py`).

## Command line

```
python src/main.py [--fullscreen] [--classic] [--mode art|data] [--size WxH]
                   [--no-trails] [--no-glow] [--no-particles]
```

| Option | Effect |
|---|---|
| `--fullscreen` | start fullscreen (a borderless window at desktop size) |
| `--classic` | the original flat look with a text HUD, instead of the thermal look |
| `--mode art` / `--mode data` | thermal look without / with the HUD (default `art`) |
| `--size 1920x1080` | window size (at least 320x200); the simulation is always 1200x750 |
| `--no-trails`, `--no-glow`, `--no-particles` | start with that thermal layer off |

## Keyboard and mouse

| Input | Effect |
|---|---|
| mouse left (hold) | food: fish are drawn to the pointer |
| mouse right (hold) | predator: fish flee the pointer (within 220 px); Max gets `/fx/predator 1`, then `0` on release |
| `-` / `=` | fewer / more fish (steps of 5, 1–100) |
| `A`/`Z`, `S`/`X`, `D`/`C` | alignment, cohesion, separation up / down (steps of 0.1) |
| `N`/`M` | noise up / down (steps of 0.03) |
| `SPACE` | pause / resume the simulation |
| `R` | new flock (keeps the current number of fish) |
| `UP`/`DOWN` | `density_fader` ± 0.05 (legacy Markov layer only) |
| `1`–`6` | section: intro, growth, dense, chaos, release, outro (legacy Markov layer only) |
| `H` | thermal look: art view ↔ data view (HUD) |
| `T` / `G` / `P` | thermal look: trails / glow / particles on or off |
| `F11` | fullscreen on / off |
| `ESC` | quit (sends `/fx/predator 0` first) |

The keyboard has no upper limit on the weights, unlike MIDI and UDP, which clip.

## AKAI MPK mini 3

**Controller settings:** set **PROG CHANGE** on and select **bank A**. Then:
- the pads send Program Change 16–23 on MIDI channel 10;
- the knobs K1–K8 send CC 16–23 on channel 1.

**Knobs** (from `MIDI_CC_MAPPING_MPK` in `config.py`). A parameter that starts with `/` is not a simulation control: it is sent to Max as that OSC address whenever the knob moves.

| Knob | CC | Controls | Range |
|---|---|---|---|
| K1 | 16 | agitation (`noise_weight`) | 0–1.5 |
| K2 | 17 | grain length → `/mix/grain_ms` | 10–400 ms |
| K3 | 18 | `cohesion_weight` | 0–3 |
| K4 | 19 | number of fish (`population`) | 1–100 |
| K5 | 20 | slice gain → `/mix/slice_gain` | 0–1 |
| K6 | 21 | grain gain → `/mix/gran_gain` | 0–1 |
| K7 | 22 | kick gain → `/mix/kick_gain` | 0–1 |
| K8 | 23 | PLAUD master → `/mix/master` | 0–1 |

Alignment stays at 1.0 with this controller.

**Pads:**

| Pad | Action |
|---|---|
| 1 | one kick (`/pad/kick`) |
| 2 | scare: a predator at the centre for 1 s (same path as the right mouse button, so Max gets the predator events) |
| 3 | food at the centre, on / off |
| 4 | calm: removes pad food, the scare and any fader-set food or predator |
| 5–8 | play slice 1–4 of the grain source (`/pad/sample 1–4`) |

Note-on / note-off from the pads (PROG CHANGE off) and the joystick are ignored.

## AKAI MIDIMIX

The 8 faders control the ecosystem (`MIDI_CC_MAPPING` in `config.py`). Alignment stays at 1.0.

| Fader | CC | Parameter | Range |
|---|---|---|---|
| 1 | 19 | number of fish (`population`) | 1–100 |
| 2 | 23 | `cohesion_weight` | 0–3 |
| 3 | 27 | `separation_weight` | 0–4 |
| 4 | 31 | `noise_weight` | 0–1.5 |
| 5 | 49 | `food_amount` (attractor at the centre) | 0–3 |
| 6 | 53 | `predator_amount` (repeller at the centre) | 0–3 |
| 7 | 57 | `density_fader` (legacy Markov layer) | 0–1 |
| 8 | 61 | `section_id` (legacy Markov layer) | 0–5 |

## Which device and which mapping

At start Python lists every MIDI input (`[midi] input device N: <name>`). It then chooses the device and the mapping like this:

1. **Device:**
   - the first input whose name contains `MIDI_INPUT_NAME` (default `"MIDIMIX"`, case-insensitive);
   - otherwise the **first** input ("fallback").
2. **Mapping:** taken from the name of the device it opened:
   - a name containing `MPK` → the MPK profile;
   - anything else → the MIDIMIX table.
3. The terminal confirms the choice: `[midi] active profile: …`.

So with only the MPK connected you get the MPK profile. With both controllers connected, the MIDIMIX wins.

With `MIDI_DEBUG = True` (the default), every message is printed:
- `[midi] cc=X value=Y channel=Z`: a raw knob or fader;
- `[midi-map] cc=X -> parameter = value`: the mapped result;
- `[pad] n  (program P, channel C)`: a pad.

### Re-mapping a control

1. Move the knob or fader and read `cc=X` in the terminal.
2. In `src/aquarium_boids/config.py`, edit the right table. Each entry is `cc: ("parameter", min, max, round_to_int)`.
3. Restart.

### MIDI troubleshooting

| Symptom | Check |
|---|---|
| no `[midi] listening to …` line | Another program (Max, a DAW) may hold the controller: close it, unplug and replug, restart. Python opens the device itself; Max must not read it |
| the wrong device opened (`… fallback`) | Set `MIDI_INPUT_NAME` in `config.py` to part of the name printed at start |
| `[midi] cc=…` lines but no `[midi-map]` | That CC is not in the active table: re-map it |
| MPK pads print `note on … ignored` | PROG CHANGE is off on the controller |

## UDP control port 7500

Any program can set controls with plain-text UDP messages such as `control cohesion_weight 2.2;`. The format and the accepted names are listed in [OSC.md](OSC.md#control-input-on-port-7500).

To try it: run `python src/tools/send_control_test.py` while the simulation runs.

## Defaults

| Control | Default |
|---|---|
| number of fish | 100 |
| `alignment_weight` | 1.0 |
| `cohesion_weight` | 0.9 |
| `separation_weight` | 1.35 |
| `noise_weight` | 0.18 |
| `food_strength`, `predator_strength` (mouse) | 1.0 |
| `food_amount`, `predator_amount` (centre) | 0 |
| `density_fader` | 0.25 |
| section | 0 (intro) |
