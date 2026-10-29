"""Diagonal-shift construction for K = 2, with local search.

Take a base 2-colouring f of the N x N grid and let

        c(x,y,z) = f( (y-x) mod N , (z-x) mod N )

so slice x is the base layer shifted diagonally by x; the N slices are the N
diagonal shifts.  A prism over slices x1,x2 (d = x2-x1 != 0) is monochromatic
iff f has two monochromatic rectangles related by the diagonal shift (d,d).

So we need: all monochromatic rectangles of f lie in distinct *diagonal orbits*.
Orbit invariant of a rectangle (c, {y1,y2}, {z1,z2}):
        ( c, (z2-z1) mod N, { (y1-z1) mod N, (y2-z1) mod N } ).
Minimise   sum over keys of C(count,2)   down to zero.
"""
import json
import os
import random
import sys
import time

sys.path.insert(0, "/home/user/prism")


class Base:
    def __init__(self, N, K, grid):
        self.N, self.K = N, K
        self.g = [r[:] for r in grid]
        self.rows = [[0] * N for _ in range(K)]
        for y in range(N):
            for z in range(N):
                self.rows[self.g[y][z]][y] |= 1 << z
        self.cnt = {}
        self.obj = 0
        self.pairfeat = {}          # (c,y1,y2) -> list of keys
        self._build_all()

    def key(self, c, y1, y2, z1, z2):
        N = self.N
        return (c, (z2 - z1) % N,
                frozenset(((y1 - z1) % N, (y2 - z1) % N)))

    def feats_of_pair(self, c, y1, y2):
        N = self.N
        inter = self.rows[c][y1] & self.rows[c][y2]
        out = []
        zs = [z for z in range(N) if inter >> z & 1]
        for i in range(len(zs)):
            for j in range(i + 1, len(zs)):
                out.append(self.key(c, y1, y2, zs[i], zs[j]))
        return out

    def _build_all(self):
        self.cnt = {}
        self.pairfeat = {}
        for c in range(self.K):
            for y1 in range(self.N):
                for y2 in range(y1 + 1, self.N):
                    fs = self.feats_of_pair(c, y1, y2)
                    self.pairfeat[c, y1, y2] = fs
                    for k in fs:
                        self.cnt[k] = self.cnt.get(k, 0) + 1
        self.obj = sum(c * (c - 1) // 2 for c in self.cnt.values())

    def flip(self, y, z):
        """returns delta in objective"""
        N = self.N
        cold = self.g[y][z]
        cnew = 1 - cold
        # affected colour/row-pair features
        affected = []
        for c in (cold, cnew):
            for y2 in range(N):
                if y2 == y:
                    continue
                a, b = (y, y2) if y < y2 else (y2, y)
                affected.append((c, a, b))
        before = {}
        for key3 in affected:
            for k in self.pairfeat[key3]:
                before[k] = before.get(k, 0) + 1
        # apply
        self.rows[cold][y] &= ~(1 << z)
        self.rows[cnew][y] |= 1 << z
        self.g[y][z] = cnew
        after = {}
        newfeats = {}
        for key3 in affected:
            fs = self.feats_of_pair(*key3)
            newfeats[key3] = fs
            for k in fs:
                after[k] = after.get(k, 0) + 1
        d = 0
        for k, n in after.items():
            old = self.cnt.get(k, 0)
            if n > old:
                d += old          # C(old+1,2)-C(old,2) = old  (for +1)
            self.cnt[k] = n
        for k, n in before.items():
            if k not in after:
                old = self.cnt.get(k, 0)
                self.cnt[k] = 0
                d -= (old - 1)
        for key3, fs in newfeats.items():
            self.pairfeat[key3] = fs
        self.obj += d
        return d

    def undo(self, y, z):
        self.flip(y, z)


def search(N, K=2, secs=60, seed=0, verbose=True):
    rng = random.Random(seed)
    g = [[rng.randrange(K) for _ in range(N)] for _ in range(N)]
    B = Base(N, K, g)
    best = B.obj
    bestg = [r[:] for r in B.g]
    tabu = {}
    it = 0
    t_end = time.time() + secs
    while time.time() < t_end and best > 0:
        it += 1
        # pick a duplicated key
        dups = [k for k, c in B.cnt.items() if c >= 2]
        if not dups:
            break
        k = rng.choice(dups)
        c, dz, ypair = k
        yp = sorted(ypair)
        bestmove = None
        for trial in range(6):
            y = rng.choice(yp)
            # a z making this feature present: z with both rows colour c
            inter = B.rows[c][yp[0]] & B.rows[c][yp[1]]
            zs = [z for z in range(N) if inter >> z & 1]
            if not zs:
                continue
            z = rng.choice(zs)
            if B.g[y][z] != c:
                continue
            key = (y, z, 1 - c)
            if tabu.get(key, 0) > it:
                continue
            d = B.flip(y, z)
            B.flip(y, z)          # undo
            if bestmove is None or d < bestmove[0]:
                bestmove = (d, y, z)
        if bestmove is None:
            continue
        d, y, z = bestmove
        if d <= 0:
            B.flip(y, z)
            tabu[y, z, B.g[y][z]] = it + 6 + rng.randrange(8)
            if B.obj < best:
                best = B.obj
                bestg = [r[:] for r in B.g]
                if verbose:
                    print(f"  it={it} obj={best}", flush=True)
        else:
            # random walk to escape
            y2 = rng.randrange(N)
            z2 = rng.randrange(N)
            B.flip(y2, z2)
    return best, bestg, it


if __name__ == "__main__":
    from core import is_valid_fast
    OUT = "/home/user/prism/results"
    for N in map(int, sys.argv[1:]):
        secs = float(os.environ.get("SECS", "60"))
        bb, bg = None, None
        for seed in range(3):
            b, g, it = search(N, secs=secs / 3, seed=seed)
            print(f"N={N} seed={seed}: obj={b} ({it} iters)", flush=True)
            if bb is None or b < bb:
                bb, bg = b, g
            if bb == 0:
                break
        if bb == 0:
            grid = [[[bg[(y - x) % N][(z - x) % N] for z in range(N)]
                     for y in range(N)] for x in range(N)]
            ok = is_valid_fast(grid)
            print(f"N={N}: built grid valid={ok}", flush=True)
            if ok:
                os.makedirs(OUT, exist_ok=True)
                json.dump(grid, open(f"{OUT}/K2_N{N}.json", "w"))
        else:
            print(f"N={N}: best obj {bb}", flush=True)
