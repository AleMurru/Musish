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
    """Direct MIDI CC input for MIDIMIX -> Python -> Max workflow.

    Uses pygame.midi to avoid adding a new dependency. The device is optional:
    if no MIDI input is available, the project continues with keyboard/mouse and
    Max UDP controls.
    """

    def __init__(
        self,
        device_name: str = "MIDIMIX",
        mapping: dict[int, tuple[str, float, float, bool]] | None = None,
        debug: bool = True,
    ):
        self.device_name = device_name.lower()
        self.mapping = mapping or {}
        self.debug = debug
        self.enabled = False
        self.device_id: int | None = None
        self.device_label = "no MIDI input"
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
            print("[midi] no MIDI input device found; keyboard/Max UDP controls remain active")
            return

        try:
            self._input = pygame_midi.Input(self.device_id)
        except Exception as exc:  # pragma: no cover - hardware dependent
            self.device_label = f"could not open MIDI input {self.device_id}: {exc}"
            print(f"[midi] {self.device_label}")
            return

        self.enabled = True
        print(f"[midi] listening to {self.device_label}")
        if self.debug:
            print("[midi] debug enabled: move MIDIMIX faders to print CC/value")

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
                    return device_id
        if fallback is not None:
            info = pygame_midi.get_device_info(fallback)
            label = info[1].decode(errors="ignore") if isinstance(info[1], bytes) else str(info[1])
            self.device_label = f"{label} [{fallback}] fallback"
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
