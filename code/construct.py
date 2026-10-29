"""Fast construction of large valid colourings via the layer decomposition.

Pipeline
  1. build a POOL of K-colourings of the N x N grid with very few
     monochromatic rectangles (min-conflicts local search from random starts)
  2. find N of them whose "monochromatic rectangle" feature sets are pairwise
     disjoint  (bitmask + randomized greedy / DFS)
  3. stack them into an N x N x N colouring and verify independently.
"""
import random
import sys
from itertools import combinations

sys.path.insert(0, "/home/user/prism")


class Layer:
    """K-colouring of the N x N grid, with feature bitmask."""

    __slots__ = ("grid", "mask", "count", "N", "K")

    def __init__(self, grid, K):
        self.grid = grid
        self.N = len(grid)
        self.K = K
        self.mask, self.count = feats_and_count(grid, K)


def rect_index(N):
    pairs = list(combinations(range(N), 2))
    return {p: i for i, p in enumerate(pairs)}, len(pairs)


def feats_and_count(grid, K):
    """Return (bitmask over (colour, y1<y2, z1<z2), popcount)."""
    N = len(grid)
    idx, m = rect_index(N)
    mask = 0
    cnt = 0
    for c in range(K):
        rows = [sum(1 << z for z in range(N) if grid[y][z] == c) for y in range(N)]
        for y1, y2 in combinations(range(N), 2):
            inter = rows[y1] & rows[y2]
            nb = inter.bit_count()
            if nb >= 2:
                cnt += nb * (nb - 1) // 2
                base = (c * m + idx[y1, y2]) * m
                zs = [z for z in range(N) if inter >> z & 1]
                for z1, z2 in combinations(zs, 2):
                    mask |= 1 << (base + idx[z1, z2])
    return mask, cnt


def mono_count(grid, K):
    N = len(grid)
    tot = 0
    for c in range(K):
        rows = [sum(1 << z for z in range(N) if grid[y][z] == c) for y in range(N)]
        for y1, y2 in combinations(range(N), 2):
            nb = (rows[y1] & rows[y2]).bit_count()
            tot += nb * (nb - 1) // 2
    return tot


def minimise_layer(N, K, iters=20000, restarts=1, rng=None, start=None):
    """Min-conflicts descent on (#monochromatic rectangles)."""
    rng = rng or random.Random()
    if start is not None:
        g = [row[:] for row in start]
    else:
        g = [[rng.randrange(K) for _ in range(N)] for _ in range(N)]
    rows = [[sum(1 << z for z in range(N) if g[y][z] == c) for y in range(N)]
            for c in range(K)]

    def paircost(c, y1, y2):
        nb = (rows[c][y1] & rows[c][y2]).bit_count()
        return nb * (nb - 1) // 2

    def rowcost(c, y):
        return sum(paircost(c, y, y2) for y2 in range(N) if y2 != y)

    total = sum(rowcost(c, y) for c in range(K) for y in range(N))

    for it in range(iters):
        # pick a row pair / colour with a large number of mono rectangles
        best = None
        for _ in range(6):
            c = rng.randrange(K)
            y1, y2 = rng.sample(range(N), 2)
            z = (rows[c][y1] & rows[c][y2])
            if z.bit_count() >= 2:
                zs = [zz for zz in range(N) if z >> zz & 1]
                sel = rng.sample(zs, 2)
                if best is None:
                    best = (c, sel)
                    break
        if best is None:
            break  # no monochromatic rectangle left in this neighbourhood
        c, zs = best
        # try recolouring each of the 4 corners to another colour, take best
        bestmove = None
        for (y, zz) in [(y1, zs[0]), (y1, zs[1]), (y2, zs[0]), (y2, zs[1])]:
            if g[y][zz] != c:
                continue
            cur = g[y][zz]
            before = rowcost(cur, y)
            for c2 in range(K):
                if c2 == cur:
                    continue
                rows[cur][y] ^= 1 << zz
                rows[c2][y] |= 1 << zz
                after = rowcost(cur, y) + rowcost(c2, y)
                rows[cur][y] ^= 1 << zz
                rows[c2][y] ^= 1 << zz
                gain = before - after
                if bestmove is None or gain > bestmove[0]:
                    bestmove = (gain, y, zz, cur, c2)
        if bestmove is None or bestmove[0] <= 0:
            continue
        gain, y, zz, cur, c2 = bestmove
        rows[cur][y] ^= 1 << zz
        rows[c2][y] |= 1 << zz
        g[y][zz] = c2
        total -= gain
    return g, mono_count(g, K)


def build_pool(N, K, target, rng, iters=8000, verbose=False):
    pool = []
    seen = set()
    tries = 0
    while len(pool) < target and tries < target * 40:
        tries += 1
        g, cnt = minimise_layer(N, K, iters=iters, rng=rng)
        key = tuple(tuple(r) for r in g)
        if key in seen:
            continue
        seen.add(key)
        pool.append(Layer(g, K))
    if verbose:
        pool.sort(key=lambda L: L.count)
        print(f"pool N={N} K={K}: {len(pool)} layers, "
              f"mono-rect counts {pool[0].count}..{pool[-1].count}", flush=True)
    return pool


def pack(pool, need, rng, tries=20000):
    """Pick `need` layers with pairwise disjoint feature masks (randomized greedy)."""
    # prefer layers with few features
    cand = sorted(pool, key=lambda L: L.count)
    if len(cand) < need:
        return None
    for t in range(tries):
        chosen = []
        used = 0
        order = cand if t == 0 else rng.sample(cand, len(cand))
        for L in order:
            if L.mask & used:
                continue
            chosen.append(L)
            used |= L.mask
            if len(chosen) == need:
                return chosen
    return None


def make_grid(layers, N):
    return [[[layers[x][y][z] for z in range(N)] for y in range(N)] for x in range(N)]


if __name__ == "__main__":
    from core import is_valid
    N, K = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    pool = build_pool(N, K, target=max(60, 4 * N), rng=rng, verbose=True)
    ch = pack(pool, N, rng)
    print("packed:", ch is not None)
