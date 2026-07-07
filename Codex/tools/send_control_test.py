"""Test Max/MIDIMAX -> Python control input without Max.

Usage:
    1. In one terminal:
       cd Codex
       python main.py

    2. In another terminal:
       cd Codex
       python tools/send_control_test.py

You should see controls changing in the Pygame HUD and in the terminal.
"""
from __future__ import annotations

import socket
import time

HOST = "127.0.0.1"
PORT = 7500
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

messages = [
    "control alignment_weight 2.2;\n",
    "control cohesion_weight 2.4;\n",
    "control separation_weight 0.7;\n",
    "control noise_weight 0.65;\n",
    "control food_amount 1.8;\n",
    "control predator_amount 2.3;\n",
    "control density_fader 0.85;\n",
    "control section_id 3;\n",
]

for msg in messages:
    print("send", msg.strip())
    sock.sendto(msg.encode("utf-8"), (HOST, PORT))
    time.sleep(0.5)

print("Reset to calmer values")
for msg in [
    "control alignment_weight 1.0;\n",
    "control cohesion_weight 0.9;\n",
    "control separation_weight 1.35;\n",
    "control noise_weight 0.18;\n",
    "control food_amount 0.0;\n",
    "control predator_amount 0.0;\n",
    "control density_fader 0.25;\n",
    "control section_id 0;\n",
]:
    print("send", msg.strip())
    sock.sendto(msg.encode("utf-8"), (HOST, PORT))
    time.sleep(0.25)
