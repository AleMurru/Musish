{
  "patcher": {
    "fileversion": 1,
    "appversion": { "major": 8, "minor": 6, "revision": 0, "architecture": "x64", "modernui": 1 },
    "classnamespace": "box",
    "rect": [80.0, 80.0, 1280.0, 820.0],
    "default_fontsize": 12.0,
    "default_fontname": "Arial",
    "gridonopen": 1,
    "gridsize": [15.0, 15.0],
    "boxes": [
      { "box": { "id": "c_title", "maxclass": "comment", "text": "Aquarium Markov v2 Preview — riceve clock/chord/note/hit da Python su UDP 7401 e li manda a noteout", "patching_rect": [30.0, 20.0, 900.0, 20.0] } },
      { "box": { "id": "c_instr", "maxclass": "comment", "text": "Uso: avvia Python main.py, apri questa patch, scegli/abilita una destinazione MIDI per noteout. In Max Console vedi NOTE/HIT/CHORD.", "patching_rect": [30.0, 45.0, 980.0, 20.0] } },
      { "box": { "id": "lb", "maxclass": "newobj", "text": "loadbang", "patching_rect": [30.0, 80.0, 70.0, 22.0] } },
      { "box": { "id": "ch_bass", "maxclass": "message", "text": "1", "patching_rect": [560.0, 245.0, 35.0, 22.0] } },
      { "box": { "id": "ch_lead", "maxclass": "message", "text": "2", "patching_rect": [560.0, 345.0, 35.0, 22.0] } },
      { "box": { "id": "ch_keys", "maxclass": "message", "text": "3", "patching_rect": [560.0, 445.0, 35.0, 22.0] } },
      { "box": { "id": "ch_chord", "maxclass": "message", "text": "4", "patching_rect": [1010.0, 245.0, 35.0, 22.0] } },
      { "box": { "id": "ch_hit", "maxclass": "message", "text": "10", "patching_rect": [1010.0, 545.0, 35.0, 22.0] } },

      { "box": { "id": "nr", "maxclass": "newobj", "text": "netreceive -u 7401", "patching_rect": [30.0, 115.0, 130.0, 22.0] } },
      { "box": { "id": "rt", "maxclass": "newobj", "text": "route direct performance clock chord note hit", "patching_rect": [30.0, 155.0, 320.0, 22.0] } },
      { "box": { "id": "p_direct", "maxclass": "print", "text": "DIRECT", "patching_rect": [30.0, 195.0, 80.0, 22.0] } },
      { "box": { "id": "p_perf", "maxclass": "print", "text": "PERFORMANCE", "patching_rect": [120.0, 195.0, 110.0, 22.0] } },
      { "box": { "id": "p_clock", "maxclass": "print", "text": "CLOCK", "patching_rect": [240.0, 195.0, 80.0, 22.0] } },
      { "box": { "id": "p_chord", "maxclass": "print", "text": "CHORD", "patching_rect": [780.0, 195.0, 80.0, 22.0] } },
      { "box": { "id": "p_note", "maxclass": "print", "text": "NOTE", "patching_rect": [390.0, 195.0, 80.0, 22.0] } },
      { "box": { "id": "p_hit", "maxclass": "print", "text": "HIT", "patching_rect": [780.0, 495.0, 80.0, 22.0] } },

      { "box": { "id": "route_note", "maxclass": "newobj", "text": "route bass lead keys", "patching_rect": [390.0, 230.0, 160.0, 22.0] } },
      { "box": { "id": "c_note", "maxclass": "comment", "text": "note voice midi velocity duration_ms degree octave layer scene chord event", "patching_rect": [390.0, 255.0, 360.0, 20.0] } },

      { "box": { "id": "un_bass", "maxclass": "newobj", "text": "unpack i i i i i i i i i", "patching_rect": [390.0, 280.0, 170.0, 22.0] } },
      { "box": { "id": "mk_bass", "maxclass": "newobj", "text": "makenote", "patching_rect": [390.0, 320.0, 70.0, 22.0] } },
      { "box": { "id": "no_bass", "maxclass": "newobj", "text": "noteout", "patching_rect": [390.0, 360.0, 60.0, 22.0] } },
      { "box": { "id": "c_bass", "maxclass": "comment", "text": "BASS -> MIDI ch 1", "patching_rect": [465.0, 360.0, 120.0, 20.0] } },

      { "box": { "id": "un_lead", "maxclass": "newobj", "text": "unpack i i i i i i i i i", "patching_rect": [390.0, 380.0, 170.0, 22.0] } },
      { "box": { "id": "mk_lead", "maxclass": "newobj", "text": "makenote", "patching_rect": [390.0, 420.0, 70.0, 22.0] } },
      { "box": { "id": "no_lead", "maxclass": "newobj", "text": "noteout", "patching_rect": [390.0, 460.0, 60.0, 22.0] } },
      { "box": { "id": "c_lead", "maxclass": "comment", "text": "LEAD -> MIDI ch 2", "patching_rect": [465.0, 460.0, 120.0, 20.0] } },

      { "box": { "id": "un_keys", "maxclass": "newobj", "text": "unpack i i i i i i i i i", "patching_rect": [390.0, 480.0, 170.0, 22.0] } },
      { "box": { "id": "mk_keys", "maxclass": "newobj", "text": "makenote", "patching_rect": [390.0, 520.0, 70.0, 22.0] } },
      { "box": { "id": "no_keys", "maxclass": "newobj", "text": "noteout", "patching_rect": [390.0, 560.0, 60.0, 22.0] } },
      { "box": { "id": "c_keys", "maxclass": "comment", "text": "KEYS -> MIDI ch 3", "patching_rect": [465.0, 560.0, 120.0, 20.0] } },

      { "box": { "id": "un_chord", "maxclass": "newobj", "text": "unpack i i i i i i", "patching_rect": [780.0, 230.0, 135.0, 22.0] } },
      { "box": { "id": "mk_chord1", "maxclass": "newobj", "text": "makenote 55 1800", "patching_rect": [780.0, 280.0, 105.0, 22.0] } },
      { "box": { "id": "mk_chord2", "maxclass": "newobj", "text": "makenote 55 1800", "patching_rect": [780.0, 330.0, 105.0, 22.0] } },
      { "box": { "id": "mk_chord3", "maxclass": "newobj", "text": "makenote 55 1800", "patching_rect": [780.0, 380.0, 105.0, 22.0] } },
      { "box": { "id": "no_chord", "maxclass": "newobj", "text": "noteout", "patching_rect": [920.0, 330.0, 60.0, 22.0] } },
      { "box": { "id": "c_chord", "maxclass": "comment", "text": "CHORD pad -> MIDI ch 4", "patching_rect": [920.0, 360.0, 160.0, 20.0] } },

      { "box": { "id": "route_hit", "maxclass": "newobj", "text": "route grain glitch noise", "patching_rect": [780.0, 530.0, 165.0, 22.0] } },
      { "box": { "id": "c_hit", "maxclass": "comment", "text": "hit voice sample_id velocity duration_ms scene event -> GM drums ch 10", "patching_rect": [780.0, 555.0, 360.0, 20.0] } },

      { "box": { "id": "un_grain", "maxclass": "newobj", "text": "unpack i i i i i", "patching_rect": [780.0, 585.0, 115.0, 22.0] } },
      { "box": { "id": "expr_grain", "maxclass": "newobj", "text": "expr 72 + $i1", "patching_rect": [780.0, 620.0, 90.0, 22.0] } },
      { "box": { "id": "mk_grain", "maxclass": "newobj", "text": "makenote", "patching_rect": [780.0, 655.0, 70.0, 22.0] } },

      { "box": { "id": "un_glitch", "maxclass": "newobj", "text": "unpack i i i i i", "patching_rect": [910.0, 585.0, 115.0, 22.0] } },
      { "box": { "id": "expr_glitch", "maxclass": "newobj", "text": "expr 84 + $i1", "patching_rect": [910.0, 620.0, 90.0, 22.0] } },
      { "box": { "id": "mk_glitch", "maxclass": "newobj", "text": "makenote", "patching_rect": [910.0, 655.0, 70.0, 22.0] } },

      { "box": { "id": "un_noise", "maxclass": "newobj", "text": "unpack i i i i i", "patching_rect": [1040.0, 585.0, 115.0, 22.0] } },
      { "box": { "id": "expr_noise", "maxclass": "newobj", "text": "expr 36 + $i1", "patching_rect": [1040.0, 620.0, 90.0, 22.0] } },
      { "box": { "id": "mk_noise", "maxclass": "newobj", "text": "makenote", "patching_rect": [1040.0, 655.0, 70.0, 22.0] } },
      { "box": { "id": "no_hit", "maxclass": "newobj", "text": "noteout", "patching_rect": [910.0, 705.0, 60.0, 22.0] } },

      { "box": { "id": "c_out", "maxclass": "comment", "text": "Se non senti nulla: doppio click sui noteout e scegli Microsoft GS Wavetable Synth / porta MIDI disponibile, oppure instrada verso Ableton/Max synth.", "patching_rect": [30.0, 760.0, 980.0, 20.0] } }
    ],
    "lines": [
      { "patchline": { "source": ["lb", 0], "destination": ["ch_bass", 0] } },
      { "patchline": { "source": ["lb", 0], "destination": ["ch_lead", 0] } },
      { "patchline": { "source": ["lb", 0], "destination": ["ch_keys", 0] } },
      { "patchline": { "source": ["lb", 0], "destination": ["ch_chord", 0] } },
      { "patchline": { "source": ["lb", 0], "destination": ["ch_hit", 0] } },

      { "patchline": { "source": ["ch_bass", 0], "destination": ["no_bass", 2] } },
      { "patchline": { "source": ["ch_lead", 0], "destination": ["no_lead", 2] } },
      { "patchline": { "source": ["ch_keys", 0], "destination": ["no_keys", 2] } },
      { "patchline": { "source": ["ch_chord", 0], "destination": ["no_chord", 2] } },
      { "patchline": { "source": ["ch_hit", 0], "destination": ["no_hit", 2] } },

      { "patchline": { "source": ["nr", 0], "destination": ["rt", 0] } },
      { "patchline": { "source": ["rt", 0], "destination": ["p_direct", 0] } },
      { "patchline": { "source": ["rt", 1], "destination": ["p_perf", 0] } },
      { "patchline": { "source": ["rt", 2], "destination": ["p_clock", 0] } },
      { "patchline": { "source": ["rt", 3], "destination": ["p_chord", 0] } },
      { "patchline": { "source": ["rt", 4], "destination": ["p_note", 0] } },
      { "patchline": { "source": ["rt", 5], "destination": ["p_hit", 0] } },

      { "patchline": { "source": ["rt", 4], "destination": ["route_note", 0] } },
      { "patchline": { "source": ["route_note", 0], "destination": ["un_bass", 0] } },
      { "patchline": { "source": ["route_note", 1], "destination": ["un_lead", 0] } },
      { "patchline": { "source": ["route_note", 2], "destination": ["un_keys", 0] } },

      { "patchline": { "source": ["un_bass", 0], "destination": ["mk_bass", 0] } },
      { "patchline": { "source": ["un_bass", 1], "destination": ["mk_bass", 1] } },
      { "patchline": { "source": ["un_bass", 2], "destination": ["mk_bass", 2] } },
      { "patchline": { "source": ["mk_bass", 0], "destination": ["no_bass", 0] } },
      { "patchline": { "source": ["mk_bass", 1], "destination": ["no_bass", 1] } },

      { "patchline": { "source": ["un_lead", 0], "destination": ["mk_lead", 0] } },
      { "patchline": { "source": ["un_lead", 1], "destination": ["mk_lead", 1] } },
      { "patchline": { "source": ["un_lead", 2], "destination": ["mk_lead", 2] } },
      { "patchline": { "source": ["mk_lead", 0], "destination": ["no_lead", 0] } },
      { "patchline": { "source": ["mk_lead", 1], "destination": ["no_lead", 1] } },

      { "patchline": { "source": ["un_keys", 0], "destination": ["mk_keys", 0] } },
      { "patchline": { "source": ["un_keys", 1], "destination": ["mk_keys", 1] } },
      { "patchline": { "source": ["un_keys", 2], "destination": ["mk_keys", 2] } },
      { "patchline": { "source": ["mk_keys", 0], "destination": ["no_keys", 0] } },
      { "patchline": { "source": ["mk_keys", 1], "destination": ["no_keys", 1] } },

      { "patchline": { "source": ["rt", 3], "destination": ["un_chord", 0] } },
      { "patchline": { "source": ["un_chord", 0], "destination": ["mk_chord1", 0] } },
      { "patchline": { "source": ["un_chord", 1], "destination": ["mk_chord2", 0] } },
      { "patchline": { "source": ["un_chord", 2], "destination": ["mk_chord3", 0] } },
      { "patchline": { "source": ["mk_chord1", 0], "destination": ["no_chord", 0] } },
      { "patchline": { "source": ["mk_chord1", 1], "destination": ["no_chord", 1] } },
      { "patchline": { "source": ["mk_chord2", 0], "destination": ["no_chord", 0] } },
      { "patchline": { "source": ["mk_chord2", 1], "destination": ["no_chord", 1] } },
      { "patchline": { "source": ["mk_chord3", 0], "destination": ["no_chord", 0] } },
      { "patchline": { "source": ["mk_chord3", 1], "destination": ["no_chord", 1] } },

      { "patchline": { "source": ["rt", 5], "destination": ["route_hit", 0] } },
      { "patchline": { "source": ["route_hit", 0], "destination": ["un_grain", 0] } },
      { "patchline": { "source": ["route_hit", 1], "destination": ["un_glitch", 0] } },
      { "patchline": { "source": ["route_hit", 2], "destination": ["un_noise", 0] } },

      { "patchline": { "source": ["un_grain", 0], "destination": ["expr_grain", 0] } },
      { "patchline": { "source": ["expr_grain", 0], "destination": ["mk_grain", 0] } },
      { "patchline": { "source": ["un_grain", 1], "destination": ["mk_grain", 1] } },
      { "patchline": { "source": ["un_grain", 2], "destination": ["mk_grain", 2] } },
      { "patchline": { "source": ["mk_grain", 0], "destination": ["no_hit", 0] } },
      { "patchline": { "source": ["mk_grain", 1], "destination": ["no_hit", 1] } },

      { "patchline": { "source": ["un_glitch", 0], "destination": ["expr_glitch", 0] } },
      { "patchline": { "source": ["expr_glitch", 0], "destination": ["mk_glitch", 0] } },
      { "patchline": { "source": ["un_glitch", 1], "destination": ["mk_glitch", 1] } },
      { "patchline": { "source": ["un_glitch", 2], "destination": ["mk_glitch", 2] } },
      { "patchline": { "source": ["mk_glitch", 0], "destination": ["no_hit", 0] } },
      { "patchline": { "source": ["mk_glitch", 1], "destination": ["no_hit", 1] } },

      { "patchline": { "source": ["un_noise", 0], "destination": ["expr_noise", 0] } },
      { "patchline": { "source": ["expr_noise", 0], "destination": ["mk_noise", 0] } },
      { "patchline": { "source": ["un_noise", 1], "destination": ["mk_noise", 1] } },
      { "patchline": { "source": ["un_noise", 2], "destination": ["mk_noise", 2] } },
      { "patchline": { "source": ["mk_noise", 0], "destination": ["no_hit", 0] } },
      { "patchline": { "source": ["mk_noise", 1], "destination": ["no_hit", 1] } }
    ]
  }
}
