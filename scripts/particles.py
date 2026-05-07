#!/usr/bin/env python3
"""
particles.py — dimensionless particle-pattern helpers.

Natural units: c = G = ħ = k_B = 1.

This file keeps particle-related formulas explicit without using SI constants as
premises. Numeric SI masses, speeds, and hertz frequencies belong in an external
conversion layer, not in the speculative origin-map kernel.
"""
from __future__ import annotations

import math
import unittest
from dataclasses import dataclass

TAU = 2.0 * math.pi
EPS = 1e-12
C = G = HBAR = KB = 1.0

FORMULAS = r"""
Natural-unit particle formulas
------------------------------
Units: c = G = ħ = k_B = 1.

Photon:
  E = ω
  p = k
  E² = p²
  v_group = dE/dp = 1

Massive mode:
  E² = p² + m²
  E_rest = m
  v_group = p/E
  λ_reduced = 1/p
  λ_Compton = 2π/m

Two-path interference:
  I = I1 + I2 + 2√(I1 I2) cos(Δθ)

Pair-production threshold for a massive particle/antiparticle pair:
  E_γ ≥ 2m
"""


@dataclass
class Mode:
    name: str
    mass: float = 0.0

    def energy(self, momentum: float) -> float:
        """E² = p² + m²."""
        return math.sqrt(momentum * momentum + self.mass * self.mass)

    def group_velocity(self, momentum: float) -> float:
        """v = p/E; equals 1 for a massless nonzero-momentum mode."""
        e = self.energy(momentum)
        return 0.0 if e < EPS else momentum / e

    def phase_velocity(self, momentum: float) -> float:
        """v_phase = E/p."""
        return self.energy(momentum) / max(abs(momentum), EPS)

    def reduced_wavelength(self, momentum: float) -> float:
        """λ_bar = 1/p because ħ=1."""
        return 1.0 / max(abs(momentum), EPS)

    def compton_wavelength(self) -> float:
        """λ_C = 2π/m because ħ=c=1."""
        if self.mass <= EPS:
            return math.inf
        return TAU / self.mass


class Photon(Mode):
    def __init__(self) -> None:
        super().__init__("photon", 0.0)

    def travel_time(self, distance: float, refractive_index: float = 1.0) -> float:
        """In vacuum c=1, so Δτ = distance. A medium uses v=1/n."""
        return distance * refractive_index

    @staticmethod
    def interference(phase_diff: float, i1: float = 1.0, i2: float = 1.0) -> float:
        return i1 + i2 + 2.0 * math.sqrt(i1 * i2) * math.cos(phase_diff)


class Electron(Mode):
    def __init__(self, mass: float = 1.0) -> None:
        super().__init__("electron-pattern", mass)

    def rest_energy(self) -> float:
        return self.mass

    def g_minus_2_placeholder(self, g_factor: float) -> float:
        """Bookkeeping only; not a derivation."""
        return (abs(g_factor) - 2.0) / 2.0


class Phonon(Mode):
    def __init__(self, sound_speed: float = 0.01, gap: float = 0.0) -> None:
        super().__init__("phonon", 0.0)
        self.sound_speed = sound_speed
        self.gap = gap

    def dispersion(self, k: float) -> float:
        """ω² = gap² + (v_s k)²."""
        return math.sqrt(self.gap * self.gap + (self.sound_speed * k) ** 2)


def pair_production_check(photon_energy: float, particle_mass: float = 1.0) -> dict:
    threshold = 2.0 * particle_mass
    return {
        "can_produce": photon_energy >= threshold,
        "threshold": threshold,
        "photon_energy": photon_energy,
        "excess_energy": max(0.0, photon_energy - threshold),
    }


class TestParticles(unittest.TestCase):
    def test_photon_speed(self):
        p = Photon()
        self.assertAlmostEqual(p.group_velocity(1.0), 1.0)
        self.assertAlmostEqual(p.travel_time(10.0), 10.0)

    def test_massive_dispersion(self):
        e = Electron(mass=1.0)
        self.assertAlmostEqual(e.rest_energy(), 1.0)
        self.assertAlmostEqual(e.energy(0.0), 1.0)
        self.assertLess(e.group_velocity(1.0), 1.0)

    def test_compton(self):
        e = Electron(mass=2.0)
        self.assertAlmostEqual(e.compton_wavelength(), math.pi)

    def test_interference(self):
        self.assertAlmostEqual(Photon.interference(0.0), 4.0)
        self.assertAlmostEqual(Photon.interference(math.pi), 0.0, places=6)

    def test_pair_threshold(self):
        self.assertFalse(pair_production_check(1.9, 1.0)["can_produce"])
        self.assertTrue(pair_production_check(2.1, 1.0)["can_produce"])


def demo() -> None:
    print("PARTICLES.PY — natural-unit particle-pattern helpers")
    print("Units: c = G = ħ = k_B = 1")
    print(FORMULAS.strip())
    photon = Photon()
    electron = Electron(mass=1.0)
    print("\nExamples:")
    print(f"  photon E(p=1) = {photon.energy(1):.3f}, v_group = {photon.group_velocity(1):.3f}")
    print(f"  massive E(p=1,m=1) = {electron.energy(1):.3f}, v_group = {electron.group_velocity(1):.3f}")
    print(f"  pair threshold for m=1: {pair_production_check(2.0, 1.0)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestParticles))
    elif len(sys.argv) > 1 and sys.argv[1] == "--formulas":
        print(FORMULAS.strip())
    else:
        demo()
