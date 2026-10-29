"""Scalable slice builder: SAT feasibility + bitmask local search to keep the
number of NEW features low.  Works where the CP-SAT objective model would be
too big (N > ~20).
"""
import random
import sys
import time
from itertools import combinations

from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")


def pairs_of(N):
    return list(combinations(range(N), 2))


class Layer2D:
    """K-colouring of the N x N grid with fast mono-rectangle bookkeeping."""

    def __init__(self, N, K, grid):
        self.N, self.K = N, K
        self.grid = [row[:] for row in grid]
        self.M = N * (N - 1) // 2
        self.pairs = pairs_of(N)
        self.pidx = {p: i for i, p in enumerate(self.pairs)}
        self.thr = [[] for _ in range(N)]
        for i, (a, b) in enumerate(self.pairs):
            self.thr[a].append((i, a, b))
            self.thr[b].append((i, a, b))
        self.masks = [[0] * N for _ in range(K)]
        for y in range(N):
            for z in range(N):
                self.masks[self.grid[y][z]][y] |= 1 << z

    def fid(self, c, ay, az):
        return (c * self.M + ay) * self.M + az

    def feats_at(self, y0, z0, c):
        """set of feature ids of colour c whose rectangle passes through (y0,z0)."""
        g = self.grid
        if g[y0][z0] != c:
            return set()
        M = self.M
        out = set()
        ylist = [(ay, a, b) for (ay, a, b) in self.thr[y0]
                 if g[a][z0] == c and g[b][z0] == c]
        if not ylist:
            return out
        zlist = self.thr[z0]
        for ay, a, b in ylist:
            base = (c * M + ay) * M
            for az, za, zb in zlist:
                if (g[y0][za] == c and g[y0][zb] == c and g[a][za] == c and
                        g[a][zb] == c and g[b][za] == c and g[b][zb] == c):
                    out.add(base + az)
        return out

    def all_feats(self):
        out = []
        for c in range(self.K):
            for ay, (y1, y2) in enumerate(self.pairs):
                inter = self.masks[c][y1] & self.masks[c][y2]
                if inter.bit_count() >= 2:
                    zs = [z for z in range(self.N) if inter >> z & 1]
                    base = (c * self.M + ay) * self.M
                    for z1, z2 in combinations(zs, 2):
                        out.append(base + self.pidx[(z1, z2)])
        return out

    def count(self):
        tot = 0
        for c in range(self.K):
            for y1, y2 in self.pairs:
                nb = (self.masks[c][y1] & self.masks[c][y2]).bit_count()
                tot += nb * (nb - 1) // 2
        return tot

    def move(self, y0, z0, cnew):
        cold = self.grid[y0][z0]
        self.masks[cold][y0] &= ~(1 << z0)
        self.masks[cnew][y0] |= 1 << z0
        self.grid[y0][z0] = cnew


def improve(N, K, grid, forbidden, iters=4000, rng=None, deadline=None):
    """Hill-climb: reduce #mono rects, never creating a forbidden feature."""
    import time
    rng = rng or random.Random()
    L = Layer2D(N, K, grid)
    for it in range(iters):
        if deadline and time.time() > deadline:
            break
        feats = L.all_feats()
        if not feats:
            break
        rng.shuffle(feats)
        improved = False
        for f in feats:
            c = f // (L.M * L.M)
            r = f % (L.M * L.M)
            ay, az = divmod(r, L.M)
            y1, y2 = L.pairs[ay]
            z1, z2 = L.pairs[az]
            y0 = rng.choice((y1, y2))
            z0 = rng.choice((z1, z2))
            cur = L.grid[y0][z0]
            best = (0, None)
            before = L.feats_at(y0, z0, cur)
            for c2 in range(K):
                if c2 == cur:
                    continue
                L.move(y0, z0, c2)
                after = L.feats_at(y0, z0, c2)
                newf = after - before
                bad = any((ff in forbidden[ff // (L.M * L.M)]) for ff in newf)
                gain = len(before) - len(f if False else newf)
                L.move(y0, z0, cur)
                if bad:
                    continue
                if gain > best[0]:
                    best = (gain, c2)
            if best[1] is not None:
                L.move(y0, z0, best[1])
                improved = True
                break
        if not improved:
            break
    return L.grid, L.count(), L.all_feats()


def sat_slice(N, K, forbidden, rng=None, aux_per_feature=True):
    """SAT: K-colour the N x N grid avoiding all forbidden features."""
    V = lambda y, z, c: (y * N + z) * K + c + 1
    s = Cadical195()
    for y in range(N):
        for z in range(N):
            s.add_clause([V(y, z, c) for c in range(K)])
            for a, b in combinations(range(K), 2):
                s.add_clause([-V(y, z, a), -V(y, z, b)])
    for c in range(K):
        M = N * (N - 1) // 2
        for f in forbidden[c]:
            r = f % (M * M)
            ay, az = divmod(r, M)
            y1, y2 = pairs_of(N)[ay] if False else (None, None)
    # (rebuilt properly below)
    s.delete()
    return None


def sat_slice2(N, K, forbidden_rects, rng=None, conf_budget=None):
    """forbidden_rects: dict colour -> set of (y1,y2,z1,z2)."""
    V = lambda y, z, c: (y * N + z) * K + c + 1
    s = Cadical195()
    for y in range(N):
        for z in range(N):
            s.add_clause([V(y, z, c) for c in range(K)])
            for a, b in combinations(range(K), 2):
                s.add_clause([-V(y, z, a), -V(y, z, b)])
    for c in range(K):
        for (y1, y2, z1, z2) in forbidden_rects[c]:
            s.add_clause([-V(y1, z1, c), -V(y1, z2, c),
                          -V(y2, z1, c), -V(y2, z2, c)])
    if rng is not None:
        ph = []
        for y in range(N):
            for z in range(N):
                c = rng.randrange(K)
                for c2 in range(K):
                    ph.append(V(y, z, c2) if c2 == c else -V(y, z, c2))
        try:
            s.set_phases(ph)
        except Exception:
            pass
    if conf_budget:
        s.conf_budget(conf_budget)
        r = s.solve_limited()
    else:
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


def build(N, K, seed=0, iters=3000, verbose=True, rng=None, budget=None, deadline=None):
    rng = rng or random.Random(seed)
    M = N * (N - 1) // 2
    pairs = pairs_of(N)
    forb_rect = [set() for _ in range(K)]
    layers = []
    for x in range(N):
        if deadline and time.time() > deadline:
            return layers
        g = sat_slice2(N, K, forb_rect, rng=rng, conf_budget=budget)
        if g is None:
            if verbose:
                print(f"  slice {x}: UNSAT", flush=True)
            return layers
        L = Layer2D(N, K, g)
        fids = [L.fid(c, ay, az) for c in range(K) for ay in range(M) for az in range(M)]
        forbidden = [set(fids[c * M * M:(c + 1) * M * M]) & set() for c in range(K)]
        # forbidden as fid sets, derived from forb_rect
        forbidden = []
        for c in range(K):
            S = set()
            for (y1, y2, z1, z2) in forb_rect[c]:
                S.add((c * M + pairs.index((y1, y2))) * M + pairs.index((z1, z2)))
            forbidden.append(S)
        g2, cnt, fs = improve(N, K, g, forbidden, iters=iters, rng=rng)
        # safety: verify the improved layer is still legal, else keep the SAT one
        L2 = Layer2D(N, K, g2)
        legal = True
        for f in L2.all_feats():
            c = f // (M * M)
            if f in forbidden[c]:
                legal = False
                break
        if not legal:
            g2 = g
            L2 = Layer2D(N, K, g)
            fs = L2.all_feats()
        for f in fs:
            c = f // (M * M)
            r = f % (M * M)
            ay, az = divmod(r, M)
            forb_rect[c].add(pairs[ay] + pairs[az])
        layers.append(g2)
        if verbose:
            print(f"  slice {x}: {len(fs)} feats, cumulative "
                  f"{sum(len(s) for s in forb_rect)}/{K*M*M}", flush=True)
    return layers


if __name__ == "__main__":
    from construct import make_grid
    from core import is_valid
    import json, os
    N, K = int(sys.argv[1]), int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    layers = build(N, K, seed=seed)
    if layers:
        g = make_grid(layers, N)
        ok = is_valid(g)
        print("VALID:", ok)
        if ok:
            os.makedirs("/home/user/prism/results", exist_ok=True)
            json.dump(g, open(f"/home/user/prism/results/K{K}_N{N}.json", "w"))
    else:
        print("FAILED")
