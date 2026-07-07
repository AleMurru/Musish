# Patch Max OSC simbolica, senza MIDI

Patch:

```text
Codex/max/aquarium_osc_symbolic.maxpat
```

Questa patch usa la porta OSC standard:

```text
udpreceive 7400
```

e non usa:

```text
oscparse
/music/midi
noteout
makenote
```

Quindi non passa da MIDI. Usa direttamente gli indirizzi OSC simbolici prodotti da Python.

## Router principale

```text
udpreceive 7400
|
route /aquarium/direct /music/note /music/rest /aquarium/descriptors /aquarium/controls /aquarium/section /music/event
```

Gli indirizzi più importanti sono:

```text
/aquarium/direct
/music/note
/music/rest
```

## /aquarium/direct

Formato:

```text
/aquarium/direct mean_speed energy center_x center_y density spread density_fader
```

Dopo il route, Max riceve solo la lista:

```text
mean_speed energy center_x center_y density spread density_fader
```

Campi:

```text
$1 = mean_speed
$2 = energy
$3 = center_x
$4 = center_y
$5 = density
$6 = spread
$7 = density_fader
```

Mapping attuale:

```text
$1 mean_speed -> frequenza drone
$2 energy     -> ampiezza drone
$5 density    -> frequenza secondo oscillatore
```

## /music/note

Formato:

```text
/music/note event_id degree octave duration_beats velocity layer_id layer_name chord_degree section_id
```

Dopo il route, Max riceve:

```text
event_id degree octave duration_beats velocity layer_id layer_name chord_degree section_id
```

Campi usati:

```text
$2 = degree
$3 = octave
$5 = velocity
$8 = chord_degree
```

La patch converte questi dati simbolici in frequenza direttamente in Max, senza usare `/music/midi`.

## Conversione degree -> frequenza

La patch converte direttamente i gradi simbolici in frequenza, senza passare da `/music/midi`.

Formula usata nella patch, volutamente semplice e robusta:

```text
frequency = 110 * 2 ** ((degree + chord_degree + octave * 7) / 7)
```

Questa è una mappatura diatonica/equal-step: ogni 7 gradi si sale di un'ottava. Non è ancora una scala minore cromatica precisa, ma è sufficiente per avere una patch OSC totalmente simbolica e funzionante.

Se vogliamo una scala minore precisa in Max, il prossimo step sarà sostituire questo `expr` con una tabella/coll:

```text
0 -> 0 semitoni
1 -> 2 semitoni
2 -> 3 semitoni
3 -> 5 semitoni
4 -> 7 semitoni
5 -> 8 semitoni
6 -> 10 semitoni
```

Quindi l'evento rimane simbolico fino a Max.

## Nota importante

Questa patch funziona solo se il tuo `udpreceive 7400` emette messaggi leggibili tipo:

```text
/aquarium/direct 0.4 0.5 ...
/music/note 12 2 0 0.5 90 2 lead 5 1
```

Se invece in Max Console vedi `FullPacket`, la tua installazione non sta parsando OSC automaticamente. In quel caso devi continuare a usare la patch plain UDP:

```text
Codex/max/aquarium_netreceive_mapped.maxpat
```

che ascolta su `netreceive -u 7401`.
