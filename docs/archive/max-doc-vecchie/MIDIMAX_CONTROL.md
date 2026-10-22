# MIDIMAX -> Max -> Python

Abbiamo preparato il lato codice per ricevere controlli esterni da Max/MIDIMAX.

## Stato attuale

Python ora ascolta su:

```text
UDP 7500
```

Formato messaggi:

```text
control nome_parametro valore;
```

Esempi:

```text
control density_fader 0.75;
control alignment_weight 1.8;
control cohesion_weight 2.2;
control separation_weight 0.9;
control noise_weight 0.4;
control food_strength 1.5;
control predator_strength 2.0;
control section_id 3;
```

Quando Python riceve un controllo, nel terminale stampa:

```text
[control] density_fader = 0.75
```

I valori appaiono anche nell'HUD della finestra Pygame.

---

## Patch Max pronta

Patch template:

```text
Codex/max/midimax_control_template.maxpat
```

Questa patch contiene:

- `ctlin` per vedere value / CC number / channel del MIDIMAX;
- box manuali per testare l'invio dei controlli;
- `udpsend 127.0.0.1 7500` per mandare i controlli a Python.

Il musicista può usare la parte `ctlin` per fare MIDI learn e poi collegare i CC reali ai messaggi già presenti.

---

## Mappatura consigliata

| MIDIMAX | Messaggio a Python | Range consigliato | Effetto |
|---|---|---:|---|
| Fader 1 | `control alignment_weight $1` | 0..3 | allineamento boids |
| Fader 2 | `control cohesion_weight $1` | 0..3 | compattezza branco |
| Fader 3 | `control separation_weight $1` | 0..4 | dispersione / distanza |
| Fader 4 | `control noise_weight $1` | 0..1.5 | turbolenza |
| Fader 5 | `control food_amount $1` | 0..3 | attrattore virtuale verso il centro |
| Fader 6 | `control predator_amount $1` | 0..3 | repulsore virtuale dal centro |
| Fader 7 | `control density_fader $1` | 0..1 | densità eventi Markov |
| Fader 8 | `control section_id $1` | 0..5 intero | sezione musicale |

---

## Come mappare un fader MIDIMAX in Max

Schema tipico:

```text
ctlin
|
route CC_NUMBER
|
scale 0 127 MIN MAX
|
message: control parametro $1
|
udpsend 127.0.0.1 7500
```

Esempio per `alignment_weight`, se il fader manda CC 1:

```text
ctlin
|
route 1
|
scale 0 127 0. 3.
|
control alignment_weight $1
|
udpsend 127.0.0.1 7500
```

Esempio per `cohesion_weight`, se il fader manda CC 2:

```text
ctlin
|
route 2
|
scale 0 127 0. 3.
|
control cohesion_weight $1
|
udpsend 127.0.0.1 7500
```

Per `section_id`, conviene quantizzare a interi 0..5:

```text
ctlin
|
route CC_SECTION
|
scale 0 127 0 5
|
int
|
control section_id $1
|
udpsend 127.0.0.1 7500
```

---

## Test senza MIDIMAX

Per verificare il lato Python senza controller:

Terminale 1:

```bash
cd Codex
python main.py
```

Terminale 2:

```bash
cd Codex
python tools/send_control_test.py
```

Se tutto funziona, vedrai i parametri cambiare nella finestra Pygame e nel terminale.

---

## Nota importante

Il controllo da tastiera/mouse rimane attivo come fallback.

Quindi ora abbiamo due modi di controllare il sistema:

```text
Tastiera/mouse -> Python
MIDIMAX -> Max -> Python
```

Il prossimo step sarà sostituire gradualmente i controlli da tastiera con una mappatura MIDIMAX definitiva scelta dal musicista.
