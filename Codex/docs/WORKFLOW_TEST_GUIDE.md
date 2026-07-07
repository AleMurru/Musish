# Guida pratica — test workflow MIDIMIX → Python/main.py → Max

Questa guida serve per verificare il workflow completo:

```text
MIDIMIX
↓
main.py / boids / Markov
↓
Max
↓
suono
```

Obiettivo del test:

1. verificare che Python legga il MIDIMIX;
2. verificare che i fader modifichino davvero i boids in `main.py`;
3. verificare che Python mandi dati a Max;
4. verificare che Max renderizzi suono dai dati ricevuti.

---

# 0. Setup iniziale

Collega MIDIMIX al computer.

Importante: per questo workflow, **Max non deve usare direttamente MIDIMIX**.  
Il controller deve essere aperto da Python.

Quindi, prima del test:

- chiudi eventuali patch Max che leggono MIDIMIX con `ctlin`;
- chiudi Ableton/DAW se stanno usando MIDIMIX;
- lascia aperto solo il terminale e poi Max come renderer audio.

---

# 1. Avvia Python

Da terminale:

```bash
cd Codex
python main.py
```

Dovresti vedere la finestra dei boids.

Nel terminale cerca righe tipo:

```text
[midi] input device 2: MIDIMIX (...)
[midi] listening to MIDIMIX [2]
[midi] debug enabled: move MIDIMIX faders to print CC/value
```

## Se vedi questo

Python ha aperto MIDIMIX correttamente.

## Se NON vedi questo

Possibili cause:

1. MIDIMIX non è collegato;
2. MIDIMIX è già aperto da Max/Ableton/altro software;
3. il device ha un nome diverso da `MIDIMIX`;
4. pygame/midi non vede il dispositivo.

Nel terminale Python stampa comunque i device MIDI disponibili:

```text
[midi] input device X: nome_device
```

Se il nome è diverso, bisogna aggiornare in:

```text
Codex/aquarium_boids/config.py
```

la variabile:

```python
MIDI_INPUT_NAME = "MIDIMIX"
```

usando una parte del nome reale stampato nel terminale.

---

# 2. Test: i fader arrivano a Python?

Muovi lentamente un fader del MIDIMIX.

Nel terminale dovresti vedere qualcosa tipo:

```text
[midi] cc=19 value=87 channel=1
[midi-map] cc=19 -> density_fader = 0.685
```

Ci sono due livelli di messaggi:

## Messaggio 1 — MIDI grezzo

```text
[midi] cc=19 value=87 channel=1
```

Significa:

- `cc=19` = numero del controllo MIDI;
- `value=87` = posizione del fader, da 0 a 127;
- `channel=1` = canale MIDI.

## Messaggio 2 — Mapping applicato

```text
[midi-map] cc=19 -> density_fader = 0.685
```

Significa che quel CC è già mappato a un parametro di `main.py`.

---

# 3. Se vedi solo `[midi] cc=...` ma non `[midi-map]`

Significa che Python riceve il fader, ma quel CC non è ancora mappato.

Apri:

```text
Codex/aquarium_boids/config.py
```

Trova:

```python
MIDI_CC_MAPPING = {
    19: ("density_fader", 0.0, 1.0, False),
    20: ("alignment_weight", 0.0, 3.0, False),
    ...
}
```

Se il tuo primo fader stampa, per esempio:

```text
[midi] cc=7 value=64 channel=1
```

allora modifica la tabella così:

```python
MIDI_CC_MAPPING = {
    7: ("density_fader", 0.0, 1.0, False),
    ...
}
```

Poi salva e riavvia:

```bash
python main.py
```

---

# 4. Mappatura consigliata MIDIMIX → main.py

| Fader | Parametro Python | Range | Effetto visuale/musicale |
|---|---|---:|---|
| Fader 1 | `density_fader` | 0..1 | più/meno eventi Markov |
| Fader 2 | `alignment_weight` | 0..3 | branco più allineato |
| Fader 3 | `cohesion_weight` | 0..3 | branco più compatto |
| Fader 4 | `separation_weight` | 0..4 | boids più distanti |
| Fader 5 | `noise_weight` | 0..1.5 | turbolenza/caos |
| Fader 6 | `food_strength` | 0..3 | forza attrattore mouse sinistro |
| Fader 7 | `predator_strength` | 0..3 | forza repulsore mouse destro |
| Fader 8 | `section_id` | 0..5 | sezione musicale |

Le sezioni sono:

```text
0 intro
1 growth
2 dense
3 chaos
4 release
5 outro
```

---

# 5. Verifica visuale in `main.py`

Nella finestra dei boids, in alto, ci sono i valori correnti.

Muovendo i fader dovresti vedere cambiare:

```text
density_fader
alignment
cohesion
separation
noise
food_strength
predator_strength
section
```

Test consigliati:

## Test A — Noise

Muovi il fader mappato a:

```text
noise_weight
```

Effetto atteso:

- basso = movimento più fluido;
- alto = movimento più nervoso/caotico.

## Test B — Cohesion

Muovi:

```text
cohesion_weight
```

Effetto atteso:

- basso = branco disperso;
- alto = boids più aggregati.

## Test C — Separation

Muovi:

```text
separation_weight
```

Effetto atteso:

- basso = boids più vicini;
- alto = boids si evitano di più.

## Test D — Density fader

Muovi:

```text
density_fader
```

Effetto atteso:

- basso = pochi eventi Markov;
- alto = più eventi Markov, più densità sonora.

---

# 6. Collegare Max come renderer

Quando il controllo dei boids funziona, apri Max.

Patch stabile consigliata:

```text
Codex/max/aquarium_netreceive_mapped.maxpat
```

Questa usa:

```text
netreceive -u 7401
```

Alternativa OSC simbolica:

```text
Codex/max/aquarium_osc_symbolic.maxpat
```

Questa usa:

```text
udpreceive 7400
```

Usa questa solo se nella tua installazione Max riceve OSC già leggibile.

---

# 7. Test Max audio

In Max:

1. premi `CTRL + E` per bloccare la patch;
2. clicca su `ezdac~`;
3. apri la Max Console.

Con `aquarium_netreceive_mapped.maxpat` dovresti vedere messaggi tipo:

```text
RAW_7401: direct ...
DIRECT_LIST: ...
MIDI_LIST: ...
```

Se li vedi, significa:

```text
Python → Max funziona
```

---

# 8. Test completo MIDIMIX → Python → Max

Ora fai questo:

1. lascia aperto `python main.py`;
2. lascia aperta la patch Max;
3. accendi `ezdac~`;
4. muovi i fader MIDIMIX.

Cosa deve succedere:

```text
MIDIMIX fader
↓
Python terminal: [midi] / [midi-map]
↓
boids cambiano comportamento nella finestra
↓
Max Console riceve direct/note/midi
↓
il suono cambia
```

Esempi:

| Fader | Effetto atteso su Max |
|---|---|
| `density_fader` | più eventi/blip Markov |
| `noise_weight` | suono più instabile perché i boids si agitano |
| `cohesion_weight` | cambia density, quindi cambia secondo oscillatore |
| `section_id` | cambia carattere/layer degli eventi |
| `predator_strength` + mouse destro | fuga più forte, energia più alta |

---

# 9. Diagnostica veloce

## Caso 1 — I boids si muovono ma MIDIMIX non controlla nulla

Controlla terminale Python.

Se non vedi:

```text
[midi] cc=...
```

allora Python non sta leggendo MIDIMIX.

Soluzioni:

- chiudi Max/Ableton se stanno usando MIDIMIX;
- scollega/ricollega MIDIMIX;
- controlla `MIDI_INPUT_NAME` in `config.py`.

## Caso 2 — Vedi `[midi] cc=...` ma non `[midi-map]`

Il CC non è nella tabella `MIDI_CC_MAPPING`.

Aggiorna:

```text
Codex/aquarium_boids/config.py
```

## Caso 3 — Python funziona ma Max non riceve

Apri la patch:

```text
Codex/max/aquarium_netreceive_mapped.maxpat
```

Controlla che usi:

```text
netreceive -u 7401
```

Guarda la Max Console.

## Caso 4 — Max riceve ma non senti suono

Controlla:

- `ezdac~` acceso;
- `Options → Audio Status`;
- output audio corretto;
- volume del sistema;
- patch in lock mode (`CTRL + E`).

---

# 10. Workflow finale desiderato

Quando tutto funziona, il musicista deve usare questo schema:

```text
MIDIMIX = controllo performativo
Python/main.py = ecosistema + generazione Markov
Max = sintesi sonora + effetti
```

Il computer non serve più come controller principale: tastiera e mouse restano solo come fallback/debug.
