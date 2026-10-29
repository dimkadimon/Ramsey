"""Generalised shift-vector construction for K = 2.

Pick a shift vector v = (a,b) in (Z_N)^2 of order exactly N.  Put

        c(x, y, z) = f( (y - x*a) mod N , (z - x*b) mod N )

so slice x is the base layer f shifted by x*v.  The N slices are the N
translates of f along the cyclic group G = <v>.

A prism over slices x1 < x2 on the actual rectangle R needs both
        R - x1*v   and   R - x2*v
to be monochromatic rectangles of f, i.e. two mono rectangles of f differing by
(x2-x1)*v != 0.  Hence

   prism-free  <=>  at most one monochromatic rectangle of f per G-orbit.

v = (0,1) or (1,0) is the single-coordinate family (provably impossible for
N >= 12); v = (1,1) is the diagonal family.  All other slopes are new.
"""
import sys
from itertools import combinations

from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")


def order_of(a, b, N):
    import math
    g = math.gcd(math.gcd(a, b), N)
    if g == 0:
        return 1
    return N // math.gcd(N, g) if g else 1


def true_order(a, b, N):
    for t in range(1, N + 1):
        if (t * a) % N == 0 and (t * b) % N == 0:
            return t
    return N


def key_of(c, r, N, a, b):
    """canonical representative of the <(a,b)>-orbit of rectangle r"""
    y1, y2, z1, z2 = r
    best = None
    for t in range(N):
        s = ((y1 + t * a) % N, (y2 + t * a) % N, (z1 + t * b) % N, (z2 + t * b) % N)
        t2 = (c, tuple(sorted(s[:2])), tuple(sorted(s[2:])))
        if best is None or t2 < best:
            best = t2
    return best


def build(N, a, b):
    var = {}
    n = 0
    for y in range(N):
        for z in range(N):
            n += 1
            var[y, z] = n
    cl = []

    def lit(y, z, c):
        return var[y % N, z] if c == 1 else -var[y % N, z]

    groups = {}
    for y1, y2 in combinations(range(N), 2):
        for z1, z2 in combinations(range(N), 2):
            for c in (0, 1):
                k = key_of(c, (y1, y2, z1, z2), N, a, b)
                groups.setdefault(k, []).append((c, y1, y2, z1, z2))
    npair = 0
    for k, lst in groups.items():
        size = len(lst)
        if size < 2:
            continue
        for r1, r2 in combinations(lst, 2):
            c1, a1, b1_, d1, e1 = r1
            c2, a2, b2_, d2, e2 = r2
            cl.append([-lit(a1, d1, c1), -lit(a1, e1, c1), -lit(b1_, d1, c1),
                       -lit(b1_, e1, c1), -lit(a2, d2, c2), -lit(a2, e2, c2),
                       -lit(b2_, d2, c2), -lit(b2_, e2, c2)])
            npair += 1
    cl.append([-var[0, 0]])
    return n, cl, var, len(groups), npair


def run(N, a, b, secs=None):
    import time
    n, cl, var, norbit, npair = build(N, a, b)
    t0 = time.time()
    s = Cadical195(bootstrap_with=cl)
    r = s.solve()
    dt = time.time() - t0
    m = s.get_model() if r else None
    s.delete()
    if not m:
        return None, dt, (n, len(cl), norbit)
    S = set(v for v in m if v > 0)
    f = [[1 if var[y, z] in S else 0 for z in range(N)] for y in range(N)]
    return f, dt, (n, len(cl), norbit)


def lift(f, N, a, b):
    return [[[f[(y - x * a) % N][(z - x * b) % N] for z in range(N)]
             for y in range(N)] for x in range(N)]


if __name__ == "__main__":
    import json
    import os
    from core import is_valid_fast
    N = int(sys.argv[1])
    OUT = "/home/user/prism/results"
    cands = [(a, b) for a in range(N) for b in range(N)
             if (a, b) != (0, 0) and true_order(a, b, N) == N]
    print(f"N={N}: {len(cands)} shift vectors of order {N}", flush=True)
    for (a, b) in cands:
        f, dt, info = run(N, a, b)
        tag = f"v=({a},{b})"
        if f is None:
            print(f"  {tag}: UNSAT ({dt:.0f}s) vars/clauses/orbits={info}", flush=True)
            continue
        g = lift(f, N, a, b)
        ok = is_valid_fast(g)
        print(f"  {tag}: SAT ({dt:.0f}s) lifted valid={ok}", flush=True)
        if ok:
            os.makedirs(OUT, exist_ok=True)
            json.dump(g, open(f"{OUT}/K2_N{N}.json", "w"))
            json.dump(f, open(f"{OUT}/K2_N{N}_base2d.json", "w"))
            json.dump([a, b], open(f"{OUT}/K2_N{N}_shiftvec.json", "w"))
            break
