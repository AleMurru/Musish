# Guida per il musicista — Acquario Boids + Max

Questa guida serve per provare il sistema e capire come iniziare a renderizzare il suono in Max.

## 1. Concetto operativo

Il sistema è diviso in due parti:

```text
Python / Pygame = simulazione boids + generazione dati + Markov Chain
Max            = rendering sonoro + mapping + performance
```

Il musicista non deve pensare a Python come a un generatore audio, ma come a un generatore di:

- movimento;
- descriptor continui;
- eventi simbolici;
- note/eventi Markov;
- controlli performativi.

Max riceve questi dati e decide come trasformarli in suono.

---

## 2. Avvio rapido

### Step 1 — Avvia Python

Da terminale:

```bash
cd Codex
python main.py
```

Si apre la finestra con i boids.

### Step 2 — Apri Max

Patch consigliata, stabile:

```text
Codex/max/aquarium_netreceive_mapped.maxpat
```

Questa usa messaggi plain UDP su porta `7401`.

Patch OSC simbolica, da testare se il tuo Max riceve OSC leggibile:

```text
Codex/max/aquarium_osc_symbolic.maxpat
```

Questa usa `/music/note` e non usa `/music/midi`.

### Step 3 — Accendi l'audio

In Max:

```text
CTRL + E   // lock patch
click su ezdac~
```

---

## 3. Messaggi principali ricevuti in Max

### A. Messaggio continuo: `direct`

Formato plain UDP:

```text
direct mean_speed energy center_x center_y density spread density_fader
```

Formato OSC equivalente:

```text
/aquarium/direct mean_speed energy center_x center_y density spread density_fader
```

Campi:

| Campo | Nome | Uso musicale consigliato |
|---:|---|---|
| `$1` | `mean_speed` | frequenza, cutoff, densità ritmica |
| `$2` | `energy` | ampiezza, saturazione, intensità |
| `$3` | `center_x` | panning, posizione stereo |
| `$4` | `center_y` | brightness, ottava, filtro |
| `$5` | `density` | compattezza armonica, tensione |
| `$6` | `spread` | riverbero, range, dispersione stereo |
| `$7` | `density_fader` | quantità di eventi, mix drone/blip |

### B. Evento simbolico Markov: `note`

Formato plain UDP:

```text
note event_id degree octave duration_beats velocity layer_id layer_name chord_degree section_id
```

Formato OSC equivalente:

```text
/music/note event_id degree octave duration_beats velocity layer_id layer_name chord_degree section_id
```

Campi più utili:

| Campo | Nome | Uso |
|---:|---|---|
| `$2` | `degree` | grado melodico generato dalla Markov |
| `$3` | `octave` | registro |
| `$5` | `velocity` | intensità |
| `$6` | `layer_id` | quale strumento/layer deve suonare |
| `$7` | `layer_name` | nome del layer |
| `$8` | `chord_degree` | armonia corrente |
| `$9` | `section_id` | sezione performativa |

Layer:

```text
0 = drone
1 = bass
2 = lead
3 = perc
4 = granular
5 = noise
```

Sezioni:

```text
0 = intro
1 = growth
2 = dense
3 = chaos
4 = release
5 = outro
```

---

## 4. Come sono mappati i suoni nella patch attuale

La patch `aquarium_netreceive_mapped.maxpat` contiene tre suoni base.

### Suono 1 — Drone principale

```text
mean_speed -> frequenza del drone
energy     -> volume del drone
```

Interpretazione:

- boids veloci = drone più acuto;
- boids lenti = drone più grave;
- alta energia = più volume;
- bassa energia = suono più tenue.

### Suono 2 — Oscillatore di densità

```text
density -> frequenza del secondo oscillatore
```

Interpretazione:

- branco compatto = secondo tono più alto;
- branco disperso = secondo tono più basso.

### Suono 3 — Blip/eventi Markov

```text
note/midi events -> piccoli impulsi melodici
```

Interpretazione:

- `density_fader` alto = più eventi;
- sezione `chaos` = eventi più aggressivi/layer più rumorosi;
- sezione `intro` = più drone, meno eventi.

---

## 5. Come il musicista dovrebbe lavorare in Max

Il consiglio è non modificare subito il generatore Python. Lavorare invece in Max così:

### Step A — Tenere fisso il receiver

```text
netreceive -u 7401
|
route direct midi note rest descriptors controls section event
```

oppure, nella versione OSC:

```text
udpreceive 7400
|
route /aquarium/direct /music/note /music/rest ...
```

### Step B — Creare layer sonori separati

Creare subpatch o sezioni Max:

```text
[p drone_layer]
[p bass_layer]
[p lead_layer]
[p perc_layer]
[p granular_layer]
[p noise_layer]
```

### Step C — Usare `layer_id` per decidere dove mandare gli eventi

Da `note`:

```text
$6 = layer_id
```

Mapping consigliato:

```text
0 -> drone / texture
1 -> bass
2 -> lead
3 -> perc
4 -> granular
5 -> noise
```

### Step D — Usare `direct` per macro-modulazioni

Esempi:

```text
mean_speed -> cutoff filtro
energy -> drive / ampiezza
center_x -> panning
center_y -> brightness
spread -> riverbero
cluster_count -> numero di voci attive
density_fader -> mix tra ambient e glitch
```

---

## 6. Come giocare dal main.py adesso

Finché MIDIMAX non è collegato, i controlli sono da tastiera/mouse nella finestra Python:

| Controllo | Effetto |
|---|---|
| `UP/DOWN` | aumenta/diminuisce `density_fader` |
| `1..6` | cambia sezione musicale |
| `A/Z` | alignment + / - |
| `S/X` | cohesion + / - |
| `D/C` | separation + / - |
| `N/M` | noise + / - |
| mouse sinistro | cibo/attrattore |
| mouse destro | predatore/repulsore |
| `SPACE` | pausa |
| `R` | reset |
| `ESC` | esci |

---

## 7. MIDIMAX: collegamento pronto lato Python

Ora il flusso può essere bidirezionale:

```text
Python -> Max      // dati, note, descriptor
Max -> Python      // controlli da MIDIMAX
```

Python ascolta già i controlli su UDP `7500`. Il musicista può quindi collegare MIDIMAX in Max e mandare valori a Python.

### Architettura proposta

```text
MIDIMAX
  ↓ MIDI CC
Max
  ↓ UDP/OSC control messages
Python main.py
  ↓ boids + Markov aggiornati live
Max sound rendering
```

### Controlli MIDIMAX consigliati

| Fader/knob MIDIMAX | Parametro Python | Effetto |
|---|---|---|
| Fader 1 | `alignment_weight` | quanto i boids si allineano |
| Fader 2 | `cohesion_weight` | quanto il branco si compatta |
| Fader 3 | `separation_weight` | quanto si evitano / si disperdono |
| Fader 4 | `noise_weight` | caos/turbolenza |
| Fader 5 | `food_amount` | attrattore virtuale verso il centro |
| Fader 6 | `predator_amount` | repulsore virtuale dal centro |
| Fader 7 | `density_fader` | quantità di eventi / collettivo-individuale |
| Fader 8 | `section_id` | intro/growth/dense/chaos/release/outro |
| Knob 3 | master FX in Max | riverbero/delay |
| Knob 4 | brightness/filter in Max | timbro globale |

### Cosa è già implementato lato codice

1. In Python:
   - receiver UDP su porta `7500`;
   - parsing di messaggi `control parametro valore`;
   - aggiornamento live di `RuntimeControls`;
   - tastiera/mouse mantenuti come fallback;
   - `food_amount` e `predator_amount` controllabili esternamente come forze virtuali automatiche.

2. In Max:
   - template pronto in `Codex/max/midimax_control_template.maxpat`;
   - il musicista deve solo collegare i CC reali del MIDIMAX ai messaggi già predisposti.

### Contratto proposto Max -> Python

Porta proposta:

```text
7500
```

Messaggi:

```text
/control/alignment_weight value_0_3
/control/cohesion_weight value_0_3
/control/separation_weight value_0_4
/control/noise_weight value_0_1_5
/control/food_amount value_0_3
/control/predator_amount value_0_3
/control/density_fader value_0_1
/control/section_id value_0_5
```

In plain UDP, se vogliamo restare compatibili con il Max attuale:

```text
control density_fader 0.75;
control alignment_weight 1.2;
control section_id 3;
```

---

## 8. Obiettivo pratico per il musicista

Per ora il musicista dovrebbe:

1. aprire la patch Max funzionante;
2. capire quali dati arrivano (`direct`, `note`, `midi`, `section`);
3. sostituire i suoni demo con synth/effetti propri;
4. decidere quali layer gli servono;
5. preparare la mappatura MIDIMAX desiderata.

Il prossimo sviluppo tecnico sarà implementare il controllo MIDIMAX -> Max -> Python.
