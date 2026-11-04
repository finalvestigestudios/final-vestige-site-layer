"""R113 synthetic adversarial checks only. No real source fixtures or CMS writes."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

FILE=Path(__file__).resolve().parents[1]/'tools/r113_preparedness_landing_custody.py'
spec=importlib.util.spec_from_file_location('r113',FILE)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
IDS=['s%02d'%i for i in range(1,15)]
SENTENCE=('Household planning reviews clear alerts, local official advice, '
          'accessibility, backup contacts, realistic routes and rehearsal. ')
BODY=('<section class="pa-act"><h2>What to do now</h2>'
      '<p>Call your local emergency number and follow local officials.'
      '{{cite:s01}}{{cite:s02}}{{cite:s03}}</p></section>'
      + ''.join('<h2 id="h%s">Heading %s</h2>'%(i,i) for i in range(8))
      + ''.join('<p id="p%s">%s{{cite:%s}}</p>'%
                (i,SENTENCE*10,IDS[i%14]) for i in range(30))
      + '<p>'+''.join('{{cite:%s}}'%i for i in IDS)+'</p>')
META={'slug':g.GUIDE,'section':'start-here','track':'modern',
      'status':{'editorial':'drafted','publish':'draft'},
      'safety_review':{'state':'pending'},
      'source_use':{i:'Distinct author source-use reading scope' for i in IDS}}
TAX={'base_path':'/preparedness/','slate':[{
     'n':i,'slug':g.GUIDE if i==1 else 'guide-%s'%i,
     'section':'start-here' if i==1 else 'lost-ways',
     'gate':True} for i in range(1,36)]}
def fixture():
    return [BODY,copy.deepcopy(META),copy.deepcopy(TAX)]
def scan(a):
    return g.inspect(*a)
class Core(unittest.TestCase):
    def test_positive_synthetic_is_never_qualified_approval(self):
        d=scan(fixture())
        self.assertEqual(d['slate'],35)
        self.assertEqual(d['unique_routes'],35)
        self.assertEqual(d['source_ids'],14)
        self.assertGreaterEqual(d['visible_citation_occurrences'],40)
        self.assertEqual(d['qualified_safety_review'],'PENDING')
        self.assertFalse(d['may_publish'])
    def test_no_payhip_url_or_purchasable_sku_emitted(self):
        v=g.preview(scan(fixture()))
        self.assertIsNone(v['paid_checkout_link'])
        self.assertEqual(v['merchant_paid_orders'],'N/A')
        self.assertEqual(v['realized_net_revenue_per_1000_qualified_sessions'],'N/A')
        self.assertFalse(v['may_publish'])
        self.assertFalse(v['may_modify_wordpress'])
    def test_honest_private_preview_not_an_active_cta(self):
        h=g.preview(scan(fixture()))['draft_wordpress_copy'].lower()
        for bad in ('href=', 'payhip', '<script', 'utm_', 'checkout', '<form'):
            self.assertNotIn(bad,h)
        self.assertIn('free',h)
        self.assertIn('local emergency officials',h)
    def test_reproducible_review_output(self):
        self.assertEqual(scan(fixture()),scan(fixture()))
    def test_inputs_unchanged(self):
        a=fixture(); b=copy.deepcopy(a);scan(a);self.assertEqual(a,b)
    def test_known_git_blob_algorithm(self):
        self.assertEqual(g.git_blob(b'hello\n'),
                         'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_raw_git_pins_hold_on_untrusted_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'preparedness/content/articles'
            p.mkdir(parents=True)
            (p/'household-emergency-plan.body.html').write_text(BODY)
            (p/'household-emergency-plan.meta.json').write_text(json.dumps(META))
            (p.parent.parent/'taxonomy.json').write_text(json.dumps(TAX))
            with self.assertRaisesRegex(g.Hold,'BODY_GIT_OBJECT_CHANGED'):
                g.check_checkout(td)
    def test_no_approval_from_self_reported_review_state(self):
        with self.assertRaises(g.Hold):
            g.preview({'may_publish':True,'qualified_safety_review':'PENDING'})
    def test_must_have_real_evidence_object(self):
        with self.assertRaises(g.Hold):
            g.preview({})
    def test_whole_slate_not_one_fake_page(self):
        a=fixture();a[2]['slate']=[]
        with self.assertRaises(g.Hold):scan(a)

BODY_BAD=[
 ('comment_cite',lambda b:b+'<!-- {{cite:s01}} -->'),
 ('attribute_cite',lambda b:b+'<p title="{{cite:s01}}"></p>'),
 ('hidden_cite',lambda b:b+'<p hidden>{{cite:s01}}</p>'),
 ('aria_hidden_cite',lambda b:b+'<span aria-hidden="true">{{cite:s01}}</span>'),
 ('inert_cite',lambda b:b+'<p inert>{{cite:s01}}</p>'),
 ('css_hidden_cite',lambda b:b+'<span style="display:none">{{cite:s01}}</span>'),
 ('visibility_hidden_cite',lambda b:b+'<span style="visibility:hidden">{{cite:s01}}</span>'),
 ('script_tag',lambda b:b+'<script>bad()</script>'),
 ('script_cite',lambda b:b+'<script>{{cite:s01}}</script>'),
 ('style_cite',lambda b:b+'<style>{{cite:s01}}</style>'),
 ('template_cite',lambda b:b+'<template>{{cite:s01}}</template>'),
 ('noscript',lambda b:b+'<noscript>text</noscript>'),
 ('svg',lambda b:b+'<svg></svg>'),
 ('iframe',lambda b:b+'<iframe></iframe>'),
 ('object',lambda b:b+'<object></object>'),
 ('duplicate_html_id',lambda b:b+'<p id="p1"></p>'),
 ('unclosed_html',lambda b:b+'<div>'),
 ('stray_close',lambda b:b+'</div>'),
 ('unknown_token',lambda b:b+'{{unsafe:foo}}'),
 ('unknown_cite',lambda b:b+'{{cite:unlisted}}'),
 ('removed_source',lambda b:b.replace('{{cite:s14}}','')),
 ('action_box_removed',lambda b:b.replace('pa-act','pa-unknown')),
 ('remove_local_officials',lambda b:b.replace('local officials','others')),
 ('remove_emergency_number',lambda b:b.replace('emergency number','number')),
 ('double_action',lambda b:b+'<section class="pa-act"></section>'),
 ('truncate',lambda b:b[:1000]),
 ('lose_depth',lambda b:b.replace(SENTENCE*10,SENTENCE)),
 ('missing_citation_count',lambda b:b.replace('{{cite:s01}}','')),
]
for name, mutate in BODY_BAD:
    def make(m):
        def run(self):
            a=fixture();a[0]=m(a[0])
            with self.assertRaises(g.Hold):scan(a)
        return run
    setattr(Core,'test_body_adversary_'+name,make(mutate))
META_BAD=[
 ('slug',lambda x:x.update(slug='wrong')),
 ('section',lambda x:x.update(section='water')),
 ('track',lambda x:x.update(track='lost-ways')),
 ('editorial',lambda x:x['status'].update(editorial='approved')),
 ('published',lambda x:x['status'].update(publish='published')),
 ('safety',lambda x:x['safety_review'].update(state='passed')),
 ('missing_scopes',lambda x:x.pop('source_use')),
 ('scope_removed',lambda x:x['source_use'].pop('s01')),
 ('scope_blank',lambda x:x['source_use'].update(s01='')),
 ('extra_source',lambda x:x['source_use'].update(s99='fabricated')),
 ('source_id_invalid',lambda x:x['source_use'].update({'bad id':'value'})),
 ('source_scope_not_string',lambda x:x['source_use'].update(s01=True)),
]
for name,mutate in META_BAD:
    def make(m):
        def run(self):
            a=fixture();m(a[1])
            with self.assertRaises(g.Hold):scan(a)
        return run
    setattr(Core,'test_meta_adversary_'+name,make(mutate))
TAX_BAD=[
 ('wrong_base',lambda t:t.update(base_path='/other/')),
 ('missing_slate',lambda t:t.pop('slate')),
 ('short',lambda t:t['slate'].pop()),
 ('duplicate_number',lambda t:t['slate'][1].update(n=1)),
 ('wrong_number',lambda t:t['slate'][1].update(n=99)),
 ('duplicate_url',lambda t:t['slate'][1].update(slug=g.GUIDE,section='start-here')),
 ('duplicate_route',lambda t:t['slate'][2].update(slug='guide-2',section='lost-ways')),
 ('guide_missing',lambda t:t['slate'][0].update(slug='elsewhere')),
 ('guide_wrong_section',lambda t:t['slate'][0].update(section='food')),
 ('guide_ungated',lambda t:t['slate'][0].update(gate=False)),
 ('slug_traversal',lambda t:t['slate'][1].update(slug='../up')),
 ('slug_slash',lambda t:t['slate'][1].update(slug='foo/bar')),
 ('section_uppercase',lambda t:t['slate'][1].update(section='Food')),
 ('malformed_row',lambda t:t['slate'].__setitem__(1,None)),
]
for name,mutate in TAX_BAD:
    def make(m):
        def run(self):
            a=fixture();m(a[2])
            with self.assertRaises((g.Hold,TypeError)):scan(a)
        return run
    setattr(Core,'test_taxonomy_adversary_'+name,make(mutate))
if __name__=='__main__':unittest.main()
