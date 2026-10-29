"""Min-conflicts / tabu search for "no monochromatic axis-aligned box" colourings.

Objective: number of *duplicated features*.  A feature is (colour c, rectangle
(y1<y2, z1<z2) in the yz-plane).  Slice x "uses" feature (c,r) if slice x is
monochromatic in colour c on r.  A monochromatic box exists  <=>  some feature
is used by two different slices.  So minimise #{features used >= 2 times}.

One move = recolour a single cell of one slice.
"""
import random
import sys
from itertools import combinations

sys.path.insert(0, "/home/user/prism")


class State:
    def __init__(self, N, K, rng, grid=None):
        self.N, self.K, self.rng = N, K, rng
        self.M = N * (N - 1) // 2
        self.pairs = list(combinations(range(N), 2))
        self.pidx = {p: i for i, p in enumerate(self.pairs)}
        # pairs through a coordinate
        self.thr = [[] for _ in range(N)]
        for i, (a, b) in enumerate(self.pairs):
            self.thr[a].append((i, a, b))
            self.thr[b].append((i, a, b))
        if grid is None:
            self.g = [[[rng.randrange(K) for _ in range(N)] for _ in range(N)]
                      for _ in range(N)]
        else:
            self.g = [row[:] for row in grid]
        self.count = {}
        self.lfeat = [set() for _ in range(N)]
        self.dupes = 0
        self._rebuild()

    def fid(self, c, ay, az):
        return (c * self.M + ay) * self.M + az

    def feats_at(self, x, y0, z0, c):
        """set of feature ids (colour c) of slice x whose rect passes (y0,z0)."""
        g = self.g[x]
        if g[y0][z0] != c:
            return set()
        out = set()
        M = self.M
        # y-pairs through y0 with both cells (pair, z0) colour c
        ylist = [(ay, a, b) for (ay, a, b) in self.thr[y0] if g[a][z0] == c and g[b][z0] == c]
        if not ylist:
            return out
        zlist = [(az, a, b) for (az, a, b) in self.thr[z0]]
        for ay, a, b in ylist:
            base = (c * M + ay) * M
            for az, za, zb in zlist:
                if g[y0][za] == c and g[y0][zb] == c and g[a][za] == c and \
                        g[a][zb] == c and g[b][za] == c and g[b][zb] == c:
                    out.add(base + az)
        return out

    def _rebuild(self):
        self.count = {}
        self.lfeat = [set() for _ in range(self.N)]
        N, K, M = self.N, self.K, self.M
        for x in range(N):
            g = self.g[x]
            for c in range(K):
                rows = [sum(1 << z for z in range(N) if g[y][z] == c) for y in range(N)]
                for ay, (y1, y2) in enumerate(self.pairs):
                    inter = rows[y1] & rows[y2]
                    zs = [z for z in range(N) if inter >> z & 1]
                    base = (c * M + ay) * M
                    for az, (z1, z2) in enumerate(self.pairs):
                        pass
                    zd = {p: i for i, p in enumerate(self.pairs)}
                    for z1, z2 in combinations(zs, 2):
                        f = base + zd[(z1, z2)]
                        self.lfeat[x].add(f)
                        self.count[f] = self.count.get(f, 0) + 1
        self.dupes = sum(1 for v in self.count.values() if v >= 2)

    def dup_list(self):
        return [f for f, v in self.count.items() if v >= 2]

    def delta(self, x, y0, z0, cnew):
        gold = self.g[x][y0][z0]
        if gold == cnew:
            return 0, None, None
        before = self.feats_at(x, y0, z0, gold) | self.feats_at(x, y0, z0, cnew)
        self.g[x][y0][z0] = cnew
        after = self.feats_at(x, y0, z0, gold) | self.feats_at(x, y0, z0, cnew)
        self.g[x][y0][z0] = gold
        d = 0
        for f in after - before:
            if self.count.get(f, 0) == 1:
                d += 1
        for f in before - after:
            if self.count.get(f, 0) == 2:
                d -= 1
        return d, before, after

    def commit(self, x, y0, z0, cnew, before, after):
        self.g[x][y0][z0] = cnew
        for f in after - before:
            cnt = self.count.get(f, 0)
            self.count[f] = cnt + 1
            self.lfeat[x].add(f)
            if cnt == 1:
                self.dupes += 1
        for f in before - after:
            cnt = self.count.get(f, 0)
            self.count[f] = cnt - 1
            self.lfeat[x].discard(f)
            if cnt == 2:
                self.dupes -= 1


def search(N, K, seconds=60.0, seed=0, grid=None, tabu_tenure=10, verbose=True):
    import time
    rng = random.Random(seed)
    t_end = time.time() + seconds
    st = State(N, K, rng, grid)
    best = st.dupes
    bestg = [row[:] for row in st.g]
    tabu = {}
    it = 0
    pairs = st.pairs
    while time.time() < t_end:
        dl = st.dup_list()
        if not dl:
            return st, 0, it
        it += 1
        f = rng.choice(dl)
        users = [x for x in range(N) if f in st.lfeat[x]]
        if not users:
            st._rebuild()
            continue
        x = rng.choice(users)
        c, y1, y2, z1, z2 = decode(f, N)
        y0, z0 = rng.choice((y1, y2)), rng.choice((z1, z2))
        if st.g[x][y0][z0] != c:
            st._rebuild()
            continue
        bestm = None
        for c2 in range(K):
            if c2 == c:
                continue
            d, before, after = st.delta(x, y0, z0, c2)
            if tabu.get((x, y0, z0, c2), 0) > it and st.dupes + d >= best:
                continue
            if bestm is None or d < bestm[0]:
                bestm = (d, c2, before, after)
        if bestm is None:
            continue
        d, c2, before, after = bestm
        st.commit(x, y0, z0, c2, before, after)
        tabu[(x, y0, z0, c)] = it + tabu_tenure + rng.randrange(6)
        if st.dupes < best:
            best = st.dupes
            bestg = [row[:] for row in st.g]
            if verbose:
                print(f"  it={it} best={best} (t={time.time()-t_end+seconds:.0f}s)",
                      flush=True)
    st.g = bestg
    st._rebuild()
    return st, best, it


def decode(f, N):
    M = N * (N - 1) // 2
    c = f // (M * M)
    r = f % (M * M)
    a, b = divmod(r, M)
    pairs = list(combinations(range(N), 2))
    y1, y2 = pairs[a]
    z1, z2 = pairs[b]
    return c, y1, y2, z1, z2


if __name__ == "__main__":
    from core import is_valid, bad_boxes
    N, K = int(sys.argv[1]), int(sys.argv[2])
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 30
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    st, best, it = search(N, K, secs, seed)
    print(f"N={N} K={K} best dupes={best} iters={it}")
    print("valid:", is_valid(st.g))


def weighted_search(N, K, seconds=60.0, seed=0, grid=None, verbose=True,
                    bump=1.0, smooth_every=2000, walk_p=0.02):
    """Breakout local search: weights on features that keep being duplicated."""
    import time
    rng = random.Random(seed)
    t_end = time.time() + seconds
    st = State(N, K, rng, grid)
    w = {}
    def wt(f):
        return w.get(f, 1.0)
    best = st.dupes
    bestg = [row[:] for row in st.g]
    it = 0
    since_best = 0
    while time.time() < t_end:
        dl = st.dup_list()
        if not dl:
            return st, 0, it
        it += 1
        # pick violated feature, weighted towards high weight
        f = max(rng.sample(dl, min(4, len(dl))), key=wt) if len(dl) > 1 else dl[0]
        users = [x for x in range(N) if f in st.lfeat[x]]
        if not users:
            st._rebuild()
            continue
        x = rng.choice(users)
        c, y1, y2, z1, z2 = decode(f, N)
        y0, z0 = rng.choice((y1, y2)), rng.choice((z1, z2))
        cur = st.g[x][y0][z0]
        bestm = None
        for c2 in range(K):
            if c2 == cur:
                continue
            gold = cur
            before = st.feats_at(x, y0, z0, gold) | st.feats_at(x, y0, z0, c2)
            st.g[x][y0][z0] = c2
            after = st.feats_at(x, y0, z0, gold) | st.feats_at(x, y0, z0, c2)
            st.g[x][y0][z0] = gold
            d = 0.0
            for g_ in after - before:
                if st.count.get(g_, 0) == 1:
                    d += wt(g_)
            for g_ in before - after:
                if st.count.get(g_, 0) == 2:
                    d -= wt(g_)
            if bestm is None or d < bestm[0]:
                bestm = (d, c2, before, after)
        if bestm is None:
            continue
        d, c2, before, after = bestm
        if d > 0 and rng.random() > walk_p:
            # no improving move: bump weights of the duplicated features
            for g_ in dl:
                w[g_] = wt(g_) + bump
            since_best += 1
            if smooth_every and since_best > smooth_every:
                for g_ in list(w):
                    w[g_] = max(1.0, w[g_] * 0.7)
                since_best = 0
            continue
        st.commit(x, y0, z0, c2, before, after)
        if st.dupes < best:
            best = st.dupes
            bestg = [row[:] for row in st.g]
            since_best = 0
            if verbose:
                print(f"  it={it} best={best}", flush=True)
        else:
            since_best += 1
    st.g = bestg
    st._rebuild()
    return st, best, it
