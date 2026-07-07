from __future__ import annotations

import queue
import socket
import threading
from dataclasses import dataclass

from .controls import RuntimeControls, clamp01


@dataclass
class ControlCommand:
    name: str
    value: str


class ControlReceiver:
    """Plain UDP receiver for Max/MIDIMAX -> Python controls.

    Expected messages from Max, FUDI-style:
        control density_fader 0.75;
        control alignment_weight 1.2;
        control section_id 3;

    Also accepted:
        density_fader 0.75;
    """

    def __init__(self, port: int = 7500, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self.commands: queue.SimpleQueue[ControlCommand] = queue.SimpleQueue()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._socket: socket.socket | None = None

    def start(self) -> None:
        if self._thread is not None:
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        self._socket.settimeout(0.2)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._socket is not None:
            self._socket.close()

    def _run(self) -> None:
        assert self._socket is not None
        while not self._stop.is_set():
            try:
                data, _addr = self._socket.recvfrom(4096)
            except TimeoutError:
                continue
            except OSError:
                break
            text = data.decode("utf-8", errors="ignore")
            for command in parse_control_text(text):
                self.commands.put(command)

    def drain(self, controls: RuntimeControls) -> list[ControlCommand]:
        applied: list[ControlCommand] = []
        while True:
            try:
                command = self.commands.get_nowait()
            except queue.Empty:
                break
            apply_control(command, controls)
            applied.append(command)
        return applied


def parse_control_text(text: str) -> list[ControlCommand]:
    commands: list[ControlCommand] = []
    for raw_line in text.replace(";", "\n").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "control":
            commands.append(ControlCommand(parts[1], parts[2]))
        elif len(parts) >= 2:
            commands.append(ControlCommand(parts[0], parts[1]))
    return commands


def _as_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except ValueError:
        return default


def _as_section(value: str) -> int:
    names = ["intro", "growth", "dense", "chaos", "release", "outro"]
    if value in names:
        return names.index(value)
    return max(0, min(5, int(round(_as_float(value, 0.0)))))


def apply_control(command: ControlCommand, controls: RuntimeControls) -> None:
    name = command.name.strip()
    value = command.value.strip()
    x = _as_float(value)

    if name in {"density", "density_fader", "granularity"}:
        controls.density_fader = clamp01(x)
    elif name in {"alignment", "alignment_weight", "align"}:
        controls.alignment_weight = max(0.0, min(3.0, x))
    elif name in {"cohesion", "cohesion_weight"}:
        controls.cohesion_weight = max(0.0, min(3.0, x))
    elif name in {"separation", "separation_weight", "sep"}:
        controls.separation_weight = max(0.0, min(4.0, x))
    elif name in {"noise", "noise_weight", "turbulence"}:
        controls.noise_weight = max(0.0, min(1.5, x))
    elif name in {"food", "food_amount", "attractor"}:
        controls.food_amount = max(0.0, min(3.0, x))
    elif name in {"food_strength", "mouse_food_strength"}:
        controls.food_strength = max(0.0, min(3.0, x))
    elif name in {"predator", "predator_amount", "repeller"}:
        controls.predator_amount = max(0.0, min(3.0, x))
    elif name in {"predator_strength", "mouse_predator_strength"}:
        controls.predator_strength = max(0.0, min(3.0, x))
    elif name in {"section", "section_id"}:
        controls.section_id = _as_section(value)
    elif name == "paused":
        controls.paused = x >= 0.5
