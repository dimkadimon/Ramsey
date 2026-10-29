"""Correct CP-SAT model of the whole 3D problem.

Variables
  lit[x,y,z,c]   <=> cell (x,y,z) has colour c        (AddExactlyOne per cell)
  p[x,k,r]       <=> slice x is monochromatic in colour k on rectangle r
                     (r = (y1<y2, z1<z2) in the yz-plane)

Constraint: for every (k, r),  AddAtMostOne over x  of p[x,k,r]
  <=> no rectangle is monochromatic in the same colour on two slices
  <=> no monochromatic axis-aligned box.
"""
import sys
from itertools import combinations

from ortools.sat.python import cp_model

sys.path.insert(0, "/home/user/prism")


def solve(N, K, time_limit=120.0, workers=2, seed=0, symmetry=True,
          hint=None, verbose=False):
    rects = [(y1, y2, z1, z2)
             for y1, y2 in combinations(range(N), 2)
             for z1, z2 in combinations(range(N), 2)]
    m = cp_model.CpModel()
    lit = {}
    for x in range(N):
        for y in range(N):
            for z in range(N):
                for c in range(K):
                    lit[x, y, z, c] = m.NewBoolVar("")
                m.AddExactlyOne([lit[x, y, z, c] for c in range(K)])

    npv = 0
    for c in range(K):
        for (y1, y2, z1, z2) in rects:
            ps = []
            for x in range(N):
                four = [lit[x, y1, z1, c], lit[x, y1, z2, c],
                        lit[x, y2, z1, c], lit[x, y2, z2, c]]
                p = m.NewBoolVar("")
                for b in four:
                    m.AddImplication(p, b)
                m.AddBoolOr([~b for b in four] + [p])
                ps.append(p)
                npv += 1
            m.AddAtMostOne(ps)

    if symmetry:
        m.Add(lit[0, 0, 0, 0] == 1)          # colour symmetry

    if hint:
        for x in range(N):
            for y in range(N):
                for z in range(N):
                    for c in range(K):
                        m.AddHint(lit[x, y, z, c], 1 if hint[x][y][z] == c else 0)

    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_search_workers = workers
    s.parameters.random_seed = seed
    st = s.Solve(m)
    name = s.StatusName(st)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        g = [[[0] * N for _ in range(N)] for _ in range(N)]
        for x in range(N):
            for y in range(N):
                for z in range(N):
                    for c in range(K):
                        if s.Value(lit[x, y, z, c]):
                            g[x][y][z] = c
        return name, g
    return name, None


if __name__ == "__main__":
    from core import is_valid
    N, K = int(sys.argv[1]), int(sys.argv[2])
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 60
    st, g = solve(N, K, tl)
    print(f"N={N} K={K} -> {st}")
    if g:
        print("verified valid:", is_valid(g))
