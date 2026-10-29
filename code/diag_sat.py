"""Diagonal-shift construction, solved exactly by SAT.

Base object: a 2-colouring f of [N]^2.  Define

        c(x, y, z) = f( (y-x) mod N , (z-x) mod N ).

Slice x is the base layer shifted diagonally by x, so the N slices are the N
diagonal shifts of f.  A prism over slices x1 < x2 is monochromatic iff f has
two monochromatic rectangles related by the diagonal shift (d, d), d = x2-x1.

Orbit invariant of a rectangle (colour c, rows y1<y2, cols z1<z2):
        key = ( c, (z2-z1) mod N, { (y1-z1) mod N, (y2-z1) mod N } ).

So:  f must have at most ONE monochromatic rectangle per key.
SAT variables: v[y][z] = colour of f at (y,z) (True = 1).
Clauses: for every pair of rectangles sharing a key, "not both monochromatic".
"""
import sys
from itertools import combinations

from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")


def rects_of(N):
    out = []
    for y1, y2 in combinations(range(N), 2):
        for z1, z2 in combinations(range(N), 2):
            out.append((y1, y2, z1, z2))
    return out


def key_of(c, r, N):
    """Canonical representative of the diagonal-shift orbit of a rectangle.

    Computed by brute force over all N shifts, so it is sound: two rectangles
    get the same key iff they differ by a diagonal shift.  (Naive invariants
    such as (z2-z1) mod N are wrong, because the difference is only defined up
    to sign and wrap-around can swap the ordering.)"""
    y1, y2, z1, z2 = r
    best = None
    for e in range(N):
        t = (c, tuple(sorted(((y1 - e) % N, (y2 - e) % N))),
             tuple(sorted(((z1 - e) % N, (z2 - e) % N))))
        if best is None or t < best:
            best = t
    return best


def group_pairs(N):
    """pairs of rectangles that must not be simultaneously monochromatic"""
    R = rects_of(N)
    groups = {}
    for r in R:
        for c in (0, 1):
            groups.setdefault(key_of(c, r, N), []).append((c, r))
    pairs = []
    for k, lst in groups.items():
        for (c1, r1), (c2, r2) in combinations(lst, 2):
            pairs.append((c1, r1, c2, r2))
    return pairs, R


def solve(N, time_limit=None, verbose=True):
    import threading
    import time
    pairs, R = group_pairs(N)
    var = {}
    n = 0
    for y in range(N):
        for z in range(N):
            n += 1
            var[y, z] = n
    cl = []

    def lit(y, z, c):
        return var[y, z] if c == 1 else -var[y, z]

    # Even N: a rectangle whose rows AND columns are both antipodal pairs is
    # mapped to itself by the shift N/2, so it is used by two different slices
    # at once.  Such rectangles must not be monochromatic at all.
    if N % 2 == 0:
        h = N // 2
        for y in range(h):
            for z in range(h):
                for c in (0, 1):
                    cl.append([-lit(y, z, c), -lit(y, z + h, c),
                               -lit(y + h, z, c), -lit(y + h, z + h, c)])

    for c1, (a1, b1, cc1, d1), c2, (a2, b2, cc2, d2) in pairs:
        cl.append([-lit(a1, cc1, c1), -lit(a1, d1, c1), -lit(b1, cc1, c1),
                   -lit(b1, d1, c1), -lit(a2, cc2, c2), -lit(a2, d2, c2),
                   -lit(b2, cc2, c2), -lit(b2, d2, c2)])
    if verbose:
        print(f"  N={N}: {n} vars, {len(cl)} clauses, {len(R)} rects/colour",
              flush=True)
    s = Cadical195(bootstrap_with=cl)
    t = threading.Timer(time_limit, s.interrupt) if time_limit else None
    t0 = time.time()
    if t:
        t.start()
    try:
        r = s.solve()
    finally:
        if t:
            t.cancel()
    dt = time.time() - t0
    m = s.get_model() if r else None
    s.delete()
    if m is None:
        return ("UNKNOWN" if time_limit else "UNSAT"), None, dt
    S = set(v for v in m if v > 0)
    f = [[1 if var[y, z] in S else 0 for z in range(N)] for y in range(N)]
    return "SAT", f, dt


def lift(f, N):
    """build the N^3 colouring c(x,y,z) = f((y-x) mod N, (z-x) mod N)"""
    return [[[f[(y - x) % N][(z - x) % N] for z in range(N)]
             for y in range(N)] for x in range(N)]


if __name__ == "__main__":
    import json
    import os
    from core import is_valid_fast
    OUT = "/home/user/prism/results"
    tl = float(os.environ.get("TL", "600"))
    for N in map(int, sys.argv[1:]):
        st, f, dt = solve(N, time_limit=tl)
        print(f"N={N}: {st} ({dt:.0f}s)", flush=True)
        if f is None:
            continue
        g = lift(f, N)
        ok = is_valid_fast(g)
        print(f"N={N}: lifted grid valid={ok}", flush=True)
        if ok:
            os.makedirs(OUT, exist_ok=True)
            json.dump(g, open(f"{OUT}/K2_N{N}.json", "w"))
            json.dump(f, open(f"{OUT}/K2_N{N}_base2d.json", "w"))
