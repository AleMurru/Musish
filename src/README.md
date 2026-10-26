# Acquario generativo musicale — Boids + Max

MVP del progetto: simulazione boids in Python/Pygame, descriptor normalizzati, generatore simbolico Markov e invio OSC a Max.

## Setup

Da ora tutto il lavoro operativo è dentro la cartella `Codex`.

```bash
cd Codex
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Python invia due flussi:

```text
7400 = OSC standard
7401 = plain UDP / fallback Max
```

Patch disponibili:

```text
Codex/max/aquarium_osc_symbolic.maxpat         # OSC simbolico: usa /music/note, non /music/midi
Codex/max/aquarium_receiver.maxpat             # debug/ricezione OSC, richiede oscparse
Codex/max/aquarium_sound_preview.maxpat        # primo suono OSC, richiede oscparse
Codex/max/aquarium_netreceive_sound.maxpat     # fallback se oscparse non esiste
Codex/max/aquarium_netreceive_sound_v2.maxpat  # fallback: tono di default + debug raw
Codex/max/aquarium_netreceive_mapped.maxpat    # plain UDP senza unpack: drone + density + blip Markov
Codex/max/audio_test.maxpat                    # test audio Max indipendente da Python/OSC
Codex/max/midimax_control_template.maxpat      # fallback Max -> Python per controllare boids con MIDIMIX/MIDIMAX
```

## Controlli

- `UP/DOWN`: aumenta/diminuisce `density_fader`
- `1..6`: sezione musicale `intro/growth/dense/chaos/release/outro`
- `A/Z`: alignment + / -
- `S/X`: cohesion + / -
- `D/C`: separation + / -
- `N/M`: noise + / -
- mouse sinistro: food/attractor
- mouse destro: predator/repeller
- `SPACE`: pausa
- `R`: reset flock
- `ESC`: esci

## OSC

Contratto completo: [`docs/OSC_CONTRACT.md`](docs/OSC_CONTRACT.md).

Guida per il musicista: [`docs/MUSICIAN_GUIDE.md`](docs/MUSICIAN_GUIDE.md).

Guida MIDIMAX/MIDIMIX via Max: [`docs/MIDIMAX_CONTROL.md`](docs/MIDIMAX_CONTROL.md).

Guida MIDIMIX diretto in Python: [`docs/MIDIMIX_DIRECT.md`](docs/MIDIMIX_DIRECT.md).

Guida pratica di test workflow: [`docs/WORKFLOW_TEST_GUIDE.md`](docs/WORKFLOW_TEST_GUIDE.md).

Messaggi principali:

```text
/aquarium/descriptors ...
/aquarium/direct ...
/music/note ...
/music/midi ...        # ancora disponibile, ma non usato dalla patch OSC simbolica
/music/rest ...
```

## Riferimento boids usato come ispirazione

Repository analizzato:

- https://github.com/Shivank1006/Bird-Flocking-Simulation

Elementi presi come base concettuale:

- tre forze classiche: alignment, cohesion, separation;
- pesi performativi per le tre forze;
- steering limitato da `max_force` e `max_speed`;
- boid disegnato come triangolo orientato secondo la velocità.

Modifiche introdotte per il nostro progetto:

- implementazione Python/Pygame invece di p5.js;
- output OSC verso Max;
- descriptor normalizzati 0-1;
- filtro low-pass sui descriptor;
- Markov chain simbolica per eventi musicali;
- controllo `density_fader`;
- gesti mouse `food/predator`;
- logging CSV in `logs/`.
