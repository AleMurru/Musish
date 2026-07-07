# Diario di lavoro — Acquario generativo musicale

## Roadmap / Stato (agg. 2026-07-07)

Progetto a 5 giorni, team di 3 (2 data scientist + 1 esperto musica elettronica). Fase attuale: **fine planning, inizio implementazione**. ~1200 righe di spec su 5 file, 0 righe di codice → priorità: smettere di pianificare e costruire.

- [ ] **D1** — Stack deciso (candidati: TouchDesigner+Ableton / Max-Jitter / pygame / p5+Tone.js) · boids/random-walk base · descrittori normalizzati 0-1 · **contratto OSC congelato** · logger CSV/JSON.
- [ ] **D2** — Generatore simbolico Markov (pitch+rhythm condizionate) · invio OSC/MIDI · prima connessione col musicista.
- [ ] **D3** — Controlli live: `density_fader` + **controlli ecosistema (food/cohesion, predator/turbulence)** · cluster.
- [ ] **D4** — Forma affidata al musicista (fader sezione) invece di form-chain automatica · rifinitura visual.
- [ ] **D5** — Stabilizzazione, preset, fallback offline, recording, presentazione.

**Decisioni aperte bloccanti:** stack; ambiente musicista (SuperCollider/Ableton/Max — verificare se "slack" = sclang); mixer analogico requisito o estetica; ownership del clock (Ableton Link?).

---

## Concept attuale

Il progetto consiste nella creazione di un **ecosistema audiovisivo generativo**: un acquario digitale popolato da pesci stilizzati che si muovono secondo regole semplici di comportamento collettivo. Dai loro movimenti vengono estratti descriptor numerici e geometrici. Questi descriptor alimentano un sistema di **generazione musicale simbolica** basato su Markov chain. Gli eventi prodotti vengono poi renderizzati dal musicista tramite il suo ambiente musicale.

Il sistema non vuole produrre automaticamente un brano finito, ma costruire uno **strumento performativo** in cui:

- i pesci generano movimento e dati;
- i dati condizionano processi musicali simbolici;
- il musicista interpreta e renderizza il materiale generato;
- alcuni fader permettono di controllare dal vivo la forma e la densità musicale.

---

## Decisione progettuale importante

Abbiamo deciso di non usare una relazione rigida:

```text
1 pesce = 1 nota
```

Questa soluzione sarebbe troppo puntiforme, caotica e poco controllabile.

La direzione scelta è una generazione a **densità variabile**, in cui il sistema può lavorare su tre livelli:

1. **Branco intero** — pochi eventi, comportamento globale, musica più ambient.
2. **Cluster di pesci** — più voci musicali, polifonia controllata.
3. **Pesci singoli selezionati** — eventi più densi, granulari o glitch.

Questa transizione viene controllata da un fader dedicato.

---

## Fader centrale: density / collectivity

Uno dei controlli principali del progetto sarà un fader che controlla quanto la generazione musicale è collettiva o puntiforme.

Possibili nomi:

- `density_fader`
- `granularity`
- `individuality_collectivity`
- `fish_involvement`

### Comportamento

| Fader | Generazione | Risultato musicale |
|---:|---|---|
| 0.0 | branco globale | drone, eventi rari, texture lenta |
| 0.25 | branco + pochi pesci attivi | arpeggi lenti, pattern leggeri |
| 0.5 | cluster | polifonia moderata, pattern riconoscibili |
| 0.75 | cluster + individui | densità alta, frammentazione |
| 1.0 | molti individui | sciame sonoro, granularità, glitch |

Il fader non controlla semplicemente il volume o il numero di note, ma un insieme di parametri:

- numero di pesci coinvolti;
- numero di eventi per battuta;
- probabilità di pausa;
- massima polifonia;
- temperatura della Markov chain;
- passaggio da livello globale a livello individuale.

Formula indicativa:

```python
density_fader = 0.0  # range 0-1

active_fish_ratio = 0.05 + density_fader * 0.65
n_active_fish = int(total_fish * active_fish_ratio)

max_polyphony = int(1 + density_fader * 12)
events_per_bar = int(2 + density_fader * 30)

temperature = 0.2 + density_fader * 1.2
rest_probability = 0.75 - density_fader * 0.6
```

---

## Parte generativa visuale — creazione dei pesci

Ogni pesce viene rappresentato come un agente 2D con uno stato interno.

### Stato minimo

```python
fish = {
    "id": int,
    "position": [x, y],
    "velocity": [vx, vy],
    "size": float,
    "color": tuple
}
```

### Stato esteso possibile

```python
fish = {
    "id": int,
    "position": [x, y],
    "velocity": [vx, vy],
    "acceleration": [ax, ay],
    "size": float,
    "energy": float,
    "species": int,
    "cluster_id": int,
    "mood": "calm/fear/hungry",
    "active": bool
}
```

### Movimento base per MVP

Per i primi giorni useremo movimento semplice:

```python
velocity += random_force
velocity = limit(velocity, max_speed)
position += velocity
bounce_on_walls()
```

Questo è sufficiente per ottenere movimento organico e descriptor utilizzabili.

### Movimento boids successivo

In una versione più avanzata, i pesci seguono tre regole principali:

1. **Separation** — evitare collisioni.
2. **Alignment** — allinearsi alla direzione dei vicini.
3. **Cohesion** — muoversi verso il centro del gruppo.

Formula complessiva:

```python
acceleration = (
    separation_weight * separation_force +
    alignment_weight * alignment_force +
    cohesion_weight * cohesion_force +
    noise_weight * random_force
)
```

I pesi possono diventare controlli live o preset performativi.

---

## Descriptor estratti dai pesci

I descriptor sono il ponte tra visual e musica.

| Descriptor | Descrizione | Uso musicale |
|---|---|---|
| `fish_count` | numero di pesci | numero potenziale di layer |
| `mean_speed` | velocità media | densità ritmica |
| `energy` | energia totale del movimento | dinamica / velocity |
| `center_x` | centroide orizzontale | panning / registro |
| `center_y` | centroide verticale | brightness / ottava |
| `spread` | dispersione del branco | range melodico |
| `density` | compattezza del branco | tensione armonica |
| `nearest_distance` | distanza media dai vicini | intervalli / rarefazione |
| `cluster_count` | numero di gruppi | numero di voci musicali |
| `direction_coherence` | coerenza direzionale | stabilità ritmica |

Tutti i descriptor devono essere normalizzati nel range 0-1 per poter essere usati facilmente nel mapping.

---

## Parte generativa musicale — Markov chain

Le Markov chain generano eventi musicali simbolici. Non producono direttamente audio, ma istruzioni musicali.

Esempio di evento:

```json
{
  "degree": 2,
  "octave": 1,
  "duration": 0.25,
  "velocity": 82,
  "layer": "lead",
  "channel": 1
}
```

### Perché generare gradi della scala

È preferibile generare `degree` invece di note MIDI assolute.

Esempio:

```text
0 = tonica
1 = seconda
2 = terza
3 = quarta
4 = quinta
5 = sesta
6 = settima
```

Così il musicista può cambiare scala, tonalità e armonia senza modificare il generatore.

### Catene Markov previste

#### Pitch chain

Genera il prossimo grado melodico.

```text
0 → 2 → 4 → 3 → 1 → 0
```

#### Rhythm chain

Genera durate e pause.

```text
1/16, 1/8, 1/4, 1/2, rest
```

#### Dynamic chain

Genera intensità.

```text
soft, medium, loud, accent
```

#### Layer chain

Sceglie quale voce musicale attivare.

```text
drone, bass, lead, perc, granular, noise
```

#### Form chain

Controlla la macro-struttura.

```text
intro → growth → dense → chaos → release → outro
```

---

## Conditioning: come i pesci influenzano Markov

I pesci non decidono direttamente ogni nota. I loro descriptor modificano le probabilità delle Markov chain.

Esempi:

```python
if mean_speed > 0.7:
    rhythm_chain.bias_towards(["1/16", "1/8"])
else:
    rhythm_chain.bias_towards(["1/4", "1/2", "rest"])
```

```python
if spread > 0.6:
    pitch_range = "wide"
else:
    pitch_range = "narrow"
```

```python
if density_fader > 0.75:
    temperature = 1.1
    rest_probability = 0.2
    max_polyphony = 10
else:
    temperature = 0.3
    rest_probability = 0.65
    max_polyphony = 2
```

---

## Forma musicale e anti-ripetitività

Per evitare una musica troppo ripetitiva useremo hyperparameter dedicati.

### Hyperparameter principali

| Nome | Funzione |
|---|---|
| `section_duration` | ogni quanti secondi valutare un cambio sezione |
| `novelty_pressure` | quanto il sistema cerca novità |
| `temperature` | quanto la Markov chain è prevedibile o caotica |
| `repetition_memory` | quanti eventi passati ricordare |
| `max_repetition` | soglia oltre cui forzare variazione |

Esempio:

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

---

## Criticità individuate

### 1. Troppa complessità

Il rischio principale è voler implementare tutto subito: boids, Markov, visual raffinato, controller, forma, rendering sonoro.

Soluzione: costruire prima un MVP semplice.

### 2. Output musicale troppo ripetitivo

Le Markov chain semplici possono generare pattern monotoni.

Soluzione:

- usare sezioni;
- cambiare matrici per sezione;
- usare novelty pressure;
- monitorare repetition score.

### 3. Output musicale troppo casuale

Se la temperature è troppo alta, il risultato perde identità.

Soluzione:

- limitare range melodico;
- usare scale musicali;
- introdurre pause;
- affidare il rendering timbrico al musicista.

### 4. Densità eccessiva

Se molti pesci generano molte note, il risultato diventa ingestibile.

Soluzione:

- limitare max polyphony;
- non fare 1 pesce = 1 nota;
- usare cluster;
- distinguere pesci coinvolti da note effettivamente prodotte.

### 5. Relazione visual-musica poco chiara

Se i mapping sono troppo astratti, il pubblico non capisce il collegamento.

Soluzione:

- evidenziare i pesci attivi;
- mostrare cluster;
- rendere visibile il fader density;
- usare cambi musicali percepibili.

### 6. Integrazione tecnica

OSC/MIDI e software musicale possono creare problemi.

Soluzione:

- testare connessione entro il giorno 2;
- salvare eventi JSON/CSV;
- preparare un fallback offline.

---

## Prossimi step immediati

### Step 1

Implementare pesci 2D con movimento base.

### Step 2

Calcolare descriptor normalizzati.

### Step 3

Implementare Markov chain minima per pitch e ritmo.

### Step 4

Generare eventi simbolici in console o JSON.

### Step 5

Aggiungere `density_fader` come parametro manuale.

### Step 6

Collegare output al software del musicista.

---

## Sintesi attuale

Il cuore del progetto è:

```text
movimento collettivo → descriptor → Markov chain condizionate → eventi simbolici → rendering live
```

La scelta artistica più forte è il fader che controlla la transizione tra:

```text
branco collettivo ↔ cluster ↔ pesci individuali
```

Questo permette di avere una musica non solo reattiva, ma realmente performativa.

---

## 2026-07-07

**Processi svolti:** rilettura completa dei 5 file di progetto (`roadmap`, `Diario`, `confronto`, `Ultima_risposta`, duplicato `mnusicale`); analisi critica di spec + questione Markov vs transformer; sintesi dello stato reale del progetto.

**Idee/criticità principali proposte:**
- **Percepibilità dell'accoppiamento = rischio #1** (declassato a #5 nei doc): boids e Markov sono due generatori autonomi mal collegati. Fix: aggiungere ≥1 **mapping diretto e immediato** (pesce veloce → transiente udibile ora) come prova percettiva, oltre alla Markov.
- **Markov è la scelta giusta, non "troppo semplice"**; un transformer simbolico peggiorerebbe (conditioning live difficile, black-box, serve corpus, latenza). Il difetto vero della Markov ord-1 (memoria corta) si risolve con **VMM/PPM** o **Markov gerarchica** (chain lenta forma/armonia + chain veloce note condizionate sull'accordo), o **Factor/Audio Oracle** (OMax/PyOracle) per il live. Non con un transformer.
- **Manca un motore armonico**: gradi su scala fissa per 5 min = armonicamente piatto. Aggiungere progressione di accordi lenta, generare gradi relativi all'accordo corrente.
- **Contraddizione tra `confronto` e `roadmap`**: il concept forte (musicista *governa l'ecosistema*: food→aggregazione→consonanza, predator→fuga→dissonanza) è sparito nella roadmap, che tiene solo il `density_fader`. Raccomandato riportare al centro il controllo dell'ecosistema.
- **Affidare la macro-forma al musicista** (fader sezione) invece della form-chain automatica → elimina il sottosistema più fragile.
- **Catene indipendenti** (pitch/rhythm scorrelati) → condizionare ritmo su pitch/sezione o stato congiunto.
- **Filtrare i descrittori** (one-euro filter) contro il jitter dei boids.
- Ordine di taglio se il tempo stringe: tenere boids base + 2 descrittori + mapping diretto + Markov pitch/rhythm + OSC; buttare per primi form-chain automatica, 5ª Markov, mood emotivi, mixer analogico.

**Modifiche ai file:**
- 2026-07-07 10:14 — aggiornato `Diario_di_lavoro.md`: aggiunta sezione "Roadmap / Stato" in cima e questo log di sessione. Nessun codice prodotto (in attesa di scelta utente: consolidare i doc [A] vs scrivere scaffold Python del generatore gerarchico + boids + OSC [B]).

## 2026-07-07 — Implementazione MVP Boids + Max

**Decisione utente:** rendering in **Max**; simulazione movimento con modello **boids**. Analizzato e clonato come riferimento `https://github.com/Shivank1006/Bird-Flocking-Simulation` in `references/Bird-Flocking-Simulation`.

**Elementi presi dal riferimento:** regole `alignment`, `cohesion`, `separation`; pesi live per le tre forze; limite `max_force`/`max_speed`; disegno triangolare orientato sulla velocità.

**Codice prodotto:**
- `main.py` — loop Pygame, simulazione, controlli, invio OSC, logging.
- `aquarium_boids/boids.py` — modello boids completo + food/predator via mouse.
- `aquarium_boids/descriptors.py` — descriptor normalizzati + smoothing low-pass.
- `aquarium_boids/markov.py` — generatore simbolico Markov pitch/rhythm/layer + progressione armonica minima.
- `aquarium_boids/osc_io.py` — invio OSC verso Max.
- `docs/OSC_CONTRACT.md` — contratto OSC congelato per Max.
- `max/aquarium_receiver.maxpat` — patch Max minima per ricevere e stampare i messaggi OSC.
- `README.md`, `requirements.txt` — setup e istruzioni.

**Test eseguiti:** `python -m py_compile main.py aquarium_boids/*.py`; validazione JSON della patch `.maxpat`.
