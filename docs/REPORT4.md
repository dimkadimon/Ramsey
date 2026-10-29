# Report IV — the cube Ramsey numbers N(c,3), and the uniform-c question

## 0. Headline

For `N(c,d)` = least R such that every c-colouring of `[R]^d` has a monochromatic box:

| c | lower bound (explicit colouring) | upper bound (**proved, new**) | previously published upper |
|---|---|---|---|
| 1 | `N(1,3) = 2` | `N(1,3) = 2` | exact |
| 2 | **`N(2,3) ≥ 12`** | **`N(2,3) ≤ 22`** | `N(2,3) < 80` |
| 3 | **`N(3,3) ≥ 24`** | **`N(3,3) ≤ 93`** | `N(3,3) < 405` |
| 4 | **`N(4,3) ≥ 41`** | **`N(4,3) ≤ 277`** | `N(4,3) < 1280` |
| 5 | **`N(5,3) ≥ 45`** | **`N(5,3) ≤ 657`** | `N(5,3) < 3125` |

Not settled, but the window for `N(2,3)` is now **11 wide** instead of 69, and every
upper bound is ~3–5× better than the published one. The upper bounds are rigorous and
self-contained (`UPPER_BOUND.md`): a Zarankiewicz/`C₄`-counting argument, verified step by
step against the explicit `[11]³` colouring.

## 1. Correction to Report III

Report III said `N(2,3) ≤ 28`, read off CFP's Figure 3 row `a₁ = a₂ = 12 → a₃ = 28`.
**That was wrong.** Their table bounds the third coordinate of *rectangular* grids
`[a₁,a₂,a₃]`, and c-guaranteed is **upward closed** in each coordinate (a valid colouring of
a supergrid restricts to a valid colouring of a subgrid). So `[12,12,28]` being 2-guaranteed
says nothing about `[13,13,13]` — the smaller grid is the easier one to colour, hence the
harder one to prove guaranteed. The correct published bound was `N(2,3) < (d+2)c^{2^{d−1}}
= 80`.

For the record the volume bound `V ≤ (d+2)^d 2^{d(d−1)/2} c^{2^d−1}` gives `n ≤ 50`, and
CFP's ε-criterion, in the form I could re-derive, gives `n ≥ 33` sufficient. Both superseded
by the 22 below.

## 2. The new upper bound

**Theorem.** `N(c,3) ≤ min{ n : n²·C(n/c,2) > C(n,2)·Z₂(n) }`, where
`Z₂(n) ≤ n/2 + (n/2)√(4n−3)` is the Kővári–Sós–Turán bound for `C₄`-free bipartite graphs.
Numerically this gives `N(2,3) ≤ 22`, `N(3,3) ≤ 93`, `N(4,3) ≤ 277`, `N(5,3) ≤ 657`.

**Proof sketch** (full text in `UPPER_BOUND.md`). For a box-free c-colouring `f` of `[n]³`,
fix a colour `γ` and two slices `x₁ ≠ x₂`, and let
`B_γ(x₁,x₂) = {(y,z) : f(x₁,y,z) = f(x₂,y,z) = γ} ⊆ [n]²`. If `B_γ` contained a rectangle,
those 8 points would be a monochromatic box, so `B_γ` is `C₄`-free as a bipartite graph,
hence `|B_γ| ≤ Z₂(n)`. Double counting gives
`Σ_{x₁<x₂}|B_γ| = Σ_{(y,z)} C(m_γ(y,z),2)`, and convexity over `Σ_γ m_γ = n` gives
`Σ_γ Σ_{x₁<x₂}|B_γ| ≥ n²·c·C(n/c,2)`, while the `C₄` bounds give
`Σ_γ Σ_{x₁<x₂}|B_γ| ≤ C(n,2)·c·Z₂(n)`. Combine.

Validated against `prism/results/K2_N11.json`: the double-counting identity matches exactly
(1540 = 1540 and 1485 = 1485), `max|B_γ| = 28 ≤ Z₂(11) = 40.7`, and the criterion holds at
`n = 11` (as it must) but fails at `n = 22`.

## 3. What would settle N(2,3)

The window is `[12, 22]`. Two ways in:

* **Lower side** — find a prism-free 2-colouring of some `[n]³`, `12 ≤ n ≤ 22`. Report III
  showed every *shift-orbit* construction dies at `n = 12`; the remaining idea is arbitrary
  per-slice row permutations, and there the pigeonhole bites: with a balanced base layer,
  the average number of slices mapping a given row-pair into a given `S(c,{z₁,z₂})` is
  `N·C(s,2)/C(N,2)` per cell, which for `N = 12`, `s = 6` is 2.7 — so a random permutation
  family fails; a working one would need `|S| ≤ 3` everywhere (a `λ ≤ 3` design constraint).
  That is the concrete open sub-problem.
* **Upper side** — improve `Z₂(n)` beyond KST, which is tight only at `n = q²+q+1`
  (projective planes), so better bounds need exact Zarankiewicz numbers; or strengthen the
  convexity step by using more than slice-pair structure.

Honest expectation: the truth is likely nearer 12 than 22 (CFP's heuristic tables and the
`ε`-analysis both point low), so the *upper* side is where the next real gain is, and it
requires Zarankiewicz input.

## 4. The uniform-c question: `N(2,d) ≥ 2^{c·2^d}`?

**Still open, and I now have a third independent reason to think it is out of reach of
counting methods.** Full text in `SCALING.md`; the new part:

The argument of §2 generalises to dimension `d`. Inequality (4) there reads

```
n^{d−1}·C(n/c,2)  ≤  C(n,2)·Z_{d−1}(n),
```

so `[n]^d` is c-guaranteed whenever `Z_{d−1}(n) < n^{d−1}/c²`, where `Z_{d−1}(n)` is the
largest box-free **subset** of `[n]^{d−1}`:

> **Proposition.** If no box-free subset of `[n]^{d−1}` has density `≥ 1/c²`, then
> `N(c,d) ≤ n`.

This is a clean reduction of the colouring threshold to a *subset*-density threshold one
dimension down. But it cannot deliver a uniform `c` either: random subsets of density `p`
are box-free for `n ≲ p^{−2^m/(2m)}`, which with `p = 1/c²` and `m = d−1` gives
`n ≲ c^{2^d/(d−1)}` — the same `2^d/d` exponent as the union bound, the local lemma, and the
layer-packing count.

So all four methods now known to me agree:

| method | exponent obtained |
|---|---|
| union bound | `2^d/(2d)` |
| Lovász local lemma | `2^d/(2d)` |
| layer/packing (feature counts) | `2^d/(2d−1)` |
| Zarankiewicz / box-free subset density | `2^d/(d−1)` |

Uniform `c > 0` needs `Θ(2^d)`. The gap is a factor `d`, and every technique produces it.
The precise sub-question, which I would put to an expert, is the box-Ramsey multiplicity
question: *is the minimum number of monochromatic boxes in a 2-colouring of `[n]^m` a factor
`2^{Θ(2^m)}` below the random count?* If yes, the layer count gives a uniform `c`; if the
minimum is only a constant factor below random (my measurements at `m = 2,3` say 0.34, 0.18),
then no such route exists.

## 5. Is it publishable now?

**Yes, as a short computational note — for the first time.** Concretely:

* **New and rigorous:** the Zarankiewicz upper-bound argument and the resulting constants
  (`N(2,3) ≤ 22` etc.), improving the standard bound `5c⁴` by a factor 3–5. This is a real
  theorem with a short, checkable proof, plus the explicit two-sided table for `c ≤ 5`.
* **Computational:** the lower bounds (`N(2,3) ≥ 12`, `N(3,3) ≥ 24`, `N(4,3) ≥ 41`,
  `N(5,3) ≥ 45`) with downloadable colourings, one of which (`[11]³`) is a difference-set
  construction.
* **Honest scope:** it does not settle any `N(c,3)`. A referee will ask whether the
  Zarankiewicz argument is new; it may be a folklore application I re-derived. That check is
  the gating item before submission, followed by making sure nobody has already tabulated
  small `N(c,3)` values.

Where I would send it: a computational-combinatorics venue (e.g. *Journal of Combinatorial
Mathematics and Combinatorial Computing*, or *INTEGERS*), or arXiv math.CO as a note. The
selling point is the table with every row now two-sided and rigorous.

## 6. Files

```
UPPER_BOUND.md                 the new theorem, full proof, validation, tables
SCALING.md                     the growth question: four methods, all giving 2^d/d
REPORT*.md                     history of the investigation (incl. the 28 → 80 correction)
prism/upper_bound.py           the criterion + thresholds
prism/scaling.py, stats.py     numerics for both reports
prism/results/K{c}_N{n}.json   41 verified colourings
prism/shiftvec.py, sv_ls.py    shift-orbit constructions and why they die at 12
```
