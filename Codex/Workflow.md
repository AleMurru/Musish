# Workflow finale ideale — MIDIMIX → Python → Max

## Idea centrale

Il workflow più ordinato per la performance è:

```text
MIDIMIX
↓
main.py
  - controlla boids
  - controlla Markov
  - calcola descriptor
↓
Max
  - riceve descriptor
  - riceve eventi simbolici
  - renderizza synth/effects
```

In questo modello:

```text
Python = ecosistema / controllo / generazione
Max    = rendering sonoro
```

Il controller fisico non passa più necessariamente da Max per controllare i pesci. I fader controllano direttamente `main.py`; Max riceve solo i dati generati e li trasforma in suono.

---

## Perché è il workflow più efficiente

Rispetto al flusso:

```text
MIDIMIX → Max → Python → Max
```

il flusso diretto:

```text
MIDIMIX → Python → Max
```

ha alcuni vantaggi:

- meno passaggi;
- meno latenza;
- `main.py` è controllato direttamente;
- Max resta concentrato sul rendering sonoro;
- i mapping dei fader possono essere salvati nel codice;
- tastiera/mouse e Max→Python possono restare come fallback.

---

## Attenzione tecnica

Non conviene che Max e Python leggano contemporaneamente lo stesso MIDIMIX, perché su Windows un device MIDI può non essere multi-client.

Quindi per la performance principale:

```text
MIDIMIX aperto da Python
Max non legge direttamente MIDIMIX
Max riceve solo dati da Python
```

Se il musicista vuole usare il MIDIMIX anche per effetti Max, ci sono due possibilità:

1. usare un driver/virtual MIDI multi-client;
2. lasciare alcuni controlli a Max e altri a Python, ma con routing più complesso.

Per ora scegliamo la soluzione più chiara:

```text
MIDIMIX controlla Python
Python manda dati a Max
```

---

## Mappatura proposta

| MIDIMIX | Controllo in `main.py` | Effetto |
|---|---|---|
| Fader 1 | `density_fader` | più/meno eventi Markov |
| Fader 2 | `alignment_weight` | branco più allineato |
| Fader 3 | `cohesion_weight` | branco più compatto |
| Fader 4 | `separation_weight` | pesci più distanti |
| Fader 5 | `noise_weight` | più caos/turbolenza |
| Fader 6 | `food_strength` | forza attrattore |
| Fader 7 | `predator_strength` | forza predatore |
| Fader 8 | `section_id` | intro/growth/dense/chaos/release/outro |

---

## Output verso Max

Python continua a mandare a Max:

```text
/aquarium/direct
/aquarium/descriptors
/music/note
/music/rest
/music/event
```

più il fallback plain UDP:

```text
direct ...
note ...
midi ...
rest ...
```

Max deve quindi renderizzare:

- descriptor continui;
- eventi simbolici Markov;
- sezioni;
- layer.

---

## Stato implementativo

Il progetto ora supporta tre modalità di controllo:

```text
1. Tastiera/mouse → Python                 // fallback locale
2. Max UDP → Python                        // fallback/controller esterno
3. MIDIMIX diretto → Python → Max          // workflow principale live
```

Il workflow principale consigliato è il terzo.
