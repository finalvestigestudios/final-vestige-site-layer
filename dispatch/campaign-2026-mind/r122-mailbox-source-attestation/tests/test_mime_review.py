import json
import tempfile
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mime_review import audit_sources, blob_sha, eml_fixture, NOTICE

class OfflineInboxTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'issues').mkdir()
        (self.root/'r121-canonical-acceptance').mkdir()
        entries=[]; rows=[]
        for number in range(1,7):
            kind='commercial-review-pending' if number in (3,5) else 'editorial'
            s=f'Issue {number}';p=f'Preview {number}'
            source=self.root/'issues'/f'{number:02d}-test.md'
            source.write_text(f'**Subject:** {s}\n**Preheader:** {p}\nUNSENT DRAFT',encoding='utf-8')
            sha=blob_sha(source.read_bytes())
            entries.append({'number':number,'subject':s,'preheader':p,'kind':kind,'merchant_affiliate_url':None,'publish_state':'hold'})
            rows.append({'issue':number,'path':'dispatch/campaign-2026-mind/issues/'+source.name,
                         'original_blob':sha,'stacked_blob':sha,'original_subject':s,'stacked_subject':s,
                         'original_preheader':p,'stacked_preheader':p})
        self.manifest={'status':'DRAFT_UNSENT_NO_SCHEDULING','issues':entries}
        self.audit={'rows':rows,'master':{'sha':'testsha'},'stacked':{'sha':'testsha'}}
        self.write()
    def write(self):
        (self.root/'manifest.json').write_text(json.dumps(self.manifest),encoding='utf-8')
        (self.root/'r121-canonical-acceptance/audit.json').write_text(json.dumps(self.audit),encoding='utf-8')
    def test_manifest_verified_snapshot(self):
        p=audit_sources(self.root,'stacked');self.assertEqual(len(p['sources']),6)
        self.assertEqual(p['status'],'HOLD_UNSENT')
    def test_independent_git_blob_algorithm(self):
        self.assertEqual(blob_sha(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_source_mutation_fails_closed(self):
        f=self.root/'issues/02-test.md';f.write_text(f.read_text()+'\nchanged',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'not the declared'):audit_sources(self.root)
    def test_manifest_subject_mutation_fails(self):
        self.manifest['issues'][0]['subject']='Wrong';self.write()
        with self.assertRaisesRegex(ValueError,'attested'):audit_sources(self.root)
    def test_invalid_allocation_fails(self):
        self.manifest['issues'][2]['kind']='editorial';self.write()
        with self.assertRaisesRegex(ValueError,'allocation'):audit_sources(self.root)
    def test_live_merchant_url_fails(self):
        self.manifest['issues'][2]['merchant_affiliate_url']='https://example.invalid/affiliate';self.write()
        with self.assertRaisesRegex(ValueError,'active'):audit_sources(self.root)
    def test_publish_state_fails(self):
        self.manifest['issues'][0]['publish_state']='publish';self.write()
        with self.assertRaisesRegex(ValueError,'active'):audit_sources(self.root)
    def test_campaign_scheduling_fails(self):
        self.manifest['status']='SCHEDULED';self.write()
        with self.assertRaisesRegex(ValueError,'unsent'):audit_sources(self.root)
    def test_differentiates_source_snapshots(self):
        self.audit['rows'][0]['original_blob']='0'*40;self.write()
        self.assertEqual(len(audit_sources(self.root,'stacked')['sources']),6)
        with self.assertRaisesRegex(ValueError,'master'):audit_sources(self.root,'master')
    def test_mime_has_both_variants_no_recipient(self):
        b=eml_fixture(1,'Study & report','Evidence body','<html><body>Evidence body</body></html>')
        m=BytesParser(policy=policy.default).parsebytes(b)
        self.assertEqual(m['X-FV-Automated-Sending-Allowed'],'FALSE')
        self.assertIsNone(m['To']);self.assertIsNone(m['Bcc'])
        self.assertIn('[UNSENT FIXTURE]',m['Subject'])
        self.assertEqual([x.get_content_type() for x in m.iter_parts()],['text/plain','text/html'])
        self.assertTrue(all(NOTICE in x.get_content() for x in m.iter_parts()))
    def test_mime_requires_both_body_variants(self):
        with self.assertRaises(ValueError):eml_fixture(2,'Subject',' ', '<html>text</html>')
        with self.assertRaises(ValueError):eml_fixture(2,'Subject','text','plain not html')
    def test_fake_snapshot_rejected(self):
        with self.assertRaisesRegex(ValueError,'explicitly'):audit_sources(self.root,'automatic')

if __name__=='__main__':unittest.main()
