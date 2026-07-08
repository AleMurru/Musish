# Diario di lavoro — Acquario generativo musicale

## Roadmap / Stato (agg. 2026-07-07)

Progetto a 5 giorni, team di 3 (2 data scientist + 1 esperto musica elettronica). Fase attuale: **implementazione avviata, due codebase parallele**.

**Stack deciso:** Python (pygame + numpy) · OSC · **rendering musicale in Max** (esiste già `Codex/.../max/aquarium_receiver.maxpat`).

**Due codebase (tenute separate per decisione utente):**
- `Codex/` = **base UFFICIALE**. Boids OO + Markov completa (accordi, sezioni, layer) + OSC verso Max + patch ricevitore. OSC `:7400`, namespace `/aquarium/*` e `/music/*`.
- `Claude/` = versione di confronto/laboratorio. Boids vettorizzati numpy + **eventi discreti diretti** (dart/turn/collision) per la percepibilità. OSC `:9000`, namespace `/aq/*`. Niente Markov (per ora).

- [x] **D1** — stack deciso · boids base (entrambe) · descrittori 0-1 · contratto OSC congelato (entrambe) · logger CSV.
- [x] **D2** — Markov pitch/rhythm + accordi/sezioni/layer (fatta in Codex) · invio OSC verso Max.
- [ ] **D3** — controlli live: `density_fader` + ecosistema (food/predator) presenti · manca cluster reale (ora grid-occupancy).
- [ ] **D4** — forma: in Codex già manuale (tasti 1-6) ✓ · rifinitura visual.
- [ ] **D5** — stabilizzazione, preset, fallback, recording, presentazione.

**Decisioni ancora aperte:** quale base tenere dopo il confronto a orecchio (utente decide dopo aver visto/sentito l'output); mixer analogico requisito o estetica; ownership del clock (Ableton Link / BPM in Max?).

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

## 2026-07-07 (pomeriggio) — Versione Claude separata, verifica base ufficiale, analisi repo

**Processi svolti:**
- Setup ambiente: `.venv` condiviso in root (Python 3.14.4, numpy 2.5.1, python-osc, pygame-ce 2.5.7).
- Scritto un core alternativo (versione Claude): boids **vettorizzati numpy** con controlli-ecosistema (food/predator/turbulence), descrittori 0-1 con smoothing EMA, **eventi discreti diretti** (dart/turn/collision) via OSC, emitter OSC, visual pygame.
- Tuning eventi: il primo tentativo generava ~280 dart/s (raffica inascoltabile) → ridisegnato il dart come **outlier statistico** (velocità > media + 2.4σ del branco) + cooldown globali → ~1.8 dart/s, radi e salienti.
- **Ispezionata e verificata la base ufficiale `Codex/`** (headless harness senza pygame): gira, produce eventi Markov coerenti (gradi/accordi/sezioni/layer, mix note/rest). Contiene già progressione accordi, sezioni manuali (tasti 1-6), OSC verso Max.
- Su richiesta utente, **spostato tutto il mio lavoro in `Claude/`** per evitare collisioni con la base ufficiale; verificato che gira dalla nuova posizione (smoke test + dry-run headless OK).
- Analizzato `github.com/beneater/boids`: JS/canvas, MIT, didattico → **niente da riusare** (i nostri boids Python fanno già coherence/separation/alignment/visualRange). Utile solo in caso di pivot del visual nel browser (p5.js/Tone.js).

**Idee/criticità principali:**
- Rischio #1 ribadito = **percepibilità del legame visual↔audio**. La base Codex fa flash su pesce *casuale*; la versione Claude emette eventi sul pesce *causale* → se si tiene Codex, travasare lì gli eventi discreti è l'intervento a più alto valore.
- `energy` in Codex è un duplicato di `mean_speed` (descrittore ridondante — da differenziare).

**Modifiche ai file (2026-07-07 pomeriggio):**
- 12:20–12:45 — creato package `Claude/aquarium/` (`config.py`, `boids.py`, `descriptors.py`, `osc_out.py`, `__init__.py`), `Claude/run_claude_version.py`, `Claude/smoke_test.py`, `Claude/README.md`.
- 12:48 — spostati i file mie in `Claude/`; aggiornati i comandi di avvio nei docstring; aggiornata la Roadmap in cima al Diario.
- Root: `main.py` orfano (importa `aquarium_boids` da root, non parte) segnalato all'utente — in attesa di ok per rimozione.

**Prossimo passo proposto:** ricevitore OSC di test (o patch Max minima) per confronto "a orecchio" delle due versioni senza configurare il DAW.

## 2026-07-07 (sera) — Upload su GitHub + Markov gerarchica (versione Claude, D2)

**Processi svolti:**
- **Upload `Claude/` su GitHub** (`AleMurru/Musish`). La cartella era esclusa dal `.gitignore` (blocco "local experiments", reintrodotto da linter/sync) → aggiunta con `git add -f` **senza modificare il `.gitignore`** (i file tracciati non vengono più ignorati) ed escludendo i `.pyc`. Commit `4810768`. Push: primo tentativo fallito per DNS (sandbox), **verificato che `4810768` è su `origin/main`** via merge-base → upload confermato.
- Verificato che `github.com/beneater/boids` (JS/canvas, MIT) **non è riusabile** — i boids Python fanno già coherence/separation/alignment/visualRange. Utile solo per eventuale pivot del visual nel browser.
- Implementato il **D2 della versione Claude**: generatore **Markov gerarchico con motore armonico** (mia raccomandazione ripetuta contro le catene indipendenti/piatte).

**Idea principale (Markov gerarchica):**
- Catena **lenta** = progressione accordi in minore (i→VI→iv→V, con risoluzione), cambio ogni ~8 eventi.
- Catena **veloce** = grado melodico, poi **agganciato alle note dell'accordo corrente**; la probabilità di aggancio dipende dall'ordine del branco (compatto/disordinato → più dissonanza; coerente → note d'accordo).
- Output = **gradi di scala 0-6** (non note assolute); ritmo/velocity/ottava/rest condizionati dai descrittori; `density` → eventi/secondo.
- Test headless OK: progressione `i→VI→i→V`, note biasate correttamente sull'accordo, mix note/rest.

**Modifiche ai file (2026-07-07 sera):**
- ~15:50–16:15 — creato `Claude/aquarium/markov.py` (WeightedMarkov + HierarchicalGenerator + MusicEvent).
- Esteso `Claude/aquarium/config.py` (namespace OSC `/aq/music/*`, BPM, DURATIONS, CHORD_EVERY_EVENTS).
- Esteso `Claude/aquarium/osc_out.py` (`send_music`).
- Aggiornato `Claude/run_claude_version.py` (tick generatore, tasto **M** music on/off, HUD con accordo + conteggio note) e `Claude/smoke_test.py` (verifica + campione musicale).
- Contratto OSC aggiunto: `/aq/music/note` (id, degree, octave, dur_beats, velocity, chord_root), `/aq/music/rest` (id, dur_beats), `/aq/music/chord` (chord_root on-change).

**Stato:** versione Claude ora end-to-end (movimento → descrittori → Markov gerarchica → OSC). NON ancora committata su GitHub (in attesa ok utente). **Decisioni aperte:** push di questo aggiornamento? · portare la Markov gerarchica in Codex (rischio collisione col lavoro Max in corso) **o** aggiungere ricevitore OSC di test alla versione Claude (raccomandato).

## 2026-07-07 (sera, 17:50) — Analisi critica della base Codex (solo review, nessuna modifica)

**Processo:** letto lo stato attuale di `Codex/` (cresciuto: input MIDI MIDIMIX via `pygame.midi`, control-in UDP/FUDI, 8 patch Max, doc musicista). Verificato **come Max produce il suono** (grep sulla patch `aquarium_netreceive_mapped.maxpat`: solo `cycle~`+`line~`+`mtof`, niente `poly~`/`route` per layer).

**Verdetto centrale:** la sofisticazione del Python NON arriva all'orecchio — il divario codice↔suono è il problema #1.

**Criticità concrete individuate (con file:riga):**
1. **Armonia cosmetica** — `osc_io.py:13-16` / `OSC_CONTRACT.md:135`: `(degree + chord_degree) % 7` non produce accordi, wrappa pure l'ottava. La progressione i-VI-iv-V è quasi impercettibile.
2. **Ritmo non udibile** — `main.py:190-203`: timing note = `events_per_second` (density+speed), scollegato da `duration_beats`; nessun clock/griglia → la rhythm chain è decorativa.
3. **Layer/sezioni non diventano timbro** — la patch Max non fa `route` per `layer_id`; i 6 layer suonano identici.
4. **Descrittori ridondanti** — `energy == mean_speed`; `density == 1 - nearest_distance` (2 coppie identiche su 10).
5. **Flash su pesce casuale** (`main.py:195-196`) — legame visuale↔audio non causale.
6. **OSC duplicato** — `/music/event`+`/music/note`+`/music/midi` insieme → rischio doppio trigger nel `route` della patch.
7. **Nessuna polifonia** (no `poly~`): i burst collassano sugli stessi oscillatori.
   *(Positivi: fallback FUDI `netreceive -u 7401` senza oscparse; debug MIDI che stampa i CC reali; control-in con alias multipli.)*

**Proposte (per impatto sul suono):** A) voce di basso sulla radice dell'accordo + fix `event_to_midi`; B) **clock + quantizzazione a griglia di 16esimi** (upgrade musicale maggiore, rende udibile la rhythm chain); C) `route` per layer verso timbri distinti in Max; D) de-duplicare descrittori (sostituire `energy` con vorticità/accelerazione); E) flash causale + eventi discreti (già pronti in `Claude/`, da travasare); F) un solo formato nota OSC per evitare doppio trigger. **Priorità: B → A → C.**

**Modifiche ai file:** nessuna (sessione di sola analisi). **Prossimo passo proposto all'utente:** implementare B (clock+quantizzazione) in Codex coordinandosi col lavoro Max, oppure verificare prima il doppio-trigger nel wiring della patch.

## 2026-07-07 (sera, 20:17) — Re-analisi Codex dopo collegamento MIDIMIX + audio (solo review)

**Contesto:** l'utente ha collegato il MIDIMIX del musicista, l'audio in Max funziona (via `makenote → noteout`), MIDIMIX rimappato sui parametri boids (commit `a287422` "Remap MIDIMIX to ecosystem controls", `b67a29c`).

**Processo:** letto il diff `4810768..HEAD` su Codex/, riletti config/osc_io/midi_in/controls/main aggiornati + la doc utente `DA_LEGGERE_troppo_stanco_regolenuova_MAP.md`; grep sulle patch Max per routing/sintesi.

**Novità positive verificate:** audio reale via `makenote→noteout` (rispetta la durata); mappatura MIDIMIX CC19-24 = ecosistema (align/cohesion/separation/noise/food/predator), CC25-26 = density/section → filosofia corretta (musicista scolpisce il mondo, il suono segue).

**Bug NUOVO trovato (concreto):** i fader food/predator del MIDIMIX **non sono proporzionali**, sono on/off. `main.py:170-173` accende un attrattore virtuale se `food_amount>0.01`, ma `boids.py:130` applica la forza con `food_strength` (=1.0, del mouse), non con `food_amount`. La doc utente (righe 42-43) intendeva 0→3 proporzionale → mismatch intento/implementazione. Fix: usare `food_amount` come intensità nel caso virtuale (2 righe).
   - Nota: verificato che NON è un bug di naming — `apply_parameter` (midi_in.py:154-157) e `RuntimeControls` (controls.py:17-18) hanno i campi `food_amount`/`predator_amount` coerenti.

**Criticità precedenti ancora presenti (invariate dai commit del remap):** armonia cosmetica `(degree+chord_degree)%7` (osc_io.py:14); nessun clock/griglia (main.py:194-203); layer non instradati a timbri distinti nelle patch Max; descrittori ridondanti (energy=mean_speed, density=1-nearest); flash su pesce casuale (main.py:200); rischio doppio-trigger `/music/note` + `/music/midi` entrambi in `route`.

**Priorità suggerita:** #4 fix food/predator proporzionale (2 righe, isolato, rischio zero) → #1 clock+quantizzazione → #3 layer→timbri in Max → #2 basso sull'accordo.

**Modifiche ai file:** nessuna (sola analisi). Proposto all'utente di partire dal fix food/predator (fattibile subito in Codex senza collisioni).

## 2026-07-07 (sera, 20:49) — Spiegazione catena audio Max (solo analisi)

**Processo:** tracciati i `patchline` reali di `max/aquarium_netreceive_sound_v2.maxpat` per spiegare all'utente come nasce davvero il suono.

**Scoperte concrete (dal wiring, non da intuizione):**
- **Due percorsi audio indipendenti.** Percorso 1 (drone): `route direct → unpack → mean_speed→expr 80+f*820→line~→cycle~`, `energy→expr 0.03+f*0.27→line~→*~→ezdac~`. Cioè **un'unica sinusoide**: pitch=velocità media, volume=energia. È l'unico suono sintetizzato *dentro* Max.
- Percorso 2 (note Markov): `route midi → unpack → makenote → noteout` = **MIDI verso synth esterno/GM**. Le note NON sono sintetizzate nella patch: se non c'è strumento MIDI a valle, la melodia Markov **non si sente**.
- **5 descrittori su 7 e i layer sono unpackati ma NON collegati** → non toccano il suono (center_x/y, density, spread, density_fader, layer_id, section_id).
- **Correzione vs analisi precedente:** in v2 il `route` manda al `makenote` solo `midi` (non `note`) → **niente doppio-trigger** in questa patch.

**Tesi principale:** il "thin" non è colpa dell'algoritmo ma di sintesi/timbro/effetti (dominio del musicista). Leve per migliorare l'ascolto: 1) strumento vero per le note (DAW o `poly~`+filtro+`adsr~`, non GM); 2) riverbero/spazio; 3) ingrassare il drone + cablare i descrittori morti (center_y→cutoff, density→detune/reverb, spread→stereo); poi clock+quantizzazione, basso sull'accordo, layer→timbri.

**Richiesta utente interrotta a metà** ("crea un file Implementazioni_da…"): chiesto conferma di nome/posizione (`Codex/Implementazioni_da_fare.md`?) e ambito (solo audio o tutte le pendenze) prima di crearlo. In attesa di risposta.

**Modifiche ai file:** nessuna.

## 2026-07-08 — Checklist implementazioni + spiegazione Markov/Opzione A

**Processo:** creata la checklist prioritizzata delle criticità/migliorie; poi spiegazione tecnica profonda (su richiesta utente) di come funzionano le Markov chain in Codex e di come l'Opzione A (MIDI multicanale → Ableton) le collega all'output.

**Decisione utente:** procedere con **Opzione A** (Ableton) per verificare, poi eventualmente B (`poly~` in Max) col musicista. Precisazione: A e B non sono sequenziali — A è la strada di produzione, B un fallback self-contained.

**Contenuti chiave spiegati:**
- **Markov in Codex** (`markov.py`): 2 catene d'ordine-1 indipendenti (pitch gradi 0-6, rhythm durate) + **ciclo d'accordi fisso** `[0,5,3,4]` ogni 16 eventi (non è Markov). "Temperatura" = esponente `1/T` sui pesi (T>1 caos, T<1 deterministico). Descrittori→generazione: temperatura=`0.25+density*0.9+speed*0.35`, rest_prob=`0.62-density*0.52-speed*0.22`, ottava←spread, velocity←energy, layer←sezione+density, bias-accordo se density>0.72. Limiti: ordine-1 (no lungo termine), catene scorrelate (pitch⊥rhythm), armonia debole.
- **Opzione A tecnica:** serve **loopMIDI** (Windows non ha IAC) come porta MIDI virtuale; `layer_id`→**canale MIDI**→traccia Ableton distinta (rende reali i layer); **clock a 16esimi in Python** dove nascono le note. Due architetture: **A-1** Max hub (`route`/`makenote` per canale) vs **A-2** Python genera MIDI diretto (`mido`+`python-rtmidi`), Max scende a drone+visual. **Raccomandata A-2**.
- **Test da 5 minuti senza codice:** loopMIDI → `noteout` verso porta `Aquarium` → traccia Ableton con strumento vero. Se il "materiale" piace, costruire A-2; se no, il problema è nella generazione (ordine-1/correlazioni).

**Prossimo passo proposto:** dopo il test da 5 minuti, scrivere il modulo Python di output MIDI (A-2): clock 16esimi + canale-per-layer + accordi reali (triade su canale pad + basso su radice), tenendo l'OSC verso Max per i descrittori. In attesa di ok / esito test.

**Modifiche ai file:**
- 2026-07-08 10:12 — creato `Codex/Implementazioni_da_fare.md` (checklist P0-P3 con `file:riga`, ordine d'attacco, catena audio attuale, suggerimenti). Nessuna modifica al codice.

### 2026-07-08 (agg.) — Ricerca web su A-2 e sync tempo (solo analisi)

**Processo:** ricerca web per validare A-2 e trovare il modo migliore di sincronizzare/instradare l'audio verso Ableton.

**Conclusioni chiave:**
- **A-2 confermata**, ma "suona bene" ≠ A-2: la qualità dipende da (1) strumenti+effetti in Ableton, (2) sync col clock del DAW, (3) musicista. Il codice consegna *materiale*, non timbro.
- **Sync del tempo (rischio #1 di A-2)** in 3 livelli: **v1** BPM fisso uguale in Python/Ableton (`loopMIDI`+`python-rtmidi`/`mido`, standard confermato su Windows); **v1.5** Python slave del **MIDI clock** di Ableton (poche dipendenze); **v2** **Ableton Link** via **`aalink`** (sync al beat, beat frazionari). Obiettivo: v1 per verificare → v2 per il groove-lock.
- **Trappola evitata:** NIENTE Max-for-Live che riceve OSC — documentato che Max e Ableton non possono ricevere OSC sulla stessa porta insieme (Cycling '74). A-2 manda **MIDI** via loopMIDI → nessuna contesa UDP. Punto a favore di A-2.
- **AbletonOSC** (:11000) esiste ma è controllo DAW/clip, non flusso performativo di note → non è la strada per il live.
- **Rischio tecnico:** `aalink` compila estensione C → wheel per Python 3.13/3.14 potrebbero mancare. Mitigazione: partire con v1/v1.5 (solo mido+rtmidi), eventuale venv 3.11/3.12 per aalink.

**Divisione del lavoro chiarita:** Python (A-2) = clock 16esimi + Markov + accordi reali (triade pad + basso su radice) + canale-per-layer + CC descrittori. Ableton (musicista) = strumenti, effetti, mix.

**Domanda aperta all'utente (blocca il codice):** il BPM lo tiene Python (v1) o Ableton master (v1.5)? Poi scrivo il modulo `midi_out`.

**Modifiche ai file:** nessuna.
