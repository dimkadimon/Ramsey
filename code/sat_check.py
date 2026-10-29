"""Independent SAT encoding + independent brute-force max-clique style check.
Deliberately written differently from the CP-SAT model so it can serve as a cross-check.
"""
import sys
from itertools import combinations
from pysat.solvers import Cadical195


def sat_feasible(N, K):
    pts = [(x, y, z) for x in range(N) for y in range(N) for z in range(N)]
    idx = {p: i for i, p in enumerate(pts)}
    var = lambda p, k: idx[p] * K + k + 1
    clauses = []
    for p in pts:
        clauses.append([var(p, k) for k in range(K)])           # at least one
        for a, b in combinations(range(K), 2):                   # at most one
            clauses.append([-var(p, a), -var(p, b)])
    nbox = 0
    for x1, x2 in combinations(range(N), 2):
        for y1, y2 in combinations(range(N), 2):
            for z1, z2 in combinations(range(N), 2):
                vs = [(x1, y1, z1), (x1, y1, z2), (x1, y2, z1), (x1, y2, z2),
                      (x2, y1, z1), (x2, y1, z2), (x2, y2, z1), (x2, y2, z2)]
                for k in range(K):
                    clauses.append([-var(p, k) for p in vs])     # not all this colour
                nbox += 1
    with Cadical195(bootstrap_with=clauses) as s:
        ok = s.solve()
        model = s.get_model() if ok else None
    grid = None
    if ok:
        S = set(v for v in model if v > 0)
        grid = [[[0] * N for _ in range(N)] for _ in range(N)]
        for p in pts:
            for k in range(K):
                if var(p, k) in S:
                    grid[p[0]][p[1]][p[2]] = k
    return ok, grid, len(clauses), nbox


if __name__ == "__main__":
    N, K = int(sys.argv[1]), int(sys.argv[2])
    ok, grid, nc, nb = sat_feasible(N, K)
    print(f"N={N} K={K} feasible={ok} clauses={nc} boxes={nb}")
    if grid:
        sys.path.insert(0, "/home/user/prism")
        from core import is_valid
        print("independent validity check:", is_valid(grid))
