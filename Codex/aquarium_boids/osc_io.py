from __future__ import annotations

from pythonosc.udp_client import SimpleUDPClient

from .controls import RuntimeControls
from .descriptors import DESCRIPTOR_ORDER
from .markov import LAYERS, MusicEvent


class OscSender:
    def __init__(self, host: str, port: int):
        self.client = SimpleUDPClient(host, port)

    def send_descriptors(self, descriptors: dict[str, float]) -> None:
        payload = [float(descriptors.get(key, 0.0)) for key in DESCRIPTOR_ORDER]
        self.client.send_message("/aquarium/descriptors", payload)
        for key in DESCRIPTOR_ORDER:
            self.client.send_message(f"/aquarium/descriptor/{key}", float(descriptors.get(key, 0.0)))

    def send_controls(self, controls: RuntimeControls) -> None:
        self.client.send_message("/aquarium/controls", controls.as_list())
        self.client.send_message("/aquarium/section", [controls.section_id, controls.section_name])

    def send_direct_mapping(self, descriptors: dict[str, float], controls: RuntimeControls) -> None:
        self.client.send_message(
            "/aquarium/direct",
            [
                descriptors.get("mean_speed", 0.0),
                descriptors.get("energy", 0.0),
                descriptors.get("center_x", 0.5),
                descriptors.get("center_y", 0.5),
                descriptors.get("density", 0.0),
                descriptors.get("spread", 0.0),
                controls.density_fader,
            ],
        )

    def send_music_event(self, event: MusicEvent) -> None:
        self.client.send_message("/music/event", event.osc_payload())
        if event.event_type == "note":
            self.client.send_message(
                "/music/note",
                [
                    event.event_id,
                    event.degree,
                    event.octave,
                    event.duration_beats,
                    event.velocity,
                    event.layer_id,
                    LAYERS[event.layer_id],
                    event.chord_degree,
                    event.section_id,
                ],
            )
        else:
            self.client.send_message("/music/rest", [event.event_id, event.duration_beats, event.section_id])
