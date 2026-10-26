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

# Controller profiles, chosen by the name of the MIDI input actually opened (substring,
# case-insensitive). Any other device, including the MIDIMIX, uses MIDI_CC_MAPPING above.
# A parameter starting with "/" is not a simulation control: it is sent to Max as an OSC
# message (address, scaled value) whenever the knob moves.
# AKAI MPK mini 3 (measured with the MIDI monitor, current program): knobs K1..K8 send
# CC 16..23 on channel 1; pads 1..8 send Program Change 16..23 on channel 10.
MIDI_CC_MAPPING_MPK = {
    16: ("noise_weight", 0.0, 1.5, False),       # K1 -> agitation (range as MIDIMIX fader 4)
    17: ("/mix/grain_ms", 10.0, 400.0, False),   # K2 -> Max granulator grain length (ms); alignment stays 1.0
    18: ("cohesion_weight", 0.0, 3.0, False),    # K3 -> cohesion (as MIDIMIX fader 2)
    19: ("population", 1.0, 100.0, True),        # K4 -> number of fish (as MIDIMIX fader 1)
    20: ("/mix/slice_gain", 0.0, 1.0, False),    # K5 -> Max slice player gain (predator: pad 2 / mouse)
    21: ("/mix/gran_gain", 0.0, 1.0, False),     # K6 -> Max granulator gain
    22: ("/mix/kick_gain", 0.0, 1.0, False),     # K7 -> Max kick gain
    23: ("/mix/master", 0.0, 1.0, False),        # K8 -> Max master
}
MIDI_PC_PADS_MPK = {16 + i: i + 1 for i in range(8)}  # Program Change 16..23 -> pad 1..8
MIDI_PROFILES = {
    "MPK": (MIDI_CC_MAPPING_MPK, MIDI_PC_PADS_MPK),
}
PAD_PREDATOR_BURST_S = 1.0  # pad 2: predator at the centre for this long

WIDTH = 1200
HEIGHT = 750
FPS = 60
BOID_COUNT = 100

SEND_DESCRIPTOR_HZ = 20
GRAN_MAX_VOICES = 32  # /gran/fish_x carries at most this many fish (Max uses its own N <= this)
BPM = 120
ROOT_MIDI = 57  # A minor by default
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]

BACKGROUND = (8, 16, 28)
TEXT = (220, 235, 245)
