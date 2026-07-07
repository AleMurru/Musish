# Roadmap — Acquario generativo musicale con Markov Chain

## Idea aggiornata del progetto

Il progetto consiste nella creazione di un **ecosistema audiovisivo generativo**: un acquario digitale popolato da pesci stilizzati che si muovono secondo regole semplici di comportamento collettivo. Dai loro movimenti vengono estratti descriptor numerici come velocità, energia, densità, dispersione, direzione media e numero di pesci coinvolti.

Questi dati non controllano direttamente il suono. Al contrario, alimentano un livello intermedio di **generazione musicale simbolica**, basato principalmente su **Markov chain**. Il sistema genera eventi musicali astratti — note, pause, durate, dinamiche, densità, sezioni — che vengono poi renderizzati dal musicista attraverso il suo ambiente musicale: Ableton, Max/MSP, SuperCollider/sclang o altro software scelto dal team.

L'architettura finale è quindi:

```text
Pesci generativi / boids
        ↓
Descriptor visivi e geometrici
        ↓
Conditioning layer
        ↓
Generatore simbolico con Markov chain
        ↓
Eventi MIDI / OSC / JSON
        ↓
Rendering sonoro del musicista
        ↓
Performance audiovisiva live
```

La musica non deve essere pensata come una relazione rigida “un pesce = una nota”. La direzione consigliata è lavorare su una **densità musicale variabile**, in cui il sistema può passare da una generazione collettiva basata sul branco a una generazione più puntiforme basata su singoli pesci o cluster.

---

# Fattibilità in 5 giorni

Il progetto è **fattibile** se viene mantenuta una struttura modulare e se si parte da un MVP molto semplice. Il rischio principale non è creare i pesci o una Markov chain base, ma integrare troppe idee contemporaneamente: simulazione complessa, visual raffinato, generazione musicale sofisticata, controller live, forma musicale, rendering sonoro.

La strategia migliore è:

1. costruire prima un sistema funzionante;
2. aggiungere il livello simbolico Markov;
3. introdurre il controllo live sulla densità;
4. rifinire estetica e performance solo dopo avere una pipeline stabile.

Entro il giorno 2 dovreste avere almeno questo:

```text
pesci in movimento → descriptor → Markov chain → eventi musicali stampati o inviati via OSC/MIDI
```

Anche senza visual complesso o rendering sonoro definitivo, questo costituisce già il cuore del progetto.

---

# Concetto chiave: densità puntiforme vs densità collettiva

La generazione musicale può avvenire su tre livelli:

## 1. Livello globale — branco intero

Il comportamento dell'intero acquario genera pochi eventi musicali macroscopici.

Esempi:

- centroide del branco → registro o panning;
- velocità media → densità ritmica;
- energia totale → dinamica;
- dispersione → ampiezza del range melodico.

Effetto musicale: drone, texture lenta, pochi eventi, musica più ambient.

## 2. Livello intermedio — cluster di pesci

I pesci vengono raggruppati in piccoli branchi o cluster. Ogni cluster può generare una voce musicale.

Esempi:

- cluster 1 → linea melodica;
- cluster 2 → pattern ritmico;
- cluster 3 → layer armonico;
- distanza tra cluster → intervalli o tensione armonica.

Effetto musicale: polifonia controllata, pattern più ricchi, buona leggibilità performativa.

## 3. Livello puntiforme — pesci singoli

Alcuni pesci selezionati possono generare eventi individuali.

Esempi:

- pesce veloce → nota accentata;
- pesce che cambia direzione → evento percussivo;
- pesce isolato → nota lunga o suono solista.

Effetto musicale: granularità, sciame sonoro, glitch, texture densa.

---

# Fader centrale: collectivity / density

Uno dei controlli live più importanti dovrebbe essere un fader dedicato alla relazione tra branco e singoli individui.

Possibili nomi:

- `density_fader`
- `granularity`
- `individuality_collectivity`
- `fish_involvement`

Questo fader controlla:

1. quanti pesci partecipano alla generazione;
2. quante note vengono generate per unità di tempo;
3. quanta polifonia è permessa;
4. se il sistema lavora su branco, cluster o individui;
5. quanto la Markov chain diventa prevedibile o caotica.

## Comportamento del fader

| Valore fader | Interpretazione | Risultato musicale |
|---:|---|---|
| 0.0 | Branco globale | drone, eventi rari, musica lenta |
| 0.25 | Branco + pochi solisti | arpeggi lenti, pattern leggeri |
| 0.5 | Cluster | polifonia moderata, pattern riconoscibili |
| 0.75 | Cluster + individui | densità alta, frammentazione |
| 1.0 | Molti individui | sciame sonoro, glitch, granularità |

## Formula indicativa

```python
density_fader = 0.0  # range 0-1

active_fish_ratio = 0.05 + density_fader * 0.65
n_active_fish = int(total_fish * active_fish_ratio)

max_polyphony = int(1 + density_fader * 12)
events_per_bar = int(2 + density_fader * 30)

temperature = 0.2 + density_fader * 1.2
rest_probability = 0.75 - density_fader * 0.6
```

Nota importante: **numero di pesci coinvolti e numero di note effettive non devono coincidere**. Anche se molti pesci sono coinvolti, il sistema deve avere un limite di polifonia per evitare caos.

---

# Parte generativa 1 — Creazione dei pesci

## Stato interno di ogni pesce

Ogni pesce può essere rappresentato come un agente 2D con questi attributi:

```python
fish = {
    "id": int,
    "position": [x, y],
    "velocity": [vx, vy],
    "acceleration": [ax, ay],
    "size": float,
    "energy": float,
    "species": int,
    "color": tuple,
    "active": bool
}
```

Attributi minimi per l'MVP:

- posizione;
- velocità;
- dimensione;
- id;
- colore.

Attributi utili per versioni più avanzate:

- energia;
- specie;
- stato emotivo: calma, paura, fame, ecc.;
- appartenenza a un cluster.

## Movimento base

Per il primo prototipo è sufficiente un movimento di tipo random walk controllato:

```python
velocity += random_force
velocity = limit(velocity, max_speed)
position += velocity
bounce_on_walls()
```

Questo produce pesci che si muovono in modo organico senza implementare subito il flocking completo.

## Movimento boids

Dal giorno 3 si può passare a un modello boids con tre forze principali:

### Separation

Evita che i pesci si sovrappongano.

```text
se un pesce è troppo vicino → applica forza di repulsione
```

### Alignment

Allinea la direzione di un pesce con quella dei vicini.

```text
velocità del pesce → tende alla velocità media dei vicini
```

### Cohesion

Spinge il pesce verso il centro dei vicini.

```text
posizione del pesce → tende al centro locale del gruppo
```

Il movimento finale può essere:

```python
acceleration = (
    separation_weight * separation_force +
    alignment_weight * alignment_force +
    cohesion_weight * cohesion_force +
    noise_weight * random_force
)
```

Questi pesi possono essere controllati dal musicista o da preset performativi.

## Descriptor estratti dai pesci

I descriptor principali sono:

| Descriptor | Significato | Uso musicale |
|---|---|---|
| `fish_count` | numero di pesci | numero potenziale di voci |
| `mean_speed` | velocità media | densità ritmica |
| `energy` | somma delle velocità | dinamica / velocity |
| `center_x` | centroide orizzontale | panning / scelta registro |
| `center_y` | centroide verticale | ottava / brightness |
| `spread` | dispersione del branco | range melodico |
| `density` | compattezza del branco | tensione armonica |
| `nearest_distance` | distanza media dai vicini | intervalli / rarefazione |
| `cluster_count` | numero di gruppi | numero di layer |
| `direction_coherence` | quanto il branco va nella stessa direzione | stabilità ritmica |

Tutti i descriptor devono essere normalizzati nel range 0-1.

---

# Parte generativa 2 — Markov chain simboliche

## Perché usare Markov chain

Le Markov chain sono adatte perché:

- sono semplici da implementare;
- sono spiegabili;
- possono essere controllate in tempo reale;
- generano pattern musicali con continuità;
- permettono variazioni senza ricorrere a un modello complesso.

Una Markov chain sceglie il prossimo stato in base allo stato corrente e a una matrice di probabilità.

Esempio semplice:

```text
0 → 2 con probabilità 0.5
0 → 4 con probabilità 0.3
0 → 1 con probabilità 0.2
```

Se gli stati sono gradi della scala, il sistema genera melodie.

## Non generare note assolute, ma gradi della scala

È meglio generare eventi simbolici come:

```python
{
    "scale_degree": 2,
    "octave": 1,
    "duration": 0.25,
    "velocity": 90,
    "instrument": "lead",
    "channel": 1
}
```

Invece di:

```python
{
    "midi_note": 62
}
```

Vantaggio: il musicista può cambiare scala, tonalità, accordi e rendering senza modificare la logica generativa.

## Catene consigliate

### 1. Markov chain per pitch

Stati:

```text
0, 1, 2, 3, 4, 5, 6
```

Dove ogni numero è un grado della scala.

Esempio in scala minore:

```text
0 = tonica
1 = seconda
2 = terza minore
3 = quarta
4 = quinta
5 = sesta minore
6 = settima minore
```

### 2. Markov chain per ritmo

Stati:

```text
1/16, 1/8, 1/4, 1/2, rest
```

Il fader di densità può modificare le probabilità:

- fader basso → più durate lunghe e pause;
- fader alto → più sedicesimi e ottavi.

### 3. Markov chain per dinamica

Stati:

```text
soft, medium, loud, accent
```

Può essere condizionata dall'energia dei pesci.

### 4. Markov chain per strumenti/layer

Stati:

```text
drone, bass, lead, perc, granular, noise
```

Può essere condizionata dal numero di cluster o dal livello di densità.

### 5. Markov chain per forma

Stati formali:

```text
intro → growth → dense → chaos → release → outro
```

Questa catena evita che il brano resti sempre uguale.

---

# Conditioning layer

Il conditioning layer traduce i descriptor dei pesci in parametri della Markov chain.

Esempi:

| Descriptor visivo | Parametro Markov |
|---|---|
| `mean_speed` | più eventi ritmici |
| `energy` | velocity più alta |
| `spread` | pitch range più ampio |
| `density` | armonia più compatta o più dissonante |
| `cluster_count` | più layer attivi |
| `direction_coherence` | ritmo più stabile |
| `density_fader` | più note, più pesci coinvolti, più temperatura |

Esempio:

```python
if mean_speed > 0.7:
    rhythm_chain.bias_towards(["1/16", "1/8"])
else:
    rhythm_chain.bias_towards(["1/4", "1/2", "rest"])

if spread > 0.6:
    pitch_range = "wide"
else:
    pitch_range = "narrow"
```

---

# Forma musicale e anti-ripetitività

Per evitare musica troppo ripetitiva, il progetto deve avere un livello di controllo formale.

## Hyperparameter principali

### `section_duration`

Ogni quanti secondi il sistema valuta un cambio di sezione.

```python
section_duration = 45
```

### `novelty_pressure`

Quanto il sistema cerca variazione.

```python
novelty_pressure = 0.6
```

### `temperature`

Quanto le scelte Markov sono prevedibili o imprevedibili.

```python
temperature = 0.2  # stabile
temperature = 1.2  # caotica
```

### `repetition_memory`

Quanti eventi passati vengono ricordati per calcolare ripetitività.

```python
repetition_memory = 64
```

### `max_repetition`

Soglia oltre cui il sistema forza una variazione.

```python
max_repetition = 0.65
```

## Logica di cambio sezione

```python
if time_since_last_section > section_duration:
    if repetition_score > max_repetition:
        force_new_section()
    elif fish_energy > 0.75:
        current_section = "chaos"
    elif fish_density > 0.65:
        current_section = "dense"
    else:
        current_section = form_markov.next(current_section)
```

Ogni sezione modifica i parametri del generatore:

| Sezione | Densità | Temperature | Ritmo | Timbro suggerito |
|---|---:|---:|---|---|
| Intro | bassa | 0.2 | lento | drone/ambient |
| Growth | media | 0.5 | regolare | synth morbido |
| Dense | alta | 0.7 | fitto | polifonia/arpeggi |
| Chaos | molto alta | 1.2 | instabile | glitch/noise |
| Release | media-bassa | 0.4 | rarefatto | riverbero/granulare |
| Outro | bassa | 0.2 | lento | fade/drone |

---

# Criticità del progetto

## 1. Complessità eccessiva

Rischio: provare a implementare boids completi, Markov complesse, visual raffinato, controller, forma e rendering sonoro tutto insieme.

Mitigazione: procedere per MVP. Prima sistema semplice, poi complessità.

## 2. Markov chain troppo ripetitiva

Rischio: pattern riconoscibili ma monotoni.

Mitigazione:

- usare `section_duration`;
- usare `novelty_pressure`;
- cambiare matrice Markov per sezione;
- calcolare `repetition_score`;
- introdurre pause e variazioni di registro.

## 3. Markov chain troppo casuale

Rischio: output senza identità musicale.

Mitigazione:

- generare gradi della scala, non note arbitrarie;
- limitare pitch range;
- usare temperature controllata;
- lasciare al musicista il rendering finale.

## 4. Troppa densità di note

Rischio: effetto caotico e ingestibile.

Mitigazione:

- limitare `max_polyphony`;
- separare pesci coinvolti da note effettivamente generate;
- introdurre `rest_probability`;
- usare cluster invece di singoli pesci.

## 5. Collegamento visual-musica poco leggibile

Rischio: lo spettatore non percepisce la relazione tra pesci e suono.

Mitigazione:

- rendere visibili cluster, pesci attivi e scie;
- usare mapping semplici e riconoscibili;
- mostrare cambi evidenti quando il fader density si muove.

## 6. Integrazione tecnica con il software musicale

Rischio: OSC/MIDI o routing audio non funzionano bene.

Mitigazione:

- testare invio OSC/MIDI entro il giorno 2;
- avere un logger JSON/CSV come fallback;
- avere un rendering sonoro minimo anche fuori dal setup live.

## 7. Controller/mixer analogico

Rischio: usare un mixer analogico come controller può richiedere lavoro extra.

Mitigazione:

- usare un MIDI controller come fallback;
- implementare mapping da tastiera o GUI;
- integrare il mixer solo dopo avere la pipeline stabile.

---

# Roadmap dettagliata aggiornata

## Giorno 1 — Simulazione base e descriptor

### Obiettivo

Creare l'acquario digitale con pesci in movimento e calcolare descriptor numerici.

### Task

1. Scegliere stack tecnico: Python/Pygame, TouchDesigner, Max/Jitter o p5.js.
2. Creare canvas/acquario 2D.
3. Implementare pesci con posizione, velocità e dimensione.
4. Implementare movimento base: random walk + rimbalzo sui bordi.
5. Calcolare descriptor:
   - `fish_count`;
   - `mean_speed`;
   - `energy`;
   - `center_x`, `center_y`;
   - `spread`;
   - `density`;
   - `nearest_distance`.
6. Normalizzare tutto in range 0-1.
7. Mostrare descriptor a schermo o in console.
8. Salvare log CSV/JSON.

### Deliverable

- Pesci in movimento.
- Descriptor funzionanti.
- Log dei dati.

---

## Giorno 2 — Markov MVP e output simbolico

### Obiettivo

Creare un generatore simbolico base collegato ai descriptor.

### Task

1. Implementare Markov chain per pitch.
2. Implementare Markov chain per ritmo.
3. Implementare Markov chain per dinamica.
4. Generare eventi simbolici:

```json
{
  "degree": 2,
  "duration": 0.25,
  "velocity": 80,
  "layer": "lead"
}
```

5. Condizionare la generazione con i descriptor:
   - velocità → ritmo;
   - energia → velocity;
   - spread → pitch range;
   - densità → dissonanza/registro;
   - numero pesci → layer attivi.
6. Stampare eventi in console.
7. Inviare eventi via OSC/MIDI o salvarli in JSON.

### Deliverable

- Pesci → descriptor → Markov → eventi musicali.
- Una prima connessione con il software del musicista, anche minimale.

---

## Giorno 3 — Fader density e controllo live

### Obiettivo

Rendere il sistema performativo e controllabile.

### Task

1. Implementare `density_fader`.
2. Collegare `density_fader` a:
   - numero di pesci coinvolti;
   - eventi per battuta;
   - max polyphony;
   - rest probability;
   - temperature;
   - livello globale/cluster/individuale.
3. Aggiungere controlli live:
   - tastiera;
   - MIDI controller;
   - mixer analogico solo se già testato.
4. Implementare cluster semplici o selezione dei pesci attivi.
5. Testare con il musicista.

### Deliverable

- Un fader che cambia chiaramente la densità musicale.
- Passaggio percepibile da branco collettivo a sciame puntiforme.

---

## Giorno 4 — Forma, sezioni e anti-ripetitività

### Obiettivo

Evitare loop monotoni e dare una struttura al brano.

### Task

1. Implementare `section_duration`.
2. Implementare stati formali:
   - intro;
   - growth;
   - dense;
   - chaos;
   - release;
   - outro.
3. Implementare `repetition_score`.
4. Implementare `novelty_pressure`.
5. Cambiare matrici Markov in base alla sezione.
6. Definire una performance di 3-5 minuti.
7. Raffinare visual: scie, pesci attivi, cluster, colori per sezione.

### Deliverable

- Brano non statico.
- Sezioni riconoscibili.
- Performance provabile dall'inizio alla fine.

---

## Giorno 5 — Stabilizzazione e presentazione

### Obiettivo

Rendere il progetto robusto e presentabile.

### Task

1. Stabilizzare codice e patch audio.
2. Salvare preset.
3. Testare routing MIDI/OSC.
4. Registrare video/audio finale.
5. Preparare fallback:
   - dati preregistrati;
   - video preregistrato;
   - generatore Markov autonomo senza visual;
   - controllo da tastiera se il controller fallisce.
6. Preparare spiegazione tecnica e artistica.

### Deliverable finale

- Demo audiovisiva live o semi-live.
- Sistema stabile.
- Recording di backup.
- Descrizione chiara del progetto.

---

# MVP minimo garantito

Se qualcosa va storto, il progetto minimo deve includere:

1. pesci 2D in movimento;
2. descriptor normalizzati;
3. Markov chain per pitch e ritmo;
4. eventi musicali esportati o inviati;
5. fader/parametro di densità;
6. registrazione dimostrativa.

Questo è sufficiente per raccontare il cuore del progetto.

---

# Versione ideale

Se tutto procede bene, la versione finale include:

- movimento boids completo;
- cluster di pesci;
- Markov chain multiple;
- fader collectivity/density;
- forma musicale con sezioni;
- anti-ripetitività;
- rendering sonoro curato dal musicista;
- visual con scie, cluster e pesci attivi;
- performance strutturata di 3-5 minuti.
