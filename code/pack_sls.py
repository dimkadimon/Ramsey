"""Stochastic local search for the 2-colour (K-colour) packing problem.

Packing criterion
-----------------
A colouring of [n]^3 is box-free  <=>  no feature (c, y-pair, z-pair) occurs
in two different x-slices, where it "occurs in slice x" when the four cells
(x,y1,z1),(x,y1,z2),(x,y2,z1),(x,y2,z2) all have colour c.

cost(state) = sum_f max(0, cnt_f - 1)   (number of *duplicate* features)
cost == 0  <=>  box-free.

The search flips single cells; a flip touches 2*(n-1)^2 features, all deltas
are exact and incremental.
"""
import json, os, random, sys, time
import numpy as np

sys.path.insert(0, "/home/user/prism")


def pair_list(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


class State:
    def __init__(self, n, K, S):
        self.n, self.K = n, K
        self.S = S                                  # (X, n, n) int8
        self.X = S.shape[0]
        self.P = pair_list(n)
        self.m = len(self.P)
        self.pidx = {p: i for i, p in enumerate(self.P)}
        # affinity tables: features (and partner coords) touched by cell (y,z)
        self.aff = {}
        for y in range(n):
            for z in range(n):
                rows = []
                for k in range(K):
                    idx, dys, dzs = [], [], []
                    for (y1, y2) in self.P:
                        if y != y1 and y != y2:
                            continue
                        yp = y2 if y == y1 else y1
                        jj = self.pidx[(y1, y2)]
                        for (z1, z2) in self.P:
                            if z != z1 and z != z2:
                                continue
                            zp = z2 if z == z1 else z1
                            kk = self.pidx[(z1, z2)]
                            idx.append((k * self.m + jj) * self.m + kk)
                            dys.append(yp)
                            dzs.append(zp)
                    rows.append((np.array(idx, dtype=np.int64),
                                 np.array(dys, dtype=np.int64),
                                 np.array(dzs, dtype=np.int64)))
                self.aff[(y, z)] = rows
        self.counts = np.zeros(K * self.m * self.m, dtype=np.int32)
        self.recompute()

    # ---------------- full recompute ----------------
    def recompute(self):
        n, K, m = self.n, self.K, self.m
        self.counts[:] = 0
        for k in range(K):
            M = (self.S == k)
            for jj, (y1, y2) in enumerate(self.P):
                Q = M[:, y1, :] & M[:, y2, :]          # (X, n)
                C = Q.T.astype(np.int32) @ Q.astype(np.int32)
                np.fill_diagonal(C, 0)
                base = (k * m + jj) * m
                for kk, (z1, z2) in enumerate(self.P):
                    self.counts[base + kk] = C[z1, z2]

    def cost(self):
        return int(np.maximum(self.counts - 1, 0).sum())

    # ---------------- delta of one cell flip ----------------
    def delta(self, x, y, z, newc):
        n = self.n
        oldc = int(self.S[x, y, z])
        if newc == oldc:
            return 0, None
        rows = self.aff[(y, z)]
        A = (self.S[x] == oldc)
        B = (self.S[x] == newc)
        idx_o, dy, dz = rows[oldc]
        bef_o = A[y, z] & A[y, dz] & A[dy, z] & A[dy, dz]
        idx_n, dy2, dz2 = rows[newc]
        bef_n = B[y, z] & B[y, dz2] & B[dy2, z] & B[dy2, dz2]
        # apply
        self.S[x, y, z] = newc
        A2 = (self.S[x] == oldc)
        B2 = (self.S[x] == newc)
        aft_o = A2[y, z] & A2[y, dz] & A2[dy, z] & A2[dy, dz]
        aft_n = B2[y, z] & B2[y, dz2] & B2[dy2, z] & B2[dy2, dz2]
        d = 0
        for idx, bef, aft in ((idx_o, bef_o, aft_o), (idx_n, bef_n, aft_n)):
            dc = aft.astype(np.int32) - bef.astype(np.int32)
            oc = self.counts[idx]
            nc = oc + dc
            d += int(np.maximum(nc - 1, 0).sum() - np.maximum(oc - 1, 0).sum())
            self.counts[idx] = nc
        return d, (x, y, z, oldc)

    def undo(self, mv):
        self.delta(*mv[:3], mv[3])   # flipping back is exactly the inverse

    def slice_contrib(self):
        """how many of the slice's mono features are duplicated elsewhere"""
        n, K, m = self.n, self.K, self.m
        contrib = np.zeros(self.X, dtype=np.int64)
        for x in range(self.X):
            t = 0
            for k in range(K):
                A = (self.S[x] == k)
                for jj, (y1, y2) in enumerate(self.P):
                    q = A[y1, :] & A[y2, :]
                    base = (k * m + jj) * m
                    for kk, (z1, z2) in enumerate(self.P):
                        if q[z1] and q[z2] and self.counts[base + kk] > 1:
                            t += 1
            contrib[x] = t
        return contrib


def find(n, K=2, secs=120.0, seed=0, verbose=True, init=None, noise=0.02,
         out_path=None, restart_after=None):
    rng = random.Random(seed)
    np.random.seed(seed)
    if init is None:
        S = np.array([[[rng.randrange(K) for _ in range(n)] for _ in range(n)]
                      for _ in range(n)], dtype=np.int8)
    else:
        S = np.array(init, dtype=np.int8)
    st = State(n, K, S)
    cost = st.cost()
    best, bestS = cost, st.S.copy()
    t_end = time.time() + secs
    it = 0
    since = 0
    while time.time() < t_end and best > 0:
        it += 1
        since += 1
        # pick a slice that is actually in trouble most of the time
        if it == 1 or it % 200 == 0:
            sc = st.slice_contrib()
            hot = np.argsort(-sc)[:max(1, n // 3)]
        x = int(hot[rng.randrange(len(hot))]) if rng.random() < 0.7 else rng.randrange(n)
        y = rng.randrange(n); z = rng.randrange(n)
        old = int(st.S[x, y, z])
        cands = [c for c in range(K) if c != old]
        bestd, bestc = None, None
        for c in cands:
            d, mv = st.delta(x, y, z, c)
            st.undo(mv)
            if bestd is None or d < bestd:
                bestd, bestc = d, c
        if bestd <= 0 or rng.random() < noise:
            d, _ = st.delta(x, y, z, bestc)
            cost += d
            if cost < best:
                best, bestS = cost, st.S.copy()
                since = 0
                if verbose:
                    print(f"   it={it} cost={best}", flush=True)
        if restart_after and since > restart_after:
            # re-heat: keep best, randomise the worst slices
            st.S = bestS.copy(); st.recompute(); cost = best
            sc = st.slice_contrib()
            worst = np.argsort(-sc)[:max(1, n // 4)]
            for x in [int(v) for v in worst]:
                st.S[x] = np.random.randint(K, size=(n, n)).astype(np.int8)
            st.recompute(); cost = st.cost()
            since = 0
    return best, bestS, it


if __name__ == "__main__":
    n = int(sys.argv[1]); secs = float(sys.argv[2]) if len(sys.argv) > 2 else 120
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    best, S, it = find(n, K, secs, seed)
    print(f"n={n} K={K} seed={seed}: cost {best} after {it} flips", flush=True)
    if best == 0:
        grid = [[[int(S[x][y][z]) for z in range(n)] for y in range(n)] for x in range(n)]
        os.makedirs("/home/user/prism/results", exist_ok=True)
        json.dump(grid, open(f"/home/user/prism/results/K{K}_N{n}.json", "w"))
        print("*** SOLVED", flush=True)
