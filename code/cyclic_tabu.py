"""Tabu search on the cyclic-construction design problem.

Variables: t[y][z] in {0,1} (z in T_y).
Objective: sum over row pairs of  V(T_y1 n T_y2) + V(T^c_y1 n T^c_y2),  where
  V(D) = sum_k C(c_k, 2)  (+ c_{N/2} when N is even)
with c_k the number of unordered pairs of D whose difference is +-k.
Zero objective  <=>  the induced colouring c(x,y,z)=[(z-x) in T_y] is prism-free.
"""
import json
import os
import random
import sys
import time

sys.path.insert(0, "/home/user/prism")


def viol(T, N):
    """exact objective for the whole family T = list of sets."""
    tot = 0
    half = N // 2
    for y1 in range(N):
        for y2 in range(y1 + 1, N):
            for D in (T[y1] & T[y2],
                      set(range(N)) - (T[y1] | T[y2])):
                cnt = {}
                for a in D:
                    for b in D:
                        if a < b:
                            k = (a - b) % N
                            k = min(k, N - k)
                            cnt[k] = cnt.get(k, 0) + 1
                s = 0
                for k, c in cnt.items():
                    if N % 2 == 0 and k == half:
                        s += c * 100          # antipodal pair: fatal
                    elif c > 1:
                        s += c * (c - 1) // 2
                tot += s
    return tot


def pair_cost(A, B, N):
    half = N // 2
    s = 0
    for both in (True, False):
        D = [z for z in range(N) if (z in A) == both and (z in B) == both]
        cnt = {}
        for i in range(len(D)):
            for j in range(i + 1, len(D)):
                k = (D[i] - D[j]) % N
                k = min(k, N - k)
                cnt[k] = cnt.get(k, 0) + 1
        for k, c in cnt.items():
            if N % 2 == 0 and k == half:
                s += c * 100
            elif c > 1:
                s += c * (c - 1) // 2
    return s


def run(N, secs=120, seed=0, rowsize=None, verbose=True):
    rng = random.Random(seed)
    k = rowsize or (N + 1) // 2
    T = [set(rng.sample(range(N), k)) for _ in range(N)]
    pc = [[0] * N for _ in range(N)]
    total = 0
    for a in range(N):
        for b in range(a + 1, N):
            pc[a][b] = pair_cost(T[a], T[b], N)
            total += pc[a][b]
    best = total
    bestT = [s.copy() for s in T]
    tabu = {}
    it = 0
    t_end = time.time() + secs
    while time.time() < t_end and best > 0:
        it += 1
        y = rng.randrange(N)
        z = rng.randrange(N)
        old = z in T[y]
        if old:
            T[y].discard(z)
        else:
            T[y].add(z)
        delta = 0
        newpc = []
        for b in range(N):
            if b == y:
                continue
            p = pair_cost(T[y], T[b], N)
            delta += p - pc[min(b, y)][max(b, y)]
            newpc.append((b, p))
        key = (y, z)
        if total + delta < best or tabu.get(key, 0) <= it:
            for b, p in newpc:
                pc[min(b, y)][max(b, y)] = p
            total += delta
            tabu[key] = it + 5 + rng.randrange(8)
            if total < best:
                best = total
                bestT = [s.copy() for s in T]
                if verbose:
                    print(f"  it={it} obj={best}", flush=True)
        else:
            if old:
                T[y].add(z)
            else:
                T[y].discard(z)
        if it % 3000 == 0 and verbose:
            print(f"  ..it={it} obj={total} best={best}", flush=True)
            if total > best * 3 + 10:      # too far astray: restart from best
                T = [s.copy() for s in bestT]
                total = best
                for a in range(N):
                    for b in range(a + 1, N):
                        pc[a][b] = pair_cost(T[a], T[b], N)
                        total = total if (a, b) != (0, 1) else total
    return best, bestT, it


if __name__ == "__main__":
    from cyclic import check_sets, build_grid
    from core import is_valid_fast
    OUT = "/home/user/prism/results"
    for N in map(int, sys.argv[1:]):
        secs = float(os.environ.get("SECS", "120"))
        bb, bT, it = None, None, 0
        for seed in range(4):
            b, T, it = run(N, secs=secs / 4, seed=seed, verbose=True)
            print(f"N={N} seed={seed}: obj={b}", flush=True)
            if bb is None or b < bb:
                bb, bT = b, T
            if bb == 0:
                break
        if bb == 0:
            g = build_grid(bT, N)
            ok = is_valid_fast(g)
            print(f"N={N}: grid valid={ok}", flush=True)
            if ok:
                os.makedirs(OUT, exist_ok=True)
                json.dump(g, open(f"{OUT}/K2_N{N}.json", "w"))
                json.dump([sorted(s) for s in bT], open(f"{OUT}/K2_N{N}_sets.json", "w"))
        else:
            print(f"N={N}: best objective {bb} (not solved)", flush=True)
