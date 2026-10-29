"""Numerics for the scaling bounds (rigorous lower vs published upper)."""
import math

def lower(d):
    """largest n with C(n,2)^d < 2^(2^d - 1): binary search with exact big ints"""
    X = 1 << ((1 << d) - 1)
    def ok(n):
        return (n * (n - 1) // 2) ** d < X
    lo, hi = 2, 1 << ((1 << d) // (2 * d) + 4)
    while ok(hi):
        hi <<= 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo

def clean_lower(d):
    return 2 ** (2 ** d / (2 * d))

def upper(d):
    return (d + 2) * 2 ** (2 ** (d - 1))

print(f"{'d':>3} {'exact lower':>16} {'clean lower':>16} {'upper (CFP)':>16} {'gap':>8}")
for d in range(3, 14):
    L, Cl, U = lower(d), clean_lower(d), upper(d)
    print(f"{d:>3}  2^{math.log2(L):>10.1f}  2^{math.log2(Cl):>10.1f}  2^{math.log2(U):>10.1f}"
          f"   {math.log2(U)/math.log2(Cl):>8.1f}")
print()
print("exponent of lower bound = 2^d/(2d):  the constant c_d = 1/(2d) -> 0.")
print("So the proven bound is NOT of the form 2^(c*2^d) with a uniform c>0.")
