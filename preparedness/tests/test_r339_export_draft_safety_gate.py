"""R339 self-contained synthetic adversarial tests: no release or QD pass."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from preparedness.tools import r339_export_draft_safety_gate as gate

SECTIONS={'start-here','water','food','shelter-power','health-sanitation','family-communication','lost-ways','field-tools'}
TOOLS=('family-reunification-card','home-fire-escape-worksheet','kit-builder','power-outage-planner','reunification-plan','water-planner')
SLUGS=[f'article-{i+1:02d}' for i in range(35)]+list(TOOLS)
ROUTES={s:f'https://finalvestige.com/preparedness/{"field-tools" if s in TOOLS else "start-here"}/{s}/' for s in SLUGS}

def content(slug):
    if slug not in ROUTES:return '<div id="hub"><a href="/preparedness/">Archive</a></div>'
    j={'@graph':[{'@type':'Article','mainEntityOfPage':ROUTES[slug],'@id':ROUTES[slug]+'#article','isAccessibleForFree':True}]}
    return f'<div data-slug="{slug}"><h1 id="main">Guide</h1><p>Draft: not public</p><p>Independent safety/source and QD verification pending</p><a href="/preparedness/start-here/article-01/">Guide</a><script type="application/ld+json">{json.dumps(j)}</script></div>'

def fixture():
    out={}
    for slug in [*SLUGS,*('hub-'+s for s in SECTIONS),'landing']:
        body=content(slug)
        out[f'wp/{slug}.html']=('<!-- wp:html -->\n<style>.pa{}</style>\n'+body+'\n<!-- /wp:html -->\n').encode()
        out[f'preview/{slug}.html']=('<!doctype html><html lang="en"><head><meta name="robots" content="noindex,nofollow"></head><body><main>'+body+'</main></body></html>').encode()
    return out

def change(out,slug,old,new):
    for group in ('wp','preview'):
        key=f'{group}/{slug}.html';out[key]=out[key].replace(old.encode(),new.encode())

class ExportHold(unittest.TestCase):
    def setUp(self):self.out=fixture()
    def scan(self):return gate.check(ROUTES,SECTIONS,self.out)
    def failcode(self,code):
        r=self.scan();self.assertEqual(r['state'],'INVALID_HARD_HOLD');self.assertTrue(any(code in x for x in r['errors']),r['errors'])
    def test_all_100_synthetic_still_draft(self):
        r=self.scan();self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r['errors'])
        self.assertEqual(r['private_export_pairs_inspected'],50)
        self.assertEqual(r['article_jsonld_identities_inspected'],41)
        self.assertFalse(r['may_publish']);self.assertFalse(r['qualified_qd_pass']);self.assertFalse(r['native_build_verified'])
    def test_native_missing_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(gate.audit_native(Path(d))['state'],'INVALID_HARD_HOLD')
    def test_missing_file(self):self.out.pop('wp/landing.html');self.failcode('EXACT_50_WP_AND_50_PREVIEW_OUTPUTS_REQUIRED')
    def test_draft_noindex(self):change(self.out,'landing','noindex,nofollow','index,follow');self.failcode('PRIVATE_PREVIEW_NOINDEX_MISSING')
    def test_unresolved_target(self):change(self.out,'article-01','/preparedness/start-here/article-01/','/preparedness/start-here/missing/');self.failcode('UNRESOLVED_RENDERED_DESTINATION')
    def test_merchant_blocked(self):change(self.out,'article-01','/preparedness/start-here/article-01/','https://payhip.com/b/fake');self.failcode('UNAPPROVED_MERCHANT_LINK')
    def test_get_form_named_field_blocked(self):change(self.out,'article-01','<h1 id="main">','<form><input name="child_contact"></form><h1 id="main">');self.failcode('POTENTIAL_NAMED_FORM_GET_EXPOSURE')
    def test_qd_marker_not_safety(self):change(self.out,'article-01','Independent safety/source and QD verification pending','Approved for publication');self.failcode('UNSAFE_PUBLIC_APPROVAL_LANGUAGE')
    def test_distinct_held_tool_identity(self):
        change(self.out,'article-01','href="/preparedness/start-here/article-01/"','href="/preparedness/field-tools/family-reunification-card/"')
        r=self.scan();self.assertEqual(r['state'],'DRAFT_HARD_HOLD');self.assertEqual(r['links_to_unpublished_family_tools'],1);self.assertFalse(r['may_publish'])

def create_dynamic(slug,mode):
    def check(self):
        if mode=='canonical':change(self.out,slug,ROUTES[slug],'https://finalvestige.com/preparedness/wrong/'+slug+'/');self.failcode('JSONLD_CANONICAL_SOURCE_DRIFT')
        if mode=='badge':change(self.out,slug,'Draft: not public','Published');self.failcode('UNSAFE_PUBLIC_APPROVAL_LANGUAGE')
    return check
for slug in SLUGS:
    for mode in ('canonical','badge'):
        setattr(ExportHold,f'test_{slug.replace("-","_")}_{mode}',create_dynamic(slug,mode))
