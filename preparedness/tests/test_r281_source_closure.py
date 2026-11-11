"""R281 source-closure regression: adversarial fixtures entirely in tempdirs."""
import json
import tempfile
import unittest
from pathlib import Path
from test_r279_live_slate_gate import g, manifest_and_tree


class SourceClosure(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.manifest=manifest_and_tree(self.root)
        self.evidence=self.root/g.EVIDENCE_LOCK
        self.evidence.write_bytes(b'UNAPPROVED EXAMPLE SOURCE LOCK')
        data=self.evidence.read_bytes()
        self.pin=(g.blob(data),len(data))

    def check(self):
        return g.check_source_closure(self.root,self.manifest,self.pin)

    def reject(self, pattern):
        with self.assertRaisesRegex((OSError,ValueError),pattern):
            self.check()

    def test_synthetic_source_scope_held(self):
        self.assertEqual(self.check(),{'source_data_files':10,'additional_pinned_source_files':1})
    def test_historical_census_exact(self):
        origins={r['path'] for r in self.manifest['entries'] if r['role']=='source_origin'}
        self.assertEqual(origins,g.SOURCE_ORIGINS)
        self.assertIn('sources/register.json', origins)
    def test_notes_allowed_in_source_root(self):
        (self.root/'sources/readme.md').write_text('internal');self.check()
    def test_notes_allowed_in_fragments(self):
        (self.root/'sources/fragments/readme.txt').write_text('internal');self.check()
    def test_lock_modified_blocks(self):
        self.evidence.write_text('ALTERED');self.reject('evidence lock modified')
    def test_lock_missing_blocks(self):
        self.evidence.unlink();self.reject('No such file')
    def test_lock_symlink_blocks(self):
        self.evidence.unlink();self.evidence.symlink_to(self.root/'sources/register.json');self.reject('symlink')
    def test_source_directory_symlink_blocks(self):
        p=self.root/'sources/alias';p.symlink_to(self.root/'sources/fragments',target_is_directory=True);self.reject('symlink')
    def test_hidden_symlink_blocks(self):
        p=self.root/'sources/.shadow';p.symlink_to(self.root/'sources/register.json');self.reject('symlink')
    def test_wrong_extra_sha_blocks(self):
        with self.assertRaisesRegex(ValueError,'evidence lock modified'):
            g.check_source_closure(self.root,self.manifest,('a'*40,self.pin[1]))
    def test_wrong_extra_size_blocks(self):
        with self.assertRaisesRegex(ValueError,'evidence lock modified'):
            g.check_source_closure(self.root,self.manifest,(self.pin[0],self.pin[1]+1))
    def test_invalid_pin_blocks(self):
        with self.assertRaisesRegex(ValueError,'pin invalid'):
            g.check_source_closure(self.root,self.manifest,('BAD',True))
    def test_source_register_is_manifest_protected(self):
        rows={r['path']:r for r in self.manifest['entries']}
        self.assertEqual(rows['sources/register.json']['role'],'source_origin')
    def test_existing_register_tamper_fails_inherited_gate(self):
        (self.root/'sources/register.json').write_text('CHANGED')
        with self.assertRaisesRegex(ValueError,'source bytes changed'):
            g.check_tree(self.root,self.manifest)
    def test_source_origin_path_moved_fails(self):
        for row in self.manifest['entries']:
            if row['role']=='source_origin':row['path']='sources/fragments/unknown.json';break
        with self.assertRaisesRegex(ValueError,'source origin path'):
            g.check_manifest(self.manifest)
    def test_unauthorized_state_never_set(self):
        result=g.audit(self.root)
        self.assertEqual(result['state'],g.INVALID)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])


ADDED_SOURCE_FILES = [
'sources/hidden.json','sources/HIDDEN.JSON','sources/.hidden.json','sources/additional.yaml',
'sources/additional.YAML','sources/additional.yml','sources/additional.csv','sources/additional.tsv',
'sources/additional.jsonl','sources/nested/evidence.json','sources/nested/second/fragment.json',
'sources/REGISTER.JSON','sources/crosswalk.JSON','sources/article-evidence-lock.JSON',
'sources/fragments/extra.json','sources/fragments/EXTRA.JSON',
'sources/fragments/extra.yml','sources/fragments/extra.YML',
'sources/fragments/nested/extra.csv','sources/fragments/nested/extra.tsv',
'sources/fragments/nested/extra.JSON','sources/fragments/.hidden.json',
'sources/fragments/history/alternate.json','sources/fragments/history/alternate.yaml',
'sources/overrides/REGISTER.JSON','sources/overrides/override.jsonl',
'sources/evidence/data.tsv','sources/fragments/start.JSON','sources/fragments/hist-field.JSON',
'sources/generated/new.json','sources/review/rev.json','sources/review/rev.jsonl',
'sources/shadow/register.csv','sources/fake/source.yml','sources/injected/sub/nested.CSV']

for i,rel in enumerate(ADDED_SOURCE_FILES):
    def test(self,path=rel):
        p=self.root/path
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('{}')
        self.reject('unregistered source data')
    setattr(SourceClosure, 'test_reject_extra_source_%02d' % (i+1), test)

if __name__=='__main__': unittest.main(verbosity=2)
