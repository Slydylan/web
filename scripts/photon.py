#!/usr/bin/env python3
"""
photon.py — carrier-wave toy model in natural units.

Natural units: c = G = ħ = k_B = 1.

Frequencies are angular phase rates per dimensionless tick. No SI hertz anchor
is used in the theory layer.
"""
from __future__ import annotations

import hashlib
import json
import math
import unittest
from dataclasses import dataclass
from typing import List, Tuple

TAU = 2.0 * math.pi
EPS = 1e-12
C = G = HBAR = KB = 1.0

FORMULAS = r"""
photon.py formula ledger
------------------------
Units: c = G = ħ = k_B = 1.

Address:
  H = BLAKE2b(seed, context)

Phase and amplitude:
  A_i = n_i/15
  θ_i = 2πn_i/15

Photon mode:
  E = ω
  p = k
  E² = p²
  v = 1

Two-path superposition:
  ψ = a|0⟩ + b|1⟩
  P_i = |a_i|² / Σ|a_j|²

Interference:
  I = I1 + I2 + 2√(I1I2)cos(Δθ)
"""


def _blob(*parts: object) -> bytes:
    return json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()


def digest_hex(*parts: object, size: int = 32) -> str:
    return hashlib.blake2b(_blob(*parts), digest_size=size).hexdigest()


def wrap_phase(v: float) -> float:
    return math.atan2(math.sin(v), math.cos(v))


@dataclass(frozen=True)
class CarrierWave:
    hex_val: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "hex_val", self.hex_val.lower()[:64].ljust(64, "0"))

    @classmethod
    def from_seed(cls, *parts: object) -> "CarrierWave":
        return cls(digest_hex(*parts))

    @property
    def nibbles(self) -> Tuple[int, ...]:
        return tuple(int(c, 16) for c in self.hex_val)

    def amplitude_at(self, i: int) -> float:
        return self.nibbles[i % len(self.nibbles)] / 15.0

    def phase_at(self, i: int) -> float:
        return TAU * self.amplitude_at(i)

    def phase_match(self, other: "CarrierWave", slots: int = 8) -> float:
        score = 0.0
        for i in range(slots):
            d = abs(wrap_phase(self.phase_at(i) - other.phase_at(i)))
            score += 1.0 - d / math.pi
        return max(0.0, min(1.0, score / slots))


@dataclass
class PhotonState:
    carrier: CarrierWave
    omega: float
    k: float
    helicity: int

    @property
    def energy(self) -> float:
        return self.omega

    @property
    def momentum(self) -> float:
        return self.k

    @property
    def velocity(self) -> float:
        return 1.0

    @classmethod
    def from_carrier(cls, carrier: CarrierWave, mode_index: int = 1) -> "PhotonState":
        omega = max(EPS, abs(wrap_phase(carrier.phase_at(1) - carrier.phase_at(0))))
        k = omega
        helicity = 1 if carrier.nibbles[mode_index % len(carrier.nibbles)] % 2 == 0 else -1
        return cls(carrier, omega, k, helicity)


@dataclass
class Superposition:
    states: List[CarrierWave]
    amplitudes: List[complex]

    @classmethod
    def from_two_paths(cls, a: CarrierWave, b: CarrierWave, phase: float = 0.0) -> "Superposition":
        return cls([a, b], [1.0 + 0j, complex(math.cos(phase), math.sin(phase))])

    def probabilities(self) -> List[float]:
        weights = [abs(a) ** 2 for a in self.amplitudes]
        total = sum(weights) or 1.0
        return [w / total for w in weights]

    def interference_intensity(self, phase_diff: float, i1: float = 1.0, i2: float = 1.0) -> float:
        return i1 + i2 + 2.0 * math.sqrt(i1 * i2) * math.cos(phase_diff)


class TestPhoton(unittest.TestCase):
    def test_photon_state(self):
        p = PhotonState.from_carrier(CarrierWave.from_seed("photon"))
        self.assertGreater(p.energy, 0)
        self.assertEqual(p.velocity, 1.0)

    def test_phase_match(self):
        a = CarrierWave.from_seed("a")
        self.assertAlmostEqual(a.phase_match(a), 1.0)

    def test_superposition_probabilities(self):
        s = Superposition.from_two_paths(CarrierWave.from_seed("a"), CarrierWave.from_seed("b"))
        self.assertEqual(len(s.probabilities()), 2)
        self.assertAlmostEqual(sum(s.probabilities()), 1.0)

    def test_interference(self):
        s = Superposition.from_two_paths(CarrierWave.from_seed("a"), CarrierWave.from_seed("b"))
        self.assertAlmostEqual(s.interference_intensity(0.0), 4.0)
        self.assertAlmostEqual(s.interference_intensity(math.pi), 0.0, places=6)


def demo() -> None:
    print("PHOTON.PY — natural-unit carrier-wave toy")
    print("Units: c = G = ħ = k_B = 1")
    print(FORMULAS.strip())
    cw = CarrierWave.from_seed("light")
    p = PhotonState.from_carrier(cw)
    print("\nExample:")
    print(f"  carrier={cw.hex_val[:16]}...")
    print(f"  omega={p.omega:.6f}, k={p.k:.6f}, E={p.energy:.6f}, v={p.velocity:.1f}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestPhoton))
    elif len(sys.argv) > 1 and sys.argv[1] == "--formulas":
        print(FORMULAS.strip())
    else:
        demo()
