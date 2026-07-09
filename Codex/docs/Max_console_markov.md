# Max console — dati Markov v2 / Aquarium

Questi sono dati che Python manda a Max. Sono divisi in 5 famiglie principali:

```text
/aquarium/descriptors
/aquarium/descriptor/...
/aquarium/controls
/aquarium/direct
/aquarium/performance
```

## 1. `/aquarium/descriptors`

Questo messaggio manda tutti i descriptor dei boids in una sola lista:

```text
/aquarium/descriptors
0.625
0.383691
0.383691
0.354571
0.072601
0.195034
0.915361
0.084639
0.343651
0.333333
```

L’ordine è:

```text
fish_count
mean_speed
energy
center_x
center_y
spread
density
nearest_distance
direction_coherence
cluster_count
```

Quindi nell'esempio:

| Valore | Nome | Significato |
|---:|---|---|
| `0.625` | `fish_count` | quantità normalizzata di pesci |
| `0.383691` | `mean_speed` | velocità media del branco |
| `0.383691` | `energy` | energia del movimento, attualmente uguale a `mean_speed` |
| `0.354571` | `center_x` | posizione orizzontale media del branco |
| `0.072601` | `center_y` | posizione verticale media del branco |
| `0.195034` | `spread` | quanto il branco è disperso |
| `0.915361` | `density` | quanto il branco è compatto |
| `0.084639` | `nearest_distance` | distanza media dal vicino più vicino |
| `0.343651` | `direction_coherence` | quanto i pesci vanno nella stessa direzione |
| `0.333333` | `cluster_count` | quante zone/gruppi sono occupati |

Tutti sono normalizzati tra `0` e `1`.

---

## 2. Descriptor singoli

Questi sono gli stessi dati, ma mandati uno per uno:

```text
/aquarium/descriptor/fish_count 0.625
/aquarium/descriptor/mean_speed 0.383691
/aquarium/descriptor/energy 0.383691
...
```

Servono se in Max vuoi prendere direttamente un solo parametro senza fare `unpack` della lista completa.

Esempio:

```text
/aquarium/descriptor/density 0.915361
```

vuol dire:

```text
il branco è molto compatto
```

---

## 3. Interpretazione dei valori di esempio

### `fish_count = 0.625`

Il codice normalizza così:

```text
fish_count = numero_pesci / 160
```

Con 100 pesci:

```text
100 / 160 = 0.625
```

Quindi è corretto.

### `mean_speed = 0.383691`

I pesci stanno andando a circa il 38% della loro velocità massima.

Musicalmente può controllare:

```text
rate eventi
cutoff filtro
brightness
tremolo
energia ritmica
```

### `energy = 0.383691`

Per ora è uguale a `mean_speed`.

Quindi:

```text
energy alta = movimento più intenso
energy bassa = movimento più calmo
```

### `center_x = 0.354571`

Il centro del branco è al 35% della larghezza dello schermo.

Interpretazione:

```text
0.0 = tutto a sinistra
0.5 = centro
1.0 = tutto a destra
```

Buono per:

```text
pan stereo
posizione spaziale
bilanciamento L/R
```

### `center_y = 0.072601`

Il centro del branco è molto in alto nello schermo.

Interpretazione:

```text
0.0 = alto
0.5 = centro verticale
1.0 = basso
```

Può controllare:

```text
filtro
brightness
registro
riverbero
```

### `spread = 0.195034`

Il branco è poco disperso.

```text
0 = compatto
1 = molto sparso
```

Buono per:

```text
stereo width
riverbero
range melodico
detune
granular window
```

### `density = 0.915361`

Il branco è molto compatto.

```text
0 = rarefatto
1 = compatto
```

Questo è coerente con `spread = 0.195`: poco spread, alta density.

### `nearest_distance = 0.084639`

I pesci sono mediamente vicini tra loro.

Importante: questo è quasi l’opposto di `density`.

Infatti:

```text
density = 1 - nearest_distance
0.915361 ≈ 1 - 0.084639
```

Quindi sono due modi diversi di leggere la stessa cosa.

### `direction_coherence = 0.343651`

Il branco non è super allineato.

```text
0 = direzioni molto diverse / caos
1 = tutti vanno nella stessa direzione
```

Il valore `0.34` indica movimento abbastanza frammentato.

### `cluster_count = 0.333333`

Il branco occupa circa un terzo delle zone spaziali previste dal codice.

Non è un vero algoritmo di clustering: è una stima leggera basata su celle dello schermo.

---

## 4. `/aquarium/controls`

Esempio:

```text
/aquarium/controls
0.25 1. 0.9 1.35 0.18 1. 1. 0. 0. 0.
```

Ordine:

```text
density_fader
alignment_weight
cohesion_weight
separation_weight
noise_weight
food_strength
predator_strength
food_amount
predator_amount
section_id
```

Quindi:

| Valore | Nome | Significato |
|---:|---|---|
| `0.25` | `density_fader` | densità musicale legacy |
| `1.0` | `alignment_weight` | forza di allineamento |
| `0.9` | `cohesion_weight` | forza di coesione |
| `1.35` | `separation_weight` | forza di separazione |
| `0.18` | `noise_weight` | turbolenza movimento |
| `1.0` | `food_strength` | forza attrattore mouse |
| `1.0` | `predator_strength` | forza repulsore mouse |
| `0.0` | `food_amount` | attrattore virtuale MIDIMIX |
| `0.0` | `predator_amount` | repulsore virtuale MIDIMIX |
| `0.0` | `section_id` | sezione corrente |

---

## 5. `/aquarium/section`

Esempio:

```text
/aquarium/section 0 intro
```

Significa:

```text
section_id = 0
section_name = intro
```

Le sezioni sono:

```text
0 intro
1 growth
2 dense
3 chaos
4 release
5 outro
```

---

## 6. `/aquarium/direct`

Esempio:

```text
/aquarium/direct
0.383691 0.383691 0.354571 0.072601 0.915361 0.195034 0.25
```

È una versione compatta pensata apposta per Max.

Ordine:

```text
mean_speed
energy
center_x
center_y
density
spread
density_fader
```

Quindi:

| Valore | Nome |
|---:|---|
| `0.383691` | `mean_speed` |
| `0.383691` | `energy` |
| `0.354571` | `center_x` |
| `0.072601` | `center_y` |
| `0.915361` | `density` |
| `0.195034` | `spread` |
| `0.25` | `density_fader` |

È il messaggio più comodo da usare in Max per mapping sonori continui.

---

## 7. `/aquarium/performance`

Esempio:

```text
/aquarium/performance 0.5 0.25 0. 0.
```

Ordine:

```text
alignment_chaos
grain_density
noise_distortion
scene_id
```

Quindi:

| Valore | Nome | Significato |
|---:|---|---|
| `0.5` | `alignment_chaos` | metà ordine / metà caos |
| `0.25` | `grain_density` | densità eventi/grani bassa-media |
| `0.0` | `noise_distortion` | niente distorsione/noise extra |
| `0.0` | `scene_id` | scena 0 / intro |

Questi sono i controlli più importanti nel workflow demo/Markov v2.

---

## Riassunto dei dati di esempio

In quel momento il sistema diceva:

```text
100 pesci attivi
branco abbastanza lento/medio
branco molto compatto
branco posizionato a sinistra e molto in alto
movimento non molto coerente direzionalmente
sezione intro
caos medio
densità grani bassa-media
distorsione assente
```

Musicalmente, Max potrebbe interpretarlo così:

```text
density alta        → suono compatto / armonico / meno riverbero
spread basso        → stereo stretto
mean_speed media    → movimento sonoro moderato
center_x a sinistra → pan verso sinistra
center_y alto       → filtro più brillante o registro alto
coherence bassa     → più frammentazione/glitch
noise_distortion 0  → suono pulito
```
