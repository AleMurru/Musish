{
  "patcher": {
    "fileversion": 1,
    "appversion": { "major": 8, "minor": 6, "revision": 0, "architecture": "x64", "modernui": 1 },
    "classnamespace": "box",
    "rect": [90.0, 90.0, 1050.0, 700.0],
    "default_fontsize": 12.0,
    "default_fontname": "Arial",
    "gridonopen": 1,
    "gridsize": [15.0, 15.0],
    "boxes": [
      { "box": { "id": "c-title", "maxclass": "comment", "text": "MIDIMAX -> Python control template. Sends plain UDP controls to Python on port 7500.", "patching_rect": [30.0, 20.0, 650.0, 20.0] } },
      { "box": { "id": "ctlin", "maxclass": "newobj", "text": "ctlin", "patching_rect": [30.0, 65.0, 45.0, 22.0] } },
      { "box": { "id": "vnum", "maxclass": "number", "patching_rect": [30.0, 105.0, 55.0, 22.0] } },
      { "box": { "id": "ccnum", "maxclass": "number", "patching_rect": [100.0, 105.0, 55.0, 22.0] } },
      { "box": { "id": "chnum", "maxclass": "number", "patching_rect": [170.0, 105.0, 55.0, 22.0] } },
      { "box": { "id": "c-learn", "maxclass": "comment", "text": "Learn mode: move a MIDIMAX fader. Boxes show value / CC number / channel. Use those CC numbers in your own ctlin/route mapping.", "patching_rect": [245.0, 105.0, 700.0, 20.0] } },
      { "box": { "id": "udp", "maxclass": "newobj", "text": "udpsend 127.0.0.1 7500", "patching_rect": [730.0, 600.0, 165.0, 22.0] } },
      { "box": { "id": "c-udp", "maxclass": "comment", "text": "All message boxes below go to Python main.py. Python prints [control] name = value.", "patching_rect": [30.0, 155.0, 600.0, 20.0] } },

      { "box": { "id": "f1", "maxclass": "flonum", "patching_rect": [30.0, 205.0, 70.0, 22.0] } },
      { "box": { "id": "m1", "maxclass": "message", "text": "control density_fader $1", "patching_rect": [115.0, 205.0, 170.0, 22.0] } },
      { "box": { "id": "c1", "maxclass": "comment", "text": "0..1 | amount of Markov events / collective -> individual", "patching_rect": [305.0, 207.0, 380.0, 20.0] } },

      { "box": { "id": "f2", "maxclass": "flonum", "patching_rect": [30.0, 250.0, 70.0, 22.0] } },
      { "box": { "id": "m2", "maxclass": "message", "text": "control alignment_weight $1", "patching_rect": [115.0, 250.0, 190.0, 22.0] } },
      { "box": { "id": "c2", "maxclass": "comment", "text": "0..3 | boids align to neighbors", "patching_rect": [320.0, 252.0, 320.0, 20.0] } },

      { "box": { "id": "f3", "maxclass": "flonum", "patching_rect": [30.0, 295.0, 70.0, 22.0] } },
      { "box": { "id": "m3", "maxclass": "message", "text": "control cohesion_weight $1", "patching_rect": [115.0, 295.0, 190.0, 22.0] } },
      { "box": { "id": "c3", "maxclass": "comment", "text": "0..3 | boids aggregate / school compactness", "patching_rect": [320.0, 297.0, 340.0, 20.0] } },

      { "box": { "id": "f4", "maxclass": "flonum", "patching_rect": [30.0, 340.0, 70.0, 22.0] } },
      { "box": { "id": "m4", "maxclass": "message", "text": "control separation_weight $1", "patching_rect": [115.0, 340.0, 200.0, 22.0] } },
      { "box": { "id": "c4", "maxclass": "comment", "text": "0..4 | collision avoidance / dispersion", "patching_rect": [330.0, 342.0, 330.0, 20.0] } },

      { "box": { "id": "f5", "maxclass": "flonum", "patching_rect": [30.0, 385.0, 70.0, 22.0] } },
      { "box": { "id": "m5", "maxclass": "message", "text": "control noise_weight $1", "patching_rect": [115.0, 385.0, 175.0, 22.0] } },
      { "box": { "id": "c5", "maxclass": "comment", "text": "0..1.5 | turbulence / chaos", "patching_rect": [305.0, 387.0, 320.0, 20.0] } },

      { "box": { "id": "f6", "maxclass": "flonum", "patching_rect": [30.0, 430.0, 70.0, 22.0] } },
      { "box": { "id": "m6", "maxclass": "message", "text": "control food_strength $1", "patching_rect": [115.0, 430.0, 175.0, 22.0] } },
      { "box": { "id": "c6", "maxclass": "comment", "text": "0..3 | strength of mouse-left attractor/food", "patching_rect": [305.0, 432.0, 360.0, 20.0] } },

      { "box": { "id": "f7", "maxclass": "flonum", "patching_rect": [30.0, 475.0, 70.0, 22.0] } },
      { "box": { "id": "m7", "maxclass": "message", "text": "control predator_strength $1", "patching_rect": [115.0, 475.0, 195.0, 22.0] } },
      { "box": { "id": "c7", "maxclass": "comment", "text": "0..3 | strength of mouse-right predator/repeller", "patching_rect": [325.0, 477.0, 380.0, 20.0] } },

      { "box": { "id": "f8", "maxclass": "flonum", "patching_rect": [30.0, 520.0, 70.0, 22.0] } },
      { "box": { "id": "m8", "maxclass": "message", "text": "control section_id $1", "patching_rect": [115.0, 520.0, 160.0, 22.0] } },
      { "box": { "id": "c8", "maxclass": "comment", "text": "0..5 | intro/growth/dense/chaos/release/outro", "patching_rect": [290.0, 522.0, 380.0, 20.0] } }
    ],
    "lines": [
      { "patchline": { "source": ["ctlin", 0], "destination": ["vnum", 0] } },
      { "patchline": { "source": ["ctlin", 1], "destination": ["ccnum", 0] } },
      { "patchline": { "source": ["ctlin", 2], "destination": ["chnum", 0] } },
      { "patchline": { "source": ["f1", 0], "destination": ["m1", 0] } },
      { "patchline": { "source": ["m1", 0], "destination": ["udp", 0] } },
      { "patchline": { "source": ["f2", 0], "destination": ["m2", 0] } },
      { "patchline": { "source": ["m2", 0], "destination": ["udp", 0] } },
      { "patchline": { "source": ["f3", 0], "destination": ["m3", 0] } },
      { "patchline": { "source": ["m3", 0], "destination": ["udp", 0] } },
      { "patchline": { "source": ["f4", 0], "destination": ["m4", 0] } },
      { "patchline": { "source": ["m4", 0], "destination": ["udp", 0] } },
      { "patchline": { "source": ["f5", 0], "destination": ["m5", 0] } },
      { "patchline": { "source": ["m5", 0], "destination": ["udp", 0] } },
      { "patchline": { "source": ["f6", 0], "destination": ["m6", 0] } },
      { "patchline": { "source": ["m6", 0], "destination": ["udp", 0] } },
      { "patchline": { "source": ["f7", 0], "destination": ["m7", 0] } },
      { "patchline": { "source": ["m7", 0], "destination": ["udp", 0] } },
      { "patchline": { "source": ["f8", 0], "destination": ["m8", 0] } },
      { "patchline": { "source": ["m8", 0], "destination": ["udp", 0] } }
    ]
  }
}
