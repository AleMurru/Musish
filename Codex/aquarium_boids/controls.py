from dataclasses import dataclass


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass
class RuntimeControls:
    density_fader: float = 0.25
    alignment_weight: float = 1.0
    cohesion_weight: float = 0.9
    separation_weight: float = 1.35
    noise_weight: float = 0.18
    section_id: int = 0
    paused: bool = False

    @property
    def section_name(self) -> str:
        return ["intro", "growth", "dense", "chaos", "release", "outro"][self.section_id]

    def as_list(self) -> list[float]:
        return [
            self.density_fader,
            self.alignment_weight,
            self.cohesion_weight,
            self.separation_weight,
            self.noise_weight,
            float(self.section_id),
        ]
