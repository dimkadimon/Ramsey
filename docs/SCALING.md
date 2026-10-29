# Growth of N(2,d): what is proved, and what is open

`N(c,d)` = least R such that every c-colouring of `[R]^d` has a monochromatic box
(`{x₁,x₁'}×…×{x_d,x_d'}`, all pairs distinct). The question here is how `N(2,d)`
grows with the dimension d.

## 1. What I can prove (rigorous, elementary)

**Theorem 1.** For every `d ≥ 2` and every `n` with `C(n,2)^d < 2^{2^d−1}` there is a
2-colouring of `[n]^d` with no monochromatic box. Hence

```
N(2,d) >  max{ n : C(n,2)^d < 2^{2^d − 1} }  ≥  2^{ 2^d / (2d) }        (d ≥ 2).
```

*Proof.* Colour each of the `n^d` points independently uniformly at random. There are
`C(n,2)^d` boxes. A fixed box is monochromatic (in either colour) with probability
`2·2^{−2^d} = 2^{1−2^d}`. By the union bound,

```
P(∃ monochromatic box) ≤ C(n,2)^d · 2^{1−2^d} < 1
```

whenever `C(n,2)^d < 2^{2^d−1}`; so some colouring has no monochromatic box. Writing
`C(n,2) ≥ n²/4` for `n ≥ 2` gives `n^{2d}/4^d < 2^{2^d−1}`, i.e.
`n < 2^{(2^d−1)/(2d) + 1}`; the clean statement `N(2,d) ≥ 2^{2^d/(2d)}` follows because
`(2^d−1)/(2d) + 1 ≥ 2^d/(2d)` for `d ≥ 2`. ∎

This is the standard argument; it is also essentially the content of the lower-bound
half of Cooper–Fenner–Purewal Cor. 3.6 (`V(c,d) > 2^{−d}e^{−1}c^{2^d−1}`), specialised
to cubes and made explicit.

For comparison, the published upper bound (same paper, Cor. 3.6) is
`N(2,d) < (d+2)·2^{2^{d−1}}`, so

```
2^{ 2^d/(2d) }  ≤  N(2,d)  <  (d+2)·2^{2^{d−1}} .
```

The exponents agree up to a factor ≈ `2d` in front of `2^d`.

| d | exact `max n` (Thm 1) | clean `2^{2^d/(2d)}` | upper `(d+2)2^{2^{d-1}}` | log₂ gap |
|---|---|---|---|---|
| 3 | 3 | 2^{1.3} | 2^{6.3} | 4.7 |
| 4 | 5 | 2^{2.0} | 2^{10.6} | 5.3 |
| 5 | 12 | 2^{3.2} | 2^{18.8} | 5.9 |
| 6 | 54 | 2^{5.3} | 2^{35.0} | 6.6 |
| 8 | 88 750 | 2^{16.0} | 2^{131.3} | 8.2 |
| 10 | 3.5·10¹⁵ | 2^{51.2} | 2^{515.6} | 10.1 |
| 12 | 2^{171.1} | 2^{170.7} | 2^{2051.8} | 12.0 |

(produced by `prism/scaling.py`). For `d = 3` the upper column overstates what is
known: the CFP table gives the better bound `N(2,3) ≤ 28`, and for `d ≥ 4` no cubical
values are tabulated.

## 2. The statement as asked: `N(2,d) ≥ 2^{c·2^d}` for a fixed `c > 0`

**This is open, and I cannot prove it.** Concretely:

* What Theorem 1 gives is `N(2,d) ≥ 2^{c_d·2^d}` with `c_d = 1/(2d)` — the constant
  *decays with d*, so it is not of the requested form.
* The requested form would mean the exponent of `N(2,d)` is `Θ(2^d)`, whereas all known
  lower-bound techniques give `Θ(2^d/d)`. The gap is exactly a factor `d`; the upper
  bound is `Θ(2^d)`. Closing it is the natural open problem in this area.

Two independent countings both produce `2^d/d`, which is why I believe this is a genuine
barrier rather than laziness:

**(a) Union bound.** `#boxes · P(mono) < 1` gives `d·α·2^{d} < 2^{d}·1` → `α < 1/(2d)`
for `N = 2^{α2^d}`. The Lovász Local Lemma gives the same rate: with
`p = 2^{1−2^d}` and dependency degree `≤ d·2^d·n^{2d−2}`, the condition `e·p·(D+1) < 1`
again forces `α ≲ 1/(2d)`.

**(b) The layer/packing count.** A colouring of `[n]^d` is equivalent to `n` layers
(colourings of `[n]^{d−1}`) with pairwise disjoint feature sets, where a feature is
`(colour, (d−1)-box)`; there are `F = 2C(n,2)^{d−1}` features. If each layer uses `ν`
features, packing needs `n·ν ≤ F` **and** the birthday condition `n·ν² ≲ F`. With
random-quality layers (`ν ≈ F/2^{2^{d−1}}`) this gives

```
n · ν² ≲ F   ⟹   n · (C(n,2)^{d−1}/2^{2^{d−1}})² ≲ C(n,2)^{d−1}
              ⟹   n^{2d−1} ≲ 2^{2^d}   ⟹   n ≲ 2^{2^d/(2d−1)},
```

the same exponent. The only lever is to make `ν` — the number of monochromatic
`(d−1)`-boxes in a layer — much smaller than random.

**So the key sub-question is a Ramsey-multiplicity question:**

> How few monochromatic boxes can a 2-colouring of `[n]^m` have?
> A uniform `c` in `N(2,m+1) ≥ 2^{c·2^{m+1}}` follows if the answer is a factor
> `2^{Θ(2^m)}` below the random count `C(n,2)^m/2^{2^m−1}`.

Measured evidence (`prism/stats.py`) says this is *not* happening at small m — the
minimum is only a constant factor below random, not an exponential one:

| m | n | total boxes | random expected mono | best found | ratio |
|---|---|---|---|---|---|
| 2 | 11 | 3 025 | 756 | 255 | 0.34 |
| 2 | 12 | 4 356 | 1 089 | 424 | 0.39 |
| 3 | 9 | 46 656 | 364 | 65 | 0.18 |
| 3 | 6 | 3 375 | 26 | 0 | 0 |

(the m = 2 rows via local search on 2-colourings of `[n]²`; the m = 3 rows by
minimising `#monochromatic 3-boxes` over 2-colourings of `[n]³` — `n = 6` is simply
small enough to be box-free). The ratio shrinks with m, but slowly — nothing like the
`2^{−Θ(2^m)}` needed. If that persists, the layer/packing route cannot give a uniform
`c`, and the requested theorem needs an idea of a different kind.

## 3. What *is* provable in the other direction, and how it relates

The dimension-raising lemma from the previous round (`prism/dimraise.py`) gives the
opposite monotonicity — `N(2,d+1) ≤ N(2,d)` via

```
F(x₁,…,x_{d+1}) = f( (x₁−x_{d+1}), …, (x_d−x_{d+1}) )
```

— so explicit three-dimensional colourings certify `N(2,d) ≥ 12` for **every** d. That
is a constant, useless asymptotically, but it is constructive (no probabilistic method),
and it shows that any lower bound of the form `2^{c·2^d}` must come from a
genuinely higher-dimensional construction, not from lifting a fixed one.

## 4. Summary

| statement | status |
|---|---|
| `N(2,d) ≥ 2^{2^d/(2d)}` for all `d ≥ 2` | **proved** (Theorem 1, union bound) |
| `N(2,d) ≥ 2^{c_d 2^d}` with `c_d = 1/(2d)` | **proved** (same) |
| `N(2,d) < (d+2)2^{2^{d−1}}` | known (CFP Cor. 3.6) |
| `N(2,d) ≥ 2^{c·2^d}` for a **fixed** `c>0` | **open**; blocked by the factor-`d` loss in both countings |
| `N(2,d) ≥ 12` for all `d ≥ 3`, constructively | proved here (dimension-raising lemma) |

Note that even the two-sided statement `2^{2^d/(2d)} ≤ N(2,d) < (d+2)2^{2^{d−1}}` is a
perfectly publishable *expository* result once the constants are made explicit — but it
is a re-derivation of known bounds, not new mathematics.
