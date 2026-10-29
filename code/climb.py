import json, os, sys, time
sys.path.insert(0, "/home/user/prism")
from sat3 import solve
from core import is_valid

OUT = "/home/user/prism/results"
os.makedirs(OUT, exist_ok=True)
K = int(sys.argv[1]); a = int(sys.argv[2]); b = int(sys.argv[3]); tl = float(sys.argv[4])
prev = None
for N in (500,):
    pass
for N in range(a, b + 1):
    t0 = time.time()
    st, g = solve(N, K, tl, prev=prev)
    dt = round(time.time() - t0, 1)
    ok = is_valid(g) if g else None
    line = f"K={K} N={N} {st} valid={ok} {dt}s"
    print(line, flush=True)
    open(f"{OUT}/climb_K{K}.log", "a").write(line + "\n")
    if st == "SAT":
        json.dump(g, open(f"{OUT}/K{K}_N{N}.json", "w"))
        prev = g
    else:
        break
