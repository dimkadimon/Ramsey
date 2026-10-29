"""Local search for a near-solution, then CDCL with those phases (polish)."""
import json, os, sys, time
sys.path.insert(0,"/home/user/prism")
from sv_ls import breakout
from shiftvec import build, lift
from pysat.solvers import Cadical195
from core import is_valid_fast

def sat_with_phases(N,a,b,f,secs):
    n,cl,var,_,_=build(N,a,b)
    ph=[]
    for y in range(N):
        for z in range(N):
            v=var[y,z]
            ph.append(v if f[y][z]==1 else -v)
    s=Cadical195(bootstrap_with=cl)
    try: s.set_phases(ph)
    except Exception: pass
    import threading
    res={}
    th=threading.Thread(target=lambda: res.__setitem__('r',s.solve()),daemon=True)
    th.start(); th.join(secs)
    if 'r' not in res: s.delete(); return None
    m=s.get_model() if res['r'] else None
    s.delete()
    if not m: return "UNSAT"
    S=set(v for v in m if v>0)
    return [[1 if var[y,z] in S else 0 for z in range(N)] for y in range(N)]

N=int(sys.argv[1]); slopes=[tuple(map(int,s.split(","))) for s in sys.argv[2].split()]
per=float(sys.argv[3]); satsecs=float(sys.argv[4])
for (a,b) in slopes:
    print(f"v=({a},{b})",flush=True)
    best=(10**9,None)
    t_end=time.time()+per
    seed=0
    while time.time()<t_end:
        seed+=1
        o,g,it=breakout(N,a,b,secs=min(60,t_end-time.time()),seed=seed)
        if o<best[0]:
            best=(o,g); print(f"  obj={o} (seed {seed})",flush=True)
        if o==0: break
    if best[0]==0:
        grid=lift(best[1],N,a,b); ok=is_valid_fast(grid)
        print("  valid:",ok,flush=True)
        if ok:
            os.makedirs("/home/user/prism/results",exist_ok=True)
            json.dump(grid,open(f"/home/user/prism/results/K2_N{N}.json","w"))
            json.dump(best[1],open(f"/home/user/prism/results/K2_N{N}_base2d.json","w"))
            json.dump([a,b],open(f"/home/user/prism/results/K2_N{N}_shiftvec.json","w"))
            print(f"*** SOLVED N={N} v=({a},{b})",flush=True); raise SystemExit
    elif best[0]<=4:
        print(f"  polishing obj={best[0]} with CDCL phases ({satsecs}s)",flush=True)
        f2=sat_with_phases(N,a,b,best[1],satsecs)
        if isinstance(f2,list):
            grid=lift(f2,N,a,b); ok=is_valid_fast(grid)
            print("  polished valid:",ok,flush=True)
            if ok:
                os.makedirs("/home/user/prism/results",exist_ok=True)
                json.dump(grid,open(f"/home/user/prism/results/K2_N{N}.json","w"))
                json.dump(f2,open(f"/home/user/prism/results/K2_N{N}_base2d.json","w"))
                json.dump([a,b],open(f"/home/user/prism/results/K2_N{N}_shiftvec.json","w"))
                print(f"*** SOLVED N={N} v=({a},{b})",flush=True); raise SystemExit
        else:
            print("  polish:",f2,flush=True)
