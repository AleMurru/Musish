OSC_HOST = "127.0.0.1"
OSC_PORT = 7400
PLAIN_UDP_PORT = 7401  # Max fallback via [netreceive -u 7401], no oscparse needed
CONTROL_PORT = 7500  # Max/MIDIMAX -> Python controls via [udpsend 127.0.0.1 7500]

# Direct MIDI controller input. Main live workflow: MIDIMIX -> Python -> Max.
ENABLE_MIDI_INPUT = True
MIDI_INPUT_NAME = "MIDIMIX"  # substring match; fallback to first available MIDI input
MIDI_DEBUG = True  # prints incoming CCs, useful for learning the real fader numbers

# Demo v0 mode: boids as control source for Max sample/granular performance.
DEMO_MODE = True

# Markov v1 is the older free-running generator. Keep it off for the new demo workflow.
ENABLE_MARKOV = False

# Markov v2 is quantized to a 16th-note clock and emits symbolic messages for Max.
ENABLE_MARKOV_V2 = True
MARKOV_V2_DEBUG = True

# Configurable CC mapping: cc_number -> (RuntimeControls field, min_value, max_value, quantize_to_int)
# NOTE: AKAI MIDIMIX CC numbers can vary by preset. If the mapping does not react,
# move faders and read printed CC numbers in the terminal, then edit these tables.
MIDI_CC_MAPPING_CLASSIC = {
    # Primary ecosystem controls: these change boids first, then sound follows descriptors.
    19: ("alignment_weight", 0.0, 3.0, False),
    20: ("cohesion_weight", 0.0, 3.0, False),
    21: ("separation_weight", 0.0, 4.0, False),
    22: ("noise_weight", 0.0, 1.5, False),
    23: ("food_amount", 0.0, 3.0, False),
    24: ("predator_amount", 0.0, 3.0, False),
    # Secondary musical controls.
    25: ("density_fader", 0.0, 1.0, False),
    26: ("section_id", 0.0, 5.0, True),
}

MIDI_CC_MAPPING_DEMO = {
    # Demo macro: 0 = branco ordinato/stessa direzione, 1 = dispersione caotica.
    19: ("alignment_chaos", 0.0, 1.0, False),
    # Performance controls for Max sample/granular patch.
    20: ("grain_density", 0.0, 1.0, False),
    21: ("noise_distortion", 0.0, 1.0, False),
    # Ecosystem controls kept for visible/sonic shaping.
    22: ("cohesion_weight", 0.0, 3.0, False),
    23: ("separation_weight", 0.0, 4.0, False),
    24: ("food_amount", 0.0, 3.0, False),
    25: ("predator_amount", 0.0, 3.0, False),
    26: ("scene_id", 0.0, 5.0, True),
}

MIDI_CC_MAPPING = MIDI_CC_MAPPING_DEMO if DEMO_MODE else MIDI_CC_MAPPING_CLASSIC

WIDTH = 1200
HEIGHT = 750
FPS = 60
BOID_COUNT = 100

SEND_DESCRIPTOR_HZ = 20
BPM = 120
ROOT_MIDI = 57  # A minor by default
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]

BACKGROUND = (8, 16, 28)
TEXT = (220, 235, 245)
