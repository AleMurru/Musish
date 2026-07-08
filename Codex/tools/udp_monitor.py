"""Monitor Python -> Max fallback messages on UDP 7401.

Use this instead of Max for a quick local test.

Terminal 1:
    cd Codex
    python tools/udp_monitor.py

Terminal 2:
    cd Codex
    python main.py

Optional Terminal 3, without MIDIMIX:
    cd Codex
    python tools/send_demo_control_test.py

Note: this binds UDP 7401, so close Max patches using [netreceive -u 7401]
while running this monitor.
"""
from __future__ import annotations

import socket
import time

HOST = "127.0.0.1"
PORT = 7401

DIRECT_NAMES = ["mean_speed", "energy", "center_x", "center_y", "density", "spread", "density_fader"]
DESCRIPTOR_NAMES = [
    "fish_count",
    "mean_speed",
    "energy",
    "center_x",
    "center_y",
    "spread",
    "density",
    "nearest_distance",
    "direction_coherence",
    "cluster_count",
]
PERFORMANCE_NAMES = ["alignment_chaos", "grain_density", "noise_distortion", "scene_id"]
CLOCK_NAMES = ["kind", "index", "step", "step_in_bar", "beat_in_bar", "bar", "bpm"]
CHORD_NAMES = ["root", "third", "fifth", "chord_degree", "scene_id", "bar"]
NOTE_NAMES = ["voice", "midi_note", "velocity", "duration_ms", "degree", "octave", "layer_id", "scene_id", "chord_degree", "event_id"]
HIT_NAMES = ["voice", "sample_id", "velocity", "duration_ms", "scene_id", "event_id"]


def parse_packet(text: str) -> list[list[str]]:
    messages: list[list[str]] = []
    for raw in text.replace(";", "\n").splitlines():
        line = raw.strip()
        if line:
            messages.append(line.split())
    return messages


def format_named(names: list[str], values: list[str]) -> str:
    out = []
    for name, value in zip(names, values):
        try:
            out.append(f"{name}={float(value):.3f}")
        except ValueError:
            out.append(f"{name}={value}")
    return " | ".join(out)


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(1.0)

    print(f"Listening for Python -> Max plain UDP on {HOST}:{PORT}")
    print("Close Max [netreceive -u 7401] while using this monitor. Ctrl+C to stop.\n")

    last_seen: dict[str, float] = {}
    last_descriptor_print = 0.0
    packet_count = 0
    start = time.time()

    try:
        while True:
            try:
                data, _addr = sock.recvfrom(8192)
            except socket.timeout:
                elapsed = time.time() - start
                print(f"waiting... packets={packet_count} elapsed={elapsed:.1f}s")
                continue

            packet_count += 1
            for parts in parse_packet(data.decode("utf-8", errors="ignore")):
                label, values = parts[0], parts[1:]
                last_seen[label] = time.time()

                if label == "direct":
                    print("direct      " + format_named(DIRECT_NAMES, values))
                elif label == "performance":
                    print("performance " + format_named(PERFORMANCE_NAMES, values))
                elif label == "descriptors":
                    # Print full descriptor set at most once per second: useful for direction_coherence.
                    now = time.time()
                    if now - last_descriptor_print >= 1.0:
                        print("descriptors " + format_named(DESCRIPTOR_NAMES, values))
                        last_descriptor_print = now
                elif label == "clock":
                    # Step clock is frequent: print only beat/bar messages.
                    if values and values[0] in {"beat", "bar"}:
                        print("clock      " + format_named(CLOCK_NAMES, values))
                elif label == "chord":
                    print("chord      " + format_named(CHORD_NAMES, values))
                elif label == "note":
                    print("note       " + format_named(NOTE_NAMES, values))
                elif label == "hit":
                    print("hit        " + format_named(HIT_NAMES, values))
                elif label in {"midi", "rest", "event"}:
                    print(f"{label:<11} {' '.join(values)}")
                else:
                    # Useful for controls/section/debug.
                    print(f"{label:<11} {' '.join(values)}")
    except KeyboardInterrupt:
        print("\nStopped.")
        if last_seen:
            print("Seen labels:", ", ".join(sorted(last_seen)))


if __name__ == "__main__":
    main()
