"""R38 private reviewer import: 76+ isolated fail-closed synthetic tests."""
import csv
import hashlib
import io
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import reviewer_csv_export_gate as r37
import reviewer_quarantine_gate as gate


def fixture():
    tables={}
    counts={'articles':1,'tools':0}
    for name,head in r37.TABLES.items():
        row={c:(hashlib.sha256(name.encode()).hexdigest() if c==head[0] else
             'NOT_STARTED' if c=='review_state' else '' if c.startswith('human_') else
             'original contributor reading / source URL / claim context: '+c)
             for c in head}
        tables[name]=r37._render(head,[row]); counts[gate.TABLE_COUNTS[name]]=1
    meta={'schema_version':1,'issue':136,'release_state':'HOLD',
          'machine_authority':r37.AUTHORITY,**{f:False for f in r37.HOLD_FLAGS},
          'parent_R34_original_reading_sha256':'a'*64,
          'parent_R35_fingerprint_sha256':'b'*64,
          'parent_R36_fingerprint_sha256':'c'*64,
          'counts':counts,
          'csv_tables':{n:{'rows':1,'columns':list(r37.TABLES[n]),
                           'sha256_utf8':gate.hash_text(s),
                           'bytes_utf8':len(s.encode('utf-8'))} for n,s in tables.items()}}
    meta['fingerprint_sha256']=r37.sha(meta)
    return {'manifest':meta,'csv_tables':tables}


def mutate_csv(original, field, value, table='claim_review.csv', state=None):
    out=copy.deepcopy(original['csv_tables'])
    inp=csv.DictReader(io.StringIO(out[table],newline=''))
    head=list(inp.fieldnames); rows=list(inp)
    rows[0][field]=value
    if state is not None:rows[0]['review_state']=state
    f=io.StringIO(newline=''); w=csv.DictWriter(f,fieldnames=head,lineterminator='\r\n')
    w.writeheader();w.writerows(rows);out[table]=f.getvalue()
    return out


def rejected(case, tables):
    try:gate.quarantine_reviewer_csv(case,tables)
    except gate.IntakeHold:return
    raise AssertionError('malformed or unsafe reviewer import was accepted')

class Positive(unittest.TestCase):
    def setUp(self):self.b=fixture()
    def test_empty_desk_stays_hold(self):
        p=gate.quarantine_reviewer_csv(self.b,self.b['csv_tables'])
        self.assertEqual(p['manifest']['release_state'],'HOLD')
        self.assertEqual(p['manifest']['unverified_progress_records'],0)
        self.assertEqual(p['quarantine_annotations'],[])
    def test_all_approval_flags_false(self):
        m=gate.quarantine_reviewer_csv(self.b,self.b['csv_tables'])['manifest']
        for flag in r37.HOLD_FLAGS:self.assertFalse(m[flag])
    def test_source_lineage_preserved(self):
        m=gate.quarantine_reviewer_csv(self.b,self.b['csv_tables'])['manifest']
        self.assertEqual((m['parent_R34_original_reading_sha256'],m['parent_R35_fingerprint_sha256'],m['parent_R36_fingerprint_sha256']),('a'*64,'b'*64,'c'*64))
    def test_deterministic_hash(self):
        p=gate.quarantine_reviewer_csv(self.b,self.b['csv_tables'])
        self.assertEqual(p['manifest']['fingerprint_sha256'],r37.sha({k:v for k,v in p['manifest'].items() if k!='fingerprint_sha256'}))
    def test_reproducible(self):
        self.assertEqual(gate.quarantine_reviewer_csv(self.b,self.b['csv_tables']),gate.quarantine_reviewer_csv(self.b,self.b['csv_tables']))
    def test_lf_newline_supported(self):
        updated={k:v.replace('\r\n','\n') for k,v in self.b['csv_tables'].items()}
        self.assertEqual(gate.quarantine_reviewer_csv(self.b,updated)['manifest']['unverified_progress_records'],0)
    def test_untrusted_claim_note(self):
        q=mutate_csv(self.b,'human_scope_risk_notes','Check paragraph citation',state='FLAGGED_FOR_FACT_CHECK')
        p=gate.quarantine_reviewer_csv(self.b,q)
        self.assertEqual(p['manifest']['unverified_progress_records'],1)
        self.assertEqual(p['quarantine_annotations'][0]['submitted_progress_unverified'],'FLAGGED_FOR_FACT_CHECK')
        self.assertFalse(p['manifest']['source_claim_accuracy_verified'])
    def test_untrusted_observation_date(self):
        q=mutate_csv(self.b,'human_access_date','2026-10-31','source_scope_review.csv','IN_PROGRESS')
        self.assertEqual(gate.quarantine_reviewer_csv(self.b,q)['manifest']['unverified_progress_records'],1)
    def test_private_escalation_never_grants_safety(self):
        q=mutate_csv(self.b,'human_scope_risk_notes','Needs qualified clinician',state='ESCALATE_TO_QUALIFIED_REVIEW')
        m=gate.quarantine_reviewer_csv(self.b,q)['manifest']
        self.assertFalse(m['qualified_safety_clearance'])
        self.assertTrue(m['no_authenticated_human_reviews_or_qualified_safety_findings'])
    def test_inputs_unchanged(self):
        before=copy.deepcopy(self.b)
        gate.quarantine_reviewer_csv(self.b,self.b['csv_tables'])
        self.assertEqual(before,self.b)

class Negative(unittest.TestCase):
    def setUp(self):self.b=fixture()
    def test_missing_table(self):
        t=copy.deepcopy(self.b['csv_tables']);t.pop('claim_review.csv');rejected(self.b,t)
    def test_extra_table(self):
        t=copy.deepcopy(self.b['csv_tables']);t['extra.csv']='';rejected(self.b,t)
    def test_baseline_digest_mismatch(self):
        b=copy.deepcopy(self.b);b['csv_tables']['claim_review.csv']+='\n';rejected(b,b['csv_tables'])
    def test_manifest_rehash_rejects_fake_approval(self):
        b=copy.deepcopy(self.b);b['manifest']['qualified_safety_clearance']=True
        b['manifest']['fingerprint_sha256']=r37.sha({k:v for k,v in b['manifest'].items() if k!='fingerprint_sha256'})
        rejected(b,b['csv_tables'])
    def test_manifest_unknown_authority(self):
        b=copy.deepcopy(self.b);b['manifest']['machine_authority']='PUBLISHED'
        b['manifest']['fingerprint_sha256']=r37.sha({k:v for k,v in b['manifest'].items() if k!='fingerprint_sha256'})
        rejected(b,b['csv_tables'])
    def test_not_started_with_notes(self):
        rejected(self.b,mutate_csv(self.b,'human_scope_risk_notes','hidden note'))
    def test_progress_with_no_notes(self):
        rejected(self.b,mutate_csv(self.b,'review_state','IN_PROGRESS'))
    def test_fake_qd_pass(self):
        rejected(self.b,mutate_csv(self.b,'review_state','QD PASS'))
    def test_fake_done(self):
        rejected(self.b,mutate_csv(self.b,'review_state','DONE'))
    def test_direct_safety_cleared(self):
        rejected(self.b,mutate_csv(self.b,'human_qualified_safety_check','YES',state='IN_PROGRESS'))
    def test_global_safety_cleared(self):
        rejected(self.b,mutate_csv(self.b,'human_independent_safety_assessment','PASS','global_shared_url_review.csv','IN_PROGRESS'))
    def test_invalid_date(self):
        rejected(self.b,mutate_csv(self.b,'human_access_date','2026-02-30','source_scope_review.csv','IN_PROGRESS'))
    def test_bad_date_format(self):
        rejected(self.b,mutate_csv(self.b,'human_access_date','10/31/2026','source_scope_review.csv','IN_PROGRESS'))
    def test_duplicate_case(self):
        t=copy.deepcopy(self.b['csv_tables']);t['claim_review.csv']+=t['claim_review.csv'].split('\r\n')[1]+'\r\n';rejected(self.b,t)
    def test_spreadsheet_bom(self):
        t=copy.deepcopy(self.b['csv_tables']);t['claim_review.csv']='\ufeff'+t['claim_review.csv'];rejected(self.b,t)
    def test_csv_null_byte(self):
        t=copy.deepcopy(self.b['csv_tables']);t['claim_review.csv']='\x00'+t['claim_review.csv'];rejected(self.b,t)
    def test_invalid_unicode_surrogate(self):
        t=copy.deepcopy(self.b['csv_tables']);t['claim_review.csv']+='\ud800';rejected(self.b,t)
    def test_note_over_limit(self):
        rejected(self.b,mutate_csv(self.b,'human_scope_risk_notes','x'*2049,state='IN_PROGRESS'))
    def test_note_control_character(self):
        rejected(self.b,mutate_csv(self.b,'human_scope_risk_notes','x\x01y',state='IN_PROGRESS'))
    def test_note_bidi_reversal(self):
        rejected(self.b,mutate_csv(self.b,'human_scope_risk_notes','x\u202ey',state='IN_PROGRESS'))

# A separate executable case for every original evidence column across all
# four tables. URLs, source uses, original context, identifiers, source variants,
# codepoint offsets and fallback relationships may never be silently modified.
for _name,_columns in r37.TABLES.items():
    for _column in _columns:
        if _column=='review_state' or _column.startswith('human_'):continue
        def case(self, name=_name, column=_column):
            rejected(self.b,mutate_csv(self.b,column,'TAMPERED: '+column,name))
        setattr(Negative,'test_original_'+_name.split('.')[0]+'_'+_column,case)

for _suffix,_text in {'equal':'=HYPERLINK(1)','plus':'+SUM(A1)',
                      'minus':'-1+2','at':'@SUM(1)','whitespace':'   =1+1',
                      'zero_width':'\u200b=1+1','bom':'\ufeff=SUM(A1)',
                      'word_joiner':'\u2060=IMPORTXML()'}.items():
    def case(self, value=_text):
        rejected(self.b,mutate_csv(self.b,'human_scope_risk_notes',value,state='IN_PROGRESS'))
    setattr(Negative,'test_formula_'+_suffix,case)

if __name__=='__main__':unittest.main()
