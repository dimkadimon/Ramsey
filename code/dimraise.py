"""Dimension-raising construction for K = 2.

LEMMA.  If there is a prism-free 2-colouring f of [N]^m, then there is a
prism-free 2-colouring of [N]^{m+1}, namely

        F(x_1,...,x_{m+1}) = f( (x_1 - x_{m+1}) mod N , ..., (x_m - x_{m+1}) mod N ).

PROOF.  Take a box in [N]^{m+1}: pairs {x_i, x_i'} in every coordinate.
Split its 2^{m+1} vertices by the last coordinate: since x_{m+1} takes two
values u < v, we get two m-dimensional boxes
        B_u = {x_1,x_1'} x ... x {x_m,x_m'}   at last coordinate u,
        B_v = the same m-box                    at last coordinate v.
If the whole (m+1)-box is monochromatic, both B_u and B_v are monochromatic in
the same colour.  Now F(.,u) is the base colouring f shifted by u in every
coordinate, and F(.,v) is f shifted by v.  A box being monochromatic is
invariant under shifting all coordinates by the same amount, so *both* B_u and
B_v being monochromatic means the m-box {x_1,x_1'}x...x{x_m,x_m'} is
monochromatic in f -- contradicting prism-freeness of f.  QED

Consequence:  N(2,m+1) <= N(2,m) for all m;  in particular any explicit
prism-free colouring of [N]^3 gives prism-free 2-colourings of [N]^d for *every*
d >= 3.
"""
import json
import sys
from itertools import combinations

sys.path.insert(0, "/home/user/prism")


def lift(f, N):
    """m-dim colouring -> (m+1)-dim colouring."""
    m = len(f)
    assert N == len(f)
    # index strings of length m
    out = [[[[0] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
    for x4 in range(N):
        for x3 in range(N):
            for x2 in range(N):
                for x1 in range(N):
                    out[x1][x2][x3][x4] = f[(x1 - x4) % N][(x2 - x4) % N][(x3 - x4) % N]
    return out


def mono_box_count(g):
    """brute force: count monochromatic boxes of the (possibly 4-dim) grid g.

    Works by the slice-pairing trick: a mono box over slices x1<x2 (first
    coordinate) and an (m-1)-box B is present iff both slices are mono on B.
    """
    N = len(g)
    d = 1
    t = g
    while isinstance(t[0], list):
        t = t[0]
        if isinstance(t, list):
            d += 1
        else:
            break
    d = 1
    t = g
    while isinstance(t, list) and isinstance(t[0], list):
        t = t[0]
        d += 1
    K = 1 + max(v for v in flatten(g))
    # features: for each (m-1)-box (in coords 1..d-1) and colour, which slices use it
    from itertools import product
    count = 0
    pairs = list(combinations(range(N), 2))
    for coords in product(pairs, repeat=d - 1):
        for c in range(K):
            used = []
            for x in range(N):
                ok = True
                for eps in product((0, 1), repeat=d - 1):
                    idx = [x] + [coords[i][eps[i]] for i in range(d - 1)]
                    if value_at(g, idx) != c:
                        ok = False
                        break
                if ok:
                    used.append(x)
            n = len(used)
            if n >= 2:
                count += n * (n - 1) // 2
    return count


def flatten(g):
    if isinstance(g, list):
        for x in g:
            yield from flatten(x)
    else:
        yield g


def value_at(g, idx):
    v = g
    for i in idx:
        v = v[i]
    return v


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    from core import is_valid_fast
    if path:
        f = json.load(open(path))
    else:
        from sat2 import solve
        st, f = solve(4, 2)
        print("built a 3-dim test colouring:", st)
    N = len(f)
    print(f"base: {N}x{N}x{N}, prism-free: {is_valid_fast(f)}")
    g4 = lift(f, N)
    print(f"lifted to 4 dimensions: {N}^4, monochromatic boxes =",
          mono_box_count(g4))
    json.dump(g4, open(f"/home/user/prism/results/K2_N{N}_dim4.json", "w"))
