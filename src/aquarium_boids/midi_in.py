from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .controls import RuntimeControls, clamp01


@dataclass
class MidiAppliedControl:
    cc: int
    value: int
    parameter: str
    scaled_value: float | int


class MidiControllerInput:
    """Direct MIDI input for the controller -> Python -> Max workflow.

    Uses pygame.midi to avoid adding a new dependency. The device is optional:
    if no MIDI input is available, the project continues with keyboard/mouse and
    Max UDP controls.

    Profiles: after a device is opened, the first profile whose key is contained in
    the device name (case-insensitive) replaces the default CC mapping and adds
    Program Change pads. Any other device keeps the default mapping (MIDIMIX).
    Mapping entries whose parameter starts with "/" are not simulation controls:
    they are returned to the caller (an OSC address for Max) and not applied.
    """

    def __init__(
        self,
        device_name: str = "MIDIMIX",
        mapping: dict[int, tuple[str, float, float, bool]] | None = None,
        debug: bool = True,
        profiles: dict[str, tuple[dict[int, tuple[str, float, float, bool]], dict[int, int], dict[int, int]]] | None = None,
    ):
        self.device_name = device_name.lower()
        self.mapping = mapping or {}
        self.debug = debug
        self.profiles = profiles or {}
        self.profile_name = "none (MIDI input not started)"
        self.pc_pads: dict[int, int] = {}  # Program Change number -> pad number
        self.note_pads: dict[int, int] = {}  # note number (note-on, any channel) -> pad number
        self._pending_pads: list[int] = []
        self.enabled = False
        self.device_id: int | None = None
        self.device_label = "no MIDI input"
        self._device_name_found = ""
        self._pygame_midi: Any = None
        self._input: Any = None
        self._seen_values: dict[int, int] = {}

    def start(self) -> None:
        try:
            import pygame.midi as pygame_midi
        except Exception as exc:  # pragma: no cover - depends on local pygame install
            self.device_label = f"pygame.midi unavailable: {exc}"
            print(f"[midi] {self.device_label}")
            return

        self._pygame_midi = pygame_midi
        pygame_midi.init()
        self.device_id = self._find_device_id(pygame_midi)
        if self.device_id is None:
            self.profile_name = "none (no MIDI input)"
            print("[midi] no MIDI input device found; keyboard/Max UDP controls remain active")
            return

        try:
            self._input = pygame_midi.Input(self.device_id)
        except Exception as exc:  # pragma: no cover - hardware dependent
            self.device_label = f"could not open MIDI input {self.device_id}: {exc}"
            self.profile_name = "none (MIDI input could not be opened)"
            print(f"[midi] {self.device_label}")
            return

        self.enabled = True
        self._select_profile()
        print(f"[midi] listening to {self.device_label}")
        if self.debug:
            print("[midi] debug enabled: move controls to print CC/value (and Program Change)")

    def _select_profile(self) -> None:
        name = self._device_name_found.lower()
        for key, (mapping, pads, note_pads) in self.profiles.items():
            if key.lower() in name:
                self.mapping = mapping
                self.pc_pads = pads
                self.note_pads = note_pads
                self.profile_name = key
                return
        self.profile_name = "MIDIMIX (default mapping)"

    def take_pads(self) -> list[int]:
        """Pads (1..8) pressed since the last call, in order."""
        pads, self._pending_pads = self._pending_pads, []
        return pads

    def stop(self) -> None:
        if self._input is not None:
            try:
                self._input.close()
            except Exception:
                pass
        if self._pygame_midi is not None:
            try:
                self._pygame_midi.quit()
            except Exception:
                pass

    def _find_device_id(self, pygame_midi: Any) -> int | None:
        fallback: int | None = None
        for device_id in range(pygame_midi.get_count()):
            interf, name, is_input, _is_output, _opened = pygame_midi.get_device_info(device_id)
            label = name.decode(errors="ignore") if isinstance(name, bytes) else str(name)
            interface = interf.decode(errors="ignore") if isinstance(interf, bytes) else str(interf)
            if is_input:
                print(f"[midi] input device {device_id}: {label} ({interface})")
                if fallback is None:
                    fallback = device_id
                if self.device_name and self.device_name in label.lower():
                    self.device_label = f"{label} [{device_id}]"
                    self._device_name_found = label
                    return device_id
        if fallback is not None:
            info = pygame_midi.get_device_info(fallback)
            label = info[1].decode(errors="ignore") if isinstance(info[1], bytes) else str(info[1])
            self.device_label = f"{label} [{fallback}] fallback"
            self._device_name_found = label
        return fallback

    def poll(self, controls: RuntimeControls, max_events: int = 64) -> list[MidiAppliedControl]:
        if not self.enabled or self._input is None:
            return []
        if not self._input.poll():
            return []

        applied: list[MidiAppliedControl] = []
        events = self._input.read(max_events)
        for event in events:
            data = event[0]
            status = int(data[0])
            cc = int(data[1])
            value = int(data[2])
            message_type = status & 0xF0
            channel = (status & 0x0F) + 1

            # Program Change 0xC0..0xCF: pads, only for profiles that define them.
            if message_type == 0xC0:
                pad = self.pc_pads.get(cc)  # data[1] is the program number
                if pad is not None:
                    self._pending_pads.append(pad)
                    if self.debug:
                        print(f"[pad] {pad}  (program {cc}, channel {channel})")
                elif self.debug:
                    print(f"[midi] program={cc} channel={channel}: not a pad in profile {self.profile_name}")
                continue

            # Note-on 0x90..0x9F with velocity > 0: pads, only for profiles that map notes (any channel).
            # Note-off and note-on with velocity 0 are ignored.
            if message_type in (0x80, 0x90):
                is_on = message_type == 0x90 and value > 0
                pad = self.note_pads.get(cc) if is_on else None  # data[1] is the note number
                if pad is not None:
                    self._pending_pads.append(pad)
                    if self.debug:
                        print(f"[pad] {pad}  (note {cc}, channel {channel})")
                elif self.debug:
                    state = "on" if is_on else "off"
                    print(f"[midi] note {state} {cc} velocity={value} channel={channel}: ignored")
                continue

            # MIDI CC messages are 0xB0..0xBF.
            if message_type != 0xB0:
                continue

            if self.debug and self._seen_values.get(cc) != value:
                self._seen_values[cc] = value
                print(f"[midi] cc={cc} value={value} channel={channel}")

            if cc not in self.mapping:
                continue

            parameter, min_value, max_value, quantize = self.mapping[cc]
            normalized = clamp01(value / 127.0)
            scaled = min_value + normalized * (max_value - min_value)
            if quantize:
                scaled_value: float | int = int(round(scaled))
            else:
                scaled_value = float(scaled)

            if not parameter.startswith("/"):  # "/..." = OSC address for Max, handled by the caller
                apply_parameter(controls, parameter, scaled_value)
            applied.append(MidiAppliedControl(cc, value, parameter, scaled_value))
        return applied


def apply_parameter(controls: RuntimeControls, parameter: str, value: float | int) -> None:
    if parameter == "density_fader":
        controls.density_fader = clamp01(float(value))
    elif parameter == "alignment_weight":
        controls.alignment_weight = max(0.0, min(3.0, float(value)))
    elif parameter == "cohesion_weight":
        controls.cohesion_weight = max(0.0, min(3.0, float(value)))
    elif parameter == "separation_weight":
        controls.separation_weight = max(0.0, min(4.0, float(value)))
    elif parameter == "noise_weight":
        controls.noise_weight = max(0.0, min(1.5, float(value)))
    elif parameter == "food_strength":
        controls.food_strength = max(0.0, min(3.0, float(value)))
    elif parameter == "predator_strength":
        controls.predator_strength = max(0.0, min(3.0, float(value)))
    elif parameter == "food_amount":
        controls.food_amount = max(0.0, min(3.0, float(value)))
    elif parameter == "predator_amount":
        controls.predator_amount = max(0.0, min(3.0, float(value)))
    elif parameter == "population":
        controls.population = max(1, min(100, int(value)))
    elif parameter == "section_id":
        controls.section_id = max(0, min(5, int(value)))
