"""Greedy slice builder with restarts + backtracking."""
import json, os, random, sys, time
sys.path.insert(0, "/home/user/prism")
from itertools import combinations
from layer_ls import Layer2D, sat_slice2, improve, pairs_of
from construct import make_grid
from core import is_valid

OUT = "/home/user/prism/results"

def attempt(N, K, rng, iters, backtrack=True, max_steps=120):
    M = N*(N-1)//2
    pairs = pairs_of(N)
    forb = [set() for _ in range(K)]          # rects per colour
    layers, feats = [], []
    x = 0
    fails = 0
    while x < N:
        if max_steps and fails > max_steps:
            break
        g = sat_slice2(N, K, forb, rng=rng, conf_budget=40000)
        if g is not None:
            L = Layer2D(N, K, g)
            forbidden = []
            for c in range(K):
                S = set()
                for (y1,y2,z1,z2) in forb[c]:
                    S.add((c*M + pairs.index((y1,y2)))*M + pairs.index((z1,z2)))
                forbidden.append(S)
            g2, cnt, fs = improve(N, K, g, forbidden, iters=iters, rng=rng)
            L2 = Layer2D(N, K, g2)
            fs = L2.all_feats()
            if any((f in forbidden[f//(M*M)]) for f in fs):
                g2, L2 = g, Layer2D(N, K, g); fs = L2.all_feats()
            for f in fs:
                c = f//(M*M); r = f%(M*M); ay, az = divmod(r, M)
                forb[c].add(pairs[ay]+pairs[az])
            layers.append(g2); feats.append(fs); x += 1
        else:
            fails += 1
            if not backtrack or not layers:
                break
            d = 1 + rng.randrange(min(3, len(layers)))
            for _ in range(d):
                fs = feats.pop(); L = layers.pop(); x -= 1
                for f in fs:
                    c = f//(M*M); r = f%(M*M); ay, az = divmod(r, M)
                    forb[c].discard(pairs[ay]+pairs[az])
    return layers

if __name__ == "__main__":
    N, K = int(sys.argv[1]), int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv)>3 else 300
    iters = int(sys.argv[4]) if len(sys.argv)>4 else 3000
    t_end = time.time()+secs
    best = 0; bestlayers=None; tries=0
    while time.time() < t_end:
        tries += 1
        rng = random.Random(tries*7919+N)
        L = attempt(N, K, rng, iters)
        if len(L) > best:
            best = len(L); bestlayers = L
            print(f"  try {tries}: prefix {best}/{N}", flush=True)
        if best == N: break
    print(f"N={N} K={K} tries={tries} best prefix={best}")
    if bestlayers and len(bestlayers)==N:
        g = make_grid(bestlayers, N); ok = is_valid(g)
        print("VALID:", ok)
        if ok:
            os.makedirs(OUT, exist_ok=True)
            json.dump(g, open(f"{OUT}/K{K}_N{N}.json","w"))
