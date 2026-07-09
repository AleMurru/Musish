# Audio & Ableton — far suonare bene la Markov Chain (Opzione A-2)

Guida operativa completa: ogni step + tutto il codice da creare. Obiettivo: **le note della
Markov diventano MIDI multicanale, sincronizzato, che suona negli strumenti di Ableton**.

> Principio guida (non dimenticarlo): il codice consegna **materiale musicale** (note giuste,
> in tempo, con armonia e layer separati). Il **timbro/bellezza** lo fa Ableton (strumenti +
> effetti) ed è lavoro del musicista. Le due cose sono separate: prima materiale solido, poi suono bello.

---

## 0. Architettura obiettivo (A-2)

```
Boids → descrittori + controlli
   │
   ├─ MARKOV (Python)  ── clock 16esimi ──┐
   │   pitch · rhythm · accordi · layer   │
   │                                      ▼
   │        NOTE MIDI multicanale → loopMIDI → ABLETON (strumenti reali)
   │        (lead/bass/perc su canali diversi + pad accordo + basso)
   │
   └─ descrittori → CC MIDI → modulano gli strumenti in Ableton (cutoff, reverb…)
   └─ (Max resta solo per il drone di supporto + visual, via OSC — invariato)
```

Cosa cambia rispetto a oggi: le note **non** passano più da `noteout` a un synth GM. Python le
manda direttamente a loopMIDI, **un canale per layer**, su una **griglia di beat**.

---

## STEP 1 — Prerequisiti

1. **loopMIDI** (Tobias Erichsen, gratis): crea una porta virtuale MIDI su Windows (che non ha IAC).
   - Aprilo → pulsante `+` in basso a sinistra → crea la porta chiamata **`Aquarium`**.
2. **Dipendenze Python: NESSUNA.** Non installare `mido`/`python-rtmidi` (su Python 3.14 non hanno
   wheel pronte e la compilazione fallisce senza Visual Studio Build Tools). Usiamo **`pygame.midi`**,
   già presente nel progetto (lo usa anche `midi_in.py`). Backend portmidi, vede i device loopMIDI.
3. **Ableton Live** con qualche strumento (Operator, Wavetable, o strumenti di terze parti).

---

## STEP 2 — Test da 5 minuti SENZA codice (verifica la catena)

Prima di scrivere codice, verifica che il "materiale" Markov suoni decente con uno strumento vero:

1. In Max, cambia la destinazione del `noteout` esistente sulla porta **`Aquarium`** (menu a tendina del `noteout`).
2. In Ableton → **Preferences → Link/Tempo/MIDI**: sotto *Input*, attiva **`Aquarium`** (colonna *Track* = On).
3. Crea una traccia MIDI → **MIDI From = Aquarium** → **Monitor = In** → ci metti uno strumento (es. un pad di Wavetable).
4. Lancia i boids: ora la melodia Markov suona **quello strumento**, non il synth di sistema.

**Se ti piace come materiale** → costruisci gli step successivi (multicanale + clock + accordi).
**Se non ti convince nemmeno con un buon strumento** → il problema è nella generazione (ordine-1,
catene scorrelate): lì il lavoro è sulla Markov, non sull'audio.

---

## STEP 3 — Nuovo modulo Python: `aquarium_boids/midi_out.py`

Gestisce la porta loopMIDI (via `pygame.midi`), la mappa layer→canale, l'invio note con note-off
ritardato, e i CC. **Nessuna dipendenza nuova.**

```python
# aquarium_boids/midi_out.py
from __future__ import annotations
import time
import pygame.midi

from .config import ROOT_MIDI, SCALE_INTERVALS

# layer_id -> canale MIDI (0-based; in Ableton appare come Ch 1..16)
LAYER_CHANNEL = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}  # drone,bass,lead,perc,granular,noise
CHORD_CHANNEL = 6   # pad d'accordo  (Ch 7 in Ableton)
BASS_CHANNEL = 7    # basso          (Ch 8 in Ableton)


def degree_to_midi(degree: int, octave: int, root: int = ROOT_MIDI) -> int:
    """Grado di scala -> nota MIDI. L'armonia NON viene collassata qui (vedi chord_notes)."""
    n = len(SCALE_INTERVALS)
    idx = degree % n
    extra_oct = degree // n           # gradi > 6 salgono d'ottava, non wrappano
    return root + SCALE_INTERVALS[idx] + 12 * (octave + extra_oct)


def chord_notes(chord_degree: int, root: int = ROOT_MIDI) -> list[int]:
    """Triade diatonica: fondamentale + terza + quinta (gradi 0,2,4 sopra la radice)."""
    return [degree_to_midi(chord_degree + t, 0, root) for t in (0, 2, 4)]


class MidiOut:
    """Output MIDI via pygame.midi (portmidi). Niente mido/python-rtmidi, niente compilatore."""
    def __init__(self, port_name: str = "Aquarium"):
        pygame.midi.init()
        self.out = None
        self._pending: list[tuple[float, int, int]] = []  # (due_time, channel, note)
        dev = self._find(port_name)
        if dev is not None:
            self.out = pygame.midi.Output(dev)   # latency=0 di default

    def _find(self, name: str):
        for i in range(pygame.midi.get_count()):
            _interf, dname, _is_in, is_out, _opened = pygame.midi.get_device_info(i)
            label = dname.decode(errors="ignore") if isinstance(dname, bytes) else str(dname)
            if is_out and name.lower() in label.lower():
                print(f"[midi_out] trovato '{label}' id={i}")
                return i
        print(f"[midi_out] porta '{name}' non trovata tra gli output MIDI. "
              f"Crea la porta in loopMIDI e riavvia.")
        return None

    def note(self, channel: int, note: int, velocity: int, duration_s: float):
        if self.out is None:
            return
        note = max(0, min(127, int(note)))
        velocity = max(1, min(127, int(velocity)))
        self.out.note_on(note, velocity, channel)
        self._pending.append((time.time() + duration_s, channel, note))

    def cc(self, channel: int, control: int, value_0_1: float):
        if self.out is None:
            return
        v = max(0, min(127, int(value_0_1 * 127)))
        self.out.write_short(0xB0 + channel, control, v)   # 0xB0 = Control Change

    def tick(self, now: float | None = None):
        """Invia i note-off scaduti. Chiamare a ogni frame."""
        if self.out is None:
            return
        now = now or time.time()
        still = []
        for due, ch, note in self._pending:
            if due <= now:
                self.out.note_off(note, 0, ch)
            else:
                still.append((due, ch, note))
        self._pending = still

    def panic(self):
        """All-notes-off su tutti i canali (a fine sessione o su reset)."""
        if self.out is None:
            return
        for ch in range(16):
            self.out.write_short(0xB0 + ch, 123, 0)   # CC123 = all notes off

    def close(self):
        self.panic()
        if self.out is not None:
            self.out.close()
        # NB: non chiamare pygame.midi.quit() se midi_in.py usa ancora pygame.midi.
```

**Perché `degree_to_midi` così:** rispetto all'attuale `event_to_midi` (`(degree+chord)%7`, che
collassava l'armonia), qui il grado melodico resta puro e i gradi alti salgono d'ottava invece di
wrappare. L'armonia la porta `chord_notes` come **triade vera** su un canale dedicato.

---

## STEP 4 — Il clock a 16esimi: `BeatClock`

Mettilo in `midi_out.py` o in un file `clock.py`. Decide *quando* può suonare una nota.

```python
class BeatClock:
    """Griglia di 16esimi. tick(dt) ritorna la lista di step scattati in questo frame."""
    def __init__(self, bpm: float = 120.0, steps_per_beat: int = 4):
        self.steps_per_beat = steps_per_beat
        self.set_bpm(bpm)
        self.acc = 0.0
        self.step = 0

    def set_bpm(self, bpm: float):
        self.bpm = bpm
        self.step_dur = 60.0 / bpm / self.steps_per_beat  # durata di un 16esimo in secondi

    def tick(self, dt: float) -> list[int]:
        self.acc += dt
        fired = []
        while self.acc >= self.step_dur:
            self.acc -= self.step_dur
            fired.append(self.step)
            self.step += 1
        return fired
```

**Concetto chiave:** oggi le note partono a `events_per_second` (frequenza continua) → ritmo informe.
Con la griglia, le note possono partire **solo sui 16esimi**, e la rhythm chain/densità decide *quali*
slot suonano. Questo è ciò che dà **groove**.

---

## STEP 5 — La logica musicale sulla griglia (glue in `main.py`)

Sostituisce il blocco `if now >= next_event_time:` attuale (main.py:194-203).
Usa il `SymbolicGenerator` esistente per pitch/rhythm/velocity/layer, ma il **tempo** e
l'**armonia** li governa la griglia.

```python
# --- setup (prima del loop) ---
from aquarium_boids.midi_out import MidiOut, BeatClock, degree_to_midi, chord_notes
from aquarium_boids.config import BPM, ROOT_MIDI
import random

midi = MidiOut("Aquarium")
clock = BeatClock(BPM)
CHORD_PROGRESSION = [0, 5, 3, 4]   # i - VI - iv - V (gradi di scala)
STEPS_PER_CHORD = 16               # un accordo per battuta (16 sedicesimi)
current_chord = -1

# --- dentro il loop, DOPO aver calcolato `descriptors` ---
beat_s = 60.0 / BPM
for step in clock.tick(dt):
    # 1) cambio accordo ogni 16 step -> pad (triade tenuta) + basso sulla radice
    if step % STEPS_PER_CHORD == 0:
        current_chord = CHORD_PROGRESSION[(step // STEPS_PER_CHORD) % len(CHORD_PROGRESSION)]
        for n in chord_notes(current_chord):
            midi.note(CHORD_CHANNEL, n, velocity=52, duration_s=beat_s * 4)   # pad ~4 beat
        midi.note(BASS_CHANNEL, degree_to_midi(current_chord, octave=-1), 85, beat_s * 2)

    # 2) LEAD: la densità decide se questo 16esimo suona
    p_note = 0.12 + controls.density_fader * 0.7
    if random.random() < p_note:
        ev = generator.generate(descriptors, controls)      # riusa le catene Markov
        if ev.event_type == "note":
            note = degree_to_midi(ev.degree, ev.octave)
            midi.note(LAYER_CHANNEL[ev.layer_id], note, ev.velocity, ev.duration_beats * beat_s)

    # 3) BASSO ritmico sul battere (ogni 4 step) — rinforza la pulsazione
    if step % 4 == 0 and current_chord >= 0:
        midi.note(BASS_CHANNEL, degree_to_midi(current_chord, octave=-1), 70, beat_s * 0.5)

    # 4) PERC su controtempo quando la densità è alta (nota fissa = campione perc in Ableton)
    if controls.density_fader > 0.5 and step % 4 == 2:
        midi.note(LAYER_CHANNEL[3], 60, velocity=90, duration_s=beat_s * 0.25)

# --- ogni frame (fuori dal for) ---
midi.tick()                                   # spegne le note scadute
# CC continui dai descrittori (una volta ogni ~50ms basta):
midi.cc(LAYER_CHANNEL[2], 74, descriptors.get("center_y", 0.5))   # brightness/cutoff sul lead
midi.cc(CHORD_CHANNEL, 91, descriptors.get("density", 0.0))       # reverb send sul pad
midi.cc(BASS_CHANNEL, 1,  descriptors.get("mean_speed", 0.0))     # mod wheel sul basso
```

**Note di design (v1, da rifinire):**
- L'accordo lo governa la **griglia**, non più il contatore interno di `SymbolicGenerator`
  (così pad, basso e melodia condividono lo stesso accordo). In seguito si può spostare la scelta
  dell'accordo in una **catena di Markov lenta** invece del ciclo fisso `[0,5,3,4]`.
- La rhythm chain di `generator` ora determina la **lunghezza** della nota (`duration_beats`), non più il timing.
- `p_note` lega la **densità del branco** al riempimento della griglia: branco denso → più note.

Alla chiusura del programma: `midi.close()` (manda all-notes-off).

---

## STEP 6 — Setup di Ableton (dove nasce il "suona bene")

Una traccia MIDI per canale. Per ognuna: **MIDI From = Aquarium**, **il canale giusto**, **Monitor In**.

| Traccia | Canale (Ableton) | Sorgente | Strumento consigliato | Effetti |
|---|---:|---|---|---|
| Lead | Ch 3 | layer 2 | Wavetable/Operator (lead) | delay + riverbero |
| Bass | Ch 8 | canale basso | synth sub/saw + filtro | saturazione leggera |
| Pad accordo | Ch 7 | canale pad | Wavetable pad, attacco lento | riverbero ampio |
| Perc | Ch 4 | layer 3 | Drum Rack / campione perc | compressione |
| (Granular/Noise) | Ch 5/6 | layer 4/5 | texture/noise | filtro + reverb |

Impostare il **BPM di Ableton = BPM del `config.py`** (default 120). Nella traccia, "MIDI From" →
scegli **Aquarium** e sotto il **canale** specifico (Ch. 3, Ch. 7, …), così ogni layer va allo strumento giusto.

**Mapping dei CC in Ableton:** click su *MIDI* (in alto a destra) → muovi il parametro (es. cutoff) →
il CC in arrivo lo aggancia. Così i descrittori del branco modulano il suono dal vivo.

| Descrittore | CC inviato | Canale | Parametro Ableton suggerito |
|---|---:|---|---|
| `center_y` | 74 | Lead | cutoff filtro (brightness) |
| `density` | 91 | Pad | reverb send (tensione) |
| `mean_speed` | 1 | Bass | mod/drive |
| `spread` | (agg.) | Master | ampiezza stereo/riverbero |

---

## STEP 7 — (v2) Sincronizzazione col clock di Ableton — `aalink`

La v1 tiene il BPM in Python (semplice, ma può derivare nel lungo). La v2 aggancia la griglia al
**transport di Ableton** via **Ableton Link**:

```bash
pip install aalink   # richiede Python 3.9+; se le wheel mancano su 3.13/3.14, usa un venv 3.11/3.12
```

Sketch (asyncio):
```python
import asyncio
from aalink import Link

async def run():
    link = Link(bpm=120)          # si allinea agli altri peer Link (Ableton con "Link" attivo)
    while True:
        await link.sync(1/4)      # sveglia ad ogni 16esimo, in fase con Ableton
        on_step(...)              # stessa logica dello STEP 5
```

In Ableton: attiva **Link** (in alto a sinistra). Da quel momento Python e Ableton condividono
tempo e fase → niente deriva. Questo è ciò che fa la differenza tra "generativo che grooca" e
"due macchine che vanno per conto loro".

> Nota: la v2 comporta rendere il loop principale asincrono o eseguire il clock su un thread.
> Va progettata con cura per non rompere il loop pygame. Farla solo dopo che la v1 suona bene.

---

## STEP 8 — Cosa NON tocchiamo e cosa resta al musicista

- **Resta com'è:** il flusso OSC verso Max per i descrittori + il drone di supporto + il visual.
  Non c'è contesa di porte perché ad Ableton mandiamo **MIDI** (loopMIDI), non OSC.
- **Al musicista (in Ableton):** scelta strumenti, sound design, effetti, mix, e la mappatura fine
  dei CC. È qui che il "materiale" diventa "musica bella". Noi garantiamo che il materiale sia
  ritmicamente saldo (clock), armonicamente sensato (accordi+basso) e separato per timbro (canali).

---

## Checklist finale

- [ ] loopMIDI installato, porta `Aquarium` creata.
- [ ] Nessuna install: usiamo `pygame.midi` (già presente).
- [ ] Test 5 minuti (STEP 2) superato: la Markov suona uno strumento vero.
- [ ] Creato `aquarium_boids/midi_out.py` (STEP 3) + `BeatClock` (STEP 4).
- [ ] Integrato lo scheduler in `main.py` (STEP 5), rimosso il vecchio blocco `events_per_second`.
- [ ] Ableton: BPM allineato, una traccia per canale con MIDI From = Aquarium + canale (STEP 6).
- [ ] CC mappati sui parametri (STEP 6).
- [ ] (Opzionale v2) `aalink` + Link attivo in Ableton (STEP 7).

## Troubleshooting rapido

- **Nessun suono:** la porta `Aquarium` compare tra i device output? Verifica con
  `python -c "import pygame.midi as m; m.init(); [print(i, m.get_device_info(i)) for i in range(m.get_count())]"`.
  In Ableton la traccia ha Monitor = In e il canale giusto? BPM allineato?
- **Note che restano "appese":** manca `midi.tick()` ogni frame o `midi.close()`/`panic()` all'uscita.
- **Ritmo che deriva dopo minuti:** è il limite della v1 (BPM fisso) → passa alla v2 (Link).
- **Tutto su un timbro:** le tracce Ableton non filtrano per canale → controlla il campo canale in "MIDI From".
```
