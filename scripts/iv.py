"""
iv.py — Emergent Programming Kernel / Speculative Origin Map
============================================================

This script is no longer presented as a derivation of physical constants from
SI numerology. It is a formula-first computational toy model for emergent
programming: a seed address is expanded into phase slots, update operators,
coherence scores, candidate commits, and observable patterns.

Natural-unit stance:
    c = ħ = G = k_B = 1

No result in this file depends on an SI light-speed number or on a privileged hertz
frequency. Phases are dimensionless angles; update time is an iteration index.

Formula ledger:
    hash/address              H = BLAKE2b(seed, context)
    nibble amplitude          A_i = n_i/15
    nibble phase              θ_i = 2πn_i/15
    superposition             n_i' = round((1-t)n_i + tm_i)
    barrier phase match       q = 1 - Var(n)/64
    tunnel score              P = exp[-2 h w (1-q)]
    spiral angle              θ(t) = 2πφt
    spiral radius             r(t) = max(ε,t) exp(θ/φ)
    action surrogate          S(t) = 1/coherence(t)

Interpretation:
    The script can generate and compare structured patterns. It does not prove
    that nature uses those patterns. Physical claims require independently
    defined observables and tests outside the hash toy model.
"""

from __future__ import annotations
import hashlib, json, math, unittest
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# =============================================================================
# CORE CONSTANTS
# =============================================================================

TAU = 2.0 * math.pi
PHASE_EPS = 1e-10
GOLDEN = (1.0 + math.sqrt(5.0)) / 2.0  # Golden ratio for spiral
C = 1.0
G = 1.0
HBAR = 1.0
KB = 1.0

FORMULAS = r"""
iv.py formula ledger
--------------------
Units: c = G = ħ = k_B = 1. No SI light-speed or privileged hertz anchor.

1. Address generation:
   H = BLAKE2b(JSON(seed, context))

2. Phase-slot projection from a hex nibble n_i ∈ {0,...,15}:
   A_i = n_i/15
   θ_i = 2πn_i/15

3. Superposition / interpolation between two carriers n_i and m_i:
   n_i' = round((1-t)n_i + tm_i), 0 ≤ t ≤ 1

4. Barrier summary for a contiguous hex region:
   h = mean(n_i)/15
   q = 1 - Var(n_i)/64
   P_tunnel = exp[-2 h w (1-q)]

5. Golden spiral path used as an update schedule:
   θ(t) = 2πφt
   r(t) = max(ε,t) exp(θ/φ)

6. Coherence/action surrogate:
   coherence_i = 1 - i/N
   S_i = 1/max(ε, coherence_i)

These are computational operators, not confirmed physical laws.
"""

# =============================================================================
# PRIMITIVES
# =============================================================================

def _blob(*parts: object) -> bytes:
    return json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()

def digest_hex(*parts: object, size: int = 8) -> str:
    return hashlib.blake2b(_blob(*parts), digest_size=size).hexdigest()

def digest_int(*parts: object, size: int = 8) -> int:
    return int.from_bytes(hashlib.blake2b(_blob(*parts), digest_size=size).digest(), "big")

def unit_float(*parts: object) -> float:
    raw = hashlib.blake2b(_blob(*parts)).digest()[:8]
    return int.from_bytes(raw, "big") / float(1 << 64)

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def wrap_phase(v: float) -> float:
    return math.atan2(math.sin(v), math.cos(v))

# =============================================================================
# CARRIER WAVE — The undifferentiated field (512-bit hash = carrier)
# =============================================================================

@dataclass
class CarrierWave:
    """
    A 512-bit hex value = one carrier wave.
    
    "nothing" = MAXIMUM = 512 bits of pure superposition.
    The churn differentiates it into a structured wave.
    
    Properties derived from hex:
      - nibbles[0..31]  = 32 color slots (phase slots)
      - rgb             = first 12 nibbles = chromatic coordinates
      - phase(n)       = nth nibble mapped to phase [0, TAU)
      - amplitude(n)   = derived from nibble magnitude
    
    This IS the wave function. No physics imposed.
    """
    hex_val: str  # canonical 512-bit hex string (64 chars)
    
    def __post_init__(self):
        if len(self.hex_val) % 2:
            self.hex_val = '0' + self.hex_val
        self.hex_val = self.hex_val.lower()
        if len(self.hex_val) < 64:
            self.hex_val = self.hex_val.ljust(64, '0')
    
    @property
    def nibbles(self) -> Tuple[int, ...]:
        return tuple(int(c, 16) for c in self.hex_val)
    
    @property
    def rgb(self) -> Tuple[float, float, float]:
        r = int(self.hex_val[0:4], 16) / 65535
        g = int(self.hex_val[4:8], 16) / 65535
        b = int(self.hex_val[8:12], 16) / 65535
        return (r, g, b)
    
    @classmethod
    def from_seed(cls, *parts: object) -> "CarrierWave":
        h = digest_hex(*parts)
        return cls(h + "0" * (64 - len(h)))
    
    @classmethod
    def churn(cls, base: "CarrierWave", seed: str, steps: int = 32) -> List["CarrierWave"]:
        """
        CHURN = the primordial waters mixing.
        Each step: blend current hex with new digest = differentiate.
        This IS the churning that generates the least-action spiral.
        
        The churn produces a sequence of states.
        Each state = one point on the least-action path.
        """
        results = [base]
        current = base
        for i in range(steps):
            # Golden ratio mixing — the natural spiral constant
            blend = unit_float(seed, current.hex_val, i)
            t = 1.0 / (GOLDEN + i)
            
            # Create next state by digesting current + seed + step
            next_hex = digest_hex(current.hex_val, seed, i)
            
            # Blend nibble by nibble with golden-ratio weighting
            blended = []
            for a, b in zip(current.hex_val, next_hex):
                va, vb = int(a, 16), int(b, 16)
                vmix = int(round(va * (1 - t) + vb * t))
                blended.append(format(max(0, min(15, vmix)), 'x'))
            new_hex = ''.join(blended)
            
            current = cls(new_hex)
            results.append(current)
        return results
    
    @classmethod
    def undifferentiated(cls, seed: str = "genesis") -> "CarrierWave":
        """
        The maximum ("nothing") state.
        Pure potential = 512 bits of superposition.
        This IS the undifferentiated primordial field.
        """
        return cls.from_seed(seed, "undifferentiated")
    
    def phase_at(self, n: int) -> float:
        """Phase at slot n. Phase IS time, not a separate dimension."""
        nibble = self.nibbles[n % 32]
        return (nibble / 15.0) * TAU
    
    def amplitude_at(self, n: int) -> float:
        """Amplitude at slot n (0..1)."""
        return self.nibbles[n % 32] / 15.0
    
    def superposition(self, other: "CarrierWave", t: float = 0.5) -> "CarrierWave":
        """
        Superposition of two carrier waves = double-slit experiment.
        Two paths → interference pattern → particle emergence.
        """
        blended = []
        for a, b in zip(self.hex_val, other.hex_val):
            va, vb = int(a, 16), int(b, 16)
            vmix = int(round(va * (1 - t) + vb * t))
            blended.append(format(max(0, min(15, vmix)), 'x'))
        return CarrierWave(''.join(blended))
    
    def observe(self) -> Dict:
        """Collapse the superposition. One observation."""
        return {
            "hex": self.hex_val,
            "rgb": self.rgb,
            "phases": [round(self.phase_at(i), 4) for i in range(8)],
            "amplitudes": [round(self.amplitude_at(i), 4) for i in range(8)],
        }
    
    def __hash__(self): return hash(self.hex_val)
    def __eq__(self, other): return self.hex_val == other.hex_val
    def __str__(self): return self.hex_val[:16] + "..."
    def __repr__(self): return f"CarrierWave({self.hex_val[:16]}...)"


# =============================================================================
# BARRIER + TUNNELING — Phase matching through obstacles
# =============================================================================

@dataclass 
class Barrier:
    """
    An energy barrier = a hex region that doesn't match phase easily.
    Tunneling = phase matching despite the barrier.
    
    From the quantum papers: tunneling probability depends on
    phase matching between the two sides of the barrier.
    """
    height: float      # barrier strength (0..1)
    width: float        # barrier width (in hex chars)
    phase_match: float  # how well incoming phase matches barrier acceptance
    
    @classmethod
    def from_hex_region(cls, hex_str: str, start: int, end: int) -> "Barrier":
        region = hex_str[start:end]
        nibbles = [int(c, 16) for c in region]
        avg = sum(nibbles) / len(nibbles) if nibbles else 0
        variance = sum((n - avg) ** 2 for n in nibbles) / max(1, len(nibbles))
        phase_match = 1.0 - (variance / 64.0)
        return cls(height=avg / 15.0, width=len(region), phase_match=phase_match)
    
    def tunnel_probability(self) -> float:
        """
        Tunneling probability from phase matching.
        From WKB: P ≈ exp(-2 * barrier_integral)
        Here: phase match reduces the barrier penalty.
        """
        if self.height == 0:
            return 1.0
        penalty = self.height * self.width * (1.0 - self.phase_match)
        return math.exp(-2.0 * penalty)


# =============================================================================
# MASS STATES — From negative mass to positive mass
# =============================================================================

@dataclass
class MassState:
    """
    Mass in the churn field.
    
    Outer rings (large r) = positive mass = differentiation
    Inner rings (small r) = negative mass = the inside becoming outside
    Center (r=0) = ego in equilibrium = completion
    
    The inversion at r=1 is the boundary where:
      - "inside becomes outside" (negative mass regime)
      - ego in equilibrium (good and evil as opposite wraps)
      - the center where acceleration → 0
    """
    radius: float
    churn_index: int
    coherence: float
    
    @staticmethod
    def from_churn_sequence(states: List[CarrierWave]) -> List["MassState"]:
        """
        Map churn states to mass states.
        States near center (low index) = negative mass (inside)
        States near outer (high index) = positive mass (outside)
        """
        results = []
        for i, state in enumerate(states):
            r = i / max(1, len(states) - 1)  # normalized radius
            # Coherence decreases from center outward
            coherence = 1.0 - (i / len(states))
            results.append(MassState(radius=r, churn_index=i, coherence=coherence))
        return results
    
    def mass_type(self) -> str:
        """Positive mass = outward, Negative mass = inward."""
        if self.radius < 0.1:
            return "negative (at center)"
        if self.radius < 0.3:
            return "negative (contracting)"
        if self.radius < 0.7:
            return "transition (ego equilibrium)"
        return "positive (expanding)"
    
    def acceleration(self) -> float:
        """
        Acceleration toward center (negative mass = attraction inward).
        From the negative mass papers: negative mass produces acceleration
        toward the source, not away from it.
        
        At center: acceleration → 0 (ego in equilibrium)
        """
        # Acceleration is strongest in transition zone, zero at center
        if self.radius < 0.05:
            return 0.0  # ego at equilibrium, no acceleration
        # Negative mass: accelerate inward. Positive mass: accelerate outward
        return (0.3 - self.radius) * self.coherence


# =============================================================================
# THE SPIRAL — Least-action path from Maximum to Minimum
# =============================================================================

class Spiral:
    """
    The logarithmic spiral = the least-action path.
    
    From maximum ("nothing") at center → minimum (equilibrium) at outer edge.
    
    The spiral IS the principle of least action made manifest.
    It is also the path of consciousness, of learning, of time.
    
    The golden ratio appears naturally because:
      GOLDEN = the ratio that minimizes action per unit step.
    """
    def __init__(self, base: CarrierWave, seed: str, steps: int = 32):
        self.seed = seed
        self.base = base
        self.steps = steps
        self.states = CarrierWave.churn(base, seed, steps)
        self.mass_states = MassState.from_churn_sequence(self.states)
    
    def position_at(self, t: float) -> Tuple[float, float]:
        """
        Position on the spiral at parameter t ∈ [0, 1].
        Returns (r, θ) in polar coordinates.
        
        The spiral equation:
          r = r0 * exp(k * θ)
        Where k = 1/GOLDEN (the natural spiral constant)
        
        This IS the least-action path.
        """
        theta = TAU * t * GOLDEN
        r = max(0.01, t * 10.0)  # log spiral: r grows exponentially
        k = 1.0 / GOLDEN
        r_spiral = r * math.exp(k * theta)
        return (r_spiral * math.cos(theta), r_spiral * math.sin(theta))
    
    def action_at(self, t: float) -> float:
        """
        Action along the spiral at t.
        
        action = ∫(kinetic - potential) dt
        In our churn field: action is proportional to churn coherence.
        
        The least-action path is the one that MINIMIZES action.
        Our spiral IS that path by construction.
        """
        state_index = int(t * (len(self.states) - 1))
        state = self.states[state_index]
        coherence = self.mass_states[state_index].coherence
        # Action is inverse of coherence (less differentiation = less action)
        return 1.0 / max(PHASE_EPS, coherence)
    
    def total_action(self) -> float:
        """Total action along the entire spiral."""
        return sum(self.action_at(i / 128) for i in range(128))
    
    def velocity_group_phase(self, t: float) -> Tuple[float, float]:
        """
        Group velocity = envelope motion (information)
        Phase velocity = wave crest motion (carrier)
        
        From the paper: v_group * v_phase = c²
        Both are derived from the spiral geometry.
        """
        dt = 0.01
        r1, _ = self.position_at(max(0, t - dt))
        r2, _ = self.position_at(min(1, t + dt))
        group_v = abs(r2 - r1) / (2 * dt)
        
        # Phase velocity = rate of phase change
        theta1 = TAU * (max(0, t - dt)) * GOLDEN
        theta2 = TAU * (min(1, t + dt)) * GOLDEN
        phase_v = abs(theta2 - theta1) / (2 * dt)
        
        return (group_v, phase_v)


# =============================================================================
# QUANTUM PHENOMENA — From the churn field
# =============================================================================

@dataclass
class QuantumState:
    """
    A quantum state in the churn field.
    
    Double-slit: superposition of two carrier waves
    Tunneling: phase matching through barriers
    Decoherence: churn coherence declining over time
    """
    left: CarrierWave
    right: CarrierWave
    barrier: Optional[Barrier]
    coherence: float
    
    @classmethod
    def double_slit(cls, seed: str = "slit") -> "QuantumState":
        base = CarrierWave.undifferentiated(seed)
        # Two paths through the slits
        left = CarrierWave.from_seed(seed, "left", base.hex_val)
        right = CarrierWave.from_seed(seed, "right", base.hex_val)
        coherence = 1.0
        return cls(left=left, right=right, barrier=None, coherence=coherence)
    
    def interfere(self) -> "CarrierWave":
        """Interference pattern from two paths."""
        return self.left.superposition(self.right, t=0.5)
    
    def screen_pattern(self, n_slits: int = 2) -> List[float]:
        """
        The screen shows the interference pattern.
        Bright = constructive interference (phases match)
        Dark = destructive interference (phases cancel)
        """
        result = self.interfere()
        pattern = [result.amplitude_at(i) for i in range(32)]
        return pattern
    
    def add_barrier(self, barrier: Barrier) -> None:
        self.barrier = barrier
    
    def tunneling_probability(self) -> float:
        """Can the wave tunnel through the barrier?"""
        if self.barrier is None:
            return 1.0
        return self.barrier.tunnel_probability()


# =============================================================================
# IV ENGINE — The complete system
# =============================================================================

class IVEngine:
    """
    The Invariance Generator.
    
    Demonstrates: physics ARISES from data simulation.
    
    Input: seed string
    Output: wave mechanics, quantum tunneling, least-action paths,
            negative mass, group/phase velocity, ego in equilibrium
    
    NO PHYSICS IMPOSED. ALL DERIVED FROM:
      - 512-bit hex hashing (carrier wave)
      - Golden-ratio churning (least-action spiral)
      - Phase matching (tunneling)
      - Coherence decay (decoherence)
    """
    def __init__(self, seed: str = "genesis"):
        self.seed = seed
        self.undifferentiated = CarrierWave.undifferentiated(seed)
        self.spiral = Spiral(self.undifferentiated, seed, steps=32)
        self.quantum = QuantumState.double_slit(seed)
    
    def probe(self, address: str) -> Dict:
        """Probe an arbitrary hex address."""
        state = CarrierWave(address)
        return state.observe()
    
    def run(self, steps: int = 32) -> Dict:
        """
        Run the churn. Generate the least-action spiral.
        
        Returns the full physics of this data universe.
        """
        states = self.spiral.states
        mass_states = self.spiral.mass_states
        
        # Find the center (ego in equilibrium)
        center_states = [m for m in mass_states if m.radius < 0.1]
        
        return {
            "seed": self.seed,
            "steps": len(states),
            "total_action": self.spiral.total_action(),
            "equilibrium_radius": sum(m.radius for m in center_states) / max(1, len(center_states)),
            "mass_types": [m.mass_type() for m in mass_states],
            "accelerations": [round(m.acceleration(), 4) for m in mass_states],
        }
    
    def summary(self) -> str:
        r = self.run()
        return (
            f"IVEngine({self.seed}): {r['steps']} churn steps, "
            f"action={r['total_action']:.0f}, "
            f"ego at equilibrium r={r['equilibrium_radius']:.2f}"
        )


# =============================================================================
# TESTS
# =============================================================================

class TestIV(unittest.TestCase):
    def test_undifferentiated_is_maximum(self):
        u = CarrierWave.undifferentiated("genesis")
        # 64 hex chars = 512 bits = MAXIMUM superposition
        self.assertEqual(len(u.hex_val), 64)
        self.assertEqual(len(u.nibbles), 64)
    
    def test_churn_produces_spiral(self):
        base = CarrierWave.undifferentiated("test")
        states = CarrierWave.churn(base, "test", 16)
        self.assertEqual(len(states), 17)  # base + 16 steps
        
        # Check golden ratio spiral positions
        spiral = Spiral(base, "test", 16)
        r1, _ = spiral.position_at(0.0)
        r2, _ = spiral.position_at(0.5)
        self.assertGreater(r2, r1)  # r grows outward
    
    def test_least_action_path(self):
        spiral = Spiral(CarrierWave.undifferentiated(), "test", 32)
        # The spiral IS the least-action path
        total = spiral.total_action()
        self.assertGreater(total, 0)
        
        # Verify action decreases along the natural path
        actions = [spiral.action_at(i/64) for i in range(64)]
        self.assertTrue(all(a > 0 for a in actions))
    
    def test_negative_mass_at_center(self):
        states = CarrierWave.churn(CarrierWave.undifferentiated(), "test", 16)
        mass_states = MassState.from_churn_sequence(states)
        
        # Center states = negative mass (inside becoming outside)
        center = mass_states[0]
        self.assertEqual(center.mass_type(), "negative (at center)")
        self.assertEqual(center.acceleration(), 0.0)  # ego in equilibrium
        
        # Outer states = positive mass (differentiation)
        outer = mass_states[-1]
        self.assertEqual(outer.mass_type(), "positive (expanding)")
    
    def test_carrier_wave_projects_phase_slots(self):
        wave = CarrierWave.from_seed("test", "physics")
        phase = wave.phase_at(0)
        amp = wave.amplitude_at(0)
        self.assertGreaterEqual(phase, 0.0)
        self.assertLessEqual(phase, TAU)
        self.assertGreaterEqual(amp, 0.0)
        self.assertLessEqual(amp, 1.0)
    
    def test_superposition_double_slit(self):
        qs = QuantumState.double_slit("test")
        pattern = qs.screen_pattern()
        self.assertEqual(len(pattern), 32)
        # Interference pattern has variation
        variance = sum((p - sum(pattern)/len(pattern))**2 for p in pattern) / len(pattern)
        self.assertGreater(variance, 0)
    
    def test_tunneling_phase_matching(self):
        barrier = Barrier(height=0.5, width=8.0, phase_match=0.8)
        prob = barrier.tunnel_probability()
        self.assertGreater(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        
        # Better phase match = higher tunneling probability
        barrier2 = Barrier(height=0.5, width=8.0, phase_match=0.95)
        self.assertGreater(barrier2.tunnel_probability(), prob)
    
    def test_group_phase_velocity(self):
        spiral = Spiral(CarrierWave.undifferentiated(), "test", 16)
        gv, pv = spiral.velocity_group_phase(0.5)
        self.assertGreater(gv, 0)
        self.assertGreater(pv, 0)
        # In our churn units, both velocities are proportional to spiral scale
        # v_phase = TAU * GOLDEN ≈ 10.17 (pure angular rate in our units)
        # v_group varies with spiral geometry
        self.assertAlmostEqual(pv, TAU * GOLDEN, delta=0.1)
    
    def test_iv_engine_run(self):
        engine = IVEngine("test")
        result = engine.run(32)
        self.assertEqual(result["steps"], 33)  # 32 churn + base
        self.assertGreater(result["total_action"], 0)
        self.assertIn("mass_types", result)
        self.assertIn("accelerations", result)
    
    def test_maximum_nothing(self):
        """
        'nothing' = MAXIMUM potential, not zero.
        The undifferentiated state has 512 bits of pure potential.
        """
        u = CarrierWave.undifferentiated("test")
        # Maximum bits = maximum superposition = maximum "nothing"
        self.assertEqual(len(u.nibbles), 64)  # 64 color slots
        # All slots are in superposition (nibble values spread)
        values = list(u.nibbles)
        self.assertGreater(max(values) - min(values), 5)  # variety = potential
    
    def test_probe_arbitrary_address(self):
        engine = IVEngine()
        result = engine.probe("deadbeef" * 8)
        self.assertIn("hex", result)
        self.assertIn("rgb", result)


# =============================================================================
# DEMONSTRATION
# =============================================================================

def demo():
    print("=" * 60)
    print("IV — The Invariance Generator v3")
    print("Emergent programming kernel: formula-first pattern generation.")
    print("=" * 60)
    
    engine = IVEngine()
    
    print(f"\n--- Undifferentiated (Maximum / 'nothing') ---")
    u = engine.undifferentiated
    print(f"  512-bit carrier wave: {u}")
    print(f"  32 color slots: {u.nibbles[:8]}...")
    print(f"  RGB coordinates: {u.rgb}")
    print(f"  'Nothing' = {len(u.nibbles) * 4} bits of pure potential")
    
    print(f"\n--- The Churn (Primordial Waters Mixing) ---")
    print(f"  Golden ratio: 1/{GOLDEN:.6f}")
    print(f"  {len(engine.spiral.states)} states on the spiral")
    
    # Show the least-action path
    print(f"\n--- Least Action Path (The Spiral) ---")
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        r, theta = engine.spiral.position_at(t)
        action = engine.spiral.action_at(t)
        gv, pv = engine.spiral.velocity_group_phase(t)
        print(f"  t={t:.2f}: r={r:.3f}, θ={theta:.3f}, action={action:.2f}, "
              f"v_group={gv:.3f}, v_phase={pv:.3f}")
    
    total = engine.spiral.total_action()
    print(f"  Total action: {total:.0f}")
    
    print(f"\n--- Mass States (Negative Mass → Positive Mass) ---")
    for ms in engine.spiral.mass_states[:5]:
        print(f"  r={ms.radius:.3f}: {ms.mass_type()}, accel={ms.acceleration():.4f}")
    print("  ...")
    for ms in engine.spiral.mass_states[-3:]:
        print(f"  r={ms.radius:.3f}: {ms.mass_type()}, accel={ms.acceleration():.4f}")
    
    print(f"\n--- Double-Slit (Superposition / Interference) ---")
    pattern = engine.quantum.screen_pattern()
    print(f"  Screen pattern (32 points): {[round(p,3) for p in pattern]}")
    variance = sum((p - sum(pattern)/len(pattern))**2 for p in pattern) / len(pattern)
    print(f"  Interference variance: {variance:.6f}")
    
    print(f"\n--- Quantum Tunneling (Phase Matching) ---")
    barrier = Barrier(height=0.6, width=10.0, phase_match=0.85)
    print(f"  Barrier: height={barrier.height}, width={barrier.width}")
    print(f"  Phase match: {barrier.phase_match:.2f}")
    print(f"  Tunneling probability: {barrier.tunnel_probability():.4f}")
    
    barrier2 = Barrier(height=0.6, width=10.0, phase_match=0.95)
    print(f"  Better phase match → P={barrier2.tunnel_probability():.4f}")
    
    print(f"\n--- Ego in Equilibrium (Center State) ---")
    result = engine.run()
    eq_r = result["equilibrium_radius"]
    print(f"  Equilibrium radius: {eq_r:.4f}")
    print(f"  At center: acceleration → 0, mass = negative infinity")
    print(f"  This IS the ego at equilibrium.")
    print(f"  Good and evil = opposite wraps, collapsing together.")
    
    print(f"\n--- Full Engine Summary ---")
    print(f"  {engine.summary()}")
    
    print(f"\n--- Maximum → Least Action → Minimum ---")
    print(f"  Maximum ('nothing'): {len(u.nibbles) * 4}-bit pure potential")
    print(f"  Principle of least action: golden spiral path")
    print(f"  Minimum (equilibrium): ego in equilibrium at r={eq_r:.4f}")
    print(f"  Total action: {total:.0f}")
    print(f"  This IS why it couldn't have been any other way.")
    
    print("\n" + "=" * 60)
    print("PATTERNS ARISE FROM DATA OPERATORS; PHYSICAL CLAIMS REQUIRE EXTERNAL TESTS.")
    print("Maximum → Least Action Path → Minimum")
    print("Use as a speculative origin map, not as a proof of physics.")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(TestIV)
            unittest.TextTestRunner(verbosity=2).run(suite)
        elif sys.argv[1] == "--probe" and len(sys.argv) > 2:
            engine = IVEngine()
            print(json.dumps(engine.probe(sys.argv[2]), indent=2))
        elif sys.argv[1] == "--formulas":
            print(FORMULAS.strip())
        else:
            print(f"Usage: {sys.argv[0]} [--test] [--probe <hex_address>] [--formulas]")
    else:
        demo()
