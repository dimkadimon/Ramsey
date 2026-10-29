"""Construct a valid colouring layer by layer with CP-SAT.

Each step: find a K-colouring of the N x N grid (one x-slice) that uses NONE of
the "features" (colour c, rectangle r -> all 4 corners colour c) already used by
previous slices, and among those minimise the number of new features it uses.

If all N steps succeed the stacked grid has no monochromatic box.
"""
import random
import sys
from itertools import combinations

from ortools.sat.python import cp_model

sys.path.insert(0, "/home/user/prism")


def rect_list(N):
    rects = []
    for y1, y2 in combinations(range(N), 2):
        for z1, z2 in combinations(range(N), 2):
            rects.append((y1, y2, z1, z2))
    return rects


def make_layer(N, K, forbidden, time_limit=30.0, workers=1, seed=0,
               minimise=True, fix=None):
    """forbidden: dict c -> set of rect indices that must NOT be monochromatic-c.

    Returns (grid2d or None, status).
    fix: dict (y,z)->colour  (for diversification / fixing cells)
    """
    rects = rect_list(N)
    m = cp_model.CpModel()
    lit = {}
    for y in range(N):
        for z in range(N):
            for c in range(K):
                lit[y, z, c] = m.NewBoolVar(f"l{y}_{z}_{c}")
            m.AddExactlyOne([lit[y, z, c] for c in range(K)])
    if fix:
        for (y, z), c in fix.items():
            m.Add(lit[y, z, c] == 1)

    obj = []
    for c in range(K):
        forb = forbidden.get(c, set())
        for ri, (y1, y2, z1, z2) in enumerate(rects):
            four = [lit[y1, z1, c], lit[y1, z2, c], lit[y2, z1, c], lit[y2, z2, c]]
            if ri in forb:
                m.AddBoolOr([~b for b in four])          # forbidden: never mono
            elif minimise:
                p = m.NewBoolVar("")
                for b in four:
                    m.AddImplication(p, b)
                m.AddBoolOr([~b for b in four] + [p])
                obj.append(p)
            # else: unconstrained (already impossible to collide: skip)
    if obj and minimise:
        m.Minimize(sum(obj))

    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_search_workers = workers
    s.parameters.random_seed = seed
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.UNKNOWN):
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


def mono_rects(grid, K):
    """set of (c, rect_index) monochromatic rectangles in a 2D layer."""
    N = len(grid)
    idx = {r: i for i, r in enumerate(rect_list(N))}
    out = set()
    for c in range(K):
        rows = [sum(1 << z for z in range(N) if grid[y][z] == c) for y in range(N)]
        for y1, y2 in combinations(range(N), 2):
            inter = rows[y1] & rows[y2]
            zs = [z for z in range(N) if inter >> z & 1]
            for z1, z2 in combinations(zs, 2):
                out.add((c, idx[y1, y2, z1, z2]))
    return out


def build(N, K, time_limit=30.0, seed=0, workers=1, verbose=True):
    used = {c: set() for c in range(K)}
    layers = []
    for x in range(N):
        t = time_limit * (1.0 if x < N - 1 else 2.0)
        g, st = make_layer(N, K, used, time_limit=t, workers=workers,
                           seed=seed + 17 * x, minimise=True)
        if g is None:
            if verbose:
                print(f"  layer {x}: FAILED ({st})", flush=True)
            return None, layers
        f = mono_rects(g, K)
        newf = sum(len(feats - used[c]) for c, feats in
                   ((c, {r for (cc, r) in f if cc == c}) for c in range(K)))
        for (c, r) in f:
            used[c].add(r)
        layers.append(g)
        if verbose:
            print(f"  layer {x}: {st} used {len(f)} features (new {newf}), "
                  f"total used {sum(len(v) for v in used.values())}", flush=True)
    return layers, layers


if __name__ == "__main__":
    from core import is_valid
    from construct import make_grid
    N, K = int(sys.argv[1]), int(sys.argv[2])
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    layers, done = build(N, K, tl, seed)
    if layers and len(layers) == N:
        g = make_grid(layers, N)
        print("VALID:", is_valid(g))
        import json, os
        os.makedirs("/home/user/prism/results", exist_ok=True)
        json.dump(g, open(f"/home/user/prism/results/K{K}_N{N}.json", "w"))
    else:
        print("failed after", len(layers), "layers")
