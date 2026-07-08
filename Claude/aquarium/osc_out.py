"""Emitter OSC. Rispetta il contratto congelato in config.py.

Puo' funzionare anche "a vuoto" (nessun server in ascolto): l'invio UDP non fallisce.
Con enabled=False stampa a console (utile per debug senza DAW).
"""
from __future__ import annotations

from . import config as C
from .boids import World

try:
    from pythonosc.udp_client import SimpleUDPClient
    _HAS_OSC = True
except ImportError:  # pragma: no cover
    _HAS_OSC = False


class OSCSender:
    def __init__(self, ip=C.OSC_IP, port=C.OSC_PORT, enabled=True, verbose=False):
        self.enabled = enabled and _HAS_OSC
        self.verbose = verbose
        self._client = SimpleUDPClient(ip, port) if self.enabled else None
        self._last_world = None

    def _send(self, addr, args):
        if self.enabled:
            self._client.send_message(addr, args)
        if self.verbose or not self.enabled:
            print(f"OSC {addr} {args}")

    def send_descriptors(self, d: dict):
        for key, addr in C.OSC_DESC.items():
            self._send(addr, float(d[key]))

    def send_events(self, events: list[tuple]):
        for ev in events:
            kind = ev[0]
            if kind == "dart":
                self._send(C.OSC_EV_DART, [ev[1], ev[2], ev[3]])
            elif kind == "turn":
                self._send(C.OSC_EV_TURN, [ev[1], ev[2], ev[3]])
            elif kind == "collision":
                self._send(C.OSC_EV_COLL, [ev[1], ev[2], ev[3]])

    def send_world(self, world: World):
        snapshot = (world.food, world.predator, world.turbulence, world.density)
        if snapshot == self._last_world:
            return
        self._last_world = snapshot
        self._send(C.OSC_WORLD["food"], float(world.food))
        self._send(C.OSC_WORLD["predator"], float(world.predator))
        self._send(C.OSC_WORLD["turbulence"], float(world.turbulence))
        self._send(C.OSC_WORLD["density"], float(world.density))

    def send_music(self, events, chord_change=None):
        """Invia eventi musicali simbolici (note/rest) + eventuale cambio d'accordo."""
        if chord_change is not None:
            self._send(C.OSC_MUSIC_CHORD, int(chord_change))
        for ev in events:
            if ev.kind == "note":
                self._send(C.OSC_MUSIC_NOTE, ev.note_payload())
            else:
                self._send(C.OSC_MUSIC_REST, ev.rest_payload())
