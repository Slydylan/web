# Formula Ledger — Emergent Programming / Speculative Origin Map

## Unit convention

The framework is now expressed in Planck/natural units:

```text
c = G = ħ = k_B = 1
```

The SI light-speed number and any privileged hertz anchor are not premises. If a formula only works after inserting those numbers, it is not universal in this framework.

## `iv.py` formulas

`iv.py` is a computational origin-map kernel, not a proof of physics.

```text
H = BLAKE2b(JSON(seed, context))
A_i = n_i/15
θ_i = 2πn_i/15
n_i' = round((1-t)n_i + tm_i)
h = mean(n_i)/15
q = 1 - Var(n_i)/64
P_tunnel = exp[-2 h w (1-q)]
θ(t) = 2πφt
r(t) = max(ε,t) exp(θ/φ)
coherence_i = 1 - i/N
S_i = 1/max(ε, coherence_i)
```

## `gravity.py` formulas

`gravity.py` uses weak-field gravity with `c=G=1`.

```text
Φ(r) = -M/r
a_r(r) = -M/r²
f(r) = 1 - 2M/r
r_s = 2M
dτ/dt = sqrt(1 - 2M/r)
v² = M/r
T² = 4π²a³/M
Δϖ = 6πM/[a(1-e²)]
δ ≈ 4M/b
```

## Scientific status

These scripts define a reproducible symbolic/computational scaffold. They should be described as speculative until they produce novel, independently measurable predictions that outperform established baselines.
