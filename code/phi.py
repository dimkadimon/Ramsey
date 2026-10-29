"""phi(n) lower bound and the resulting cube bound.

mono(slice) = sum over column pairs of C(a_j,2)+C(b_j,2)
  a_j = #rows where both columns of pair j are 0,  b_j likewise for 1.
sum_j a_j = T0 = sum_y C(k_y,2),  sum_j b_j = T1 = sum_y C(n-k_y,2),
k_y = number of 0s in row y.
Convexity, applied twice (exact integer version):
  mono >= minpairs(T0,Np) + minpairs(T1,Np),  Np = C(n,2).
Both terms increase with T0,T1 and T0+T1 is minimised by balanced rows,
so the global minimum is attained on multisets k_y in {floor(n/2), ceil(n/2)}.
"""
from math import comb

def minpairs(T, bins):
    q, r = divmod(T, bins)
    return (bins - r) * comb(q, 2) + r * comb(q + 1, 2)

def phi_lb(n):
    Np = comb(n, 2)
    h = n // 2
    best = None
    for m in range(n + 1):
        ks = [h + 1] * m + [h] * (n - m)
        T0 = sum(comb(k, 2) for k in ks)
        T1 = sum(comb(n - k, 2) for k in ks)
        v = minpairs(T0, Np) + minpairs(T1, Np)
        if best is None or v < best:
            best = v
    return best

def phi_exact(n):
    from itertools import combinations_with_replacement
    best = None
    for cols in combinations_with_replacement(range(1 << n), n):
        t = 0
        for i in range(n):
            for j in range(i + 1, n):
                a = n - bin(cols[i] | cols[j]).count('1')
                b = bin(cols[i] & cols[j]).count('1')
                t += comb(a, 2) + comb(b, 2)
        if best is None or t < best:
            best = t
    return best

if __name__ == "__main__":
    print("validation (bound must never exceed the exact minimum):")
    for n in range(2, 6):
        e, l = phi_exact(n), phi_lb(n)
        print(f"  n={n}: phi_exact={e:4d}  phi_lb={l:4d}  {'ok' if l<=e else '*** INVALID ***'}")
    print()
    print(" n | phi_lb |   n*phi_lb |  2*C(n,2)^2 | verdict")
    for n in range(12, 26):
        l = phi_lb(n); lhs = n * l; rhs = 2 * comb(n, 2) ** 2
        v = 'UNCOLORABLE' if lhs > rhs else ('exactly tight' if lhs == rhs else 'not excluded')
        print(f"{n:3d} | {l:6d} | {lhs:10d} | {rhs:12d} | {v}")
