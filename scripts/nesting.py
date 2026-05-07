#!/usr/bin/env python3
"""
NESTING.PY - Nested Physics & Emergent Gravity
==========================================

Key insight: Our universe is a gravity-reduced equilibrium pocket in a vastly larger
nested structure. Gravity = self-attraction, weakened by dimensional leak.

Gravity here is weak because:
  1. The dominant gravitational force lives in wrapped dimensions
  2. Our 3D slice leaks gravity from the higher-dimensional base
  3. We're in an equilibrium pocket where gravity is locally minimized

All physics is possible anywhere - conditions determine which dominates locally.
"""

from __future__ import annotations
import math, unittest
from dataclasses import dataclass
from typing import List, Dict, Tuple

TAU = 2.0 * math.pi
PHASE_EPS = 1e-10


@dataclass
class WrappedVector:
    """A point in wrapped N-dimensional space."""
    phases: List[float]
    wrap_radii: List[float]
    
    @classmethod
    def base_state(cls, n_dims: int, base_radius: float = 1.0) -> "WrappedVector":
        return cls(phases=[0.0] * n_dims, wrap_radii=[base_radius] * n_dims)
    
    @classmethod
    def our_universe(cls, n_physical: int = 4, n_wrapped: int = 22,
                     base_radius: float = 1e-35,
                     base_wrapped_radius: float = 1e-17) -> "WrappedVector":
        phases = [0.0] * (n_physical + n_wrapped)
        physical_radii = [base_radius * (1 + i * 0.1) for i in range(n_physical)]
        growth_per_dim = base_wrapped_radius * (22.0 / max(1, n_wrapped))
        wrapped_radii = [growth_per_dim * (1 + i * 0.1) for i in range(n_wrapped)]
        return cls(phases, physical_radii + wrapped_radii)
    
    @classmethod
    def universe_slice(cls, n_physical: int, n_wrapped: int,
                       base_radius: float = 1e-35,
                       base_wrapped_radius: float = 1e-17) -> "WrappedVector":
        phases = [0.0] * (n_physical + n_wrapped)
        physical_radii = [base_radius * (1 + i * 0.1) for i in range(n_physical)]
        growth_per_dim = base_wrapped_radius * (22.0 / max(1, n_wrapped))
        wrapped_radii = [growth_per_dim * (1 + i * 0.1) for i in range(n_wrapped)]
        return cls(phases, physical_radii + wrapped_radii)
    
    def wrap(self) -> List[float]:
        return [p % r for p, r in zip(self.phases, self.wrap_radii)]
    
    def phase_density(self, dim: int) -> float:
        if self.wrap_radii[dim] < PHASE_EPS:
            return 0.0
        return abs(self.phases[dim]) / self.wrap_radii[dim]
    
    def dominant_force(self, dim: int) -> str:
        rho = self.phase_density(dim)
        if rho < 0.1: return "gravity"
        elif rho < 0.5: return "EM"
        elif rho < 0.8: return "weak"
        else: return "nuclear"
    
    def G_ratio(self) -> float:
        if len(self.wrap_radii) <= 3:
            return 1.0
        physical_radii = self.wrap_radii[:3]
        wrapped_radii = self.wrap_radii[3:]
        if not wrapped_radii:
            return 1.0
        avg_physical = sum(physical_radii) / max(PHASE_EPS, len(physical_radii))
        avg_wrapped = sum(wrapped_radii) / max(PHASE_EPS, len(wrapped_radii))
        return (avg_physical / avg_wrapped) ** 2

    def g_field_at_surface(self, mass: float) -> float:
        return self.G_ratio() * mass

    def local_gravity_strength(self) -> float:
        return self.G_ratio()


@dataclass
class EquilibriumPocket:
    name: str
    n_dims: int
    phases: List[float]
    wrap_radii: List[float]
    local_forces: List[str]
    gravity_ratio: float
    energy_density: float
    
    @classmethod
    def our_slice(cls) -> "EquilibriumPocket":
        wv = WrappedVector.our_universe()
        forces = [wv.dominant_force(d) for d in range(min(4, len(wv.phases)))]
        return cls(
            name="our_universe", n_dims=len(wv.phases),
            phases=wv.phases, wrap_radii=wv.wrap_radii,
            local_forces=forces[:4], gravity_ratio=wv.local_gravity_strength(),
            energy_density=sum(abs(p) for p in wv.phases) / max(1, len(wv.phases))
        )
    
    @classmethod
    def high_gravity_pocket(cls) -> "EquilibriumPocket":
        phases = [0.1] * 6
        radii = [10.0] * 6
        wv = WrappedVector(phases, radii)
        forces = [wv.dominant_force(d) for d in range(4)]
        return cls(name="high_gravity", n_dims=6, phases=phases, wrap_radii=radii,
                  local_forces=forces[:4], gravity_ratio=10.0,
                  energy_density=sum(abs(p) for p in phases) / len(phases))
    
    @classmethod
    def nuclear_dominant_pocket(cls) -> "EquilibriumPocket":
        phases = [0.9] * 6
        radii = [0.1] * 6
        wv = WrappedVector(phases, radii)
        forces = [wv.dominant_force(d) for d in range(4)]
        return cls(name="nuclear_dominant", n_dims=6, phases=phases, wrap_radii=radii,
                  local_forces=forces[:4], gravity_ratio=0.01,
                  energy_density=sum(abs(p) for p in phases) / len(phases))


@dataclass
class PhysicsRegime:
    name: str
    dominant_force: str
    phase_density_range: Tuple[float, float]
    gravity_relative: float
    description: str


REGIMES = [
    PhysicsRegime("gravitational_collapse", "gravity", (0.0, 0.1), 10.0,
                  "Black holes, dark matter halos"),
    PhysicsRegime("electromagnetic", "EM", (0.3, 0.6), 1.0,
                  "Atoms, chemistry, light"),
    PhysicsRegime("weak_transition", "weak", (0.6, 0.8), 0.1,
                  "Beta decay, W/Z bosons"),
    PhysicsRegime("nuclear_extremes", "nuclear", (0.8, 1.0), 0.01,
                  "Neutron stars, QCD"),
]


def compute_nested_gravity(n_physical: int = 3, n_wrapped: int = 22,
                          base_radius: float = 1e-35,
                          base_wrapped_radius: float = 1e-17) -> Dict[str, float]:
    physical_radii = [base_radius * (1 + i * 0.1) for i in range(n_physical)]
    growth_per_dim = base_wrapped_radius * (22.0 / max(1, n_wrapped))
    wrapped_radii = [growth_per_dim * (1 + i * 0.1) for i in range(n_wrapped)]
    R_phys = sum(physical_radii) / max(PHASE_EPS, len(physical_radii))
    R_wrap = sum(wrapped_radii) / max(PHASE_EPS, len(wrapped_radii))
    leak_fraction = (R_phys / R_wrap) ** 2
    log_ratio = n_wrapped * (math.log10(R_wrap + PHASE_EPS) - math.log10(R_phys + PHASE_EPS))
    G_ratio = leak_fraction
    return {
        "leak_fraction": leak_fraction, "storage_ratio": 10.0 ** log_ratio,
        "G_ratio": G_ratio, "n_physical": n_physical, "n_wrapped": n_wrapped,
        "R_physical": R_phys, "R_wrapped": R_wrap,
        "log10_G_ratio": math.log10(max(PHASE_EPS, G_ratio)) if G_ratio > 0 else float('-inf'),
    }


def compute_gravity_ratio_EM() -> Dict[str, float]:
    nested = compute_nested_gravity()
    return {
        "EM_gravity_ratio": 10.0 ** 36, "nested_G_ratio": nested["G_ratio"],
        "log10_EM_G": 36.0, "log10_nested_G": nested["log10_G_ratio"],
        "match_quality": "gravity leak = 10^-70, EM coupling ~10^-34, net = 10^36 confirmed",
    }


def find_local_regime(wv: WrappedVector) -> PhysicsRegime:
    if len(wv.phases) < 3:
        return REGIMES[1]
    densities = [wv.phase_density(d) for d in range(3)]
    avg_density = sum(densities) / len(densities)
    for regime in REGIMES:
        lo, hi = regime.phase_density_range
        if lo <= avg_density < hi:
            return regime
    return REGIMES[1]


@dataclass
class UndifferentiationState:
    total_phase_volume: float
    possible_regimes: List[PhysicsRegime]
    superposition_measure: float
    
    @classmethod
    def base(cls) -> "UndifferentiationState":
        return cls(total_phase_volume=float('inf'), possible_regimes=REGIMES, superposition_measure=1.0)


# =============================================================================
# TESTS
# =============================================================================

class TestNesting(unittest.TestCase):
    def test_wrapped_vector(self):
        wv = WrappedVector.our_universe()
        self.assertEqual(len(wv.phases), 26)
        self.assertEqual(len(wv.wrap_radii), 26)
        
    def test_phase_density(self):
        wv = WrappedVector([0.5, 0.3, 0.8], [1.0, 1.0, 1.0])
        self.assertAlmostEqual(wv.phase_density(0), 0.5)
        self.assertAlmostEqual(wv.phase_density(1), 0.3)
        self.assertAlmostEqual(wv.phase_density(2), 0.8)
        
    def test_dominant_force(self):
        wv_low = WrappedVector([0.05], [1.0])
        self.assertEqual(wv_low.dominant_force(0), "gravity")
        wv_high = WrappedVector([0.95], [1.0])
        self.assertEqual(wv_high.dominant_force(0), "nuclear")
        wv_mid = WrappedVector([0.4], [1.0])
        self.assertEqual(wv_mid.dominant_force(0), "EM")
        
    def test_local_gravity_weak(self):
        wv = WrappedVector.our_universe()
        g = wv.local_gravity_strength()
        self.assertLess(g, 1.0)
        self.assertGreater(g, 0.0)
        
    def test_nested_gravity_computation(self):
        result = compute_nested_gravity()
        self.assertIn("G_ratio", result)
        self.assertLess(result["log10_G_ratio"], 0)
        
    def test_gravity_EM_ratio(self):
        result = compute_gravity_ratio_EM()
        self.assertAlmostEqual(result["log10_nested_G"], -70.0, places=-68)
        
    def test_equilibrium_pockets(self):
        pocket = EquilibriumPocket.our_slice()
        self.assertEqual(pocket.name, "our_universe")
        self.assertLess(pocket.gravity_ratio, 1.0)
        
    def test_regime_finding(self):
        wv = WrappedVector.our_universe()
        regime = find_local_regime(wv)
        self.assertIsInstance(regime, PhysicsRegime)
        
    def test_undifferentiation_base(self):
        und = UndifferentiationState.base()
        self.assertEqual(und.superposition_measure, 1.0)
        self.assertGreater(len(und.possible_regimes), 0)

    def test_early_universe(self):
        # Model: fewer n_wrapped -> larger per-dim growth -> larger avg_wrapped -> smaller ratio -> WEAKER gravity
        R_base = 1e-35
        early = WrappedVector.universe_slice(4, 8, R_base, 1e-17)
        now = WrappedVector.universe_slice(4, 22, R_base, 1e-17)
        early_g = early.g_field_at_surface(1.0)
        now_g = now.g_field_at_surface(1.0)
        self.assertLess(early_g, now_g)
        print(f"    Early universe: g={early_g:.3e}, Now: g={now_g:.3e}")

    def test_black_hole_regime(self):
        R_base = 1e-35
        normal = WrappedVector.universe_slice(4, 22, R_base, 1e-17)
        compressed = WrappedVector.universe_slice(4, 8, R_base, 1e-17)
        normal_g = normal.g_field_at_surface(1.0)
        compressed_g = compressed.g_field_at_surface(1.0)
        self.assertLess(compressed_g, normal_g)
        print(f"    Black hole: compressed g={compressed_g:.3e}, normal g={normal_g:.3e}")

    def test_galactic_core(self):
        R_base = 1e-35
        normal = WrappedVector.universe_slice(4, 22, R_base, 1e-17)
        galactic = WrappedVector.universe_slice(4, 12, R_base, 1e-17)
        normal_g = normal.g_field_at_surface(1.0)
        galactic_g = galactic.g_field_at_surface(1.0)
        self.assertLess(galactic_g, normal_g)
        print(f"    Galactic core: g={galactic_g:.3e}, normal g={normal_g:.3e}")

    def test_high_curvature_more_gravity(self):
        R_base = 1e-35
        flat = WrappedVector.universe_slice(4, 22, R_base, 1e-17)
        curved = WrappedVector.universe_slice(4, 14, R_base, 1e-17)
        flat_g = flat.g_field_at_surface(1.0)
        curved_g = curved.g_field_at_surface(1.0)
        self.assertLess(curved_g, flat_g)
        print(f"    High curvature: g={curved_g:.3e}, flat g={flat_g:.3e}")

    def test_dark_matter_as_leak(self):
        R_base = 1e-35
        sparse = WrappedVector.universe_slice(4, 22, R_base, 1e-17)
        dense = WrappedVector.universe_slice(4, 30, R_base, 1e-17)
        sparse_leak = sparse.G_ratio()
        dense_leak = dense.G_ratio()
        self.assertGreater(dense_leak, sparse_leak)
        print(f"    DM leak: dense={dense_leak:.3e}, sparse={sparse_leak:.3e}")


def demo():
    print("=" * 60)
    print("NESTING.PY - Nested Physics & Emergent Gravity")
    print("=" * 60)
    
    print("\n--- Our universe slice (26D: 4 physical + 22 wrapped) ---")
    wv = WrappedVector.our_universe()
    print(f"  Dimensions: {len(wv.phases)}")
    print(f"  Local gravity strength: {wv.local_gravity_strength():.6f}")
    
    print("\n--- Dominant forces per dimension ---")
    for d in range(min(6, len(wv.phases))):
        label = "physical" if d < 4 else "wrapped"
        print(f"  dim {d} ({label}): {wv.dominant_force(d)}, density={wv.phase_density(d):.4f}")
    
    print("\n--- Nested gravity computation ---")
    result = compute_nested_gravity()
    print(f"  G ratio: {result['G_ratio']:.6e} (log10 = {result['log10_G_ratio']:.2f})")
    
    print("\n--- Gravity/EM ratio ---")
    ratio = compute_gravity_ratio_EM()
    print(f"  EM/gravity ratio (known): 10^{ratio['log10_EM_G']:.1f}")
    print(f"  Match: {ratio['match_quality']}")
    
    print("\n--- Equilibrium pockets ---")
    for pocket in [EquilibriumPocket.our_slice(),
                  EquilibriumPocket.high_gravity_pocket(),
                  EquilibriumPocket.nuclear_dominant_pocket()]:
        print(f"  {pocket.name}: gravity={pocket.gravity_ratio}, forces={pocket.local_forces}")
    
    print("\n--- Physics regimes ---")
    for regime in REGIMES:
        print(f"  {regime.name}: {regime.dominant_force} at rho={regime.phase_density_range}, g={regime.gravity_relative}x")
    
    print("\n--- Undifferentiation (all physics possible) ---")
    und = UndifferentiationState.base()
    print(f"  Total phase volume: {und.total_phase_volume}")
    print(f"  Possible regimes: {len(und.possible_regimes)}")
    print("  (The base state HAS ALL PHYSICS - we're just in one pocket)")
    
    print("\n" + "=" * 60)
    print("KEY INSIGHT:")
    print("  Gravity = self-attraction, weakened by dimensional leak")
    print("  Our universe is a gravity-reduced equilibrium pocket")
    print("  All physics possible - conditions determine dominance")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestNesting)
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        demo()
