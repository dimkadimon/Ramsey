"""Layer-by-layer builder, SAT feasibility + CP-SAT improvement with hint.

Step for slice x:
  1. CaDiCaL: find any K-colouring of the N x N grid whose monochromatic
     rectangles avoid every feature already used by slices 0..x-1.
  2. CP-SAT warm-started from that colouring, minimise number of new features
     (keeping the forbidden ones forbidden).
  3. commit; repeat for all N slices.  Restarts with different seeds.
"""
import random
import sys
from itertools import combinations

from ortools.sat.python import cp_model
from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")
from layer_cp import rect_list, mono_rects


def sat_layer(N, K, forbidden, ridx, seed=0, phase_gen=None):
    """Any layer avoiding forbidden features, or None."""
    V = lambda y, z, c: (y * N + z) * K + c + 1
    s = Cadical195()
    for y in range(N):
        for z in range(N):
            s.add_clause([V(y, z, c) for c in range(K)])
            for a, b in combinations(range(K), 2):
                s.add_clause([-V(y, z, a), -V(y, z, b)])
    for c in range(K):
        for ri in forbidden[c]:
            y1, y2, z1, z2 = ridx[ri]
            s.add_clause([-V(y1, z1, c), -V(y1, z2, c),
                          -V(y2, z1, c), -V(y2, z2, c)])
    if phase_gen is not None:
        try:
            s.set_phases(phase_gen(V, N, K))
        except Exception:
            pass
    r = s.solve()
    m = s.get_model() if r else None
    s.delete()
    if m is None:
        return None
    S = set(v for v in m if v > 0)
    g = [[0] * N for _ in range(N)]
    for y in range(N):
        for z in range(N):
            for c in range(K):
                if V(y, z, c) in S:
                    g[y][z] = c
    return g


def cp_layer(N, K, forbidden, ridx, time_limit=5.0, workers=1, seed=0, hint=None):
    rects = rect_list(N)
    m = cp_model.CpModel()
    lit = {}
    for y in range(N):
        for z in range(N):
            for c in range(K):
                lit[y, z, c] = m.NewBoolVar("")
            m.AddExactlyOne([lit[y, z, c] for c in range(K)])
    obj = []
    for c in range(K):
        forb = forbidden[c]
        for ri, (y1, y2, z1, z2) in enumerate(rects):
            four = [lit[y1, z1, c], lit[y1, z2, c], lit[y2, z1, c], lit[y2, z2, c]]
            if ri in forb:
                m.AddBoolOr([~b for b in four])
            else:
                p = m.NewBoolVar("")
                for b in four:
                    m.AddImplication(p, b)
                m.AddBoolOr([~b for b in four] + [p])
                obj.append(p)
    m.Minimize(sum(obj))
    if hint:
        for y in range(N):
            for z in range(N):
                for c in range(K):
                    m.AddHint(lit[y, z, c], 1 if hint[y][z] == c else 0)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_search_workers = workers
    s.parameters.random_seed = seed
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, s.StatusName(st)
    g = [[None] * N for _ in range(N)]
    for y in range(N):
        for z in range(N):
            for c in range(K):
                if s.Value(lit[y, z, c]):
                    g[y][z] = c
    if any(v is None for row in g for v in row):
        return None, "INCOMPLETE"
    return g, s.StatusName(st)


def build(N, K, seed=1, cp_time=5.0, workers=1, verbose=True):
    ridx = rect_list(N)
    rng = random.Random(seed)
    forbidden = [set() for _ in range(K)]
    layers = []
    total_cap = K * len(ridx) ** 2 // K if False else K * len(ridx) * 1
    for x in range(N):
        # diversify SAT phase
        def phases(V, NN, KK, rng=rng):
            ph = []
            for y in range(NN):
                for z in range(NN):
                    c = rng.randrange(KK)
                    for c2 in range(KK):
                        ph.append(V(y, z, c2) if c2 == c else -V(y, z, c2))
            return ph
        g = sat_layer(N, K, forbidden, ridx, phase_gen=phases)
        if g is None:
            if verbose:
                print(f"  slice {x}: SAT says impossible", flush=True)
            return None, layers
        g2, st = cp_layer(N, K, forbidden, ridx, time_limit=cp_time,
                          workers=workers, seed=rng.randrange(10**6), hint=g)
        if g2 is not None:
            g = g2
        f = mono_rects(g, K)
        for (c, r) in f:
            forbidden[c].add(r)
        layers.append(g)
        if verbose:
            used = sum(len(v) for v in forbidden)
            print(f"  slice {x}: {len(f)} features, cumulative {used}", flush=True)
    return layers, layers


if __name__ == "__main__":
    from core import is_valid
    from construct import make_grid
    import json, os
    N, K = int(sys.argv[1]), int(sys.argv[2])
    cp_time = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    layers, _ = build(N, K, seed=seed, cp_time=cp_time)
    if layers and len(layers) == N:
        g = make_grid(layers, N)
        ok = is_valid(g)
        print("VALID:", ok, flush=True)
        if ok:
            os.makedirs("/home/user/prism/results", exist_ok=True)
            json.dump(g, open(f"/home/user/prism/results/K{K}_N{N}.json", "w"))
    else:
        print("FAILED at", len(layers), "layers")
