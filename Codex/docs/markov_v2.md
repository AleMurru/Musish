# `markov_v2.py` — spiegazione completa e controllo del codice

File analizzato:

```text
Codex/aquarium_boids/markov_v2.py
```

Questo documento serve per capire **in dettaglio** cosa fa ogni parte del codice della Markov v2. La Markov v2 è il generatore musicale simbolico attualmente attivo nel progetto Codex quando in `config.py` vale:

```python
ENABLE_MARKOV_V2 = True
```

La vecchia `markov.py` non è più il generatore principale, ma è ancora importata perché contiene `WeightedMarkov`, classe usata anche qui.

---

## 1. Idea generale

`markov_v2.py` fa quattro cose:

```text
1. Tiene un clock musicale quantizzato a sedicesimi.
2. Genera accordi a inizio battuta.
3. Genera note di basso e lead su griglia ritmica.
4. Genera hit/grain/glitch/noise per Max.
```

Il file non produce audio. Produce **eventi simbolici** che poi `osc_io.py` manda a Max:

```text
clock ...
chord ...
note ...
hit ...
```

Flusso reale nel progetto:

```text
main.py
  ↓
BeatClock.tick(dt_s)
  ↓
MarkovV2Generator.generate_step(step, descriptors, controls)
  ↓
OscSender.send_markov_v2_event(event)
  ↓
Max
```

---

## 2. Concetti musicali usati dal codice

### 2.1 Griglia temporale

Il clock lavora a sedicesimi:

```text
steps_per_beat = 4
1 beat = 4 sedicesimi
1 battuta 4/4 = 16 sedicesimi
```

A `BPM = 120`:

```text
1 beat = 0.5 s
1 sedicesimo = 0.125 s
```

### 2.2 Scala

Da `config.py`:

```python
ROOT_MIDI = 57
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
```

Significa:

```text
root = MIDI 57 = La
scala = minore naturale
0 = La
1 = Si
2 = Do
3 = Re
4 = Mi
5 = Fa
6 = Sol
7 = La ottava sopra
```

### 2.3 Descriptor dei boids usati

| Descriptor | Effetto nella Markov v2 |
|---|---|
| `mean_speed` | più velocità del branco → più probabilità di note/hit |
| `energy` | più energia → velocity MIDI più alta |
| `density` | branco compatto → lead più spesso su note dell'accordo |
| `spread` | branco largo → registro più ampio e accordi più variabili |
| `direction_coherence` | coerenza bassa → più frammentazione ritmica |

### 2.4 Controlli performativi usati

| Controllo | Effetto |
|---|---|
| `alignment_chaos` | aumenta caos, temperatura Markov, offbeat, glitch |
| `grain_density` | aumenta densità di eventi |
| `noise_distortion` | aumenta hit noise/glitch e velocity aggressiva |
| `section_id` | scena/preset/banco sample per Max |

---

# 3. Analisi riga per riga / blocco per blocco

> Le righe vuote non hanno logica esecutiva: servono solo a separare visivamente i blocchi. Sono comunque indicate quando delimitano sezioni importanti.

---

## Righe 1-9 — Import

### Riga 1

```python
from __future__ import annotations
```

Rende più flessibili le annotazioni di tipo. Permette di usare type hint moderni senza che Python debba risolverli immediatamente a runtime.

### Riga 2

Riga vuota di separazione.

### Riga 3

```python
import random
```

Importa il generatore casuale standard. È usato per tutte le decisioni probabilistiche: se generare note, scegliere ottave, scegliere hit, variare velocity, ecc.

### Riga 4

```python
from dataclasses import dataclass, field
```

Importa:

- `dataclass`: crea automaticamente `__init__`, rappresentazione e gestione dei campi;
- `field`: serve per campi con `default_factory`, cioè oggetti creati freschi per ogni istanza.

Senza `field(default_factory=...)`, le catene Markov potrebbero essere condivise male tra istanze diverse.

### Riga 5

```python
from typing import Literal
```

Importa `Literal`, usato per dire: questa variabile può avere solo alcuni valori stringa precisi.

### Riga 6

Riga vuota di separazione.

### Riga 7

```python
from .config import BPM, ROOT_MIDI, SCALE_INTERVALS
```

Importa parametri globali:

- `BPM`: tempo musicale;
- `ROOT_MIDI`: nota base della scala;
- `SCALE_INTERVALS`: intervalli della scala.

Questi tre valori controllano tempo e intonazione della Markov v2.

### Riga 8

```python
from .controls import RuntimeControls, clamp01
```

Importa:

- `RuntimeControls`: struttura che contiene i controlli live/MIDIMIX;
- `clamp01`: funzione che limita un valore tra `0.0` e `1.0`.

`clamp01` è fondamentale perché le probabilità devono restare nel range 0..1.

### Riga 9

```python
from .markov import WeightedMarkov
```

Importa la classe Markov pesata dalla vecchia `markov.py`.

Questa è una dipendenza importante: anche se `markov.py` non è più il generatore attivo, `markov_v2.py` usa ancora `WeightedMarkov` per scegliere stati successivi con probabilità pesate.

---

## Righe 11-19 — Tipi simbolici e mapping voce/layer

### Riga 11

```python
VoiceName = Literal["bass", "lead", "keys"]
```

Definisce il tipo delle voci melodiche. Una `voice` di nota può essere solo:

```text
bass
lead
keys
```

Nel codice attuale vengono generati soprattutto `bass` e `lead`. `keys` è predisposto ma non ancora usato direttamente.

### Riga 12

```python
HitVoice = Literal["grain", "glitch", "noise"]
```

Definisce il tipo delle voci per gli hit/sample brevi:

```text
grain  = micro-evento o grano
glitch = evento sporco/irregolare
noise  = rumore/distorsione
```

### Riga 13

```python
ClockKind = Literal["step", "beat", "bar"]
```

Definisce i tre tipi di evento clock:

```text
step = ogni sedicesimo
beat = ogni quarto
bar  = ogni battuta
```

### Riga 14

Riga vuota.

### Righe 15-19

```python
VOICE_LAYER_ID = {
    "bass": 1,
    "lead": 2,
    "keys": 2,
}
```

Mappa una voce musicale a un vecchio `layer_id` numerico.

Significato pratico:

| Voce | Layer ID |
|---|---:|
| bass | 1 |
| lead | 2 |
| keys | 2 |

Serve per compatibilità con il sistema precedente e con Max. Se un domani vuoi routing più preciso, potresti assegnare `keys` a un layer diverso.

---

## Righe 22-43 — Classe `BeatClock`

Questa classe è il clock musicale. Non genera note. Genera numeri di step su una griglia di sedicesimi.

### Riga 22

```python
@dataclass
```

Dice a Python che `BeatClock` è una dataclass.

### Riga 23

```python
class BeatClock:
```

Inizia la definizione della classe.

### Riga 24

```python
"""Simple musical clock quantized to a 16th-note grid."""
```

Docstring: spiega che il clock è quantizzato a sedicesimi.

### Riga 26

```python
bpm: float = BPM
```

Campo della dataclass. Il BPM di default viene da `config.py`.

### Riga 27

```python
steps_per_beat: int = 4
```

Quattro step per beat = sedicesimi.

Se mettessi:

```python
steps_per_beat = 2
```

avresti ottavi. Se mettessi `8`, avresti trentaduesimi.

### Riga 28

```python
accumulator_s: float = 0.0
```

Accumula tempo reale in secondi. Ogni frame Pygame aggiunge `dt_s`. Quando l'accumulatore supera la durata di uno step, il clock emette uno step.

### Riga 29

```python
step: int = 0
```

Contatore globale degli step. Parte da 0 e cresce sempre:

```text
0, 1, 2, 3, ...
```

### Riga 31

```python
@property
```

Trasforma il metodo successivo in una proprietà. Quindi puoi scrivere:

```python
self.step_duration_s
```

invece di:

```python
self.step_duration_s()
```

### Righe 32-33

```python
def step_duration_s(self) -> float:
    return 60.0 / self.bpm / self.steps_per_beat
```

Calcola la durata di uno step in secondi.

Formula:

```text
60 / BPM = durata di un beat
(60 / BPM) / steps_per_beat = durata di uno step
```

Esempio con `BPM=120`, `steps_per_beat=4`:

```text
60 / 120 = 0.5 s per beat
0.5 / 4 = 0.125 s per sedicesimo
```

### Righe 35-43

```python
def tick(self, dt_s: float) -> list[int]:
    """Return all grid steps that fire during this frame."""
    self.accumulator_s += max(0.0, dt_s)
    fired: list[int] = []
    while self.accumulator_s >= self.step_duration_s:
        self.accumulator_s -= self.step_duration_s
        fired.append(self.step)
        self.step += 1
    return fired
```

È il metodo centrale del clock.

Spiegazione riga per riga:

- riga 35: riceve `dt_s`, cioè i secondi passati dall'ultimo frame;
- riga 36: docstring;
- riga 37: aggiunge tempo all'accumulatore; `max(0.0, dt_s)` evita tempo negativo;
- riga 38: crea lista vuota degli step emessi;
- riga 39: finché è passato abbastanza tempo per uno step;
- riga 40: sottrae una durata-step dall'accumulatore;
- riga 41: aggiunge lo step corrente alla lista;
- riga 42: incrementa lo step globale;
- riga 43: restituisce tutti gli step scattati.

Perché restituisce una lista e non un solo step? Perché se un frame è lento, potrebbero essere passati due o più sedicesimi. Il `while` recupera gli step persi.

---

## Righe 46-91 — Dataclass degli eventi

Queste classi sono contenitori dati. Non fanno logica musicale; definiscono il formato degli eventi.

### Righe 46-54 — `ClockEvent`

```python
@dataclass
class ClockEvent:
    kind: ClockKind
    index: int
    step: int
    step_in_bar: int
    beat_in_bar: int
    bar: int
    bpm: float = BPM
```

Campi:

| Campo | Significato |
|---|---|
| `kind` | `step`, `beat` o `bar` |
| `index` | indice specifico dell'evento clock |
| `step` | step globale |
| `step_in_bar` | posizione 0..15 nella battuta |
| `beat_in_bar` | beat 0..3 nella battuta |
| `bar` | numero di battuta globale |
| `bpm` | BPM corrente |

Esempio:

```python
ClockEvent("beat", 4, 16, 0, 0, 1, 120)
```

significa: siamo sul beat 4 globale, allo step 16, inizio della battuta 1.

### Righe 57-64 — `ChordEvent`

```python
@dataclass
class ChordEvent:
    root: int
    third: int
    fifth: int
    chord_degree: int
    scene_id: int
    bar: int
```

Evento accordo. Contiene una triade già convertita in MIDI:

| Campo | Significato |
|---|---|
| `root` | fondamentale MIDI |
| `third` | terza MIDI |
| `fifth` | quinta MIDI |
| `chord_degree` | grado simbolico dell'accordo |
| `scene_id` | scena corrente |
| `bar` | battuta in cui accade |

### Righe 67-78 — `NoteEventV2`

```python
@dataclass
class NoteEventV2:
    event_id: int
    voice: VoiceName
    midi_note: int
    velocity: int
    duration_ms: int
    degree: int
    octave: int
    layer_id: int
    scene_id: int
    chord_degree: int
```

Evento nota. È già pronto per Max.

| Campo | Significato |
|---|---|
| `event_id` | ID progressivo |
| `voice` | `bass`, `lead`, `keys` |
| `midi_note` | nota MIDI già calcolata |
| `velocity` | intensità 0..127 |
| `duration_ms` | durata in millisecondi |
| `degree` | grado melodico simbolico |
| `octave` | ottava simbolica |
| `layer_id` | layer numerico legacy |
| `scene_id` | scena corrente |
| `chord_degree` | accordo corrente |

### Righe 81-88 — `HitEvent`

```python
@dataclass
class HitEvent:
    event_id: int
    voice: HitVoice
    sample_id: int
    velocity: int
    duration_ms: int
    scene_id: int
```

Evento per sample breve o rumore.

| Campo | Significato |
|---|---|
| `event_id` | ID progressivo |
| `voice` | `grain`, `glitch`, `noise` |
| `sample_id` | quale sample scegliere in Max |
| `velocity` | intensità |
| `duration_ms` | durata |
| `scene_id` | scena corrente |

### Riga 91

```python
MarkovV2Event = ClockEvent | ChordEvent | NoteEventV2 | HitEvent
```

Alias di tipo: un evento della Markov v2 può essere uno qualunque di questi quattro tipi.

Serve soprattutto per chiarezza e type hint.

---

## Righe 94-105 — Conversione valori MIDI

### Righe 94-95 — `clamp_midi`

```python
def clamp_midi(value: int) -> int:
    return max(0, min(127, int(value)))
```

Limita un valore al range MIDI valido:

```text
0..127
```

Se arriva `-5`, restituisce `0`. Se arriva `150`, restituisce `127`.

È usato per note e velocity.

### Righe 98-105 — `degree_to_midi`

```python
def degree_to_midi(degree: int, octave: int = 0, root_midi: int = ROOT_MIDI) -> int:
    """Convert a scale degree to MIDI without destroying octave information.

    Unlike the old v1 conversion, degrees outside 0..6 move through octaves
    instead of wrapping back into the same octave.
    """
    octave_offset, scale_index = divmod(int(degree), len(SCALE_INTERVALS))
    return clamp_midi(root_midi + SCALE_INTERVALS[scale_index] + 12 * (octave + octave_offset))
```

Questa funzione converte un grado della scala in nota MIDI.

Punto cruciale: usa `divmod`, quindi non perde l'informazione di ottava.

Esempi con scala di 7 note:

```text
degree 0 → octave_offset 0, scale_index 0
degree 6 → octave_offset 0, scale_index 6
degree 7 → octave_offset 1, scale_index 0
degree 8 → octave_offset 1, scale_index 1
```

Quindi il grado 7 non torna semplicemente a 0 nella stessa ottava: sale davvero di ottava.

Formula finale:

```text
root_midi + intervallo_scala + 12 * (octave + octave_offset)
```

Questa è una correzione importante rispetto alla vecchia Markov v1, dove `(degree + chord) % 7` schiacciava tutto nella stessa ottava.

---

## Righe 108-114 — Triadi/accordi

```python
def chord_notes(chord_degree: int, octave: int = 0) -> tuple[int, int, int]:
    """Diatonic triad: root + third + fifth above chord_degree."""
    return (
        degree_to_midi(chord_degree, octave),
        degree_to_midi(chord_degree + 2, octave),
        degree_to_midi(chord_degree + 4, octave),
    )
```

Questa funzione costruisce una triade diatonica.

Se `chord_degree = 0` in La minore:

```text
root  = degree 0 = La
third = degree 2 = Do
fifth = degree 4 = Mi
```

Quindi produce l'accordo di La minore.

Se `chord_degree = 5`:

```text
root  = Fa
third = La
fifth = Do
```

Quindi produce una triade costruita sul grado 5 della scala.

---

# 4. Classe principale: `MarkovV2Generator`

## Righe 117-124 — Definizione classe

```python
@dataclass
class MarkovV2Generator:
    """Quantized symbolic generator for Max.

    The generator emits a small, practical set of musical events:
    clock, chord, note and hit. Descriptors and performance controls shape
    probability, velocity, range and chaos.
    """
```

Questa è la classe principale del file.

È una dataclass perché contiene stato:

- `event_id`;
- `chord_degree`;
- catene Markov interne.

La docstring chiarisce la filosofia:

```text
non genera audio,
genera eventi simbolici pratici per Max.
```

---

## Righe 126-159 — Stato interno e catene Markov

### Riga 126

```python
event_id: int = 0
```

ID progressivo degli eventi musicali. Aumenta ogni volta che viene creato un basso, una lead o un hit. Non aumenta per clock e chord.

### Riga 127

```python
chord_degree: int = 0
```

Accordo corrente espresso come grado della scala. Parte da 0.

### Righe 128-136 — `lead_pitch`

```python
lead_pitch: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
    0: [(0, 0.25), (1, 0.08), (2, 0.30), (4, 0.25), (5, 0.12)],
    ...
}))
```

Catena Markov per la melodia lead.

Chiave = stato corrente.
Valore = lista di possibili stati successivi con peso.

Esempio:

```python
0: [(0, 0.25), (1, 0.08), (2, 0.30), (4, 0.25), (5, 0.12)]
```

Se la lead si trova sul grado 0, il prossimo grado può essere:

| Prossimo grado | Peso |
|---:|---:|
| 0 | 0.25 |
| 1 | 0.08 |
| 2 | 0.30 |
| 4 | 0.25 |
| 5 | 0.12 |

Non sono probabilità normalizzate manualmente: `random.choices` normalizza i pesi internamente.

Musicalmente:

- favorisce alcuni salti e movimenti;
- evita cromatismi perché lavora su gradi di scala;
- è una Markov di ordine 1: guarda solo lo stato precedente.

### Righe 137-141 — `rhythm_steps`

```python
rhythm_steps: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
    1: [(1, 0.55), (2, 0.30), (4, 0.15)],
    2: [(1, 0.30), (2, 0.45), (4, 0.25)],
    4: [(1, 0.22), (2, 0.38), (4, 0.40)],
}))
```

Catena Markov per la durata della lead in step.

Valori possibili:

```text
1 = un sedicesimo
2 = un ottavo
4 = un quarto
```

Esempio:

```python
1: [(1, 0.55), (2, 0.30), (4, 0.15)]
```

Se la durata precedente era 1 step, è più probabile restare su 1 step.

### Righe 142-147 — `chord_chain`

```python
chord_chain: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
    0: [(0, 0.08), (5, 0.36), (3, 0.24), (4, 0.32)],
    5: [(3, 0.40), (4, 0.28), (0, 0.24), (5, 0.08)],
    3: [(4, 0.46), (0, 0.28), (5, 0.18), (3, 0.08)],
    4: [(0, 0.55), (5, 0.20), (3, 0.15), (4, 0.10)],
}))
```

Catena Markov degli accordi.

Gradi principali:

```text
0, 5, 3, 4
```

In La minore naturale indicativamente:

```text
0 = La
5 = Fa
3 = Re
4 = Mi
```

La progressione tende a girare in zona:

```text
i - VI - iv - V-ish
```

A differenza della vecchia v1, qui la progressione è davvero Markov e non solo un ciclo fisso.

### Righe 148-153 — `bass_degrees`

```python
bass_degrees: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
    0: [(0, 0.50), (4, 0.28), (7, 0.14), (2, 0.08)],
    ...
}))
```

Catena Markov per il basso, ma relativa all'accordo corrente.

Valori:

```text
0 = fondamentale dell'accordo
2 = terza
4 = quinta
7 = ottava
```

Quindi il basso tende a essere stabile: molta fondamentale, un po' di quinta, poca terza.

### Righe 154-159 — `hit_samples`

```python
hit_samples: WeightedMarkov = field(default_factory=lambda: WeightedMarkov({
    0: [(0, 0.35), (1, 0.28), (2, 0.20), (3, 0.17)],
    ...
}))
```

Catena per scegliere `sample_id` degli hit.

I sample sono numeri simbolici:

```text
0, 1, 2, 3
```

Max decide a quale file audio corrispondono.

---

# 5. Metodo centrale: `generate_step`

## Righe 161-188

```python
def generate_step(self, step: int, descriptors: dict[str, float], controls: RuntimeControls) -> list[MarkovV2Event]:
```

Questo metodo viene chiamato una volta per ogni sedicesimo generato dal clock.

Input:

| Input | Significato |
|---|---|
| `step` | sedicesimo globale |
| `descriptors` | stato del branco |
| `controls` | controlli live |

Output:

```python
list[MarkovV2Event]
```

cioè una lista di eventi da mandare a Max.

### Righe 162-164

```python
step_in_bar = step % 16
beat_in_bar = step_in_bar // 4
bar = step // 16
```

Calcolano la posizione musicale.

- `step_in_bar`: posizione 0..15 dentro la battuta;
- `beat_in_bar`: beat 0..3;
- `bar`: battuta globale.

Esempio:

```text
step = 18
step_in_bar = 18 % 16 = 2
beat_in_bar = 2 // 4 = 0
bar = 18 // 16 = 1
```

Quindi siamo nella battuta 1, terzo sedicesimo.

### Righe 166-168

```python
events: list[MarkovV2Event] = [
    ClockEvent("step", step, step, step_in_bar, beat_in_bar, bar, BPM)
]
```

Ogni sedicesimo genera sempre un evento `clock step`.

Questo serve a Max per sincronizzarsi.

### Righe 169-170

```python
if step_in_bar % 4 == 0:
    events.append(ClockEvent("beat", step // 4, step, step_in_bar, beat_in_bar, bar, BPM))
```

Se lo step è multiplo di 4, siamo su un beat.

Step beat in una battuta:

```text
0, 4, 8, 12
```

Quindi viene aggiunto anche un evento `clock beat`.

### Righe 171-173

```python
if step_in_bar == 0:
    events.append(ClockEvent("bar", bar, step, step_in_bar, beat_in_bar, bar, BPM))
    events.append(self._next_chord(descriptors, controls, bar))
```

Se siamo all'inizio della battuta:

1. aggiunge `clock bar`;
2. genera il prossimo accordo con `_next_chord`.

Quindi gli accordi cambiano solo a inizio battuta.

### Righe 175-178 — Generazione basso

```python
if step_in_bar in {0, 8} or (controls.grain_density > 0.68 and step_in_bar in {4, 12}):
    if random.random() < self._bass_probability(descriptors, controls, step_in_bar):
        events.append(self._make_bass(descriptors, controls))
```

Il basso può suonare:

- sempre potenzialmente su step 0 e 8, cioè beat 1 e 3;
- anche su step 4 e 12, cioè beat 2 e 4, se `grain_density > 0.68`.

Poi non suona automaticamente: viene fatta una prova probabilistica.

`random.random()` produce un numero tra 0 e 1. Se è minore della probabilità calcolata da `_bass_probability`, allora viene generato il basso.

### Righe 180-182 — Generazione lead

```python
if random.random() < self._lead_probability(descriptors, controls, step_in_bar):
    events.append(self._make_lead(descriptors, controls))
```

La lead può essere generata su qualunque sedicesimo.

La probabilità dipende da:

- `grain_density`;
- `mean_speed`;
- posizione forte nella griglia;
- caos;
- coerenza del branco.

### Righe 184-186 — Generazione hit

```python
if random.random() < self._hit_probability(descriptors, controls, step_in_bar):
    events.append(self._make_hit(descriptors, controls))
```

Gli hit possono accadere su qualunque sedicesimo.

Sono più probabili con:

- alto `alignment_chaos`;
- alto `noise_distortion`;
- alta `grain_density`;
- offbeat;
- velocità alta.

### Riga 188

```python
return events
```

Restituisce tutti gli eventi prodotti su quello step.

Uno step può produrre, per esempio:

```text
clock step
clock beat
clock bar
chord
note bass
note lead
hit glitch
```

oppure solo:

```text
clock step
```

---

# 6. Accordi: `_next_chord`

## Righe 190-196

```python
def _next_chord(self, descriptors: dict[str, float], controls: RuntimeControls, bar: int) -> ChordEvent:
    chaos = controls.alignment_chaos
    spread = descriptors.get("spread", 0.0)
    temperature = 0.35 + chaos * 0.55 + spread * 0.25
    self.chord_degree = int(self.chord_chain.next(temperature=temperature))
    root, third, fifth = chord_notes(self.chord_degree, octave=0)
    return ChordEvent(root, third, fifth, self.chord_degree, controls.section_id, bar)
```

Spiegazione:

- legge `alignment_chaos`;
- legge `spread`;
- calcola una temperatura;
- usa la Markov degli accordi;
- converte il grado in triade MIDI;
- restituisce un `ChordEvent`.

### Temperatura

```python
temperature = 0.35 + chaos * 0.55 + spread * 0.25
```

Range indicativo:

```text
min = 0.35
max = 0.35 + 0.55 + 0.25 = 1.15
```

Più temperatura = scelte meno prevedibili.

Quindi:

```text
branco ordinato/stretto → accordi più stabili
branco caotico/largo    → accordi più variabili
```

---

# 7. Probabilità basso: `_bass_probability`

## Righe 198-201

```python
def _bass_probability(self, descriptors: dict[str, float], controls: RuntimeControls, step_in_bar: int) -> float:
    density = descriptors.get("density", 0.0)
    base = 0.92 if step_in_bar in {0, 8} else 0.42
    return clamp01(base + density * 0.12 - controls.alignment_chaos * 0.18)
```

Il basso è più probabile sui beat strutturali:

```text
step 0 e 8 → base 0.92
step 4 e 12 → base 0.42
```

Formula:

```text
probabilità = base + density*0.12 - alignment_chaos*0.18
```

Effetto:

- branco compatto (`density` alta) → basso più probabile;
- caos alto → basso meno probabile;
- `clamp01` garantisce range 0..1.

---

# 8. Probabilità lead: `_lead_probability`

## Righe 203-214

```python
def _lead_probability(self, descriptors: dict[str, float], controls: RuntimeControls, step_in_bar: int) -> float:
    speed = descriptors.get("mean_speed", 0.0)
    coherence = descriptors.get("direction_coherence", 0.0)
    chaos = controls.alignment_chaos
    density = controls.grain_density

    strong_grid_bonus = 0.12 if step_in_bar in {0, 4, 8, 12} else 0.0
    offbeat_bonus = 0.10 * chaos if step_in_bar in {2, 6, 10, 14} else 0.0
    fragmented_bonus = 0.12 * (1.0 - coherence)

    return clamp01(0.03 + density * 0.42 + speed * 0.16 + strong_grid_bonus + offbeat_bonus + fragmented_bonus)
```

Formula completa:

```text
prob = 0.03
     + grain_density * 0.42
     + mean_speed * 0.16
     + strong_grid_bonus
     + offbeat_bonus
     + fragmented_bonus
```

### Componenti

| Componente | Significato |
|---|---|
| `0.03` | probabilità minima |
| `grain_density * 0.42` | fader densità eventi |
| `speed * 0.16` | pesci veloci → più note |
| `strong_grid_bonus` | bonus sui beat forti 0/4/8/12 |
| `offbeat_bonus` | caos alto → più note sugli offbeat 2/6/10/14 |
| `fragmented_bonus` | branco incoerente → più frammentazione |

Quindi questa funzione è il cuore della densità melodica.

---

# 9. Probabilità hit: `_hit_probability`

## Righe 216-227

```python
def _hit_probability(self, descriptors: dict[str, float], controls: RuntimeControls, step_in_bar: int) -> float:
    chaos = controls.alignment_chaos
    distortion = controls.noise_distortion
    speed = descriptors.get("mean_speed", 0.0)
    offbeat = step_in_bar in {3, 7, 11, 15, 6, 14}
    downbeat = step_in_bar in {0, 8}
    base = 0.02 + controls.grain_density * 0.08 + chaos * 0.12 + distortion * 0.22 + speed * 0.05
    if offbeat:
        base += 0.10 * max(chaos, distortion)
    if downbeat and distortion > 0.72:
        base += 0.10
    return clamp01(base)
```

Formula base:

```text
base = 0.02
     + grain_density * 0.08
     + chaos * 0.12
     + distortion * 0.22
     + speed * 0.05
```

Poi:

- se siamo su offbeat, aggiunge un bonus proporzionale a caos/distorsione;
- se siamo su downbeat e distorsione è molto alta, aggiunge un accento.

Effetto musicale:

```text
sistema calmo → pochi hit
sistema caotico/distorto → più glitch/noise/hit
```

---

# 10. Creazione basso: `_make_bass`

## Righe 229-236

```python
def _make_bass(self, descriptors: dict[str, float], controls: RuntimeControls) -> NoteEventV2:
    self.event_id += 1
    relative = int(self.bass_degrees.next(temperature=0.45 + controls.alignment_chaos * 0.35))
    degree = self.chord_degree + relative
    midi_note = degree_to_midi(degree, octave=-1)
    velocity = clamp_midi(62 + int(descriptors.get("energy", 0.0) * 38) + int(controls.noise_distortion * 12))
    duration_ms = int((420 + controls.grain_density * 220) * (60.0 / BPM) / 0.5)
    return NoteEventV2(self.event_id, "bass", midi_note, velocity, duration_ms, degree, -1, VOICE_LAYER_ID["bass"], controls.section_id, self.chord_degree)
```

Spiegazione:

1. incrementa `event_id`;
2. sceglie una nota relativa all'accordo tramite `bass_degrees`;
3. somma questa nota al grado dell'accordo corrente;
4. converte in MIDI un'ottava sotto (`octave=-1`);
5. calcola velocity;
6. calcola durata;
7. restituisce una `NoteEventV2` con `voice="bass"`.

### Temperatura basso

```python
0.45 + controls.alignment_chaos * 0.35
```

Range:

```text
0.45..0.80
```

Il basso resta relativamente stabile anche con caos alto.

### Velocity basso

```python
62 + energy*38 + noise_distortion*12
```

Range teorico:

```text
62..112
```

poi limitato da `clamp_midi`.

### Durata basso

```python
(420 + grain_density * 220) * (60.0 / BPM) / 0.5
```

A `BPM=120`, `(60/BPM)/0.5 = 1`, quindi durata:

```text
420..640 ms
```

Se cambi BPM, la durata scala.

---

# 11. Creazione lead: `_make_lead`

## Righe 238-258

```python
def _make_lead(self, descriptors: dict[str, float], controls: RuntimeControls) -> NoteEventV2:
    self.event_id += 1
    chaos = controls.alignment_chaos
    spread = descriptors.get("spread", 0.0)
    density = descriptors.get("density", 0.0)
    temperature = 0.35 + chaos * 0.75 + controls.grain_density * 0.20
    degree = int(self.lead_pitch.next(temperature=temperature))

    if density > 0.70 and random.random() < 0.45:
        degree = random.choice([self.chord_degree, self.chord_degree + 2, self.chord_degree + 4])
    octave_span = 1 + int(spread * 2.5 + chaos * 1.5)
    octave = random.randint(0, octave_span)
    if chaos > 0.75 and random.random() < 0.25:
        octave -= 1

    midi_note = degree_to_midi(degree + self.chord_degree, octave=octave)
    velocity = clamp_midi(42 + int(descriptors.get("energy", 0.0) * 55) + int(chaos * 20) + random.randint(-6, 10))
    duration_steps = int(self.rhythm_steps.next(temperature=0.55 + chaos * 0.55))
    duration_ms = int(duration_steps * (60.0 / BPM / 4.0) * 1000)
    return NoteEventV2(self.event_id, "lead", midi_note, velocity, duration_ms, degree, octave, VOICE_LAYER_ID["lead"], controls.section_id, self.chord_degree)
```

Questa funzione genera la nota melodica principale.

### Passi logici

1. Incrementa `event_id`.
2. Legge caos, spread, density.
3. Calcola temperatura.
4. Usa `lead_pitch` per scegliere un grado melodico.
5. Se il branco è compatto, a volte forza la nota su una nota dell'accordo.
6. Sceglie l'ottava.
7. Con caos alto, a volte scende di ottava.
8. Converte in MIDI.
9. Calcola velocity.
10. Sceglie durata con `rhythm_steps`.
11. Restituisce `NoteEventV2`.

### Temperatura lead

```python
temperature = 0.35 + chaos * 0.75 + grain_density * 0.20
```

Range:

```text
0.35..1.30
```

Quindi la lead è molto più sensibile al caos rispetto al basso.

### Bias accordale

```python
if density > 0.70 and random.random() < 0.45:
    degree = random.choice([self.chord_degree, self.chord_degree + 2, self.chord_degree + 4])
```

Se il branco è compatto, nel 45% dei casi la nota viene forzata su:

```text
fondamentale, terza o quinta dell'accordo
```

Questa è una buona idea musicale: branco compatto = armonia più stabile.

### Registro

```python
octave_span = 1 + int(spread * 2.5 + chaos * 1.5)
octave = random.randint(0, octave_span)
```

Se `spread` e `chaos` sono alti, la lead può andare su più ottave.

### Possibile discesa con caos alto

```python
if chaos > 0.75 and random.random() < 0.25:
    octave -= 1
```

Con caos alto, nel 25% dei casi la nota scende di un'ottava. Serve a rendere il registro meno prevedibile.

### Nota MIDI

```python
midi_note = degree_to_midi(degree + self.chord_degree, octave=octave)
```

Somma il grado melodico al grado dell'accordo corrente, poi converte in MIDI.

Nota: nel caso del bias accordale, `degree` può già contenere `self.chord_degree`; poi qui viene sommato di nuovo. Questo può spostare più avanti del previsto il grado. Non è necessariamente un bug bloccante, ma è un punto da controllare se l'armonia suona troppo trasposta o instabile.

### Velocity lead

```python
42 + energy*55 + chaos*20 + random(-6, 10)
```

Lead più forte se:

- i pesci sono energetici;
- il sistema è caotico;
- il random aggiunge accento.

### Durata

```python
duration_steps = rhythm_steps.next(...)
duration_ms = duration_steps * durata_sedicesimo * 1000
```

A 120 BPM:

```text
1 step = 125 ms
2 step = 250 ms
4 step = 500 ms
```

---

# 12. Creazione hit: `_make_hit`

## Righe 260-273

```python
def _make_hit(self, descriptors: dict[str, float], controls: RuntimeControls) -> HitEvent:
    self.event_id += 1
    distortion = controls.noise_distortion
    chaos = controls.alignment_chaos
    if distortion > 0.72:
        voice: HitVoice = "noise"
    elif chaos > 0.62:
        voice = "glitch"
    else:
        voice = "grain"
    sample_id = int(self.hit_samples.next(temperature=0.55 + chaos * 0.55 + distortion * 0.35))
    velocity = clamp_midi(38 + int(descriptors.get("energy", 0.0) * 42) + int(distortion * 38) + random.randint(-5, 8))
    duration_ms = int(80 + controls.grain_density * 180 + chaos * 90)
    return HitEvent(self.event_id, voice, sample_id, velocity, duration_ms, controls.section_id)
```

Logica:

1. incrementa `event_id`;
2. legge distorsione e caos;
3. sceglie il tipo di hit;
4. sceglie `sample_id` con Markov;
5. calcola velocity;
6. calcola durata;
7. restituisce `HitEvent`.

### Scelta voce

```python
if distortion > 0.72:
    voice = "noise"
elif chaos > 0.62:
    voice = "glitch"
else:
    voice = "grain"
```

Priorità:

1. Se distorsione è molto alta → noise.
2. Altrimenti, se caos è alto → glitch.
3. Altrimenti → grain.

### Temperatura sample

```python
0.55 + chaos*0.55 + distortion*0.35
```

Range:

```text
0.55..1.45
```

Con caos/distorsione alti, la scelta del sample diventa più variabile.

### Velocity hit

```python
38 + energy*42 + distortion*38 + random(-5, 8)
```

Hit più forte con energia e distorsione alte.

### Durata hit

```python
80 + grain_density*180 + chaos*90
```

Range:

```text
80..350 ms
```

Con densità e caos alti, gli hit diventano più lunghi.

---

# 13. Come funziona `WeightedMarkov`

Anche se la classe è in `markov.py`, è essenziale per capire questo file.

Concettualmente funziona così:

```python
choices = self.transitions[self.state]
states = [stato for stato, peso in choices]
weights = [peso ** (1 / temperature) for peso in weights]
self.state = random.choices(states, weights=weights, k=1)[0]
return self.state
```

La temperatura modifica i pesi:

| Temperatura | Effetto |
|---:|---|
| `< 1` | rende le scelte più conservative/prevedibili |
| `= 1` | usa i pesi originali |
| `> 1` | appiattisce le differenze, più caos |

Esempio:

```text
temperature bassa → il peso forte domina
temperature alta  → anche i pesi deboli possono uscire
```

---

# 14. Cosa arriva a Max

Gli eventi creati qui vengono convertiti in `osc_io.py`.

### `ClockEvent`

```text
clock kind index step step_in_bar beat_in_bar bar bpm
```

### `ChordEvent`

```text
chord root third fifth chord_degree scene_id bar
```

### `NoteEventV2`

```text
note voice midi_note velocity duration_ms degree octave layer_id scene_id chord_degree event_id
```

### `HitEvent`

```text
hit voice sample_id velocity duration_ms scene_id event_id
```

---

# 15. Punti di controllo principali

Se vuoi controllare musicalmente il comportamento, questi sono i punti più importanti.

## 15.1 Densità note lead

Funzione:

```python
_lead_probability
```

Parametro più importante:

```python
grain_density * 0.42
```

Aumenta questo coefficiente se vuoi più note.

## 15.2 Caos melodico

Funzione:

```python
_make_lead
```

Riga logica:

```python
temperature = 0.35 + chaos * 0.75 + grain_density * 0.20
```

Riduci `0.75` se la melodia è troppo casuale.

## 15.3 Stabilità accordi

Funzione:

```python
_next_chord
```

Riga logica:

```python
temperature = 0.35 + chaos * 0.55 + spread * 0.25
```

Riduci i coefficienti se vuoi progressioni più prevedibili.

## 15.4 Frequenza hit/glitch/noise

Funzione:

```python
_hit_probability
```

Riga logica:

```python
base = 0.02 + grain_density*0.08 + chaos*0.12 + distortion*0.22 + speed*0.05
```

Il valore più influente è `distortion*0.22`.

## 15.5 Registro lead

Funzione:

```python
_make_lead
```

Riga logica:

```python
octave_span = 1 + int(spread * 2.5 + chaos * 1.5)
```

Se la melodia salta troppo, riduci `2.5` e `1.5`.

---

# 16. Possibili criticità o punti da rivedere

## 16.1 Dipendenza da `markov.py`

`markov_v2.py` importa:

```python
from .markov import WeightedMarkov
```

Se vogliamo eliminare `markov.py`, prima bisogna spostare `WeightedMarkov` in un file neutro, per esempio:

```text
aquarium_boids/weighted_markov.py
```

## 16.2 `keys` è dichiarata ma non generata

`VoiceName` include:

```text
keys
```

ma il codice attuale genera solo:

```text
bass
lead
```

Se vogliamo un layer armonico di keys/pad, va aggiunta una funzione tipo `_make_keys` o eventi note associati al `ChordEvent`.

## 16.3 Possibile doppia somma del grado accordale nella lead

Nel bias accordale:

```python
degree = random.choice([self.chord_degree, self.chord_degree + 2, self.chord_degree + 4])
```

poi più sotto:

```python
midi_note = degree_to_midi(degree + self.chord_degree, octave=octave)
```

Quindi in quel caso `self.chord_degree` può essere sommato due volte. Se musicalmente senti note troppo trasposte, questo è un punto da correggere.

Possibile fix concettuale:

```python
degree = random.choice([0, 2, 4])
midi_note = degree_to_midi(degree + self.chord_degree, octave=octave)
```

## 16.4 `noise_distortion` influenza la Markov più che i boids

In questo file `noise_distortion` influenza bene gli hit. Però se nelle doc diciamo che aumenta anche il caos visivo dei boids, bisogna verificare/collegare meglio quel comportamento in `boids.py` o `controls.py`.

---

# 17. Riassunto operativo

La Markov v2 lavora così:

```text
A ogni sedicesimo:
  manda sempre clock step
  se siamo su beat → manda clock beat
  se siamo su inizio battuta → manda clock bar + chord
  forse genera bass
  forse genera lead
  forse genera hit
```

I parametri più importanti per controllarla sono:

```text
alignment_chaos   → caos musicale
 grain_density    → quantità eventi
 noise_distortion → noise/glitch/hit aggressivi
 density          → stabilità armonica
 spread           → ampiezza registro
 energy           → velocity
 mean_speed       → attività
```

In breve:

```text
boids ordinati/compatti/lenti → musica più stabile, meno densa
boids caotici/dispersi/veloci → musica più frammentata, più hit, più registro
```

---

# 18. Mini-mappa per modifiche rapide

| Vuoi cambiare... | Dove intervenire |
|---|---|
| BPM | `config.py` → `BPM` |
| scala/tonalità | `config.py` → `ROOT_MIDI`, `SCALE_INTERVALS` |
| progressione accordi | `chord_chain` |
| melodia lead | `lead_pitch` |
| durate lead | `rhythm_steps` |
| note basso | `bass_degrees` |
| sample hit | `hit_samples` |
| quantità lead | `_lead_probability` |
| quantità hit | `_hit_probability` |
| quantità basso | `_bass_probability` |
| registro lead | `_make_lead` |
| velocity | `_make_bass`, `_make_lead`, `_make_hit` |
| formato eventi verso Max | `osc_io.py`, non questo file |
