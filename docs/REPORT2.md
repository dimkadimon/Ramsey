# Prism-free K-colourings of N×N×N grids — report II

**Problem.** K-colour `[N]³` so that no axis-aligned box `{x₁,x₂}×{y₁,y₂}×{z₁,z₂}`
(all pairs distinct) is monochromatic. Equivalently (Cooper–Fenner–Purewal,
arXiv:0810.3019): lower-bound `N(c,d)`, the least R such that `[R]^d` is
c-*guaranteed*.

## 1. Where the numbers stand

| K | largest verified N | ⇒ bound | best published upper bound |
|---|---|---|---|
| 1 | **1** | `N(1,3) = 2` (exact) | — |
| 2 | **11** | `N(2,3) ≥ 12` | `N(2,3) ≤ 28` (CFP §7 table; `[12,12,28]` is 2-guaranteed) |
| 3 | **23** | `N(3,3) ≥ 24` | `N(3,3) < 5·3⁴ = 405` (CFP Cor 3.6) |
| 4 | **40** | `N(4,3) ≥ 41` | `N(4,3) < 5·4⁴ = 1280` |
| 5 | **44** | `N(5,3) ≥ 45` | `N(5,3) < 5·5⁴ = 3125` |

New this round: **K = 3 improved from 22 to 23** (verified over all
`C(23,2)³ = 16,194,277` boxes). K = 3, N = 24 is out of reach for the current
constructor (best prefix 22/24 over ~30 restarts).

## 2. The run at N = 12 (K = 2) — what happened

Three explicit construction families, all of the form "slice x = base layer shifted":

| family | shift | condition on the base 2-colouring of [N]² | N = 11 | N = 12 |
|---|---|---|---|---|
| (a) cyclic | `c = [(z−x) ∈ T_y]` | row intersections shift-safe (Sidon-type) | ✅ | **UNSAT** |
| (b) single-coordinate | `c = f(y−x, z)` | every row-set `S(c,{z₁,z₂})` is a **Sidon set** in Z_N | ✅ | **UNSAT (proved, 176 s)** |
| (c) diagonal | `c = f(y−x, z−x)` | ≤ 1 monochromatic rectangle per **diagonal orbit** | ✅ | open (hard) |

Family (b) is the weakest of the three (smallest orbits), and its exact condition is
clean: with `d = x₂−x₁` and rows `a = y₁−x₁`, `b = y₂−x₁`, a prism needs
`a, b, a−d, b−d ∈ S(c,{z₁,z₂})`; two 2-subsets are translates iff they have the same
oriented difference, so the construction is prism-free **iff every `S(c,{z₁,z₂})` is
Sidon**. Since a Sidon set in `Z_N` satisfies `|S|(|S|−1) ≤ N−1` while a balanced
2-colouring gives `|S| ≈ N/4`, this family is feasible only for `N ≤ 16` in principle —
and SAT says it is *already impossible at N = 12*.

That is the most informative negative result of this round: the natural algebraic
families all die at 12. It is **not** a proof that `[12]³` is 2-guaranteed — the full
problem is far bigger than these families — but it makes `N(2,3) = 12` a live
possibility.

**Next family to try (concrete, untested): permutations.** Let
`c(x,y,z) = f(π_x(y), z)` with `N` *arbitrary permutations* `π_x` of `[N]` instead of the
`N` cyclic shifts. A prism needs two slices x₁,x₂ with `π_{x₁}(P)`, `π_{x₂}(P)` both
inside some `S(c,{z₁,z₂})` for one actual row-pair `P`. For random data
`P(π(P) ⊆ S) ≈ C(N/4,2)/C(N,2) ≈ 0.045` and there are only N = 12 permutations, so the
expected number of hits per constraint is ≈ 0.55 — comfortably below 1. There is a lot of
slack here; a randomised construction plus local search over permutations is the obvious
next move, and would give `N(2,3) ≥ 13` if it works.

## 3. N(3,3)

Improved to `N(3,3) ≥ 24` via the layer/feature constructor (K = 3, N = 23 in one
restart, verified by brute force). The exact value is out of reach: it needs
`[24]³` **and** `[25]³` … to be proved 2-/3-guaranteed, i.e. genuine UNSAT proofs for
instances far beyond current reach. Best available published bound stays
`N(3,3) < 405`.

## 4. Dimension-raising construction (K = 2, any dimension)

**Lemma.** If `f` is a prism-free 2-colouring of `[N]^m`, then

```
F(x₁,…,x_{m+1}) = f( (x₁−x_{m+1}) mod N , …, (x_m−x_{m+1}) mod N )
```

is a prism-free 2-colouring of `[N]^{m+1}`.

**Proof.** In a box of `[N]^{m+1}`, split the `2^{m+1}` vertices by the last coordinate
into two `m`-boxes `B_u`, `B_v` (same `m`-box, at the two values of `x_{m+1}`). If the box
is monochromatic both `B_u` and `B_v` are monochromatic in the same colour. But `F(·,u)`
and `F(·,v)` are `f` shifted by `u` resp. `v` in every coordinate, and being monochromatic
is shift-invariant, so `B_u` monochromatic already means `f` has a monochromatic `m`-box —
contradiction. ∎

**Consequences.** `N(2,m+1) ≤ N(2,m)`; and the explicit `[11]³` colouring lifts to
`[11]^d` for **every** `d ≥ 3`, so `N(2,d) ≥ 12` for all `d`.

Verified: the lift at `d = 4` was checked exhaustively (all
`C(11,2)⁴ = 9,150,625` 4-boxes, **0** monochromatic, plus a sensitivity check that
reports the single box after a forced monochromatic `2⁴` sub-block); at `d = 5` the lemma
plus 300,000 uniformly random 5-boxes (0 monochromatic).

The same lifting trick applies to the weaker *orbit* condition of family (c), which is
what would let a single base colouring at dimension `m` produce larger `N` at dimension
`m+1`; that is the route to beating these numbers in higher dimensions.

## 5. Is this publishable now?

**As a mathematics paper: no.** Concretely, what would and would not survive refereeing:

* **Would not.** The bounds `N(3,3) ≥ 24`, `N(4,3) ≥ 41`, `N(5,3) ≥ 45` are heuristic
  output sitting two orders of magnitude below the published bounds (405, 1280, 3125);
  they are a table of computer results, not a theorem, and any competent implementation
  reproduces them.
* **Would not.** The negative results (families (a), (b) impossible at N = 12) are
  statements about three specific construction families. Real, but narrow.
* **Might, barely.** The dimension-raising lemma is clean and I have not found it stated
  in this form, but it is elementary enough to be folklore — it is morally the
  "small side means not guaranteed" phenomenon that CFP §4 is built on.
* **Would, if finished.** An exact value of `N(2,3)`: either a 2-colouring of `[12]³`
  together with a proof that `[13]³` is 2-guaranteed, or a proof that `[12]³` is
  2-guaranteed. Named Ramsey-type quantities with exact small values get published; the
  current window is `12 ≤ N(2,3) ≤ 28`.

**Realistic publication routes, in order of effort:**

1. **Short computational note / arXiv (math.CO) + repo**: "computational lower bounds for
   `N(c,3)`, c ≤ 5, via a layer-packing formulation", containing the reformulation
   (monochromatic prism ⟺ two slices sharing a monochromatic rectangle), the constructor,
   the table above, and the dimension-raising lemma. Plausible in a venue that takes
   computational combinatorics (e.g. *Journal of Combinatorial Mathematics*, or an
   *Experimental Mathematics*-style note) — but only after a proper literature check that
   nobody tabulated these already, and with a referee likely asking for exact values.
2. **Aim at the exact value of `N(2,3)`.** The permutation family above is the concrete
   next step; if `[12]³` turns out 2-colourable the window becomes `13 ≤ N(2,3) ≤ 28`, and
   the matching upper bound would then need CFP's Lemma 7.1 machinery re-run for
   `[12]×[12]` at the exact (2,t)-guarantee threshold.
3. **A scaling theorem.** Show a construction giving `N(2,d) ≥ 2^{c·2^d}` for some c > 0,
   or prove `N(2,d)` is bounded — the lemma here gives monotonicity in `d`, which is a
   starting point but the constants are constant, not exponential.

**Bottom line:** not yet a paper. It is a good, honest computational investigation with
one clean lemma, one improved table entry, and one sharpened open question (`N(2,3)`,
currently in `[12,28]`, with the natural constructions provably dead at 12).

## 6. Files

```
prism_colourings.html              visual report of the largest grid per K
prism/results/K{K}_N{N}.json       verified colourings (grid[x][y][z])
prism/results/K2_N11_base2d.json   the 2-D base layer for the K=2 construction
prism/shift_sat.py, shift_run.py   single-coordinate shift family (Sidon condition)  ← new
prism/diag_sat.py, diag_portfolio.py  diagonal-shift family                          ← new
prism/dimraise.py                  dimension-raising lemma + lift + brute-force check ← new
prism/cyclic.py, cyclic_sat.py     cyclic/difference-set family
prism/layer_ls.py, k3_push.py      main constructor (SAT slice + bitmask local search)
prism/core.py, verify.py, stats.py, report.py
```

Reproduce the headline items:

```bash
python3 prism/cyclic.py 11          # K=2, N=11: difference-set construction
python3 prism/shift_run.py 11       # K=2, N=11: Sidon single-shift construction
python3 prism/shift_run.py 12       # K=2, N=12: UNSAT for this family  (~3 min)
python3 prism/dimraise.py prism/results/K2_N11.json   # lift to [11]^4, exhaustive check
python3 prism/verify.py prism/results/K3_N23.json     # 16.2 M boxes, 0 violations
```
