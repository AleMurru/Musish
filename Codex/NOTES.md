# Note operative Codex

Da questa sessione in poi, tutto il codice/prototipo prodotto dall'assistente viene tenuto dentro `Codex/` per evitare confusione con i documenti e altri esperimenti presenti nella root.

## Stato attuale

Sì: esiste già una simulazione boids funzionante in:

```text
Codex/main.py
Codex/aquarium_boids/boids.py
```

La simulazione usa:

- alignment;
- cohesion;
- separation;
- noise controllabile;
- food/attractor con mouse sinistro;
- predator/repeller con mouse destro;
- descriptor normalizzati;
- OSC verso Max;
- Markov simbolica per eventi musicali.

## Avvio rapido

```bash
cd Codex
pip install -r requirements.txt
python main.py
```

Aprire in Max:

```text
Codex/max/aquarium_receiver.maxpat
```
