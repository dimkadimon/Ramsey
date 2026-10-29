"""SAT for box-free c=2 colourings of [n]^3, using the packing formulation.

One boolean variable per cell: V(x,y,z) = 1  <=>  cell has colour 1.
For every pair of distinct x-slices and every (row pair, col pair) the
8 cells must not be all 0 and must not be all 1  ->  two clauses of width 8.
Total clauses 2*C(n,2)^3, variables n^3.
"""
import sys, time, json
from itertools import combinations
from pysat.solvers import Cadical195

def solve(n, secs=300, seed_phase=True):
    idx = lambda x, y, z: x*n*n + y*n + z + 1
    S = Cadical195()
    t0 = time.time()
    C2 = list(combinations(range(n), 2))
    ncell = n**3
    cnt = 0
    for (x1, x2) in C2:
        for (y1, y2) in C2:
            for (z1, z2) in C2:
                pos = [idx(x1,y1,z1), idx(x1,y1,z2), idx(x1,y2,z1), idx(x1,y2,z2),
                       idx(x2,y1,z1), idx(x2,y1,z2), idx(x2,y2,z1), idx(x2,y2,z2)]
                S.add_clause(pos)                    # not all colour 0
                S.add_clause([-v for v in pos])      # not all colour 1
                cnt += 2
    print(f"n={n}: {ncell} vars, {cnt} clauses, build {time.time()-t0:.1f}s", flush=True)
    # colour symmetry
    S.add_clause([-idx(0,0,0)])
    try:
        S.conf_budget(int(secs*100000))
    except Exception as e:
        print("no conf_budget:", e, flush=True)
    t1 = time.time()
    r = S.solve_limited()
    print(f"solve: {r} in {time.time()-t1:.1f}s", flush=True)
    if r:
        model = set(v for v in S.get_model() if v > 0)
        g = [[[1 if idx(x,y,z) in model else 0 for z in range(n)] for y in range(n)] for x in range(n)]
        return g
    return None

if __name__ == "__main__":
    n = int(sys.argv[1]); secs = float(sys.argv[2]) if len(sys.argv) > 2 else 300
    g = solve(n, secs)
    if g is None:
        print("UNKNOWN/UNSAT")
    else:
        json.dump(g, open(f"/home/user/prism/results/K2_N{n}.json", "w"))
        print("SAT -> colouring written")
