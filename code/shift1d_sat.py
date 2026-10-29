"""SAT search in the 1-D shift family:  chi(x,y,z) = f(x+y, z).

Variables v(u,z), u in [0,2n-2], z in [0,n-1]:  v true <=> f(u,z)=1.
Criterion (Prop. shift): for every colour g, z1<z2, a,b>=1, u0 with u0+a+b <= 2n-2,
the four cells (u0,z1),(u0,z2),(u0+a,z1),(u0+a,z2),(u0+b,z1),(u0+b,z2),
(u0+a+b,z1),(u0+a+b,z2) may not all have colour g.

Any model gives a genuinely box-free colouring of [n]^3 via chi(x,y,z)=f(x+y,z),
checked independently by core.is_valid_fast.
"""
import sys, time, json
from pysat.solvers import Cadical195

def build(n):
    U = 2 * n - 2                     # max value of x+y
    var = lambda u, z: (u * n + z) + 1
    S = Cadical195()
    cnt = 0
    for z1 in range(n):
        for z2 in range(z1 + 1, n):
            for a in range(1, n):
                for b in range(1, n):
                    for u0 in range(0, U + 1 - a - b):
                        pos = [var(u0, z1), var(u0, z2),
                               var(u0 + a, z1), var(u0 + a, z2),
                               var(u0 + b, z1), var(u0 + b, z2),
                               var(u0 + a + b, z1), var(u0 + a + b, z2)]
                        S.add_clause([-x for x in pos])   # not all colour 1
                        S.add_clause(pos)                 # not all colour 0
                        cnt += 2
    S.add_clause([-var(0, 0)])        # colour symmetry
    return S, cnt, U

def run(n, secs):
    t0 = time.time()
    S, cnt, U = build(n)
    print(f"n={n}: vars {(2*n-1)*n}, clauses {cnt}, build {time.time()-t0:.1f}s", flush=True)
    try:
        S.conf_budget(int(secs * 200000))
    except Exception as e:
        print("no conf_budget", e, flush=True)
    t1 = time.time()
    r = S.solve_limited()
    el = time.time() - t1
    print(f"solve_limited -> {r} in {el:.0f}s", flush=True)
    if r:
        m = set(v for v in S.get_model() if v > 0)
        f = [[1 if ((u*n+z)+1) in m else 0 for z in range(n)] for u in range(2*n-1)]
        grid = [[[f[x+y][z] for z in range(n)] for y in range(n)] for x in range(n)]
        return grid
    return None

if __name__ == "__main__":
    n = int(sys.argv[1]); secs = float(sys.argv[2]) if len(sys.argv) > 2 else 240
    g = run(n, secs)
    if g is None:
        print("NO SOLUTION FOUND (unknown/unsat)")
    else:
        sys.path.insert(0, "/home/user/prism")
        from core import is_valid_fast, bad_boxes
        print("independent check is_valid_fast:", is_valid_fast(g), flush=True)
        print("bad boxes:", len(bad_boxes(g, limit=5)), flush=True)
        if is_valid_fast(g):
            json.dump(g, open(f"/home/user/prism/results/K2_N{n}.json", "w"))
            print("*** BOX-FREE COLOURING of [%d]^3 FOUND IN THE SHIFT FAMILY" % n, flush=True)
