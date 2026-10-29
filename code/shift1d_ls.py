"""Local search in the 1-D shift family  chi(x,y,z) = f(x+y, z).

Criterion (Prop. shift): for every colour g and z1<z2, the set
    D_g(z1,z2) = {u : f(u,z1)=f(u,z2)=g}
must contain no {u0, u0+a, u0+b, u0+a+b} with a,b>=1 (inside [0,2n-2]).

Key identity used for the cost: for a set D (as a bitmask over 0..U),
    #{violating (a,b,u0)} = sum_{a>=1} C( |D & (D>>a)| , 2 ),
because |D & (D>>a)| counts u with u,u+a in D, and a pair {u<v} of those
gives the violation (a, b=v-u, u0=u).
"""
import json, random, sys, time

def viol(D):
    """number of violating (a,b,u0) triples contained in the bitmask D"""
    t = 0
    a = 1
    while (D >> a):
        t += (bin(D & (D >> a)).count('1') * (bin(D & (D >> a)).count('1') - 1)) // 2
        a += 1
    return t

def viol_fast(D, nmax=None):
    """number of violating (a,b,u0) with 1 <= a,b <= nmax and u0+a+b <= U."""
    if nmax is None:
        nmax = D.bit_length()          # no bound: counts all a,b >= 1
    t = 0
    for a in range(1, nmax + 1):
        B = D & (D >> a)
        if not B:
            continue
        for b in range(1, nmax + 1):
            t += bin(B & (B >> b)).count('1')
    return t

def cost(rows1, rows0, n):
    t = 0
    for i in range(n):
        for j in range(i + 1, n):
            t += viol_fast(rows1[i] & rows1[j], n - 1)
            t += viol_fast(rows0[i] & rows0[j], n - 1)
    return t

def solve(n, secs=300, seed=0, verbose=True):
    rng = random.Random(seed)
    U = 2 * n - 2
    full = (1 << (U + 1)) - 1
    rows1 = [rng.getrandbits(U + 1) & full for _ in range(n)]
    rows0 = [full & ~r for r in rows1]
    cur = cost(rows1, rows0, n)
    best, bestF = cur, rows1[:]
    t_end = time.time() + secs
    it = 0
    while time.time() < t_end and best > 0:
        it += 1
        z = rng.randrange(n)
        u = rng.randrange(U + 1)
        # flip bit u of row z
        old = rows1[z]
        rows1[z] = old ^ (1 << u)
        rows0[z] = full & ~rows1[z]
        new = cost(rows1, rows0, n)
        if new <= cur or rng.random() < 0.02:
            cur = new
            if cur < best:
                best, bestF = cur, rows1[:]
                if verbose:
                    print(f"  it={it} cost={best}", flush=True)
        else:
            rows1[z] = old
            rows0[z] = full & ~old
    return best, bestF, it

if __name__ == "__main__":
    n = int(sys.argv[1]); secs = float(sys.argv[2]) if len(sys.argv) > 2 else 300
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    best, rows1, it = solve(n, secs, seed)
    print(f"n={n}: best cost {best} after {it} flips", flush=True)
    if best == 0:
        U = 2 * n - 2
        f = [[(rows1[z] >> u) & 1 for z in range(n)] for u in range(U + 1)]
        grid = [[[f[x + y][z] for z in range(n)] for y in range(n)] for x in range(n)]
        sys.path.insert(0, "/home/user/prism")
        from core import is_valid_fast, n_boxes, bad_boxes
        ok = is_valid_fast(grid)
        print("independent check:", ok, "| boxes scanned:", n_boxes(n), flush=True)
        if ok:
            json.dump(grid, open(f"/home/user/prism/results/K2_N{n}.json", "w"))
            print(f"*** BOX-FREE [{n}]^3 IN THE SHIFT FAMILY", flush=True)
