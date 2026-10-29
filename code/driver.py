"""Search driver: try increasing N for a fixed K, log results, save colourings."""
import json, os, sys, time
sys.path.insert(0, "/home/user/prism")
from core import is_valid
from cpsat_model import solve

OUT = "/home/user/prism/results"
os.makedirs(OUT, exist_ok=True)


def run(K, Ns, time_limit, workers=1, tag=""):
    log = []
    for N in Ns:
        t0 = time.time()
        st, g = solve(N, K, time_limit, workers=workers, seed=N * 7 + K)
        dt = time.time() - t0
        ok = None
        if g is not None:
            ok = is_valid(g)
            if ok:
                fn = f"{OUT}/K{K}_N{N}{tag}.json"
                json.dump(g, open(fn, "w"))
        msg = f"K={K} N={N} status={st} valid={ok} t={dt:.1f}s"
        print(msg, flush=True)
        log.append(msg)
        if st in ("INFEASIBLE",):
            break
    open(f"{OUT}/log_K{K}{tag}.txt", "w").write("\n".join(log))


if __name__ == "__main__":
    K = int(sys.argv[1])
    lo, hi = int(sys.argv[2]), int(sys.argv[3])
    tl = float(sys.argv[4])
    tag = sys.argv[5] if len(sys.argv) > 5 else ""
    run(K, range(lo, hi + 1), tl, tag=tag)
