import json, os, sys, time
sys.path.insert(0,"/home/user/prism")
from shift_sat import build, lift
from pysat.solvers import Cadical195
from core import is_valid_fast
N=int(sys.argv[1])
n,cl,var=build(N)
t0=time.time()
s=Cadical195(bootstrap_with=cl)
r=s.solve()
dt=time.time()-t0
m=s.get_model() if r else None
if not m:
    print(f"N={N}: UNSAT/{r} ({dt:.0f}s)",flush=True); sys.exit(0)
S=set(v for v in m if v>0)
f=[[1 if var[y,z] in S else 0 for z in range(N)] for y in range(N)]
g=lift(f,N); ok=is_valid_fast(g)
print(f"N={N}: SAT ({dt:.0f}s) lifted valid={ok}",flush=True)
if ok:
    os.makedirs("/home/user/prism/results",exist_ok=True)
    json.dump(g,open(f"/home/user/prism/results/K2_N{N}.json","w"))
    json.dump(f,open(f"/home/user/prism/results/K2_N{N}_base2d.json","w"))
