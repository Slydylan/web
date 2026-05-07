#!/usr/bin/env python3
"""
planck_units.py — natural-unit declarations for the speculative origin map.

The framework is expressed in Planck/natural units:

    c = ħ = G = k_B = 1

The SI light-speed number is not a premise here. In these units length,
time, mass, energy, and temperature are dimensionless coordinates measured in
Planck units. Any SI conversion belongs outside the theory layer.
"""

from __future__ import annotations

C = 1.0
HBAR = 1.0
G = 1.0
KB = 1.0
TAU = 6.283185307179586
EPS = 1e-12


def require_positive(name: str, value: float) -> float:
    """Validate a strictly positive Planck-unit scalar."""
    if value <= 0:
        raise ValueError(f"{name} must be positive in Planck units; got {value!r}")
    return value
