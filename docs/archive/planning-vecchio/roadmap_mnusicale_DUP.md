# Roadmap — Acquario generativo musicale con Markov Chain

> Nota: questo file mantiene il nome richiesto `roadmap_acquario_generativo_mnusicale.md`. La versione con nome corretto è anche disponibile come `roadmap_acquario_generativo_musicale.md`.

Il contenuto principale della roadmap aggiornata si trova in:

```text
roadmap_acquario_generativo_musicale.md
```

Per evitare divergenze tra due file quasi identici, usare quello come documento principale.

## Sintesi delle nuove idee integrate

- La musica non viene generata direttamente dai singoli pesci.
- I pesci producono descriptor: velocità, energia, densità, dispersione, cluster, direzione.
- I descriptor condizionano Markov chain simboliche per pitch, ritmo, dinamica, layer e forma.
- Un fader centrale `density_fader` controlla il passaggio tra:
  - comportamento collettivo del branco;
  - cluster di pesci;
  - eventi più puntiformi legati a individui selezionati.
- La forma musicale viene controllata con hyperparameter come:
  - `section_duration`;
  - `novelty_pressure`;
  - `temperature`;
  - `repetition_memory`;
  - `max_repetition`.
- Il rendering sonoro finale resta nelle mani del musicista.
