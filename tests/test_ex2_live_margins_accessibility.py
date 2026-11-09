#!/usr/bin/env python3
"""Synthetic contract tests: not production, WordPress rendering, axe or WCAG approval."""
import importlib.util
import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'tools/experience-2/propose_live_margins_accessibility.py'
spec = importlib.util.spec_from_file_location('margins', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

spans = '\n'.join(
    '<span class="fv-margin-strip__item" style="--i:%d">Synthetic test note %d, not a historical claim.</span>' % (i, i+1)
    for i in range(72))
raw = ('''<!-- wp:html -->
<div class="fv-margin-strip fv-margin-strip--rotator"><div class="fv-margin-strip__inner">
<div class="fv-margin-strip__label">Hidden in the Margins</div>
<div class="fv-margin-strip__window" tabindex="0" aria-live="off" aria-label="Rotating source and accountability notes">'''
       + spans + '''</div></div></div>
<style>@media(prefers-reduced-motion:reduce){.fv-margin-strip__item:nth-child(1){display:block}}</style>
<!-- /wp:html --><div id="out-of-scope">MUST NOT COPY THIS</div>''')
checks = []

def check(name, thunk, expected=True):
    try:
        actual = bool(thunk())
    except (ValueError, AssertionError):
        actual = False
    checks.append({'name':name, 'pass': actual == expected})

check('positive 72 source spans preserved', lambda: len(m.SPAN.findall(m.build(raw)[0])) == 72)
check('72 notes duplicated into accessible list', lambda: m.build(raw)[0].count('<li>') == 72)
check('original 72 texts conserved', lambda: all('Synthetic test note %d' % n in m.build(raw)[0] for n in range(1,73)))
check('animated copy excluded from accessible tree', lambda: 'aria-hidden="true"' in m.build(raw)[0])
check('source document outside first block not exported', lambda: 'MUST NOT COPY THIS' not in m.build(raw)[0])
check('not adding JavaScript', lambda: '<script' not in m.build(raw)[0].lower())
check('reordered note index rejected', lambda: m.build(raw.replace('style="--i:41"', 'style="--i:140"')), False)
check('duplicate note index rejected', lambda: m.build(raw.replace('style="--i:71"', 'style="--i:70"')), False)
check('missing record rejected', lambda: m.build(raw.replace(
    '<span class="fv-margin-strip__item" style="--i:71">Synthetic test note 72, not a historical claim.</span>', '')), False)
check('invalid embedded HTML rejected', lambda: m.build(raw.replace('Synthetic test note 14', '<script>alert(1)</script>')), False)
check('already patched content rejected', lambda: m.build(raw.replace('fv-margin-strip__window"', 'fv-margin-strip__window fv-margin-strip__ledger"')), False)
check('missing baseline keyboard semantics rejected', lambda: m.build(raw.replace('tabindex="0"', '')), False)
check('missing reduced-motion safeguard rejected', lambda: m.build(raw.replace('nth-child(1){display:block}', 'nth-child(1){display:none}')), False)
check('wrong Page 6 id rejected', lambda: m.read_page({'data':{'id':8,'status':'publish','content':raw}}), False)
check('draft Page 6 rejected', lambda: m.read_page({'data':{'id':6,'status':'draft','content':raw}}), False)
check('missing editor content rejected', lambda: m.read_page({'data':{'id':6,'status':'publish'}}), False)
summary = {'scope':'SYNTHETIC contract only; no CMS writes', 'passed':sum(c['pass'] for c in checks), 'total':len(checks), 'checks':checks}
print(json.dumps(summary, indent=2))
if summary['passed'] != summary['total']:
    raise SystemExit(1)
