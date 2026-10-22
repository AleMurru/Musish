{
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 1,
            "revision": 4,
            "architecture": "x64",
            "modernui": 1
        },
        "classnamespace": "box",
        "rect": [
            80.0,
            80.0,
            1500.0,
            900.0
        ],
        "openinpresentation": 1,
        "default_fontsize": 12.0,
        "gridsize": [
            15.0,
            15.0
        ],
        "boxes": [
            {
                "box": {
                    "id": "obj-1",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        20.0,
                        10.0,
                        700.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        8.0,
                        420.0,
                        20.0
                    ],
                    "text": "SHOAL GRAN - one grain voice per fish (16 voices, MC). Own patch, no PLAUD code.",
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-2",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        20.0,
                        35.0,
                        640.0,
                        63.0
                    ],
                    "text": "1. INPUTS from Python via the PLAUD device: udpreceive 7400 -> route /gran/fish_x /gran/density /gran/noise -> s granFishX / granDensity / granNoise. granFishX = x (0..1) of up to 32 fish, voice i = fish i; the first 16 are used and the list length is the fish count. Test mode closes these gates and uses the generator in section 6 instead.",
                    "linecount": 4
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        700.0,
                        33.0,
                        1250.0,
                        63.0
                    ],
                    "text": "2. VOICES (MC, 16 channels, one per fish). A phasor~ is each voice's ONSET clock: rate = (0.5 + density x 0.075) grains/s x (1 + J x r), r = rand~ (~3 Hz, different per voice) + 0.3 x a fixed per-voice offset, J = 0.35 + 0.4 x noise, so onsets drift instead of buzzing. The rate is capped at 1000/grain length so a grain ends before the next onset. Each grain reads exactly grain-length ms at 1x speed (grain phase = phasor x period / length, clipped to 1) under a Hann window, then the voice is silent until its next onset; voices overlap. Position: random in region start .. start + (0.25 + 0.75 x noise) x region width (left channel). Voices >= fish count fade out (~50 ms).",
                    "linecount": 4
                }
            },
            {
                "box": {
                    "id": "obj-4",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        700.0,
                        760.0,
                        760.0,
                        34.0
                    ],
                    "text": "3. PAN. Each voice is panned by its fish's x, equal power: left = cos(x pi/2), right = sin(x pi/2), smoothed ~60 ms; all voices are then summed per side (mc.mixdown~ 1).",
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        700.0,
                        1000.0,
                        760.0,
                        34.0
                    ],
                    "text": "4. OUTPUT. master = on/off x master gain x 1/sqrt(active voices), 50 ms ramp, own dac~ 1 2. Turn DSP on in Max to hear it.",
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        20.0,
                        765.0,
                        660.0,
                        63.0
                    ],
                    "text": "5. SOURCE. shoal_gran.aiff (your own sound, not part of the project) loads by relative name with 'replace'; console: 'loaded' or an ERROR after 5 s. info~ then reads the duration (outlet 6, ms) into 'source file length (s)': used by the slice player (10/30/55/80 %) and as the region limit (start + width clamped to the file; effective values printed as shoal_gran_region).",
                    "linecount": 4
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        20.0,
                        990.0,
                        640.0,
                        34.0
                    ],
                    "text": "6. TEST MODE (no Python). 16 fake fish drift on slow sines (x = 0.5 + 0.4 sin(0.6 t + 0.7 i)); test density and test noise replace the Python values.",
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        20.0,
                        1240.0,
                        640.0,
                        34.0
                    ],
                    "text": "Built as JSON and untested in Max: on first run check mc.pack~ float inputs, mc.wave~ signal start/end, mc.sah~ triggering and mc.mixdown~ 1.",
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        100.0,
                        80.0,
                        22.0
                    ],
                    "text": "r granFishX"
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        250.0,
                        100.0,
                        85.0,
                        22.0
                    ],
                    "text": "r granDensity"
                }
            },
            {
                "box": {
                    "id": "obj-11",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        450.0,
                        100.0,
                        75.0,
                        22.0
                    ],
                    "text": "r granNoise"
                }
            },
            {
                "box": {
                    "id": "obj-12",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        135.0,
                        45.0,
                        22.0
                    ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "obj-13",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        250.0,
                        135.0,
                        45.0,
                        22.0
                    ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "obj-14",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        450.0,
                        135.0,
                        45.0,
                        22.0
                    ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "obj-15",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        170.0,
                        40.0,
                        22.0
                    ],
                    "text": "t l l"
                }
            },
            {
                "box": {
                    "id": "obj-16",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 16,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        205.0,
                        250.0,
                        22.0
                    ],
                    "text": "unpack f f f f f f f f f f f f f f f f"
                }
            },
            {
                "box": {
                    "id": "obj-17",
                    "maxclass": "newobj",
                    "numinlets": 16,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        20.0,
                        240.0,
                        250.0,
                        22.0
                    ],
                    "text": "mc.pack~ 16"
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        300.0,
                        170.0,
                        45.0,
                        22.0
                    ],
                    "text": "zl len"
                }
            },
            {
                "box": {
                    "id": "obj-19",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        300.0,
                        205.0,
                        60.0,
                        22.0
                    ],
                    "text": "clip 0 16"
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "float",
                        "float",
                        "float"
                    ],
                    "patching_rect": [
                        300.0,
                        240.0,
                        50.0,
                        22.0
                    ],
                    "text": "t f f f"
                }
            },
            {
                "box": {
                    "id": "obj-21",
                    "maxclass": "number",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        380.0,
                        240.0,
                        45.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        248.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-22",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        430.0,
                        240.0,
                        170.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        66.0,
                        249.0,
                        230.0,
                        20.0
                    ],
                    "text": "active voices (fish, max 16)"
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        250.0,
                        280.0,
                        110.0,
                        22.0
                    ],
                    "text": "expr 0.5+$f1*0.075"
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        370.0,
                        280.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        276.0,
                        50.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 100.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-25",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        425.0,
                        280.0,
                        120.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        66.0,
                        277.0,
                        230.0,
                        20.0
                    ],
                    "text": "density (1..100)"
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "float",
                        "float",
                        "float"
                    ],
                    "patching_rect": [
                        450.0,
                        320.0,
                        50.0,
                        22.0
                    ],
                    "text": "t f f f"
                }
            },
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ],
                    "patching_rect": [
                        450.0,
                        355.0,
                        40.0,
                        22.0
                    ],
                    "text": "* 0.4"
                }
            },
            {
                "box": {
                    "id": "obj-28",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        500.0,
                        355.0,
                        110.0,
                        22.0
                    ],
                    "text": "expr 0.25+0.75*$f1"
                }
            },
            {
                "box": {
                    "id": "obj-29",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        560.0,
                        320.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        304.0,
                        50.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-30",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        615.0,
                        320.0,
                        80.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        66.0,
                        305.0,
                        230.0,
                        20.0
                    ],
                    "text": "noise (0..1)"
                }
            },
            {
                "box": {
                    "id": "obj-31",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        700.0,
                        100.0,
                        260.0,
                        22.0
                    ],
                    "text": "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
                }
            },
            {
                "box": {
                    "id": "obj-32",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 16,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        700.0,
                        130.0,
                        250.0,
                        22.0
                    ],
                    "text": "unpack f f f f f f f f f f f f f f f f"
                }
            },
            {
                "box": {
                    "id": "obj-33",
                    "maxclass": "newobj",
                    "numinlets": 16,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        700.0,
                        160.0,
                        250.0,
                        22.0
                    ],
                    "text": "mc.pack~ 16"
                }
            },
            {
                "box": {
                    "id": "obj-34",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        980.0,
                        100.0,
                        470.0,
                        22.0
                    ],
                    "text": "0 0.6755 -0.9962 0.7936 -0.1742 -0.5367 0.9657 -0.8874 0.343 0.3816 -0.9057 0.9542 -0.5014 -0.2147 0.8181 -0.9917"
                }
            },
            {
                "box": {
                    "id": "obj-35",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 16,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        980.0,
                        130.0,
                        250.0,
                        22.0
                    ],
                    "text": "unpack f f f f f f f f f f f f f f f f"
                }
            },
            {
                "box": {
                    "id": "obj-36",
                    "maxclass": "newobj",
                    "numinlets": 16,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        160.0,
                        250.0,
                        22.0
                    ],
                    "text": "mc.pack~ 16"
                }
            },
            {
                "box": {
                    "id": "obj-37",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        195.0,
                        60.0,
                        22.0
                    ],
                    "text": "mc.*~ 0."
                }
            },
            {
                "box": {
                    "id": "obj-38",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        225.0,
                        60.0,
                        22.0
                    ],
                    "text": "mc.+~ 1."
                }
            },
            {
                "box": {
                    "id": "obj-39",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        255.0,
                        60.0,
                        22.0
                    ],
                    "text": "mc.*~ 2."
                }
            },
            {
                "box": {
                    "id": "obj-40",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        285.0,
                        70.0,
                        22.0
                    ],
                    "text": "mc.phasor~"
                }
            },
            {
                "box": {
                    "id": "obj-41",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1100.0,
                        315.0,
                        75.0,
                        22.0
                    ],
                    "text": "mc.!-~ 1."
                }
            },
            {
                "box": {
                    "id": "obj-42",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1200.0,
                        255.0,
                        65.0,
                        22.0
                    ],
                    "text": "mc.noise~"
                }
            },
            {
                "box": {
                    "id": "obj-43",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1200.0,
                        285.0,
                        65.0,
                        22.0
                    ],
                    "text": "mc.*~ 0.5"
                }
            },
            {
                "box": {
                    "id": "obj-44",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1200.0,
                        315.0,
                        65.0,
                        22.0
                    ],
                    "text": "mc.+~ 0.5"
                }
            },
            {
                "box": {
                    "id": "obj-45",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1200.0,
                        345.0,
                        75.0,
                        22.0
                    ],
                    "text": "mc.sah~ 0.5"
                }
            },
            {
                "box": {
                    "id": "obj-46",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1200.0,
                        375.0,
                        65.0,
                        22.0
                    ],
                    "text": "mc.*~ 0.1"
                }
            },
            {
                "box": {
                    "id": "obj-47",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1200.0,
                        405.0,
                        90.0,
                        22.0
                    ],
                    "text": "mc.*~ 180520."
                }
            },
            {
                "box": {
                    "id": "obj-48",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1300.0,
                        435.0,
                        65.0,
                        22.0
                    ],
                    "text": "mc.+~ 80."
                }
            },
            {
                "box": {
                    "id": "obj-49",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        470.0,
                        130.0,
                        22.0
                    ],
                    "text": "mc.wave~ shoal_gran"
                }
            },
            {
                "box": {
                    "id": "obj-50",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1130.0,
                        470.0,
                        80.0,
                        22.0
                    ],
                    "text": "mc.cycle~ 0."
                }
            },
            {
                "box": {
                    "id": "obj-51",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1130.0,
                        500.0,
                        70.0,
                        22.0
                    ],
                    "text": "mc.*~ -0.5"
                }
            },
            {
                "box": {
                    "id": "obj-52",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1130.0,
                        530.0,
                        70.0,
                        22.0
                    ],
                    "text": "mc.+~ 0.5"
                }
            },
            {
                "box": {
                    "id": "obj-53",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        560.0,
                        45.0,
                        22.0
                    ],
                    "text": "mc.*~"
                }
            },
            {
                "box": {
                    "id": "obj-54",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        700.0,
                        470.0,
                        60.0,
                        22.0
                    ],
                    "text": "mc.<~ 0."
                }
            },
            {
                "box": {
                    "id": "obj-55",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        700.0,
                        500.0,
                        125.0,
                        22.0
                    ],
                    "text": "mc.slide~ 2400 2400"
                }
            },
            {
                "box": {
                    "id": "obj-56",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        595.0,
                        45.0,
                        22.0
                    ],
                    "text": "mc.*~"
                }
            },
            {
                "box": {
                    "id": "obj-57",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        700.0,
                        280.0,
                        125.0,
                        22.0
                    ],
                    "text": "mc.slide~ 2880 2880"
                }
            },
            {
                "box": {
                    "id": "obj-58",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        700.0,
                        315.0,
                        70.0,
                        22.0
                    ],
                    "text": "mc.*~ 0.25"
                }
            },
            {
                "box": {
                    "id": "obj-59",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        700.0,
                        345.0,
                        80.0,
                        22.0
                    ],
                    "text": "mc.cycle~ 0."
                }
            },
            {
                "box": {
                    "id": "obj-60",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        800.0,
                        315.0,
                        75.0,
                        22.0
                    ],
                    "text": "mc.!-~ 1."
                }
            },
            {
                "box": {
                    "id": "obj-61",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        800.0,
                        345.0,
                        70.0,
                        22.0
                    ],
                    "text": "mc.*~ 0.25"
                }
            },
            {
                "box": {
                    "id": "obj-62",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        800.0,
                        375.0,
                        80.0,
                        22.0
                    ],
                    "text": "mc.cycle~ 0."
                }
            },
            {
                "box": {
                    "id": "obj-63",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        630.0,
                        45.0,
                        22.0
                    ],
                    "text": "mc.*~"
                }
            },
            {
                "box": {
                    "id": "obj-64",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1050.0,
                        630.0,
                        45.0,
                        22.0
                    ],
                    "text": "mc.*~"
                }
            },
            {
                "box": {
                    "id": "obj-65",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        980.0,
                        665.0,
                        95.0,
                        22.0
                    ],
                    "text": "mc.mixdown~ 1"
                }
            },
            {
                "box": {
                    "id": "obj-66",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1100.0,
                        665.0,
                        95.0,
                        22.0
                    ],
                    "text": "mc.mixdown~ 1"
                }
            },
            {
                "box": {
                    "id": "obj-67",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        980.0,
                        830.0,
                        40.0,
                        22.0
                    ],
                    "text": "*~ 0."
                }
            },
            {
                "box": {
                    "id": "obj-68",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        1100.0,
                        830.0,
                        40.0,
                        22.0
                    ],
                    "text": "*~ 0."
                }
            },
            {
                "box": {
                    "id": "obj-69",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [
                        980.0,
                        870.0,
                        55.0,
                        22.0
                    ],
                    "text": "dac~ 1 2"
                }
            },
            {
                "box": {
                    "id": "obj-70",
                    "maxclass": "toggle",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "int"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        700.0,
                        830.0,
                        24.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        40.0,
                        20.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-71",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        730.0,
                        832.0,
                        60.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        36.0,
                        40.0,
                        200.0,
                        20.0
                    ],
                    "text": "on / off"
                }
            },
            {
                "box": {
                    "id": "obj-72",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        800.0,
                        830.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        92.0,
                        50.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-73",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        855.0,
                        830.0,
                        110.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        66.0,
                        93.0,
                        230.0,
                        20.0
                    ],
                    "text": "master gain (0..1)"
                }
            },
            {
                "box": {
                    "id": "obj-74",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        380.0,
                        680.0,
                        70.0,
                        22.0
                    ],
                    "text": "maximum 1."
                }
            },
            {
                "box": {
                    "id": "obj-75",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        380.0,
                        710.0,
                        40.0,
                        22.0
                    ],
                    "text": "sqrt"
                }
            },
            {
                "box": {
                    "id": "obj-76",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        380.0,
                        740.0,
                        40.0,
                        22.0
                    ],
                    "text": "!/ 1."
                }
            },
            {
                "box": {
                    "id": "obj-77",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        700.0,
                        870.0,
                        75.0,
                        22.0
                    ],
                    "text": "pak 0 0. 1."
                }
            },
            {
                "box": {
                    "id": "obj-78",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        700.0,
                        900.0,
                        105.0,
                        22.0
                    ],
                    "text": "expr $f1*$f2*$f3"
                }
            },
            {
                "box": {
                    "id": "obj-79",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        700.0,
                        930.0,
                        60.0,
                        22.0
                    ],
                    "text": "pack f 50"
                }
            },
            {
                "box": {
                    "id": "obj-80",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "signal",
                        "bang"
                    ],
                    "patching_rect": [
                        700.0,
                        960.0,
                        40.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-81",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        830.0,
                        900.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        120.0,
                        50.0,
                        22.0
                    ],
                    "minimum": 10.0,
                    "maximum": 500.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-82",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        885.0,
                        900.0,
                        150.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        66.0,
                        121.0,
                        230.0,
                        20.0
                    ],
                    "text": "grain length (ms, 10..500)"
                }
            },
            {
                "box": {
                    "id": "obj-83",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "float",
                        "float"
                    ],
                    "patching_rect": [
                        830.0,
                        930.0,
                        40.0,
                        22.0
                    ],
                    "text": "t f f"
                }
            },
            {
                "box": {
                    "id": "obj-84",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        1060.0,
                        900.0,
                        55.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        148.0,
                        55.0,
                        22.0
                    ],
                    "minimum": 1.0,
                    "maximum": 3600.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-85",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        1120.0,
                        900.0,
                        150.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        71.0,
                        149.0,
                        225.0,
                        20.0
                    ],
                    "text": "source file length (s) - read from the file"
                }
            },
            {
                "box": {
                    "id": "obj-86",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1060.0,
                        930.0,
                        85.0,
                        22.0
                    ],
                    "text": "pak 20. 80."
                }
            },
            {
                "box": {
                    "id": "obj-87",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1060.0,
                        960.0,
                        115.0,
                        22.0
                    ],
                    "text": "expr $f1*1000.-$f2"
                }
            },
            {
                "box": {
                    "id": "obj-88",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "patching_rect": [
                        20.0,
                        830.0,
                        60.0,
                        22.0
                    ],
                    "text": "loadbang"
                }
            },
            {
                "box": {
                    "id": "obj-89",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        "bang"
                    ],
                    "patching_rect": [
                        20.0,
                        860.0,
                        40.0,
                        22.0
                    ],
                    "text": "t b b"
                }
            },
            {
                "box": {
                    "id": "obj-90",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "patching_rect": [
                        100.0,
                        860.0,
                        70.0,
                        22.0
                    ],
                    "text": "delay 5000"
                }
            },
            {
                "box": {
                    "id": "obj-91",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        890.0,
                        135.0,
                        22.0
                    ],
                    "text": "replace shoal_gran.aiff"
                }
            },
            {
                "box": {
                    "id": "obj-92",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "float",
                        "bang"
                    ],
                    "patching_rect": [
                        20.0,
                        920.0,
                        115.0,
                        22.0
                    ],
                    "text": "buffer~ shoal_gran"
                }
            },
            {
                "box": {
                    "id": "obj-93",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        190.0,
                        860.0,
                        35.0,
                        22.0
                    ],
                    "text": "stop"
                }
            },
            {
                "box": {
                    "id": "obj-94",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        150.0,
                        920.0,
                        175.0,
                        22.0
                    ],
                    "text": "source shoal_gran.aiff loaded"
                }
            },
            {
                "box": {
                    "id": "obj-95",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        950.0,
                        520.0,
                        22.0
                    ],
                    "text": "ERROR source shoal_gran.aiff NOT FOUND - put your own sound next to shoal_gran.maxpat"
                }
            },
            {
                "box": {
                    "id": "obj-96",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        350.0,
                        920.0,
                        100.0,
                        22.0
                    ],
                    "text": "print shoal_gran"
                }
            },
            {
                "box": {
                    "id": "obj-97",
                    "maxclass": "toggle",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "int"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        20.0,
                        1040.0,
                        24.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        66.0,
                        20.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-98",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        50.0,
                        1042.0,
                        210.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        36.0,
                        66.0,
                        260.0,
                        20.0
                    ],
                    "text": "test mode (no Python: 16 fake fish)"
                }
            },
            {
                "box": {
                    "id": "obj-99",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "int",
                        "int",
                        "int"
                    ],
                    "patching_rect": [
                        20.0,
                        1075.0,
                        50.0,
                        22.0
                    ],
                    "text": "t i i i"
                }
            },
            {
                "box": {
                    "id": "obj-100",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "int"
                    ],
                    "patching_rect": [
                        20.0,
                        1105.0,
                        40.0,
                        22.0
                    ],
                    "text": "== 0"
                }
            },
            {
                "box": {
                    "id": "obj-101",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "patching_rect": [
                        90.0,
                        1105.0,
                        40.0,
                        22.0
                    ],
                    "text": "sel 1"
                }
            },
            {
                "box": {
                    "id": "obj-102",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "patching_rect": [
                        150.0,
                        1105.0,
                        60.0,
                        22.0
                    ],
                    "text": "metro 50"
                }
            },
            {
                "box": {
                    "id": "obj-103",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 4,
                    "outlettype": [
                        "int",
                        "",
                        "",
                        "int"
                    ],
                    "patching_rect": [
                        150.0,
                        1135.0,
                        55.0,
                        22.0
                    ],
                    "text": "counter"
                }
            },
            {
                "box": {
                    "id": "obj-104",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        "float"
                    ],
                    "patching_rect": [
                        150.0,
                        1165.0,
                        40.0,
                        22.0
                    ],
                    "text": "t b f"
                }
            },
            {
                "box": {
                    "id": "obj-105",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ],
                    "patching_rect": [
                        210.0,
                        1165.0,
                        45.0,
                        22.0
                    ],
                    "text": "* 0.05"
                }
            },
            {
                "box": {
                    "id": "obj-106",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 3,
                    "outlettype": [
                        "bang",
                        "bang",
                        "int"
                    ],
                    "patching_rect": [
                        150.0,
                        1195.0,
                        55.0,
                        22.0
                    ],
                    "text": "uzi 16 0"
                }
            },
            {
                "box": {
                    "id": "obj-107",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        270.0,
                        1195.0,
                        210.0,
                        22.0
                    ],
                    "text": "expr 0.5+0.4*sin($f2*0.6+$i1*0.7)"
                }
            },
            {
                "box": {
                    "id": "obj-108",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        500.0,
                        1195.0,
                        75.0,
                        22.0
                    ],
                    "text": "zl group 16"
                }
            },
            {
                "box": {
                    "id": "obj-109",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        300.0,
                        1040.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        184.0,
                        50.0,
                        22.0
                    ],
                    "minimum": 1.0,
                    "maximum": 100.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-110",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        355.0,
                        1040.0,
                        130.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        66.0,
                        185.0,
                        230.0,
                        20.0
                    ],
                    "text": "test density (1..100)"
                }
            },
            {
                "box": {
                    "id": "obj-111",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        500.0,
                        1040.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        212.0,
                        50.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-112",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        555.0,
                        1040.0,
                        110.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        66.0,
                        213.0,
                        230.0,
                        20.0
                    ],
                    "text": "test noise (0..1)"
                }
            },
            {
                "box": {
                    "id": "obj-113",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        300.0,
                        1075.0,
                        45.0,
                        22.0
                    ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "obj-114",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        500.0,
                        1075.0,
                        45.0,
                        22.0
                    ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "obj-115",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "patching_rect": [
                        1300.0,
                        830.0,
                        60.0,
                        22.0
                    ],
                    "text": "loadbang"
                }
            },
            {
                "box": {
                    "id": "obj-116",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 12,
                    "outlettype": [
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        "bang"
                    ],
                    "patching_rect": [
                        1300.0,
                        860.0,
                        200.0,
                        22.0
                    ],
                    "text": "t b b b b b b b b b b b b"
                }
            },
            {
                "box": {
                    "id": "obj-117",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1300.0,
                        895.0,
                        36.0,
                        22.0
                    ],
                    "text": "1"
                }
            },
            {
                "box": {
                    "id": "obj-118",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1340.0,
                        895.0,
                        36.0,
                        22.0
                    ],
                    "text": "0.6"
                }
            },
            {
                "box": {
                    "id": "obj-119",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1380.0,
                        895.0,
                        36.0,
                        22.0
                    ],
                    "text": "80"
                }
            },
            {
                "box": {
                    "id": "obj-120",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1420.0,
                        895.0,
                        36.0,
                        22.0
                    ],
                    "text": "142.592"
                }
            },
            {
                "box": {
                    "id": "obj-121",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1460.0,
                        895.0,
                        36.0,
                        22.0
                    ],
                    "text": "0"
                }
            },
            {
                "box": {
                    "id": "obj-122",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1300.0,
                        925.0,
                        36.0,
                        22.0
                    ],
                    "text": "60"
                }
            },
            {
                "box": {
                    "id": "obj-123",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1340.0,
                        925.0,
                        36.0,
                        22.0
                    ],
                    "text": "0.3"
                }
            },
            {
                "box": {
                    "id": "obj-124",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1380.0,
                        925.0,
                        36.0,
                        22.0
                    ],
                    "text": "0"
                }
            },
            {
                "box": {
                    "id": "obj-125",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1420.0,
                        925.0,
                        36.0,
                        22.0
                    ],
                    "text": "50"
                }
            },
            {
                "box": {
                    "id": "obj-126",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1460.0,
                        925.0,
                        36.0,
                        22.0
                    ],
                    "text": "0.2"
                }
            },
            {
                "box": {
                    "id": "obj-127",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        800.0,
                        800.0,
                        95.0,
                        22.0
                    ],
                    "text": "r mixGranGain"
                }
            },
            {
                "box": {
                    "id": "obj-128",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        900.0,
                        800.0,
                        150.0,
                        20.0
                    ],
                    "text": "MPK K6 -> master gain"
                }
            },
            {
                "box": {
                    "id": "obj-129",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        20.0,
                        1300.0,
                        900.0,
                        48.0
                    ],
                    "text": "7. SLICE PLAYER (MPK pads 5-8, independent of the grain voices). r padSample n (1..4) plays a 1.5 s stereo slice of buffer~ shoal_gran from 10 / 30 / 55 / 80 % of the source file length (play~ driven by a position ramp), with 20 ms fade in / out and its own slice gain, to dac~ 1 2. A new pad restarts the slice.",
                    "linecount": 3
                }
            },
            {
                "box": {
                    "id": "obj-130",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        1350.0,
                        80.0,
                        22.0
                    ],
                    "text": "r padSample"
                }
            },
            {
                "box": {
                    "id": "obj-131",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        1380.0,
                        55.0,
                        22.0
                    ],
                    "text": "clip 1 4"
                }
            },
            {
                "box": {
                    "id": "obj-132",
                    "maxclass": "newobj",
                    "numinlets": 5,
                    "numoutlets": 5,
                    "outlettype": [
                        "bang",
                        "bang",
                        "bang",
                        "bang",
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        1410.0,
                        80.0,
                        22.0
                    ],
                    "text": "sel 1 2 3 4"
                }
            },
            {
                "box": {
                    "id": "obj-133",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        1440.0,
                        38.0,
                        22.0
                    ],
                    "text": "0.1"
                }
            },
            {
                "box": {
                    "id": "obj-134",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        65.0,
                        1440.0,
                        38.0,
                        22.0
                    ],
                    "text": "0.3"
                }
            },
            {
                "box": {
                    "id": "obj-135",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        110.0,
                        1440.0,
                        38.0,
                        22.0
                    ],
                    "text": "0.55"
                }
            },
            {
                "box": {
                    "id": "obj-136",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        155.0,
                        1440.0,
                        38.0,
                        22.0
                    ],
                    "text": "0.8"
                }
            },
            {
                "box": {
                    "id": "obj-137",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        1475.0,
                        70.0,
                        22.0
                    ],
                    "text": "* 180600."
                }
            },
            {
                "box": {
                    "id": "obj-138",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        400.0,
                        1475.0,
                        55.0,
                        22.0
                    ],
                    "text": "* 1000."
                }
            },
            {
                "box": {
                    "id": "obj-139",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "bang",
                        "float",
                        "float"
                    ],
                    "patching_rect": [
                        20.0,
                        1505.0,
                        55.0,
                        22.0
                    ],
                    "text": "t b f f"
                }
            },
            {
                "box": {
                    "id": "obj-140",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ],
                    "patching_rect": [
                        150.0,
                        1535.0,
                        55.0,
                        22.0
                    ],
                    "text": "+ 1500."
                }
            },
            {
                "box": {
                    "id": "obj-141",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        1565.0,
                        55.0,
                        22.0
                    ],
                    "text": "pack f f"
                }
            },
            {
                "box": {
                    "id": "obj-142",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        20.0,
                        1595.0,
                        80.0,
                        22.0
                    ],
                    "text": "$1, $2 1500"
                }
            },
            {
                "box": {
                    "id": "obj-143",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "signal",
                        "bang"
                    ],
                    "patching_rect": [
                        20.0,
                        1625.0,
                        40.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-144",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "signal",
                        "signal",
                        "bang"
                    ],
                    "patching_rect": [
                        20.0,
                        1655.0,
                        115.0,
                        22.0
                    ],
                    "text": "play~ shoal_gran 2"
                }
            },
            {
                "box": {
                    "id": "obj-145",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        250.0,
                        1565.0,
                        140.0,
                        22.0
                    ],
                    "text": "0, 1 20 1 1460 0 20"
                }
            },
            {
                "box": {
                    "id": "obj-146",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "signal",
                        "bang"
                    ],
                    "patching_rect": [
                        250.0,
                        1595.0,
                        40.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-147",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        250.0,
                        1625.0,
                        50.0,
                        22.0
                    ],
                    "text": "*~ 0.7"
                }
            },
            {
                "box": {
                    "id": "obj-148",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        20.0,
                        1690.0,
                        35.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-149",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        80.0,
                        1690.0,
                        35.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-150",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        330.0,
                        1625.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        332.0,
                        50.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-151",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        385.0,
                        1625.0,
                        170.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        66.0,
                        333.0,
                        230.0,
                        20.0
                    ],
                    "text": "slice gain (MPK pads 5-8)"
                }
            },
            {
                "box": {
                    "id": "obj-152",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "patching_rect": [
                        450.0,
                        1565.0,
                        60.0,
                        22.0
                    ],
                    "text": "loadbang"
                }
            },
            {
                "box": {
                    "id": "obj-153",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        450.0,
                        1595.0,
                        30.0,
                        22.0
                    ],
                    "text": "0.7"
                }
            },
            {
                "box": {
                    "id": "obj-154",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        830.0,
                        870.0,
                        90.0,
                        22.0
                    ],
                    "text": "r mixGrainMs"
                }
            },
            {
                "box": {
                    "id": "obj-155",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        1060.0,
                        870.0,
                        140.0,
                        20.0
                    ],
                    "text": "MPK K2 -> grain length"
                }
            },
            {
                "box": {
                    "id": "obj-156",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        120.0,
                        1350.0,
                        80.0,
                        22.0
                    ],
                    "text": "prepend pad"
                }
            },
            {
                "box": {
                    "id": "obj-157",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        100.0,
                        1475.0,
                        105.0,
                        22.0
                    ],
                    "text": "prepend start_ms"
                }
            },
            {
                "box": {
                    "id": "obj-158",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        230.0,
                        1410.0,
                        140.0,
                        22.0
                    ],
                    "text": "print shoal_gran_slice"
                }
            },
            {
                "box": {
                    "id": "obj-159",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1400.0,
                        160.0,
                        75.0,
                        22.0
                    ],
                    "text": "mc.rand~ 3."
                }
            },
            {
                "box": {
                    "id": "obj-160",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1400.0,
                        195.0,
                        70.0,
                        22.0
                    ],
                    "text": "mc.*~ 0.3"
                }
            },
            {
                "box": {
                    "id": "obj-161",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1400.0,
                        225.0,
                        45.0,
                        22.0
                    ],
                    "text": "mc.+~"
                }
            },
            {
                "box": {
                    "id": "obj-162",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ],
                    "patching_rect": [
                        450.0,
                        385.0,
                        50.0,
                        22.0
                    ],
                    "text": "+ 0.35"
                }
            },
            {
                "box": {
                    "id": "obj-163",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1400.0,
                        255.0,
                        105.0,
                        22.0
                    ],
                    "text": "mc.minimum~ 12.5"
                }
            },
            {
                "box": {
                    "id": "obj-164",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1400.0,
                        285.0,
                        80.0,
                        22.0
                    ],
                    "text": "mc.!/~ 12.5"
                }
            },
            {
                "box": {
                    "id": "obj-165",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1400.0,
                        315.0,
                        45.0,
                        22.0
                    ],
                    "text": "mc.*~"
                }
            },
            {
                "box": {
                    "id": "obj-166",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1400.0,
                        345.0,
                        90.0,
                        22.0
                    ],
                    "text": "mc.clip~ 0. 1."
                }
            },
            {
                "box": {
                    "id": "obj-167",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "multichannelsignal"
                    ],
                    "patching_rect": [
                        1400.0,
                        405.0,
                        90.0,
                        22.0
                    ],
                    "text": "mc.+~ 20000."
                }
            },
            {
                "box": {
                    "id": "obj-168",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1180.0,
                        960.0,
                        70.0,
                        22.0
                    ],
                    "text": "maximum 0."
                }
            },
            {
                "box": {
                    "id": "obj-169",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        880.0,
                        930.0,
                        55.0,
                        22.0
                    ],
                    "text": "!/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-170",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        1520.0,
                        900.0,
                        55.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        360.0,
                        55.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 3600.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-171",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        1580.0,
                        900.0,
                        150.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        71.0,
                        361.0,
                        225.0,
                        20.0
                    ],
                    "text": "region start (s)"
                }
            },
            {
                "box": {
                    "id": "obj-172",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1520.0,
                        930.0,
                        55.0,
                        22.0
                    ],
                    "text": "* 1000."
                }
            },
            {
                "box": {
                    "id": "obj-173",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        1520.0,
                        960.0,
                        55.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        388.0,
                        55.0,
                        22.0
                    ],
                    "minimum": 0.5,
                    "maximum": 3600.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-174",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        1580.0,
                        960.0,
                        150.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        71.0,
                        389.0,
                        225.0,
                        20.0
                    ],
                    "text": "region width (s)"
                }
            },
            {
                "box": {
                    "id": "obj-175",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        980.0,
                        700.0,
                        100.0,
                        22.0
                    ],
                    "text": "lores~ 6000. 0."
                }
            },
            {
                "box": {
                    "id": "obj-176",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        1100.0,
                        700.0,
                        100.0,
                        22.0
                    ],
                    "text": "lores~ 6000. 0."
                }
            },
            {
                "box": {
                    "id": "obj-177",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        1220.0,
                        700.0,
                        60.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        416.0,
                        60.0,
                        22.0
                    ],
                    "minimum": 200.0,
                    "maximum": 18000.0,
                    "format": 6
                }
            },
            {
                "box": {
                    "id": "obj-178",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        1285.0,
                        700.0,
                        190.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        76.0,
                        417.0,
                        230.0,
                        20.0
                    ],
                    "text": "tone: low-pass on the grains (Hz)"
                }
            },
            {
                "box": {
                    "id": "obj-179",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "patching_rect": [
                        1520.0,
                        990.0,
                        60.0,
                        22.0
                    ],
                    "text": "loadbang"
                }
            },
            {
                "box": {
                    "id": "obj-180",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "bang",
                        "bang",
                        "bang"
                    ],
                    "patching_rect": [
                        1520.0,
                        1020.0,
                        55.0,
                        22.0
                    ],
                    "text": "t b b b"
                }
            },
            {
                "box": {
                    "id": "obj-181",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1520.0,
                        1050.0,
                        34.0,
                        22.0
                    ],
                    "text": "89"
                }
            },
            {
                "box": {
                    "id": "obj-182",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1560.0,
                        1050.0,
                        30.0,
                        22.0
                    ],
                    "text": "15"
                }
            },
            {
                "box": {
                    "id": "obj-183",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1600.0,
                        1050.0,
                        40.0,
                        22.0
                    ],
                    "text": "6000"
                }
            },
            {
                "box": {
                    "id": "obj-184",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        560.0,
                        1625.0,
                        100.0,
                        22.0
                    ],
                    "text": "r mixSliceGain"
                }
            },
            {
                "box": {
                    "id": "obj-185",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        665.0,
                        1625.0,
                        140.0,
                        20.0
                    ],
                    "text": "MPK K5 -> slice gain"
                }
            },
            {
                "box": {
                    "id": "obj-186",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 10,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        560.0,
                        890.0,
                        105.0,
                        22.0
                    ],
                    "text": "info~ shoal_gran"
                }
            },
            {
                "box": {
                    "id": "obj-187",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ],
                    "patching_rect": [
                        560.0,
                        920.0,
                        50.0,
                        22.0
                    ],
                    "text": "/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-188",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        560.0,
                        860.0,
                        125.0,
                        22.0
                    ],
                    "text": "prepend duration_ms"
                }
            },
            {
                "box": {
                    "id": "obj-189",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        560.0,
                        950.0,
                        105.0,
                        22.0
                    ],
                    "text": "prepend channels"
                }
            },
            {
                "box": {
                    "id": "obj-190",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1760.0,
                        960.0,
                        110.0,
                        22.0
                    ],
                    "text": "pak 35. 142.592"
                }
            },
            {
                "box": {
                    "id": "obj-191",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ],
                    "patching_rect": [
                        1760.0,
                        990.0,
                        75.0,
                        22.0
                    ],
                    "text": "minimum 0."
                }
            },
            {
                "box": {
                    "id": "obj-192",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "float",
                        "float"
                    ],
                    "patching_rect": [
                        1760.0,
                        1020.0,
                        40.0,
                        22.0
                    ],
                    "text": "t f f"
                }
            },
            {
                "box": {
                    "id": "obj-193",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1760.0,
                        1050.0,
                        110.0,
                        22.0
                    ],
                    "text": "pak 35. 142.592"
                }
            },
            {
                "box": {
                    "id": "obj-194",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1760.0,
                        1080.0,
                        90.0,
                        22.0
                    ],
                    "text": "expr $f2-$f1"
                }
            },
            {
                "box": {
                    "id": "obj-195",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1900.0,
                        900.0,
                        115.0,
                        22.0
                    ],
                    "text": "pak 105. 107.592"
                }
            },
            {
                "box": {
                    "id": "obj-196",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ],
                    "patching_rect": [
                        1900.0,
                        930.0,
                        75.0,
                        22.0
                    ],
                    "text": "minimum 0."
                }
            },
            {
                "box": {
                    "id": "obj-197",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1900.0,
                        960.0,
                        100.0,
                        22.0
                    ],
                    "text": "prepend start_s"
                }
            },
            {
                "box": {
                    "id": "obj-198",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        1760.0,
                        1110.0,
                        100.0,
                        22.0
                    ],
                    "text": "prepend width_s"
                }
            },
            {
                "box": {
                    "id": "obj-199",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        1900.0,
                        1110.0,
                        145.0,
                        22.0
                    ],
                    "text": "print shoal_gran_region"
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "destination": [
                        "obj-12",
                        1
                    ],
                    "source": [
                        "obj-9",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-13",
                        1
                    ],
                    "source": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-14",
                        1
                    ],
                    "source": [
                        "obj-11",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-15",
                        0
                    ],
                    "source": [
                        "obj-12",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-16",
                        0
                    ],
                    "source": [
                        "obj-15",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-18",
                        0
                    ],
                    "source": [
                        "obj-15",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        0
                    ],
                    "source": [
                        "obj-16",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        0
                    ],
                    "source": [
                        "obj-32",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        0
                    ],
                    "source": [
                        "obj-35",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        1
                    ],
                    "source": [
                        "obj-16",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        1
                    ],
                    "source": [
                        "obj-32",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        1
                    ],
                    "source": [
                        "obj-35",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        2
                    ],
                    "source": [
                        "obj-16",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        2
                    ],
                    "source": [
                        "obj-32",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        2
                    ],
                    "source": [
                        "obj-35",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        3
                    ],
                    "source": [
                        "obj-16",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        3
                    ],
                    "source": [
                        "obj-32",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        3
                    ],
                    "source": [
                        "obj-35",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        4
                    ],
                    "source": [
                        "obj-16",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        4
                    ],
                    "source": [
                        "obj-32",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        4
                    ],
                    "source": [
                        "obj-35",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        5
                    ],
                    "source": [
                        "obj-16",
                        5
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        5
                    ],
                    "source": [
                        "obj-32",
                        5
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        5
                    ],
                    "source": [
                        "obj-35",
                        5
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        6
                    ],
                    "source": [
                        "obj-16",
                        6
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        6
                    ],
                    "source": [
                        "obj-32",
                        6
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        6
                    ],
                    "source": [
                        "obj-35",
                        6
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        7
                    ],
                    "source": [
                        "obj-16",
                        7
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        7
                    ],
                    "source": [
                        "obj-32",
                        7
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        7
                    ],
                    "source": [
                        "obj-35",
                        7
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        8
                    ],
                    "source": [
                        "obj-16",
                        8
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        8
                    ],
                    "source": [
                        "obj-32",
                        8
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        8
                    ],
                    "source": [
                        "obj-35",
                        8
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        9
                    ],
                    "source": [
                        "obj-16",
                        9
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        9
                    ],
                    "source": [
                        "obj-32",
                        9
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        9
                    ],
                    "source": [
                        "obj-35",
                        9
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        10
                    ],
                    "source": [
                        "obj-16",
                        10
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        10
                    ],
                    "source": [
                        "obj-32",
                        10
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        10
                    ],
                    "source": [
                        "obj-35",
                        10
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        11
                    ],
                    "source": [
                        "obj-16",
                        11
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        11
                    ],
                    "source": [
                        "obj-32",
                        11
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        11
                    ],
                    "source": [
                        "obj-35",
                        11
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        12
                    ],
                    "source": [
                        "obj-16",
                        12
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        12
                    ],
                    "source": [
                        "obj-32",
                        12
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        12
                    ],
                    "source": [
                        "obj-35",
                        12
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        13
                    ],
                    "source": [
                        "obj-16",
                        13
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        13
                    ],
                    "source": [
                        "obj-32",
                        13
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        13
                    ],
                    "source": [
                        "obj-35",
                        13
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        14
                    ],
                    "source": [
                        "obj-16",
                        14
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        14
                    ],
                    "source": [
                        "obj-32",
                        14
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        14
                    ],
                    "source": [
                        "obj-35",
                        14
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-17",
                        15
                    ],
                    "source": [
                        "obj-16",
                        15
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-33",
                        15
                    ],
                    "source": [
                        "obj-32",
                        15
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        15
                    ],
                    "source": [
                        "obj-35",
                        15
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-19",
                        0
                    ],
                    "source": [
                        "obj-18",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-20",
                        0
                    ],
                    "source": [
                        "obj-19",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-21",
                        0
                    ],
                    "source": [
                        "obj-20",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-54",
                        1
                    ],
                    "source": [
                        "obj-20",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-74",
                        0
                    ],
                    "source": [
                        "obj-20",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-75",
                        0
                    ],
                    "source": [
                        "obj-74",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-76",
                        0
                    ],
                    "source": [
                        "obj-75",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-77",
                        2
                    ],
                    "source": [
                        "obj-76",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-23",
                        0
                    ],
                    "source": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-24",
                        0
                    ],
                    "source": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        1
                    ],
                    "source": [
                        "obj-23",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-26",
                        0
                    ],
                    "source": [
                        "obj-14",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-29",
                        0
                    ],
                    "source": [
                        "obj-26",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-27",
                        0
                    ],
                    "source": [
                        "obj-26",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-28",
                        0
                    ],
                    "source": [
                        "obj-26",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-162",
                        0
                    ],
                    "source": [
                        "obj-27",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-37",
                        1
                    ],
                    "source": [
                        "obj-162",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-46",
                        1
                    ],
                    "source": [
                        "obj-28",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-32",
                        0
                    ],
                    "source": [
                        "obj-31",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-35",
                        0
                    ],
                    "source": [
                        "obj-34",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-160",
                        0
                    ],
                    "source": [
                        "obj-36",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-161",
                        0
                    ],
                    "source": [
                        "obj-159",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-161",
                        1
                    ],
                    "source": [
                        "obj-160",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-37",
                        0
                    ],
                    "source": [
                        "obj-161",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-38",
                        0
                    ],
                    "source": [
                        "obj-37",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        0
                    ],
                    "source": [
                        "obj-38",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-163",
                        0
                    ],
                    "source": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-40",
                        0
                    ],
                    "source": [
                        "obj-163",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-164",
                        0
                    ],
                    "source": [
                        "obj-163",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-41",
                        0
                    ],
                    "source": [
                        "obj-40",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-165",
                        0
                    ],
                    "source": [
                        "obj-40",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-165",
                        1
                    ],
                    "source": [
                        "obj-164",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-166",
                        0
                    ],
                    "source": [
                        "obj-165",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-49",
                        0
                    ],
                    "source": [
                        "obj-166",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-50",
                        1
                    ],
                    "source": [
                        "obj-166",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-43",
                        0
                    ],
                    "source": [
                        "obj-42",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-44",
                        0
                    ],
                    "source": [
                        "obj-43",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-45",
                        0
                    ],
                    "source": [
                        "obj-44",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-45",
                        1
                    ],
                    "source": [
                        "obj-41",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-46",
                        0
                    ],
                    "source": [
                        "obj-45",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-47",
                        0
                    ],
                    "source": [
                        "obj-46",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-167",
                        0
                    ],
                    "source": [
                        "obj-47",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-48",
                        0
                    ],
                    "source": [
                        "obj-167",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-49",
                        1
                    ],
                    "source": [
                        "obj-167",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-49",
                        2
                    ],
                    "source": [
                        "obj-48",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-51",
                        0
                    ],
                    "source": [
                        "obj-50",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-52",
                        0
                    ],
                    "source": [
                        "obj-51",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-53",
                        0
                    ],
                    "source": [
                        "obj-49",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-53",
                        1
                    ],
                    "source": [
                        "obj-52",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-54",
                        0
                    ],
                    "source": [
                        "obj-33",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-55",
                        0
                    ],
                    "source": [
                        "obj-54",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-56",
                        0
                    ],
                    "source": [
                        "obj-53",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-56",
                        1
                    ],
                    "source": [
                        "obj-55",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-57",
                        0
                    ],
                    "source": [
                        "obj-17",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-58",
                        0
                    ],
                    "source": [
                        "obj-57",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-59",
                        1
                    ],
                    "source": [
                        "obj-58",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-60",
                        0
                    ],
                    "source": [
                        "obj-57",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-61",
                        0
                    ],
                    "source": [
                        "obj-60",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-62",
                        1
                    ],
                    "source": [
                        "obj-61",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
                        0
                    ],
                    "source": [
                        "obj-56",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-64",
                        0
                    ],
                    "source": [
                        "obj-56",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
                        1
                    ],
                    "source": [
                        "obj-59",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-64",
                        1
                    ],
                    "source": [
                        "obj-62",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-65",
                        0
                    ],
                    "source": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-66",
                        0
                    ],
                    "source": [
                        "obj-64",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-175",
                        0
                    ],
                    "source": [
                        "obj-65",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-67",
                        0
                    ],
                    "source": [
                        "obj-175",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-176",
                        0
                    ],
                    "source": [
                        "obj-66",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-68",
                        0
                    ],
                    "source": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-69",
                        0
                    ],
                    "source": [
                        "obj-67",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-69",
                        1
                    ],
                    "source": [
                        "obj-68",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-77",
                        0
                    ],
                    "source": [
                        "obj-70",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-77",
                        1
                    ],
                    "source": [
                        "obj-72",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-78",
                        0
                    ],
                    "source": [
                        "obj-77",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-79",
                        0
                    ],
                    "source": [
                        "obj-78",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-80",
                        0
                    ],
                    "source": [
                        "obj-79",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-67",
                        1
                    ],
                    "source": [
                        "obj-80",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-68",
                        1
                    ],
                    "source": [
                        "obj-80",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-83",
                        0
                    ],
                    "source": [
                        "obj-81",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-86",
                        1
                    ],
                    "source": [
                        "obj-83",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-48",
                        1
                    ],
                    "source": [
                        "obj-83",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-190",
                        0
                    ],
                    "source": [
                        "obj-173",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-87",
                        0
                    ],
                    "source": [
                        "obj-86",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-168",
                        0
                    ],
                    "source": [
                        "obj-87",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-47",
                        1
                    ],
                    "source": [
                        "obj-168",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-89",
                        0
                    ],
                    "source": [
                        "obj-88",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-90",
                        0
                    ],
                    "source": [
                        "obj-89",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-91",
                        0
                    ],
                    "source": [
                        "obj-89",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-92",
                        0
                    ],
                    "source": [
                        "obj-91",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-93",
                        0
                    ],
                    "source": [
                        "obj-92",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-94",
                        0
                    ],
                    "source": [
                        "obj-92",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-90",
                        0
                    ],
                    "source": [
                        "obj-93",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-95",
                        0
                    ],
                    "source": [
                        "obj-90",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-96",
                        0
                    ],
                    "source": [
                        "obj-95",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-96",
                        0
                    ],
                    "source": [
                        "obj-94",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-99",
                        0
                    ],
                    "source": [
                        "obj-97",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-100",
                        0
                    ],
                    "source": [
                        "obj-99",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-12",
                        0
                    ],
                    "source": [
                        "obj-100",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-13",
                        0
                    ],
                    "source": [
                        "obj-100",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-14",
                        0
                    ],
                    "source": [
                        "obj-100",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-113",
                        0
                    ],
                    "source": [
                        "obj-99",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-114",
                        0
                    ],
                    "source": [
                        "obj-99",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-102",
                        0
                    ],
                    "source": [
                        "obj-99",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-101",
                        0
                    ],
                    "source": [
                        "obj-99",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-109",
                        0
                    ],
                    "source": [
                        "obj-101",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-111",
                        0
                    ],
                    "source": [
                        "obj-101",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-19",
                        0
                    ],
                    "source": [
                        "obj-101",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-103",
                        0
                    ],
                    "source": [
                        "obj-102",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-104",
                        0
                    ],
                    "source": [
                        "obj-103",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-105",
                        0
                    ],
                    "source": [
                        "obj-104",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-107",
                        1
                    ],
                    "source": [
                        "obj-105",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-106",
                        0
                    ],
                    "source": [
                        "obj-104",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-107",
                        0
                    ],
                    "source": [
                        "obj-106",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-108",
                        0
                    ],
                    "source": [
                        "obj-107",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-15",
                        0
                    ],
                    "source": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-113",
                        1
                    ],
                    "source": [
                        "obj-109",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-114",
                        1
                    ],
                    "source": [
                        "obj-111",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-23",
                        0
                    ],
                    "source": [
                        "obj-113",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-24",
                        0
                    ],
                    "source": [
                        "obj-113",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-26",
                        0
                    ],
                    "source": [
                        "obj-114",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-116",
                        0
                    ],
                    "source": [
                        "obj-115",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-126",
                        0
                    ],
                    "source": [
                        "obj-116",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-26",
                        0
                    ],
                    "source": [
                        "obj-126",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-125",
                        0
                    ],
                    "source": [
                        "obj-116",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-23",
                        0
                    ],
                    "source": [
                        "obj-125",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-124",
                        0
                    ],
                    "source": [
                        "obj-116",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-19",
                        0
                    ],
                    "source": [
                        "obj-124",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-123",
                        0
                    ],
                    "source": [
                        "obj-116",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-111",
                        0
                    ],
                    "source": [
                        "obj-123",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-122",
                        0
                    ],
                    "source": [
                        "obj-116",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-109",
                        0
                    ],
                    "source": [
                        "obj-122",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-121",
                        0
                    ],
                    "source": [
                        "obj-116",
                        5
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-97",
                        0
                    ],
                    "source": [
                        "obj-121",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-120",
                        0
                    ],
                    "source": [
                        "obj-116",
                        6
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-84",
                        0
                    ],
                    "source": [
                        "obj-120",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-119",
                        0
                    ],
                    "source": [
                        "obj-116",
                        7
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-81",
                        0
                    ],
                    "source": [
                        "obj-119",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-118",
                        0
                    ],
                    "source": [
                        "obj-116",
                        8
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-72",
                        0
                    ],
                    "source": [
                        "obj-118",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-117",
                        0
                    ],
                    "source": [
                        "obj-116",
                        9
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-70",
                        0
                    ],
                    "source": [
                        "obj-117",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-34",
                        0
                    ],
                    "source": [
                        "obj-116",
                        10
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-31",
                        0
                    ],
                    "source": [
                        "obj-116",
                        11
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-72",
                        0
                    ],
                    "source": [
                        "obj-127",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-131",
                        0
                    ],
                    "source": [
                        "obj-130",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-132",
                        0
                    ],
                    "source": [
                        "obj-131",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-133",
                        0
                    ],
                    "source": [
                        "obj-132",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-137",
                        0
                    ],
                    "source": [
                        "obj-133",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-134",
                        0
                    ],
                    "source": [
                        "obj-132",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-137",
                        0
                    ],
                    "source": [
                        "obj-134",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-135",
                        0
                    ],
                    "source": [
                        "obj-132",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-137",
                        0
                    ],
                    "source": [
                        "obj-135",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-136",
                        0
                    ],
                    "source": [
                        "obj-132",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-137",
                        0
                    ],
                    "source": [
                        "obj-136",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-138",
                        0
                    ],
                    "source": [
                        "obj-84",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-137",
                        1
                    ],
                    "source": [
                        "obj-138",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-139",
                        0
                    ],
                    "source": [
                        "obj-137",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-140",
                        0
                    ],
                    "source": [
                        "obj-139",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-141",
                        1
                    ],
                    "source": [
                        "obj-140",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-141",
                        0
                    ],
                    "source": [
                        "obj-139",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-145",
                        0
                    ],
                    "source": [
                        "obj-139",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-142",
                        0
                    ],
                    "source": [
                        "obj-141",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-143",
                        0
                    ],
                    "source": [
                        "obj-142",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-144",
                        0
                    ],
                    "source": [
                        "obj-143",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-146",
                        0
                    ],
                    "source": [
                        "obj-145",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-147",
                        0
                    ],
                    "source": [
                        "obj-146",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-147",
                        1
                    ],
                    "source": [
                        "obj-150",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-148",
                        0
                    ],
                    "source": [
                        "obj-144",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-149",
                        0
                    ],
                    "source": [
                        "obj-144",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-148",
                        1
                    ],
                    "source": [
                        "obj-147",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-149",
                        1
                    ],
                    "source": [
                        "obj-147",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-69",
                        0
                    ],
                    "source": [
                        "obj-148",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-69",
                        1
                    ],
                    "source": [
                        "obj-149",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-153",
                        0
                    ],
                    "source": [
                        "obj-152",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-150",
                        0
                    ],
                    "source": [
                        "obj-153",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-81",
                        0
                    ],
                    "source": [
                        "obj-154",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-156",
                        0
                    ],
                    "source": [
                        "obj-130",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-158",
                        0
                    ],
                    "source": [
                        "obj-156",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-157",
                        0
                    ],
                    "source": [
                        "obj-137",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-158",
                        0
                    ],
                    "source": [
                        "obj-157",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-169",
                        0
                    ],
                    "source": [
                        "obj-81",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-164",
                        1
                    ],
                    "source": [
                        "obj-169",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-163",
                        1
                    ],
                    "source": [
                        "obj-169",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-195",
                        0
                    ],
                    "source": [
                        "obj-170",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-167",
                        1
                    ],
                    "source": [
                        "obj-172",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-175",
                        1
                    ],
                    "source": [
                        "obj-177",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-176",
                        1
                    ],
                    "source": [
                        "obj-177",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-180",
                        0
                    ],
                    "source": [
                        "obj-179",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-183",
                        0
                    ],
                    "source": [
                        "obj-180",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-182",
                        0
                    ],
                    "source": [
                        "obj-180",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-181",
                        0
                    ],
                    "source": [
                        "obj-180",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-170",
                        0
                    ],
                    "source": [
                        "obj-181",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-173",
                        0
                    ],
                    "source": [
                        "obj-182",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-177",
                        0
                    ],
                    "source": [
                        "obj-183",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-150",
                        0
                    ],
                    "source": [
                        "obj-184",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-186",
                        0
                    ],
                    "source": [
                        "obj-92",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-187",
                        0
                    ],
                    "source": [
                        "obj-186",
                        6
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-84",
                        0
                    ],
                    "source": [
                        "obj-187",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-188",
                        0
                    ],
                    "source": [
                        "obj-186",
                        6
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-96",
                        0
                    ],
                    "source": [
                        "obj-188",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-189",
                        0
                    ],
                    "source": [
                        "obj-186",
                        8
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-96",
                        0
                    ],
                    "source": [
                        "obj-189",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-190",
                        1
                    ],
                    "source": [
                        "obj-84",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-191",
                        0
                    ],
                    "source": [
                        "obj-190",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-192",
                        0
                    ],
                    "source": [
                        "obj-191",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-193",
                        0
                    ],
                    "source": [
                        "obj-192",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-86",
                        0
                    ],
                    "source": [
                        "obj-192",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-198",
                        0
                    ],
                    "source": [
                        "obj-192",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-193",
                        1
                    ],
                    "source": [
                        "obj-84",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-194",
                        0
                    ],
                    "source": [
                        "obj-193",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-195",
                        1
                    ],
                    "source": [
                        "obj-194",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-196",
                        0
                    ],
                    "source": [
                        "obj-195",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-172",
                        0
                    ],
                    "source": [
                        "obj-196",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-197",
                        0
                    ],
                    "source": [
                        "obj-196",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-199",
                        0
                    ],
                    "source": [
                        "obj-197",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-199",
                        0
                    ],
                    "source": [
                        "obj-198",
                        0
                    ]
                }
            }
        ]
    }
}
