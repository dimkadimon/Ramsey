"""RIGOROUS UPPER BOUND for the cube, via a C4/Zarankiewicz counting argument.

Setup.  Let f : [n]^3 -> [c] be a colouring with NO monochromatic box.

Fix a colour gamma and two distinct slices x1 < x2.  Put

    B_gamma(x1,x2) = { (y,z) : f(x1,y,z) = gamma = f(x2,y,z) }  subset of [n]^2.

Claim 1.  B_gamma(x1,x2) contains no rectangle {y1,y2}x{z1,z2}: if it did, those
eight grid points would all have colour gamma, i.e. a monochromatic box.
So viewed as a bipartite graph on Y x Z, B_gamma(x1,x2) is C4-free.

Claim 2 (elementary Kovari-Sos-Turan for C4).  A C4-free bipartite graph with
both sides of size n has at most

        z(n) = n/2 + (n/2) * sqrt(4n-3)

edges.  [Proof: sum over z1<z2 of #{y adjacent to both} <= C(n,2); on the other
hand by convexity sum_y C(d_y,2) >= (e^2/n - e)/2.]

Claim 3 (double counting).  With m_c(y,z) = #{x : f(x,y,z) = c},
        sum_{x1<x2} |B_c(x1,x2)| = sum_{y,z} C(m_c(y,z), 2),
and by convexity the right side is at least n^2 * C(N_c/n^2, 2), where
N_c = sum m_c = # points of colour c.

Combining:   n^2 * C(N_c/n^2, 2)  <=  C(n,2) * z(n)   for every colour c.   (*)

One colour has N_c >= n^3 / c.  Writing (*) out:

    N_c^2 - n^2 N_c <= n^3 (n-1) z(n),

so N_c <= [ n^2 + sqrt( n^4 + 4 n^3 (n-1) z(n) ) ] / 2, and therefore

    n^3 / c  <=  [ n^2 + sqrt( n^4 + 4 n^3 (n-1) z(n) ) ] / 2 .        (**)

If (**) fails, no box-free c-colouring of [n]^3 exists, i.e. [n]^3 is c-guaranteed.

This is self-contained and gives explicit numbers (table below).
"""
from fractions import Fraction
import math


def z(n):
    """upper bound on edges of a C4-free bipartite graph with parts of size n"""
    return n / 2 + (n / 2) * math.sqrt(4 * n - 3)


def consistent(n, c):
    """does inequality (**) hold?  (True => the counting argument gives no contradiction)"""
    lhs = n ** 3 / c
    rhs = (n ** 2 + math.sqrt(n ** 4 + 4 * n ** 3 * (n - 1) * z(n))) / 2
    return lhs <= rhs


def guaranteed_from(n, c):
    return not consistent(n, c)


def threshold(c, nmax=200000):
    """smallest n such that the argument proves [n]^3 is c-guaranteed"""
    for n in range(2, nmax):
        if guaranteed_from(n, c):
            return n
    return None


if __name__ == "__main__":
    print("n   consistent? (counting argument allows a box-free colouring)")
    for n in range(20, 34):
        print(f"{n:3d}   {consistent(n,2)}   lhs={n**3/2:12.1f} rhs="
              f"{(n**2 + math.sqrt(n**4 + 4*n**3*(n-1)*z(n)))/2:12.1f}")
    print()
    print("thresholds (smallest n proved c-guaranteed by this argument):")
    for c in range(2, 7):
        t = threshold(c)
        print(f"  c={c}: n >= {t}   (published Cor 3.6 gives n < {(3+2)*c**4})")


# ---------------------------------------------------------------- refinement
# Joint (multi-colour) version.  At each cell (y,z) the multiplicities satisfy
# sum_c m_c = n, so by convexity  sum_c C(m_c,2) >= c*C(n/c,2) = n^2/(2c) - n/2.
# Summing over the n^2 cells:
#        sum_{x1<x2} sum_c |B_c(x1,x2)|  >=  n^2 (n^2/(2c) - n/2).
# And each colour separately is C4-free, so the total is at most C(n,2)*c*z(n).
# Hence the necessary condition
#        n^2 (n^2/(2c) - n/2)  <=  C(n,2) * c * z(n).        (***)

def consistent_joint(n, c):
    lhs = n * n * (n * n / (2 * c) - n / 2)
    rhs = (n * (n - 1) / 2) * c * z(n)
    return lhs <= rhs


def threshold_joint(c, nmax=1000):
    for n in range(2, nmax):
        if not consistent_joint(n, c):
            return n
    return None


def _report_joint():
    print("\njoint (multi-colour) criterion (***):")
    for n in range(10, 22):
        print(f"  n={n:3d}: lhs={n*n*(n*n/4-n/2):10.0f}  rhs={(n*(n-1)/2)*2*z(n):10.0f}"
              f"  consistent={consistent_joint(n,2)}")
    print()
    print("joint thresholds:")
    for c in range(2, 8):
        t = threshold_joint(c)
        print(f"  c={c}: n >= {t}")
