# MIDIMIX diretto in Python — workflow principale

Abbiamo implementato il workflow consigliato:

```text
MIDIMIX
↓
main.py
  - controlla boids
  - controlla Markov
  - calcola descriptor
↓
Max
  - riceve descriptor
  - riceve eventi simbolici
  - renderizza synth/effects
```

In questa modalità Max **non deve leggere il MIDIMIX**. Max resta il renderer sonoro. Python apre direttamente il device MIDI e usa i fader per controllare l'ecosistema.

---

## Avvio

1. Collega MIDIMIX al computer.
2. Chiudi eventuali patch/programmi che stanno già usando MIDIMIX come input MIDI.
3. Avvia Python:

```bash
cd Codex
python main.py
```

Nel terminale dovresti vedere qualcosa tipo:

```text
[midi] input device 2: MIDIMIX (...)
[midi] listening to MIDIMIX [2]
[midi] debug enabled: move MIDIMIX faders to print CC/value
```

Se muovi un fader, dovresti vedere:

```text
[midi] cc=19 value=87 channel=1
[midi-map] cc=19 -> density_fader = 0.685
```

---

## Mappatura attuale

La mappatura è definita in:

```text
Codex/aquarium_boids/config.py
```

Tabella:

```python
MIDI_CC_MAPPING = {
    19: ("density_fader", 0.0, 1.0, False),
    20: ("alignment_weight", 0.0, 3.0, False),
    21: ("cohesion_weight", 0.0, 3.0, False),
    22: ("separation_weight", 0.0, 4.0, False),
    23: ("noise_weight", 0.0, 1.5, False),
    24: ("food_strength", 0.0, 3.0, False),
    25: ("predator_strength", 0.0, 3.0, False),
    26: ("section_id", 0.0, 5.0, True),
}
```

Significato:

| CC | Parametro | Range | Effetto |
|---:|---|---:|---|
| 19 | `density_fader` | 0..1 | quantità eventi Markov |
| 20 | `alignment_weight` | 0..3 | allineamento boids |
| 21 | `cohesion_weight` | 0..3 | compattezza branco |
| 22 | `separation_weight` | 0..4 | dispersione |
| 23 | `noise_weight` | 0..1.5 | turbolenza |
| 24 | `food_strength` | 0..3 | forza attrattore mouse sinistro |
| 25 | `predator_strength` | 0..3 | forza predatore mouse destro |
| 26 | `section_id` | 0..5 int | sezione musicale |

---

## Se i fader non controllano i parametri

I numeri CC possono cambiare in base al preset del MIDIMIX.

Per questo `MIDI_DEBUG = True` stampa ogni CC nel terminale:

```text
[midi] cc=XX value=YY channel=1
```

Procedura:

1. Muovi il fader che vuoi usare come Fader 1.
2. Guarda il numero `cc=XX` nel terminale.
3. Apri `Codex/aquarium_boids/config.py`.
4. Sostituisci il CC nella tabella `MIDI_CC_MAPPING`.

Esempio: se il primo fader stampa `cc=7`, modifica:

```python
7: ("density_fader", 0.0, 1.0, False),
```

al posto di:

```python
19: ("density_fader", 0.0, 1.0, False),
```

Poi riavvia:

```bash
python main.py
```

---

## Max nel nuovo workflow

Max deve solo ricevere e renderizzare:

```text
Python -> Max
```

Patch consigliate:

```text
Codex/max/aquarium_netreceive_mapped.maxpat    # plain UDP stabile
Codex/max/aquarium_osc_symbolic.maxpat         # OSC simbolico se funziona nella tua installazione Max
```

Non serve aprire `midimax_control_template.maxpat` nel workflow diretto. Quella patch resta utile come fallback se si vuole tornare al flusso:

```text
MIDIMIX -> Max -> Python
```

---

## Fallback ancora disponibili

Il sistema supporta tre modalità contemporaneamente:

```text
1. Tastiera/mouse -> Python
2. Max UDP -> Python su porta 7500
3. MIDIMIX diretto -> Python
```

Quindi se il MIDIMIX non viene letto, puoi comunque controllare il sistema con tastiera/mouse o con la patch Max di controllo.
