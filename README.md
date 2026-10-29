# Ramsey — monochromatic boxes in coloured grids

Code, colourings and notes for the problem: colour the grid `[n]^3` with `c` colours so
that **no axis-aligned box** `{x1,x2} x {y1,y2} x {z1,z2}` (all three pairs distinct) has
all 8 vertices the same colour. Equivalently, lower-bound

> `N(c,d)` = least R such that every c-colouring of `[R]^d` has a monochromatic box,

the cube case of the *grid Ramsey* problem for boxes studied by Cooper, Fenner and
Purewal (*Monochromatic boxes in colored grids*, arXiv:0810.3019) and by Agnarsson,
Doerr and Schoen (*Coloring t-dimensional m-boxes*, Discrete Math. 226 (2001)).

## Results

Two-sided windows for the cube (`N(c,3)`):

| c | lower bound | witness | upper bound |
|---|-------------|---------|-------------|
| 1 | 2 | — | 2 (exact) |
| 2 | 13 | literature (CFP Fig. 3, row 12/12/27) | 22 |
| 3 | **24** | our `[23]^3` colouring | 93 |
| 4 | **41** | our `[40]^3` colouring | 277 |
| 5 | **45** | our `[44]^3` colouring | 657 |

The upper bounds follow from the double-counting recursion of CFP (Lemma 4); we give an
independent Zarankiewicz/C4 proof that reproduces exactly the same numbers.
The c = 2 lower bound 13 is also already implied by the CFP table (a 2-colouring of
`[12,12,27]` restricts to one of `[12]^3`), so our own `[11]^3` colouring gives only 12.

**Read `docs/LITERATURE.md` before citing anything here.** In short: our upper bounds are
*not* new (they coincide exactly with Cooper–Fenner–Purewal Lemma 4 evaluated for the
cube), and the only claims we believe to be unrecorded are the c = 3,4,5 lower bounds and
the structural lemmas.

## Layout

```
code/      Python: constructors, SAT/CP-SAT models, local search, verifiers
results/   verified colourings, grid[x][y][z] = colour (JSON)
docs/      working notes, including what is and is not new
paper/     LaTeX source of the accompanying note
```

## Reproduce

```bash
pip install python-sat ortools
python3 code/layer_ls.py 40 4            # build & verify a 4-colouring of [40]^3
python3 code/verify.py results/K4_N40.json
python3 code/cyclic.py 11                # K=2, N=11 difference-set construction
python3 code/upper_bound.py              # the C4 / Lemma-4 thresholds
python3 code/scaling.py                  # lower vs upper bounds for general d
```

## Verification

`code/verify.py` brute-forces every box of a stored colouring
(`C(n,2)^3` boxes; 846 million at n = 44) and `core.is_valid_fast` checks slice pairs;
the two agree on random inputs and both reject deliberately corrupted grids.

## License

MIT — see `LICENSE`.
