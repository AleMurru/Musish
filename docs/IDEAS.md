# Ideas and future work

Nothing on this page is implemented. Items are grouped by area. Known limitations of the current code come first; they are kept unchanged on purpose, because fixing them would change what Max receives.

## Known limitations (deliberately unchanged)

- **Send rate.** The 1/20 s gate is checked once per frame, so at 60 fps the descriptors go out about every 4th frame (≈ 15 Hz, not 20). A time accumulator would give a true 20 Hz, but it changes OSC timing.
- **Frame-rate dependence.** Smoothing is per frame, so it depends on the frame rate.
- **Redundant descriptors.**
  - `density` is `1 − nearest_distance`: two of the ten descriptors carry the same signal.
  - `cluster_count` is a grid-occupancy estimate, not real clustering.
- **Loudness** (`/plaud/loudness`) follows the number of fish, not the flock's behaviour.
- **Latent L2** (`/plaud/temp`) never goes below 0.2.
- **Unbounded keyboard weights.** The A/S/D/N keys have no upper limit; MIDI and UDP clip.
- **MIDI choice.** MIDI falls back silently to the first input device. A `--midi-name` / `--no-midi` option would make the choice explicit.
- **Port 7500.** If it is already taken, the program stops with an `OSError` instead of running without the control port.
- **Fish can leave the screen.** There is no hard border: very strong forces can push fish off screen.

## Sound and PLAUD

- **Artist ↔ flock crossfade** per parameter group, so the performer can take over any mapped parameter directly.
- **A PANIC control:** zero the distortion and waveshaping, centre the pan, stop the kick.
- **More PLAUD parameters from the flock.** Candidates:
  - spectral stretch ← `spread`;
  - spectral roll ← `center_y`;
  - components ← `density`.
- **Direct latent navigation** with the `/plaud/latent` vector (already sent, not routed). This needs the model's latent ranges.
- **Open questions for PLAUD:**
  - how to reduce the model's noise;
  - the dataset size and format for retraining on more of Rafael's recordings;
  - `nn~` CPU and latency under live load.
- **Granulator:**
  - use more than 16 of the 32 fish positions that are sent;
  - choose the grain region from the flock (e.g. `center_y` → region start).

## Descriptors

- Replace the redundant `density` / `nearest_distance` pair with an independent measure, e.g. vorticity (collective rotation) or speed variance (nervousness).
- Real clustering (DBSCAN or similar) instead of grid occupancy.
- A time-based or "one-euro" filter instead of the per-frame one-pole.

## The symbolic layer (`/music/*`)

The Markov generator still runs but is not part of the SynthFish performance. To make it musical:

- **A beat grid:** a 16th-note clock at the BPM. The rhythm chain then decides which steps sound. Today notes start at a continuous rate, so the rhythm chain is not audible.
- **Real harmony:** send a triad on a "pad" channel and the chord root as a bass note, instead of folding `degree + chord_degree` into one note.
- **Layers as instruments:** one MIDI channel per layer, to a DAW through a virtual MIDI port (loopMIDI on Windows).
- **Clock sync**, in steps: a fixed shared BPM → follow the DAW's MIDI clock → Ableton Link.
  - Caveat: Python Link bindings may lack wheels for Python 3.13.
  - Avoid Max and the DAW both listening for OSC on the same UDP port.
- **Better models:**
  - variable-order Markov / PPM;
  - a hierarchical chain (a slow form/harmony chain, plus a note chain conditioned on the chord);
  - a Factor Oracle;
  - condition rhythm on pitch.
- **Planned but never built:** `section_duration`, `novelty_pressure`, `repetition_memory`, `max_repetition`. Only `temperature` exists.

## Making the link visible

- Flash the fish that caused a sound event; today the flash lands on a random fish.
- On-screen cues for the audience that tie a gesture (food, predator) to its sound. The thermal look already shows the food glow and the predator rings.

## Other concepts from the early planning

- A **flocking orchestra:** sub-flocks as instrument sections.
- **The map as a score:** zones of the aquarium with their own sound worlds.
- **Fish with moods** that change their behaviour over time.
- **Geometric visuals** as an alternative to the thermal look.

## History

The early planning notes (in Italian) and the first technical guides are no longer on this branch. They are kept in the git history at commit `fcc93f6`:
- `docs/archive/` (planning, diary, roadmap, PLAUD meeting brief);
- `Codex/docs/` (the first OSC, MIDI and Max guides).

For example: `git show fcc93f6:docs/archive/PLAUD_meeting_brief.md`.
