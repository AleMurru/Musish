# Patch Max mappata — come vengono creati i suoni

Patch consigliata:

```text
Codex/max/aquarium_netreceive_mapped.maxpat
```

Questa patch è una copia/reimplementazione della patch `netreceive`, ma con routing più esplicito e senza `unpack`, perché nella nostra configurazione i messaggi arrivano già come liste leggibili da Max.

## Flusso dati

Python invia messaggi testuali compatibili con Max sulla porta `7401`:

```text
netreceive -u 7401
|
route direct midi note rest descriptors controls section event
```

I due messaggi usati per il suono sono:

```text
direct mean_speed energy center_x center_y density spread density_fader
midi event_id midi_note velocity duration_ms layer_id section_id
```

## Perché non usiamo `unpack`

Nel tuo caso `unpack` stava bloccando la patch. La nuova patch usa invece message box con `$1`, `$2`, `$3`, ecc.

Esempio:

```text
direct 0.42 0.60 0.50 0.48 0.70 0.30 0.25
```

Dopo `route direct`, la lista diventa:

```text
0.42 0.60 0.50 0.48 0.70 0.30 0.25
```

Quindi:

```text
$1 = mean_speed
$2 = energy
$3 = center_x
$4 = center_y
$5 = density
$6 = spread
$7 = density_fader
```

## Suono 1 — Drone continuo

Il drone è generato da:

```text
mean_speed -> expr 70 + mean_speed * 760 -> line~ -> cycle~
energy     -> expr 0.02 + energy * 0.22 -> line~ -> *~
```

Quindi:

- pesci più veloci = frequenza più alta;
- pesci più lenti = frequenza più bassa;
- energia più alta = volume più alto;
- energia più bassa = volume più basso.

Nel `main.py`, puoi influenzarlo così:

- `N` aumenta noise: movimento più nervoso, frequenza/energia tendono ad aumentare;
- mouse destro, predatore: fuga, energia più alta;
- mouse sinistro, attrattore: aggregazione, cambiamento del centro e della densità;
- `A/Z`, `S/X`, `D/C`: modificano alignment/cohesion/separation e quindi il comportamento collettivo.

## Suono 2 — Secondo oscillatore da densità

La densità del branco controlla un secondo oscillatore:

```text
density -> expr 110 + density * 330 -> line~ -> cycle~ -> *~ 0.06
```

Quindi:

- branco compatto = secondo tono più alto;
- branco disperso = secondo tono più basso.

Per giocarci:

- aumenta `S` / cohesion: i boids tendono a stare più vicini;
- usa mouse sinistro come cibo/attrattore;
- aumenta `D` / separation per far respirare il branco e cambiare densità.

## Suono 3 — Blip generati dalle Markov Chain

Le Markov Chain in Python generano eventi musicali. Python li converte anche in messaggi `midi`:

```text
midi event_id midi_note velocity duration_ms layer_id section_id
```

Nella patch:

```text
$2 = midi_note -> mtof -> cycle~
$3 = velocity  -> ampiezza del blip
```

Quindi:

- la Markov pitch/rhythm decide quando arrivano i blip e che nota MIDI hanno;
- la `velocity` controlla quanto sono forti;
- ogni evento fa un piccolo inviluppo: attacco rapido e decay breve.

Nel `main.py`, puoi influenzare la quantità di eventi con:

- `UP/DOWN` = `density_fader`; più alto = più eventi;
- movimento veloce dei boids = eventi più frequenti e Markov più variabile;
- tasti `1-6` = sezione performativa, cambia la scelta dei layer e il carattere generale.

## Mapping attuale sintetico

| Dato Python | Campo | Suono in Max |
|---|---:|---|
| `mean_speed` | `direct $1` | frequenza drone |
| `energy` | `direct $2` | volume drone |
| `density` | `direct $5` | secondo oscillatore |
| `midi_note` | `midi $2` | pitch dei blip Markov |
| `velocity` | `midi $3` | volume dei blip Markov |

## Come espandere la patch

Prossimi mapping consigliati:

```text
center_x       -> panning stereo
center_y       -> filtro / brightness
spread         -> riverbero o range melodico
density_fader  -> mix tra drone e blip
layer_id       -> strumenti diversi: drone, bass, lead, perc, granular, noise
section_id     -> preset timbrici diversi
```

## Nota su ogni pesce

Non conviene mandare ogni pesce come suono separato. Meglio:

```text
stato globale -> drone/modulazioni
cluster -> layer musicali
pochi pesci attivi -> eventi speciali
Markov -> note/eventi simbolici
```

Questo mantiene Max leggibile e musicalmente controllabile.
