# `controls.py` — stato live dei controlli performativi

File di riferimento:

```text
Codex/aquarium_boids/controls.py
```

Questo file definisce lo **stato live** del sistema: tutti i parametri che possono cambiare durante la performance.

È uno dei file più importanti perché collega:

```text
MIDIMIX / tastiera / Max controls
↓
RuntimeControls
↓
boids.py + markov.py + osc_io.py
```

---

# 1. Codice principale

Nel file trovi:

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
    food_strength: float = 1.0
    predator_strength: float = 1.0
    food_amount: float = 0.0
    predator_amount: float = 0.0
    section_id: int = 0
    paused: bool = False
```

---

# 2. Cosa significa `@dataclass`

```python
@dataclass
class RuntimeControls:
```

`@dataclass` è un decoratore Python.

Serve a trasformare una classe usata principalmente per contenere dati in una classe più comoda.

---

## Senza `@dataclass`

Dovresti scrivere:

```python
class RuntimeControls:
    def __init__(self):
        self.density_fader = 0.25
        self.alignment_weight = 1.0
        self.cohesion_weight = 0.9
        self.separation_weight = 1.35
        self.noise_weight = 0.18
```

---

## Con `@dataclass`

Puoi scrivere semplicemente:

```python
@dataclass
class RuntimeControls:
    density_fader: float = 0.25
    alignment_weight: float = 1.0
    cohesion_weight: float = 0.9
```

Python genera automaticamente:

```text
__init__
__repr__
confronti base
```

Quindi puoi fare:

```python
controls = RuntimeControls()
```

E hai già:

```python
controls.density_fader
controls.alignment_weight
controls.cohesion_weight
```

---

# 3. Perché `@dataclass` è utile qui

`RuntimeControls` è uno **stato live performativo**.

In altre parole è un contenitore di parametri modificabili in tempo reale.

Questo oggetto viene modificato da:

```text
MIDIMIX
Max via UDP
Tastiera
Mouse
```

E viene letto da:

```text
boids.py     → movimento dei pesci
markov.py    → eventi musicali
osc_io.py    → invio stato a Max
main.py      → HUD, loop principale, pause
```

Quindi `RuntimeControls` è il punto centrale in cui si incontrano controllo, simulazione e musica.

---

# 4. `clamp01`

```python
def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
```

Questa funzione forza un valore dentro il range:

```text
0.0 → 1.0
```

Esempi:

```python
clamp01(-0.4)  # 0.0
clamp01(0.6)   # 0.6
clamp01(1.8)   # 1.0
```

Serve per parametri normalizzati come:

```text
density_fader
```

---

# 5. Parametri principali di `RuntimeControls`

## `density_fader: float = 0.25`

Valore iniziale:

```python
0.25
```

Range ideale:

```text
0.0 → 1.0
```

Non controlla direttamente i boids. Controlla la generazione musicale.

In `main.py`:

```python
burst = 1 + int(controls.density_fader * 3.2)
```

Quindi:

```text
density_fader basso → pochi eventi
density_fader alto → più eventi per ciclo
```

In `markov.py`:

```python
temperature = 0.25 + controls.density_fader * 0.9 + speed * 0.35
```

Quindi:

```text
density_fader alto → Markov più variabile
```

E:

```python
rest_probability = max(0.05, 0.62 - controls.density_fader * 0.52 - speed * 0.22)
```

Quindi:

```text
density_fader alto → meno pause
density_fader basso → più pause
```

### Perché 0.25?

Per partire in uno stato non troppo denso.

```text
0.0 = troppo vuoto
1.0 = subito caotico
0.25 = texture iniziale controllabile
```

### Se lo cambi

```python
density_fader = 0.0
```

partenza molto ambient, pochi eventi.

```python
density_fader = 0.7
```

partenza già attiva e musicale.

---

## `alignment_weight: float = 1.0`

Controlla quanto ogni boid si allinea alla direzione dei vicini.

In `boids.py`:

```python
alignment = self.align(boids) * controls.alignment_weight
```

### Perché 1.0?

È un valore neutro.

I boids si allineano, ma non diventano tutti un blocco rigido.

### Se lo abbassi

```python
alignment_weight = 0.0
```

i boids non seguono più la direzione degli altri.

Movimento più individuale e disordinato.

### Se lo alzi

```python
alignment_weight = 2.5
```

il branco si muove più compatto direzionalmente.

Effetto:

```text
direction_coherence più alta
movimento più fluido
suono più stabile
```

---

## `cohesion_weight: float = 0.9`

Controlla quanto i boids vogliono stare vicini al gruppo.

```python
cohesion = self.cohesion(boids) * controls.cohesion_weight
```

### Perché 0.9?

Leggermente sotto 1.0 per evitare che i boids collassino troppo al centro.

### Se lo abbassi

```python
cohesion_weight = 0.0
```

il branco si disperde.

Effetto:

```text
spread aumenta
density diminuisce
suono più largo/raro
```

### Se lo alzi

```python
cohesion_weight = 2.5
```

i boids tendono a formare una massa compatta.

Effetto:

```text
density aumenta
secondo oscillatore Max cambia
armonia più compatta
```

---

## `separation_weight: float = 1.35`

Controlla quanto i boids si evitano tra loro.

```python
separation = self.separation(boids) * controls.separation_weight
```

### Perché 1.35?

È un po' più alto di alignment/cohesion perché serve a evitare sovrapposizioni.

Senza abbastanza separation, i boids tendono ad ammassarsi.

### Se lo abbassi

```python
separation_weight = 0.2
```

i boids possono diventare troppo vicini.

Effetto:

```text
branco più compatto
density alta
meno respiro visuale
```

### Se lo alzi

```python
separation_weight = 3.0
```

i boids si respingono molto.

Effetto:

```text
più spazio tra individui
spread/nearest_distance cambiano
movimento più nervoso
```

---

## `noise_weight: float = 0.18`

Aggiunge turbolenza random.

```python
noise = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * self.max_force * controls.noise_weight
```

### Perché 0.18?

Valore basso. Serve solo a non rendere il movimento troppo meccanico.

### Se lo abbassi

```python
noise_weight = 0.0
```

movimento più pulito e prevedibile.

### Se lo alzi

```python
noise_weight = 1.0
```

movimento più instabile.

Effetto:

```text
mean_speed/energy più variabili
Markov più imprevedibile
suono più agitato
```

---

# 6. Food e predator

## `food_strength: float = 1.0`

Controlla la forza del mouse sinistro come attrattore.

```text
food_strength = mouse-left attractor multiplier
```

Se tieni premuto mouse sinistro, i boids vengono attratti verso il mouse.

### Perché 1.0?

Valore neutro.

### Se lo alzi

```python
food_strength = 2.5
```

il mouse attira molto più forte.

### Se lo abbassi

```python
food_strength = 0.2
```

il mouse ha effetto più delicato.

---

## `predator_strength: float = 1.0`

Controlla la forza del mouse destro come repulsore.

Se tieni premuto mouse destro, i boids scappano dal mouse.

### Perché 1.0?

Valore neutro.

### Se lo alzi

```python
predator_strength = 3.0
```

effetto fuga molto forte.

### Se lo abbassi

```python
predator_strength = 0.3
```

repulsione più morbida.

---

## `food_amount: float = 0.0`

Questo è l'attrattore virtuale controllato dal MIDIMIX.

In `main.py`:

```python
if attractor is None and controls.food_amount > 0.01:
    attractor = Vector2(WIDTH * 0.5, HEIGHT * 0.5)
```

Quindi se `food_amount` è alto, anche senza mouse, il centro dello schermo diventa attrattore.

### Perché 0.0?

Per non avere attrattore automatico all'avvio.

### Se lo alzi

```python
food_amount = 2.0
```

i boids vengono richiamati verso il centro.

Effetto:

```text
density aumenta
center_x/center_y vanno verso 0.5
suono più compatto
```

---

## `predator_amount: float = 0.0`

È il predatore virtuale controllato dal MIDIMIX.

In `main.py`:

```python
if repeller is None and controls.predator_amount > 0.01:
    repeller = Vector2(WIDTH * 0.5, HEIGHT * 0.5)
```

Quindi se `predator_amount` è alto, il centro dello schermo diventa repulsore.

### Perché 0.0?

Per non far scappare i boids appena parte il programma.

### Se lo alzi

```python
predator_amount = 2.5
```

i boids fuggono dal centro.

Effetto:

```text
spread aumenta
energia aumenta
suono più drammatico
```

---

# 7. Sezione e pausa

## `section_id: int = 0`

Parte da:

```text
intro
```

Perché una performance di solito inizia rarefatta.

Se vuoi partire direttamente in una sezione più intensa:

```python
section_id = 2  # dense
```

oppure:

```python
section_id = 3  # chaos
```

## `paused: bool = False`

Controlla se la simulazione è in pausa.

In `main.py`:

```python
if not controls.paused:
    ...
```

Se `paused = True`, i boids smettono di aggiornarsi.

Si cambia con:

```text
SPACE
```

---

# 8. `section_name`

Nel file c'è:

```python
@property
def section_name(self) -> str:
    return ["intro", "growth", "dense", "chaos", "release", "outro"][self.section_id]
```

Questa proprietà converte `section_id` in un nome testuale.

Esempio:

```python
controls.section_id = 3
print(controls.section_name)
```

Risultato:

```text
chaos
```

Questa proprietà viene usata soprattutto in `markov.py` per cambiare comportamento musicale in base alla sezione.

---

# 9. `as_list`

Nel file c'è:

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

Questa funzione trasforma lo stato dei controlli in una lista numerica.

Serve per inviare lo stato corrente a Max:

```python
self.client.send_message("/aquarium/controls", controls.as_list())
```

Così Max può visualizzare o usare anche i parametri di controllo.

---

# 10. Come ottenere risultati diversi modificando i valori iniziali

## Preset calmo / ambient

```python
density_fader = 0.1
alignment_weight = 1.5
cohesion_weight = 0.6
separation_weight = 1.5
noise_weight = 0.05
food_amount = 0.0
predator_amount = 0.0
section_id = 0
```

Risultato:

```text
movimento fluido
pochi eventi
drone/texture
```

---

## Preset branco compatto

```python
density_fader = 0.35
alignment_weight = 1.2
cohesion_weight = 2.4
separation_weight = 0.7
noise_weight = 0.1
food_amount = 1.5
predator_amount = 0.0
section_id = 2
```

Risultato:

```text
branco compatto
density alta
suono più concentrato
```

---

## Preset caos / predatore

```python
density_fader = 0.85
alignment_weight = 0.4
cohesion_weight = 0.3
separation_weight = 3.0
noise_weight = 1.2
food_amount = 0.0
predator_amount = 2.5
section_id = 3
```

Risultato:

```text
fuga
spread alto
eventi più densi
suono glitch/noise
```

---

## Preset sciame elegante

```python
density_fader = 0.45
alignment_weight = 2.5
cohesion_weight = 1.2
separation_weight = 1.7
noise_weight = 0.15
food_amount = 0.2
predator_amount = 0.0
section_id = 1
```

Risultato:

```text
movimento ordinato
branco fluido
musica più regolare
```

---

# Sintesi

`controls.py` risponde alla domanda:

```text
Qual è lo stato live attuale del sistema?
```

Contiene i parametri che determinano:

- comportamento dei boids;
- densità musicale;
- sezione performativa;
- attrattori e repulsori;
- pausa/play.

Se vuoi aggiungere un nuovo parametro controllabile live, parti da:

```text
Codex/aquarium_boids/controls.py
```

poi dovrai collegarlo a:

```text
midi_in.py      // se deve essere controllato da MIDIMIX
control_in.py   // se deve essere controllato da Max/UDP
boids.py        // se influenza il movimento
markov.py       // se influenza la musica
osc_io.py       // se deve essere mandato a Max
```
