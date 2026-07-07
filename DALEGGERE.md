# DA LEGGERE — Boids e Markov Chain nel progetto

Questo documento spiega i due blocchi fondamentali del progetto:

1. **Boids** — come generiamo il movimento dei pesci.
2. **Markov chain** — come dal movimento dei pesci generiamo eventi musicali simbolici da passare al musicista.

---

# 1. Boids: generazione del movimento dei pesci

I **boids** sono un modello classico per simulare il comportamento collettivo di animali come stormi di uccelli, banchi di pesci o sciami.

L'idea è semplice: ogni pesce non conosce l'intero sistema, ma osserva solo i suoi vicini e decide come muoversi secondo alcune regole locali.

Il risultato può sembrare molto naturale: i pesci si aggregano, si separano, cambiano direzione insieme e formano branchi.

---

## Ogni pesce è un agente

Ogni pesce ha uno stato interno:

```python
fish = {
    "id": 0,
    "position": [x, y],
    "velocity": [vx, vy],
    "acceleration": [ax, ay],
    "size": 8,
    "energy": 0.5
}
```

A ogni frame aggiorniamo:

```text
posizione
velocità
direzione
energia
```

Quindi il pesce non è solo una forma grafica, ma un piccolo agente dinamico.

---

# Le tre regole principali dei boids

## 1. Separation — separazione

Serve a evitare che i pesci si sovrappongano.

Se un pesce vede un vicino troppo vicino, si allontana.

```text
“Non andare addosso agli altri”
```

Effetto visivo:

- i pesci evitano collisioni;
- il branco respira;
- non diventano tutti un punto unico.

Effetto musicale possibile:

- molta separazione → musica più sparsa;
- poca separazione → musica più densa.

---

## 2. Alignment — allineamento

Ogni pesce tende ad allineare la propria direzione con quella dei vicini.

```text
“Vai più o meno nella stessa direzione del gruppo”
```

Effetto visivo:

- il branco si muove in modo coerente;
- i pesci sembrano seguire una corrente comune.

Effetto musicale possibile:

- alto alignment → ritmo più regolare;
- basso alignment → ritmo più instabile.

---

## 3. Cohesion — coesione

Ogni pesce tende ad avvicinarsi al centro dei suoi vicini.

```text
“Resta vicino al gruppo”
```

Effetto visivo:

- si formano branchi;
- i pesci non si disperdono troppo.

Effetto musicale possibile:

- alta coesione → armonia più compatta;
- bassa coesione → range melodico più ampio.

---

# Movimento finale del pesce

A ogni frame il pesce riceve diverse forze:

```python
acceleration = (
    separation_weight * separation_force +
    alignment_weight * alignment_force +
    cohesion_weight * cohesion_force +
    noise_weight * random_force
)
```

Poi aggiorna la velocità e la posizione:

```python
velocity += acceleration
velocity = limit(velocity, max_speed)
position += velocity
```

Quindi i parametri principali sono:

```text
separation_weight
alignment_weight
cohesion_weight
noise_weight
max_speed
```

Questi parametri possono anche essere controllati live dal musicista.

---

# Esempio performativo con i boids

Se aumentiamo `cohesion_weight`, i pesci si stringono in branco.

Questo può generare:

```text
visivo: banco compatto
musica: meno note, armonia più chiusa, suono più denso
```

Se aumentiamo `noise_weight`, i pesci diventano agitati.

Questo può generare:

```text
visivo: movimento caotico
musica: più note brevi, più glitch, Markov più imprevedibile
```

---

# 2. Markov chain: generazione dell'output simbolico

La Markov chain è il livello che trasforma i dati dei pesci in **materiale musicale astratto**.

Non genera direttamente suono.  
Genera istruzioni musicali.

Per esempio:

```json
{
  "degree": 2,
  "octave": 1,
  "duration": 0.25,
  "velocity": 82,
  "layer": "lead"
}
```

Questo evento significa:

```text
suona il grado 2 della scala,
all'ottava +1,
per durata 0.25,
con intensità 82,
sul layer lead
```

Poi il musicista decide come renderizzarlo:

- con un synth;
- con un campione;
- con SuperCollider;
- con Ableton;
- con Max/MSP;
- con effetti, riverberi, granular synthesis, ecc.

---

# Cos'è una Markov chain in pratica

Una Markov chain sceglie il prossimo stato in base allo stato attuale.

Esempio semplice per le altezze:

```text
Se sono sul grado 0:
- posso andare al grado 2 con probabilità 50%
- posso andare al grado 4 con probabilità 30%
- posso restare sul grado 0 con probabilità 20%
```

Quindi non è totalmente casuale: ha una memoria minima.

---

## Esempio di Markov chain melodica

Stati:

```text
0, 1, 2, 3, 4, 5, 6
```

Questi non sono MIDI note assolute, ma **gradi della scala**.

In una scala minore:

```text
0 = tonica
1 = seconda
2 = terza minore
3 = quarta
4 = quinta
5 = sesta minore
6 = settima minore
```

La Markov chain potrebbe generare:

```text
0 → 2 → 4 → 3 → 2 → 0
```

Se la tonalità scelta dal musicista è A minor, questo diventa:

```text
A → C → E → D → C → A
```

Se il musicista cambia tonalità in D minor, diventa:

```text
D → F → A → G → F → D
```

Il pattern rimane coerente, ma il rendering armonico è nelle mani del musicista.

---

# Non una sola Markov chain, ma più chain

Il sistema dovrebbe avere più Markov chain parallele.

## 1. Markov chain per pitch

Genera il grado della scala.

Output:

```json
"degree": 4
```

---

## 2. Markov chain per ritmo

Genera durata o pausa.

Stati:

```text
1/16, 1/8, 1/4, 1/2, rest
```

Output:

```json
"duration": 0.25
```

oppure:

```json
"event_type": "rest"
```

---

## 3. Markov chain per dinamica

Genera intensità.

Stati:

```text
soft, medium, loud, accent
```

Output:

```json
"velocity": 90
```

---

## 4. Markov chain per layer

Sceglie quale voce musicale deve suonare.

Stati:

```text
drone, bass, lead, perc, granular
```

Output:

```json
"layer": "bass"
```

---

## 5. Markov chain per forma

Controlla la macro-struttura.

Stati:

```text
intro, growth, dense, chaos, release, outro
```

Output:

```json
"section": "dense"
```

---

# Come i pesci condizionano la Markov chain

I descriptor dei pesci non dicono direttamente:

```text
suona Do, poi Mi, poi Sol
```

Piuttosto modificano le probabilità.

---

## Pesci lenti

```text
mean_speed basso
```

La Markov rhythm chain favorisce:

```text
durate lunghe
pause
pochi eventi
```

Output possibile:

```json
{
  "degree": 0,
  "duration": 1.0,
  "velocity": 45,
  "layer": "drone"
}
```

---

## Pesci veloci

```text
mean_speed alto
```

La Markov rhythm chain favorisce:

```text
durate brevi
più eventi
meno pause
```

Output possibile:

```json
{
  "degree": 4,
  "duration": 0.125,
  "velocity": 95,
  "layer": "perc"
}
```

---

## Branco compatto

```text
density alta
spread basso
```

Il sistema può favorire:

```text
range melodico stretto
armonia compatta
meno salti
```

---

## Branco disperso

```text
spread alto
density bassa
```

Il sistema può favorire:

```text
range melodico ampio
più ottave
più salti
più spazializzazione
```

---

# Esempio completo di generazione

Immaginiamo questo stato dei pesci:

```python
descriptors = {
    "mean_speed": 0.75,
    "energy": 0.8,
    "density": 0.3,
    "spread": 0.7,
    "cluster_count": 3,
    "direction_coherence": 0.4
}
```

Interpretazione:

```text
pesci veloci
molta energia
branco disperso
3 cluster
movimento poco allineato
```

Il sistema decide:

```text
ritmo più fitto
velocity alta
range melodico ampio
3 layer attivi
temperature abbastanza alta
```

Output simbolico:

```json
[
  {
    "time": 0.0,
    "degree": 2,
    "octave": 0,
    "duration": 0.125,
    "velocity": 92,
    "layer": "lead"
  },
  {
    "time": 0.125,
    "degree": 5,
    "octave": 1,
    "duration": 0.125,
    "velocity": 88,
    "layer": "perc"
  },
  {
    "time": 0.25,
    "degree": 4,
    "octave": -1,
    "duration": 0.25,
    "velocity": 80,
    "layer": "bass"
  }
]
```

Il musicista riceve questi eventi e li trasforma in suono.

---

# Il ruolo del fader density

Il fader immaginato è molto importante.

Non controlla solo “più note o meno note”.  
Controlla il passaggio tra tre regimi:

```text
branco → cluster → individui
```

---

## Fader basso: comportamento collettivo

```text
density_fader = 0.0
```

Il sistema considera il branco come una sola entità.

Output:

```json
{
  "degree": 0,
  "duration": 2.0,
  "velocity": 50,
  "layer": "drone"
}
```

Musicalmente:

```text
pochi eventi
suoni lunghi
texture lenta
```

---

## Fader medio: comportamento per cluster

```text
density_fader = 0.5
```

Il sistema raggruppa i pesci in cluster.  
Ogni cluster può generare una voce.

Output:

```json
[
  {"degree": 0, "duration": 0.5, "layer": "bass"},
  {"degree": 3, "duration": 0.25, "layer": "lead"},
  {"degree": 4, "duration": 0.25, "layer": "perc"}
]
```

Musicalmente:

```text
polifonia controllata
pattern riconoscibili
3-4 layer attivi
```

---

## Fader alto: comportamento individuale

```text
density_fader = 1.0
```

Il sistema seleziona più pesci attivi e genera più eventi.

Output:

```json
[
  {"degree": 1, "duration": 0.125, "layer": "granular"},
  {"degree": 5, "duration": 0.125, "layer": "perc"},
  {"degree": 2, "duration": 0.0625, "layer": "lead"},
  {"degree": 6, "duration": 0.125, "layer": "noise"}
]
```

Musicalmente:

```text
sciame sonoro
glitch
molti micro-eventi
densità alta
```

Importante: anche con fader alto non fate suonare tutti i pesci.  
Serve sempre un limite:

```python
max_polyphony = 8
```

---

# Forma finale dell'output per il musicista

Potete passare al musicista tre tipi di output.

---

## Opzione 1 — OSC

Messaggi tipo:

```text
/music/event degree 2 octave 1 duration 0.25 velocity 82 layer lead
/music/section dense
/music/density 0.7
/music/energy 0.8
```

Ottimo per Max/MSP, SuperCollider, TouchDesigner.

---

## Opzione 2 — MIDI

Convertite gli eventi in note MIDI.

Esempio:

```text
note_on 64 velocity 82 channel 1
note_off 64 after 0.25
```

Ottimo per Ableton.

---

## Opzione 3 — JSON/CSV

Per debug o fallback:

```json
{
  "time": 12.5,
  "section": "dense",
  "events": [
    {
      "degree": 2,
      "octave": 1,
      "duration": 0.25,
      "velocity": 82,
      "layer": "lead"
    }
  ]
}
```

Ottimo se volete registrare una performance e renderizzarla dopo.

---

# Riassunto essenziale

## Boids

Servono a generare pesci che si muovono in modo naturale.

```text
separation → non collidere
alignment → seguire direzione dei vicini
cohesion → restare nel gruppo
```

Da questi movimenti estraete descriptor.

---

## Markov chain

Servono a generare materiale musicale simbolico.

```text
pitch chain → quale grado della scala
rhythm chain → quale durata
dynamic chain → quale intensità
layer chain → quale voce
form chain → quale sezione
```

I descriptor dei pesci modificano le probabilità delle chain.

---

## Output finale

Il sistema produce eventi tipo:

```json
{
  "degree": 4,
  "octave": 1,
  "duration": 0.25,
  "velocity": 90,
  "layer": "lead"
}
```

Il musicista prende questi eventi e decide come trasformarli in suono.
