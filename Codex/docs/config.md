# `config.py` — configurazione globale del progetto

File di riferimento:

```text
Codex/aquarium_boids/config.py
```

Questo file contiene **tutti i parametri globali** del sistema:

- porte di comunicazione tra Python e Max;
- attivazione e mapping del MIDIMIX;
- dimensione della finestra Pygame;
- numero di boids;
- parametri musicali di base;
- scala musicale usata per convertire gli eventi simbolici in note.

---

# 1. Porte di comunicazione

Nel file trovi:

```python
OSC_HOST = "127.0.0.1"
OSC_PORT = 7400
PLAIN_UDP_PORT = 7401
CONTROL_PORT = 7500
```

Significato:

```text
7400 = OSC standard verso Max
7401 = plain UDP verso Max, fallback stabile
7500 = controlli da Max verso Python
```

Quindi il sistema usa tre flussi possibili:

```text
Python → Max: 7400 OSC
Python → Max: 7401 plain UDP / Max-compatible fallback
Max → Python: 7500 controlli esterni
```

Nel workflow attuale principale:

```text
MIDIMIX → Python → Max
```

Max riceve i dati da Python e renderizza il suono.

---

# 2. Configurazione MIDIMIX

Nel file trovi:

```python
ENABLE_MIDI_INPUT = True
MIDI_INPUT_NAME = "MIDIMIX"
MIDI_DEBUG = True
```

## `ENABLE_MIDI_INPUT`

```python
ENABLE_MIDI_INPUT = True
```

Dice a Python di provare ad aprire direttamente un device MIDI.

Se è `True`, `main.py` prova a usare il MIDIMIX come controller diretto.

Se fosse `False`, il sistema funzionerebbe comunque con:

```text
tastiera / mouse
Max → Python via UDP 7500
```

## `MIDI_INPUT_NAME`

```python
MIDI_INPUT_NAME = "MIDIMIX"
```

Python cerca un dispositivo MIDI il cui nome contiene questa stringa.

Se nel terminale appare un nome diverso, bisogna aggiornare questa variabile.

Esempio:

```python
MIDI_INPUT_NAME = "Akai MIDIMIX"
```

oppure anche solo:

```python
MIDI_INPUT_NAME = "MIDI"
```

se serve fare match più generico.

## `MIDI_DEBUG`

```python
MIDI_DEBUG = True
```

Quando è attivo, ogni volta che muovi un fader Python stampa nel terminale:

```text
[midi] cc=19 value=87 channel=1
```

Questo serve per scoprire i veri numeri CC dei fader del MIDIMIX.

---

# 3. Mappatura MIDIMIX

La parte più importante è:

```python
MIDI_CC_MAPPING = {
    19: ("alignment_weight", 0.0, 3.0, False),
    20: ("cohesion_weight", 0.0, 3.0, False),
    21: ("separation_weight", 0.0, 4.0, False),
    22: ("noise_weight", 0.0, 1.5, False),
    23: ("food_amount", 0.0, 3.0, False),
    24: ("predator_amount", 0.0, 3.0, False),
    25: ("density_fader", 0.0, 1.0, False),
    26: ("section_id", 0.0, 5.0, True),
}
```

Ogni riga significa:

```text
CC MIDI → parametro Python → range minimo/massimo → intero sì/no
```

Esempio:

```python
19: ("alignment_weight", 0.0, 3.0, False)
```

vuol dire:

```text
se arriva CC 19
prendi valore MIDI 0-127
scalalo in 0.0-3.0
assegnalo ad alignment_weight
non arrotondarlo a intero
```

Per `section_id`:

```python
26: ("section_id", 0.0, 5.0, True)
```

`True` vuol dire:

```text
arrotonda a intero
```

perché le sezioni sono discrete:

```text
0 intro
1 growth
2 dense
3 chaos
4 release
5 outro
```

---

# 4. Cos'è `section_id`

`section_id` è un numero intero che rappresenta la **sezione musicale/performativa corrente**.

La mappatura è:

```text
0 = intro
1 = growth
2 = dense
3 = chaos
4 = release
5 = outro
```

Serve per dire al sistema:

> “In che parte della performance siamo?”

Non è un parametro fisico dei boids. È un parametro di **forma musicale**.

## Dove viene usato

Viene usato soprattutto in:

```text
Codex/aquarium_boids/markov.py
```

Per esempio:

```python
if controls.section_name == "intro":
    layer_id = random.choices([0, 1, 2], weights=[0.60, 0.25, 0.15], k=1)[0]
elif controls.section_name == "chaos":
    layer_id = random.choices([2, 3, 4, 5], weights=[0.25, 0.30, 0.25, 0.20], k=1)[0]
```

Significa:

- in `intro` il sistema favorisce layer più morbidi:

```text
drone, bass, lead
```

- in `chaos` favorisce layer più aggressivi:

```text
lead, perc, granular, noise
```

Quindi `section_id` cambia il **carattere musicale** degli eventi generati.

## Perché è utile performativamente

In live puoi fare:

```text
intro → growth → dense → chaos → release → outro
```

senza cambiare codice.

Il musicista può usare un fader o pulsanti per spostarsi tra sezioni.

Esempio:

```text
section_id = 0
```

musica più lenta, rarefatta, drone.

```text
section_id = 3
```

musica più caotica, più percussiva/noise.

---

# 5. Parametri visuali

```python
WIDTH = 1200
HEIGHT = 750
FPS = 60
BOID_COUNT = 100
```

Questi controllano:

- dimensione finestra;
- frame rate;
- numero boids.

## `WIDTH` / `HEIGHT`

Dimensioni della finestra Pygame.

Aumentandole, hai più spazio visivo.

## `FPS`

Frame per secondo della simulazione.

```text
60 = fluido
30 = più leggero per CPU
```

## `BOID_COUNT`

Numero di boids/pesci.

```python
BOID_COUNT = 100
```

Se lo aumenti:

- visual più denso;
- calcolo più pesante;
- descriptor più stabili statisticamente.

Se lo diminuisci:

- visual più leggero;
- movimento meno “branco”;
- più leggibilità degli individui.

---

# 6. Parametri musicali

Nel file trovi:

```python
BPM = 120
ROOT_MIDI = 57
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
```

## `BPM`

Serve per convertire durate in beat in millisecondi.

Esempio:

```text
BPM 120 → un beat = 500 ms
```

Viene usato per produrre messaggi tipo:

```text
/music/midi event_id midi_note velocity duration_ms layer_id section_id
```

---

# 7. `ROOT_MIDI`

```python
ROOT_MIDI = 57
```

57 è una nota MIDI.

```text
57 = A3 / La
```

Quindi la scala parte da La.

Cambiare `ROOT_MIDI` significa cambiare tonalità.

Esempi:

```python
ROOT_MIDI = 60  # C / Do
ROOT_MIDI = 62  # D / Re
ROOT_MIDI = 57  # A / La
```

---

# 8. `SCALE_INTERVALS`

```python
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
```

Questa è una scala minore naturale espressa in semitoni rispetto alla tonica.

In La minore:

```text
0  = A
2  = B
3  = C
5  = D
7  = E
8  = F
10 = G
```

Quindi:

```text
degree 0 → A
degree 1 → B
degree 2 → C
degree 3 → D
degree 4 → E
degree 5 → F
degree 6 → G
```

---

# 9. Come viene usata `SCALE_INTERVALS`

In:

```text
Codex/aquarium_boids/osc_io.py
```

c'è:

```python
def event_to_midi(event: MusicEvent) -> int:
    scale_index = (event.degree + event.chord_degree) % len(SCALE_INTERVALS)
    octave_shift = event.octave * 12
    return int(ROOT_MIDI + SCALE_INTERVALS[scale_index] + octave_shift)
```

La Markov non produce direttamente note MIDI. Produce:

```text
degree
chord_degree
octave
```

Poi questa funzione converte in MIDI.

Esempio:

```text
ROOT_MIDI = 57
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]

degree = 2
chord_degree = 0
octave = 0
```

Risultato:

```text
scale_index = 2
SCALE_INTERVALS[2] = 3
MIDI = 57 + 3 = 60
```

MIDI 60 = C.

---

# 10. La scala è modificabile?

Sì, assolutamente.

Puoi cambiare sia:

```python
ROOT_MIDI
```

sia:

```python
SCALE_INTERVALS
```

---

## Esempio: Do maggiore

```python
ROOT_MIDI = 60
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
```

Risultato:

```text
C D E F G A B
```

---

## Esempio: La minore armonica

```python
ROOT_MIDI = 57
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 11]
```

Differenza:

```text
G diventa G#
```

Suono più teso, più “classico/drammatico”.

---

## Esempio: pentatonica minore

```python
ROOT_MIDI = 57
SCALE_INTERVALS = [0, 3, 5, 7, 10]
```

Attenzione: questa scala ha 5 gradi, non 7.

Il codice funziona comunque perché usa:

```python
len(SCALE_INTERVALS)
```

per calcolare l'indice.

Ma la Markov Chain attuale genera gradi da 0 a 6. Se usi una scala a 5 note, gli indici vengono ridotti con modulo:

```python
(degree + chord_degree) % 5
```

Funziona, ma cambia il comportamento melodico.

---

## Esempio: scala cromatica

```python
ROOT_MIDI = 60
SCALE_INTERVALS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
```

Più instabile, meno tonale.

---

## Esempio: scala esatonale / whole tone

```python
ROOT_MIDI = 60
SCALE_INTERVALS = [0, 2, 4, 6, 8, 10]
```

Molto sospesa, acquatica, irreale.

Questa potrebbe essere interessante per il progetto.

---

# 11. Come ottenere risultati diversi modificando `config.py`

## Più stabilità live

```python
BOID_COUNT = 80
FPS = 60
MIDI_DEBUG = False
```

Meno stampa in terminale e simulazione più leggera.

## Più densità visuale

```python
BOID_COUNT = 160
```

Più massa visiva, ma più costo CPU.

## Scala più consonante

```python
ROOT_MIDI = 57
SCALE_INTERVALS = [0, 3, 5, 7, 10]
```

Pentatonica minore: meno rischio di note dissonanti.

## Scala più acquatica/sospesa

```python
ROOT_MIDI = 60
SCALE_INTERVALS = [0, 2, 4, 6, 8, 10]
```

Whole tone: colore irreale e fluttuante.

## Mapping MIDIMIX diverso

Se il fader che vuoi usare per `alignment_weight` manda CC 7:

```python
MIDI_CC_MAPPING = {
    7: ("alignment_weight", 0.0, 3.0, False),
    ...
}
```

---

# Sintesi

`config.py` risponde alla domanda:

```text
Quali sono i parametri globali del sistema?
```

Contiene:

- porte di rete;
- configurazione MIDIMIX;
- mapping dei fader;
- dimensione simulazione;
- numero di boids;
- root e scala musicale.

Se vuoi cambiare:

```text
mapping controller
scala
tonalità
numero boids
porte di comunicazione
```

il primo file da controllare è:

```text
Codex/aquarium_boids/config.py
```
