"""Hybrid: layer-greedy prefix  +  tabu search on the rest."""
import json, os, random, sys, time
sys.path.insert(0, "/home/user/prism")
from layer_cp import rect_list, mono_rects
from layer_sat import sat_layer, cp_layer
from tabu3d import weighted_search
from construct import make_grid
from core import is_valid

OUT = "/home/user/prism/results"


def greedy_prefix(N, K, t_end, cp_time, rng, verbose=True):
    ridx = rect_list(N)
    forbidden = [set() for _ in range(K)]
    layers, feats = [], []
    x = 0
    while x < N and time.time() < t_end:
        def phases(V, NN, KK):
            ph = []
            for y in range(NN):
                for z in range(NN):
                    c = rng.randrange(KK)
                    for c2 in range(KK):
                        ph.append(V(y, z, c2) if c2 == c else -V(y, z, c2))
            return ph
        g = sat_layer(N, K, forbidden, ridx, phase_gen=phases)
        if g is None:
            break
        g2, st = cp_layer(N, K, forbidden, ridx, time_limit=cp_time,
                          seed=rng.randrange(10**6), hint=g)
        if g2 is not None:
            g = g2
        f = mono_rects(g, K)
        for (c, r) in f:
            forbidden[c].add(r)
        layers.append(g); feats.append(f); x += 1
        if verbose:
            print(f"  greedy slice {x-1}: {len(f)} feats", flush=True)
    return layers


def pad(N, K, layers, rng):
    g = [[[rng.randrange(K) for _ in range(N)] for _ in range(N)] for _ in range(N)]
    for i, L in enumerate(layers):
        for y in range(N):
            for z in range(N):
                g[i][y][z] = L[y][z]
    return g


if __name__ == "__main__":
    N, K = int(sys.argv[1]), int(sys.argv[2])
    gtime = float(sys.argv[3]); stime = float(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    rng = random.Random(seed)
    t0 = time.time()
    pre = greedy_prefix(N, K, t0 + gtime, 4.0, rng)
    print(f"prefix {len(pre)}/{N}", flush=True)
    g = pad(N, K, pre, rng)
    st, best, it = weighted_search(N, K, stime, seed=seed, grid=g, verbose=True)
    print(f"local search best dupes = {best}", flush=True)
    if best == 0:
        ok = is_valid(st.g)
        print("VALID:", ok)
        if ok:
            os.makedirs(OUT, exist_ok=True)
            json.dump(st.g, open(f"{OUT}/K{K}_N{N}.json", "w"))
    else:
        print("failed (dupes", best, ")")
