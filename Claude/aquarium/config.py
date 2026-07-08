"""Configurazione centrale + contratto OSC congelato.

Tutti i valori di controllo dell'ecosistema sono 0..1.
I descrittori inviati via OSC sono sempre normalizzati 0..1.
"""

# --- Finestra / mondo ---------------------------------------------------------
WIDTH = 1280
HEIGHT = 720
BOUNDS = (WIDTH, HEIGHT)
FPS = 60

# --- Popolazione / fisica boids ----------------------------------------------
N_FISH = 120
MAX_SPEED = 3.6          # px/frame
MAX_FORCE = 0.18         # limite accelerazione
PERCEPTION = 60.0        # raggio di percezione vicini (px)
SEPARATION_R = 26.0      # raggio di separazione (px)

# Pesi base delle tre regole (i controlli live li modulano)
W_SEPARATION = 1.6
W_ALIGNMENT = 1.0
W_COHESION = 0.9
BORDER_MARGIN = 80.0
W_BORDER = 0.9

# --- Soglie eventi discreti (mapping diretto -> percepibilita') --------------
# Gli eventi devono essere RADI e salienti: pochi al secondo, ognuno riconoscibile
# a schermo. Il dart e' un OUTLIER statistico (un pesce che scatta fuori dal branco),
# non un valore assoluto: cosi' resta raro anche quando tutto il branco e' veloce.
DART_SIGMA = 2.4         # velocita' > media + DART_SIGMA*std del branco
DART_SPEED_FLOOR = 0.6   # ...e comunque sopra questa frazione di MAX_SPEED
DART_COOLDOWN = 0.5      # s min tra due dart dello stesso pesce
DART_GLOBAL_COOLDOWN = 0.10  # s min tra due dart qualsiasi (limita la raffica)

TURN_DOT = -0.5          # cos(angolo) sotto cui e' un'inversione netta ("turn")
TURN_SPEED_FLOOR = 0.35  # ignora i flip dei pesci lenti (jitter)
TURN_COOLDOWN = 0.6      # s min tra due turn dello stesso pesce
TURN_GLOBAL_COOLDOWN = 0.12

COLLISION_R = 12.0       # px: due pesci piu' vicini di cosi' = collisione
COLLISION_COOLDOWN = 0.18

# --- Smoothing descrittori ----------------------------------------------------
EMA_ALPHA = 0.18         # 0=fermo, 1=nessuno smoothing

# --- OSC ----------------------------------------------------------------------
OSC_IP = "127.0.0.1"
OSC_PORT = 9000
DESC_SEND_HZ = 30        # frequenza invio descrittori continui

# ---- CONTRATTO OSC (CONGELATO - non cambiare senza avvisare il musicista) ----
# Descrittori continui (float 0..1), inviati a DESC_SEND_HZ
OSC_DESC = {
    "fish_count":  "/aq/desc/fish_count",
    "mean_speed":  "/aq/desc/mean_speed",
    "energy":      "/aq/desc/energy",
    "center_x":    "/aq/desc/center_x",
    "center_y":    "/aq/desc/center_y",
    "spread":      "/aq/desc/spread",
    "density":     "/aq/desc/density",
    "nearest":     "/aq/desc/nearest_dist",
    "coherence":   "/aq/desc/coherence",
    "turbulence":  "/aq/desc/turbulence",
}
# Eventi discreti (immediati)
OSC_EV_DART = "/aq/event/dart"        # args: int id, float speed(0..1), float y(0..1)
OSC_EV_TURN = "/aq/event/turn"        # args: int id, float x(0..1), float y(0..1)
OSC_EV_COLL = "/aq/event/collision"   # args: float x(0..1), float y(0..1), float strength(0..1)
# Stato mondo (echo dei controlli, inviato quando cambia)
OSC_WORLD = {
    "food":       "/aq/world/food",
    "predator":   "/aq/world/predator",
    "turbulence": "/aq/world/turbulence",
    "density":    "/aq/world/density",
}
# Eventi musicali simbolici (Markov gerarchica) - gradi di scala, NON note assolute
# Il musicista sceglie scala/tonalita' in Max.
OSC_MUSIC_NOTE = "/aq/music/note"   # args: int id, int degree(0..6), int octave, float dur_beats, int velocity(0..127), int chord_root(0..6)
OSC_MUSIC_REST = "/aq/music/rest"   # args: int id, float dur_beats
OSC_MUSIC_CHORD = "/aq/music/chord"  # args: int chord_root(0..6)  (inviato quando cambia)

# --- Generatore musicale ------------------------------------------------------
BPM = 110
DURATIONS = {                     # nome -> durata in beat
    "sixteenth": 0.25,
    "eighth":    0.5,
    "quarter":   1.0,
    "half":      2.0,
    "rest":      1.0,
}
CHORD_EVERY_EVENTS = 8            # ogni quanti eventi valutare il cambio d'accordo
