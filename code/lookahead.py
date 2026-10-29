"""Greedy slice construction with 1-step look-ahead ("rollout") for K=2.

At each slice:
  * generate M feasible candidate layers (SAT) and locally improve each,
  * for each candidate, test whether a *further* random layer can still be found
    once it is committed (a cheap feasibility probe for the future),
  * commit the candidate with the best probe score (ties -> fewest features).
This avoids the dead-end that plain greedy hits around slice 7 for N = 11.
"""
import json
import os
import random
import sys
import time

sys.path.insert(0, "/home/user/prism")
from layer_ls import Layer2D, sat_slice2, improve, pairs_of
from construct import make_grid
from core import is_valid_fast

OUT = "/home/user/prism/results"


def feats_to_rects(fs, M, pairs):
    out = []
    for f in fs:
        c = f // (M * M)
        r = f % (M * M)
        ay, az = divmod(r, M)
        out.append((c,) + pairs[ay] + pairs[az])
    return out


def forbidden_fids(rects, M, pairs, K):
    pos = {}
    for i, p in enumerate(pairs):
        pos[p] = i
    S = [set() for _ in range(K)]
    for (c, y1, y2, z1, z2) in rects:
        S[c].add((c * M + pos[(y1, y2)]) * M + pos[(z1, z2)])
    return S


def candidate(N, K, rects, rng, iters, budget):
    """One feasible, locally improved layer given forbidden rectangles."""
    rect_sets = [set() for _ in range(K)]
    for t in rects:
        rect_sets[t[0]].add(t[1:])
    g = sat_slice2(N, K, rect_sets, rng=rng, conf_budget=budget)
    if g is None:
        return None
    M = N * (N - 1) // 2
    pairs = pairs_of(N)
    fidf = forbidden_fids(rects, M, pairs, K)
    g2, cnt, fs = improve(N, K, g, fidf, iters=iters, rng=rng)
    L = Layer2D(N, K, g2)
    fs = L.all_feats()
    if any(f in fidf[f // (M * M)] for f in fs):
        g2, L = g, Layer2D(N, K, g)
        fs = L.all_feats()
    return g2, fs


def build(N, K, seed=0, M=6, iters=2000, budget=40000, verbose=True,
          deadline=None):
    rng = random.Random(seed)
    layers = []
    used = []                      # list of rect tuples
    for x in range(N):
        cands = []
        for _ in range(M):
            if deadline and time.time() > deadline:
                return None, layers
            c = candidate(N, K, used, rng, iters, budget)
            if c is not None:
                cands.append(c)
        if not cands:
            if verbose:
                print(f"  slice {x}: no candidate", flush=True)
            return None, layers
        # probe: how many of P random further layers are still constructible?
        best = None
        for g2, fs in cands:
            used2 = used + feats_to_rects(fs, N * (N - 1) // 2, pairs_of(N))
            score = 0
            for _ in range(2):
                if candidate(N, K, used2, rng, iters // 2, budget) is not None:
                    score += 1
            cand_score = (score, -len(fs))
            if best is None or cand_score > best[0]:
                best = (cand_score, g2, fs)
        _, g2, fs = best
        used = used + feats_to_rects(fs, N * (N - 1) // 2, pairs_of(N))
        layers.append(g2)
        if verbose:
            print(f"  slice {x}: chose {best[0]}, cum features "
                  f"{len(used)}", flush=True)
    return layers, layers


if __name__ == "__main__":
    N, K = int(sys.argv[1]), int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 600
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    M = int(sys.argv[5]) if len(sys.argv) > 5 else 6
    t_end = time.time() + secs
    best = 0
    tries = 0
    while time.time() < t_end:
        tries += 1
        layers, _ = build(N, K, seed=tries * 977 + seed, M=M,
                          deadline=t_end, verbose=True)
        n = len(layers) if layers else 0
        if n > best:
            best = n
            print(f"  -> try {tries}: {best}/{N}", flush=True)
        if n == N:
            g = make_grid(layers, N)
            ok = is_valid_fast(g)
            print("VALID:", ok)
            if ok:
                os.makedirs(OUT, exist_ok=True)
                json.dump(g, open(f"{OUT}/K{K}_N{N}.json", "w"))
            break
    print(f"N={N} K={K} tries={tries} best={best}/{N}")
