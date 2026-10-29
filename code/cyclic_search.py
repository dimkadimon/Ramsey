"""Search for the cyclic-shift construction of K=2 prism-free colourings.

Need N subsets T_y of Z_N such that for every y<y' both
    T_y n T_y'      (shared 1-columns)
    T^c_y n T^c_y'  (shared 0-columns)
are Sidon sets (all C(s,2) differences distinct up to sign).
Then c(x,y,z) = [ (z-x) mod N in T_y ] is prism-free.
"""
import json, os, random, sys, time
sys.path.insert(0, "/home/user/prism")
from itertools import combinations
from cyclic import is_sidon, check_sets, build_grid
from core import is_valid_fast

OUT="/home/user/prism/results"

def violations(Ts, N, y=None):
    bad = []
    for a, b in combinations(range(N), 2):
        if y is not None and y != a and y != b:
            continue
        D1 = Ts[a] & Ts[b]
        D0 = set(range(N)) - (Ts[a] | Ts[b])
        if not is_sidon(D1, N):
            bad.append((a, b, 1))
        if not is_sidon(D0, N):
            bad.append((a, b, 0))
    return bad


def search(N, secs=120, seed=0, tsize=None, verbose=True):
    rng=random.Random(seed)
    t = tsize if tsize else (N+1)//2
    Ts=[set(rng.sample(range(N),t)) for _ in range(N)]
    cur = violations(Ts,N)
    best=(len(cur), [s.copy() for s in Ts])
    t_end=time.time()+secs
    it=0
    while time.time()<t_end and cur:
        it+=1
        y=rng.randrange(N); z=rng.randrange(N)
        if z in Ts[y]: Ts[y].discard(z)
        else: Ts[y].add(z)
        new=violations(Ts,N,y)
        # count violations involving y before/after
        old_local=[v for v in cur if v[0]==y or v[1]==y]
        if len(new) <= len(old_local) or rng.random()<0.02:
            cur=[v for v in cur if not (v[0]==y or v[1]==y)]+new
            if len(cur)<best[0]:
                best=(len(cur),[s.copy() for s in Ts])
                if verbose: print(f"  it={it} violations={len(cur)}",flush=True)
        else:
            if z in Ts[y]: Ts[y].discard(z)
            else: Ts[y].add(z)
    return best

if __name__=="__main__":
    for N in map(int, sys.argv[1:]):
        secs=float(os.environ.get("SECS","60"))
        bestv=10**9; bestT=None
        for seed in range(6):
            tsize = None
            v,Ts = search(N, secs=secs, seed=seed, tsize=None, verbose=False)
            if v<bestv: bestv, bestT = v, Ts
            if v==0: break
        print(f"N={N}: best violations={bestv}", flush=True)
        if bestv==0:
            g=build_grid(bestT,N)
            ok=is_valid_fast(g)
            print(f"  built grid valid={ok}", flush=True)
            if ok:
                json.dump(g,open(f"{OUT}/K2_N{N}.json","w"))
                json.dump([sorted(s) for s in bestT],open(f"{OUT}/K2_N{N}_sets.json","w"))
