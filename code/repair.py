"""Slice-level min-conflicts: repeatedly re-solve the worst slice given the others."""
import json, os, random, sys, time
sys.path.insert(0, "/home/user/prism")
from itertools import combinations
from layer_ls import sat_slice2, Layer2D, improve, pairs_of
from construct import make_grid
from core import is_valid_fast

OUT="/home/user/prism/results"

def slices_feats(g, N, K):
    return [Layer2D(N,K,[row[:] for row in g[x]]) for x in range(N)]

def dupes_count(Ls, K):
    from collections import Counter
    cnt=Counter()
    for L in Ls:
        for f in set(L.all_feats()):
            cnt[f]+=1
    dup={f for f,v in cnt.items() if v>=2}
    return dup, cnt

def main(N,K,secs,seed=0,iters=1500):
    rng=random.Random(seed)
    pairs=pairs_of(N); M=N*(N-1)//2
    # init: greedy-ish random slices
    g=[[[rng.randrange(K) for _ in range(N)] for _ in range(N)] for _ in range(N)]
    t_end=time.time()+secs; best=10**9
    while time.time()<t_end:
        Ls=slices_feats(g,N,K)
        dup,cnt=dupes_count(Ls,K)
        if not dup:
            return g,0
        if len(dup)<best:
            best=len(dup); print("  dupes",best,flush=True)
        # pick a duplicated feature, pick a slice using it
        f=rng.choice(list(dup))
        c=f//(M*M); r=f%(M*M); ay,az=divmod(r,M)
        users=[x for x in range(N) if f in Ls[x].all_feats()]
        x=rng.choice(users)
        # forbidden = all features used by the other slices
        forb=[set() for _ in range(K)]
        for y2,L2 in enumerate(Ls):
            if y2==x: continue
            for ff in L2.all_feats():
                cc=ff//(M*M); rr=ff%(M*M); a1,a2=divmod(rr,M)
                forb[cc].add(pairs[a1]+pairs[a2])
        new=sat_slice2(N,K,forb,rng=rng,conf_budget=60000)
        if new is None:
            continue
        fid_sets=[]
        for cc in range(K):
            S=set()
            for (y1,y2,z1,z2) in forb[cc]:
                S.add((cc*M+pairs.index((y1,y2)))*M+pairs.index((z1,z2)))
            fid_sets.append(S)
        new2,_,fs=improve(N,K,new,fid_sets,iters=iters,rng=rng)
        L2=Layer2D(N,K,new2)
        if any((ff in fid_sets[ff//(M*M)]) for ff in L2.all_feats()):
            new2=new
        g[x]=new2
    return g,best

if __name__=="__main__":
    N,K=int(sys.argv[1]),int(sys.argv[2]); secs=float(sys.argv[3])
    seed=int(sys.argv[4]) if len(sys.argv)>4 else 0
    g,best=main(N,K,secs,seed)
    print("final dupes/failed slices:",best)
    if best==0 and is_valid_fast(g):
        print("VALID")
        os.makedirs(OUT,exist_ok=True)
        json.dump(g,open(f"{OUT}/K{K}_N{N}.json","w"))
