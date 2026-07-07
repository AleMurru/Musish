# Guida rapida — usare Acquario Boids con Max

## Punto importante

Il file Max:

```text
Codex/max/aquarium_receiver.maxpat
```

**non visualizza il video dei boids**.  
Per ora il video/simulazione viene visualizzato dalla finestra Python/Pygame quando esegui:

```bash
cd Codex
python main.py
```

Max serve a ricevere i dati OSC e usarli per generare/modulare suono.

Quindi il setup attuale è:

```text
Python/Pygame = video + parametri + boids
Max = ricezione OSC + suono
```

---

## 1. Apri Max

Apri:

```text
Codex/max/aquarium_receiver.maxpat
```

La patch ascolta sulla porta UDP:

```text
7400
```

Dentro la patch trovi:

```text
udpreceive 7400
oscparse
route aquarium music
```

Questi oggetti ricevono e separano i messaggi OSC provenienti da Python.

---

## 2. Avvia la simulazione Python

Da terminale:

```bash
cd Codex
.venv\Scripts\activate
python main.py
```

Se non hai ancora installato le dipendenze:

```bash
pip install -r requirements.txt
```

Dovrebbe aprirsi una finestra con i boids/pesci.

---

## 3. Controlla se Max riceve i dati

Apri la **Max Console**.

Dovresti vedere messaggi stampati tipo:

```text
descriptors: ...
direct: ...
music_note: ...
music_rest: ...
```

Se vedi questi messaggi, Python e Max stanno comunicando correttamente.

---

## 4. Come giocare con i parametri

I parametri per ora si controllano dalla finestra Python, non da Max.

Clicca sulla finestra della simulazione e usa:

| Controllo | Effetto |
|---|---|
| `UP` / `DOWN` | aumenta/diminuisce `density_fader` |
| `1`-`6` | cambia sezione musicale: intro/growth/dense/chaos/release/outro |
| `A` / `Z` | aumenta/diminuisce alignment |
| `S` / `X` | aumenta/diminuisce cohesion |
| `D` / `C` | aumenta/diminuisce separation |
| `N` / `M` | aumenta/diminuisce noise |
| mouse sinistro | attrattore/cibo |
| mouse destro | predatore/repulsore |
| `SPACE` | pausa |
| `R` | reset boids |
| `ESC` | esci |

I valori principali appaiono anche scritti in alto nella finestra video.

---

## 5. Messaggi più utili per Max

### Modulazione continua

```text
/aquarium/direct mean_speed energy center_x center_y density spread density_fader
```

Usalo per modulare parametri audio in tempo reale:

- `mean_speed` → filtro, tremolo, densità ritmica;
- `energy` → ampiezza/velocity;
- `center_x` → panning;
- `center_y` → brightness/filtro;
- `density` → compattezza/tensione;
- `spread` → riverbero/range;
- `density_fader` → quantità di eventi o mix.

### Eventi musicali

```text
/music/note event_id degree octave duration_beats velocity layer_id layer_name chord_degree section_id
```

Questi eventi sono simbolici.  
In Max devi convertire `degree + chord_degree + octave` in una nota MIDI o frequenza.

Formula consigliata:

```text
minor_scale = [0, 2, 3, 5, 7, 8, 10]
midi = root + minor_scale[(degree + chord_degree) % 7] + 12 * octave
```

Esempio:

```text
root = 57  // A minor
```

---

## 6. Se non funziona

Controlla:

1. Python è avviato con `python main.py`?
2. Max patch è aperta?
3. La porta è `7400`?
4. La Max Console è aperta?
5. Firewall Windows ha bloccato Python?

---

## Stato attuale

Attualmente la patch Max è solo un **receiver/debug patch**.  
Serve a verificare che i dati arrivino.

Il prossimo step sarà creare una patch Max sonora vera, ad esempio:

```text
/music/note → conversione degree→MIDI → synth/poly~
/aquarium/direct → modulazione filtri/riverbero/panning
```
