"""Single-coordinate shift construction for K = 2, solved exactly by SAT.

Construction:  c(x, y, z) = f( (y - x) mod N , z )

Slice x is the base layer f shifted by x in the y direction only.

A prism over slices x1 < x2 and the actual rectangle rows {y1,y2}, cols {z1,z2}
needs both slices monochromatic there.  With d = x2-x1 and a = y1-x1,
b = y2-x1, that says

        a, b  in  S(c,{z1,z2})   and   a-d, b-d  in  S(c,{z1,z2})

where S(c,{z1,z2}) = { y : f(y,z1) = f(y,z2) = c }.  Two 2-subsets are
translates of each other exactly when they have the same oriented difference,
so the construction is prism-free iff

        for every colour c and column pair {z1,z2},
        S(c,{z1,z2}) has at most one ordered pair with any given difference
        i.e. S(c,{z1,z2}) is a SIDON set in Z_N.

(Shifting in one coordinate only keeps the orbits small, which is why this is
much weaker than the diagonal-shift condition.)

Size heuristic: |S| ~ N/4 for a balanced 2-colouring, while a Sidon set in Z_N
has size ~ sqrt(N).  So this family should be feasible up to about N = 16.
"""
import sys
from itertools import combinations

from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")


def build(N, nb=None):
    var = {}
    n = 0
    for y in range(N):
        for z in range(N):
            n += 1
            var[y, z] = n
    cl = []

    def lit(y, z, c):
        return var[y % N, z] if c == 1 else -var[y % N, z]

    for c in (0, 1):
        for z1, z2 in combinations(range(N), 2):
            for d in range(1, N):
                for a in range(N):
                    for b in range(a + 1, N):
                        cl.append([-lit(a, z1, c), -lit(a, z2, c),
                                   -lit(a + d, z1, c), -lit(a + d, z2, c),
                                   -lit(b, z1, c), -lit(b, z2, c),
                                   -lit(b + d, z1, c), -lit(b + d, z2, c)])
    cl.append([-var[0, 0]])      # colour-swap symmetry: f(0,0) = 0
    return n, cl, var


def solve(N, time_limit=None, verbose=True):
    import threading
    import time
    n, cl, var = build(N)
    if verbose:
        print(f"  N={N}: {n} vars, {len(cl)} clauses", flush=True)
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
    """c(x,y,z) = f((y-x) mod N, z)"""
    return [[[f[(y - x) % N][z] for z in range(N)] for y in range(N)]
            for x in range(N)]


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
