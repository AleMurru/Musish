# ROADMAP_DEMO_v0 — Boids + MIDIMIX + Max + sample del musicista

Obiettivo: costruire una **demo funzionante, chiara e ascoltabile** prima di tornare a Markov Chain / AI generativa.

La demo v0 deve dimostrare questo flusso:

```text
MIDIMIX
↓
Python / Pygame / boids
↓
descriptor + controlli performativi
↓
Max
↓
sample / granulazione / effetti del musicista
↓
suono sensato
```

In questa fase mettiamo temporaneamente in secondo piano:

```text
Markov Chain
AI generativa
melodie simboliche
accordi automatici
MIDI multi-canale verso Ableton
```

La priorità è avere un sistema performativo collegato end-to-end:

```text
muovo fader → cambiano i pesci → cambiano i parametri in Max → cambia il suono
```

---

## 1. Idea centrale della demo v0

Invece di far generare note ai pesci, usiamo i pesci come **sorgente di controllo** per il sistema sonoro del musicista.

Quindi non facciamo:

```text
pesci → Markov → note MIDI → synth
```

ma:

```text
pesci → descriptor → Max → sample / granulatore / effetti
```

Il musicista porta i suoi suoni, Max li riproduce o li granularizza, Python controlla il comportamento dei pesci e invia parametri in tempo reale.

---

## 2. Perché questa strada è più adatta adesso

Il progetto oggi ha già:

- boids funzionanti in Python;
- MIDIMIX letto direttamente da Python;
- descriptor normalizzati;
- invio dati a Max via OSC e plain UDP;
- patch Max di ricezione;
- possibilità di controllare i boids live.

Il problema non è più “manca un algoritmo musicale”.

Il problema è:

```text
non abbiamo ancora una demo sonora semplice, stabile e convincente
```

Questa roadmap serve proprio a ottenere quella demo.

---

## 3. Architettura tecnica proposta

### 3.1 Python

Python mantiene il ruolo di:

```text
ecosistema visivo + estrazione dati + controllo live
```

Python deve:

1. visualizzare i boids;
2. leggere il MIDIMIX;
3. modificare il comportamento dei boids;
4. calcolare descriptor come `mean_speed`, `center_x`, `density`, `spread`;
5. inviare a Max i dati continui;
6. eventualmente inviare anche parametri performativi dedicati alla granulazione.

---

### 3.2 Max

Max diventa il motore sonoro principale.

Max deve:

1. ricevere i dati da Python;
2. caricare i sample del musicista;
3. riprodurre / granularizzare / processare i sample;
4. mappare i descriptor e i fader ai parametri sonori;
5. produrre audio finale.

---

### 3.3 MIDIMIX

Il MIDIMIX non controlla direttamente Max.

Workflow consigliato:

```text
MIDIMIX → Python → Max
```

Motivo:

- Python sa già leggere il MIDIMIX;
- un device MIDI su Windows può non essere multi-client;
- evitiamo conflitti tra Python, Max e Ableton;
- Max riceve parametri già puliti e coerenti da Python.

---

## 4. Comunicazione Python → Max

Attualmente Python invia già dati su due canali:

```text
OSC standard: 7400
Plain UDP / Max-friendly: 7401
```

Per la demo v0 conviene usare il canale più semplice e robusto:

```text
netreceive -u 7401
```

In Max:

```text
[netreceive -u 7401]
|
[route direct controls performance]
```

Nota: `performance` non esiste ancora nel codice attuale, ma è il messaggio consigliato da aggiungere per i nuovi parametri richiesti dal musicista.

---

## 5. Messaggi già disponibili oggi

### 5.1 `direct`

Python invia già:

```text
direct mean_speed energy center_x center_y density spread density_fader
```

Ordine dei valori:

| Posizione | Nome | Significato |
|---:|---|---|
| `$1` | `mean_speed` | velocità media del branco |
| `$2` | `energy` | energia del movimento, oggi simile a `mean_speed` |
| `$3` | `center_x` | centro orizzontale del branco |
| `$4` | `center_y` | centro verticale del branco |
| `$5` | `density` | compattezza del branco |
| `$6` | `spread` | dispersione del branco |
| `$7` | `density_fader` | controllo musicale di densità |

Questi dati bastano già per una demo sonora.

Esempi:

```text
center_x → pan audio
mean_speed → rate dei trigger
density → densità della granulazione
spread → riverbero / stereo width
energy → volume / drive
center_y → filtro / brightness
```

---

### 5.2 `controls`

Python invia anche:

```text
controls density_fader alignment cohesion separation noise food_strength predator_strength food_amount predator_amount section_id
```

Questi sono i valori dei controlli live.

Per la demo sample/granulari, però, è meglio non dipendere troppo da `controls`, perché l'ordine è legato al contratto corrente.

Per i nuovi parametri del musicista è più pulito creare un messaggio dedicato.

---

## 6. Nuovi parametri richiesti dal musicista

Il musicista ha chiesto tre parametri performativi per la granulazione:

1. `Alignment / Chaos`
2. `Density`
3. `Noise / Distortion`

Questi parametri vanno chiariti bene perché possono avere due funzioni diverse:

```text
A. funzione visuale: modificano il comportamento dei pesci
B. funzione sonora: vengono inviati a Max e mappati dal musicista
```

La proposta migliore è usarli in entrambi i modi, ma con ruoli chiari.

---

## 7. Parametro 1 — Alignment / Chaos

### 7.1 Cambio di programma

Il controllo `Pan` viene sostituito da un controllo più legato al comportamento del branco:

```text
alignment_chaos
```

Range:

```text
0.0 = branco ordinato, i pesci tendono ad andare nella stessa direzione
1.0 = branco disperso, movimento caotico e meno allineato
```

Questo controllo è più visibile e più coerente con l'idea di ecosistema: il fader non sposta semplicemente i pesci, ma cambia la qualità del loro comportamento collettivo.

---

### 7.2 Implementazione consigliata in Python

Aggiungere un nuovo controllo:

```python
alignment_chaos: float = 0.5
```

Nel modello boids questo valore diventa una macro che influenza:

```text
alignment_weight
cohesion_weight
separation_weight
noise_weight
```

Comportamento desiderato:

```text
fader basso → più alignment, più direzione comune, meno noise, meno separazione
fader alto  → meno alignment, più noise, più separazione, movimento più frammentato
```

Importante: il cambio deve essere progressivo e organico. Non deve resettare i pesci o teletrasportarli.

Formula concettuale:

```python
chaos = controls.alignment_chaos
order = 1.0 - chaos

alignment  *= high_when_ordered
cohesion   *= slightly_high_when_ordered
separation *= high_when_chaotic
noise      += chaos_amount
```

In più, quando il fader è molto basso, si può aggiungere una piccola forza di schooling verso una direzione comune, così l'effetto “vanno tutti nella stessa direzione” diventa immediatamente visibile.

---

### 7.3 Cosa mandare a Max

Max deve ricevere:

```text
alignment_chaos
```

Uso musicale consigliato:

| Valore | Visuale | Possibile suono |
|---:|---|---|
| basso | movimento ordinato, direzione comune | suono pulito, stabile, meno distorto |
| medio | comportamento naturale | texture bilanciata |
| alto | dispersione/caos | più noise, granularità, distorsione, instabilità |

Max può comunque continuare a usare `center_x` da `direct` per il pan audio reale, se serve.

---

## 8. Parametro 2 — Density

### 8.1 Ambiguità del nome

Nel progetto esistono già due concetti simili:

```text
density          = descrittore del branco, cioè compattezza dei pesci
density_fader    = controllo musicale già esistente
```

Il musicista chiede un parametro `Density` per la granulazione.

Per evitare confusione, nel codice conviene chiamarlo:

```text
grain_density
```

oppure:

```text
sample_density
```

---

### 8.2 Significato consigliato

`grain_density` dovrebbe controllare:

```text
quanti grani / trigger / eventi sonori vengono prodotti in Max
```

Range:

```text
0.0 = quasi nessun trigger / texture rarefatta
1.0 = tanti grani / texture densa
```

---

### 8.3 Relazione con i boids

Possibili strategie:

#### Opzione A — parametro solo sonoro

Il fader controlla `grain_density`, Python lo manda a Max, ma i pesci non cambiano.

Pro:

- molto semplice;
- il musicista ha controllo diretto.

Contro:

- il pubblico vede meno relazione visuale.

#### Opzione B — parametro sonoro + influenza sui boids

Il fader controlla `grain_density`, ma influenza anche leggermente:

```text
cohesion / separation / quantità di movimento
```

Pro:

- più performativo;
- il gesto del fader si vede e si sente.

Contro:

- può confondere se modifica troppe cose.

#### Raccomandazione v0

Per la demo v0:

```text
grain_density controlla direttamente Max
```

Il movimento dei pesci continuerà a influenzare il suono tramite i descriptor.

Max potrà combinare:

```text
grain_density del fader + mean_speed dei pesci + density del branco
```

Esempio:

```text
trigger_rate = grain_density * 0.7 + mean_speed * 0.3
```

---

## 9. Parametro 3 — Noise / Distortion

### 9.1 Significato

Il musicista vuole un parametro controllabile da fader a cui lui darà forma musicale in Max.

Nel codice possiamo chiamarlo:

```text
noise_distortion
```

oppure:

```text
distortion_amount
```

Range:

```text
0.0 = pulito / poco noise
1.0 = rumoroso / distorto
```

---

### 9.2 Relazione con i boids

Qui c'è una relazione naturale con il parametro già esistente:

```python
noise_weight
```

`noise_weight` rende il movimento dei pesci più caotico.

Quindi per la demo v0 possiamo fare:

```text
fader Noise/Distortion → noise_weight dei boids + noise_distortion verso Max
```

Questo è molto efficace perché:

```text
più distorsione sonora = più movimento nervoso dei pesci
```

Il pubblico capisce meglio il legame gesto → visuale → suono.

---

### 9.3 Mapping in Max

Max può usare `noise_distortion` per controllare:

- quantità di distorsione;
- saturazione;
- bitcrushing;
- rumore aggiunto;
- filtro più aggressivo;
- feedback;
- mix dry/wet di un effetto.

Esempi Max vanilla:

```text
noise_distortion → drive di [overdrive~]
noise_distortion → gain prima di [clip~]
noise_distortion → dry/wet di noise layer
noise_distortion → amount di [degrade~]
noise_distortion → expr~ tanh($v1 * drive)
```

---

## 10. Messaggio nuovo consigliato: `performance`

Per non rompere il contratto esistente, aggiungiamo un nuovo messaggio dedicato alla demo:

```text
performance alignment_chaos grain_density noise_distortion scene_id
```

Versione OSC:

```text
/aquarium/performance alignment_chaos grain_density noise_distortion scene_id
```

Versione plain UDP per Max:

```text
performance 0.50 0.70 0.20 1;
```

Campi:

| Posizione | Nome | Range | Descrizione |
|---:|---|---:|---|
| `$1` | `alignment_chaos` | `0..1` | ordine/caos del branco: basso = stessa direzione, alto = dispersione caotica |
| `$2` | `grain_density` | `0..1` | densità granulazione / trigger |
| `$3` | `noise_distortion` | `0..1` | quantità noise/distorsione |
| `$4` | `scene_id` | `0..5` | scena/banco sample/sezione |

In Max:

```text
[route direct performance]
        |
        +-- performance: $1 alignment_chaos, $2 grain_density, $3 noise_distortion, $4 scene_id
```

---

## 11. Mapping MIDIMIX consigliato per la demo v0

Per la demo v0 conviene avere una modalità semplificata, più vicina alle esigenze del musicista.

### Proposta mapping demo

| Fader MIDIMIX | Parametro Python | Range | Effetto visuale | Effetto sonoro in Max |
|---|---|---:|---|---|
| Fader 1 | `alignment_chaos` | `0..1` | basso = stessa direzione, alto = dispersione caotica | stabilità/instabilità, ordine/noise |
| Fader 2 | `grain_density` | `0..1` | nessuno diretto, o leggero aumento attività | densità grani / trigger |
| Fader 3 | `noise_distortion` + `noise_weight` | `0..1` | movimento più nervoso | distorsione / noise / degrado |
| Fader 4 | `cohesion_weight` | `0..3` | branco più compatto | influenza `density` |
| Fader 5 | `separation_weight` | `0..4` | branco più disperso | influenza `spread` |
| Fader 6 | `food_amount` | `0..3` | attrazione al centro | accumulo/tensione |
| Fader 7 | `predator_amount` | `0..3` | fuga dal centro | energia/esplosione |
| Fader 8 | `scene_id` | `0..5` | sezione/scena | banco sample / preset Max |

Questa mappatura sostituisce temporaneamente quella attuale, che era più boids-oriented.

### Nota importante

Il mapping attuale è:

```text
F1 alignment
F2 cohesion
F3 separation
F4 noise
F5 food
F6 predator
F7 density_fader
F8 section
```

Per la demo v0 possiamo scegliere una delle due strade:

#### Strada A — sostituire il mapping

Più semplice per la performance.

#### Strada B — creare modalità `DEMO_MODE`

Più ordinata tecnicamente.

Esempio:

```python
DEMO_MODE = True
```

Se `DEMO_MODE` è attivo, si usa il mapping demo; altrimenti si usa il mapping originale.

Raccomandazione:

```text
creare DEMO_MODE
```

Così non perdiamo il lavoro precedente.

---

## 12. Come Max dovrebbe usare i dati

### 12.1 Patch Max consigliata

Creare una nuova patch separata:

```text
Codex/max/aquarium_sample_player_v0.maxpat
```

Non modificare subito le patch vecchie.

La patch deve ricevere:

```text
direct
performance
```

Schema:

```text
[netreceive -u 7401]
|
[route direct performance]
|                 |
|                 +--> controlli performativi musicista
|
+--> descriptor boids
```

---

### 12.2 Layer sonori consigliati

Per una demo chiara bastano 3 layer.

#### Layer A — Texture / drone / ambiente

Usa sample lunghi.

Controlli:

```text
spread → riverbero / stereo width
density → filtro / compattezza
energy → volume
```

#### Layer B — Grain / microsuoni

Usa sample brevi o porzioni di sample.

Controlli:

```text
grain_density → rate dei grani
mean_speed → variazione rate
center_x → pan dei grani
noise_distortion → degrado / saturazione
```

#### Layer C — Hits / eventi

Usa one-shot, impatti, glitch, colpi.

Controlli:

```text
energy alta → trigger hit
predator_amount alto → più probabilità di hit
scene_id → cambia banco hit
```

---

## 13. Strategie Max per i sample

Dipende da quanto vuole fare il musicista in Max.

### Opzione semplice — `playlist~`

Buona per demo rapida e caricamento manuale.

Pro:

- facile da usare;
- visivo;
- comodo per drag & drop.

Contro:

- meno flessibile per granulazione complessa.

---

### Opzione media — `sfplay~`

Buona per riprodurre file da disco.

Pro:

- semplice;
- adatto a one-shot e loop;
- leggero.

Contro:

- non è un vero granulatore.

---

### Opzione più flessibile — `buffer~` + `groove~` / `play~`

Buona per granulazione e manipolazione.

Pro:

- il sample è in memoria;
- si può controllare posizione, velocità, loop, finestre;
- più adatto a granular synthesis.

Contro:

- patch più complessa.

---

### Raccomandazione pratica

Per la primissima demo:

```text
playlist~ o sfplay~ per sentire subito qualcosa
```

Poi:

```text
buffer~ + groove~ per granulazione più raffinata
```

---

## 14. Cartella sample consigliata

Il musicista dovrebbe preparare una cartella ordinata.

Esempio:

```text
Codex/samples/
  textures/
    texture_01.wav
    texture_02.wav
  grains/
    grain_01.wav
    grain_02.wav
  hits/
    hit_01.wav
    hit_02.wav
  noise/
    noise_01.wav
  bass/
    bass_01.wav
```

Oppure, se i sample non devono stare nel repository Git:

```text
D:/Samples_Aquarium/
  textures/
  grains/
  hits/
  noise/
```

Decisione consigliata:

- non committare librerie audio pesanti su Git;
- mettere nel repo solo pochi sample demo leggeri, se servono;
- documentare il path della libreria del musicista.

---

## 15. Ruoli: cosa fai tu come informatico

Tu devi occuparti di:

### 15.1 Python

- mantenere `main.py` stabile;
- aggiungere i nuovi controlli:
  - `alignment_chaos`;
  - `grain_density`;
  - `noise_distortion`;
- decidere mapping MIDIMIX demo;
- inviare nuovo messaggio `performance` a Max;
- eventualmente aggiungere `DEMO_MODE`;
- fare in modo che `alignment_chaos` trasformi il branco da ordinato a caotico;
- garantire che i descriptor continuino a uscire correttamente.

---

### 15.2 Max tecnico / ricezione dati

- creare patch Max minima `aquarium_sample_player_v0.maxpat`;
- ricevere `direct` e `performance`;
- stampare/debuggare i valori in Max;
- normalizzare/smussare i segnali se necessario;
- preparare punti di connessione chiari per il musicista.

---

### 15.3 Documentazione

- aggiornare `docs/OSC_CONTRACT.md` con il nuovo messaggio `performance`;
- aggiornare guida MIDIMIX se cambia mapping;
- mantenere `ROADMAP_DEMO_v0.md` aggiornato;
- segnare cosa funziona e cosa no nel Diario.

---

### 15.4 Test tecnici

Checklist informatico:

```text
[ ] Python parte senza errori
[ ] MIDIMIX viene rilevato
[ ] Fader 1 modifica alignment_chaos
[ ] Fader 2 modifica grain_density
[ ] Fader 3 modifica noise_distortion
[ ] I pesci passano da stessa direzione a dispersione caotica con alignment_chaos
[ ] Max riceve direct
[ ] Max riceve performance
[ ] Max produce audio
[ ] I valori sono stabili e non jitterano troppo
```

---

## 16. Ruoli: cosa deve fare il musicista

Il musicista deve occuparsi di:

### 16.1 Materiale sonoro

Preparare sample organizzati per funzione:

```text
textures / loop lunghi
grains / frammenti brevi
hits / eventi percussivi
noise / materiale rumoroso
bass / materiale grave, se utile
```

Per ogni cartella dovrebbe scegliere pochi suoni buoni, non centinaia.

Per la prima demo bastano:

```text
3 texture
5 grains
5 hits
2 noise
```

---

### 16.2 Mapping musicale in Max

Il musicista deve decidere cosa significa musicalmente:

```text
alignment_chaos
center_x
grain_density
noise_distortion
mean_speed
density
spread
energy
```

Esempio:

```text
center_x → pan stereo
grain_density → numero di grani
noise_distortion → drive/distorsione
spread → riverbero
density → filtro/tono
energy → volume/intensità
```

---

### 16.3 Sound design

Il musicista deve occuparsi di:

- volumi;
- compressione;
- riverbero;
- distorsione;
- spazializzazione;
- scelta dei sample;
- eventuale granulatore vero;
- estetica finale.

Questa è la parte dove il musicista porta qualità sonora.

---

### 16.4 Feedback performativo

Il musicista deve dirci:

- quali fader sono comodi;
- quali mapping sono troppo sensibili;
- quali parametri non servono;
- quali movimenti visuali sono musicalmente utili;
- quali suoni funzionano meglio;
- se vuole più controllo manuale o più automatismo dai pesci.

---

## 17. Procedura passo passo

## Step 0 — Congelare obiettivo demo

Obiettivo demo v0:

```text
boids controllati da MIDIMIX che pilotano sample/granulazione in Max
```

Non cercare ancora:

- AI;
- Markov;
- armonia;
- composizione automatica;
- Ableton routing complesso.

---

## Step 1 — Preparare sample

Responsabile: musicista.

Creare una cartella sample con pochi file selezionati.

Esempio minimo:

```text
textures: 3 file
hits: 5 file
grains: 5 file
noise: 2 file
```

Formato consigliato:

```text
.wav
44.1kHz o 48kHz
mono o stereo
nomi semplici senza caratteri strani
```

---

## Step 2 — Testare flusso attuale

Responsabile: informatico.

Avviare Python:

```bash
cd Codex
python main.py
```

Aprire patch Max attuale:

```text
Codex/max/aquarium_netreceive_mapped.maxpat
```

Verificare:

```text
[ ] Max riceve direct
[ ] Max produce suono
[ ] MIDIMIX muove parametri in Python
```

---

## Step 3 — Decidere mapping demo MIDIMIX

Responsabili: informatico + musicista.

Proposta:

```text
F1 alignment_chaos
F2 grain_density
F3 noise_distortion
F4 cohesion
F5 separation
F6 food
F7 predator
F8 scene_id
```

Confermare o modificare prima di scrivere codice.

---

## Step 4 — Aggiungere controlli demo in Python

Responsabile: informatico.

Modifiche previste:

1. `RuntimeControls`:

```python
alignment_chaos: float = 0.5
grain_density: float = 0.25
noise_distortion: float = 0.0
```

2. `config.py`:

- aggiungere mapping MIDIMIX demo;
- eventualmente `DEMO_MODE = True`.

3. `boids.py` o `main.py`:

- usare `alignment_chaos` per modulare alignment/cohesion/separation/noise e creare ordine/caos.

4. `osc_io.py`:

- inviare `performance alignment_chaos grain_density noise_distortion scene_id`.

5. docs:

- aggiornare contratto OSC;
- aggiornare mapping MIDIMIX.

---

## Step 5 — Creare patch Max sample player v0

Responsabile: informatico + musicista.

Creare:

```text
Codex/max/aquarium_sample_player_v0.maxpat
```

Struttura minima:

```text
[netreceive -u 7401]
|
[route direct performance]
```

Poi:

```text
direct      → descriptor boids
performance → fader performativi demo
```

Per iniziare basta:

```text
center_x → pan
grain_density → trigger rate
noise_distortion → drive
density/spread → filtro/reverb
```

---

## Step 6 — Primo test sonoro

Responsabili: tutti.

Test da fare:

1. muovere F1:

```text
fader basso: pesci più allineati, stessa direzione
fader alto: pesci più dispersi e caotici
```

2. muovere F2:

```text
aumentano/diminuiscono grani o trigger
```

3. muovere F3:

```text
movimento più nervoso
suono più distorto/rumoroso
```

4. muovere food/predator:

```text
branco si aggrega/scappa
suono reagisce tramite density/spread/energy
```

---

## Step 7 — Tuning musicale

Responsabile principale: musicista.

Qui non si cambia l'architettura.

Si regolano:

- scale dei parametri;
- smoothing;
- volumi;
- trigger rate minimo/massimo;
- riverberi;
- distorsioni;
- scelta sample;
- sensibilità dei fader.

---

## Step 8 — Stabilizzazione demo

Responsabile: informatico.

Una volta che il sistema suona:

- salvare patch Max stabile;
- salvare mapping definitivo;
- documentare avvio rapido;
- fare commit/push;
- preparare fallback se MIDIMIX non viene letto.

---

## 18. Criteri di successo della demo v0

La demo v0 è riuscita se possiamo mostrare questo:

```text
1. Avvio Python
2. Avvio Max
3. Muovo MIDIMIX
4. I pesci cambiano comportamento
5. I sample del musicista reagiscono
6. Il risultato è musicalmente presentabile
```

Non serve ancora che sia “intelligente”.

Serve che sia:

```text
visibile
udibile
controllabile
stabile
comprensibile
```

---

## 19. Decisioni da prendere prima di implementare

Prima di scrivere codice, bisogna decidere:

### 19.1 Mapping MIDIMIX definitivo per demo

Confermare o modificare:

```text
F1 alignment_chaos
F2 grain_density
F3 noise_distortion
F4 cohesion
F5 separation
F6 food
F7 predator
F8 scene_id
```

### 19.2 Dove stanno i sample

Possibilità:

```text
Codex/samples/          # comodo, ma attenzione a Git
cartella esterna        # consigliato per librerie grandi
```

### 19.3 Tipo di patch Max iniziale

Scegliere tra:

```text
playlist~ / sfplay~     # demo rapida
buffer~ + groove~       # più adatto a granulazione
patch granulare già del musicista
```

### 19.4 Markov spenta o solo ignorata?

Per la demo v0 possiamo:

```text
A. lasciare Python che manda Markov, ma Max la ignora
B. aggiungere flag ENABLE_MARKOV = False
```

Raccomandazione:

```text
aggiungere flag ENABLE_MARKOV = False
```

per non sporcare log/console e semplificare la demo.

---

## 20. Roadmap sintetica

```text
[1] Confermare mapping MIDIMIX demo
[2] Preparare sample minimi
[3] Aggiungere alignment_chaos / grain_density / noise_distortion in Python
[4] Inviare messaggio performance a Max
[5] Creare patch Max aquarium_sample_player_v0
[6] Collegare sample e mapping base
[7] Testare con MIDIMIX
[8] Tuning musicale col musicista
[9] Commit/push versione demo
[10] Solo dopo: tornare a Markov / AI
```

---

## 21. Nota finale

Questa demo non è un passo indietro rispetto alla Generazione AI.

È il fondamento necessario.

Prima costruiamo uno strumento performativo che funziona:

```text
boids → controllo sonoro → sample reali → performance
```

Poi potremo aggiungere AI/Markov come ulteriore livello sopra un sistema già stabile e musicalmente credibile.
