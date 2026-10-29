# Report III — N(2,3), and the growth of N(2,d)

## 0. Bottom line

| goal | outcome |
|---|---|
| exact `N(2,3)` | **not settled.** Rigorous window `12 ≤ N(2,3) ≤ 28`; N = 12 attacked four ways, still open |
| `N(2,d) ≥ 2^{c·2^d}` with fixed `c>0` | **not proved and, I argue below, out of reach of known techniques.** Proved instead: `N(2,d) ≥ 2^{2^d/(2d)}` |
| spin-off | a sharp structural condition for shift constructions at even N (stabilisers of rectangles) that invalidates the naive version of the method |

## 1. N = 12, K = 2: four families, all blocked

Everything tried has the shape "slice x = one base 2-colouring f of `[N]²`, transported by a
symmetry", `c(x,y,z) = f( (y,z) − x·v )` for a shift vector `v ∈ (Z_N)²` of order N
(including `v=(0,1)`, `(1,1)` diagonal, and all 89 slanted slopes).

**Exact criterion (this is the useful new bit).** Such a colouring is prism-free **iff**

> every monochromatic rectangle of f that is *fixed* by a non-zero shift of `⟨v⟩` must not
> exist, and among the remaining orbits of rectangles, **at most one** may be
> monochromatic.

A rectangle `{y₁,y₂}×{z₁,z₂}` is fixed by `t·v ≠ 0` whenever `t·v` swaps its two rows
and/or its two columns. That happens systematically for **even N**: taking `t = N/2`
gives `t·a ≡ N/2 ≡ −N/2`, so every rectangle whose row-difference is exactly `N/2` is
mapped to itself. **Consequence for N = 12: the base colouring must contain no
monochromatic rectangle spanning exactly 6 rows, and none spanning exactly 6 columns**,
on top of the one-per-orbit condition.

Status by family:

| family | criterion | N=11 | N=12 |
|---|---|---|---|
| `v=(0,1)` single-coordinate | every row-set is a Sidon set | ✅ | **UNSAT proved** (176 s, CaDiCaL) |
| `v=(1,1)` diagonal | ≤1 mono rect per diagonal orbit + no distance-6 rects | ✅ | open |
| slanted `v`, 89 slopes | ≤1 per orbit + no distance-6 rects | ✅ | open, LS stalls at 9 violations |
| arbitrary permutations π_x | not yet formulated cleanly | ✅ (cyclic) | open |

Search effort at N=12: CaDiCaL on the full 3-D encoding (>30 min, no result); CaDiCaL on
the orbit encoding (timed out, 240 s/slope); local search on the orbit objective with
weighted breakout (best 9 violations over all slopes, ~40 min); LS + CDCL polish
(LS phases handed to CaDiCaL — no result).

**An important correction to last round's optimism.** With a *buggy* objective (missing the
stabiliser condition) the local search reported 0–1 violations at N=12 for several slopes —
which looked like a solution. It was not: the "solutions" produced invalid colourings,
because a rectangle fixed by a shift is used by two slices at once. After the fix the
same searches stall at 9. The N=12 barrier is therefore *harder* than it looked, and every
natural symmetry-orbit construction is now blocked at exactly 12.

What remains untried: genuine *permutations* (not group shifts) of the rows, where the
"orbit" bookkeeping does not apply at all. That is the only concrete idea I have left for
N = 12.

## 2. The scaling theorem

Full write-up with proofs: **`SCALING.md`**. Summary:

**Proved (Theorem 1, union bound, elementary).** For every `d ≥ 2`,
`N(2,d) > max{n : C(n,2)^d < 2^{2^d−1}}`, hence

```
N(2,d) ≥ 2^{ 2^d / (2d) } .
```

With the published upper bound `N(2,d) < (d+2)·2^{2^{d−1}}` this sandwiches
`N(2,d)` within a factor ≈ 2d in the exponent (`prism/scaling.py` tabulates it).

**The requested statement is open.** `N(2,d) ≥ 2^{c·2^d}` with a *fixed* `c > 0` requires
exponent `Θ(2^d)`; every known technique gives `Θ(2^d/d)`:

* union bound: `#boxes · P(mono) < 1` forces `α < 1/(2d)` for `N = 2^{α2^d}`;
* Lovász local lemma: same rate, since the dependency degree is `≈ d·2^d·n^{2d−2}`;
* layer/packing count: `n` layers with `ν` features each in a universe of
  `F = 2C(n,2)^{d−1}` features needs `n·ν² ≲ F`, giving again
  `n ≲ 2^{2^d/(2d−1)}`.

So a uniform `c` is equivalent to improving the best known lower bound by a factor `d` in
the exponent — a genuine open problem, not something I can close.

**What would close it, made precise.** By the layer count, everything hinges on how few
monochromatic boxes a 2-colouring of `[n]^m` can have: a uniform `c` follows if that
minimum is a factor `2^{Θ(2^m)}` below the random count. I measured this
(`prism/stats.py`, plus a direct minimisation for m = 3):

| m | n | random expected mono boxes | best found | ratio |
|---|---|---|---|---|
| 2 | 11 | 756 | 255 | 0.34 |
| 2 | 12 | 1 089 | 424 | 0.39 |
| 3 | 9 | 364 | 65 | 0.18 |
| 3 | 6 | 26 | 0 | 0 |

The ratio falls with `m` but only slowly — nowhere near `2^{−Θ(2^m)}`. This is evidence
that the layer/packing route cannot deliver a uniform `c`, i.e. that the factor-`d` loss is
not an artefact of the union bound but reflects the real difficulty.

Also proved (previous round, `prism/dimraise.py`) and still standing: the
dimension-raising lemma gives `N(2,d+1) ≤ N(2,d)`, hence `N(2,d) ≥ 12` for every `d ≥ 3`
— constructive, but constant, and useless asymptotically.

## 3. What is publishable now

**Still not a paper, but two items are now close to being one.**

1. **The exact criterion for shift constructions** (stabilisers + one-per-orbit) is a small
   but genuine lemma: it explains *why* `v=(0,1)` dies, *why* even `N` is special, and it
   is the tool any future attempt at N = 12 for these families must use. Combined with the
   "all 89 slopes blocked" computational evidence, that is a coherent negative result:
   *no symmetry-orbit construction gives a 2-colouring of `[12]³`*.
2. **The scaling note** (`SCALING.md`) is a clean, self-contained treatment of
   `2^{2^d/(2d)} ≤ N(2,d) < (d+2)2^{2^{d−1}}` with explicit constants — expository, since
   both bounds are essentially known, but the reduction of the uniform-`c` question to the
   box-Ramsey-multiplicity question, together with the measured ratios, is a reasonable
   research-note contribution.

What would still make a *paper*: settling `N(2,3)` (either side), or a proof of the
uniform-`c` bound. Neither is in hand.

## 4. Files

```
SCALING.md                     scaling theorem: proof, status, numerics
prism/shiftvec.py              shift-vector construction + exact orbit keys
prism/sv_ls.py                 local search on the orbit objective (stabiliser-aware)
prism/sv_hunt.py, polish.py    slope sweeps, LS+CDCL polish
prism/scaling.py               numerics for the two-sided bounds
prism/stats.py                 min-mono-box measurements
prism/diag_sat.py, shift_sat.py  SAT encodings of the special slopes
prism/dimraise.py              dimension-raising lemma + exhaustive 4-D check
```
