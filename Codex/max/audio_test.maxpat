{
  "patcher": {
    "fileversion": 1,
    "appversion": { "major": 8, "minor": 6, "revision": 0, "architecture": "x64", "modernui": 1 },
    "classnamespace": "box",
    "rect": [100.0, 100.0, 520.0, 300.0],
    "default_fontsize": 12.0,
    "default_fontname": "Arial",
    "boxes": [
      { "box": { "id": "c1", "maxclass": "comment", "text": "Audio test: lock patch with Ctrl+E, then click ezdac~. You should hear a 440 Hz tone.", "patching_rect": [30.0, 25.0, 460.0, 20.0] } },
      { "box": { "id": "o1", "maxclass": "newobj", "text": "cycle~ 440", "patching_rect": [40.0, 80.0, 80.0, 22.0] } },
      { "box": { "id": "o2", "maxclass": "newobj", "text": "*~ 0.12", "patching_rect": [40.0, 125.0, 60.0, 22.0] } },
      { "box": { "id": "o3", "maxclass": "ezdac~", "patching_rect": [40.0, 180.0, 45.0, 45.0] } },
      { "box": { "id": "c2", "maxclass": "comment", "text": "If this is silent, the problem is Max audio settings / output device, not OSC or Python.", "patching_rect": [105.0, 190.0, 390.0, 20.0] } }
    ],
    "lines": [
      { "patchline": { "source": ["o1", 0], "destination": ["o2", 0] } },
      { "patchline": { "source": ["o2", 0], "destination": ["o3", 0] } },
      { "patchline": { "source": ["o2", 0], "destination": ["o3", 1] } }
    ]
  }
}
