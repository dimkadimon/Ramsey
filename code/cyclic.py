"""Algebraic (cyclic-shift) construction for K = 2.

Idea.  Let T_y  (y = 0..N-1) be subsets of Z_N and define

        c(x, y, z) = 1   <=>   (z - x) mod N  in  T_y .

So slice x is the base layer shifted by x in z; the N slices are exactly the N
cyclic z-shifts of one layer.

When is it prism-free?  Take slices x and x+d (d != 0) and rows y,y'.  Both
slices are monochromatic on columns {z1,z2} iff
      u = z1-x, v = z2-x, u-d, v-d  are all in  D = T_y n T_y'
(or all in the co-intersection D0 = T^c_y n T^c_y' for colour 0, with d = -d).
So a monochromatic box exists iff some D contains a 2-set together with its
translate by -d.  If every pairwise difference of D is distinct (D is a *Sidon
set* in Z_N), the only such translate is the trivial one, d = 0.  Hence

   prism-free  <=  for all y<y':  T_y n T_y'  and  T^c_y n T^c_y'  are Sidon.

This turns the problem into a small combinatorial design search.
"""
import sys
from itertools import combinations

sys.path.insert(0, "/home/user/prism")


def is_sidon(S, N):
    """Is S "shift-safe"?  All pairwise differences must be distinct up to sign,
    AND (for even N) no pair may be antipodal, because a shift by N/2 maps an
    antipodal pair onto itself, which also produces a prism."""
    S = sorted(S)
    seen = set()
    for a, b in combinations(S, 2):
        d = (a - b) % N
        e = (b - a) % N
        k = min(d, e)
        if k == 0 or k in seen:
            return False
        if N % 2 == 0 and k == N // 2:
            return False
        seen.add(k)
    return True


def check_sets(Ts, N, verbose=False):
    bad = []
    for y1, y2 in combinations(range(len(Ts)), 2):
        D1 = Ts[y1] & Ts[y2]
        D0 = set(range(N)) - (Ts[y1] | Ts[y2])
        if not is_sidon(D1, N):
            bad.append(("one", y1, y2, sorted(D1)))
        if not is_sidon(D0, N):
            bad.append(("zero", y1, y2, sorted(D0)))
    if verbose and bad:
        print("violations:", bad[:6], "...total", len(bad))
    return bad


def build_grid(Ts, N):
    return [[[1 if ((z - x) % N) in Ts[y] else 0 for z in range(N)]
             for y in range(N)] for x in range(N)]


# ---------------------------------------------------------------- N = 11 design
def qr_design(N):
    """T_y = (quadratic residues + y): the (11,5,2) symmetric design for N=11."""
    qr = {x for x in range(N) if pow(x, (N - 1) // 2, N) in (1,) or x == 0}
    # residues of x^2 mod N
    qr = {(x * x) % N for x in range(1, N)}
    return [set((t + y) % N for t in qr) for y in range(N)]


if __name__ == "__main__":
    from core import is_valid_fast
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    Ts = qr_design(N)
    print(f"N={N}  |T_y| = {[len(t) for t in Ts]}")
    bad = check_sets(Ts, N, verbose=True)
    print("Sidon violations:", len(bad))
    g = build_grid(Ts, N)
    print("brute-force independent check:", is_valid_fast(g))
