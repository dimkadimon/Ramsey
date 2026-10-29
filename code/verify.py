"""Independent verifier for a stored colouring JSON.

Deliberately brute-force (enumerates every box) and independent of the
solvers: no shared code with the search, apart from nothing at all.

Usage:  python3 verify.py results/K3_N20.json
"""
import json
import sys


def check(grid, show=5):
    N = len(grid)
    colours = sorted({c for X in grid for Y in X for c in Y})
    print(f"grid {N}x{N}x{N}, {len(colours)} distinct colours {colours}")
    count = 0
    bad = []
    for x1 in range(N):
        for x2 in range(x1 + 1, N):
            for y1 in range(N):
                for y2 in range(y1 + 1, N):
                    for z1 in range(N):
                        for z2 in range(z1 + 1, N):
                            c = grid[x1][y1][z1]
                            if (grid[x1][y1][z2] == c and grid[x1][y2][z1] == c and
                                grid[x1][y2][z2] == c and grid[x2][y1][z1] == c and
                                grid[x2][y1][z2] == c and grid[x2][y2][z1] == c and
                                grid[x2][y2][z2] == c):
                                count += 1
                                bad.append((c, x1, x2, y1, y2, z1, z2))
                                if len(bad) <= show:
                                    print("  monochromatic box:", bad[-1])
    nboxes = (N * (N - 1) // 2) ** 3
    print(f"boxes examined: {nboxes}; monochromatic: {count}")
    print("VERDICT:", "VALID (no monochromatic box)" if count == 0 else "INVALID")
    return count == 0


if __name__ == "__main__":
    for path in sys.argv[1:]:
        print("==", path)
        check(json.load(open(path)))
