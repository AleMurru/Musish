"""Send test messages to Max fallback patch on UDP 7401.

Usage:
    cd Codex
    python tools/send_max_test.py

Open Max patch:
    max/aquarium_netreceive_sound_v2.maxpat
"""
from __future__ import annotations

import math
import socket
import time

HOST = "127.0.0.1"
PORT = 7401
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Sending test Max/FUDI UDP messages to {HOST}:{PORT}. Ctrl+C to stop.")
start = time.time()
event_id = 0
try:
    while True:
        t = time.time() - start
        speed = 0.5 + 0.5 * math.sin(t * 1.3)
        energy = 0.5 + 0.5 * math.sin(t * 0.8 + 1.0)
        direct = f"direct {speed:.4f} {energy:.4f} 0.5 0.5 0.5 0.5 0.5;\n"
        sock.sendto(direct.encode("utf-8"), (HOST, PORT))
        if int(t * 2) != int((t - 0.05) * 2):
            event_id += 1
            midi_note = 60 + (event_id % 12)
            midi = f"midi {event_id} {midi_note} 90 250 2 1;\n"
            sock.sendto(midi.encode("utf-8"), (HOST, PORT))
        time.sleep(0.05)
except KeyboardInterrupt:
    print("Stopped.")
