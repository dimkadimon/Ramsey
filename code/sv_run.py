import json, os, sys, time
sys.path.insert(0,"/home/user/prism")
from shiftvec import build, lift, true_order
from pysat.solvers import Cadical195
from core import is_valid_fast
N=int(sys.argv[1]); per=float(sys.argv[2])
cands=[(a,b) for a in range(1,N) for b in range(1,N) if true_order(a,b,N)==N]
print(f"N={N}: slanted vectors: {cands}",flush=True)
for (a,b) in cands:
    n,cl,var,norbit,npair=build(N,a,b)
    t0=time.time()
    import threading
    s=Cadical195(bootstrap_with=cl)
    res={}
    def go(): res['r']=s.solve()
    th=threading.Thread(target=go,daemon=True); th.start(); th.join(per)
    dt=time.time()-t0
    if 'r' not in res:
        print(f"  v=({a},{b}): timeout ({dt:.0f}s) orbits={norbit}",flush=True)
        s.delete(); continue
    m=s.get_model() if res['r'] else None
    s.delete()
    if not m:
        print(f"  v=({a},{b}): UNSAT ({dt:.0f}s) orbits={norbit}",flush=True); continue
    S=set(v for v in m if v>0)
    f=[[1 if var[y,z] in S else 0 for z in range(N)] for y in range(N)]
    g=lift(f,N,a,b); ok=is_valid_fast(g)
    print(f"  v=({a},{b}): SAT ({dt:.0f}s) valid={ok}",flush=True)
    if ok:
        os.makedirs("/home/user/prism/results",exist_ok=True)
        json.dump(g,open(f"/home/user/prism/results/K2_N{N}.json","w"))
        json.dump(f,open(f"/home/user/prism/results/K2_N{N}_base2d.json","w"))
        json.dump([a,b],open(f"/home/user/prism/results/K2_N{N}_shiftvec.json","w"))
        print("SOLVED N=%d"%N,flush=True); break
