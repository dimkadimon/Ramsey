import glob, json, os, re, sys
sys.path.insert(0,"/home/user/prism")
from layer_ls import Layer2D
from core import is_valid_fast
for p in sorted(glob.glob("/home/user/prism/results/K*_N*.json"),
                key=lambda s:(int(re.search(r"K(\d+)",s).group(1)),int(re.search(r"N(\d+)",s).group(1)))):
    K=int(re.search(r"K(\d+)",p).group(1)); N=int(re.search(r"N(\d+)",p).group(1))
    g=json.load(open(p))
    if len(g)!=N: continue
    Ls=[Layer2D(N,K,[r[:] for r in g[x]]) for x in range(N)]
    used=set()
    for L in Ls: used|=set(L.all_feats())
    tot=K*(N*(N-1)//2)**2
    ok=is_valid_fast(g)
    per=[len(set(L.all_feats())) for L in Ls]
    print(f"K={K} N={N} valid={ok} features used={len(used)}/{tot} ({100*len(used)/tot:.1f}%) "
          f"per-slice min/avg/max={min(per)}/{sum(per)//len(per)}/{max(per)}")
