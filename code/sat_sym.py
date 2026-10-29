"""K=2 SAT model with symmetry breaking, aimed at N = 11, 12, 13.

Cell variables are booleans: b[x][y][z] = True  <=>  cell has colour 1.

Constraints
  * each box is not monochromatic  ->  two 8-literal clauses per box
  * colour-swap symmetry:  b[0][0][0] = False
  * SLICE-ORDER symmetry:  slices, read as bit vectors, are sorted
    (decreasing lexicographic).  Any colouring can be permuted so that its
    slices are sorted, so this is a valid symmetry break and removes a factor
    of N! (11! ~ 4e7 for N = 11).
"""
import sys

from pysat.solvers import Cadical195

sys.path.insert(0, "/home/user/prism")


class Enc:
    def __init__(self):
        self.n = 0
        self.cl = []

    def new(self):
        self.n += 1
        return self.n

    def add(self, c):
        self.cl.append(c)


def build(N, lex_sort=True, colour_break=True, extra=None):
    E = Enc()
    b = {}
    for x in range(N):
        for y in range(N):
            for z in range(N):
                b[x, y, z] = E.new()

    if colour_break:
        E.add([-b[0, 0, 0]])

    # boxes
    for x1 in range(N):
        for x2 in range(x1 + 1, N):
            for y1 in range(N):
                for y2 in range(y1 + 1, N):
                    for z1 in range(N):
                        for z2 in range(z1 + 1, N):
                            v = [b[x1, y1, z1], b[x1, y1, z2], b[x1, y2, z1],
                                 b[x1, y2, z2], b[x2, y1, z1], b[x2, y1, z2],
                                 b[x2, y2, z1], b[x2, y2, z2]]
                            E.add([-t for t in v])   # not all colour 1
                            E.add(v)                 # not all colour 0

    if lex_sort:
        # slices as bit vectors in row-major (y,z) order; require v_x >=lex v_{x+1}
        order = [(y, z) for y in range(N) for z in range(N)]
        for x in range(N - 1):
            A = [b[x, y, z] for (y, z) in order]
            B = [b[x + 1, y, z] for (y, z) in order]
            e = [E.new() for _ in order]      # e[i] = prefixes 0..i-1 equal
            E.add([e[0]])                      # e[0] is true
            for i in range(len(order) - 1):
                # e[i+1] -> e[i]
                E.add([-e[i + 1], e[i]])
                # e[i+1] -> (A_i == B_i)
                E.add([-e[i + 1], -A[i], B[i]])
                E.add([-e[i + 1], A[i], -B[i]])
                # (e[i] and A_i==B_i) -> e[i+1]
                E.add([-e[i], -A[i], -B[i], e[i + 1]])
                E.add([-e[i], A[i], B[i], e[i + 1]])
            for i in range(len(order)):
                # if prefixes equal then not (A_i = 0 and B_i = 1)
                E.add([-e[i], A[i], -B[i]])

    if extra:
        extra(E, b, N)
    return E, b


def solve(N, time_limit=None, workers=1, seed=1, lex_sort=True, verbose=True):
    import threading
    import time
    E, b = build(N, lex_sort=lex_sort)
    if verbose:
        print(f"  N={N}: {E.n} vars, {len(E.cl)} clauses", flush=True)
    s = Cadical195(bootstrap_with=E.cl)
    timer = threading.Timer(time_limit, s.interrupt) if time_limit else None
    t0 = time.time()
    if timer:
        timer.start()
    try:
        r = s.solve()
    finally:
        if timer:
            timer.cancel()
    dt = time.time() - t0
    m = s.get_model() if r else None
    s.delete()
    if m is None:
        return ("UNKNOWN" if time_limit else "UNSAT"), None, dt
    S = set(v for v in m if v > 0)
    g = [[[1 if b[x, y, z] in S else 0 for z in range(N)] for y in range(N)]
         for x in range(N)]
    return "SAT", g, dt


if __name__ == "__main__":
    import json
    import os
    from core import is_valid_fast
    N = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    st, g, dt = solve(N, time_limit=tl)
    print(f"N={N} -> {st} in {dt:.0f}s")
    if g:
        print("verified:", is_valid_fast(g))
        if is_valid_fast(g):
            os.makedirs("/home/user/prism/results", exist_ok=True)
            json.dump(g, open(f"/home/user/prism/results/K2_N{N}.json", "w"))
