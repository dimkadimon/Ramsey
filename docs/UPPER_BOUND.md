# A Zarankiewicz argument for cube grid-Ramsey numbers

**Result.** Write `N(c,d)` for the least R such that every c-colouring of `[R]^d` has a
monochromatic box. Then

```
N(2,3) ≤ 22,   N(3,3) ≤ 93,   N(4,3) ≤ 277,   N(5,3) ≤ 657,
```

against the published bounds `N(c,3) < (d+2)c^{2^{d−1}} = 5c⁴` (Cooper–Fenner–Purewal,
Cor. 3.6), i.e. 80, 405, 1280, 3125. The argument is elementary and self-contained.

## 1. The argument

Let `f : [n]^d → [c]` be a colouring with **no monochromatic box**.

**Step 1 (each pair of slices gives a box-free set).** Fix a colour `γ` and two distinct
slices `x₁ ≠ x₂` (slices = hyperplanes `x₁ = const`). Put

```
B_γ(x₁,x₂) = { (y₂,…,y_d) ∈ [n]^{d−1} : f(x₁,y) = γ = f(x₂,y) }.
```

If `B_γ(x₁,x₂)` contained a `(d−1)`-box, then together with the two slice coordinates that
box would give `2^d` grid points all of colour `γ` — a monochromatic box. Hence:

> `B_γ(x₁,x₂)` contains **no** `(d−1)`-box.

**Step 2 (double count).** With `m_γ(y) = #{x : f(x,y) = γ}`,

```
Σ_{x₁<x₂} |B_γ(x₁,x₂)| = Σ_{y ∈ [n]^{d−1}} C(m_γ(y), 2).                        (1)
```

**Step 3 (convexity, lower bound).** At each `y` the multiplicities satisfy
`Σ_γ m_γ(y) = n`, and `t ↦ C(t,2)` is convex, so

```
Σ_γ C(m_γ(y), 2) ≥ c · C(n/c, 2).
```

Summing (1) over the `c` colours:

```
Σ_γ Σ_{x₁<x₂} |B_γ(x₁,x₂)| ≥ n^{d−1} · c · C(n/c, 2).                          (2)
```

**Step 4 (upper bound).** By Step 1 each `B_γ(x₁,x₂)` is a box-free subset of
`[n]^{d−1}`; let `Z_{d−1}(n)` be the maximum size of such a subset. There are `C(n,2)`
slice pairs and `c` colours:

```
Σ_γ Σ_{x₁<x₂} |B_γ(x₁,x₂)| ≤ C(n,2) · c · Z_{d−1}(n).                          (3)
```

**Step 5 (conclude).** Combining (2) and (3):

```
n^{d−1} · C(n/c, 2)  ≤  C(n,2) · Z_{d−1}(n).                                   (4)
```

If (4) fails, no box-free c-colouring of `[n]^d` exists, i.e. `[n]^d` is c-guaranteed.

## 2. The 3-dimensional case

For `d = 3`, `Z₂(n)` is the largest number of edges in a `C₄`-free bipartite graph with both
parts of size `n` (Zarankiewicz number `z(n,n;2,2)`). The elementary Kővári–Sós–Turán bound
gives

```
Z₂(n) ≤ n/2 + (n/2)·√(4n−3).
```

*Proof of the bound.* For each pair of columns `{z₁,z₂}` at most one row is adjacent to both
(otherwise a `C₄`), so `Σ_y C(d_y,2) ≤ C(n,2)`. By convexity
`Σ_y C(d_y,2) ≥ n·C(e/n,2) = (e²/n − e)/2`, hence `e² − ne − n²(n−1) ≤ 0`. ∎

So (4) becomes the explicit necessary condition

```
n² · C(n/2, 2)  ≤  C(n,2) · [ n/2 + (n/2)√(4n−3) ]        (c = 2)              (5)
```

which fails first at `n = 22`:

| n | LHS `n²C(n/2,2)` | RHS `C(n,2)Z₂(n)` | verdict |
|---|---|---|---|
| 20 | 18 000 | 18 572 | consistent |
| 21 | 21 995 | 22 050 | consistent |
| **22** | **26 620** | **25 964** | **contradiction** |

**Hence `N(2,3) ≤ 22`.** ∎

More colours, same criterion:

| c | threshold from (4)+(KST) | published `5c⁴` |
|---|---|---|
| 2 | **22** | 80 |
| 3 | **93** | 405 |
| 4 | **277** | 1280 |
| 5 | **657** | 3125 |
| 6 | 1341 | 6480 |
| 7 | 2461 | 12005 |
| 8 | 4173 | 20480 |

## 3. Numerical validation of every step

Checked against the explicit prism-free 2-colouring of `[11]³` (`prism/results/K2_N11.json`),
where all quantities can be computed exactly:

* identity (1): `Σ_{x₁<x₂}|B_γ| = 1540` vs `Σ_y C(m_γ,2) = 1540` for `γ = 0`, and
  `1485 = 1485` for `γ = 1` — exact match;
* Step 1: `max_{x₁,x₂}|B_γ(x₁,x₂)| = 28 ≤ Z₂(11) = 40.7` ✓;
* Step 3: `Σ_γ Σ|B_γ| = 3025 ≥ n²·(n²/4 − n/2) = 2995` ✓;
* (5) holds at `n = 11` (`2995 ≤ 4479`), as it must for a colouring that exists, and fails
  at `n = 22`.

## 4. What this does and does not give

* It **halves the window**: combined with the explicit colouring of `[11]³`,
  `12 ≤ N(2,3) ≤ 22`.
* It gives the first two-sided rigorous windows for `c = 3,4,5` as well (see the summary
  report).
* It does **not** settle `N(2,3)`. Closing `12…22` needs either an explicit 2-colouring of
  some `[n]³` with `12 ≤ n ≤ 22`, or a much stronger upper-bound technique.
* The argument is *shape-agnostic*: `Z₂(n)` is only tight at `n = q²+q+1` (projective
  planes), so the KST bound cannot be improved much without exact Zarankiewicz numbers.

## 5. General d, and a reduction relevant to the uniform-c question

For general `d`, (4) reads

```
[n]^d is c-guaranteed  whenever  Z_{d−1}(n) < n^{d−1}/c²,                      (6)
```

i.e. whenever no box-free **subset** of `[n]^{d−1}` has density at least `1/c²`.

Since a prism-free c-colouring of `[n]^d` has c colour classes, each a box-free subset of
`[n]^d` of density `≈ 1/c`, we get: *explicit low-density box-free subsets are exactly what
blocks this upper-bound method*. And the dimension-raising lemma supplies them — the
`[11]³` colouring lifts to box-free subsets of `[11]^m` of density `1/2` for every `m`.

So (6) can only beat the known `(d+2)2^{2^{d−1}}` bound if the box-free-subset density
threshold grows slowly with `d`. By the random-subset argument, density `p` box-free subsets
of `[n]^m` exist whenever `C(n,2)^m p^{2^m} < 1`, i.e. `n ≲ p^{−2^m/(2m)}·2^{...}`; with
`p = 1/c²` this is `n ≲ (c²)^{2^m/(2m)} = c^{2^{m+1}/m}` — exponent `2^d/d` again. So the
method is not strong enough for a uniform `c`; it reproduces the same exponent, as one
expects.
