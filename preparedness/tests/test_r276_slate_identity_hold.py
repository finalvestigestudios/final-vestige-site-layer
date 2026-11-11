"""R276 isolated synthetic fidelity/adversarial checks. NOT native complete repo QA."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

mod_path = Path(__file__).resolve().parents[1] / 'tools/r276_slate_identity_hold.py'
spec = importlib.util.spec_from_file_location('r276_hold', mod_path)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixture():
    data, entries = {}, []
    def entry(path, role, raw):
        data[path] = raw if isinstance(raw, bytes) else raw.encode('utf-8')
        entries.append({'path':path,'role':role,'size':len(data[path]),'sha':g.git_blob(data[path])})
    for folder, maxn, startn in [('articles',35,1),('tools',6,101)]:
        for i in range(1,maxn+1):
            slug = 'article-' + str(i) if folder == 'articles' else 'tool-' + str(i)
            entry('content/'+folder+'/'+slug+'.body.html', folder[:-1]+'_body' if False else ('article_body' if folder=='articles' else 'tool_body'), f'<p>{slug} readable original long-form content</p>')
            entry('content/'+folder+'/'+slug+'.meta.json', 'article_meta' if folder=='articles' else 'tool_meta',
                  json.dumps({'slug':slug,'n':startn+i-1,'status':{'publish':'draft','editorial':'drafted'},'safety_review':{'state':'pending'}}))
    # The historical Article 1..35 roster must contain water-planner as a tool in the crosswalk.
    for e in entries:
        if e['path']=='content/tools/tool-6.body.html':
            data.pop(e['path']);e['path']='content/tools/water-planner.body.html';data[e['path']]=b'<p>long original tool</p>';e['size']=len(data[e['path']]);e['sha']=g.git_blob(data[e['path']])
        if e['path']=='content/tools/tool-6.meta.json':
            data.pop(e['path']);e['path']='content/tools/water-planner.meta.json';data[e['path']]=json.dumps({'slug':'water-planner','n':106,'status':{'publish':'draft'}}).encode();e['size']=len(data[e['path']]);e['sha']=g.git_blob(data[e['path']])
    entry(g.EXTRA['hub_body'],'hub_body', '<h1>Preparedness review-only hub</h1>')
    for p in sorted(g.ORIGINS):entry(p,'source_origin','{"sources": []}')
    entry(g.EXTRA['crosswalk'],'crosswalk',json.dumps({'article_origins':{**{'article-'+str(i):'base' for i in range(1,36)},'water-planner':'base'}}))
    entry(g.EXTRA['docket'],'docket',json.dumps({'state':g.HOLD,'source_rows':244,'review_alias_groups':32,'duplicate_source_id_groups':15}))
    for role in ('source_gate','docket_gate','export_gate'):entry(g.EXTRA[role],role,'# frozen source-custody gate\n')
    m={'schema':g.SCHEMA,'state':g.HOLD,'snapshot_ref':g.REF,'entries':entries,
       'source_review':{'shared_url_groups':32,'duplicate_id_groups':15,'held_occurrences':3},
       **{k:False for k in ('independent_qd_pass','publication_authorized','medical_safety_verified','privacy_approved','merchant_offer_approved','may_merge')}}
    return m,data

class Suite(unittest.TestCase):
    def test_positive_frozen_manifest(self):
        m,data=fixture(); out=g.inspect(m,lambda p:data[p]); self.assertTrue(out['original_byte_parity']);self.assertEqual((out['article_count'],out['tool_count']),(35,6));self.assertFalse(out['publication_authorized'])
    def test_no_release_without_pinned_manifest(self):
        m,data=fixture();out=g.audit('/dev/null',lambda p: json.dumps(m).encode() if p==g.MANIFEST else data[p]);self.assertEqual(out['state'],g.INVALID);self.assertFalse(out['independent_qd_pass'])
    def test_missing_source_fails(self):
        m,data=fixture();del data[m['entries'][0]['path']];self.assertRaises(KeyError,g.inspect,m,lambda p:data[p])
    def test_duplicate_json_keys_fails(self):
        self.assertRaisesRegex(ValueError,'duplicate JSON',g.strict_json,b'{"a":1,"a":2}')
    def test_nan_fails(self):self.assertRaises(ValueError,g.strict_json,b'{"a":NaN}')
    def test_git_blob(self):self.assertEqual(g.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_original_tool_numbers_can_repeat(self):
        m,data=fixture()
        p='content/tools/tool-2.meta.json'
        content=json.loads(data[p]);content['n']=101
        data[p]=json.dumps(content).encode()
        e=next(e for e in m['entries'] if e['path']==p)
        e['sha']=g.git_blob(data[p]);e['size']=len(data[p])
        self.assertTrue(g.inspect(m,lambda k:data[k])['original_byte_parity'])

    def test_duplicate_article_number_fails(self):
        m,data=fixture()
        p='content/articles/article-2.meta.json'
        content=json.loads(data[p]);content['n']=1
        data[p]=json.dumps(content).encode()
        e=next(e for e in m['entries'] if e['path']==p)
        e['sha']=g.git_blob(data[p]);e['size']=len(data[p])
        with self.assertRaisesRegex(ValueError,'duplicate article number'):
            g.inspect(m,lambda k:data[k])


MUTATIONS={
  'schema':lambda m,d:m.update(schema='INVALID'),
  'state':lambda m,d:m.update(state='APPROVED'),
  'ref':lambda m,d:m.update(snapshot_ref='main'),
  'no_review':lambda m,d:m.pop('source_review'),
  'review_group_count':lambda m,d:m['source_review'].update(shared_url_groups=31),
  'review_id_count':lambda m,d:m['source_review'].update(duplicate_id_groups=14),
  'review_held_occurrences':lambda m,d:m['source_review'].update(held_occurrences=0),
  'false_qd':lambda m,d:m.update(independent_qd_pass=True),
  'false_publish':lambda m,d:m.update(publication_authorized=True),
  'false_medical':lambda m,d:m.update(medical_safety_verified=True),
  'false_privacy':lambda m,d:m.update(privacy_approved=True),
  'false_merchant':lambda m,d:m.update(merchant_offer_approved=True),
  'false_merge':lambda m,d:m.update(may_merge=True),
  'removed_qd_flag':lambda m,d:m.pop('independent_qd_pass'),
  'missing_article':lambda m,d:m['entries'].pop(0),
  'duplicated_article':lambda m,d:m['entries'].append(copy.deepcopy(m['entries'][0])),
  'wrong_role':lambda m,d:m['entries'][0].update(role='source_origin'),
  'wrong_suffix':lambda m,d:m['entries'][0].update(path='content/articles/article-1.txt'),
  'traversal':lambda m,d:m['entries'][0].update(path='../content/articles/article-1.body.html'),
  'backslash':lambda m,d:m['entries'][0].update(path='content\\articles\\article-1.body.html'),
  'absolute':lambda m,d:m['entries'][0].update(path='/content/articles/article-1.body.html'),
  'duplicate_path':lambda m,d:m['entries'][1].update(path=m['entries'][0]['path']),
  'changed_sha':lambda m,d:m['entries'][0].update(sha='0'*40),
  'short_sha':lambda m,d:m['entries'][0].update(sha='0'*39),
  'nonhex_sha':lambda m,d:m['entries'][0].update(sha='z'*40),
  'tampered_size':lambda m,d:m['entries'][0].update(size=m['entries'][0]['size']-1),
  'bool_size':lambda m,d:m['entries'][0].update(size=True),
  'extra_field':lambda m,d:m['entries'][0].update(approved=True),
  'alter_body':lambda m,d:d.__setitem__(m['entries'][0]['path'],b'<p>shortened</p>'),
  'alter_meta_publish':lambda m,d:d.__setitem__('content/articles/article-1.meta.json',json.dumps({'slug':'article-1','n':1,'status':{'publish':'published'}}).encode()),
  'alias_meta_slug':lambda m,d:d.__setitem__('content/articles/article-1.meta.json',json.dumps({'slug':'article-2','n':1,'status':{'publish':'draft'}}).encode()),
  'source_origin_swap':lambda m,d:m['entries'][-8].update(path='sources/other.json'),
  'crosswalk_missing_article':lambda m,d:d.__setitem__(g.EXTRA['crosswalk'],json.dumps({'article_origins':{'water-planner':'base'}}).encode()),
  'crosswalk_fake_article':lambda m,d:d.__setitem__(g.EXTRA['crosswalk'],json.dumps({'article_origins':{**{'article-'+str(i):'base' for i in range(1,35)},'invented':'base','water-planner':'base'}}).encode()),
  'docket_approved':lambda m,d:d.__setitem__(g.EXTRA['docket'],json.dumps({'state':'APPROVED','source_rows':244,'review_alias_groups':32,'duplicate_source_id_groups':15}).encode()),
  'docket_lost_row':lambda m,d:d.__setitem__(g.EXTRA['docket'],json.dumps({'state':g.HOLD,'source_rows':243,'review_alias_groups':32,'duplicate_source_id_groups':15}).encode()),
  'docket_groups_lost':lambda m,d:d.__setitem__(g.EXTRA['docket'],json.dumps({'state':g.HOLD,'source_rows':244,'review_alias_groups':31,'duplicate_source_id_groups':15}).encode()),
}
# All mutators must fail, including ones rejected at the earlier blob-identity layer.
for label,change in MUTATIONS.items():
    def test(self, fn=change):
        m,d=fixture();fn(m,d)
        with self.assertRaises((ValueError,KeyError,TypeError,AttributeError)):
            g.inspect(m,lambda p:d[p])
    setattr(Suite,'test_adversarial_'+label,test)

if __name__=='__main__':unittest.main()
