"""CP-SAT model: K-colour [N]^3, no monochromatic axis-aligned box."""
from itertools import combinations
from ortools.sat.python import cp_model


def solve(N, K, time_limit=60.0, workers=2, symmetry=True, hint=None, seed=0):
    """Return (status_str, grid_or_None)."""
    m = cp_model.CpModel()
    c = {}
    for x in range(N):
        for y in range(N):
            for z in range(N):
                c[x, y, z] = m.NewIntVar(0, K - 1, f"c_{x}_{y}_{z}")

    # literals lit[(x,y,z)][k]  <=> (c == k)   (last colour derived as negation)
    lit = {}
    for x in range(N):
        for y in range(N):
            for z in range(N):
                for k in range(K - 1):
                    b = m.NewBoolVar(f"lit_{x}_{y}_{z}_{k}")
                    m.Add(c[x, y, z] == k).OnlyEnforceIf(b)
                    m.Add(c[x, y, z] != k).OnlyEnforceIf(b.Not())
                    lit[x, y, z, k] = b

    def L(x, y, z, k):
        """Bool literal meaning c[x,y,z]==k (returns cp bool var, or negation)."""
        if k < K - 1:
            return lit[x, y, z, k]
        # c == K-1  <=>  not(c==0) and ... ; use a reified var for safety
        b = m.NewBoolVar("")
        for kk in range(K - 1):
            m.AddBoolOr([lit[x, y, z, kk], b])
        for kk in range(K - 1):
            m.AddBoolOr([lit[x, y, z, kk].Not(), b.Not()])
        return b

    # p[x,y1,y2,z1,z2,k] <=> layer x is colour k on the whole rectangle (y1,y2)*(z1,z2)
    for k in range(K):
        for y1, y2 in combinations(range(N), 2):
            for z1, z2 in combinations(range(N), 2):
                ps = []
                for x in range(N):
                    four = [L(x, y1, z1, k), L(x, y1, z2, k),
                            L(x, y2, z1, k), L(x, y2, z2, k)]
                    p = m.NewBoolVar("")
                    for b in four:
                        m.AddImplication(p, b)
                    m.AddBoolOr([b.Not() for b in four] + [p])
                    ps.append(p)
                m.AddAtMostOne(ps)

    if symmetry:
        # colours appear in order of first appearance along lexicographic order
        order = [(x, y, z) for x in range(N) for y in range(N) for z in range(N)]
        m.Add(c[order[0]] == 0)
        run = m.NewIntVar(0, K - 1, "run")
        m.Add(run == 0)
        for i in range(1, len(order)):
            v = c[order[i]]
            m.Add(v <= run + 1)
            run = m.AddMaxEquality(m.NewIntVar(0, K - 1, ""), [run, v]) if False else run
            nr = m.NewIntVar(0, K - 1, "")
            m.AddMaxEquality(nr, [run, v])
            run = nr

    if hint is not None:
        for (x, y, z), v in hint.items():
            m.AddHint(c[x, y, z], v)

    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_search_workers = workers
    s.parameters.random_seed = seed
    st = s.Solve(m)
    name = s.StatusName(st)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        g = [[[s.Value(c[x, y, z]) for z in range(N)] for y in range(N)] for x in range(N)]
        return name, g
    return name, None


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/user/prism")
    from core import is_valid
    N, K = int(sys.argv[1]), int(sys.argv[2])
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 30
    st, g = solve(N, K, tl)
    print(N, K, st)
    if g:
        print("valid:", is_valid(g))
