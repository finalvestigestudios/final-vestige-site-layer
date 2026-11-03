"""R22 native-gate tests: synthetic frozen source custody, not human verification."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

TESTS=Path(__file__).resolve().parent
TOOLS=TESTS.parent/'tools'
sys.path.insert(0,str(TESTS))
sys.path.insert(0,str(TOOLS))
import source_group_review_gate as gate
from test_source_group_review_gate import fixture


def arrange(tmp):
    crosswalk,taxonomy,sources=fixture()
    crosswalk['source_head_commits']=dict(gate.FROZEN_HEADS)
    crosswalk['source_head_commits']['food']=gate.FIXTURE_FOOD
    documents={**sources,
      'preparedness/sources/crosswalk.json': gate.canonical(crosswalk),
      'preparedness/taxonomy.json': gate.canonical(taxonomy)}
    pinned={k:gate.git_blob(v) for k,v in documents.items()}
    for key,data in documents.items():
        target=Path(tmp)/key
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    return documents,pinned


class FrozenCustody(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.documents,self.pinned=arrange(self.root)

    def run_gate(self):
        with mock.patch.object(gate,'FROZEN_BLOBS',self.pinned):
            return gate.audit_frozen(self.root)

    def test_original_ten_files_reconciled_as_hold(self):
        r=self.run_gate()
        self.assertEqual(r['release_state'],'HOLD')
        self.assertIs(r['may_publish'],False)
        self.assertIs(r['independent_qd_pass'],False)
        self.assertIs(r['medical_safety_approved'],False)
        self.assertIs(r['human_source_review_complete'],False)
        self.assertEqual(r['source_inputs_pinned'],10)
        self.assertEqual(r['article_slugs'],35)
        self.assertEqual(r['shared_source_groups_pending_human_review'],30)
        self.assertTrue(r['food_provenance_alias_unresolved'])
        self.assertRegex(r['source_review_queue_sha256'],r'^[0-9a-f]{64}$')

    def test_repeat_deterministic(self):
        self.assertEqual(self.run_gate(),self.run_gate())

    def test_original_food_author_head_does_not_clear_safety(self):
        self.rewrite_crosswalk(lambda c:c['source_head_commits'].__setitem__('food',gate.AUTHOR_FOOD),repin=True)
        r=self.run_gate()
        self.assertFalse(r['food_provenance_alias_unresolved'])
        self.assertFalse(r['may_publish'])

    def rewrite_crosswalk(self,fn,repin=False):
        name='preparedness/sources/crosswalk.json'
        file=self.root/name
        data=json.loads(file.read_bytes());fn(data)
        raw=gate.canonical(data);file.write_bytes(raw)
        if repin:self.pinned[name]=gate.git_blob(raw)

    def rewrite_taxonomy(self,fn,repin=False):
        name='preparedness/taxonomy.json'
        file=self.root/name
        data=json.loads(file.read_bytes());fn(data)
        raw=gate.canonical(data);file.write_bytes(raw)
        if repin:self.pinned[name]=gate.git_blob(raw)

    def hold(self):
        with self.assertRaises((gate.SourceGateHold,ValueError,TypeError,UnicodeError,KeyError)):
            self.run_gate()

    def test_change_article_origin_is_not_structurally_detected_without_lock(self):
        # Document why the independent frozen Git blob is an essential boundary.
        self.rewrite_crosswalk(lambda c:c['article_origins'].__setitem__('article-00','food'))
        self.hold()

    def test_turn_off_slate_gate_is_frozen(self):
        self.rewrite_taxonomy(lambda t:t['slate'][0].update(gate=False))
        self.hold()

    def test_edit_existing_reading_note_is_frozen(self):
        self.rewrite_crosswalk(lambda c:c['groups'][0]['variants'][0]['source'].__setitem__('supports','All reviewed'))
        self.hold()

    def test_repin_and_edit_source_url_still_rejected_by_original_crosswalk(self):
        k='preparedness/sources/fragments/start.json'
        f=self.root/k
        doc=json.loads(f.read_bytes())
        doc['sources'][0]['url']='https://evil.invalid/publisher-substitution'
        raw=gate.canonical(doc)
        f.write_bytes(raw);self.pinned[k]=gate.git_blob(raw)
        self.hold()

    def test_duplicate_json_key_even_with_repin_fails(self):
        k='preparedness/taxonomy.json'
        raw=self.documents[k].replace(b'"base_path":',b'"base_path":"/other/","base_path":',1)
        (self.root/k).write_bytes(raw);self.pinned[k]=gate.git_blob(raw)
        self.hold()

    def test_nonfinite_json_even_with_repin_fails(self):
        k='preparedness/taxonomy.json'
        raw=self.documents[k].replace(b'"base_path":',b'"extra":NaN,"base_path":',1)
        (self.root/k).write_bytes(raw);self.pinned[k]=gate.git_blob(raw)
        self.hold()

    def test_missing_preparedness_root_fails(self):
        with mock.patch.object(gate,'FROZEN_BLOBS',self.pinned):
            with self.assertRaises(gate.SourceGateHold):
                gate.audit_frozen(self.root/'does-not-exist')

    def test_symlink_source_is_rejected(self):
        key='preparedness/taxonomy.json'
        original=self.root/key;replacement=self.root/'copy.json'
        replacement.write_bytes(original.read_bytes())
        original.unlink();original.symlink_to(replacement)
        self.hold()

    def test_missing_source_file_fails(self):
        (self.root/'preparedness/sources/fragments/food.json').unlink()
        self.hold()

    def test_oversized_source_fails(self):
        key='preparedness/sources/crosswalk.json'
        (self.root/key).write_bytes(b'x'*500_001)
        self.hold()

    def test_false_crosswalk_review_even_when_repin_fails(self):
        self.rewrite_crosswalk(lambda c:c.update(status='HUMAN_VERIFIED'),repin=True)
        self.hold()

    def test_missing_group_even_when_repin_fails(self):
        self.rewrite_crosswalk(lambda c:c['groups'].pop(),repin=True)
        self.hold()

    def test_safety_claim_on_group_even_when_repin_fails(self):
        self.rewrite_crosswalk(lambda c:c['groups'][0].update(reviewer='fake human'),repin=True)
        self.hold()


def attach(name,fn):
    def test(self):
        fn(self)
        self.hold()
    setattr(FrozenCustody,'test_mutation_'+name,test)

for origin in gate.FROZEN_BLOBS:
    key=origin
    attach('frozen_blob_'+key.split('/')[-1].replace('.','_').replace('-','_'),
           lambda s,key=key: (s.root/key).write_bytes(s.documents[key]+b' '))
for name in (k for k in gate.FROZEN_HEADS if k!='food'):
    attach('head_relabel_'+name.replace('-','_'),
           lambda s,name=name: s.rewrite_crosswalk(lambda c:c['source_head_commits'].__setitem__(name,'f'*40),repin=True))
for name,fn in {
    'drop_article':lambda c:c['article_origins'].pop('article-00'),
    'insert_article':lambda c:c['article_origins'].update({'bogus-article':'start'}),
    'wrong_food_head':lambda c:c['source_head_commits'].__setitem__('food','a'*40),
    'remove_head_map':lambda c:c.pop('source_head_commits'),
    'change_variant_note':lambda c:c['groups'][0]['variants'][0]['source'].__setitem__('notes','human checked'),
    'wrong_group_url':lambda c:c['groups'][0].__setitem__('canonical_url','https://evil.invalid'),
    'remove_group_variant':lambda c:c['groups'][0]['variants'].pop(),
}.items():
    attach('crosswalk_'+name,lambda s,fn=fn:s.rewrite_crosswalk(fn,repin=(name not in ('drop_article','insert_article'))))
for name,fn in {
    'remove_water_planner':lambda t:t.update(tools=[]),
    'disable_water_gate':lambda t:t['tools'][0].__setitem__('gate',False),
    'duplicate_slug':lambda t:t['slate'][0].__setitem__('slug',t['slate'][1]['slug']),
    'delete_slate_item':lambda t:t['slate'].pop(),
}.items():
    attach('taxonomy_'+name,lambda s,fn=fn:s.rewrite_taxonomy(fn,repin=True))

class NativeExactCheckout(unittest.TestCase):
    def test_complete_checked_out_source_blobs_remain_frozen(self):
        # R18's native unittest stage automatically runs this once a trusted
        # full checkout is available. Partial reconstructions cannot claim a
        # real-source result; they explicitly skip rather than fabricate one.
        root=TESTS.parents[1]
        if not (root/'.git').exists():
            self.skipTest('not a complete Git checkout; R22 real-corpus check not executed')
        receipt=gate.audit_frozen(root,counts=gate.INTEGRATED_COUNTS,tools=gate.INTEGRATED_TOOLS)
        self.assertEqual(receipt['release_state'],'HOLD')
        self.assertIs(receipt['may_publish'],False)
        self.assertEqual(receipt['shared_source_groups_pending_human_review'],32)


if __name__=='__main__':unittest.main()
