"""SAT search for the cyclic-shift construction (K = 2).

Variables t[y][z]  (t=1 <=> z in T_y).  Conditions, for every row pair y1<y2:

  * colour-1 shared set  D1 = {z : t[y1][z] and t[y2][z]}  must be shift-safe
  * colour-0 shared set  D0 = {z : not t[y1][z] and not t[y2][z]} likewise

"Shift-safe" = no two distinct pairs of D have the same difference up to sign,
and (N even) no antipodal pair.  Each violation is an 8-literal clause.
"""
import sys

from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")


def classes(N):
    """difference classes, up to sign; for even N the antipodal class is special"""
    ks = [k for k in range(1, (N // 2) + 1)]
    return ks


def build(N, fix_first=True):
    var = {}
    n = 0

    def V(y, z):
        nonlocal n
        key = (y, z % N)
        if key not in var:
            n += 1
            var[key] = n
        return var[key]

    cl = []
    for y1 in range(N):
        for y2 in range(y1 + 1, N):
            for k in classes(N):
                antipodal = (N % 2 == 0 and k == N // 2)
                starts = range(N // 2) if antipodal else range(N)
                if antipodal:
                    for a in starts:
                        lits = [V(y1, a), V(y2, a), V(y1, a + k), V(y2, a + k)]
                        cl.append([-x for x in lits])   # D1: forbid the pair
                        cl.append(lits[:])              # D0: forbid the pair
                else:
                    for a in starts:
                        for b in range(a + 1, N):
                            if b == a:
                                continue
                            A = [V(y1, a), V(y2, a), V(y1, a + k), V(y2, a + k)]
                            B = [V(y1, b), V(y2, b), V(y1, b + k), V(y2, b + k)]
                            cl.append([-x for x in A] + [-x for x in B])
                            cl.append(A[:] + B[:])
    if fix_first:
        # row 0 can be normalised: symmetry z -> z+c allows t[0][0] = 1
        cl.append([V(0, 0)])

    # Symmetry breaking: permuting the rows is a symmetry of the construction
    # (it permutes the y coordinate), so sort rows lexicographically decreasing.
    for y in range(N - 1):
        A = [V(y, z) for z in range(N)]
        Bv = [V(y + 1, z) for z in range(N)]
        e = []
        for _ in range(N):
            n += 1
            e.append(n)
        cl.append([e[0]])
        for i in range(N - 1):
            cl.append([-e[i + 1], e[i]])
            cl.append([-e[i + 1], -A[i], Bv[i]])
            cl.append([-e[i + 1], A[i], -Bv[i]])
            cl.append([-e[i], -A[i], -Bv[i], e[i + 1]])
            cl.append([-e[i], A[i], Bv[i], e[i + 1]])
        for i in range(N):
            cl.append([-e[i], A[i], -Bv[i]])
    return n, cl, var


def solve(N, time_limit=None, verbose=True, fix_first=False):
    import threading
    import time
    n, cl, var = build(N, fix_first=fix_first)
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
        return None, dt
    S = set(v for v in m if v > 0)
    Ts = [set(z for z in range(N) if var[(y, z)] in S) for y in range(N)]
    return Ts, dt


if __name__ == "__main__":
    import json
    import os
    from cyclic import build_grid, check_sets
    from core import is_valid_fast
    OUT = "/home/user/prism/results"
    for N in map(int, sys.argv[1:]):
        Ts, dt = solve(N, time_limit=300)
        if Ts is None:
            print(f"N={N}: no design found ({dt:.0f}s)", flush=True)
            continue
        bad = check_sets(Ts, N)
        g = build_grid(Ts, N)
        ok = is_valid_fast(g)
        print(f"N={N}: design found ({dt:.0f}s), design-violations={len(bad)}, "
              f"grid valid={ok}", flush=True)
        if ok:
            os.makedirs(OUT, exist_ok=True)
            json.dump(g, open(f"{OUT}/K2_N{N}.json", "w"))
            json.dump([sorted(s) for s in Ts], open(f"{OUT}/K2_N{N}_sets.json", "w"))
