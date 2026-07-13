# PLAUD × Boids — Meeting Brief & Questions

Short brief to share with the PLAUD author, plus ordered questions to assess
whether/how PLAUD can be the live sound engine for our boids project.

---

## 1. Our project in one minute

We are building an **audiovisual generative instrument** for a generative-AI-music
workshop, aiming at a **live performance**. A digital aquarium of **boids** (flocking
fish) moves on screen; from their collective motion we extract numeric **descriptors**;
these descriptors drive sound. The musician does not play notes — they **shape the
ecosystem** (food, predators, cohesion, turbulence) and the sound follows the flock.

**The vision we want to test with you:** let the boids **navigate PLAUD's latent
space** in real time, so the flock "swims through" the artist's trained sonic world,
rendered live in Max via `nn~`.

## 2. How the system works right now

- **Simulation:** Python + pygame. ~100 boids, classic flocking (alignment / cohesion /
  separation) + noise, plus food/predator gestures.
- **Descriptors (all normalized 0–1), sent over OSC to Max at ~20 Hz:**

  | Descriptor | Meaning |
  |---|---|
  | `mean_speed` | average flock speed |
  | `energy` | motion energy |
  | `center_x`, `center_y` | flock centroid position |
  | `spread` | how dispersed the flock is |
  | `density` | how compact the flock is |
  | `direction_coherence` | how aligned the flock is |
  | `cluster_count` | rough number of sub-groups |

  These are **continuous, smoothed** control signals — a natural fit for a control/latent
  vector. We can change the count, rate, range, and OSC format on our side easily.

- **Live control (MIDI):** an **AKAI MIDIMIX**. Faders send MIDI CC → Python; each fader
  is mapped to an **ecosystem parameter** (alignment, cohesion, separation, noise,
  food, predator, density, section). Philosophy: **the musician sculpts the world, the
  sound follows the descriptors.**
- **Current sound layer (placeholder):** a symbolic Markov generator + a simple
  granular idea. This is exactly the part we hope to **replace/augment with PLAUD**.

## 3. The artist's sounds (what PLAUD was trained on)

Experimental / electronic / ambient material: synths, granular textures, effected
voices, field recordings. Files range from **~40 s to ~10 min**. Overall very
**atmospheric/textural**, and the current trained model sounds **quite noisy**.

---

## 4. Questions (ordered)

### A. Control interface — how do boids plug in?
1. At **runtime**, what exactly does the exported `nn~` model expect as input:
   **interpretable features** (pitch, loudness…), **abstract latents**, or a **hybrid**?
   How many control dimensions, and at what **control rate**?
2. What is the expected **range / normalization** of those inputs? Our descriptors are
   `0–1`, ~20 Hz — is that compatible, or should we match a specific rate/scale?
3. In `nn~`, do we drive synthesis via **`decode`** (feed a latent/control vector → audio)?
   Can you confirm the **inlets/outlets** layout of the exported model?

### B. Latent-space navigation (the core idea)
4. Can we **map the boid descriptors directly onto the latent/control dimensions** and
   let the flock navigate freely, **bypassing the Prior**? Is that a supported mode?
5. Alternatively, is the intended flow that the **transformer Prior generates** the
   control stream and we only **nudge/modulate** it? Can both modes coexist live?
6. Is the latent space **smooth and meaningful** (do nearby points sound related)? Any
   **"regions"** we should know about, so we can design the boid→latent mapping?
7. How many latent dims are practically **"playable"** (worth exposing to the flock)?

### C. Sound quality — reducing the noise
8. The current model is noisy. Is that mainly a **dataset** issue, a **training-length**
   issue, or a **loss/architecture** issue?
9. What are the highest-impact levers to get cleaner output: more **epochs**, the
   **adversarial** regime, different **losses** (MRSTFT weights), **dataset curation**,
   or `audio.chunk_duration_s` / sample-rate choices?
10. Any recommended **experiment config** (features-only / latent-only / hybrid) for
    ambient/textural material like ours?

### D. Dataset — size & format
11. Is **~30 minutes** of curated audio enough for a usable model, or should we push
    toward more? What's your practical minimum/sweet spot for "small personal datasets"?
12. Are **long files (5–10 min)** fine as-is, or should we **chunk** them first? Any
    guidance on `chunk_duration_s` and on mixing very short and very long files?
13. Does **heterogeneous** material (drones + voices + transients) train well as one
    model, or is it better to train **separate models per sound family**?

### E. Real-time / live feasibility in Max
14. Does the exported model run **real-time in Max** on a laptop (CPU), or is a **GPU**
    needed at inference? Typical **latency / buffer size** to expect?
15. Any constraints on **control-update rate** vs audio rate we must respect to avoid
    zippering/artifacts when the flock moves quickly?
16. **Multichannel** (`n_channels`) — could we use it for **stereo/spatial** output in
    the performance, driven by flock position/spread?
17. TorchScript vs ONNX — which do you recommend for the smoothest `nn~` path?

### F. Integration & the 30-hour window
18. Given a **live demo tomorrow evening (~30h)**, is it realistic to reach a **playable
    model + `nn~` in Max**, or should we treat PLAUD as the **v2 upgrade** on top of a
    granular fallback?
19. What's the **minimal end-to-end path** you'd suggest to hear *something* driven by
    our OSC control stream as fast as possible?
20. What do you need **from us** to make integration easy (control-vector spec, OSC
    format, a fixed number of normalized control channels, sample files)?

---

## 5. What we can offer on our side (to make it easy)

- A **stable stream of N normalized (0–1) control channels** at a chosen rate (default
  ~20 Hz), over OSC or mapped to `nn~` inlets — we can reshape this to match your
  ControlSpace (dimension count, rate, ranges).
- Live **MIDIMIX** control over the flock (so a human can steer the "navigation").
- Flexibility on our sound layer: we can **drop the symbolic/Markov path** and let
  PLAUD be the primary engine if the latent navigation works.
