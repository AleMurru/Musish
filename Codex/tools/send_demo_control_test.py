"""Send demo-v0 controls to Python without a MIDIMIX.

Usage:
    1. In one terminal:
       cd Codex
       python main.py

    2. Optional, in another terminal to inspect outgoing data:
       cd Codex
       python tools/udp_monitor.py

    3. In a third terminal:
       cd Codex
       python tools/send_demo_control_test.py

Expected visual result:
- alignment_chaos 0.0 -> fish become more ordered / same direction
- alignment_chaos 1.0 -> fish become more dispersed and chaotic
- noise_distortion also increases boids turbulence and is sent to Max
"""
from __future__ import annotations

import socket
import time

HOST = "127.0.0.1"
PORT = 7500
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

MESSAGES = [
    ("control alignment_chaos 0.0;\n", 3.0),
    ("control grain_density 0.15;\n", 0.5),
    ("control noise_distortion 0.0;\n", 2.0),
    ("control alignment_chaos 0.5;\n", 2.0),
    ("control grain_density 0.65;\n", 0.5),
    ("control noise_distortion 0.45;\n", 2.0),
    ("control alignment_chaos 1.0;\n", 3.0),
    ("control grain_density 1.0;\n", 0.5),
    ("control noise_distortion 1.0;\n", 3.0),
    ("control food_amount 2.0;\n", 2.0),
    ("control predator_amount 2.0;\n", 2.0),
    ("control scene_id 3;\n", 1.0),
]

RESET = [
    "control alignment_chaos 0.5;\n",
    "control grain_density 0.25;\n",
    "control noise_distortion 0.0;\n",
    "control food_amount 0.0;\n",
    "control predator_amount 0.0;\n",
    "control scene_id 0;\n",
]


def send(message: str) -> None:
    print("send", message.strip())
    sock.sendto(message.encode("utf-8"), (HOST, PORT))


for message, pause in MESSAGES:
    send(message)
    time.sleep(pause)

print("Reset to neutral demo values")
for message in RESET:
    send(message)
    time.sleep(0.25)
