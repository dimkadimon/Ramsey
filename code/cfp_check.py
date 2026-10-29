"""Exact evaluation of Cooper-Fenner-Purewal Lemma 3.2 (arXiv v1) / Lemma 4 (SIAM).

Recurrence derived from their own proof:
    Delta_0 = 1,  Delta_j = Delta_{j-1} * (a_j*Delta_{j-1} - c^{2^{j-1}}) / (a_j - 1)
(their printed form Delta^2_{j-1}(1 - c^{2^{j-1}}/((Delta_{j-1}-1)(a_j-1))) is the
same identity rewritten, and is singular at j=1, so Delta_1 = (a1-c)/(a1-1) as in
their d=1 proof).

[d]^d is c-uncolorable if all Delta_j > 0 and M*Delta_d >= c^{2^d - 1}, M = prod C(a_i,2).
"""
from fractions import Fraction as F
from math import comb


def deltas(c, a):
    D = F(1)
    out = [D]
    for j, aj in enumerate(a, start=1):
        D = D * (aj * D - c ** (2 ** (j - 1))) / (aj - 1)
        out.append(D)
    return out


def uncolorable(c, a):
    D = deltas(c, a)
    if any(d <= 0 for d in D[1:]):
        return False, D
    M = 1
    for aj in a:
        M *= comb(aj, 2)
    need = c ** (2 ** len(a) - 1)
    return (M * D[-1] >= need), D


if __name__ == "__main__":
    # --- sanity: d=1 truth is a1>=3 for c=2; d=2 truth is 5 ---
    print("d=1,c=2: least uncolorable a1 =", min(a for a in range(2, 8) if uncolorable(2, [a])[0]))
    print("d=2,c=2: least uncolorable n  =", min(n for n in range(2, 12) if uncolorable(2, [n, n])[0]))
    print("d=2,c=2 [3,7] uncolorable?", uncolorable(2, [3, 7])[0], " [5,5]?", uncolorable(2, [5, 5])[0],
          " [2,9]?", uncolorable(2, [2, 9])[0])
    print()
    for c in range(2, 6):
        n = min(n for n in range(2, 400) if uncolorable(c, [n] * 3)[0])
        print(f"c={c}, d=3: least n with [n]^3 c-uncolorable = {n}   => N({c},3) <= {n-1}")
    print()
    print("c=2 d=3 detail:")
    for n in range(18, 24):
        ok, D = uncolorable(2, [n] * 3)
        print(f"  n={n}: Delta={[float(d) for d in D]}  uncolorable={ok}")
