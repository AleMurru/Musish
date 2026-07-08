# Implementazioni da fare — Acquario Boids (Codex)

Checklist di criticità e migliorie, verificate sul codice attuale (con riferimenti `file:riga`).
Il tema centrale resta il **divario codice ↔ suono**: il Python genera molto, ma poco arriva all'orecchio.

> Legenda priorità: **P0** = fix rapido/isolato, rischio zero · **P1** = alto impatto sul suono · **P2** = strutturale · **P3** = rifinitura.

---

## 0. Ordine consigliato di attacco

1. **P0 — Fix food/predator proporzionale** (2 righe, isolato, subito).
2. **P1 — Strumento vero per le note** (via DAW o synth in Max, non GM) + **riverbero/spazio**.
3. **P1 — Clock + quantizzazione** a griglia di 16esimi.
4. **P2 — Layer → timbri** distinti in Max.
5. **P2 — Basso sull'accordo** (armonia udibile).
6. **P3 — Cablare i descrittori "morti"**, de-duplicare descrittori, flash causale, un solo formato nota OSC.

---

## 1. Bug concreti

### 1.1 [P0] Fader food/predator del MIDIMIX non proporzionali (on/off)
- **Dove:** `main.py:170-173` (accende un attrattore virtuale se `food_amount > 0.01`) + `boids.py:130` e `boids.py:135` (la forza usata è `food_strength`/`predator_strength`, NON `food_amount`/`predator_amount`).
- **Problema:** i fader 5/6 del MIDIMIX cambiano solo l'on/off, non l'intensità. La doc utente (`DA_LEGGERE_...MAP.md`) li intende 0→3 proporzionali. Mismatch intento/implementazione.
- **Fix (2 righe):** nel caso di attrattore/repulsore virtuale usare `food_amount`/`predator_amount` come intensità. Es. in `boids.flock`, per il ramo virtuale moltiplicare lo steer per `controls.food_amount` (e `predator_amount`) invece che per `food_strength`/`predator_strength`; oppure in `main.py`, quando si attiva l'attrattore virtuale, impostare la forza effettiva = `food_amount`.

### 1.2 [P3] Rischio doppio-trigger delle note via OSC
- **Dove:** `osc_io.py:62-94` invia sia `/music/note` sia `/music/midi`; le patch fanno `route ... midi note ...`.
- **Stato:** in `max/aquarium_netreceive_sound_v2.maxpat` risulta cablato al `makenote` **solo** `midi` → in quella patch **niente doppio-trigger**. Ma altre patch (`aquarium_receiver`, `aquarium_netreceive_sound`) instradano anche `note`: se entrambi finiscono al synth, ogni nota suona doppia.
- **Fix:** verso il synth tenere **un solo formato** (consigliato `/music/midi`) e non cablare anche `/music/note`.

---

## 2. Criticità strutturali (divario codice ↔ suono)

*Verificate sul codice attuale — nessuna toccata dai commit del remap MIDIMIX.*

### 2.1 [P2] Armonia cosmetica
- **Dove:** `osc_io.py:14` → `(degree + chord_degree) % 7`.
- **Problema:** somma grado melodico e radice d'accordo e wrappa mod 7; non produce mai accordi (niente simultaneità) e distrugge la relazione d'ottava. La progressione i-VI-iv-V **non si sente come accordi**.

### 2.2 [P1] Nessun clock / griglia ritmica
- **Dove:** `main.py:194-203`.
- **Problema:** il momento in cui parte la nota è deciso da `events_per_second` (density + mean_speed), **scollegato** da `duration_beats` prodotto dalla rhythm chain. Il ritmo udibile è la frequenza di emissione, non la catena ritmica → risultato informe, la rhythm chain è decorativa.

### 2.3 [P2] I layer non diventano timbro
- **Dove:** patch Max (grep): `route ... midi note rest` + un solo `makenote → noteout`, **nessun `route` per `layer_id`**.
- **Problema:** i 6 layer (drone/bass/lead/perc/granular/noise) esistono come numero ma **suonano identici**. Tutta la generazione multi-layer è muta.

### 2.4 [P3] Descrittori ridondanti
- **Dove:** `descriptors.py`.
- **Problema:** `energy == mean_speed` (identici) e `density == 1 - nearest_distance` (perfettamente anticorrelati): 2 coppie su 10 portano lo stesso segnale. Il musicista mappa canali "diversi" che sono uguali.
- **Fix:** rimpiazzare `energy` con un descrittore indipendente (es. accelerazione/varianza = nervosismo, o vorticità = rotazione collettiva); tenere solo uno tra `density` e `nearest_distance`.

### 2.5 [P3] Flash su pesce casuale (legame visuale non causale)
- **Dove:** `main.py:200` → `random.choice(flock).flash = 1.0`.
- **Problema:** lampeggia un pesce a caso, non quello che ha "causato" la nota → il pubblico non aggancia causa→effetto.
- **Fix:** flash sul pesce più veloce/rilevante; oppure trigger su eventi salienti (scatto/collisione) come nella versione `Claude/` (`/aq/event/dart|turn|collision`), da travasare.

---

## 3. Come nasce il suono adesso (per capire dove intervenire)

*Dai `patchline` reali di `max/aquarium_netreceive_sound_v2.maxpat`.*

- **Percorso 1 — drone (unico suono sintetizzato DENTRO Max):**
  `route direct → unpack → mean_speed → expr 80+f*820 → line~ → cycle~`, `energy → expr 0.03+f*0.27 → line~ → *~ → ezdac~`.
  Cioè **una sola sinusoide**: pitch = velocità media del branco, volume = energia.
- **Percorso 2 — note Markov:** `route midi → unpack → makenote → noteout` = **MIDI verso synth esterno/GM**. Le note **non** sono sintetizzate nella patch: senza strumento MIDI a valle, la melodia non si sente.
- **Descrittori/parametri "morti"** (unpackati ma non collegati): `center_x, center_y, density, spread, density_fader` (drone) e `layer_id, section_id` (note). **5 su 7 + i layer non toccano il suono.**

**Conseguenza:** il "thin" non è colpa dell'algoritmo, ma di **sintesi/timbro/effetti** — dominio del musicista. Il Python come generatore di materiale è già sufficiente.

---

## 4. Suggerimenti per l'impatto sul suono

### 4.1 [P1] Strumento vero per le note
- Instradare `noteout` verso uno strumento software in Ableton/DAW, **oppure** sintetizzare in Max con `poly~` + `saw~`/`cycle~` + filtro (`svf~`/`onepole~`) + `adsr~`. Il synth GM è il motivo #1 per cui suona povero.

### 4.2 [P1] Riverbero / spazio
- Un `cycle~ → dac~` è secco e clinico. Un solo send a un riverbero (anche `yafr2` dagli examples di Max) migliora la percezione più di qualsiasi modifica all'algoritmo. Vittoria più economica.

### 4.3 [P1] Clock + quantizzazione
- Far partire gli eventi da una **griglia di 16esimi al BPM** (un `[metro 125]` in Max o un accumulatore a beat in Python); density/rhythm decidono **quali slot** suonano (nota vs pausa). Dà groove e rende finalmente udibile la rhythm chain. `density_fader` = probabilità di riempimento degli slot.

### 4.4 [P2] Layer → timbri
- In Max, `route`-are per `layer_id` verso almeno 3 catene distinte: basso (`saw`/`tri` + filtro passa-basso), lead (`cycle~` + filtro), perc (burst di `noise~` + envelope corto). Senza, la generazione multi-layer è sprecata.

### 4.5 [P2] Basso sull'accordo (armonia udibile)
- A ogni cambio di `chord_degree`, inviare una nota di **basso = radice dell'accordo** su un canale MIDI dedicato: `ROOT_MIDI + SCALE_INTERVALS[chord_degree] - 12`. Così l'armonia si sente **sotto** la melodia, senza riscrivere `event_to_midi`.

### 4.6 [P3] Cablare i descrittori "morti"
- Ingrassare il drone (aggiungere una quinta e un'ottava leggermente detunate → pad invece di sinusoide) e usare i descrittori inutilizzati:
  - `center_y` → cutoff lowpass (luminosità);
  - `density` → detune / quantità di riverbero (tensione);
  - `spread` → ampiezza stereo.
- Quantizzare anche il **pitch del drone** alla scala (`SCALE_INTERVALS`) così pure il bordone è intonato, con `line~` più lungo per un glissato musicale invece che nervoso.

### 4.7 [P3] Un solo formato nota OSC
- Verso il synth tenere solo `/music/midi` (vedi 1.2) → elimina il possibile doppio-trigger.

---

## 5. Note
- Cosa già buono (da NON toccare): fallback FUDI `netreceive -u 7401` senza `oscparse`; debug MIDI che stampa i CC reali del MIDIMIX; `control_in` con alias multipli; mappatura MIDIMIX → ecosistema (il musicista scolpisce il mondo, il suono segue).
- Priorità secca (dai suggerimenti sul suono): **P0 food/predator → clock → layer→timbro → basso**.



## IMPORTANTE:
Verità scomoda: quello che senti NON è la Markov
[Sicuro] Nella patch ci sono due percorsi audio separati e indipendenti, e il più elaborato dei due probabilmente non lo stai sentendo.

Percorso 1 — il drone (è QUESTO che esce dalle casse di Max)
Traccia dei collegamenti:


netreceive 7401 → route "direct" → unpack (mean_speed energy center_x…)
  mean_speed → expr 80 + f*820   → line~ → cycle~   (oscillatore sinusoidale)
  energy     → expr 0.03 + f*0.27 → line~ → *~       (volume)
  cycle~ * volume → ezdac~ (uscita audio)
Cioè: un solo oscillatore sinusoidale, la cui altezza segue la velocità media del branco (80–900 Hz) e il cui volume segue l'energia. Questo è tutto ciò che Max sintetizza internamente. È un tono che scivola come una sirena a seconda di quanto corrono i pesci.

Percorso 2 — le note Markov (escono come MIDI, NON come audio di Max)

route "midi" → unpack (id note velocity duration layer section)
  note → makenote → noteout   → uscita MIDI di sistema
noteout manda le note a uno strumento MIDI esterno (il synth General MIDI del sistema, o un DAW). La patch non le sintetizza. Se non hai un synth collegato a quell'uscita MIDI, la melodia della Markov non si sente affatto — senti solo il drone del Percorso 1.

Cosa "segue" davvero (e cosa è morto)
[Sicuro] Guardando i patchline:

Drone pitch ← mean_speed. Drone volume ← energy (che però = mean_speed, quindi lo stesso segnale due volte).
Note MIDI: midi_note ← (degree+chord)%scala, velocity ← energy, duration_ms ← rhythm chain. Ma udibili solo se c'è uno strumento MIDI a valle.
Morti nella patch (unpackati ma non collegati a nulla): center_x, center_y, density, spread, density_fader del drone, e layer_id, section_id delle note. 5 descrittori su 7 e i layer non toccano il suono.
Correzione onesta rispetto a ieri: in questa v2 il route manda al makenote solo midi, non note → qui niente doppio-trigger. Buono.

Perché suona "thin"
Non è colpa dell'algoritmo. È che:

l'unico suono interno è una sinusoide nuda (nessun timbro, nessun effetto);
la parte ricca (le note) è delegata a un synth GM economico o a nulla;
quasi tutti i descrittori non sono cablati.
[Verosimilmente] La leva più grande per il "bello all'ascolto" non è la generazione, è la sintesi/timbro/effetti — cioè il dominio del musicista. Il Python come generatore di materiale è già abbastanza buono.

Come renderlo migliore (in ordine di resa sonora per sforzo)
1. Dai uno strumento vero alle note (impatto massimo). Instrada noteout verso uno strumento software in Ableton/DAW, oppure sintetizza dentro Max con poly~ + saw~/cycle~ + onepole/svf~ filtro + adsr~. Il synth GM è il motivo #1 per cui suona povero.

2. Aggiungi riverbero/spazio. Un cycle~ → dac~ è secco e clinico. Un solo send a un riverbero (anche yafr2 dagli examples di Max) cambia la percezione più di qualsiasi modifica all'algoritmo. Vittoria più economica in assoluto.

3. Ingrassa il drone e usa i descrittori morti. Da sinusoide a pad: aggiungi 2 oscillatori (una quinta e un'ottava, leggermente detunati). Poi cabla i descrittori inutilizzati:

center_y → cutoff di un lowpass (luminosità);
density → detune/quantità di riverbero (tensione);
spread → ampiezza stereo.

## Ultima risposta di claude:

La tua intuizione è corretta ma incompleta, e la parte mancante è importante: spostare il cuore sulla Markov non basta — anzi, rischia di peggiorare l'ascolto se prima non risolvi tre cose che oggi il drone stava mascherando. Ti spiego perché, poi come.

Perché oggi la Markov NON è il cuore (la causa radice)
[Sicuro] Il problema non è "usiamo le sinusoidi". È che le note della Markov non hanno uno strumento dove suonare. Ricorda la catena reale:

il drone sinusoidale è l'unico suono sintetizzato dentro Max → lo senti sempre;
le note Markov escono da noteout come MIDI verso un synth esterno → se non c'è nulla collegato, o c'è il synth General MIDI di sistema, la Markov è muta o suona come un piano scadente.
Quindi oggi il rapporto è invertito: il materiale musicale ricco (Markov) è orfano, e il ripiego (sonificazione sinusoidale) è protagonista. Per fare della Markov il cuore devi darle voci vere e retrocedere il drone a supporto.

I 3 problemi che il drone nascondeva (da risolvere PRIMA)
[Verosimilmente] Se colleghi la Markov a un buon synth così com'è, suonerà come note MIDI casuali — peggio del drone. Perché la sofisticazione non arriva all'orecchio:

Niente clock/griglia (main.py:194-203). Le note partono a una frequenza continua, non su una griglia di beat. Senza pulsazione, anche con un synth bellissimo suona informe. La rhythm chain non si sente.
Niente accordi veri (osc_io.py:14). (degree+chord_degree)%7 produce note singole spostate, mai un accordo. Manca l'armonia che tiene insieme la melodia.
Un solo timbro (patch Max). I 6 layer (bass/lead/perc/…) finiscono tutti sullo stesso makenote→noteout, canale unico. Senza separazione, non c'è arrangiamento: è tutto una voce sola.
Il drone continuo "riempiva" mascherando questi buchi. Toglilo senza risolverli e resti nudo.

Come si risolve: l'architettura obiettivo

Boids → descrittori + controlli
   │
   ├── MARKOV (cuore)  ── quantizzata su clock a 16esimi ──┐
   │     pitch · rhythm · chord · layer · section          │
   │                                                        ▼
   │        note per-layer su canali MIDI separati → 3-4 STRUMENTI veri
   │        (basso · lead · perc · pad d'accordo)   (Ableton o poly~ in Max)
   │
   └── descrittori (mean_speed, density, spread…) → MODULANO gli strumenti
         (cutoff, riverbero, detune, dinamica)  ← SUPPORTO, non più protagonista
Le quattro mosse concrete, in ordine:

Voci vere per la Markov. Ogni layer_id → un canale MIDI → uno strumento distinto. Il basso su un synth basso, il lead su un synth lead, la perc su un campionatore/rumore. È questo che trasforma "note" in "musica prodotta".
Clock a 16esimi. Python possiede il tempo: un accumulatore a beat al BPM, le note si allineano alla griglia, la rhythm chain decide quali slot suonano (nota/pausa). Ora la ritmica si sente.
Accordi reali. A ogni cambio d'accordo, manda una triade simultanea (radice+terza+quinta) su un canale "pad", e fai un basso sulla radice. La melodia resta sopra, condizionata sull'accordo. Così c'è armonia percepibile.
Il drone diventa un pad armonico di supporto, guidato dall'accordo corrente (non più dalla velocità); mean_speed/density passano a modulare filtro/riverbero.
La decisione che determina tutto il resto
[Sicuro] Prima di scrivere una riga, serve una scelta che cambia l'intera implementazione: dove avviene la sintesi delle voci Markov?

Opzione A — In Ableton (strumenti del musicista). Python/Max manda MIDI multi-canale ad Ableton via porta MIDI virtuale (loopMIDI/IAC). Pro: timbri professionali subito, è il mestiere del musicista, sound design potente. Contro: serve configurare il routing MIDI e il set di Ableton. Consigliata, dato che hai un musicista con Ableton — la qualità sonora la porta lui, noi portiamo il materiale.
Opzione B — In Max (poly~). Costruiamo 3-4 voci sintetiche dentro Max. Pro: tutto self-contained, nessun routing esterno. Contro: i timbri li devi costruire tu, resa inferiore agli strumenti di un DAW.
[Verosimilmente] A è la strada giusta per "renderlo bello all'ascolto": il collo di bottiglia è il timbro, e il timbro lo fa meglio Ableton. Il nostro Python resta il generatore (clock + Markov + accordi + layer su canali MIDI); Ableton è il motore sonoro.

Dimmi tu: A (MIDI multi-canale → Ableton) o B (voci poly~ in Max)? Da quella risposta dipende se il prossimo lavoro è "canali MIDI + clock in Python" oppure "costruire un synth in Max". Io vado su A.