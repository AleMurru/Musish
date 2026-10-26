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
midi event_id midi_note velocity duration_ms layer_id section_id
note event_id degree octave duration_beats velocity layer_id layer_name chord_degree section_id
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

## Eventi musicali simbolici

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
