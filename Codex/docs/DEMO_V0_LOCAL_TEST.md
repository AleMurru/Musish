# Demo v0 — test locale prima del musicista

Obiettivo: verificare sul nostro PC che i descriptor e i nuovi controlli demo arrivino bene, prima di passare il sistema al musicista.

## 1. Test matematico dei descriptor

Non richiede Max, MIDIMIX o finestra Pygame.

```bash
cd Codex
.venv\Scripts\python.exe tools/test_descriptors.py
```

Risultato atteso:

```text
OK: descriptor sanity checks passed.
```

Questo controlla che:

- un branco allineato dia `direction_coherence` alto;
- un branco con direzioni opposte dia `direction_coherence` basso;
- un branco compatto dia `density` alta e `spread` basso;
- un branco disperso dia `spread` alto;
- `center_x` distingua sinistra/destra;
- `mean_speed` distingua lento/veloce.

## 2. Test live senza Max

Usiamo un monitor UDP al posto di Max.

Terminale 1:

```bash
cd Codex
.venv\Scripts\python.exe tools/udp_monitor.py
```

Terminale 2:

```bash
cd Codex
.venv\Scripts\python.exe main.py
```

Il monitor deve stampare messaggi come:

```text
direct      mean_speed=... | energy=... | center_x=... | center_y=... | density=... | spread=... | density_fader=...
descriptors fish_count=... | mean_speed=... | ... | direction_coherence=... | cluster_count=...
performance alignment_chaos=... | grain_density=... | noise_distortion=... | scene_id=...
```

Nota: `udp_monitor.py` usa la porta `7401`, quindi durante questo test non deve essere aperta una patch Max con `[netreceive -u 7401]`.

## 3. Test dei fader senza MIDIMIX

Se il MIDIMIX non è collegato, possiamo simulare i controlli via UDP verso Python.

Con `main.py` aperto, in un terzo terminale:

```bash
cd Codex
.venv\Scripts\python.exe tools/send_demo_control_test.py
```

Risultato atteso:

- `alignment_chaos 0.0`: i pesci diventano più ordinati / stessa direzione;
- `alignment_chaos 1.0`: i pesci diventano più caotici e dispersi;
- `grain_density` cambia nel messaggio `performance`;
- `noise_distortion` cambia nel messaggio `performance` e aumenta la turbolenza dei pesci;
- `scene_id` cambia nel messaggio `performance`.

## 4. Test con MIDIMIX reale

Quando il MIDIMIX è collegato:

```bash
cd Codex
.venv\Scripts\python.exe main.py
```

Muovere i fader:

| Fader | Atteso |
|---|---|
| F1 | `alignment_chaos`: basso = ordine/stessa direzione, alto = caos/dispersione |
| F2 | `grain_density` cambia nel messaggio `performance` |
| F3 | `noise_distortion` cambia e aumenta il caos visivo |
| F4 | `cohesion_weight` |
| F5 | `separation_weight` |
| F6 | `food_amount` |
| F7 | `predator_amount` |
| F8 | `scene_id` |

## 5. Criterio per passare al musicista

Possiamo passare al musicista quando:

```text
[ ] test_descriptors.py passa
[ ] udp_monitor.py riceve direct
[ ] udp_monitor.py riceve performance
[ ] F1 o send_demo_control_test cambia chiaramente ordine/caos dei pesci
[ ] F2/F3/F8 arrivano correttamente nel messaggio performance
```
