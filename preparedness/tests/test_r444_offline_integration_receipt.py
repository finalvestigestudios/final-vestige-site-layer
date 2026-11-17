"""R444 synthetic only: 60+ discoverable regression tests; no source/QD/sales claims."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/'tools'/'r444_offline_integration_receipt.py'
spec=importlib.util.spec_from_file_location('r444',SRC)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixture(root):
    rows=[]
    for r in range(434,444):
        path=f'preparedness/tools/r{r}_synthetic.py'
        dest=root/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        data=f'# synthetic R{r}\n'.encode()
        dest.write_bytes(data)
        rows.append({'path':path,'revision':r,'role':'source',
                     'sha256':g.sha256(data),'git_blob':g.blob_sha(data),
                     'bytes':len(data)})
    return {'schema':1,'repo':'finalvestigestudios/final-vestige-site-layer',
            'issue':136,'conversion_issue':820,'release_state':'DRAFT_HARD_HOLD',
            'publication_approved':False,'qd_pass':False,'paid_offer_verified':False,
            'net_revenue_verified':False,'native_build_verified':False,
            'authentic_exports_verified':False,'original_articles':35,'source_ids':203,
            'source_occurrences':280,'shared_url_groups':17,
            'source_disputes_unresolved':5,'forks_unselected':9,'records':rows,
            'test_receipts':[{'scope':'focused','run_count':229,'failure_count':0,
                              'error_count':0,'claimed_pass':True}]}


class Contract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.m=fixture(self.root)

    def errors(self):
        return g.audit(self.m,self.root)['errors']

    def test_clean_synthetic_still_hold(self):
        x=g.audit(self.m,self.root)
        self.assertEqual([],x['errors'])
        self.assertEqual(10,x['evidence_files_read'])
        self.assertTrue(x['r444_structural_check_only'])
        self.assertEqual('DRAFT_HARD_HOLD',x['release_state'])
        for k in ('publication_approved','qd_pass','commerce_approved','realized_revenue_verified'):
            self.assertFalse(x[k])

    def test_cli_always_exit_2(self):
        path=self.root/'manifest.json'
        path.write_text(json.dumps(self.m))
        p=subprocess.run([sys.executable,'-I',str(SRC),str(path),'--root',str(self.root)],
                         capture_output=True,text=True)
        self.assertEqual(2,p.returncode)
        self.assertFalse(json.loads(p.stdout)['qd_pass'])

    def test_missing_root_is_not_validated(self):
        self.assertIn('LOCAL_EXECUTED_FILES_NOT_SUPPLIED',g.audit(self.m)['errors'])

    def test_symlink_cannot_provide_evidence(self):
        p=self.root/self.m['records'][0]['path']
        p.unlink()
        p.symlink_to(self.root/self.m['records'][1]['path'])
        self.assertTrue(any(x.startswith('MISSING_OR_UNSAFE_EVIDENCE_FILE:') for x in self.errors()))

    def test_mutated_exact_bytes_rejected(self):
        (self.root/self.m['records'][0]['path']).write_text('tampered')
        self.assertTrue(any(x.startswith('BYTES_OR_HASH_DRIFT:') for x in self.errors()))

    def test_historical_failure_record_not_green(self):
        self.m['test_receipts'][0].update(scope='historical-conflict',
                                          run_count=495,failure_count=43,error_count=5,
                                          claimed_pass=False)
        self.assertEqual([],self.errors())
        self.m['test_receipts'][0]['claimed_pass']=True
        self.assertIn('FALSE_PASS_CLAIM:0',self.errors())

    def test_combined_pass_needs_authenticated_inheritance(self):
        self.m['test_receipts'][0]['scope']='combined'
        self.assertIn('UNAUTHENTICATED_CUMULATIVE_PASS:0',self.errors())

    def test_no_original_file_writes(self):
        files={str(p):p.read_bytes() for p in self.root.rglob('*.py')}
        g.audit(self.m,self.root)
        self.assertEqual(files,{str(p):p.read_bytes() for p in self.root.rglob('*.py')})


SCALARS=[
 ('schema',2,'INTEGRATION_OWNER_OR_SCHEMA_DRIFT'),
 ('repo','other/repo','INTEGRATION_OWNER_OR_SCHEMA_DRIFT'),
 ('issue',137,'INTEGRATION_OWNER_OR_SCHEMA_DRIFT'),
 ('conversion_issue',819,'INTEGRATION_OWNER_OR_SCHEMA_DRIFT'),
 ('release_state','LIVE','RELEASE_OR_QD_STATE_NOT_HARD_HOLD'),
 ('publication_approved',True,'RELEASE_OR_QD_STATE_NOT_HARD_HOLD'),
 ('qd_pass',True,'RELEASE_OR_QD_STATE_NOT_HARD_HOLD'),
 ('paid_offer_verified',True,'FALSE_COMMERCIAL_VERIFICATION'),
 ('net_revenue_verified',True,'FALSE_COMMERCIAL_VERIFICATION'),
 ('original_articles',34,'ORIGINAL_SLATE_COUNTS_DRIFT'),
 ('original_articles',36,'ORIGINAL_SLATE_COUNTS_DRIFT'),
 ('source_ids',202,'ORIGINAL_SLATE_COUNTS_DRIFT'),
 ('source_ids',204,'ORIGINAL_SLATE_COUNTS_DRIFT'),
 ('source_occurrences',279,'ORIGINAL_SLATE_COUNTS_DRIFT'),
 ('source_occurrences',281,'ORIGINAL_SLATE_COUNTS_DRIFT'),
 ('shared_url_groups',16,'ORIGINAL_SLATE_COUNTS_DRIFT'),
 ('shared_url_groups',18,'ORIGINAL_SLATE_COUNTS_DRIFT'),
 ('source_disputes_unresolved',4,'UNADJUDICATED_SOURCE_OR_FORK_WAS_SELECTED'),
 ('forks_unselected',8,'UNADJUDICATED_SOURCE_OR_FORK_WAS_SELECTED'),
 ('native_build_verified',True,'UNPROVEN_NATIVE_BUILD_OR_EXPORT_CLAIM'),
 ('authentic_exports_verified',True,'UNPROVEN_NATIVE_BUILD_OR_EXPORT_CLAIM')
]
ROWS=[
 ('path','../escape.py','INVALID_EVIDENCE_PATH:'),
 ('path','preparedness/tools/../x.py','INVALID_EVIDENCE_PATH:'),
 ('path','preparedness/outside/x.py','INVALID_EVIDENCE_PATH:'),
 ('revision',433,'REVISION_OUTSIDE_PINNED_CHAIN:'),
 ('revision',444,'REVISION_OUTSIDE_PINNED_CHAIN:'),
 ('revision','434','REVISION_OUTSIDE_PINNED_CHAIN:'),
 ('role','published','UNDECLARED_EVIDENCE_ROLE:'),
 ('sha256','x'*64,'MISSING_SHA256_PIN:'),
 ('sha256','f'*63,'MISSING_SHA256_PIN:'),
 ('git_blob','x'*40,'MISSING_GIT_BLOB_PIN:'),
 ('git_blob','f'*39,'MISSING_GIT_BLOB_PIN:'),
 ('bytes',0,'INVALID_BYTE_LENGTH:'),
 ('bytes',-1,'INVALID_BYTE_LENGTH:'),
 ('bytes',True,'INVALID_BYTE_LENGTH:'),
 ('bytes',2000001,'INVALID_BYTE_LENGTH:'),
 ('sha256','0'*64,'BYTES_OR_HASH_DRIFT:'),
 ('git_blob','0'*40,'BYTES_OR_HASH_DRIFT:')
]
RECEIPTS=[
 ('scope','live','TEST_SCOPE_UNDECLARED:'),
 ('run_count',0,'TEST_COUNT_INVALID:'),
 ('run_count',-1,'TEST_COUNT_INVALID:'),
 ('failure_count',-1,'FAILURE_COUNT_INVALID:'),
 ('error_count',-1,'FAILURE_COUNT_INVALID:'),
 ('failure_count',1,'FALSE_PASS_CLAIM:'),
 ('error_count',1,'FALSE_PASS_CLAIM:')
]
for prefix,items,field in [('scalar',SCALARS,None),('row',ROWS,'records'),('receipt',RECEIPTS,'test_receipts')]:
    for idx,(key,value,expect) in enumerate(items,1):
        def test(self,key=key,value=value,expect=expect,field=field):
            if field is None:self.m[key]=value
            else:self.m[field][0][key]=value
            self.assertTrue(any(e.startswith(expect) for e in self.errors()),self.errors())
        setattr(Contract,f'test_{prefix}_mutation_{idx:02d}_{key}',test)

if __name__=='__main__':unittest.main()
