import json, os, random, sys, time
sys.path.insert(0,"/home/user/prism")
from layer_ls import build
from construct import make_grid
from core import is_valid_fast
OUT="/home/user/prism/results"
K=int(sys.argv[1]); N=int(sys.argv[2]); secs=float(sys.argv[3]); per=float(sys.argv[4])
best=0; tries=0; t_end=time.time()+secs
while time.time()<t_end:
    tries+=1
    rng=random.Random(tries*7919+N)
    layers=build(N,K,seed=tries,iters=2500,verbose=False,rng=rng,
                 deadline=min(t_end, time.time()+per))
    n=len(layers) if layers else 0
    if n>best:
        best=n; print(f"  try {tries}: {best}/{N}",flush=True)
    if n==N:
        g=make_grid(layers,N); ok=is_valid_fast(g)
        print("VALID:",ok,flush=True)
        if ok:
            os.makedirs(OUT,exist_ok=True); json.dump(g,open(f"{OUT}/K{K}_N{N}.json","w")); break
print(f"K={K} N={N} tries={tries} best={best}/{N}")
