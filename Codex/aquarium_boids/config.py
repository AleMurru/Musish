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
MIDI_CC_MAPPING = {
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
    # Population: number of active fish 1..100 (MIDIMIX fader 3 = CC 27). Drives fish_count
    # -> granular density/probability[0..100]. Move it to another fader by changing the CC.
    27: ("population", 1.0, 100.0, True),
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
