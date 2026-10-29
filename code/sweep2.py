import json, os, sys, time
sys.path.insert(0,"/home/user/prism")
from layer_sat import build
from construct import make_grid
from core import is_valid
OUT="/home/user/prism/results"
K=int(sys.argv[1]); cpt=float(sys.argv[2])
for N in map(int, sys.argv[3:]):
    t0=time.time()
    layers,_=build(N,K,seed=N*13+K,cp_time=cpt,verbose=False)
    dt=time.time()-t0
    ok=False
    if layers and len(layers)==N:
        g=make_grid(layers,N); ok=is_valid(g)
        if ok: json.dump(g,open(f"{OUT}/K{K}_N{N}.json","w"))
    line=f"K={K} N={N} ok={ok} layers={len(layers or [])}/{N} {dt:.0f}s"
    print(line,flush=True); open(f"{OUT}/sweep.log","a").write(line+"\n")
