# Integration — Boids → Granulator (and → PLAUD nn~)

Goal: let flock **movement** and **events** drive the granular engine
(`granulateur_stereo_v5`, 48-ch `mc.gen~`) — starting with **Pan, Density,
Noise/Distortion** — and, as a next step, drive the **PLAUD `nn~` decode**
(4 latents + DDSP params). Priority: feasibility for the live demo.

## What already exists (so we only wire, not build)

- **Python boids** already send descriptors over OSC to Max, ~20 Hz, all
  normalized `0..1`, already low-pass smoothed:
  - `/aquarium/descriptor/<name>` (one address per descriptor), and
  - `/aquarium/direct  mean_speed energy center_x center_y density spread density_fader`
  - plain FUDI fallback on UDP **7401** (`descriptors ... ;`, `direct ... ;`) for
    Max without `[oscparse]`.
  - OSC target: `127.0.0.1:7400`.
- **Granulator** (`VF_gran_stereo`) already exposes **Pan / Density /
  Noise-Distorsion** + granular params.
- **PLAUD** already runs: `nn~ RafaelV1.ts decode 8192`, fed by
  `mc.receive~ ---final_latents 4` (4 latents), plus param receives
  (`waveshaping`, `limit_components`, `spectral_roll`, `spectral_stretch`,
  `postnet_mix`).

---

## STEP 1 — Boids → Granulator (immediate, zero new Python)

Map the three target params from descriptors we already send. All sources are
`0..1` and already smoothed on our side.

| Granulator param | Boid source (existing OSC) | Scaling in Max |
|---|---|---|
| **Pan** | `/aquarium/descriptor/center_x` | `pan = x*2 - 1`  (0..1 → -1..1) |
| **Density** → `probability [0/100]` | `/aquarium/descriptor/density` | `prob = density*100` |
| **Density** → `density nb of channel` (1..48) | `/aquarium/descriptor/density` | `nch = 1 + round(density*47)` |
| **Noise / Distorsion** | chaos (see below) | `0..1`, optionally curve `^2` |
| *(bonus)* depth/brightness | `/aquarium/descriptor/center_y` | filter cutoff / fadein |

**Density behaviour requested:** min → a single granulated sound, max → full
spectrum. Drive **both** `probability` and `density nb of channel` from
`density` so low = sparse/mono-ish, high = dense across the 48 channels.

**"Chaos" signal for Noise/Distortion.** A chaotic event (predator, flock
breaking up) should push distortion. Two options:
- *Zero-Python:* compute in Max from what we already send —
  `chaos = clamp( predator_amount  +  (1 - direction_coherence) )`
  (`predator_amount` is field #9 of `/aquarium/controls`; `direction_coherence`
  is `/aquarium/descriptor/direction_coherence`).
- *Nicer (tiny Python add):* we emit a dedicated `/aquarium/chaos` float `0..1`
  so the patch just reads one number. Say the word and we add it.

### RECOMMENDED: pre-scaled `/gran/*` messages (least Max work)

`main.py` now also sends **already-scaled** values, so the Max patch does **no
math** — just route them into the granulator inlets:

```text
/gran/pan      float  -1 .. 1     -> Pan
/gran/density  float   0 .. 100   -> probability [0/100]
/gran/nchan    int     1 .. 48    -> density nb of channel
/gran/noise    float   0 .. 1     -> Noise / Distorsion
/gran          list [pan density nchan noise]   (bundled convenience)
```

Meaning: few fish -> density ~1, nchan 1 (a single grain voice); full flock ->
density 100, nchan 48 (full spectrum). `noise` rises with agitation, predator and
flock disorder. Sent ~20 Hz on OSC `7400` and as FUDI `gran ... ;` on `7401`.

Minimal Max receiver:

```
[udpreceive 7400]
|
[oscparse]
|
[route /gran/pan /gran/density /gran/nchan /gran/noise]
   |         |            |            |
[line~ 20] [line 30]   (int)       [line~ 30]
   |->Pan    |->probability |->nb channel  |->Noise/Distorsion
```

### Max wiring (receiver side, sketch) — raw descriptors (alternative)

```
[udpreceive 7400]
|
[oscparse]
|
[route /aquarium/descriptor/center_x /aquarium/descriptor/density /aquarium/descriptor/direction_coherence]
   |            |               |
 center_x     density        coherence
   |            |               |
[* 2.][- 1.]  [* 100.]        [!- 1.]        <- scale to param ranges
   |            |               |
[line~ 10]   [line~ 20]      [line~ 30]       <- 10-50 ms smoothing (anti-zipper)
   | -> Pan     | -> probability / nb channels | -> Noise/Distortion
```

(FUDI fallback: `[udpreceive 7401] -> [route descriptors direct] -> [unpack ...]`.)

Notes:
- Our descriptors are already smoothed, but keep a short `line~` (10-50 ms) on
  the param side to avoid zippering on fast moves.
- Keep the update rate at ~20 Hz (aggregate, not per-boid). No need for more.

---

## STEP 2 — Boids → PLAUD `nn~` (next, still just sending values)

The `nn~` patch already receives 4 latents and named params. Driving PLAUD from
the flock = sending numbers to those receives (no patch surgery).

**READY: `/plaud/*` messages (the flock as a moving point in latent space).**
`main.py` now sends the flock position as a latent-navigation point, ~20 Hz,
centered to -1..1 (0 = middle of the space):

```text
/plaud/x       float -1..1        flock horizontal  -> latent dim 0
/plaud/y       float -1..1        flock vertical    -> latent dim 1
/plaud/xy      [x y]
/plaud/latent  [x y z w]          ready 4-vector (z=spread, w=mean_speed)
/plaud/loudness float 0.6..1.4    fish_count -> loudness (partial window; artist keeps master)
/plaud/temp     float 0..1        agitation  -> synthesis temperature/chaos
```

Latents (ch1..4) navigate the sound; `loudness`/`temp` are DSP params. Map only a
few, leave the rest (highs, feedback, shape, partials, l1/l2) to the artist by hand.

Max side: route `/plaud/x` `/plaud/y` (+ optionally z,w) -> `[mc.pack~ 4]` ->
`s ---final_latents`. **Rescale to the model's latent range**: our values are
-1..1; RAVE-style latents are ~N(0,1) (roughly -3..3), so multiply by ~2-3 (a
`[* 2.5]` on each) and add a `[line~ 30]` for smooth motion. The exact range is
the one open question for the PLAUD author (see PLAUD_meeting_brief.md).

**Latents (the "fish navigate the latent space" idea — already reachable):**
send 4 values into `---final_latents`. Suggested first mapping:

| Latent | Boid source | Note |
|---|---|---|
| latent 0 | `center_x` | horizontal position |
| latent 1 | `center_y` | vertical position |
| latent 2 | `spread` | flock dispersion |
| latent 3 | `mean_speed` | flock energy |

⚠️ Ask PLAUD author for the **expected latent range** (often not 0..1 — could be
~ -3..3). Rescale our `0..1` accordingly before sending. This is the single most
important unknown for latent navigation.

**DDSP params (artist AND/OR flock can drive them live):**

| PLAUD param (receive) | Suggested driver |
|---|---|
| `waveshaping` | chaos / predator (more chaos → more shaping) |
| `limit_components` | density (compact flock → fuller spectrum) |
| `spectral_stretch` | spread |
| `spectral_roll` | center_y (brightness) |
| `postnet_mix` | artist fader (taste control) |

---

## Artist vs flock — the mix layer (requested)

Every mappable param should support **both** the flock and the artist. Simplest
scheme in Max, per parameter:

```
boids_value ---\
                >--[* w_boids]--\
artist_value --/                 [+ ]--> param
                   [* w_artist]--/
```

- `w_boids` / `w_artist` = two faders (or one crossfade) per param group.
- The **MIDIMIX already controls the ecosystem** (flock behaviour), so the artist
  is *already* shaping the sound indirectly; this adds *direct* override on the
  audio params on top.
- Add a **PANIC**: one button that zeroes Noise/Distortion (and waveshaping) and
  resets pan to center — for safety during the live set.

---

## Feasibility / risks (30h live demo)

- **Step 1 (granular): LOW risk.** Both ends exist; it's an afternoon of Max
  wiring + our OSC (already flowing). This is the demo backbone. Do it first,
  then **record a backup**.
- **Step 2 (PLAUD latents): MEDIUM.** Also just sending values, but: (1) confirm
  latent range, (2) model is currently noisy, (3) verify `nn~` CPU/latency on the
  M4 under load. Treat as the upgrade layer, not the backbone.
- **Raw artist sounds in parallel:** trivial — just more granulator voices / a
  second sample bank; no new plumbing.

## Open questions to confirm

1. Who owns/edits the granulator patch, and can they add the `[udpreceive 7400]`
   receiver block? (If yes, Step 1 needs nothing from us.)
2. PLAUD `---final_latents` expected value range?
3. Do the granulator's `Pan/Density/Noise` inlets take `0..1` / `-1..1` / `0..100`
   exactly as assumed above?
