"""Sweep: build valid colourings with the layer-greedy constructor and record them."""
import json, os, sys, time
sys.path.insert(0, "/home/user/prism")
from layer_sat import build
from construct import make_grid
from core import is_valid

OUT = "/home/user/prism/results"
os.makedirs(OUT, exist_ok=True)


def attempt(N, K, cp_time=3.0, seed=1):
    t0 = time.time()
    layers, _ = build(N, K, seed=seed, cp_time=cp_time, verbose=False)
    dt = time.time() - t0
    if layers and len(layers) == N:
        g = make_grid(layers, N)
        ok = is_valid(g)
        if ok:
            json.dump(g, open(f"{OUT}/K{K}_N{N}.json", "w"))
        return ok, dt, len(layers)
    return False, dt, len(layers or [])


if __name__ == "__main__":
    # pairs given as K:N on the command line
    for spec in sys.argv[1:]:
        K, N = map(int, spec.split(":"))
        cpt = float(os.environ.get("CPT", "3"))
        ok, dt, nl = attempt(N, K, cp_time=cpt, seed=hash(spec) % 1000)
        line = f"K={K} N={N} ok={ok} layers={nl}/{N} {dt:.0f}s"
        print(line, flush=True)
        open(f"{OUT}/sweep.log", "a").write(line + "\n")
