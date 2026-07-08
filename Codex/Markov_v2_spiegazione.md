# Markov v2 — spiegazione del codice

## 1. Obiettivo

La Markov v2 reintroduce l'output musicale simbolico, ma in modo più ordinato rispetto alla Markov precedente.

La differenza fondamentale è questa:

```text
Markov v1  = eventi liberi nel tempo, non davvero agganciati a una griglia musicale
Markov v2  = eventi quantizzati su clock a sedicesimi, divisi in layer utili per Max
```

Quindi la Markov v2 non sostituisce i descriptor già funzionanti. Li affianca.

Il nuovo flusso è:

```text
MIDIMIX
↓
Python / boids
↓
descriptor + controlli performance
↓
Max riceve:
  direct       → modulazioni continue
  performance  → macro-controlli del performer
  clock        → tempo musicale
  chord        → armonia
  note         → note simboliche per bass/lead/keys
  hit          → eventi sample / glitch / noise
```

---

## 1.1 Uso ottimale della Markov v2

La Markov v2 non va pensata come un generatore casuale di note, ma come un **direttore d'orchestra probabilistico**.

Il suo compito non è produrre direttamente un bel timbro. Il suo compito è decidere:

```text
quando succede un evento
che tipo di evento succede
quanto è forte
quanto dura
quale voce musicale lo suona
quanto è ordinato o caotico
quanto è denso o rarefatto
```

Il timbro finale invece resta responsabilità di Max e del musicista.

Quindi la separazione ideale è:

```text
Python / Markov v2 = decisione musicale
Max / musicista    = rendering sonoro
```

In pratica:

```text
Pesci + MIDIMIX → influenzano la Markov
Markov          → manda eventi simbolici
Max             → trasforma gli eventi in sample, synth, effetti e mix
```

---

## 1.2 Come i pesci influenzano la Markov

I pesci producono descriptor continui:

```text
mean_speed
energy
density
spread
direction_coherence
center_x
center_y
```

Questi descriptor non devono per forza diventare suono diretto. Possono modificare il comportamento della Markov.

Esempi:

| Descriptor | Influenza musicale possibile |
|---|---|
| `mean_speed` | più attività ritmica, più probabilità di note |
| `energy` | velocity più alta, eventi più forti |
| `density` | note più consonanti, armonia più stabile |
| `spread` | registro melodico più ampio, più spazio |
| `direction_coherence` alta | pattern più regolari |
| `direction_coherence` bassa | pattern più frammentati |
| `center_x` | pan o scelta di zona stereo in Max |
| `center_y` | filtro, brightness, registro |

Quindi i pesci non sono solo una sorgente di modulazione audio: diventano una sorgente di **controllo compositivo**.

---

## 1.3 Come i fader MIDIMIX influenzano la Markov

I fader sono macro-controlli performativi.

### `alignment_chaos`

```text
basso → musica più ordinata/stabile
alto  → più caos, offbeat, salti melodici, hit e glitch
```

### `grain_density`

```text
basso → pochi eventi, più spazio
alto  → più note, più hit, più grani, meno silenzio
```

### `noise_distortion`

```text
basso → meno noise, velocity più morbide
alto  → più hit noise/glitch, velocity più aggressive
```

Altri fader influenzano i boids e quindi agiscono indirettamente sulla Markov:

```text
cohesion   → branco compatto → armonia più stabile
separation → branco disperso → registro più largo / più frammentazione
food       → accumulo / attrazione / tensione
predator   → fuga / esplosione / accenti
scene_id   → scena, banco sample, preset Max
```

---

## 1.4 Ruolo del musicista e dei sample in Max

La Markov v2 manda eventi simbolici, per esempio:

```text
note bass 45 90 500
note lead 69 84 250
chord 57 60 64
hit glitch 3 100 120
```

Questi messaggi non obbligano a usare suoni sintetici basilari. Anzi: il caso d'uso migliore è che il musicista li usi per controllare i suoi sample e strumenti in Max.

Esempi di mapping in Max:

| Messaggio | Possibile rendering Max |
|---|---|
| `note bass` | sample basso pitchato, synth sub, linea grave |
| `note lead` | sample melodico, synth lead, frammento pitchato |
| `chord` | pad, texture armonica, drone intonato |
| `hit grain` | micro-sample, granuli, frammenti brevi |
| `hit glitch` | sample glitch, click, tagli ritmici |
| `hit noise` | rumori, distorsione, impatti sporchi |

Quindi:

```text
Python decide cosa deve succedere musicalmente.
Max decide come quella cosa deve suonare.
```

Questa è la forma più forte del progetto, perché conserva il controllo artistico del musicista e usa la Markov come struttura generativa.

---

## 2. File coinvolti

### `aquarium_boids/config.py`

Qui sono stati aggiunti i flag:

```python
ENABLE_MARKOV = False
ENABLE_MARKOV_V2 = True
MARKOV_V2_DEBUG = True
```

Significato:

- `ENABLE_MARKOV = False`: spegne la vecchia Markov v1;
- `ENABLE_MARKOV_V2 = True`: accende la nuova Markov quantizzata;
- `MARKOV_V2_DEBUG = True`: stampa nel terminale note, accordi e hit generati.

---

### `aquarium_boids/markov_v2.py`

È il file principale della nuova Markov.

Contiene:

```python
BeatClock
MarkovV2Generator
ClockEvent
ChordEvent
NoteEventV2
HitEvent
```

---

### `aquarium_boids/osc_io.py`

Qui è stato aggiunto:

```python
send_markov_v2_event(...)
```

Questo metodo trasforma gli eventi Python in messaggi per Max.

---

### `main.py`

Qui la Markov v2 viene inizializzata e chiamata a ogni frame.

La logica è:

```python
for step in markov_v2_clock.tick(dt_s):
    for music_event in markov_v2.generate_step(step, descriptors, controls):
        osc.send_markov_v2_event(music_event)
```

Quindi:

1. il clock accumula il tempo reale;
2. quando scatta un sedicesimo, genera uno `step`;
3. la Markov decide quali eventi musicali produrre su quello step;
4. gli eventi vengono mandati a Max.

---

## 3. Il clock: `BeatClock`

Classe:

```python
@dataclass
class BeatClock:
    bpm: float = BPM
    steps_per_beat: int = 4
```

Con:

```python
steps_per_beat = 4
```

significa:

```text
1 beat = 4 sedicesimi
1 battuta 4/4 = 16 sedicesimi
```

Il metodo importante è:

```python
def tick(self, dt_s: float) -> list[int]:
```

Ogni frame riceve quanti secondi sono passati. Quando è passato abbastanza tempo per un sedicesimo, restituisce uno o più step.

Esempio concettuale:

```text
BPM 120
1 beat = 0.5 secondi
1 sedicesimo = 0.125 secondi
```

Quindi ogni 0.125 secondi parte un nuovo step.

---

## 4. Tipi di eventi

La Markov v2 genera quattro famiglie di messaggi.

## 4.1 `ClockEvent`

Serve a sincronizzare Max.

Messaggio plain UDP:

```text
clock kind index step step_in_bar beat_in_bar bar bpm;
```

Esempio:

```text
clock beat 32 128 0 0 8 120;
```

Campi:

| Campo | Significato |
|---|---|
| `kind` | `step`, `beat` o `bar` |
| `index` | indice del tipo di evento |
| `step` | sedicesimo globale |
| `step_in_bar` | posizione 0..15 nella battuta |
| `beat_in_bar` | beat 0..3 |
| `bar` | numero di battuta |
| `bpm` | tempo |

Max può usare questo per sincronizzare metro, delay, trigger e sample.

---

## 4.2 `ChordEvent`

Serve per l'armonia.

Messaggio:

```text
chord root third fifth chord_degree scene_id bar;
```

Esempio:

```text
chord 57 60 64 0 1 8;
```

I primi tre valori sono note MIDI:

```text
root  = fondamentale
third = terza
fifth = quinta
```

Il musicista può usarle per:

- pad;
- drone armonico;
- texture intonata;
- selezione di sample armonici;
- cambio di preset.

---

## 4.3 `NoteEventV2`

Serve per note musicali vere.

Messaggio:

```text
note voice midi_note velocity duration_ms degree octave layer_id scene_id chord_degree event_id;
```

Esempio:

```text
note lead 69 84 250 2 1 2 1 0 43;
```

Campi:

| Campo | Significato |
|---|---|
| `voice` | voce musicale: `bass`, `lead`, `keys` |
| `midi_note` | nota MIDI già pronta |
| `velocity` | intensità 0..127 |
| `duration_ms` | durata in millisecondi |
| `degree` | grado melodico simbolico |
| `octave` | ottava simbolica |
| `layer_id` | layer numerico compatibile con il sistema precedente |
| `scene_id` | scena corrente |
| `chord_degree` | grado dell'accordo corrente |
| `event_id` | id progressivo evento |

In Max il routing consigliato è:

```text
[route note]
|
[route bass lead keys]
```

---

## 4.4 `HitEvent`

Serve per eventi percussivi, glitch, rumore, sample brevi.

Messaggio:

```text
hit voice sample_id velocity duration_ms scene_id event_id;
```

Esempio:

```text
hit glitch 3 100 120 2 44;
```

`voice` può essere:

```text
grain
glitch
noise
```

Il musicista può usare `sample_id` per scegliere quale sample suonare.

---

## 5. Conversione da gradi a note MIDI

Funzione:

```python
def degree_to_midi(degree: int, octave: int = 0, root_midi: int = ROOT_MIDI) -> int:
```

Usa la scala definita in `config.py`:

```python
ROOT_MIDI = 57
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
```

Quindi di default siamo in La minore naturale.

La cosa importante è che questa funzione non fa solo:

```python
(degree + chord) % 7
```

come nella versione vecchia.

Ora, se un grado supera 6, sale davvero di ottava.

Esempio:

```text
degree 0 → La
degree 2 → Do
degree 4 → Mi
degree 7 → La dell'ottava sopra
```

Questo rende la linea melodica più musicale.

---

## 6. Accordi: `chord_notes`

Funzione:

```python
def chord_notes(chord_degree: int, octave: int = 0) -> tuple[int, int, int]:
```

Crea una triade diatonica:

```text
fondamentale + terza + quinta
```

In codice:

```python
degree_to_midi(chord_degree)
degree_to_midi(chord_degree + 2)
degree_to_midi(chord_degree + 4)
```

Questo rende l'armonia percepibile in Max.

---

## 7. Le Markov interne

La classe `MarkovV2Generator` contiene più catene Markov:

```python
lead_pitch
rhythm_steps
chord_chain
bass_degrees
hit_samples
```

### `lead_pitch`

Sceglie il prossimo grado melodico della voce lead.

Esempio:

```python
0: [(0, 0.25), (1, 0.08), (2, 0.30), (4, 0.25), (5, 0.12)]
```

Significa:

```text
se sono sul grado 0, posso restare su 0 oppure andare verso 1, 2, 4, 5 con probabilità diverse
```

---

### `rhythm_steps`

Sceglie la durata delle note lead in numero di sedicesimi:

```text
1 = un sedicesimo
2 = un ottavo
4 = un quarto
```

---

### `chord_chain`

Sceglie l'accordo a ogni battuta.

I gradi usati sono principalmente:

```text
0, 5, 3, 4
```

Che corrispondono circa alla progressione:

```text
i - VI - iv - V
```

in contesto minore.

---

### `bass_degrees`

Sceglie note per il basso rispetto all'accordo corrente:

```text
0 = fondamentale
4 = quinta
7 = ottava
2 = terza
```

Il basso quindi resta più stabile e leggibile.

---

### `hit_samples`

Sceglie quale sample breve attivare:

```text
sample_id 0, 1, 2, 3
```

Il musicista può mappare questi ID ai suoi sample.

---

## 8. Come i pesci influenzano la Markov

La Markov v2 legge sia i descriptor sia i controlli performance.

## 8.1 `alignment_chaos`

Controlla ordine/caos musicale.

Valori bassi:

```text
pattern più regolari
meno hit rumorosi
più stabilità
```

Valori alti:

```text
più probabilità di offbeat
più salti melodici
più hit/glitch/noise
maggiore temperatura Markov
```

---

## 8.2 `grain_density`

Controlla quanti eventi musicali vengono generati.

Valori bassi:

```text
meno note lead
meno hit
texture più rarefatta
```

Valori alti:

```text
più note lead
più hit/grani
basso leggermente più attivo
```

---

## 8.3 `noise_distortion`

Controlla l'aggressività degli hit.

Valori alti:

```text
più eventi noise
velocity più alta
hit più presenti
```

In più, nel sistema demo, `noise_distortion` aumenta anche il `noise_weight` dei boids.

---

## 8.4 `mean_speed`

Influenza:

```text
probabilità delle note lead
velocity percepita
attività generale
```

---

## 8.5 `energy`

Influenza soprattutto:

```text
velocity delle note
velocity degli hit
```

---

## 8.6 `density`

Quando il branco è compatto, la lead viene leggermente spinta verso note dell'accordo:

```text
fondamentale
terza
quinta
```

Quindi il comportamento compatto produce materiale più armonicamente stabile.

---

## 8.7 `spread`

Quando il branco è disperso, la lead può usare un registro più ampio.

```text
spread basso → registro più contenuto
spread alto  → registro più largo
```

---

## 8.8 `direction_coherence`

Se il branco è poco coerente, la probabilità di note frammentate aumenta leggermente.

Quindi:

```text
pesci ordinati   → ritmo più stabile
pesci incoerenti → ritmo più frammentato
```

---

## 9. Logica per ogni step

Il metodo centrale è:

```python
def generate_step(self, step, descriptors, controls) -> list[MarkovV2Event]:
```

A ogni sedicesimo fa questo:

```text
1. manda sempre clock step
2. se siamo su un beat, manda clock beat
3. se siamo a inizio battuta, manda clock bar + nuovo chord
4. decide se generare basso
5. decide se generare lead
6. decide se generare hit/grain/glitch/noise
```

Quindi Max riceve eventi musicali già a tempo.

---

## 10. Messaggi verso Max

In `osc_io.py` il metodo:

```python
send_markov_v2_event(event)
```

converte gli eventi in messaggi.

Plain UDP su porta `7401`:

```text
clock ...;
chord ...;
note ...;
hit ...;
```

OSC su porta `7400`:

```text
/markov/v2/clock
/markov/v2/chord
/markov/v2/note
/markov/v2/hit
```

Per la prova con Max consigliamo ancora il plain UDP:

```text
[netreceive -u 7401]
|
[route direct performance clock chord note hit]
```

---

## 11. Come testarla

### Test senza Max

Terminale 1:

```bash
cd Codex
.venv\Scripts\python.exe tools\udp_monitor.py
```

Terminale 2:

```bash
cd Codex
.venv\Scripts\python.exe main.py
```

Dovresti vedere messaggi:

```text
clock
chord
note
hit
```

oltre a:

```text
direct
performance
descriptors
```

---

## 12. Cosa deve fare Max

Patch consigliata:

```text
[netreceive -u 7401]
|
[route direct performance clock chord note hit]
```

Poi:

```text
note → [route bass lead keys]
hit  → [route grain glitch noise]
chord → pad / texture armonica
clock → sincronizzazione
```

Il musicista decide come suonano questi eventi:

- synth basso;
- sample pitchati;
- pad;
- granulatore;
- hit glitch;
- rumore/distorsione;
- effetti.

---

## 13. Perché questa versione è più musicale

La Markov v2 è più musicale perché:

```text
1. è agganciata a una griglia ritmica
2. separa basso, lead, accordi e hit
3. manda accordi veri come triadi
4. usa note MIDI già pronte per Max
5. mantiene anche i gradi simbolici per analisi/mapping
6. lascia il sound design al musicista
7. usa i descriptor dei pesci per variare densità, registro, caos e velocity
```

Quindi il sistema non sta ancora “componendo un brano finito”, ma genera materiale musicale strutturato che il musicista può renderizzare bene in Max.
