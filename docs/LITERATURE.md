# Literature check: has anyone improved bounds for N(c,3)?

**Short answer: not that we can find — and, more importantly, our own claimed improvements
turned out not to be improvements.** This note records what was checked and what it showed,
so that the (weaker) claims in the paper stand on solid ground.

## 1. The state of the art for the cube

Let `N(c,d)` = least R such that every c-colouring of `[R]^d` has a monochromatic box.

Published sources:

* **Cooper, Fenner, Purewal**, *Monochromatic boxes in colored grids*, arXiv:0810.3019
  (2008). Defines c-guaranteed / c-colourable grids, proves `V(c,d) = Theta(c^{2^d-1})`
  for the largest c-colourable volume, bounds the volume of minimal obstructions, and
  studies the case `c=2, d=3` computationally. Note: they define `N(c,d)` themselves, as
  the least R such that `[R]^d` is c-guaranteed.
* **Agnarsson, Doerr, Schoen**, *Coloring t-dimensional m-boxes*, Discrete Math. 226
  (2001) 21–33. Asymptotics for `N(c,d,m)`, valid for large m, including the equilateral
  case.
* **Fenner, Gasarch, Glover, Purewal**, *Rectangle free coloring of grids*,
  arXiv:1005.3750 — the `d = 2` (rectangle) case, exact characterisations for 2 ≤ c ≤ 4.
  Different problem (rectangles, not boxes), included here for context.

No later paper improving `N(c,d)` for boxes was found. The `d=3` computational questions
are treated in the "Three Dimensions and Two Colors" section of CFP and, as far as we can
tell, have not been revisited.

**Terminological trap.** There is an unrelated and actively developed "grid Ramsey
problem" `G(r)` (Milićević, *An improved upper bound for the grid Ramsey problem*,
J. Graph Theory 94 (2020) 509–517): there one r-colours the *edges* of `K_N × K_N` and
looks for a rectangle whose two pairs of opposite edges are monochromatic. That is a
different (bipartite-Ramsey) problem; its bounds do not transfer here. Radziszowski's
*Small Ramsey Numbers* survey does not cover boxes.

## 2. What CFP's own results already imply for the cube

This is the important part, and it invalidated two of our earlier claims.

**(a) The upper bounds are not new.** CFP Lemma 4 gives, for a monotone grid
`[a_1,...,a_d]`, a recursion
`Delta_0 = 1`, `Delta_j = Delta_{j-1}^2 (1 - (c^{2^{j-1}}/Delta_{j-1} - 1)/(a_j - 1))`,
and shows the grid is `(c, M·Delta_d / c^{2^d-1})`-guaranteed when all `Delta_j > 0`,
where `M = prod_i C(a_i,2)`. Evaluating this for the cube `[n]^3` gives:

| c | smallest n with `M·Delta_3/c^4 >= 1` |
|---|---|
| 2 | 22 |
| 3 | 93 |
| 4 | 277 |
| 5 | 657 |
| 6 | 1341 |

These are **exactly** the numbers our independent `C_4`/Zarankiewicz argument produced
(22, 93, 277, 657). So the argument in `UPPER_BOUND.md` is an independent proof of a known
bound, not an improvement. The much weaker closed form quoted in CFP Corollary 3.6,
`N(c,3) < (d+2)c^{2^{d-1}} = 5c^4` (i.e. 80 for c=2), is not the best their machinery gives.

**(b) The c=2 lower bound is also not new.** CFP's Figure 3 records that `[12,12,27]` is
2-colourable (their table is indexed by the first two side lengths and gives the threshold
third side). A box-free colouring of `[12,12,27]` restricts to one of the subgrid `[12]^3`,
so
```
N(2,3) >= 13
```
already follows from published work. Our best explicit 2-colouring is of `[11]^3`
(`N(2,3) >= 12`), so it is *weaker* than the published consequence.

**Therefore the honest current window is `13 <= N(2,3) <= 22`**, and neither end is ours.
The one defensible claim is bookkeeping: the closed-form corollary in the literature gives
only `13 <= N(2,3) < 80`, and evaluating the paper's own Lemma 4 for the cube tightens the
upper end to 22. We make that claim in the paper and attribute it to CFP.

## 3. What survives as (probably) new

* Explicit box-free colourings and hence **lower bounds for `c = 3, 4, 5`**:
  `N(3,3) >= 24`, `N(4,3) >= 41`, `N(5,3) >= 45`. CFP's computational tables cover `c=2`
  only, and their general colourability theorem (Thm. 2) gives only `n <= 4` for `c = 3`.
  We found no tabulated `c >= 3` cube values anywhere. These are easy results with a
  straightforward method; treat them as records, not theorems.
* The layer/"feature packing" formulation and the feature-utilisation measurements.
* The shift-orbit criterion (with the stabiliser condition), the Sidon analysis of the
  single-coordinate family, and the dimension-raising lemma. These are our own, though
  elementary; we make no priority claim.
* The uniform-`c` analysis: four counting routes all giving exponent `2^d/d`, plus the
  box-multiplicity measurements. We found no discussion of the `Theta(2^d)` vs
  `Theta(2^d/d)` gap in this specific form, but the gap itself is presumably well known.

## 4. Errors we made and corrected

Recorded for transparency, since earlier internal notes (kept in this directory) contain
the superseded claims:

1. We first read CFP's Figure 3 as giving `N(2,3) <= 28`. That is wrong: the table bounds
   the *third* side of rectangular grids, and c-guarantee is upward closed, so it says
   nothing about the cube. Correct published consequence: `< 5c^4 = 80`.
2. We then claimed `N(2,3) <= 22` as a new improvement. It is correct but not new — it is
   CFP Lemma 4 evaluated for the cube (§2a).
3. We claimed `N(2,3) >= 12` from our `[11]^3` colouring as the record. It is not; `>= 13`
   is implied by CFP Fig. 3 (§2b).
4. An early local search reported "solutions" for `n = 12` in the shift-vector families
   that were invalid; the missing condition was the stabiliser condition of
   Theorem (criterion) — a rectangle fixed by a non-trivial shift is used by two slices at
   once. Fixed in `code/sv_ls.py`; see `REPORT3.md` §1.

## 5. What a referee would want next

* A literature check in a math library (zbMATH/MathSciNet) for `c-guaranteed` and for
  box/hyperoctahedron Ramsey numbers, which we could only do via open web sources.
* The exact value of `N(2,3)`. The window `[13,22]` is the only one where both ends are
  within reach: the lower end by a non-shift construction (the permutation family is the
  natural candidate), the upper end by improving `Z_2(n)` beyond Kővári–Sós–Turán or by a
  smarter multi-colour convexity argument.
