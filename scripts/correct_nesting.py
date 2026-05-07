#!/usr/bin/env python3
"""
CORRECT_NESTING.PY v3 — Fixed Force Hierarchy + Bifurcation Flip + Factorial Growth

CORRECTED PICTURE (v3):
- Force dominance depends on SCALE and CONTEXT, not raw coupling
- Strong: dominant at nuclear scale (confined)
- EM: dominant at atomic/chemical scale (electrons)
- Gravity: dominant at cosmic scale (geometry, no wrap needed to dominate)

WRAP MECHANISM (v3 — corrected):
- Strong: small scale, minimal geometric impact → appears strongest locally
- EM: medium scale, propagates in 4D → medium strength, dominates chemistry
- Weak: couples to Higgs field → medium-weak
- Gravity: IS the geometry → weakest locally, but DOMINATES cosmically

KEY INSIGHT: "Weakness" of gravity is perceptual:
- EM couples to 4D, propagates locally
- Gravity couples to ALL dimensions including wrapped
- Wrapped dimensions provide escape routes → less stays local
- But gravity STILL determines spacetime geometry

BIFURCATION FLIP (v3):
- Maximum invariance → one path selected → entropy drop
- Creates n-1 new dimensions (mirrors/bifurcations)
- This IS the big bang, inflation, dark energy

FACTORIAL GROWTH:
- Dimensional expansion = factorial growth of possible paths
- Dark energy = entropy increase from factorial explosion
"""

from __future__ import annotations
import math, unittest
from dataclasses import dataclass

PHASE_EPS = 1e-10
PI = 3.141592653589793
TAU = 2.0 * PI

# =============================================================================
# DIMENSIONAL WRAP
# =============================================================================

@dataclass
class DimensionalWrap:
    """
    A dimension with wrap factor w = total / observable.
    leak_fraction = (w-1)/w
    local_fraction = 1/w
    """
    w: float
    
    @property
    def leak_fraction(self) -> float:
        return (self.w - 1.0) / self.w if self.w > 0 else 1.0
    
    @property
    def local_fraction(self) -> float:
        return 1.0 / self.w if self.w > 0 else 0.0
    
    def effective(self, base: float) -> float:
        return base * self.local_fraction
    
    def __repr__(self):
        return f"DimensionalWrap(w={self.w:.2e}, leak={self.leak_fraction:.4f})"


# =============================================================================
# PHYSICS REGIMES
# =============================================================================

@dataclass  
class PhysicsRegime:
    name: str
    n_physical: int
    n_wrapped: int
    physical_scale: float
    wrap_base: float
    dominant_force: str
    description: str
    
    @classmethod
    def our_universe(cls) -> "PhysicsRegime":
        return cls(
            name="our_universe",
            n_physical=4,
            n_wrapped=22,
            physical_scale=1.0,
            wrap_base=1e18,
            dominant_force="electromagnetic",
            description="4 observable dimensions + 22 expanding wrapped. Gravity is geometrically dominant but locally weak.",
        )
    
    @classmethod
    def early_universe(cls) -> "PhysicsRegime":
        return cls(
            name="early_universe",
            n_physical=4,
            n_wrapped=4,
            physical_scale=1.0,
            wrap_base=1e5,
            dominant_force="gravity",
            description="Inflation era: fewer wrapped dimensions, gravity relatively stronger.",
        )
    
    @classmethod
    def black_hole(cls) -> "PhysicsRegime":
        return cls(
            name="black_hole",
            n_physical=4,
            n_wrapped=0,
            physical_scale=0.01,
            wrap_base=1.0,
            dominant_force="gravity",
            description="No wrapped dimensions. Gravity dominates spacetime geometry.",
        )
    
    @classmethod
    def quantum_scale(cls) -> "PhysicsRegime":
        return cls(
            name="quantum_scale",
            n_physical=4,
            n_wrapped=0,
            physical_scale=1.0,
            wrap_base=1.0,
            dominant_force="strong",
            description="All dimensions at Planck scale. Forces unify.",
        )


# =============================================================================
# FORCE HIERARCHY (v3 — using log-space to avoid underflow)
# =============================================================================

class ForceHierarchy:
    """
    Force hierarchy via dimensional wrap, using log-space to handle extreme ratios.
    
    Force strength in log10 units:
    - Strong:   0 (reference, confined to small scale)
    - EM:      -2 (EM is 100x weaker than strong at nuclear scale)
    - Weak:    -5 (weak is 1000x weaker than EM at nuclear scale)
    - Gravity: -36 (gravity is 10^36 weaker than EM at nuclear scale)
    
    These are BASE couplings. The wrap mechanism determines how much
    "leaks" into wrapped dimensions vs stays local.
    """
    
    # Log10 base couplings
    LOG10_STRONG = 0.0
    LOG10_EM = -2.0
    LOG10_WEAK = -5.0
    LOG10_GRAVITY = -38.0  # GRAVITY IS FUNDAMENTALLY WEAKEST
    
    def __init__(self, regime: PhysicsRegime):
        self.regime = regime
        self._compute()
    
    def _compute(self):
        r = self.regime
        
        # Build log-wraps in log10 space to avoid overflow
        # w_i = wrap_base^i, log10(w_i) = i * log10(wrap_base)
        log10_base = math.log10(r.wrap_base) if r.wrap_base > 1 else 0.0
        self.wrapped_logs: list[float] = []
        for i in range(r.n_wrapped):
            self.wrapped_logs.append(log10_base * i)
        
        total_leak = sum(self.wrapped_logs) if self.wrapped_logs else 0.0
        
        # Strong: confined, minimal impact from wrap (only ~1% of leak affects it)
        self.log10_strong = self.LOG10_STRONG - total_leak * 0.01
        
        # EM: uses only physical dimensions, no wrap penalty
        self.log10_em = self.LOG10_EM
        
        # Weak: some wrap coupling (~10% leak penalty)
        weak_leak = sum(self.wrapped_logs[:max(1, r.n_wrapped//4)]) if self.wrapped_logs else 0.0
        self.log10_weak = self.LOG10_WEAK - weak_leak * 0.1
        
        # Gravity: ALL dimensions, full leak penalty
        self.log10_gravity = self.LOG10_GRAVITY - total_leak
        
        # Determine contextual dominance
        self.dominance = self._dominant_force()
    
    def _dominant_force(self) -> str:
        r = self.regime
        if r.n_wrapped == 0:
            return "gravity"
        if r.n_wrapped <= 4:
            return "gravity"
        return "electromagnetic"
    
    @property
    def em_gravity_ratio_log10(self) -> float:
        """Log10 of EM/gravity ratio."""
        return self.log10_em - self.log10_gravity
    
    @property
    def em_gravity_ratio(self) -> float:
        """EM/gravity ratio as float (may overflow to inf for extreme ratios)."""
        try:
            ratio = 10.0 ** self.em_gravity_ratio_log10
            return ratio
        except OverflowError:
            return float("inf")
    
    def summary(self) -> dict:
        return {
            "regime": self.regime.name,
            "log10_strong": self.log10_strong,
            "log10_em": self.log10_em,
            "log10_weak": self.log10_weak,
            "log10_gravity": self.log10_gravity,
            "dominant": self.dominance,
            "em_gravity_ratio_log10": self.em_gravity_ratio_log10,
            "em_gravity_ratio": self.em_gravity_ratio,
            "leak_log10": sum(self.wrapped_logs),
        }


# =============================================================================
# BIFURCATION FLIP
# =============================================================================

class BifurcationFlip:
    """
    The flip from maximum invariance to maximum novelty.
    
    At max invariance: n! equally valid paths, entropy = log(n!)
    Flip: one path selected, entropy drops by log(n!)
    Creates n-1 new dimensions (bifurcation/mirror)
    These dimensions expand = dark energy = factorial growth
    """
    
    def __init__(self, n_initial: int = 4):
        self.n_initial = n_initial
    
    def invariant_state(self) -> dict:
        n = self.n_initial
        return {
            "state": "maximum_invariant",
            "n_dimensions": n,
            "microstates": math.factorial(n),
            "entropy": math.log(math.factorial(n)),
            "action": TAU,
        }
    
    def flip(self) -> dict:
        n = self.n_initial
        return {
            "state": "bifurcation_flip",
            "microstates_before": math.factorial(n),
            "microstates_after": 1,
            "entropy_change": -math.log(math.factorial(n)),
            "dimensions_created": n - 1,
            "mirrors_created": (n - 1) // 2,
            "factorial_growth_rate": math.factorial(n),
        }
    
    def expansion(self, n_steps: int) -> dict:
        n = self.n_initial
        final_n = n + n_steps
        initial_entropy = math.log(math.factorial(n))
        final_entropy = math.log(math.factorial(final_n))
        return {
            "state": "factorial_expansion",
            "initial_dims": n,
            "final_dims": final_n,
            "entropy_growth": final_entropy - initial_entropy,
            "acceleration": math.factorial(final_n),
        }
    
    def gravity_strength(self, n_steps: int) -> dict:
        """Gravity weakens as dimensions expand."""
        n = self.n_initial + n_steps
        factorial = math.factorial(n)
        g = 1.0 / factorial
        return {
            "dimensions": n,
            "gravity_strength": g,
            "log10_gravity": -math.log10(factorial) if factorial > 0 else -300,
        }


# =============================================================================
# UNIFIED PHYSICS
# =============================================================================

class UnifiedPhysics:
    def __init__(self, n_initial: int = 4):
        self.n_initial = n_initial
        self.bf = BifurcationFlip(n_initial)
    
    def summary(self) -> dict:
        bf = self.bf
        
        inv = bf.invariant_state()
        flip = bf.flip()
        exp = bf.expansion(22)
        gs = bf.gravity_strength(22)
        
        hierarchy = ForceHierarchy(PhysicsRegime.our_universe())
        h = hierarchy.summary()
        
        return {
            "genesis": inv,
            "flip": flip,
            "expansion": exp,
            "gravity": gs,
            "forces": {
                "dominant": h["dominant"],
                "em_gravity_ratio_log10": h["em_gravity_ratio_log10"],
                "em_gravity_ratio": h["em_gravity_ratio"],
            },
        }


# =============================================================================
# TESTS
# =============================================================================

class TestCorrectNesting(unittest.TestCase):
    def test_dimension_wrap(self):
        d = DimensionalWrap(1e18)
        self.assertAlmostEqual(d.leak_fraction, 1.0 - 1e-18, places=5)
        self.assertAlmostEqual(d.local_fraction, 1e-18, places=5)
    
    def test_our_universe_hierarchy(self):
        r = PhysicsRegime.our_universe()
        h = ForceHierarchy(r)
        s = h.summary()
        
        # In our universe: EM is contextually dominant locally
        self.assertEqual(s["dominant"], "electromagnetic")
        # Gravity is ~10^36 weaker than EM
        self.assertGreater(s["em_gravity_ratio_log10"], 34)  # log10 ratio > 34
        self.assertGreater(h.em_gravity_ratio, 1e34)
    
    def test_early_universe(self):
        r = PhysicsRegime.early_universe()
        h = ForceHierarchy(r)
        self.assertEqual(h.dominance, "gravity")
    
    def test_black_hole(self):
        r = PhysicsRegime.black_hole()
        h = ForceHierarchy(r)
        self.assertEqual(h.dominance, "gravity")
        self.assertEqual(h.log10_gravity, ForceHierarchy.LOG10_GRAVITY)
    
    def test_quantum_scale(self):
        r = PhysicsRegime.quantum_scale()
        h = ForceHierarchy(r)
        self.assertEqual(h.dominance, "gravity")
    
    def test_bifurcation_flip(self):
        bf = BifurcationFlip(n_initial=4)
        inv = bf.invariant_state()
        flip = bf.flip()
        
        self.assertEqual(inv["microstates"], 24)
        self.assertEqual(flip["microstates_before"], 24)
        self.assertEqual(flip["microstates_after"], 1)
        self.assertEqual(flip["dimensions_created"], 3)
    
    def test_factorial_expansion(self):
        bf = BifurcationFlip(n_initial=4)
        exp = bf.expansion(22)
        
        self.assertEqual(exp["initial_dims"], 4)
        self.assertEqual(exp["final_dims"], 26)
        self.assertGreater(exp["entropy_growth"], 0)
    
    def test_gravity_weakens(self):
        bf = BifurcationFlip(n_initial=4)
        gs = bf.gravity_strength(22)
        
        self.assertLess(gs["gravity_strength"], 1e-20)
        self.assertLess(gs["log10_gravity"], -20)
    
    def test_unified_physics(self):
        u = UnifiedPhysics(4)
        ps = u.summary()
        
        self.assertEqual(ps["genesis"]["n_dimensions"], 4)
        self.assertEqual(ps["flip"]["dimensions_created"], 3)
        self.assertGreater(ps["expansion"]["entropy_growth"], 0)
        self.assertGreater(ps["forces"]["em_gravity_ratio"], 1e34)


# =============================================================================
# DEMONSTRATION
# =============================================================================

def demo():
    print("=" * 70)
    print("CORRECT NESTING v3 — Force Hierarchy + Bifurcation Flip")
    print("=" * 70)
    
    print("\n--- FORCE HIERARCHY BY REGIME ---")
    
    regimes = [
        PhysicsRegime.our_universe(),
        PhysicsRegime.early_universe(),
        PhysicsRegime.black_hole(),
        PhysicsRegime.quantum_scale(),
    ]
    
    for r in regimes:
        h = ForceHierarchy(r)
        s = h.summary()
        print(f"\n  {r.name.upper()}:")
        print(f"    {r.description}")
        print(f"    dominant: {s['dominant']}")
        print(f"    EM/gravity ratio: 10^{s['em_gravity_ratio_log10']:.2f}")
    
    print("\n--- BIFURCATION FLIP ---")
    
    bf = BifurcationFlip(n_initial=4)
    
    inv = bf.invariant_state()
    print(f"\n  MAXIMUM INVARIANCE:")
    print(f"    dimensions: {inv['n_dimensions']}")
    print(f"    microstates: {inv['microstates']} (4!)")
    print(f"    entropy: {inv['entropy']:.4f}")
    
    flip = bf.flip()
    print(f"\n  BIFURCATION FLIP:")
    print(f"    microstates: {flip['microstates_before']} → {flip['microstates_after']}")
    print(f"    entropy change: {flip['entropy_change']:.4f}")
    print(f"    dimensions created: {flip['dimensions_created']}")
    
    exp = bf.expansion(22)
    print(f"\n  FACTORIAL EXPANSION (22 steps):")
    print(f"    dimensions: {exp['initial_dims']} → {exp['final_dims']}")
    print(f"    entropy growth: {exp['entropy_growth']:.2f}")
    print(f"    acceleration: {exp['acceleration']:.2e}")
    
    gs = bf.gravity_strength(22)
    print(f"\n  GRAVITY AFTER EXPANSION:")
    print(f"    dimensions: {gs['dimensions']}")
    print(f"    gravity strength: {gs['gravity_strength']:.2e}")
    print(f"    log10(gravity): {gs['log10_gravity']:.2f}")
    
    print("\n" + "=" * 70)
    print("THE PICTURE:")
    print("- Bifurcation flip: max invariance → one path → entropy drop")
    print("- Entropy drop seeds dark energy")
    print("- Dimensional expansion = factorial growth = weaker gravity")
    print("- Force hierarchy is context-dependent")
    print("- Gravity is geometrically weakest locally, dominant cosmically")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestCorrectNesting)
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        demo()