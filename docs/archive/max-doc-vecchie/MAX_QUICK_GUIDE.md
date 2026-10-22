# Guida rapida — usare Acquario Boids con Max

## Punto importante

I file Max disponibili sono:

```text
Codex/max/aquarium_receiver.maxpat          # solo debug/ricezione OSC, richiede oscparse
Codex/max/aquarium_sound_preview.maxpat     # primo suono OSC, richiede oscparse
Codex/max/aquarium_netreceive_sound.maxpat     # fallback senza oscparse
Codex/max/aquarium_netreceive_sound_v2.maxpat  # fallback consigliato: tono di default + debug raw
Codex/max/audio_test.maxpat                    # test solo audio, senza Python
```

Max **non visualizza il video dei boids**.  
Il video/simulazione viene visualizzato dalla finestra Python/Pygame quando esegui:

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

Se Max dice che `oscparse` non esiste, apri questa patch:

```text
Codex/max/aquarium_netreceive_sound_v2.maxpat
```

Questa patch non usa OSC parsing: riceve messaggi testuali Max/FUDI via `netreceive -u 7401`. Inoltre contiene un tono di default, quindi se `ezdac~` è acceso dovresti sentire qualcosa anche prima che arrivino dati.

Se invece il tuo Max supporta `oscparse`, puoi aprire:

```text
Codex/max/aquarium_sound_preview.maxpat
```

Se vuoi solo controllare i messaggi OSC, apri invece:

```text
Codex/max/aquarium_receiver.maxpat
```

Le porte sono:

```text
7400 = OSC standard, per patch con oscparse
7401 = plain UDP / Max messages, per patch con netreceive senza oscparse
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
music_midi: ...
music_rest: ...
```

Se vedi questi messaggi, Python e Max stanno comunicando correttamente.

Nella patch `aquarium_sound_preview.maxpat`, clicca su `ezdac~` per accendere l'audio. Sentirai un drone semplice controllato da velocità/energia dei boids.

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

Per prototipi Max rapidi ora esiste anche:

```text
/music/midi event_id midi_note velocity duration_ms layer_id section_id
```

Questo messaggio è già convertito in MIDI note e viene mandato anche alla sezione `makenote -> noteout` nella patch `aquarium_sound_preview.maxpat`.

Se vuoi lavorare in modo più musicale e flessibile, usa ancora `/music/note` e converti `degree + chord_degree + octave` in una nota MIDI o frequenza.

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

Ora ci sono due livelli:

1. `aquarium_receiver.maxpat` — debug/ricezione OSC.
2. `aquarium_sound_preview.maxpat` — primo suono funzionante: drone controllato da `/aquarium/direct` + MIDI out opzionale da `/music/midi`.

Il prossimo step sarà creare una patch Max più musicale con:

```text
/music/midi o /music/note → synth/poly~
/aquarium/direct → filtri/riverbero/panning
layer_id → strumenti diversi
```
