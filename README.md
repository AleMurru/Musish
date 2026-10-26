# Fishmus

A flock of simulated fish performs **PLAUD**, a DDSP neural synthesis model trained on about
30 minutes of recordings by the musician Rafael. Nobody plays notes or writes prompts. The fish
swim, and their collective behaviour (where the flock is, how agitated it is, when a predator
scatters it) drives the model live. The performer shapes the ecosystem (food, predators,
cohesion, number of fish), and the sound follows the flock.

The instrument concept is called *Shoal*. The project started as *Generative Boids* / Musish.

**Demo video:** [VIDEO_LINK](VIDEO_LINK)

## How it works

```
 boids simulation (Python / pygame)
   |  alignment, cohesion, separation, noise, food, predator
   v
 flock descriptors, 0-1, ~15 Hz
   |  position, spread, speed, energy, density, coherence, fish count, per-fish x
   v
 OSC over UDP -> 127.0.0.1:7400
   v
 Max/MSP
   |- PLAUD (nn~)        flock position steers PLAUD's prior territory;
   |                     fish count -> loudness, agitation -> latent L2
   |- max/shoal_fx       predator events -> a kick + a spectral shake of PLAUD
   '- max/shoal_gran     each fish is a grain voice, panned by its x position

 AKAI MPK mini 3 (MIDI) -> live control of the flock and of the mix
```

## Quick start (no Max needed)

Needs Python 3.13 (tested on Windows).

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

Without Max the simulation runs normally, and the OSC packets simply go unanswered.

| Input | Action |
|---|---|
| mouse left (hold) | food: the fish are attracted to the pointer |
| mouse right (hold) | predator: the fish flee from the pointer; Max receives a scare event |
| H | art view (no text) / data view (HUD with descriptors) |
| T / G / P | trails / glow / drifting particles on or off |
| F11 | fullscreen on/off |
| ESC | quit |

Options:
- `--fullscreen`: start fullscreen.
- `--classic`: the original flat look.
- `--size 1920x1080`: set the window size; the simulation itself is always 1200x750.

## With Max

**What you need:**
- Max 9.
- The `nn~` external.
- A PLAUD device and a trained PLAUD model. PLAUD is by Błażej Kotowski and is **not included**
  in this repository.

**1. Add the OSC routes in the PLAUD device.** Add `[udpreceive 7400]`, then one `route` per
family. Each output goes to a `send` that the patches listen to:

| route | send names |
|---|---|
| `route /plaud/x /plaud/y /plaud/loudness /plaud/temp` | `plaudX` `plaudY` (read by `prior~`), `plaudLoudness`, `plaudTemp` |
| `route /fx/predator /fx/predator_strength` | `fxPredator` `fxPredatorStrength` |
| `route /gran/fish_x /gran/density /gran/noise` | `granFishX` `granDensity` `granNoise` |
| `route /mix/master /mix/kick_gain /mix/gran_gain /mix/grain_ms /mix/slice_gain` | PLAUD output gain (0-1 -> -70..0 dB), `mixKickGain` `mixGranGain` `mixGrainMs` `mixSliceGain` |
| `route /pad/kick /pad/sample` | `padKick` `padSample` |

`shoal_fx` drives PLAUD's own `---waveshaping` and `---spectral-warp` parameters for the shake.

In `prior~` (the PLAUD prior subpatch), three changes put the flock on the map:
- `[r plaudX]` → the `territory_x` number box.
- `[r plaudY]` → `[!- 1.]` → the `territory_y` number box. The inversion is needed because pygame's y axis points down.
- Change `metro 2754 @active 1` to `metro 2754 @active 0`. This stops prior~'s own random walk on Y, so only the flock moves the point.

**2. Open the two patches** in the same Max session as the device:
- `max/shoal_fx.maxpat`: the predator kick (synth or sample) and the spectral shake.
- `max/shoal_gran.maxpat`: a 16-voice granulator, one voice per fish, plus the slice player for pads 5–8.

**3. Add your own audio.** No audio is shipped. Put two files next to the patches:
- `shoal_kick.wav`: any short kick sample.
- `shoal_gran.aiff`: any sound to granulate. The grain region and its length are set in the patch.

To switch sources live, put your own sounds in `max/grains/` and pick them from the menu (.wav / .aif / .aiff; "rescan" refreshes the list).

## OSC messages (Python → Max, port 7400)

| Address | Range | Meaning |
|---|---|---|
| `/plaud/x`, `/plaud/y` | 0–1 | flock centroid. Steers PLAUD's prior. |
| `/plaud/loudness` | 0.6–1.4 | follows the number of fish. Drives PLAUD's loudness and its "components" limit. |
| `/plaud/temp` | 0.2–1.0 | flock energy (agitation). Drives PLAUD's latent L2 (the name is historical). |
| `/fx/predator` | 1 / 0 | predator scare onset / release. Triggers the kick and the shake. |
| `/fx/predator_strength` | 0–1 | predator strength (sent before each onset) |
| `/gran/fish_x` | list of up to 32 floats, 0–1 | x position of each fish. Sets the grain voice pan. |
| `/gran/density` | 0–100 | number of fish, scaled (grain rate) |
| `/gran/noise` | 0–1 | chaos: agitation + predator + disorder (grain jitter and region spread) |
| `/gran/pan`, `/gran/nchan` | −1–1, 1–48 | flock pan and channel count (legacy granular mapping) |
| `/mix/master` | 0–1 | PLAUD master level |
| `/mix/kick_gain`, `/mix/gran_gain`, `/mix/slice_gain` | 0–1 | kick, grain and slice levels |
| `/mix/grain_ms` | 10–400 | grain length (ms) |
| `/pad/kick` | — | trigger the kick |
| `/pad/sample` | 1–4 | play slice 1–4 of the grain source |
| `/aquarium/descriptors` | 10 floats, 0–1 | all flock descriptors (also sent one per address under `/aquarium/descriptor/<name>`) |

The descriptors are sent at about 15 Hz. `/mix/*` and `/pad/*` are sent only when a control is used.

## AKAI MPK mini 3

On the controller, set **PROG CHANGE** on and **bank A**. The mapping profile is chosen
automatically from the MIDI device name. If an AKAI MIDIMIX is also connected, it takes priority and keeps its own
mapping.

| Knob | Controls | | Pad | Action |
|---|---|---|---|---|
| K1 | agitation (noise) | | 1 | kick |
| K2 | grain length (10–400 ms) | | 2 | scare (1 s predator burst) |
| K3 | cohesion | | 3 | food on/off (centre of the screen) |
| K4 | number of fish (1–100) | | 4 | calm (clears food and predator) |
| K5 | slice gain | | 5–8 | slices 1–4 |
| K6 | grain gain | | | |
| K7 | kick gain | | | |
| K8 | PLAUD master | | | |

## Repository layout

- `src/`: the instrument.
  - `main.py` and `aquarium_boids/`: simulation, descriptors, OSC, MIDI, rendering.
  - `docs/`: technical notes, mostly in Italian.
  - `tools/send_control_test.py`: sends test controls to UDP port 7500.
- `max/`: the Shoal patches described above.
- `docs/archive/`: the original planning notes, in Italian, kept for the record.

## Credits

- Simone Zanetti, Alessandro Murru, and Rafael (music and training recordings).
- PLAUD by Błażej Kotowski.
- Developed at the Generative Music AI Workshop (UPF / MTG with The Sound of AI), Barcelona, July 2026.

## Limitations

- Tested on Windows only.
- The PLAUD device, the PLAUD model and all audio assets are not included. Without them, the Max
  side cannot be run as shown in the demo.
- The Max patches were built for standalone Max 9, not for Max for Live.

## License

To be agreed with co-authors.
