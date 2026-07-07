# Claude — Aquarium as Instrument (versione separata)

Implementazione **tenuta separata** dalla base ufficiale in `../Codex/`.
Serve come candidata di confronto e come laboratorio per lo strato di
**percepibilità** (eventi discreti sul pesce che li causa).

## Struttura

```
Claude/
  aquarium/
    config.py        parametri + CONTRATTO OSC congelato
    boids.py         simulazione boids vettorizzata (numpy) + World (controlli live)
    descriptors.py   descrittori collettivi 0..1 con smoothing EMA
    osc_out.py       emitter OSC (descrittori + eventi + stato mondo)
    __init__.py
  run_claude_version.py   visual pygame + controlli live
  smoke_test.py           test headless del core (no grafica, no rete)
  README.md
```

Il `.venv` è condiviso e sta nella root del progetto (`../.venv`).

## Avvio

Visual (richiede schermo):
```
cd Claude
../.venv/Scripts/python.exe run_claude_version.py
```
Test headless del core:
```
cd Claude
../.venv/Scripts/python.exe smoke_test.py
```

## Controlli live

| Input | Effetto |
|---|---|
| Mouse SX (tenuto) | sorgente di **cibo** → aggregazione (consonanza) |
| Mouse DX (tenuto) | **predatore** → fuga (dissonanza) |
| Q/A · W/S · E/D · R/F | food · predator · turbulence · density ± |
| T · H · O | scie · HUD · invio OSC on/off |
| SPACE · BACKSPACE · ESC | pausa · reset · esci |

## Contratto OSC (congelato — vedi `aquarium/config.py`)

Target default: `127.0.0.1:9000`.

**Descrittori continui** (float 0..1, a 30 Hz): `/aq/desc/{fish_count, mean_speed,
energy, center_x, center_y, spread, density, nearest_dist, coherence, turbulence}`

**Eventi discreti** (immediati — il mapping diretto per la percepibilità):
- `/aq/event/dart`  → `int id, float speed(0..1), float y(0..1)`
- `/aq/event/turn`  → `int id, float x(0..1), float y(0..1)`
- `/aq/event/collision` → `float x(0..1), float y(0..1), float strength(0..1)`

**Stato mondo** (echo dei controlli, on-change): `/aq/world/{food, predator, turbulence, density}`

> NB: namespace e porta **diversi** dalla base Codex (`:7400`, `/aquarium/...`, `/music/...`),
> apposta per poter far girare le due versioni in parallelo verso Max/Ableton.

## Differenze rispetto alla base ufficiale (Codex)

| | Codex (ufficiale) | Claude (questa) |
|---|---|---|
| Boids | OO (pygame Vector2) | vettorizzato numpy |
| Musica simbolica | **Markov completa** (accordi, sezioni, layer) | assente (solo descrittori + eventi) |
| Forma | manuale, tasti 1-6 | — |
| Link visual↔audio | flash su pesce casuale + `/aquarium/direct` continuo | **eventi sul pesce causale** (dart/turn/collision) |

## Prossimi passi (cosa farò qui)

1. Ricevitore OSC di test (stampa/plot) per sentire/vedere l'output senza DAW.
2. (se richiesto) Markov gerarchica: chain lenta accordo/sezione + chain veloce note
   condizionate sull'accordo corrente.
3. (se si sceglie questa base o si travasa) collegare gli eventi discreti a trigger
   percussivi nel setup del musicista.
