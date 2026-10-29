"""Layer-greedy with backtracking / restarts (needed when feature space is tight)."""
import json, os, random, sys, time
sys.path.insert(0, "/home/user/prism")
from layer_cp import rect_list, mono_rects
from layer_sat import sat_layer, cp_layer
from construct import make_grid
from core import is_valid

OUT = "/home/user/prism/results"


def build(N, K, seconds=300.0, cp_time=4.0, seed=0, verbose=True):
    rng = random.Random(seed)
    ridx = rect_list(N)
    t_end = time.time() + seconds
    best_prefix = 0
    while time.time() < t_end:
        forbidden = [set() for _ in range(K)]
        layers = []
        feats = []
        x = 0
        while x < N:
            def phases(V, NN, KK):
                ph = []
                for y in range(NN):
                    for z in range(NN):
                        c = rng.randrange(KK)
                        for c2 in range(KK):
                            ph.append(V(y, z, c2) if c2 == c else -V(y, z, c2))
                return ph
            g = sat_layer(N, K, forbidden, ridx, phase_gen=phases)
            if g is not None:
                g2, st = cp_layer(N, K, forbidden, ridx, time_limit=cp_time,
                                  seed=rng.randrange(10 ** 6), hint=g)
                if g2 is not None:
                    g = g2
                f = mono_rects(g, K)
                for (c, r) in f:
                    forbidden[c].add(r)
                layers.append(g)
                feats.append(f)
                x += 1
                best_prefix = max(best_prefix, x)
                if verbose:
                    print(f"  slice {x-1}: {len(f)} feats, total {sum(len(v) for v in forbidden)}", flush=True)
            else:
                if not layers:
                    return None, 0
                d = min(len(layers), 1 + rng.randrange(2))
                for _ in range(d):
                    f = feats.pop()
                    for (c, r) in f:
                        forbidden[c].discard(r)
                    layers.pop()
                    x -= 1
                if verbose:
                    print(f"  backtrack {d} -> at slice {x}", flush=True)
        if len(layers) == N:
            return layers, N
    return None, best_prefix


if __name__ == "__main__":
    N, K = int(sys.argv[1]), int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 300
    cpt = float(sys.argv[4]) if len(sys.argv) > 4 else 4
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    layers, bp = build(N, K, secs, cpt, seed)
    if layers:
        g = make_grid(layers, N)
        ok = is_valid(g)
        print("VALID:", ok)
        if ok:
            os.makedirs(OUT, exist_ok=True)
            json.dump(g, open(f"{OUT}/K{K}_N{N}.json", "w"))
    else:
        print("failed, best prefix", bp)
