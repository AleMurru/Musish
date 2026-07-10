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

    def send_granular(self, descriptors: dict[str, float], controls: RuntimeControls) -> list:
        """Pre-scaled controls ready for the Max granulator (Pan / Density / Noise).

        The Max patch just routes these into the granulator inlets, no scaling needed:
          /gran/pan     float -1..1   (from flock horizontal position)
          /gran/density float 0..100  (probability, from number of fish)
          /gran/nchan   int   1..48   (granular channels, from number of fish)
          /gran/noise   float 0..1    (chaos: agitation + predator + disorder)
        Also sent bundled as /gran and as FUDI "gran ... ;" on 7401.
        """
        center_x = descriptors.get("center_x", 0.5)
        fish = descriptors.get("fish_count", 0.0)
        agitation = descriptors.get("energy", 0.0)
        coherence = descriptors.get("direction_coherence", 0.0)
        predator = controls.predator_amount / 3.0

        pan = center_x * 2.0 - 1.0
        probability = fish * 100.0
        nchan = 1 + round(fish * 47)
        noise = max(0.0, min(1.0, agitation * 1.2 + predator * 0.7 + (1.0 - coherence) * 0.2))

        self.client.send_message("/gran/pan", pan)
        self.client.send_message("/gran/density", probability)
        self.client.send_message("/gran/nchan", nchan)
        self.client.send_message("/gran/noise", noise)
        payload = [pan, probability, nchan, noise]
        self.client.send_message("/gran", payload)
        self._send_plain("gran", payload)
        return payload

    def send_plaud(self, descriptors: dict[str, float]) -> tuple[float, float]:
        """Flock position as a moving point in PLAUD's latent space (for nn~ decode).

        The flock centroid (x, y) navigates the latent space; two more descriptors
        fill the remaining latent dims of the 4-latent model. All centered to -1..1
        (0 = middle of the space). Max/Rafael rescales to the model's latent range.
          /plaud/x        float -1..1   (flock horizontal -> latent dim 0)
          /plaud/y        float -1..1   (flock vertical   -> latent dim 1)
          /plaud/xy       [x y]
          /plaud/latent   [x y z w]     ready 4-vector for [mc.pack~ 4] -> ---final_latents
          /plaud/loudness float 0.6..1.4  (fish_count; partial window, artist keeps final say)
          /plaud/temp     float 0..1      (agitation -> synthesis temperature/chaos)
        """
        x = descriptors.get("center_x", 0.5) * 2.0 - 1.0
        y = descriptors.get("center_y", 0.5) * 2.0 - 1.0
        z = descriptors.get("spread", 0.0) * 2.0 - 1.0
        w = descriptors.get("mean_speed", 0.0) * 2.0 - 1.0
        self.client.send_message("/plaud/x", x)
        self.client.send_message("/plaud/y", y)
        self.client.send_message("/plaud/xy", [x, y])
        self.client.send_message("/plaud/latent", [x, y, z, w])
        self._send_plain("plaud", [x, y, z, w])

        # DSP params driven by the flock (partial windows so the artist keeps control).
        loudness = 0.6 + descriptors.get("fish_count", 0.0) * 0.8       # 0.6..1.4 within PLAUD 0..2
        temp = max(0.0, min(1.0, 0.2 + descriptors.get("energy", 0.0) * 1.3))  # agitation -> chaos
        self.client.send_message("/plaud/loudness", loudness)
        self.client.send_message("/plaud/temp", temp)
        return (x, y)

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
