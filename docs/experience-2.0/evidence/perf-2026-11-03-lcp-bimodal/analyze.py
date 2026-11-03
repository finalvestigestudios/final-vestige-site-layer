"""Summarise harness JSONL: per variant, split into LCP modes, report median / p75 / p95 and slow share.

usage: python analyze.py file.jsonl [file2.jsonl ...] [--split MS]   (default split 3000 ms: >= split is the 'slow' mode)
Percentiles use linear interpolation. n is printed everywhere; nothing here mixes files unless you pass several.
"""
import sys, json, statistics, collections


def pct(a, p):
    a = sorted(a)
    if not a:
        return None
    k = (len(a) - 1) * p
    f = int(k)
    c = min(f + 1, len(a) - 1)
    return a[f] + (a[c] - a[f]) * (k - f)


def fin(r):
    l = r["w"]["lcp"]
    return l[-1] if l else {"t": None, "el": "none"}


def fcp(r):
    return next((p[1] for p in r["w"]["paint"] if p[0] == "first-contentful-paint"), None)


def row(label, xs):
    if not xs:
        return f"{label:34s} n=0"
    return f"{label:34s} n={len(xs):3d} min {min(xs):5.0f} med {pct(xs, .5):5.0f} p75 {pct(xs, .75):5.0f} p95 {pct(xs, .95):5.0f} max {max(xs):5.0f}"


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    split = 3000
    if "--split" in sys.argv:
        split = int(sys.argv[sys.argv.index("--split") + 1])
    recs = []
    for f in files:
        recs += [json.loads(l) for l in open(f, encoding="utf-8")]
    by = collections.defaultdict(list)
    for r in recs:
        by[(r["variant"], r["cache"], r["cpu"], r.get("enc", "none"))].append(r)
    for key, rs in by.items():
        print(f"== variant={key[0]} cache={key[1]} cpu={key[2]} enc={key[3]}  runs={len(rs)}")
        lcp = [fin(r)["t"] for r in rs if fin(r)["t"] is not None]
        slow = [r for r in rs if fin(r)["t"] is not None and fin(r)["t"] >= split]
        fast = [r for r in rs if fin(r)["t"] is not None and fin(r)["t"] < split]
        print(row("LCP all", lcp))
        print(row("LCP fast (<%d)" % split, [fin(r)["t"] for r in fast]))
        print(row("LCP slow (>=%d)" % split, [fin(r)["t"] for r in slow]))
        print(f"slow share {len(slow)}/{len(rs)} = {100 * len(slow) / max(1, len(rs)):.0f}%")
        print(row("FCP all", [fcp(r) for r in rs if fcp(r)]))
        print(row("FCP fast", [fcp(r) for r in fast if fcp(r)]))
        print(row("FCP slow", [fcp(r) for r in slow if fcp(r)]))
        els = collections.Counter(fin(r)["el"][:40] for r in rs)
        print("final LCP element:", dict(els))
        print(row("nav responseEnd", [r["nav"][0] for r in rs]))
        print(row("load event", [r["nav"][2] for r in rs]))


if __name__ == "__main__":
    main()
