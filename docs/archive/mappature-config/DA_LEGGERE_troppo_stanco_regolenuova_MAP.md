# Mappatura MIDIMIX → parametri boids

Ho mappato i fader del MIDIMIX in modo che controllino **prima il comportamento dei boids**, e solo dopo, indirettamente, il suono.

Il mapping è definito in:

```text
Codex/aquarium_boids/config.py
```

nella variabile:

```python
MIDI_CC_MAPPING
```

Attualmente è:

```python
MIDI_CC_MAPPING = {
    19: ("alignment_weight", 0.0, 3.0, False),
    20: ("cohesion_weight", 0.0, 3.0, False),
    21: ("separation_weight", 0.0, 4.0, False),
    22: ("noise_weight", 0.0, 1.5, False),
    23: ("food_amount", 0.0, 3.0, False),
    24: ("predator_amount", 0.0, 3.0, False),
    25: ("density_fader", 0.0, 1.0, False),
    26: ("section_id", 0.0, 5.0, True),
}
```

---

## Mappatura dei fader

| MIDIMIX | CC | Parametro Python | Range | Effetto |
|---|---:|---|---:|---|
| Fader 1 | 19 | `alignment_weight` | 0 → 3 | quanto i boids si allineano |
| Fader 2 | 20 | `cohesion_weight` | 0 → 3 | quanto il branco si compatta |
| Fader 3 | 21 | `separation_weight` | 0 → 4 | quanto i boids si evitano |
| Fader 4 | 22 | `noise_weight` | 0 → 1.5 | quanta turbolenza casuale c’è |
| Fader 5 | 23 | `food_amount` | 0 → 3 | attrattore virtuale verso il centro |
| Fader 6 | 24 | `predator_amount` | 0 → 3 | repulsore virtuale dal centro |
| Fader 7 | 25 | `density_fader` | 0 → 1 | densità degli eventi Markov |
| Fader 8 | 26 | `section_id` | 0 → 5 | sezione musicale |

---

# Come viene scalato il valore MIDI

Il MIDIMIX manda valori MIDI:

```text
0 → 127
```

Python li converte nel range del parametro.

Esempio per `alignment_weight`:

```text
MIDI 0   → alignment_weight 0.0
MIDI 64  → alignment_weight circa 1.5
MIDI 127 → alignment_weight 3.0
```

Esempio per `separation_weight`:

```text
MIDI 0   → separation_weight 0.0
MIDI 127 → separation_weight 4.0
```

Esempio per `section_id`:

```text
MIDI 0   → section_id 0
MIDI 127 → section_id 5
```

`section_id` è quantizzato a intero.

---

# Cosa fa ogni parametro nel modello boids

## 1. `alignment_weight`

Controlla la forza di allineamento.

Nel modello boids:

```text
alignment = tendenza a seguire la direzione media dei vicini
```

Fader basso:

```text
ogni boid va più per conto suo
```

Fader alto:

```text
il branco si muove in modo più coordinato
```

Effetto sonoro indiretto:

```text
direction_coherence aumenta
ritmo più stabile
movimento più leggibile
```

---

## 2. `cohesion_weight`

Controlla la forza di coesione.

```text
cohesion = tendenza ad avvicinarsi al centro dei vicini
```

Fader basso:

```text
i boids si disperdono
```

Fader alto:

```text
si aggregano in branco
```

Effetto sonoro:

```text
density aumenta
spread diminuisce
secondo oscillatore cambia
armonia più compatta
```

---

## 3. `separation_weight`

Controlla la forza di separazione.

```text
separation = evitare collisioni e sovrapposizioni
```

Fader basso:

```text
boids più vicini, meno distanza personale
```

Fader alto:

```text
boids si respingono di più
```

Effetto sonoro:

```text
spread e nearest_distance cambiano
texture più rarefatta
```

---

## 4. `noise_weight`

Aggiunge turbolenza casuale.

```text
noise = forza randomica sul movimento
```

Fader basso:

```text
movimento fluido e ordinato
```

Fader alto:

```text
movimento caotico, nervoso
```

Effetto sonoro:

```text
mean_speed/energy più instabili
Markov più variabile
suono più glitch/agitato
```

---

## 5. `food_amount`

È un attrattore virtuale verso il centro dello schermo.

Prima il “food” funzionava solo con mouse sinistro. Ora il fader crea automaticamente una forza attrattiva verso:

```text
centro dell’acquario
```

Fader basso:

```text
nessun attrattore automatico
```

Fader alto:

```text
i boids vengono richiamati al centro
```

Effetto sonoro:

```text
branco più compatto
density aumenta
center_x / center_y tendono al centro
```

---

## 6. `predator_amount`

È un repulsore virtuale dal centro dello schermo.

Prima il predatore funzionava solo con mouse destro. Ora il fader crea automaticamente una forza di fuga dal centro.

Fader basso:

```text
nessun predatore automatico
```

Fader alto:

```text
i boids scappano dal centro
```

Effetto sonoro:

```text
energia aumenta
spread aumenta
movimento più drammatico
```

---

## 7. `density_fader`

Questo non è propriamente un parametro boids. È un parametro musicale.

Controlla:

```text
quanti eventi Markov vengono generati
quanto è densa la musica
quanto la generazione passa da collettiva a puntiforme
```

Fader basso:

```text
pochi eventi
texture più lenta
```

Fader alto:

```text
più eventi
più blip / granularità
```

---

## 8. `section_id`

Controlla la sezione musicale.

Valori:

```text
0 = intro
1 = growth
2 = dense
3 = chaos
4 = release
5 = outro
```

Influenza la generazione degli eventi, soprattutto layer e carattere.

---

# In sintesi

I primi 6 fader controllano l’ecosistema:

```text
alignment
cohesion
separation
noise
food
predator
```

Gli ultimi 2 controllano la generazione musicale:

```text
density_fader
section_id
```

Quindi la logica è:

```text
MIDIMIX
↓
modifica comportamento boids
↓
boids modificano descriptor
↓
descriptor modificano Markov e Max
↓
suono cambia
```

Questa è la mappatura corretta per rendere il sistema performativo e non solo “parametrico”.
