"""Combined identity-encoding baseline groups (documented method): e1 base+ctl and e6 base."""
import json, sys, collections
from analyze import pct
fin = lambda r: (r['w']['lcp'][-1] if r['w']['lcp'] else {'t': None})
fcp = lambda r: next((p[1] for p in r['w']['paint'] if p[0] == 'first-contentful-paint'), None)
rs = []
for f in ['e1_identity_light', 'e6_identity_hoist']:
    rs += [json.loads(l) for l in open(f'runs/{f}.jsonl')]
rs = [r for r in rs if r['variant'] in ('base', 'ctl')]
def show(l, xs): print(f"{l:8s} n={len(xs)} med {pct(xs,.5):.0f} p75 {pct(xs,.75):.0f} p95 {pct(xs,.95):.0f} min {min(xs)} max {max(xs)}")
a = [fin(r)['t'] for r in rs]; show('all', a)
sl = [t for t in a if t >= 3000]; fa = [t for t in a if t < 3000]; show('slow', sl); show('fast', fa); print('slow share', len(sl), '/', len(a))
print('fast final LCP element:', collections.Counter(fin(r)['el'][:30] for r in rs if fin(r)['t'] < 3000))
print('fast final LCP size:', collections.Counter(fin(r)['size'] for r in rs if fin(r)['t'] < 3000).most_common(4))
show('FCP fast', [fcp(r) for r in rs if fin(r)['t'] < 3000]); show('FCP slow', [fcp(r) for r in rs if fin(r)['t'] >= 3000])
