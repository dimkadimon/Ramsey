# Upper bounds for N(c,3): the packing inequality, and N(2,3) ≤ 21

*Supersedes the round-IV version of this file, which claimed the value 22 as new. 22 is
not new: it is exactly what Lemma 4 of Cooper–Fenner–Purewal (SIAM J. Discrete Math. 22
(2008), arXiv:0810.3019) gives for the cube. The value 21 is new.*

## 1. Conventions

`N(c,d)` = the least `R` such that every `c`-colouring of `[R]^d` contains a monochromatic
**box** (2 points per coordinate, so `2^d` vertices, all one colour). So `N(c,d) ≤ m`
means "every `c`-colouring of `[m]^d` has a monochromatic box".

## 2. Features and the packing inequality

A **feature** is a triple `(colour, row-pair {y1,y2}, column-pair {z1,z2})`. Slice `x`
**uses** it when all four cells `(x,y1,z1),(x,y1,z2),(x,y2,z1),(x,y2,z2)` have that colour.

*Fact 1.* A colouring of `[n]^3` has **no** monochromatic box **iff** no feature is used by
two different slices. (The 8 vertices of a box are the two slices' copies of one rectangle.)

Hence a box-free colouring needs the `n` slices to use **pairwise disjoint** features, and
since a slice uses exactly as many features as it has monochromatic rectangles,

```
n * phi_c(n)  <=  c * C(n,2)^2          (P)
```

where `phi_c(n)` = least number of monochromatic axis-parallel rectangles in a
`c`-colouring of `[n]^2`. This is Lemma 15 of CFP in packing language.

## 3. The 2-D bound

Let `k_y` = number of colour-0 cells in row `y`, and for each of the `Np = C(n,2)` column
pairs `j` let `a_j` / `b_j` = number of rows where both cells of `j` are 0 / 1. Then

```
R = sum_j [C(a_j,2) + C(b_j,2)],   sum_j a_j = T0 = sum_y C(k_y,2),
                                   sum_j b_j = T1 = sum_y C(n-k_y,2)
```

Two levels of convexity, both *exact in the integers* (distribute as evenly as possible,
function `mu(T,bins)`):

```
R >= mu(T0,Np) + mu(T1,Np),      T0+T1 >= n * min_k [C(k,2)+C(n-k,2)]
```

## 4. Why n = 21

For `n = 21`: each row contributes `C(k,2)+C(21-k,2) >= 100`, and this is an **even**
number, so either `T0+T1 = 2100` or `T0+T1 >= 2102`.

* If `T0+T1 = 2100`, every row has `k_y ∈ {10,11}`, so `(T0,T1) = (945+10m, 1155-10m)`
  for an integer `m`. Then the minimum is at `m = 10,11`:
  `mu(1045,210) + mu(1055,210) = 2080 + 2125 = 4205`.
* If `T0+T1 >= 2102`, the value is at least `2*mu(1051,210) = 4210`.

So `phi_2(21) >= 4205`. Now (P) with `c=2, n=21` needs

```
21 * 4205 = 88305  <=  2 * C(21,2)^2 = 88200,     false.
```

**Therefore `[21]^3` is 2-uncolorable, i.e. `N(2,3) ≤ 21`.**  Verify with
`python3 code/final_bound.py`.

### Why 21 is the wall (and where the one unit comes from)

The *continuous* form, with `T0 = T1 = 1050`, gives only `phi_2(21) >= 4200`, and
`21 * 4200 = 88200`, **exactly** the number of features available — a perfect packing.
`21 = 4^2+4+1` is a projective-plane order and the extremal Zarankiewicz value
`Z_2(21) = 105 = 5*21` is attained by the plane of order 4. So:

* no refinement *within* the continuous/C4 counting scheme can pass `n = 21`;
* the improvement is precisely an **integrality** effect: `T0 = T1 = 1050` is not
  attainable by an integer row composition, and the least integer excess costs 105
  features out of 88200.

## 5. Other c

The same computation with `c` colours: (P) first fails at `n = 93, 277, 657` for
`c = 3,4,5` — the same thresholds as CFP Lemma 4. So this method improves **only** `c=2`.

| c | least n excluded by (P) | CFP Lemma 4 | improvement |
|---|---|---|---|
| 2 | 21 | 22 | **1** |
| 3 | 93 | 93 | none |
| 4 | 277 | 277 | none |
| 5 | 657 | 657 | none |

## 6. Reproducing CFP itself

`code/cfp_check.py` re-derives CFP's Lemma 4 (their printed form of the `Δ` recursion is
singular at `j=1`; the recurrence used is the one that follows from their own proof),

```
Delta_0 = 1,  Delta_j = Delta_{j-1} * (a_j*Delta_{j-1} - c^{2^{j-1}}) / (a_j - 1)
```

with `[a_1..a_d]` `c`-guaranteed if all `Delta_j > 0` and `M*Delta_d >= c^{2^d-1}`,
`M = prod C(a_i,2)`. This reproduces their cube thresholds `22, 93, 277` for `c=2,3,4`,
and at `d=1,2` gives 4 and 6 (valid but not sharp; the truth is 3 and 5), which is the
expected behaviour of a valid bound.

## 7. Bottom line

```
13 <= N(2,3) <= 21        (was [13,22]; lower bound due to CFP Fig. 3)
24 <= N(3,3) <= 93
41 <= N(4,3) <= 277
45 <= N(5,3) <= 657
```
