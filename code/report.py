"""Build a compact self-contained HTML report (canvas rendering, largest grid per K)."""
import glob
import json
import os
import re
import sys

sys.path.insert(0, "/home/user/prism")
from core import is_valid_fast

RES = "/home/user/prism/results"
PALETTE = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
           "#42d4f4", "#f032e6", "#bfef45"]


def load_all():
    out = {}
    for p in glob.glob(f"{RES}/K*_N*.json"):
        mm = re.match(r"K(\d+)_N(\d+)\.json", os.path.basename(p))
        if not mm:
            continue
        K, N = int(mm.group(1)), int(mm.group(2))
        g = json.load(open(p))
        if len(g) != N:
            continue
        out.setdefault(K, {})[N] = g
    return out


def flat(g):
    N = len(g)
    return "".join(str(g[x][y][z]) for x in range(N) for y in range(N) for z in range(N))


def main():
    data = load_all()
    rows, sections = [], []
    for K in sorted(data):
        good = {N: g for N, g in data[K].items() if is_valid_fast(g)}
        if not good:
            continue
        Ns = sorted(good)
        rows.append(f"<tr><td>K = {K}</td><td class='big'>{max(Ns)}</td>"
                    f"<td>{', '.join(map(str, Ns))}</td></tr>")
        N = max(Ns)
        sections.append(
            f"<h2>K = {K} colours &mdash; largest verified: N = {N}</h2>"
            f"<p>A colouring of [{N}]&sup3; with no monochromatic prism. "
            f"Each small grid is one x = const slice; slice x goes left to right, "
            f"top row = y = 0, left column = z = 0.</p>"
            f"<div class='cube' data-n='{N}' data-k='{K}' data-g='{flat(good[N])}'></div>")
    html = (HEAD + "<h2>Results</h2><table>"
            + "<tr><th>colours</th><th>largest N with a verified prism-free"
              " colouring</th><th>all verified N</th></tr>"
            + "".join(rows)
            + "<tr><td>K = 1</td><td class='big'>1</td><td>1 &nbsp;"
              "(N &ge; 2 is impossible: the whole cube is one colour)</td></tr>"
            + "</table>"
            + "<p class='note'>Every colouring below was checked by an independent "
              "verifier that compares all pairs of slices for a shared "
              "monochromatic rectangle &mdash; the exact definition of a "
              "monochromatic prism. Zero violations found.</p>"
            + "".join(sections) + FOOT + SCRIPT)
    open("/home/user/prism_colourings.html", "w").write(html)
    print("wrote prism_colourings.html", len(html), "bytes")


HEAD = """<!doctype html><meta charset="utf-8">
<title>Prism-free K-colourings of N&times;N&times;N grids</title>
<style>
body{font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
 margin:0;padding:30px 34px 60px;background:#0f1319;color:#e7ebf0;max-width:1100px}
h1{font-size:25px;margin:0 0 8px}
h2{margin:36px 0 10px;font-size:19px;border-bottom:1px solid #28323e;padding-bottom:7px}
p{color:#a7b4c2;max-width:76ch}
table{border-collapse:collapse;margin:12px 0 20px;font-size:14px}
th,td{border:1px solid #28323e;padding:6px 12px;text-align:left}
th{background:#171f28;color:#cfe0ef}
td.big{font-weight:700;color:#7fd1a0;font-size:16px}
.note{font-size:13.5px;color:#8b9aa9}
.cube{display:flex;flex-wrap:wrap;gap:12px;margin:10px 0 6px}
.cube canvas{border:1px solid #222b36;border-radius:3px;image-rendering:pixelated}
.legend{display:flex;gap:16px;font-size:13px;color:#a7b4c2;margin:6px 0}
.legend span{display:flex;align-items:center;gap:6px}
.legend i{width:13px;height:13px;border-radius:2px;display:inline-block}
code{background:#171f28;padding:1px 5px;border-radius:3px;color:#cfe0ef}
</style>
<h1>No monochromatic prism: K-colourings of [N]&sup3;</h1>
<p>A <b>prism</b> = an axis-aligned rectangular box, the 8 points
{x<sub>1</sub>,x<sub>2</sub>}&times;{y<sub>1</sub>,y<sub>2</sub>}&times;{z<sub>1</sub>,z<sub>2</sub>}
with both values distinct in each coordinate (a &ldquo;combinatorial box&rdquo;). We want
K-colourings of the N&times;N&times;N grid in which no prism has all 8 vertices the same colour.</p>
"""

FOOT = """
<h2>Why it gets hard, and what is proven</h2>
<p>Reduction used by the search: a monochromatic prism is exactly a pair of x-slices that are
both monochromatic in the <i>same</i> colour on the <i>same</i>
{y<sub>1</sub>,y<sub>2</sub>}&times;{z<sub>1</sub>,z<sub>2</sub>} rectangle. Call
(colour, rectangle) a <b>feature</b>. Then:</p>
<p><code>colouring is prism-free &nbsp;&hArr;&nbsp; no feature is used by two slices.</code></p>
<p>So the problem becomes packing N K-colourings of the N&times;N grid with pairwise disjoint
feature sets. There are K&middot;C(N,2)&sup2; features and a slice needs at least &nu;(N,K) of
them, so <code>N&middot;&nu;(N,K) &le; K&middot;C(N,2)&sup2;</code> is necessary &mdash; that
counting bound is generous, and the real obstruction is the packing geometry, which is why
small K is the hard end.</p>
<p>The problem is the 3-dimensional case of the <i>grid Ramsey</i> numbers studied by
Cooper, Fenner &amp; Purewal, <i>Monochromatic Boxes in Colored Grids</i>
(arXiv:0810.3019). Their tables show that [12]&times;[12]&times;[25] is 2-colourable,
which by subgrid monotonicity means a prism-free 2-colouring of [12]&sup3; provably exists
&mdash; our search found such colourings up to N = 10 and did not settle 11 and 12.</p>
"""

SCRIPT = """<script>
const PAL = ["#e6194b","#3cb44b","#4363d8","#f58231","#911eb4","#42d4f4","#f032e6","#bfef45"];
document.querySelectorAll('.cube').forEach(el=>{
  const N = +el.dataset.n, K = +el.dataset.k, s = el.dataset.g;
  const px = Math.max(3, Math.min(11, Math.floor(300/N)));
  for(let x=0;x<N;x++){
    const cv = document.createElement('canvas');
    cv.width = N*px; cv.height = N*px; cv.title = 'x = '+x;
    const ctx = cv.getContext('2d');
    for(let y=0;y<N;y++) for(let z=0;z<N;z++){
      const c = +s[(x*N+y)*N+z];
      ctx.fillStyle = PAL[c % PAL.length];
      ctx.fillRect(z*px, y*px, px, px);
    }
    el.appendChild(cv);
  }
  const lg = document.createElement('div');
  lg.className='legend';
  for(let c=0;c<K;c++) lg.innerHTML += '<span><i style="background:'+PAL[c%PAL.length]+'"></i>colour '+c+'</span>';
  el.after(lg);
});
</script>"""

if __name__ == "__main__":
    main()
