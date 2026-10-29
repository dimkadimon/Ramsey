"""Upper bounds for N(c,3): CFP Lemma 15 packing + exact 2-D convexity."""
from math import comb
from itertools import product

def minpairs(T, bins):
    q, r = divmod(T, bins)
    return (bins - r) * comb(q, 2) + r * comb(q + 1, 2)

def near_balanced_types(n, c):
    q, r = divmod(n, c)
    # parts drawn from {q-1..q+2}, summing to n
    out = set()
    lo, hi = max(0, q - 1), q + 2
    def rec(i, rem, cur):
        if i == c - 1:
            v = rem
            if lo <= v <= hi:
                out.add(tuple(sorted(cur + [v], reverse=True)))
            return
        for v in range(lo, min(hi, rem) + 1):
            rec(i + 1, rem - v, cur + [v])
    rec(0, n, [])
    return sorted(out)

def phi_lb(n, c):
    Np = comb(n, 2)
    types = near_balanced_types(n, c)
    def val(ms):
        T = [0] * c
        for t, m in ms:
            for i in range(c):
                T[i] += m * comb(t[i], 2)
        return sum(minpairs(T[i], Np) for i in range(c))
    best = val([(types[0], n)])
    for a in types:
        for b in types:
            for m in range(n + 1):
                v = val([(a, n - m), (b, m)])
                if v < best:
                    best = v
    return best

if __name__ == "__main__":
    import sys
    print(" c | least n with n*phi_lb > c*C(n,2)^2 | => N(c,3) <= | CFP bound")
    cfp = {2: 21, 3: 92, 4: 276, 5: 656}
    for c in (2, 3, 4, 5):
        for n in range(3, 900):
            l = phi_lb(n, c)
            if n * l > c * comb(n, 2) ** 2:
                print(f" {c} | {n:32d} | {n-1:11d} | {cfp[c]:3d}"
                      + ("   <-- IMPROVED" if n - 1 < cfp[c] else "   (no gain)"))
                break
