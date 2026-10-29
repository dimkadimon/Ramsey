"""Local search over the base colouring f for the shift-vector construction.

Objective:  sum over G-orbits of C(#monochromatic rectangles of f in that orbit, 2).
Zero  <=>  at most one mono rectangle per orbit  <=>  the lifted [N]^3 colouring
c(x,y,z) = f(y - x*a, z - x*b) is prism-free.
"""
import json
import os
import random
import sys
import time
from itertools import combinations

sys.path.insert(0, "/home/user/prism")
from shiftvec import key_of, true_order


class Prob:
    def __init__(self, N, a, b, grid):
        self.N, self.a, self.b = N, a, b
        self.rects = [(y1, y2, z1, z2)
                      for y1, y2 in combinations(range(N), 2)
                      for z1, z2 in combinations(range(N), 2)]
        self.rid = {r: i for i, r in enumerate(self.rects)}
        # Orbit structure.  A rectangle may be FIXED by a nontrivial shift
        # (then it appears in several slices at once), so orbits with size < N
        # must contain NO monochromatic rectangle at all.
        self.rep = {}
        self.hard = set()
        seen = set()
        self.orbit_size = {}
        for c in (0, 1):
            for i, r in enumerate(self.rects):
                if (c, i) in seen:
                    continue
                y1, y2, z1, z2 = r
                orb = set()
                for t in range(N):
                    u = ((y1 + t * a) % N, (y2 + t * a) % N,
                         (z1 + t * b) % N, (z2 + t * b) % N)
                    orb.add((c, min(u[0], u[1]), max(u[0], u[1]),
                             min(u[2], u[3]), max(u[2], u[3])))
                rep = min(orb)
                self.orbit_size[rep] = len(orb)
                for o in orb:
                    cc, p1, p2, q1, q2 = o
                    j = self.rid[(p1, p2, q1, q2)]
                    self.rep[cc, j] = rep
                    seen.add((cc, j))
                    if len(orb) < N:
                        self.hard.add((cc, j))
        # cells touching each rect
        self.through = {}
        for (y, z) in [(y, z) for y in range(N) for z in range(N)]:
            lst = []
            for y2 in range(N):
                if y2 == y:
                    continue
                for z2 in range(N):
                    if z2 == z:
                        continue
                    r = (min(y, y2), max(y, y2), min(z, z2), max(z, z2))
                    lst.append(self.rid[r])
            self.through[y, z] = lst
        self.g = [row[:] for row in grid]
        self.mask = [[0] * N for _ in range(2)]
        for y in range(N):
            for z in range(N):
                self.mask[self.g[y][z]][y] |= 1 << z
        self.cnt = {}
        self.mono = {}     # (c, rect) -> bool
        for c in (0, 1):
            for i, (y1, y2, z1, z2) in enumerate(self.rects):
                m = self.mask[c][y1] & self.mask[c][y2]
                v = bool(m >> z1 & 1) and bool(m >> z2 & 1)
                self.mono[c, i] = v
                if v:
                    k = self.rep[c, i]
                    self.cnt[k] = self.cnt.get(k, 0) + 1
        self.obj = self.score()

    def score(self):
        v = sum(c * (c - 1) // 2 for c in self.cnt.values())
        v += 50 * sum(1 for k, m in self.mono.items() if m and k in self.hard)
        return v

    def flip_delta(self, y, z):
        c0 = self.g[y][z]
        c1 = 1 - c0
        touched = self.through[y, z]
        before = {}
        for c in (c0, c1):
            for i in touched:
                if self.mono[c, i]:
                    k = self.rep[c, i]
                    before[k] = before.get(k, 0) + 1
        # apply
        self.mask[c0][y] &= ~(1 << z)
        self.mask[c1][y] |= 1 << z
        after = {}
        for c in (c0, c1):
            for i in touched:
                y1, y2, z1, z2 = self.rects[i]
                m = self.mask[c][y1] & self.mask[c][y2]
                v = bool(m >> z1 & 1) and bool(m >> z2 & 1)
                if v:
                    k = self.rep[c, i]
                    after[k] = after.get(k, 0) + 1
        self.mask[c0][y] |= 1 << z
        self.mask[c1][y] &= ~(1 << z)
        d = 0
        for k, n in after.items():
            old = self.cnt.get(k, 0)
            if n > old:
                d += n - old if False else old
        for k, n in before.items():
            cur = self.cnt.get(k, 0)
            newn = cur - n + after.get(k, 0)
            d += newn * (newn - 1) // 2 - cur * (cur - 1) // 2
        for k, n in after.items():
            if k not in before:
                cur = self.cnt.get(k, 0)
                d += (cur + n) * (cur + n - 1) // 2 - cur * (cur - 1) // 2
        return d

    def apply(self, y, z):
        c0 = self.g[y][z]
        c1 = 1 - c0
        touched = self.through[y, z]
        self.mask[c0][y] &= ~(1 << z)
        self.mask[c1][y] |= 1 << z
        self.g[y][z] = c1
        for c in (c0, c1):
            for i in touched:
                y1, y2, z1, z2 = self.rects[i]
                m = self.mask[c][y1] & self.mask[c][y2]
                v = bool(m >> z1 & 1) and bool(m >> z2 & 1)
                if v == self.mono[c, i]:
                    continue
                k = self.rep[c, i]
                cur = self.cnt.get(k, 0)
                hard = (c, i) in self.hard
                if v:
                    self.obj += cur + (50 if hard else 0)
                    self.cnt[k] = cur + 1
                else:
                    self.obj -= (cur - 1) + (50 if hard else 0)
                    self.cnt[k] = cur - 1
                self.mono[c, i] = v


def search(N, a, b, secs=30, seed=0, grid=None, verbose=False):
    rng = random.Random(seed)
    if grid is None:
        grid = [[rng.randrange(2) for _ in range(N)] for _ in range(N)]
    P = Prob(N, a, b, grid)
    best, bestg = P.obj, [r[:] for r in P.g]
    tabu = {}
    it = 0
    t_end = time.time() + secs
    while time.time() < t_end and best > 0:
        it += 1
        bestmove = None
        for _ in range(8):
            y, z = rng.randrange(N), rng.randrange(N)
            if tabu.get((y, z), 0) > it:
                continue
            d = P.flip_delta(y, z)
            if bestmove is None or d < bestmove[0]:
                bestmove = (d, y, z)
        if bestmove is None:
            continue
        d, y, z = bestmove
        if d <= 0:
            P.apply(y, z)
            tabu[y, z] = it + 5 + rng.randrange(7)
            if P.obj < best:
                best, bestg = P.obj, [r[:] for r in P.g]
                if verbose:
                    print(f"   it={it} obj={best}", flush=True)
        else:
            y, z = rng.randrange(N), rng.randrange(N)
            P.apply(y, z)
    return best, bestg, it


if __name__ == "__main__":
    from shiftvec import lift
    from core import is_valid_fast
    N = int(sys.argv[1])
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 20
    slopes = [tuple(map(int, s.split(","))) for s in sys.argv[3:]] if len(sys.argv) > 3 else None
    if slopes is None:
        slopes = [(a, b) for a in range(1, N) for b in range(1, N)
                  if true_order(a, b, N) == N]
    print(f"N={N}: {len(slopes)} slopes, {secs}s each", flush=True)
    for (a, b) in slopes:
        bo, bg = None, None
        for seed in range(3):
            o, g, it = search(N, a, b, secs=secs / 3, seed=seed)
            if bo is None or o < bo:
                bo, bg = o, g
            if bo == 0:
                break
        print(f"  v=({a},{b}): best obj={bo}", flush=True)
        if bo == 0:
            grid = lift(bg, N, a, b)
            ok = is_valid_fast(grid)
            print(f"  v=({a},{b}): lifted valid={ok}", flush=True)
            if ok:
                os.makedirs("/home/user/prism/results", exist_ok=True)
                json.dump(grid, open(f"/home/user/prism/results/K2_N{N}.json", "w"))
                json.dump(bg, open(f"/home/user/prism/results/K2_N{N}_base2d.json", "w"))
                json.dump([a, b], open(f"/home/user/prism/results/K2_N{N}_shiftvec.json", "w"))
                print(f"SOLVED N={N} with v=({a},{b})", flush=True)
                break


def breakout(N, a, b, secs=60, seed=0, grid=None, verbose=False, bump=1.0):
    """Weighted breakout search: violated orbits accumulate weight, and moves are
    chosen by weighted objective; weights are smoothed periodically."""
    rng = random.Random(seed)
    if grid is None:
        grid = [[rng.randrange(2) for _ in range(N)] for _ in range(N)]
    P = Prob(N, a, b, grid)
    w = {}
    def wt(k):
        return w.get(k, 1.0)
    best, bestg = P.obj, [r[:] for r in P.g]
    it = 0
    t_end = time.time() + secs
    while time.time() < t_end and best > 0:
        it += 1
        cells = [(y, z) for y in range(N) for z in range(N)]
        rng.shuffle(cells)
        bestmove = None
        for (y, z) in cells:
            c0 = P.g[y][z]
            c1 = 1 - c0
            touched = P.through[y, z]
            delta = 0.0
            # weighted delta
            before = {}
            for c in (c0, c1):
                for i in touched:
                    if P.mono[c, i]:
                        k = P.rep[c, i]
                        before[k] = before.get(k, 0) + 1
            P.mask[c0][y] &= ~(1 << z)
            P.mask[c1][y] |= 1 << z
            after = {}
            for c in (c0, c1):
                for i in touched:
                    y1, y2, z1, z2 = P.rects[i]
                    m = P.mask[c][y1] & P.mask[c][y2]
                    if (m >> z1 & 1) and (m >> z2 & 1):
                        k = P.rep[c, i]
                        after[k] = after.get(k, 0) + 1
            P.mask[c0][y] |= 1 << z
            P.mask[c1][y] &= ~(1 << z)
            for k in set(list(before) + list(after)):
                cnt = P.cnt.get(k, 0)
                nb, na = before.get(k, 0), after.get(k, 0)
                cur = cnt * (cnt - 1) // 2
                new = (cnt - nb + na) * (cnt - nb + na - 1) // 2
                delta += wt(k) * (new - cur)
            for c in (c0, c1):
                for i in touched:
                    if (c, i) not in P.hard:
                        continue
                    if P.mono[c, i]:
                        delta -= 50
            for c in (c0, c1):
                for i in touched:
                    if (c, i) not in P.hard:
                        continue
                    y1, y2, z1, z2 = P.rects[i]
                    cwas = P.g[y][z]
                    P.mask[cwas][y] &= ~(1 << z)
                    P.mask[1 - cwas][y] |= 1 << z
                    m = P.mask[c][y1] & P.mask[c][y2]
                    if (m >> z1 & 1) and (m >> z2 & 1):
                        delta += 50
                    P.mask[cwas][y] |= 1 << z
                    P.mask[1 - cwas][y] &= ~(1 << z)
            if bestmove is None or delta < bestmove[0]:
                bestmove = (delta, y, z)
        d, y, z = bestmove
        if d < 0 or rng.random() < 0.01:
            P.apply(y, z)
            if P.obj < best:
                best, bestg = P.obj, [r[:] for r in P.g]
                if verbose:
                    print(f"   it={it} obj={best}", flush=True)
        else:
            for k, n in P.cnt.items():
                if n >= 2:
                    w[k] = wt(k) + bump
            if it % 500 == 0:
                for k in list(w):
                    w[k] = max(1.0, w[k] * 0.75)
    return best, bestg, it
