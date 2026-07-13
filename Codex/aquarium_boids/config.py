OSC_HOST = "127.0.0.1"
OSC_PORT = 7400
PLAIN_UDP_PORT = 7401  # Max fallback via [netreceive -u 7401], no oscparse needed
CONTROL_PORT = 7500  # Max/MIDIMAX -> Python controls via [udpsend 127.0.0.1 7500]

# Direct MIDI controller input. Main live workflow: MIDIMIX -> Python -> Max.
ENABLE_MIDI_INPUT = True
MIDI_INPUT_NAME = "MIDIMIX"  # substring match; fallback to first available MIDI input
MIDI_DEBUG = True  # prints incoming CCs, useful for learning the real fader numbers

# Configurable CC mapping: cc_number -> (RuntimeControls field, min_value, max_value, quantize_to_int)
# NOTE: AKAI MIDIMIX CC numbers can vary by preset. If the mapping does not react,
# move faders and read printed CC numbers in the terminal, then edit this table.
# AKAI MIDIMIX: the 8 physical faders emit CC 19, 23, 27, 31, 49, 53, 57, 61 (fader 1..8).
# Live mapping (Rafael's setup): one physical fader per control.
# alignment_weight is intentionally left unmapped -> stays at its default (1.0).
MIDI_CC_MAPPING = {
    # Ecosystem controls (move the boids; the sound follows the descriptors):
    19: ("population", 1.0, 100.0, True),        # fader 1 -> number of fish -> granular density
    23: ("cohesion_weight", 0.0, 3.0, False),    # fader 2 -> flock compactness
    27: ("separation_weight", 0.0, 4.0, False),  # fader 3 -> flock dispersion
    31: ("noise_weight", 0.0, 1.5, False),       # fader 4 -> agitation -> noise/distortion
    49: ("food_amount", 0.0, 3.0, False),        # fader 5 -> center attractor
    53: ("predator_amount", 0.0, 3.0, False),    # fader 6 -> center repeller -> chaos
    # Musical controls (do NOT move the boids):
    57: ("density_fader", 0.0, 1.0, False),      # fader 7 -> Markov event density
    61: ("section_id", 0.0, 5.0, True),          # fader 8 -> musical section
}

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
