"""Self-contained certificate:  N(2,3) <= 20.

Notation: a *feature* is a triple (colour c, row pair {y1,y2}, column pair {z1,z2}).
Slice x of [n]^3 *uses* it when the four cells (x,y1,z1),(x,y1,z2),(x,y2,z1),(x,y2,z2)
all have colour c.

FACT 1 (packing).  A 2-colouring of [n]^3 has no monochromatic 8-vertex prism
        <=>  no feature is used by two different slices.
FACT 2 (convexity, 2-D).  Every 2-colouring of [n]x[n] has at least
        phi(n) = sum over column pairs j of [C(a_j,2)+C(b_j,2)]
        monochromatic rectangles, where a_j,b_j count rows whose two cells in
        column pair j are both 0 / both 1.
        With T0 = sum_j a_j = sum_y C(k_y,2)  (k_y = #0-cells in row y) and
        T1 = sum_j b_j = sum_y C(n-k_y,2), over Np = C(n,2) column pairs:
            sum_j C(a_j,2) >= minpairs(T0, Np),  minpairs(T,B) = exact minimum of
            sum of C(x_j,2) over integers x_j >= 0 with sum T (convexity).
FACT 3 (Lemma 15 of Cooper-Fenner-Purewal, in packing language).
        n * phi(n) <= 2*C(n,2)^2 is necessary for a box-free 2-colouring of [n]^3.
"""
from math import comb

def minpairs(T, bins):
    q, r = divmod(T, bins)
    return (bins - r) * comb(q, 2) + r * comb(q + 1, 2)

def phi21_lower_bound():
    n, Np = 21, comb(21, 2)                       # Np = 210
    per_row_min = comb(10, 2) + comb(11, 2)       # 45 + 55 = 100, k optimal
    assert per_row_min == min(comb(k,2)+comb(21-k,2) for k in range(22))
    S = n * per_row_min                           # T0+T1 >= 2100
    # every row contributes an even amount, and T0,T1 are integers, so either
    #   (i) T0+T1 = 2100, forcing k_y in {10,11} for every row, i.e.
    #       T0 = 945+10m, T1 = 1155-10m for an integer m in [0,21]; or
    #   (ii) T0+T1 >= 2102.
    best = None
    for m in range(22):                           # case (i)
        T0, T1 = 945 + 10*m, 1155 - 10*m
        v = minpairs(T0, Np) + minpairs(T1, Np)
        best = v if best is None or v < best else best
    best_i = best
    best_ii = 2 * minpairs(1051, Np)               # case (ii): most balanced split of 2102
    phi = min(best_i, best_ii)
    return phi, best_i, best_ii

if __name__ == "__main__":
    n = 21
    phi, bi, bii = phi21_lower_bound()
    print(f"phi(21) >= {phi}   (case i: {bi}, case ii: {bii})")
    pool = 2 * comb(n, 2) ** 2
    need = n * phi
    print(f"features available 2*C(21,2)^2 = {pool}")
    print(f"features required  21*phi      = {need}")
    print(f"{need} > {pool}  ->  [21]^3 is 2-uncolorable  =>  N(2,3) <= 20"
          if need > pool else "no contradiction")
    print()
    print("and 20 is not excluded:", 20 * 3400, "<=", 2 * comb(20, 2) ** 2)
