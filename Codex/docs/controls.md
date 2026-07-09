# `controls.py` — stato live dei controlli performativi

File studiato:

```text
Codex/aquarium_boids/controls.py
```

Questo file è piccolo, ma è centrale: definisce l'oggetto che contiene **tutti i parametri modificabili durante la performance**.

In pratica `controls.py` è il punto in cui si incontrano:

```text
MIDIMIX / tastiera / mouse / Max UDP
↓
RuntimeControls
↓
boids.py + markov.py + osc_io.py + main.py
```

---

## 1. Codice completo

```python
from dataclasses import dataclass


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass
class RuntimeControls:
    density_fader: float = 0.25
    alignment_weight: float = 1.0
    cohesion_weight: float = 0.9
    separation_weight: float = 1.35
    noise_weight: float = 0.18
    food_strength: float = 1.0  # mouse-left attractor multiplier
    predator_strength: float = 1.0  # mouse-right repeller multiplier
    food_amount: float = 0.0  # virtual center attractor controlled by MIDIMIX
    predator_amount: float = 0.0  # virtual center repeller controlled by MIDIMIX
    section_id: int = 0
    paused: bool = False

    @property
    def section_name(self) -> str:
        return ["intro", "growth", "dense", "chaos", "release", "outro"][self.section_id]

    def as_list(self) -> list[float]:
        return [
            self.density_fader,
            self.alignment_weight,
            self.cohesion_weight,
            self.separation_weight,
            self.noise_weight,
            self.food_strength,
            self.predator_strength,
            self.food_amount,
            self.predator_amount,
            float(self.section_id),
        ]
```

---

## 2. Responsabilità del file

`controls.py` non muove i pesci, non genera musica e non manda OSC.

La sua responsabilità è più semplice:

```text
contenere lo stato live dei controlli performativi
```

Esempio:

```python
controls = RuntimeControls()
```

Da quel momento `controls` diventa una specie di mixer interno del programma:

```python
controls.density_fader
controls.alignment_weight
controls.cohesion_weight
controls.section_id
```

Altri file leggono o modificano questi valori.

---

## 3. `dataclass`: perché viene usato

```python
from dataclasses import dataclass
```

```python
@dataclass
class RuntimeControls:
```

`@dataclass` serve per creare una classe contenitore senza scrivere manualmente il costruttore.

Senza `@dataclass`, avremmo dovuto scrivere qualcosa tipo:

```python
class RuntimeControls:
    def __init__(self):
        self.density_fader = 0.25
        self.alignment_weight = 1.0
        self.cohesion_weight = 0.9
        ...
```

Con `@dataclass`, invece, basta dichiarare i campi:

```python
@dataclass
class RuntimeControls:
    density_fader: float = 0.25
    alignment_weight: float = 1.0
```

Python genera automaticamente un `__init__` equivalente.

Quindi questo funziona subito:

```python
controls = RuntimeControls()
```

E produce valori iniziali già pronti.

---

## 4. `clamp01`

```python
def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
```

Questa funzione forza un numero dentro il range:

```text
0.0 → 1.0
```

Esempi:

```python
clamp01(-0.5)  # 0.0
clamp01(0.4)   # 0.4
clamp01(2.0)   # 1.0
```

Serve soprattutto per parametri normalizzati, cioè parametri che devono stare fra 0 e 1.

Nel progetto viene usata principalmente per:

```text
density_fader
```

Attenzione: `clamp01` è definita qui, ma `RuntimeControls` **non la applica automaticamente**. Se qualcuno scrive:

```python
controls.density_fader = 99
```

il valore diventa davvero `99`.

Il clamp viene applicato nei punti in cui i valori vengono ricevuti, per esempio:

- `main.py`, quando si usano UP/DOWN;
- `midi_in.py`, quando arriva un valore dal MIDIMIX;
- `control_in.py`, quando arriva un controllo da Max via UDP.

---

## 5. Campi di `RuntimeControls`

### 5.1 `density_fader`

```python
density_fader: float = 0.25
```

È uno dei controlli più importanti del progetto.

Range ideale:

```text
0.0 → 1.0
```

Non controlla direttamente il movimento dei pesci. Controlla soprattutto la generazione musicale.

In `main.py` influenza quanti eventi vengono generati:

```python
burst = 1 + int(controls.density_fader * 3.2)
```

In `markov.py` influenza:

- temperatura della Markov;
- probabilità di pausa;
- scelta dei layer;
- densità percepita degli eventi.

Concettualmente:

| Valore | Risultato |
|---:|---|
| `0.0` | pochi eventi, texture lenta/ambient |
| `0.5` | densità media, pattern più attivi |
| `1.0` | molti eventi, granularità/glitch |

---

### 5.2 `alignment_weight`

```python
alignment_weight: float = 1.0
```

Controlla quanto i pesci tendono ad allinearsi alla direzione dei vicini.

Usato in `boids.py`:

```python
alignment = self.align(boids) * controls.alignment_weight
```

Effetto visivo:

| Valore basso | Valore alto |
|---|---|
| movimento più indipendente | branco più coordinato |

Effetto musicale indiretto:

- aumenta o diminuisce `direction_coherence`;
- influenza la stabilità ritmica della Markov;
- rende il movimento più o meno leggibile.

---

### 5.3 `cohesion_weight`

```python
cohesion_weight: float = 0.9
```

Controlla quanto i pesci tendono ad avvicinarsi al centro dei vicini.

Usato in `boids.py`:

```python
cohesion = self.cohesion(boids) * controls.cohesion_weight
```

Effetto visivo:

| Valore basso | Valore alto |
|---|---|
| branco disperso | branco compatto |

Effetto musicale indiretto:

- cambia `density`;
- cambia `spread`;
- può rendere il suono più compatto o più rarefatto.

---

### 5.4 `separation_weight`

```python
separation_weight: float = 1.35
```

Controlla quanto i pesci si respingono quando sono troppo vicini.

Usato in `boids.py`:

```python
separation = self.separation(boids) * controls.separation_weight
```

Effetto visivo:

| Valore basso | Valore alto |
|---|---|
| pesci più vicini/sovrapposti | pesci più distanziati |

È una forza importante per evitare che il branco collassi in un unico punto.

---

### 5.5 `noise_weight`

```python
noise_weight: float = 0.18
```

Aggiunge casualità al movimento.

Usato in `boids.py`:

```python
noise = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * self.max_force * controls.noise_weight
```

Effetto visivo:

| Valore basso | Valore alto |
|---|---|
| movimento fluido | movimento nervoso/caotico |

Effetto musicale indiretto:

- varia `mean_speed`;
- rende più instabili i descriptor;
- aumenta la percezione di caos.

---

### 5.6 `food_strength`

```python
food_strength: float = 1.0
```

È il moltiplicatore dell'attrattore attivato con il mouse sinistro.

Nel progetto ci sono due concetti distinti:

```text
food_strength = forza del food manuale/mouse
food_amount   = quantità di food virtuale da MIDIMIX/Max
```

`food_strength` serve quando l'utente clicca con il mouse sinistro nella finestra Pygame.

---

### 5.7 `predator_strength`

```python
predator_strength: float = 1.0
```

È il moltiplicatore del repulsore attivato con il mouse destro.

Anche qui ci sono due concetti distinti:

```text
predator_strength = forza del predatore manuale/mouse
predator_amount   = quantità di predatore virtuale da MIDIMIX/Max
```

`predator_strength` serve quando l'utente clicca con il mouse destro nella finestra Pygame.

---

### 5.8 `food_amount`

```python
food_amount: float = 0.0
```

È l'attrattore virtuale controllato dal MIDIMIX o da Max.

Nel workflow attuale è mappato al fader 5 del MIDIMIX.

In `main.py`, se `food_amount > 0.01`, viene creato un attrattore virtuale al centro dello schermo:

```python
if attractor is None and controls.food_amount > 0.01:
    attractor = Vector2(WIDTH * 0.5, HEIGHT * 0.5)
```

Poi in `boids.py` la forza viene applicata così:

```python
food_force = controls.food_amount if controls.food_amount > 0.0 else controls.food_strength
self.acceleration += self._steer_towards(attractor - self.position) * (0.9 * food_force)
```

Quindi il fader non è solo ON/OFF: può controllare l'intensità dell'attrazione.

---

### 5.9 `predator_amount`

```python
predator_amount: float = 0.0
```

È il repulsore virtuale controllato dal MIDIMIX o da Max.

Nel workflow attuale è mappato al fader 6 del MIDIMIX.

In `main.py`, se `predator_amount > 0.01`, viene creato un repulsore virtuale al centro dello schermo:

```python
if repeller is None and controls.predator_amount > 0.01:
    repeller = Vector2(WIDTH * 0.5, HEIGHT * 0.5)
```

Poi in `boids.py` la forza viene applicata così:

```python
predator_force = controls.predator_amount if controls.predator_amount > 0.0 else controls.predator_strength
self.acceleration += self._steer_towards(delta) * (2.8 * predator_force * (1.0 - distance / 220.0))
```

Effetto:

| Valore basso | Valore alto |
|---|---|
| nessun predatore virtuale | fuga forte dal centro |

---

### 5.10 `section_id`

```python
section_id: int = 0
```

Rappresenta la sezione musicale corrente.

Mappatura:

| `section_id` | Nome |
|---:|---|
| `0` | `intro` |
| `1` | `growth` |
| `2` | `dense` |
| `3` | `chaos` |
| `4` | `release` |
| `5` | `outro` |

Viene usato soprattutto in `markov.py` per cambiare la scelta dei layer.

Esempio:

```python
if controls.section_name == "intro":
    layer_id = random.choices([0, 1, 2], weights=[0.60, 0.25, 0.15], k=1)[0]
elif controls.section_name == "chaos":
    layer_id = random.choices([2, 3, 4, 5], weights=[0.25, 0.30, 0.25, 0.20], k=1)[0]
```

Quindi la sezione non è solo un'etichetta: cambia il comportamento del generatore musicale.

Attenzione importante: `section_name` usa `section_id` come indice di lista. Quindi `section_id` deve restare tra 0 e 5.

Se qualcuno facesse:

```python
controls.section_id = 99
```

questa riga romperebbe:

```python
controls.section_name
```

Per questo `midi_in.py` e `control_in.py` limitano il valore a `0..5`.

---

### 5.11 `paused`

```python
paused: bool = False
```

Indica se la simulazione visiva è in pausa.

In `main.py`, con `SPACE` viene invertito:

```python
controls.paused = not controls.paused
```

Nota importante: nello stato attuale, `paused` ferma l'aggiornamento dei boids, ma non spegne necessariamente tutto il resto.

Nel loop principale:

```python
if not controls.paused:
    for boid in flock:
        boid.flock(...)
    for boid in flock:
        boid.update(...)
```

I descriptor vengono ancora calcolati e gli eventi musicali possono ancora essere generati. Quindi `paused` significa principalmente:

```text
ferma il movimento dei pesci
```

non necessariamente:

```text
silenzia il sistema
```

Se in futuro vogliamo una pausa totale, bisogna modificare `main.py`.

---

## 6. `section_name`

```python
@property
def section_name(self) -> str:
    return ["intro", "growth", "dense", "chaos", "release", "outro"][self.section_id]
```

`@property` permette di usare una funzione come se fosse un attributo.

Quindi invece di scrivere:

```python
controls.section_name()
```

si scrive:

```python
controls.section_name
```

Esempio:

```python
controls.section_id = 3
print(controls.section_name)
```

Risultato:

```text
chaos
```

Serve perché internamente il programma usa un numero (`section_id`), ma per HUD, logica musicale e messaggi OSC è più leggibile avere anche il nome.

---

## 7. `as_list`

```python
def as_list(self) -> list[float]:
    return [
        self.density_fader,
        self.alignment_weight,
        self.cohesion_weight,
        self.separation_weight,
        self.noise_weight,
        self.food_strength,
        self.predator_strength,
        self.food_amount,
        self.predator_amount,
        float(self.section_id),
    ]
```

Questo metodo converte lo stato dei controlli in una lista.

Viene usato in `osc_io.py`:

```python
self.client.send_message("/aquarium/controls", controls.as_list())
self._send_plain("controls", controls.as_list())
```

Quindi Max riceve i controlli in questo ordine:

```text
density_fader
alignment_weight
cohesion_weight
separation_weight
noise_weight
food_strength
predator_strength
food_amount
predator_amount
section_id
```

Questo ordine è importante.

Se cambiamo l'ordine qui, bisogna aggiornare anche:

- `docs/OSC_CONTRACT.md`;
- eventuali patch Max che leggono `controls`;
- eventuali script di test;
- qualsiasi documentazione del mapping.

---

## 8. Chi modifica `RuntimeControls`

### 8.1 Tastiera in `main.py`

`main.py` modifica direttamente i controlli quando premi tasti:

```text
UP/DOWN → density_fader
A/Z     → alignment_weight
S/X     → cohesion_weight
D/C     → separation_weight
N/M     → noise_weight
1..6    → section_id
SPACE   → paused
```

---

### 8.2 MIDIMIX in `midi_in.py`

`midi_in.py` riceve valori MIDI CC e li assegna ai campi di `RuntimeControls`.

Esempio:

```text
CC 19 → alignment_weight
CC 20 → cohesion_weight
CC 21 → separation_weight
CC 22 → noise_weight
CC 23 → food_amount
CC 24 → predator_amount
CC 25 → density_fader
CC 26 → section_id
```

La mappatura reale è in `config.py`.

---

### 8.3 Max/UDP in `control_in.py`

`control_in.py` permette di mandare controlli a Python via UDP.

Esempi:

```text
control density_fader 0.75;
control alignment_weight 1.2;
control section_id 3;
```

Anche questi valori vengono applicati allo stesso oggetto `RuntimeControls`.

---

## 9. Chi legge `RuntimeControls`

### 9.1 `boids.py`

Legge i parametri fisici:

```text
alignment_weight
cohesion_weight
separation_weight
noise_weight
food_strength
predator_strength
food_amount
predator_amount
```

Li usa per calcolare accelerazione e movimento dei pesci.

---

### 9.2 `markov.py`

Legge i parametri musicali/formali:

```text
density_fader
section_id
section_name
```

Li usa per decidere:

- quante pause produrre;
- quanto rendere variabile la Markov;
- quali layer favorire;
- che carattere musicale avere.

---

### 9.3 `osc_io.py`

Legge tutto lo stato e lo manda fuori:

```text
/aquarium/controls
/aquarium/section
/aquarium/direct
```

---

### 9.4 `main.py`

Lo usa per:

- HUD a schermo;
- logging CSV;
- scelta attrattore/repulsore virtuale;
- pausa;
- generazione eventi.

---

## 10. Schema mentale da ricordare

La cosa più importante è questa:

```text
RuntimeControls = stato condiviso della performance
```

Non è un controller fisico.
Non è il MIDIMIX.
Non è Max.
Non è la tastiera.

È il contenitore centrale che rappresenta il valore corrente dei controlli, indipendentemente da dove arrivino.

```text
Tastiera ─┐
MIDIMIX ──┼──> RuntimeControls ───> boids / Markov / OSC / HUD
Max UDP ─┘
```

---

## 11. Cose importanti se modifichiamo questo file

### 11.1 Aggiungere un nuovo controllo

Se aggiungiamo un campo, per esempio:

```python
reverb_amount: float = 0.0
```

non basta aggiungerlo qui.

Bisogna decidere anche:

1. chi lo modifica?
   - tastiera?
   - MIDIMIX?
   - Max UDP?

2. chi lo usa?
   - boids?
   - Markov?
   - Max?

3. va mandato via OSC?
   - se sì, aggiornare `as_list` o creare un messaggio dedicato;

4. bisogna aggiornare la documentazione e la patch Max?

---

### 11.2 Non rompere `as_list`

`as_list` è un contratto implicito con Max.

Cambiare l'ordine dei valori può rompere patch che si aspettano un certo campo in una certa posizione.

Meglio aggiungere nuovi valori in fondo, non in mezzo.

---

### 11.3 Validazione non automatica

`RuntimeControls` è una dataclass semplice. Non impedisce valori sbagliati.

Esempio:

```python
controls.section_id = -10
controls.density_fader = 400
```

Python lo accetta.

La protezione avviene nei file che ricevono input esterno:

- `midi_in.py`;
- `control_in.py`;
- `main.py`.

---

## 12. Riassunto finale

`controls.py` definisce lo stato live del sistema.

I punti da ricordare sono:

- `RuntimeControls` è il contenitore centrale dei parametri performativi;
- `density_fader` è il controllo musicale principale;
- `alignment/cohesion/separation/noise` controllano il comportamento boids;
- `food_amount/predator_amount` sono controlli virtuali da MIDIMIX/Max;
- `food_strength/predator_strength` sono legati ai gesti mouse;
- `section_id` controlla la forma musicale;
- `as_list()` è il formato con cui i controlli vengono mandati a Max;
- se modifichiamo questo file, probabilmente dobbiamo aggiornare anche MIDI, OSC, Max e documentazione.

---

## 13. Domande successive / approfondimenti

Questa sezione verrà aggiornata con le prossime domande sul file `controls.py`.

