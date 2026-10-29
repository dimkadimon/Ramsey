"""Portfolio attack on the diagonal-shift SAT for one N: random partial
assignments (freeze a few cells) to diversify, several seeds in parallel."""
import json, os, random, sys, threading
sys.path.insert(0,"/home/user/prism")
from itertools import combinations
from pysat.solvers import Cadical195
from diag_sat import group_pairs, rects_of, lift
from core import is_valid_fast

OUT="/home/user/prism/results"

def build(N, extra_lits):
    pairs,_=group_pairs(N)
    var={}; n=0
    for y in range(N):
        for z in range(N):
            n+=1; var[y,z]=n
    lit=lambda y,z,c: var[y,z] if c==1 else -var[y,z]
    cl=[]
    if N%2==0:
        h=N//2
        for y in range(h):
            for z in range(h):
                for c in (0,1):
                    cl.append([-lit(y,z,c),-lit(y,z+h,c),-lit(y+h,z,c),-lit(y+h,z+h,c)])
    for c1,(a1,b1,cc1,d1),c2,(a2,b2,cc2,d2) in pairs:
        cl.append([-lit(a1,cc1,c1),-lit(a1,d1,c1),-lit(b1,cc1,c1),-lit(b1,d1,c1),
                   -lit(a2,cc2,c2),-lit(a2,d2,c2),-lit(b2,cc2,c2),-lit(b2,d2,c2)])
    cl.extend(extra_lits)
    return n,cl,var

def attempt(N, seed, secs, nfix, result):
    rng=random.Random(seed)
    extra=[[-1]]                   # colour-swap: f[0][0]=0
    cells=[(y,z) for y in range(N) for z in range(N) if (y,z)!=(0,0)]
    for (y,z) in rng.sample(cells, nfix):
        v=(y*N+z)+1
        extra.append([v if rng.random()<0.5 else -v])
    n,cl,var=build(N,extra)
    s=Cadical195(bootstrap_with=cl)
    t=threading.Timer(secs, s.interrupt); t.start()
    r=s.solve(); t.cancel()
    m=s.get_model() if r else None
    if m:
        S=set(v for v in m if v>0)
        f=[[1 if var[y,z] in S else 0 for z in range(N)] for y in range(N)]
        g=lift(f,N)
        if is_valid_fast(g):
            result.append((seed,g,f))
    s.delete()

if __name__=="__main__":
    N=int(sys.argv[1]); secs=float(sys.argv[2]); nfix=int(sys.argv[3]) if len(sys.argv)>3 else 0
    seeds=[int(x) for x in sys.argv[4].split(",")] if len(sys.argv)>4 else list(range(6))
    result=[]
    ths=[threading.Thread(target=attempt,args=(N,sd,secs,nfix,result)) for sd in seeds[:2]]
    for t in ths: t.start()
    for t in ths: t.join()
    if result:
        seed,g,f=result[0]
        print(f"N={N}: FOUND (seed {seed})", flush=True)
        os.makedirs(OUT,exist_ok=True)
        json.dump(g,open(f"{OUT}/K2_N{N}.json","w"))
        json.dump(f,open(f"{OUT}/K2_N{N}_base2d.json","w"))
    else:
        print(f"N={N}: nothing", flush=True)
