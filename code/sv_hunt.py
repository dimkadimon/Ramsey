import json, os, sys, time
sys.path.insert(0,"/home/user/prism")
from sv_ls import breakout, Prob, search
from shiftvec import lift, true_order
from core import is_valid_fast
N=int(sys.argv[1]); per=float(sys.argv[2]); total=float(sys.argv[3])
slopes=[(a,b) for a in range(1,N) for b in range(1,N) if true_order(a,b,N)==N]
t_end=time.time()+total
best_overall=(10**9,None)
for (a,b) in slopes:
    if time.time()>t_end: break
    bo,bg=None,None
    for seed in (1,2):
        if time.time()>t_end: break
        o,g,it=breakout(N,a,b,secs=per/2,seed=seed)
        if bo is None or o<bo: bo,bg=o,g
        if bo==0: break
    print(f"  v=({a},{b}): obj={bo}",flush=True)
    if bo<best_overall[0]:
        best_overall=(bo,(a,b),bg)
        print(f"   *new best {bo} at v=({a},{b})",flush=True)
    if bo==0:
        grid=lift(bg,N,a,b); ok=is_valid_fast(grid)
        print(f"lifted valid={ok}",flush=True)
        if ok:
            os.makedirs("/home/user/prism/results",exist_ok=True)
            json.dump(grid,open(f"/home/user/prism/results/K2_N{N}.json","w"))
            json.dump(bg,open(f"/home/user/prism/results/K2_N{N}_base2d.json","w"))
            json.dump([a,b],open(f"/home/user/prism/results/K2_N{N}_shiftvec.json","w"))
            print(f"*** SOLVED N={N} with v=({a},{b})",flush=True)
            break
print("done, best",best_overall[0],best_overall[1],flush=True)
