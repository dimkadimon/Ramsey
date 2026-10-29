"""Layer decomposition.

A K-colouring of [N]^3 with no monochromatic box is EXACTLY a choice of N
K-colourings of the N x N grid ("layers") such that no feature (colour c,
rectangle r) is "monochromatic-c on r" in more than one layer.

Proof: a monochromatic box = two layers x1<x2 that are both monochromatic in
colour c on the same rectangle r (the yz-face of the box).

So the search becomes: pick N layers with pairwise disjoint feature sets.
"""
import sys
from itertools import combinations

sys.path.insert(0, "/home/user/prism")


def layer_features(layer, K):
    """set of (c, y1, y2, z1, z2) for which the 4 corners are all colour c."""
    N = len(layer)
    feats = set()
    for c in range(K):
        masks = [sum(1 << z for z in range(N) if layer[y][z] == c) for y in range(N)]
        for y1, y2 in combinations(range(N), 2):
            inter = masks[y1] & masks[y2]
            zs = [z for z in range(N) if inter >> z & 1]
            for z1, z2 in combinations(zs, 2):
                feats.add((c, y1, y2, z1, z2))
    return feats


def layers_of(grid):
    """split a 3D grid into its x-layers (list of 2D grids)."""
    N = len(grid)
    return [[[grid[x][y][z] for z in range(N)] for y in range(N)] for x in range(N)]


def check_decomposition(grid, K):
    layers = layers_of(grid)
    seen = set()
    for i, L in enumerate(layers):
        f = layer_features(L, K)
        if f & seen:
            return False, i, sorted(f & seen)[:5]
        seen |= f
    return True, None, None


if __name__ == "__main__":
    import json
    g = json.load(open(sys.argv[1]))
    K = int(sys.argv[2])
    N = len(g)
    print("N =", N, " layer features per layer:",
          [len(layer_features(L, K)) for L in layers_of(g)])
    print("decomposition consistent:", check_decomposition(g, K))
