# OSC contract — Acquario Boids → Max

Default OSC target:

```text
host: 127.0.0.1
port: 7400
```

Fallback Max/FUDI target, senza `oscparse`:

```text
host: 127.0.0.1
port: 7401
Max object: netreceive -u 7401
```

Control input Max/MIDIMAX -> Python:

```text
host: 127.0.0.1
port: 7500
format: control parameter value;
example: control density_fader 0.75;
```

## Plain UDP fallback senza oscparse

In parallelo all'OSC, Python invia anche messaggi testuali compatibili con Max `netreceive`:

```text
direct mean_speed energy center_x center_y density spread density_fader
performance alignment_chaos grain_density noise_distortion scene_id
clock kind index step step_in_bar beat_in_bar bar bpm
chord root third fifth chord_degree scene_id bar
note voice midi_note velocity duration_ms degree octave layer_id scene_id chord_degree event_id
hit voice sample_id velocity duration_ms scene_id event_id
midi event_id midi_note velocity duration_ms layer_id section_id
note event_id degree octave duration_beats velocity layer_id layer_name chord_degree section_id  # legacy v1 only
rest event_id duration_beats section_id
```

Quindi in Max puoi usare:

```text
netreceive -u 7401
|
route direct midi note rest
```

Questa è la soluzione consigliata se `oscparse` non esiste nella tua installazione di Max.

## Descriptor continui

Inviati a ~20 Hz.

```text
/aquarium/descriptors fish_count mean_speed energy center_x center_y spread density nearest_distance direction_coherence cluster_count
```

Tutti i valori sono float normalizzati `0..1`.

Sono inviati anche come indirizzi separati:

```text
/aquarium/descriptor/mean_speed value
/aquarium/descriptor/density value
...
```

## Controlli performativi

```text
/aquarium/controls density_fader alignment cohesion separation noise food_strength predator_strength food_amount predator_amount section_id
/aquarium/section section_id section_name
```

## Mapping diretto per Max

Questo messaggio è pensato per modulazioni immediate, così il pubblico percepisce il link visuale/sonoro senza aspettare la Markov chain.

```text
/aquarium/direct mean_speed energy center_x center_y density spread density_fader
```

Uso suggerito in Max:

- `mean_speed` → densità trigger, filtro, tremolo;
- `energy` → velocity/ampiezza;
- `center_x` → panning;
- `center_y` → brightness/ottava;
- `density` → consonanza/compattezza;
- `spread` → range o riverbero;
- `density_fader` → mix tra drone e granularità.

## Controlli performance demo v0

Messaggio dedicato alla demo sample/granular in Max:

```text
/aquarium/performance alignment_chaos grain_density noise_distortion scene_id
```

Fallback plain UDP:

```text
performance alignment_chaos grain_density noise_distortion scene_id
```

Campi:

| Campo | Range | Uso |
|---|---:|---|
| `alignment_chaos` | `0..1` | `0` = branco ordinato/stessa direzione, `1` = dispersione caotica |
| `grain_density` | `0..1` | densità di grani/trigger/sample in Max |
| `noise_distortion` | `0..1` | quantità di noise/distorsione; in Python aumenta anche il caos del movimento |
| `scene_id` | `0..5` | scena, banco sample o preset Max |

## Markov v2 — output simbolico quantizzato

La Markov v2 è il nuovo output musicale consigliato per Max. È quantizzata su griglia di sedicesimi e usa Python come master clock.

In Max, con fallback plain UDP:

```text
[netreceive -u 7401]
|
[route direct performance clock chord note hit]
```

### `clock`

```text
clock kind index step step_in_bar beat_in_bar bar bpm
```

Esempi:

```text
clock step 128 128 0 0 8 120;
clock beat 32 128 0 0 8 120;
clock bar 8 128 0 0 8 120;
```

Campi principali:

| Campo | Significato |
|---|---|
| `kind` | `step`, `beat` o `bar` |
| `step` | sedicesimo globale |
| `step_in_bar` | posizione 0..15 nella battuta |
| `beat_in_bar` | beat 0..3 nella battuta |
| `bar` | battuta globale |
| `bpm` | tempo corrente |

### `chord`

```text
chord root third fifth chord_degree scene_id bar
```

Esempio:

```text
chord 57 60 64 0 1 8;
```

Max può usare queste tre note per un pad, una texture armonica o per scegliere sample intonati.

### `note`

```text
note voice midi_note velocity duration_ms degree octave layer_id scene_id chord_degree event_id
```

Esempi:

```text
note bass 45 90 500 0 -1 1 1 0 42;
note lead 69 84 250 2 1 2 1 0 43;
```

`voice` iniziali:

```text
bass
lead
keys
```

In Max:

```text
[route note]
|
[route bass lead keys]
```

### `hit`

```text
hit voice sample_id velocity duration_ms scene_id event_id
```

Esempio:

```text
hit glitch 3 100 120 2 44;
```

`voice` iniziali:

```text
grain
glitch
noise
```

Questo messaggio è pensato per sample brevi, one-shot, rumori e micro-eventi.

## Eventi musicali simbolici legacy v1

Evento generico:

```text
/music/event event_id event_type degree octave duration_beats velocity layer_id chord_degree section_id
```

Dove:

```text
event_type: 1 = note, 0 = rest
layer_id: 0 drone, 1 bass, 2 lead, 3 perc, 4 granular, 5 noise
section_id: 0 intro, 1 growth, 2 dense, 3 chaos, 4 release, 5 outro
```

Evento nota, più comodo da routare in Max:

```text
/music/note event_id degree octave duration_beats velocity layer_id layer_name chord_degree section_id
```

Evento MIDI già convertito, utile per prototipi sonori veloci in Max:

```text
/music/midi event_id midi_note velocity duration_ms layer_id section_id
```

Questo messaggio viene generato usando `ROOT_MIDI` e `SCALE_INTERVALS` in `aquarium_boids/config.py`.

Evento pausa:

```text
/music/rest event_id duration_beats section_id
```

## Nota musicale importante

`degree` e `chord_degree` non sono note MIDI assolute. Sono gradi simbolici. In Max conviene convertirli in MIDI secondo scala/tonalità scelta dal musicista.

Esempio scala minore naturale con root MIDI 57 = A:

```text
minor_scale = [0, 2, 3, 5, 7, 8, 10]
midi = root + minor_scale[(degree + chord_degree) % 7] + 12 * octave
```
