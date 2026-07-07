from __future__ import annotations

import socket

from pythonosc.udp_client import SimpleUDPClient

from .config import BPM, PLAIN_UDP_PORT, ROOT_MIDI, SCALE_INTERVALS
from .controls import RuntimeControls
from .descriptors import DESCRIPTOR_ORDER
from .markov import LAYERS, MusicEvent


def event_to_midi(event: MusicEvent) -> int:
    scale_index = (event.degree + event.chord_degree) % len(SCALE_INTERVALS)
    octave_shift = event.octave * 12
    return int(ROOT_MIDI + SCALE_INTERVALS[scale_index] + octave_shift)


class OscSender:
    def __init__(self, host: str, port: int):
        self.host = host
        self.client = SimpleUDPClient(host, port)
        self.plain_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.plain_target = (host, PLAIN_UDP_PORT)

    def _send_plain(self, label: str, values: list) -> None:
        """Send a Max/FUDI-style UDP message for [netreceive -u 7401].

        This is a compatibility fallback for Max installations without [oscparse].
        Example packet: "direct 0.1 0.2 0.3;\n"
        """
        atoms = " ".join(str(value) for value in values)
        message = f"{label} {atoms};\n" if atoms else f"{label};\n"
        self.plain_socket.sendto(message.encode("utf-8"), self.plain_target)

    def send_descriptors(self, descriptors: dict[str, float]) -> None:
        payload = [float(descriptors.get(key, 0.0)) for key in DESCRIPTOR_ORDER]
        self.client.send_message("/aquarium/descriptors", payload)
        self._send_plain("descriptors", payload)
        for key in DESCRIPTOR_ORDER:
            self.client.send_message(f"/aquarium/descriptor/{key}", float(descriptors.get(key, 0.0)))

    def send_controls(self, controls: RuntimeControls) -> None:
        self.client.send_message("/aquarium/controls", controls.as_list())
        self.client.send_message("/aquarium/section", [controls.section_id, controls.section_name])
        self._send_plain("controls", controls.as_list())
        self._send_plain("section", [controls.section_id, controls.section_name])

    def send_direct_mapping(self, descriptors: dict[str, float], controls: RuntimeControls) -> None:
        payload = [
            descriptors.get("mean_speed", 0.0),
            descriptors.get("energy", 0.0),
            descriptors.get("center_x", 0.5),
            descriptors.get("center_y", 0.5),
            descriptors.get("density", 0.0),
            descriptors.get("spread", 0.0),
            controls.density_fader,
        ]
        self.client.send_message("/aquarium/direct", payload)
        self._send_plain("direct", payload)

    def send_music_event(self, event: MusicEvent) -> None:
        self.client.send_message("/music/event", event.osc_payload())
        self._send_plain("event", event.osc_payload())
        if event.event_type == "note":
            midi_note = event_to_midi(event)
            duration_ms = int(event.duration_beats * 60000 / BPM)
            note_payload = [
                event.event_id,
                event.degree,
                event.octave,
                event.duration_beats,
                event.velocity,
                event.layer_id,
                LAYERS[event.layer_id],
                event.chord_degree,
                event.section_id,
            ]
            midi_payload = [
                event.event_id,
                midi_note,
                event.velocity,
                duration_ms,
                event.layer_id,
                event.section_id,
            ]
            self.client.send_message("/music/note", note_payload)
            self.client.send_message("/music/midi", midi_payload)
            self._send_plain("note", note_payload)
            self._send_plain("midi", midi_payload)
        else:
            rest_payload = [event.event_id, event.duration_beats, event.section_id]
            self.client.send_message("/music/rest", rest_payload)
            self._send_plain("rest", rest_payload)
