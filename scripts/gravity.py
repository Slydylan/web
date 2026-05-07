#!/usr/bin/env python3
"""
gravity.py — weak-field gravity in pure Planck units.

This script no longer uses an SI light-speed constant or a
special frequency anchor. It uses geometrized Planck units:

    c = G = ħ = k_B = 1

All inputs are dimensionless Planck-unit coordinates. Mass is the gravitational
length M = GM_SI/c² expressed in Planck lengths, but inside this file G and c
never appear as numerical conversion factors.

Formula ledger:
    potential(r)            Φ(r) = -M/r
    radial acceleration     a_r  = -M/r²
    Schwarzschild factor    f(r) = 1 - 2M/r
    clock rate              dτ/dt = sqrt(1 - 2M/r)
    circular orbit speed    v² = M/r
    Kepler law              T² = 4π² a³/M
    perihelion advance      Δϖ = 6πM/[a(1-e²)]
    light deflection        δ ≈ 4M/b       weak-field, grazing ray
    horizon radius          r_s = 2M

Interpretation:
    This is a formula-first toy scaffold. Matching known astrophysical values
    requires supplying Planck-unit M, r, a, b values converted externally.
"""
from __future__ import annotations

import math
import unittest
from dataclasses import dataclass, field
from typing import List, Tuple

TAU = 2.0 * math.pi
PI = math.pi
EPS = 1e-12
C = 1.0
G = 1.0
HBAR = 1.0
KB = 1.0

FORMULAS = r"""
Planck-unit gravity formulas used by gravity.py
-----------------------------------------------
Units: c = G = ħ = k_B = 1.

1. Weak-field potential:
   Φ(r) = -M/r

2. Radial acceleration:
   a_r(r) = -M/r²

3. Schwarzschild factor and horizon:
   f(r) = 1 - 2M/r
   r_s = 2M

4. Clock dilation for a static observer outside the horizon:
   dτ/dt = sqrt(1 - 2M/r)

5. Circular orbit speed and Kepler period:
   v² = M/r
   T² = 4π²a³/M

6. First-post-Newtonian perihelion advance:
   Δϖ = 6πM/[a(1-e²)] radians/orbit

7. Weak-field light bending:
   δ ≈ 4M/b radians
"""


def _positive(name: str, value: float) -> float:
    if value <= 0:
        raise ValueError(f"{name} must be positive in Planck units; got {value!r}")
    return value


@dataclass
class PhaseField:
    """Central mass field, with mass/radius in Planck units."""
    mass: float
    radius: float
    phi_0: float = 1.0

    def __post_init__(self) -> None:
        _positive("radius", self.radius)
        if self.mass < 0:
            raise ValueError("mass must be non-negative for this weak-field model")

    @property
    def schwarzschild_radius(self) -> float:
        """r_s = 2M because G=c=1."""
        return 2.0 * self.mass

    def potential(self, r: float) -> float:
        """Φ(r) = -M/r."""
        r = max(_positive("r", r), self.radius, EPS)
        return -self.mass / r

    def schwarzschild_factor(self, r: float) -> float:
        """f(r) = 1 - 2M/r."""
        r = max(_positive("r", r), EPS)
        return 1.0 - (2.0 * self.mass / r)

    def phi(self, r: float) -> float:
        """Compatibility alias: returns the Schwarzschild factor f(r)."""
        return self.schwarzschild_factor(r)

    def gradient(self, r: float) -> float:
        """dΦ/dr = M/r² for Φ = -M/r."""
        r = max(_positive("r", r), self.radius, EPS)
        return self.mass / (r * r)

    def g(self, r: float) -> float:
        """Radial acceleration a_r = -M/r² in c=G=1 units."""
        r = max(_positive("r", r), self.radius, EPS)
        return -self.mass / (r * r)

    def clock_rate(self, r: float) -> float:
        """dτ/dt = sqrt(1 - 2M/r), clamped to 0 at/inside the horizon."""
        f = self.schwarzschild_factor(max(r, self.radius, EPS))
        return math.sqrt(max(0.0, f))


@dataclass
class Body:
    mass: float
    position: Tuple[float, float]
    velocity: Tuple[float, float]

    @property
    def r(self) -> float:
        return math.hypot(self.position[0], self.position[1])

    @property
    def v(self) -> float:
        return math.hypot(self.velocity[0], self.velocity[1])

    def ke(self) -> float:
        return 0.5 * self.mass * self.v**2

    def pe(self, f: PhaseField) -> float:
        return -self.mass * f.mass / max(EPS, self.r)


@dataclass
class Orbit:
    body: Body
    center: Tuple[float, float]
    field: PhaseField
    steps: int = 0
    positions: List[Tuple[float, float]] = field(default_factory=list)
    energies: List[float] = field(default_factory=list)

    @property
    def total_energy(self) -> float:
        return self.body.ke() + self.body.pe(self.field)

    @property
    def radial_distance(self) -> float:
        dx = self.body.position[0] - self.center[0]
        dy = self.body.position[1] - self.center[1]
        return math.hypot(dx, dy)

    def step(self, dt: float = 0.01) -> None:
        """Semi-implicit Euler step for a weak-field orbit."""
        r = self.radial_distance
        if r < EPS:
            return
        g = self.field.g(r)
        dx = self.center[0] - self.body.position[0]
        dy = self.center[1] - self.body.position[1]
        norm = math.hypot(dx, dy) + EPS
        ax = g * dx / norm
        ay = g * dy / norm
        self.body.velocity = (
            self.body.velocity[0] + ax * dt,
            self.body.velocity[1] + ay * dt,
        )
        self.body.position = (
            self.body.position[0] + self.body.velocity[0] * dt,
            self.body.position[1] + self.body.velocity[1] * dt,
        )
        self.steps += 1
        self.positions.append(self.body.position)
        self.energies.append(self.total_energy)

    def precession_per_orbit(self, r1: float, r2: float) -> float:
        """
        Δϖ = 6πM/[a(1-e²)] radians/orbit, with c=G=1.

        r1 and r2 are periapsis/apoapsis in Planck lengths or any consistent
        natural-unit length scale. M must be in the same geometrized units.
        """
        if r1 <= 0 or r2 <= 0:
            return 0.0
        a = 0.5 * (r1 + r2)
        e = abs(r2 - r1) / (r1 + r2)
        return 6.0 * PI * self.field.mass / (a * (1.0 - e * e))

    def energy_conserved(self, tol: float = 0.05) -> bool:
        if len(self.energies) < 2:
            return True
        e0 = self.energies[0]
        e1 = self.energies[-1]
        return abs(e1 - e0) / max(EPS, abs(e0)) < tol


@dataclass
class LightRay:
    position: Tuple[float, float]
    direction: float
    impact_parameter: float = 0.0
    accumulated_bend: float = 0.0

    def weak_field_deflection(self, f: PhaseField, b: float | None = None) -> float:
        """δ ≈ 4M/b in radians."""
        impact = abs(b if b is not None else self.impact_parameter)
        if impact <= EPS:
            x, y = self.position
            impact = max(abs(y), math.hypot(x, y), EPS)
        return 4.0 * f.mass / impact

    def step(self, f: PhaseField, dt: float) -> None:
        """Toy ray march using the local gradient; formula ledger gives analytic δ."""
        x, y = self.position
        r = max(math.hypot(x, y), f.radius, EPS)
        bend = f.gradient(r) * dt
        self.direction += bend
        self.accumulated_bend += abs(bend)
        self.position = (
            x + math.cos(self.direction) * dt,
            y + math.sin(self.direction) * dt,
        )


@dataclass
class Clock:
    rate: float = 1.0
    field: PhaseField | None = None
    radius: float | None = None

    def tick(self, dt_coord: float) -> float:
        if self.field is None or self.field.mass < EPS:
            self.rate = 1.0
            return dt_coord
        r = self.radius if self.radius is not None else max(10.0 * self.field.schwarzschild_radius, self.field.radius)
        self.rate = self.field.clock_rate(r)
        return dt_coord * self.rate

    def time_dilation_factor(self) -> float:
        return self.rate


class TestGravity(unittest.TestCase):
    def test_constants_are_natural_units(self):
        self.assertEqual(C, 1.0)
        self.assertEqual(G, 1.0)

    def test_surface_gravity_unitless(self):
        f = PhaseField(mass=1.0, radius=10.0)
        self.assertAlmostEqual(f.g(10.0), -0.01, places=6)

    def test_schwarzschild_radius(self):
        f = PhaseField(mass=3.0, radius=20.0)
        self.assertAlmostEqual(f.schwarzschild_radius, 6.0)
        self.assertAlmostEqual(f.schwarzschild_factor(12.0), 0.5)

    def test_clock_dilation(self):
        f = PhaseField(mass=1.0, radius=3.0)
        clock = Clock(field=f, radius=10.0)
        dt = clock.tick(1.0)
        self.assertAlmostEqual(dt, math.sqrt(0.8), places=6)

    def test_clock_at_infinity_or_no_mass(self):
        f = PhaseField(mass=0.0, radius=1.0)
        clock = Clock(field=f)
        self.assertAlmostEqual(clock.tick(1.0), 1.0, places=6)

    def test_precession_formula(self):
        orbit = Orbit(
            body=Body(mass=1e-6, position=(20.0, 0.0), velocity=(0.0, math.sqrt(1.0 / 20.0))),
            center=(0.0, 0.0),
            field=PhaseField(mass=1.0, radius=3.0),
        )
        p = orbit.precession_per_orbit(20.0, 30.0)
        expected = 6.0 * PI * 1.0 / (25.0 * (1.0 - 0.2**2))
        self.assertAlmostEqual(p, expected, places=9)

    def test_light_bending_formula(self):
        f = PhaseField(mass=1.0, radius=3.0)
        ray = LightRay(position=(-100.0, 20.0), direction=0.0, impact_parameter=20.0)
        self.assertAlmostEqual(ray.weak_field_deflection(f), 0.2, places=6)

    def test_orbit_stable_short_run(self):
        f = PhaseField(mass=1.0, radius=1.0)
        r = 40.0
        body = Body(mass=1e-6, position=(r, 0.0), velocity=(0.0, math.sqrt(f.mass / r)))
        orbit = Orbit(body, center=(0.0, 0.0), field=f)
        r0 = orbit.radial_distance
        for _ in range(500):
            orbit.step(0.05)
        self.assertLess(abs(orbit.radial_distance - r0) / r0, 0.05)
        self.assertTrue(orbit.energy_conserved(tol=0.05))


def demo() -> None:
    print("=" * 72)
    print("GRAVITY.PY — Planck-unit weak-field gravity")
    print("Units: c = G = ħ = k_B = 1")
    print("=" * 72)

    field = PhaseField(mass=1.0, radius=3.0)
    print("\n1. NATURAL-UNIT DECLARATIONS")
    print(f"   c={C:g}, G={G:g}, ħ={HBAR:g}, k_B={KB:g}")
    print("   No SI light-speed or frequency anchor appears in the equations.")

    r = 10.0
    print("\n2. CENTRAL FIELD")
    print(f"   M={field.mass:g}, r={r:g}")
    print(f"   Φ(r)=-M/r = {field.potential(r):.6f}")
    print(f"   a_r=-M/r² = {field.g(r):.6f}")
    print(f"   r_s=2M = {field.schwarzschild_radius:.6f}")
    print(f"   dτ/dt=sqrt(1-2M/r) = {field.clock_rate(r):.6f}")

    r1, r2 = 20.0, 30.0
    orbit = Orbit(
        body=Body(mass=1e-6, position=(r1, 0.0), velocity=(0.0, math.sqrt(field.mass / r1))),
        center=(0.0, 0.0),
        field=field,
    )
    precession = orbit.precession_per_orbit(r1, r2)
    print("\n3. ORBIT FORMULAS")
    print(f"   v_circular=sqrt(M/r) = {math.sqrt(field.mass/r1):.6f}")
    print(f"   Δϖ=6πM/[a(1-e²)] = {precession:.6f} rad/orbit")

    b = 20.0
    ray = LightRay(position=(-100.0, b), direction=0.0, impact_parameter=b)
    print("\n4. LIGHT BENDING")
    print(f"   δ≈4M/b = {ray.weak_field_deflection(field):.6f} rad")

    print("\n5. FORMULA LEDGER")
    print(FORMULAS.strip())
    print("\n" + "=" * 72)
    print("Status: dimensionless scaffold, not an SI numerology claim.")
    print("=" * 72)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestGravity))
    elif len(sys.argv) > 1 and sys.argv[1] == "--formulas":
        print(FORMULAS.strip())
    else:
        demo()
