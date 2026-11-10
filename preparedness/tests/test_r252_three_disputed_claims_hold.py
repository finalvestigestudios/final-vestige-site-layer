"""R252 source/claim-hold tests are synthetic, not a native 35-article run."""
import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('r252',ROOT/'tools/r252_three_disputed_claims_hold.py')
r252=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r252)
DOCKET=r252.strict_json((ROOT/'audits/r252_three_disputed_claims_hard_hold.json').read_bytes())
A7=(b'<li><strong>Look for other clean water in the house</strong> via heaters and ice.{{cite:cdc-find-clean-water}}</li>\n'
    b'<li><strong>Stop and ask what might be upstream.</strong> Fuel, chemicals or waste.{{cite:cdc-find-clean-water}}</li>')
A20=(b'<li>Ready.gov asks you to consider languages spoken in the household,{{cite:start-ready-plan}} via preparedness.</li>')
VALID={r252.START:A7,r252.HOUSE:A20}
SHAS={k:(r252.git_blob(v),) for k,v in VALID.items()}


def audit(blobs=None,docket=None,oids=None):
    return r252.audit_bytes(blobs if blobs is not None else VALID,
                            docket if docket is not None else DOCKET,
                            allowed_oids=oids if oids is not None else SHAS)


class TestHold(unittest.TestCase):
    def test_bounded_review_receipt(self):
        a=audit()
        self.assertEqual(a['observed_count'],3)
        self.assertEqual(a['shared_source_groups_still_unreviewed'],32)
        self.assertFalse(a['publication_authorized'])
        self.assertFalse(a['ready_gov_page_verified'])
        self.assertEqual(a,audit())

    def test_identifiers_and_sources(self):
        a=audit()['occurrences']
        self.assertEqual([x['n'] for x in a],[7,7,20])
        self.assertEqual([x['occurrence'] for x in a],[1,2,1])
        self.assertNotEqual(a[0]['claim_fragment_sha256'],a[1]['claim_fragment_sha256'])

    def test_json_duplicate_keys_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):
            r252.strict_json(b'{"a":1,"a":2}')

    def test_json_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,'nonfinite'):
            r252.strict_json(b'{"x":NaN}')

    def test_paths_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            (root/'test').write_bytes(b'x')
            for p in ['/etc/passwd','../escape','./test','test/..','test\\x','', 'missing']:
                with self.subTest(path=p), self.assertRaises(ValueError):
                    r252.safe_read(root,p)
            (root/'sym').symlink_to(root/'test')
            with self.assertRaises(ValueError):r252.safe_read(root,'sym')

    def test_wrong_input_type_rejected(self):
        for v in (None,False,1,[],{},'wrong'):
            with self.subTest(v=v),self.assertRaises(ValueError):
                audit({r252.START:v,r252.HOUSE:A20})

    def test_missing_extra_input_rejected(self):
        with self.assertRaises(ValueError):audit({r252.START:A7})
        with self.assertRaises(ValueError):audit({**VALID,'extra':b''})

    def test_wrong_sha_rejected(self):
        for slug in VALID:
            with self.subTest(slug=slug),self.assertRaisesRegex(ValueError,'blob drift'):
                a=VALID.copy();a[slug]+=b' '
                audit(a)

    def test_duplicate_marker_rejected_with_own_oid(self):
        a={**VALID,r252.START:A7+A7}
        sh={**SHAS,r252.START:(r252.git_blob(a[r252.START]),)}
        with self.assertRaisesRegex(ValueError,'count differs'):audit(a,oids=sh)

    def test_missing_marker_rejected_with_own_oid(self):
        a={**VALID,r252.HOUSE:A20.replace(b'{{cite:start-ready-plan}}',b'')}
        sh={**SHAS,r252.HOUSE:(r252.git_blob(a[r252.HOUSE]),)}
        with self.assertRaisesRegex(ValueError,'count differs'):audit(a,oids=sh)

    def test_relocated_context_rejected_with_own_oid(self):
        a={**VALID,r252.START:A7.replace(b'Look for other clean water in the house',b'Look somewhere')}
        sh={**SHAS,r252.START:(r252.git_blob(a[r252.START]),)}
        with self.assertRaisesRegex(ValueError,'displaced'):audit(a,oids=sh)

    def test_docket_row_order_rejected(self):
        x=copy.deepcopy(DOCKET);x['occurrences'].reverse()
        with self.assertRaises(ValueError):audit(docket=x)


def mutant(name,make):
    def check(self):
        d=make(copy.deepcopy(DOCKET))
        with self.assertRaisesRegex(ValueError,'R252 HARD HOLD'):
            audit(docket=d)
    setattr(TestHold,'test_mutant_'+name,check)


def tweak(field,value):
    def f(d):d[field]=value;return d
    return f

for flag in r252.FALSE_FLAGS:
    for kind,val in [('true',True),('none',None),('string','false')]:
        mutant(flag+'_'+kind,tweak(flag,val))
for key,val in [('issue',900),('conversion_issue',900),('state','PASS'),('schema','v0'),
                ('ready_gov_access','VERIFIED'),('historical_shared_source_groups_still_unreviewed',0)]:
    mutant(key,tweak(key,val))
for i in range(3):
    for fld,new in [('citation_id','bad'),('source_url','https://example.org'),
                    ('n',99),('occurrence',99),('claim_verdict','APPROVED'),
                    ('source_scope_verdict','VERIFIED'),('human_review_required',False),
                    ('lead_in','Missing'),('review_topic','Override')]:
        def f(d,i=i,fld=fld,new=new):d['occurrences'][i][fld]=new;return d
        mutant('row_'+str(i)+'_'+fld,f)
for k in (0,1,2):
    def f(d,k=k):d['occurrences'].pop(k);return d
    mutant('removed_row_'+str(k),f)

if __name__=='__main__':unittest.main()
