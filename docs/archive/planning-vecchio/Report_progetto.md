# Report di progetto — Acquario generativo musicale

*Strumento audiovisivo generativo per un workshop di generative AI music, orientato a una performance live.*

---

## 1. Il concept

Un **acquario digitale** popolato da pesci (boids) che si muovono secondo regole di
comportamento collettivo. Dal loro movimento vengono estratti **descrittori numerici**
(velocità, densità, dispersione, coerenza, posizione…). Questi descrittori non producono
suono direttamente: **pilotano dei motori sonori** (un granulatore e un modello DDSP neurale,
PLAUD) renderizzati in Max/MSP.

Il musicista **non suona note**: **scolpisce l'ecosistema** (coesione, predatori, cibo,
turbolenza, numero di pesci) tramite un controller MIDI, e il suono segue lo stato del branco.

**Catena completa:**

```
MIDIMIX (fader) → Python (boids) → descrittori → OSC → Max (granulatore + PLAUD nn~) → suono
```

---

## 2. Architettura del sistema

- **Simulazione (Python / pygame):** ~100 boids con flocking classico (allineamento,
  coesione, separazione) + rumore, gesti di cibo/predatore, popolazione variabile.
- **Descrittori:** misure del branco normalizzate 0–1, filtrate low-pass per togliere il
  jitter.
- **Trasporto:** OSC su `127.0.0.1:7400` (+ fallback FUDI su `7401`), ~20 Hz.
- **Controllo live:** AKAI **MIDIMIX** letto direttamente da Python; ogni fader fisico
  controlla un parametro dell'ecosistema.
- **Motori sonori in Max:** un **granulatore** multicanale (48 voci) e **PLAUD** (modello
  DDSP neurale caricato via `nn~`, con spazio latente a 4 dimensioni).

---

## 3. Cosa è stato realizzato

### 3.1 Pulizia e correzione dei descrittori
I descrittori erano in parte **ridondanti o "piatti"** (il musicista li aveva giustamente
definiti "inutili"). Verificato empiricamente con test headless e corretto:
- **`energy`** non è più un doppione di `mean_speed`: ora misura l'**agitazione** reale del
  branco (sforzo di sterzata/accelerazione), un canale indipendente.
- **`center_x/y`** espansi attorno al centro: prima il centroide di 100 pesci restava
  incollato a 0.5 (pan impercettibile), ora usa tutta la corsa.
- **`fish_count`** reso "vivo": normalizzato sul numero massimo di pesci, ora varia
  realmente con la popolazione.

### 3.2 Popolazione dei pesci controllabile dal vivo
Aggiunto un controllo per variare il **numero di pesci da 1 a 100** in tempo reale
(tastiera `-`/`=` e fader MIDIMIX). Questo rende `fish_count` un segnale espressivo:
pochi pesci → suono rarefatto, molti pesci → texture piena.

### 3.3 Integrazione con il granulatore
Aggiunti messaggi OSC **già scalati** (`/gran/*`) così la patch Max non deve fare calcoli:
- `/gran/pan` (posizione del branco → panning),
- `/gran/density` + `/gran/nchan` (numero di pesci → densità granulare / canali attivi),
- `/gran/noise` (agitazione + predatore + disordine → distorsione).

### 3.4 Integrazione con PLAUD (modello neurale DDSP)
- **Navigazione dello spazio latente:** la posizione del branco (`/plaud/x`, `/plaud/y`)
  diventa un "punto" che si muove nello spazio latente a 4 dimensioni del modello → il timbro
  cambia col movimento del branco.
- **Parametri DSP:** `/plaud/loudness` (dal numero di pesci, a finestra parziale così
  l'artista tiene il master) e `/plaud/temp` (dall'agitazione → caos della sintesi).
- Filosofia: i boids pilotano **pochi parametri espressivi**, l'artista tiene a mano il resto.

### 3.5 Mappatura MIDIMIX definitiva
Rimappata sui **8 fader fisici** dell'AKAI MIDIMIX (uno per parametro):
popolazione, coesione, separazione, rumore, cibo, predatore, densità musicale, sezione.

### 3.6 Documentazione prodotta
- Contratto/spec di integrazione OSC per granulatore e PLAUD.
- Brief tecnico per l'incontro con l'autore di PLAUD (domande su latenti, dataset, real-time).
- Piano "Strada A": come far sì che i fader modifichino la **fisica** dei pesci (e quindi i
  descrittori) in modo coerente.

---

## 4. Problemi risolti (principali)

- **Descrittori ridondanti/piatti** → puliti e resi indipendenti (§3.1), verificati con misure.
- **Solo una sinusoide in uscita** → capito che un solo descrittore era cablato al suono; il
  resto arrivava a Max ma non era collegato. La soluzione è cablare i descrittori ai motori
  sonori (granulatore/PLAUD), non modificare l'algoritmo.
- **Saturazione precoce dei latenti:** i valori `/plaud/x/y` toccavano il limite già a metà
  schermo (colpa dell'espansione pensata per il pan). Risolto separando i due segnali: il pan
  resta espanso, la navigazione del latente usa la posizione grezza 0..1, proporzionale.
- **Distinzione dei due motori:** chiarito che granulatore e PLAUD sono strumenti diversi, con
  parametri diversi, da pilotare separatamente.

---

## 5. Workflow e collaborazione

- Lavoro isolato su un **branch git dedicato** (`granular-integration`) per non intaccare la
  linea principale; `main` resta stabile.
- Coordinamento tra i membri del team (chi lavora sulle Markov, chi sul granulatore/PLAUD in
  Max) tramite branch separati e sincronizzazione via GitHub.
- Contratto OSC mantenuto **stabile e retro-compatibile**: le nuove funzionalità sono state
  aggiunte senza rompere gli indirizzi esistenti.

---

## 6. Stato attuale

- Sistema **end-to-end funzionante**: i movimenti del branco pilotano dal vivo il granulatore
  e i parametri di PLAUD, tutto controllabile dal MIDIMIX.
- Dati verificati e coerenti; i due motori sonori collegati e testati in Max.

## 7. Prossimi step

- **PLAUD:** confermare il range dei latenti con l'autore e rifinire la navigazione.
- **Dataset dell'artista / training AI:** granulare/sintetizzare i suoni dell'artista (e il
  modello allenato) come materia sonora della performance.
- **Markov ↔ campioni:** collegare la generazione simbolica ai suoni dell'artista.
- **UI / leggibilità:** rendere visibile il legame movimento→suono per il pubblico.
- **Rifiniture performative:** preset, backup registrato, prova generale.
