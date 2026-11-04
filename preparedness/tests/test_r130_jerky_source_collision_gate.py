"""R130 synthetic safety/adversarial tests. No production paths or network writes."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools'))
import r130_jerky_source_collision_gate as gate

URL = 'https://nchfp.uga.edu/how/dry/recipes/jerky'

def entry(source_id, *, trailing=False, supports='Read A', notes='Read B'):
    return {'id':source_id, 'url':URL+('/' if trailing else ''),'supports':supports,
            'notes':notes,'verified_on':'2026-10-29','human_link_check':False}

def fixture():
    hist_old={'sources':[entry('safe-other'),entry(gate.OLD,trailing=True)]}
    hist_new={'sources':[entry('safe-other'),entry(gate.NEW, notes='different source scope')]}
    food={'sources':[entry(gate.NEW, supports='Much wider interpretation',notes='independently authored')]}
    data={}
    for version in ('old','new','rc'):
        data[version]={'hist':copy.deepcopy(hist_new if version=='new' else hist_old)}
        for slug,n in zip(gate.SLUGS,(7,1)):
            source_id=gate.NEW if version=='new' else gate.OLD
            body='<h2>Reader</h2>\n<p>'+ (('{{cite:'+source_id+'}}') * n)+'{{cite:safe-other}}</p>'
            source_use={source_id:'Specific author scope', 'safe-other':'Other'}
            meta={'slug':slug,'status':{'publish':'draft'},
                  'safety_review':{'state':'pending','scope':'review required'}, 'source_use':source_use}
            data[version][slug+'_body']=body
            data[version][slug+'_meta']=meta
    data['rc']['food']=food
    return data

class Baselines(unittest.TestCase):
    def test_hold_not_approval(self):
        result=gate.inspect(fixture())
        self.assertEqual(result['status'],'HOLD_HUMAN_SOURCE_ID_COLLISION')
        for field in ('may_merge','may_publish','independent_QD_PASS','medical_safety_verified'):
            self.assertFalse(result[field])
    def test_collision_detected(self):
        result=gate.inspect(fixture())
        self.assertEqual(result['source_collision']['id'],gate.NEW)
        self.assertFalse(result['source_collision']['identical_supports'])
        self.assertTrue(result['source_collision']['source_interpretations_require_human_review'])
    def test_eight_retargets(self):
        result=gate.inspect(fixture())
        self.assertEqual(result['citation_retarget_occurrences'],8)
        self.assertEqual(result['articles']['pemmican-and-dried-meats']['old_id_citations'],7)
        self.assertEqual(result['articles']['pioneer-travel-rations']['old_id_citations'],1)
    def test_line_ending_normalized_only(self):
        f=fixture()
        for slug in gate.SLUGS:
            f['new'][slug+'_body']=f['new'][slug+'_body'].replace('\n','\r\n')
        self.assertEqual(gate.inspect(f)['citation_retarget_occurrences'],8)
    def test_json_key_order_no_content_change(self):
        f=fixture()
        m=f['new'][gate.SLUGS[0]+'_meta']
        f['new'][gate.SLUGS[0]+'_meta']=dict(reversed(list(m.items())))
        gate.inspect(f)
    def test_trailing_slash_equivalent(self):
        f=fixture();f['new']['hist']['sources'][1]['url']=URL+'/'
        gate.inspect(f)
    def test_shared_matches_even_identical_scope(self):
        f=fixture();f['rc']['food']['sources'][0]['supports']='Read A'
        result=gate.inspect(f)
        self.assertTrue(result['source_collision']['identical_supports'])
        self.assertFalse(result['may_merge'])
    def test_raw_git_blob_hash(self):
        self.assertEqual(gate.blob_hash(b'test'), '30d74d258442c7c65512eafab474568dd706c430')
    def test_duplicate_json_rejected(self):
        with self.assertRaises(gate.Hold):gate.parse(b'{"id":1,"id":2}')
    def test_missing_git_object(self):
        def missing(commit,path):raise gate.Hold('GIT_OBJECT_UNAVAILABLE')
        with self.assertRaises(gate.Hold):gate.audit(missing)
    def test_mismatched_git_blob(self):
        with self.assertRaisesRegex(gate.Hold,'GIT_BLOB_IDENTITY_CHANGED'):
            gate.audit(lambda commit,path:b'\x00')
    def test_invalid_uri(self):
        with self.assertRaises(gate.Hold):gate.normalized_url('ftp://x.test/path')
    def test_git_object_inventory(self):
        self.assertEqual(len(gate.PINS),16)
        self.assertEqual(set(gate.REPO_COMMITS),{'old','new','rc'})
    def test_unique_source_ids(self):
        with self.assertRaisesRegex(gate.Hold,'DUPLICATE_SOURCE_ID'):
            gate.source_map({'sources':[entry('x'),entry('x')]})
    def test_missing_author_scope(self):
        f=fixture();f['new'][gate.SLUGS[0]+'_meta']['source_use']={}
        with self.assertRaises(gate.Hold):gate.inspect(f)

# Each case makes one independent negative regression test. Deliberately mutate
# sources, article content and governance separately; no shared fixture writes.
MUTATIONS={
 'missing_cluster':lambda f:f.pop('new'),
 'unknown_cluster':lambda f:f.setdefault('spurious',{}),
 'missing_rc_food':lambda f:f['rc'].pop('food'),
 'unexpected_rc_key':lambda f:f['rc'].update(other='str'),
 'missing_old_article':lambda f:f['old'].pop(gate.SLUGS[0]+'_body'),
 'missing_new_metadata':lambda f:f['new'].pop(gate.SLUGS[1]+'_meta'),
 'old_hist_not_frozen':lambda f:f['rc']['hist']['sources'][1].update(notes='edited'),
 'old_id_deleted':lambda f:f['old']['hist']['sources'].pop(),
 'old_id_replaced_with_new':lambda f:f['old']['hist']['sources'][1].update(id=gate.NEW),
 'new_id_still_old':lambda f:f['new']['hist']['sources'][1].update(id=gate.OLD),
 'new_id_deleted':lambda f:f['new']['hist']['sources'].pop(),
 'food_shared_source_deleted':lambda f:f['rc']['food']['sources'].pop(),
 'new_source_url_other':lambda f:f['new']['hist']['sources'][1].update(url='https://elsewhere.org/different'),
 'food_source_url_other':lambda f:f['rc']['food']['sources'][0].update(url='https://elsewhere.org/different'),
 'old_source_http':lambda f:f['old']['hist']['sources'][1].update(url='http://nchfp.uga.edu/how/dry/recipes/jerky'),
 'new_source_ftp':lambda f:f['new']['hist']['sources'][1].update(url='ftp://nchfp.uga.edu/how/dry/recipes/jerky'),
 'food_source_userinfo':lambda f:f['rc']['food']['sources'][0].update(url='https://alice@nhcfp.uga.edu/how/dry/recipes/jerky'),
 'new_source_query':lambda f:f['new']['hist']['sources'][1].update(url=URL+'?ref=ad'),
 'new_source_fragment':lambda f:f['new']['hist']['sources'][1].update(url=URL+'#section'),
 'hist_supports_drift':lambda f:f['new']['hist']['sources'][1].update(supports='Different scientific claim'),
 'new_verified_date_changed':lambda f:f['new']['hist']['sources'][1].update(verified_on='2026-11-04'),
 'new_approval_forged':lambda f:f['new']['hist']['sources'][1].update(human_link_check=True),
 'food_approval_forged':lambda f:f['rc']['food']['sources'][0].update(human_link_check=True),
 'old_approval_forged':lambda f:f['old']['hist']['sources'][1].update(human_link_check=True),
 'food_unverified':lambda f:f['rc']['food']['sources'][0].update(verified_on=None),
 'new_id_double_in_fragment':lambda f:f['new']['hist']['sources'].append(entry(gate.NEW)),
 'unrelated_source_modified':lambda f:f['new']['hist']['sources'][0].update(notes='new opinion'),
 'missing_supports':lambda f:f['new']['hist']['sources'][1].update(supports=''),
 'missing_notes':lambda f:f['rc']['food']['sources'][0].update(notes=''),
 'invalid_source_row':lambda f:f['rc']['food']['sources'].append('bad record'),
 'old_pemmican_citations_removed':lambda f:f['old'][gate.SLUGS[0]+'_body'].replace('{{cite:'+gate.OLD+'}}','',1) and f['old'].__setitem__(gate.SLUGS[0]+'_body',f['old'][gate.SLUGS[0]+'_body'].replace('{{cite:'+gate.OLD+'}}','',1)),
 'new_pemmican_citation_removed':lambda f:f['new'].__setitem__(gate.SLUGS[0]+'_body',f['new'][gate.SLUGS[0]+'_body'].replace('{{cite:'+gate.NEW+'}}','',1)),
 'new_extra_content':lambda f:f['new'].__setitem__(gate.SLUGS[0]+'_body',f['new'][gate.SLUGS[0]+'_body']+'<p>new advice</p>'),
 'new_warning_deleted':lambda f:f['new'].__setitem__(gate.SLUGS[1]+'_body',f['new'][gate.SLUGS[1]+'_body'].replace('<h2>Reader</h2>','')),
 'new_invalid_cite':lambda f:f['new'].__setitem__(gate.SLUGS[0]+'_body',f['new'][gate.SLUGS[0]+'_body'].replace('{{cite:'+gate.NEW+'}}','{{cite: BAD }}',1)),
 'rc_body_not_frozen':lambda f:f['rc'].__setitem__(gate.SLUGS[0]+'_body',f['rc'][gate.SLUGS[0]+'_body']+'a'),
 'old_slug_changed':lambda f:f['old'][gate.SLUGS[0]+'_meta'].update(slug='other'),
 'new_slug_changed':lambda f:f['new'][gate.SLUGS[0]+'_meta'].update(slug='other'),
 'rc_slug_changed':lambda f:f['rc'][gate.SLUGS[0]+'_meta'].update(slug='other'),
 'new_publish_approved':lambda f:f['new'][gate.SLUGS[0]+'_meta']['status'].update(publish='published'),
 'rc_publish_approved':lambda f:f['rc'][gate.SLUGS[1]+'_meta']['status'].update(publish='published'),
 'new_safety_approved':lambda f:f['new'][gate.SLUGS[0]+'_meta']['safety_review'].update(state='approved'),
 'rc_safety_approved':lambda f:f['rc'][gate.SLUGS[1]+'_meta']['safety_review'].update(state='approved'),
 'new_author_explanation_changed':lambda f:f['new'][gate.SLUGS[0]+'_meta']['source_use'].update({gate.NEW:'different interpretation'}),
 'rc_author_explanation_changed':lambda f:f['rc'][gate.SLUGS[0]+'_meta']['source_use'].update({gate.OLD:'different'}),
 'new_author_note_missing':lambda f:f['new'][gate.SLUGS[0]+'_meta']['source_use'].pop('safe-other'),
 'new_author_note_blank':lambda f:f['new'][gate.SLUGS[0]+'_meta']['source_use'].update({gate.NEW:'   '}),
 'new_author_extra':lambda f:f['new'][gate.SLUGS[0]+'_meta']['source_use'].update({'unexpected':'note'}),
 'new_safety_scope_changed':lambda f:f['new'][gate.SLUGS[0]+'_meta']['safety_review'].update(scope='new content'),
 'new_related_changed':lambda f:f['new'][gate.SLUGS[0]+'_meta'].update(related=['other']),
 'old_metadata_publish_non_draft':lambda f:f['old'][gate.SLUGS[0]+'_meta']['status'].update(publish='published'),
 'new_body_uncited_id':lambda f:f['new'].__setitem__(gate.SLUGS[1]+'_body',f['new'][gate.SLUGS[1]+'_body']+'{{cite:missing}}'),
 'new_body_old_id_still_present':lambda f:f['new'].__setitem__(gate.SLUGS[1]+'_body',f['new'][gate.SLUGS[1]+'_body']+'{{cite:'+gate.OLD+'}}'),
}

def create_negative_test(name,mutation):
    def run(self):
        f=fixture()
        mutation(f)
        with self.assertRaises(gate.Hold, msg=name):
            gate.inspect(f)
    run.__name__='test_reject_'+name
    return run
for name,mutation in MUTATIONS.items():
    setattr(Baselines,'test_reject_'+name,create_negative_test(name,mutation))

if __name__=='__main__':unittest.main()
