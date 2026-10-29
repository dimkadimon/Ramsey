"""Memory-lean SAT solver: clauses streamed straight into CaDiCaL.

Encoding: var(p,k) <=> point p has colour k.
  - exactly one colour per point
  - for each box b and colour k:  not all 8 vertices of b have colour k
Optional strong extra: symmetry breaking + pruning of tiny boxes.
"""
import sys
from itertools import combinations
from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")


def solve(N, K, time_limit=None, prev=None, phases_random=False, seed=None):
    """Return (status, grid). status in {'SAT','UNSAT','UNKNOWN'}."""
    V = lambda x, y, z, k: ((x * N + y) * N + z) * K + k + 1
    s = Cadical195()
    # exactly-one colour per point
    for x in range(N):
        for y in range(N):
            for z in range(N):
                s.add_clause([V(x, y, z, k) for k in range(K)])
                for a, b in combinations(range(K), 2):
                    s.add_clause([-V(x, y, z, a), -V(x, y, z, b)])
    # no monochromatic box
    for x1, x2 in combinations(range(N), 2):
        for y1, y2 in combinations(range(N), 2):
            for z1, z2 in combinations(range(N), 2):
                vs = [(x1, y1, z1), (x1, y1, z2), (x1, y2, z1), (x1, y2, z2),
                      (x2, y1, z1), (x2, y1, z2), (x2, y2, z1), (x2, y2, z2)]
                for k in range(K):
                    s.add_clause([-V(p[0], p[1], p[2], k) for p in vs])
    if prev is not None:
        ph = []
        for x in range(N):
            for y in range(N):
                for z in range(N):
                    c = prev[x][y][z]
                    for k in range(K):
                        ph.append(V(x, y, z, k) if k == c else -V(x, y, z, k))
        try:
            s.set_phases(ph)
        except Exception:
            pass
    import threading
    timer = threading.Timer(time_limit, s.interrupt) if time_limit else None
    if timer:
        timer.start()
    try:
        r = s.solve()
    finally:
        if timer:
            timer.cancel()
    model = s.get_model() if r else None
    s.delete()
    if model is None:
        return ("UNKNOWN" if time_limit else "UNSAT"), None
    S = set(v for v in model if v > 0)
    grid = [[[None] * N for _ in range(N)] for _ in range(N)]
    for x in range(N):
        for y in range(N):
            for z in range(N):
                for k in range(K):
                    if V(x, y, z, k) in S:
                        grid[x][y][z] = k
    return "SAT", grid


if __name__ == "__main__":
    from core import is_valid
    N, K = int(sys.argv[1]), int(sys.argv[2])
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else None
    st, g = solve(N, K, tl)
    print(f"N={N} K={K} -> {st}")
    if g:
        print("verified valid:", is_valid(g))
