#!/usr/bin/env python3
"""Synthetic positive and targeted mutation controls, not a live WP acceptance."""
import copy
import importlib.util
import json
from pathlib import Path

p = Path(__file__).resolve().parents[2] / 'tools/experience-2/verify_live_homepage_reconciliation.py'
spec = importlib.util.spec_from_file_location('fvaudit', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

nav = '<nav class="fv-hf__chapter-nav" aria-label="Explore the chapters">' + ''.join(
    '<a href="#' + s + '">Chapter</a>' for s in mod.CHAPTER_IDS) + '</nav>'
anchors = ''.join('<section id="' + s + '">text</section>' for s in mod.CHAPTER_IDS)
margins = ''.join('<span class="fv-margin-strip__item" style="--i:%d">fact</span>' % i for i in range(72))
source = ('<!-- wp:html -->\n'+nav+anchors+margins+'<a href="/focus/">Focus</a>'+
          '<a href="/dispatch/">Dispatch</a>\n' +
          '<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->\n'+
          '<a href="https://www.nasa.gov/">NASA</a><a href="https://www.rmg.co.uk/">RMG</a>'+
          '<a href="https://digitalcollections.nypl.org/">NYPL</a>\n'+
          '<img src="s67-19766.webp"><img src="Franklinexpeditionnote.jpg">' +
          '<img src="edit-017-v02-nypl-5003296-original.jpg">' +
          '<img src="focus_complete_cover.webp"><!-- /wp:html -->')
page = {'data':{'id':6,'status':'publish','modified':'test-only','content':source}}
checks=[]
def run(name,candidate,expected):
    try:actual=mod.audit(candidate)['source_checks_pass']
    except Exception:actual=False
    checks.append({'case':name,'pass':actual is expected})
run('synthetic positive Gutenberg source',page,True)
mutations = {
    'absent 7th chapter':lambda s:s.replace('href="#fv-hf-mind-title"','href="#dead-end"'),
    'absent chapter anchor':lambda s:s.replace('id="fv-hf-observer"','id="missing-observer"'),
    'removed margin':lambda s:s.replace('<span class="fv-margin-strip__item" style="--i:71">fact</span>',''),
    'reordered margins':lambda s:s.replace('style="--i:0"','style="--i:999"'),
    'removed Jetpack':lambda s:s.replace('<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->',''),
    'duplicated Jetpack':lambda s:s.replace('<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->','<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->'*2),
    'Focus vanished':lambda s:s.replace('href="/focus/"','href="/other/"'),
    'Dispatch vanished':lambda s:s.replace('href="/dispatch/"','href="/other/"'),
    'private shortcode leaked':lambda s:s+'[fv_ex2_playground]',
    'private review URL leaked':lambda s:s+'fv-ex2-focus-review',
    'broken NASA provenance':lambda s:s.replace('nasa.gov','example.com'),
    'missing archival image':lambda s:s.replace('Franklinexpeditionnote.jpg','not-a-document.jpg'),
    'missing Focus cover':lambda s:s.replace('focus_complete_cover.webp','other-cover.webp'),
}
for name,mutate in mutations.items():
    v=copy.deepcopy(page);v['data']['content']=mutate(source);run(name,v,False)
v=copy.deepcopy(page);v['data']['id']=9;run('wrong page ID',v,False)
v=copy.deepcopy(page);v['data']['status']='draft';run('unpublished status',v,False)
v=copy.deepcopy(page);del v['data']['content'];run('no raw editor content',v,False)
summary={'scope':'synthetic Gutenberg editor strings only; NOT production or WordPress Core','passed':sum(c['pass'] for c in checks),'total':len(checks),'cases':checks}
print(json.dumps(summary,indent=2))
if summary['passed']!=summary['total']:raise SystemExit(1)
