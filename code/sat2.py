"""Clean SAT encoding: K-colour [N]^3 with no monochromatic axis-aligned box.

Variable (p, k) <-> point p has colour k.  For every box and colour:
    not all 8 vertices have colour k.
Uses CaDiCaL via python-sat.
"""
import sys
from itertools import combinations
from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")
from core import is_valid


def build(N, K):
    pts = [(x, y, z) for x in range(N) for y in range(N) for z in range(N)]
    idx = {p: i for i, p in enumerate(pts)}
    var = lambda p, k: idx[p] * K + k + 1
    clauses = []
    for p in pts:
        clauses.append([var(p, k) for k in range(K)])
        for a, b in combinations(range(K), 2):
            clauses.append([-var(p, a), -var(p, b)])
    nb = 0
    for x1, x2 in combinations(range(N), 2):
        for y1, y2 in combinations(range(N), 2):
            for z1, z2 in combinations(range(N), 2):
                vs = [(x1, y1, z1), (x1, y1, z2), (x1, y2, z1), (x1, y2, z2),
                      (x2, y1, z1), (x2, y1, z2), (x2, y2, z1), (x2, y2, z2)]
                for k in range(K):
                    clauses.append([-var(p, k) for p in vs])
                nb += 1
            # end z
    return clauses, pts, var, nb


def solve(N, K, time_limit=None, prev=None, solver_cls=Cadical195):
    """Return (status, grid).  status in {'SAT','UNSAT','UNKNOWN'}"""
    clauses, pts, var, nb = build(N, K)
    kw = {"time_limit": time_limit} if time_limit else {}
    try:
        s = solver_cls(bootstrap_with=clauses, **kw)
    except TypeError:
        s = solver_cls(bootstrap_with=clauses)
    with s:
        if prev is not None:
            ph = []
            for p in pts:
                k = prev[p[0]][p[1]][p[2]]
                for kk in range(K):
                    ph.append(var(p, kk) if kk == k else -var(p, kk))
            try:
                s.set_phases(ph)
            except Exception:
                pass
        try:
            r = s.solve() if time_limit is None else s.solve_limited()
        except Exception:
            r = None
        model = s.get_model() if r else None
    if model is None:
        return ("UNKNOWN" if time_limit else "UNSAT"), None
    S = set(v for v in model if v > 0)
    grid = [[[None] * N for _ in range(N)] for _ in range(N)]
    for p in pts:
        for k in range(K):
            if var(p, k) in S:
                grid[p[0]][p[1]][p[2]] = k
    return "SAT", grid


if __name__ == "__main__":
    N, K = int(sys.argv[1]), int(sys.argv[2])
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else None
    st, g = solve(N, K, tl)
    print(f"N={N} K={K} -> {st}")
    if g:
        print("verified valid:", is_valid(g))
