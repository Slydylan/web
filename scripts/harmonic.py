#!/usr/bin/env python3
"""Harmonic.py - Consensus Slices & K-Consensus Physics"""
from __future__ import annotations
import hashlib, json, math, unittest
from dataclasses import dataclass, field
from typing import Dict, List

TAU = 2.0 * math.pi
EPS = 1e-10

def _blob(*parts):
    return json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()

def dig(*parts, size=8):
    return hashlib.blake2b(_blob(parts), digest_size=size).hexdigest()

def uf(*parts):
    r = hashlib.blake2b(_blob(parts)).digest()
    return int.from_bytes(r[:8], "big") / float(1 << 64)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def wp(v):
    return math.atan2(math.sin(v), math.cos(v))


@dataclass
class Slice:
    seed: str
    n: int
    coup: float
    freq: float
    nodes: List[float] = field(default_factory=list)
    _id: str = field(default="")

    def __post_init__(self):
        if not self.nodes:
            self.nodes = [wp(TAU * (uf(self.seed, "n", i) - 0.5)) for i in range(self.n)]
        if not self._id:
            self._id = dig(self.seed, "slice")[:16]

    def step(self, dt=0.01):
        delta = [0.0] * self.n
        for i in range(self.n):
            L = (i - 1) % self.n
            R = (i + 1) % self.n
            delta[i] = self.coup * (wp(self.nodes[L] - self.nodes[i]) + wp(self.nodes[R] - self.nodes[i]))
        self.nodes = [wp(self.nodes[i] + delta[i] * dt) for i in range(self.n)]

    def run(self, steps, dt=0.01):
        h = [list(self.nodes)]
        for _ in range(steps - 1):
            self.step(dt)
            h.append(list(self.nodes))
        return h

    def corr(self, h):
        if not h:
            return {"c": 0, "len": 0, "coh": False}
        n = len(h[0])
        ap2 = sum(p**2 for f in h for p in f) / (len(h) * n)
        if ap2 < EPS:
            return {"c": 0, "len": 0, "coh": False}
        C = []
        for r in range(1, n // 2):
            cr = sum(f[i] * f[(i+r) % n] for f in h for i in range(n)) / (len(h) * n * ap2)
            C.append((r, round(cr, 4)))
        cl = n // 2
        for r, cr in C:
            if cr < 1.0 / math.e:
                cl = r
                break
        return {"c": C[:8], "len": cl, "coh": cl > n // 4}

    def soliton(self, pos, amp):
        if 0 <= pos < self.n:
            self.nodes[pos] = wp(self.nodes[pos] + amp)

    def spec(self):
        n = len(self.nodes)
        O = []
        for k in range(n // 2):
            re = sum(self.nodes[j] * math.cos(TAU * k * j / n) for j in range(n)) / n
            im = sum(self.nodes[j] * math.sin(TAU * k * j / n) for j in range(n)) / n
            O.append(math.sqrt(re*re + im*im))
        return O


@dataclass
class Obs:
    oid: str
    bias: List[float]

    @classmethod
    def mk(cls, oid, n=3):
        return cls(oid, [uf(oid, "b", i) - 0.5 for i in range(n)])

    def see(self, true):
        return [clamp(true[i] + self.bias[i] * 0.1, -1.0, 1.0) for i in range(len(true))]

    def learn(self, consensus, observed, lr=0.05):
        for i in range(min(len(self.bias), len(consensus), len(observed))):
            err = consensus[i] - observed[i]
            self.bias[i] = clamp(self.bias[i] + lr * err, -0.5, 0.5)


@dataclass
class KC:
    k: int
    nd: int
    obs: List[Obs] = field(default_factory=list)
    ch: List[List[float]] = field(default_factory=list)

    def __post_init__(self):
        if not self.obs:
            self.obs = [Obs.mk(f"o{i}", self.nd) for i in range(self.k)]
        if not self.ch:
            self.ch = []

    def med(self, observations):
        if not observations:
            return [0.0] * self.nd
        out = []
        for dim in range(self.nd):
            vals = sorted(o[dim] for o in observations)
            out.append(vals[len(vals) // 2])
        self.ch.append(out)
        return out

    def trial(self, true_state, calibrate=False):
        oo = [ob.see(true_state) for ob in self.obs]
        consensus = self.med(oo)
        if calibrate and len(self.ch) > 1:
            prev = self.ch[-2]
            for ob, ov in zip(self.obs, oo):
                ob.learn(prev, ov)
        err = sum(abs(consensus[i] - true_state[i]) for i in range(len(true_state)))
        return {"t": true_state, "c": consensus, "e": err}

    def run(self, n, calibrate=True):
        results = []
        for i in range(n):
            true = [uf("trial", i, d) - 0.5 for d in range(self.nd)]
            results.append(self.trial(true, calibrate=calibrate and i > 0))
        ae = sum(r["e"] for r in results) / n
        return {"k": self.k, "n": n, "ae": round(ae, 6), "cal": calibrate}


class CP:
    def __init__(self, seed="phi"):
        self.seed = seed
        self.S: Dict[str, Slice] = {}

    def mk(self, name, n=32, c=0.3):
        sl = Slice(seed=name, n=n, coup=c, freq=1e14)
        self.S[sl._id] = sl
        return sl

    def evo(self, sid, steps):
        if sid not in self.S:
            return {"err": "not found"}
        sl = self.S[sid]
        h = sl.run(steps)
        co = sl.corr(h)
        return {"id": sid, "s": steps, "coh": co["coh"], "cl": co["len"]}

    def observe(self, sid, k=3, n=20):
        if sid not in self.S:
            return {"err": "not found"}
        sl = self.S[sid]
        kc = KC(k=k, nd=3)
        h = sl.run(n)
        results = []
        for j, frame in enumerate(h):
            true = [clamp(frame[d] + 0.01 * (uf(j, d) - 0.5), -1.0, 1.0) for d in range(3)]
            results.append(kc.trial(true, calibrate=j > 0))
        ae = sum(r["e"] for r in results) / len(results)
        return {"id": sid, "k": k, "n": n, "ae": round(ae, 6)}


class T(unittest.TestCase):
    def test_slc(self):
        s = Slice("t", 16, 0.3, 1e14)
        self.assertEqual(s.n, 16)

    def test_stp(self):
        s = Slice("t", 8, 0.5, 1e14)
        s.step()
        self.assertIsNotNone(s.nodes)

    def test_cor(self):
        s = Slice("ct", 32, 0.8, 1e14)
        h = s.run(30)
        c = s.corr(h)
        self.assertIn("coh", c)

    def test_sol(self):
        s = Slice("sol", 32, 0.3, 1e14)
        b = s.nodes[16]
        s.soliton(16, 2.0)
        self.assertNotEqual(s.nodes[16], b)

    def test_ob(self):
        o = Obs.mk("to", 3)
        t = [0.5, -0.2, 0.8]
        v = o.see(t)
        self.assertEqual(len(v), 3)
        for i in range(3):
            self.assertLess(abs(v[i] - t[i]), 0.1)

    def test_kc(self):
        kc = KC(3, 3)
        t = [0.5, -0.2, 0.8]
        r = kc.trial(t, calibrate=False)
        self.assertLess(r["e"], 1.0)

    def test_cal(self):
        kc = KC(3, 3)
        res = kc.run(10, calibrate=True)
        self.assertEqual(res["k"], 3)
        self.assertGreater(res["ae"], 0)

    def test_pipe(self):
        cp = CP("pt")
        sl = cp.mk("ps")
        ev = cp.evo(sl._id, 30)
        self.assertIn("coh", ev)
        ob = cp.observe(sl._id, k=3, n=10)
        self.assertIn("ae", ob)


def demo():
    print("=" * 68)
    print("HARMONIC.PY - Consensus Slices & K-Consensus Physics")
    print("=" * 68)

    s = Slice("earth", 32, 0.3, 1e14)
    print(f"Slice: id={s._id[:8]}, nodes={s.n}, coup={s.coup}")
    h = s.run(50)
    co = s.corr(h)
    print(f"Corr: len={co['len']}, coh={co['coh']}")
    print(f"C(r=1..6): {co['c'][:6]}")

    s2 = Slice("sol", 32, 0.4, 1e14)
    print(f"Soliton[16] before={s2.nodes[16]:.4f}")
    s2.soliton(16, 2.0)
    print(f"Soliton[16] after={s2.nodes[16]:.4f}")
    h2 = s2.run(20)
    co2 = s2.corr(h2)
    print(f"After spread: len={co2['len']}, coh={co2['coh']}")

    kc = KC(3, 3)
    r = kc.run(20, calibrate=True)
    print(f"K=3, 20 trials: avg_err={r['ae']}")

    r1 = KC(5, 3).run(20, calibrate=False)
    r2 = KC(5, 3).run(20, calibrate=True)
    print(f"Uncalibrated: {r1['ae']}  Calibrated: {r2['ae']}")

    cp = CP("d")
    sl = cp.mk("a", c=0.5)
    ev = cp.evo(sl._id, 40)
    ob = cp.observe(sl._id, k=3, n=15)
    print(f"Pipeline: coh={ev['coh']}, cl={ev['cl']}, ae={ob['ae']}")

    print("=" * 68)
    print("Key: slice = phase coherence domain (NOT spatial region)")
    print("K=1 trivial, K=2 Bell, K=3 Triad, K=inf = classical")
    print("=" * 68)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(T))
    else:
        demo()
