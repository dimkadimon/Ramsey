"""Campaign: for each K, climb N while SAT survives; log everything; save grids."""
import json, os, sys, time
sys.path.insert(0, "/home/user/prism")
from sat2 import solve
from core import is_valid

OUT = "/home/user/prism/results"
os.makedirs(OUT, exist_ok=True)


def climb(K, n_start, n_max, tl):
    prev = None
    for N in range(n_start, n_max + 1):
        t0 = time.time()
        st, g = solve(N, K, time_limit=tl, prev=prev if prev and len(prev) == N - 0 else None)
        dt = round(time.time() - t0, 1)
        ok = is_valid(g) if g else None
        line = f"K={K} N={N} {st} valid={ok} {dt}s"
        print(line, flush=True)
        with open(f"{OUT}/climb_K{K}.log", "a") as f:
            f.write(line + "\n")
        if st == "SAT":
            json.dump(g, open(f"{OUT}/K{K}_N{N}.json", "w"))
        else:
            break


if __name__ == "__main__":
    K, a, b, tl = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    climb(K, a, b, tl)
