"""Aquarium as Instrument - core della simulazione (Giorno 1).

Moduli:
  config       parametri + contratto OSC congelato
  boids        simulazione boids vettorizzata + World (controlli live)
  descriptors  descrittori collettivi normalizzati 0..1 con smoothing EMA
  osc_out      emitter OSC (descrittori continui + eventi discreti + stato mondo)
"""
