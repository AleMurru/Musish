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

Max deve ascoltare su UDP `7400`. Patch minima:

```text
Codex/max/aquarium_receiver.maxpat
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

Messaggi principali:

```text
/aquarium/descriptors ...
/aquarium/direct ...
/music/note ...
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
