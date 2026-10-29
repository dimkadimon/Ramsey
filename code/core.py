"""Core utilities: check colourings, count monochromatic boxes."""
from itertools import combinations


def boxes(N):
    """All axis-aligned rectangular prisms in [N]^3, as tuples of 8 points."""
    for x1, x2 in combinations(range(N), 2):
        for y1, y2 in combinations(range(N), 2):
            for z1, z2 in combinations(range(N), 2):
                yield ((x1, y1, z1), (x1, y1, z2), (x1, y2, z1), (x1, y2, z2),
                       (x2, y1, z1), (x2, y1, z2), (x2, y2, z1), (x2, y2, z2))


def bad_boxes(grid, limit=None):
    """Return list of monochromatic boxes (empty => valid colouring)."""
    N = len(grid)
    out = []
    for b in boxes(N):
        c0 = grid[b[0][0]][b[0][1]][b[0][2]]
        if all(grid[p[0]][p[1]][p[2]] == c0 for p in b):
            out.append((c0, b))
            if limit and len(out) >= limit:
                return out
    return out


def is_valid(grid):
    return not bad_boxes(grid, limit=1)


def n_boxes(N):
    return (N * (N - 1) // 2) ** 3


def is_valid_fast(grid, K=None):
    """O(K N^4) check: two slices are a monochromatic box iff they are both
    monochromatic in the same colour on the same yz-rectangle.
    Independent of the construction code path (works directly from the
    definition, comparing every pair of slices)."""
    N = len(grid)
    K = K if K is not None else (1 + max(c for X in grid for Y in X for c in Y))
    pairs = list(combinations(range(N), 2))
    for c in range(K):
        # masks[x][y] = columns z with colour c in slice x, row y
        masks = [[0] * N for _ in range(N)]
        for x in range(N):
            for y in range(N):
                m = 0
                for z in range(N):
                    if grid[x][y][z] == c:
                        m |= 1 << z
                masks[x][y] = m
        for (y1, y2) in pairs:
            b = [masks[x][y1] & masks[x][y2] for x in range(N)]
            for i in range(N):
                if b[i].bit_count() < 2:
                    continue
                for j in range(i + 1, N):
                    if (b[i] & b[j]).bit_count() >= 2:
                        return False
    return True
