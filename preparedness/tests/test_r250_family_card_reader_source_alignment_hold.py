"""R250 synthetic receipt mutations; full original repo and browser NOT tested."""
import hashlib
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r250', ROOT/'tools/r250_family_card_reader_source_alignment_hold.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
HTML = '''<section><h2>Unapproved</h2><p>The current shorter card can include six filled-in fields: household name, household phone number, out-of-area contact, out-of-area phone number, first meeting place, and review date. These details may be visible if a printed card is lost or shared.</p><p>The interactive form is hidden when JavaScript is off. It is not a saved plan.</p><p>Check the assertion of a written plan at home.</p><p>No paid kit and no paid checkout available.</p></section>'''

def receipts(html=HTML):
    matrix=[{'field':key,'print_label':key,'in_full':True,
             'in_minimal':key in {x[0] for x in mod.SIX},
             'reader_authorization':'UNREVIEWED'} for key in mod.ALL_KEYS]
    f={'state':mod.HOLD,'issue':136,'conversion_issue':820,'source_count':5,
       'full_field_count':13,'minimal_field_count':6,'minimal_excluded_field_count':7,
       'field_matrix':matrix,'human_review_required':True}
    for k in mod.FALSE_FLAGS:f[k]=False
    for k in ('unconditional_minimal_household_name','unconditional_minimal_household_phone',
              'unconditional_home_plan_statement','claimed_only_list_is_incomplete',
              'nojs_form_claim_is_contradicted','privacy_claim_scope_requires_browser_review'):
        f[k]=True
    p={'state':mod.HOLD,'issue':136,'conversion_issue':820,
       'printed_full_fields':13,'printed_shorter_fields':6,'excluded_shorter_fields':7,
       'visible_free_destinations':['/preparedness/'],
       'preview_sha256':hashlib.sha256(html.encode()).hexdigest(),
       'human_review_required':True}
    for k in mod.PREVIEW_FALSE_FLAGS:p[k]=False
    return f,p

class TestSourceReader(unittest.TestCase):
    def test_baseline(self):
        f,p=receipts()
        got=mod.inspect(f,p,HTML)
        self.assertEqual(got['state'],mod.HOLD)
        self.assertEqual(got['source_to_reader_six_field_parity'],'OBSERVED_NOT_APPROVED')
        self.assertEqual(got,mod.inspect(f,p,HTML))
        self.assertFalse(got['release_authorized'])

    def test_source_field_gate_mutations(self):
        for i in range(13):
            for key,value in (('in_minimal',not (mod.ALL_KEYS[i] in {x[0] for x in mod.SIX})),
                              ('in_full',False),('reader_authorization','APPROVED'),
                              ('field','different')):
                with self.subTest(i=i,key=key):
                    f,p=receipts()
                    f['field_matrix'][i][key]=value
                    with self.assertRaisesRegex(ValueError,'HARD HOLD'):
                        mod.inspect(f,p,HTML)

    def test_source_release_flags(self):
        for k in mod.FALSE_FLAGS:
            for v in (True,None,'false'):
                with self.subTest(k=k,v=v):
                    f,p=receipts();f[k]=v
                    with self.assertRaises(ValueError):mod.inspect(f,p,HTML)

    def test_preview_release_flags(self):
        for k in mod.PREVIEW_FALSE_FLAGS:
            for v in (True,None,'false'):
                with self.subTest(k=k,v=v):
                    f,p=receipts();p[k]=v
                    with self.assertRaises(ValueError):mod.inspect(f,p,HTML)

    def test_six_visible_labels(self):
        for key,label in mod.SIX:
            with self.subTest(key=key):
                bad=HTML.replace(label,'some other detail',1)
                f,p=receipts(bad)
                with self.assertRaisesRegex(ValueError,'six-field'):mod.inspect(f,p,bad)

    def test_claim_witness_mutations(self):
        keys=('unconditional_minimal_household_name','unconditional_minimal_household_phone',
              'unconditional_home_plan_statement','claimed_only_list_is_incomplete',
              'nojs_form_claim_is_contradicted','privacy_claim_scope_requires_browser_review')
        for k in keys:
            for v in (False,None,'yes'):
                with self.subTest(k=k,v=v):
                    f,p=receipts();f[k]=v
                    with self.assertRaises(ValueError):mod.inspect(f,p,HTML)

    def test_preview_disclosure_mutations(self):
        for term in ('printed card is lost or shared',
                     'interactive form is hidden when JavaScript is off',
                     'written plan at home', 'No paid kit', 'no paid checkout',
                     'six filled-in fields:'):
            with self.subTest(term=term):
                bad=HTML.replace(term,'[redacted]');f,p=receipts(bad)
                with self.assertRaises(ValueError):mod.inspect(f,p,bad)

    def test_receipt_and_count_drift(self):
        for k in ('full_field_count','minimal_field_count','minimal_excluded_field_count','source_count','issue','conversion_issue'):
            f,p=receipts();f[k]=0
            with self.subTest(k=k),self.assertRaises(ValueError):mod.inspect(f,p,HTML)
        for k in ('printed_full_fields','printed_shorter_fields','excluded_shorter_fields','issue','conversion_issue','preview_sha256','visible_free_destinations'):
            f,p=receipts();p[k]='BAD'
            with self.subTest(k=k),self.assertRaises(ValueError):mod.inspect(f,p,HTML)

    def test_bad_inputs(self):
        f,p=receipts()
        for bad in (None,7,[],{},b'bad'):
            with self.subTest(v=str(bad)),self.assertRaises(ValueError):mod.inspect(bad,p,HTML)
            with self.subTest(p=str(bad)),self.assertRaises(ValueError):mod.inspect(f,bad,HTML)
            with self.subTest(h=str(bad)),self.assertRaises(ValueError):mod.inspect(f,p,bad)

    def test_alternative_punctuation_or_duplicate(self):
        for s in (' review date, and first meeting place','review date and first meeting place',
                  'review date, date','review date and emergency contact'):
            bad=HTML.replace('and review date',s)
            f,p=receipts(bad)
            with self.subTest(s=s),self.assertRaises(ValueError):mod.inspect(f,p,bad)
        bad=HTML.replace('</section>','<p>six filled-in fields: six elsewhere.</p></section>')
        f,p=receipts(bad)
        with self.assertRaises(ValueError):mod.inspect(f,p,bad)


# Each independent adversarial mutation is an actual unittest case (not a subtest).
def generated_negative(case_id, mutate):
    def run(self):
        f,p=receipts()
        html=HTML
        f,p,html=mutate(f,p,html)
        with self.assertRaisesRegex(ValueError,'HARD HOLD'):
            mod.inspect(f,p,html)
    setattr(TestSourceReader,'test_negative_%03d'%case_id,run)

case=0
for k in mod.FALSE_FLAGS:
    def mut(f,p,h,k=k):f[k]=True;return f,p,h
    generated_negative(case,mut);case+=1
for k in mod.PREVIEW_FALSE_FLAGS:
    def mut(f,p,h,k=k):p[k]=True;return f,p,h
    generated_negative(case,mut);case+=1
for i in range(13):
    def mut(f,p,h,i=i):f['field_matrix'][i]['in_full']=False;return f,p,h
    generated_negative(case,mut);case+=1
for i in range(13):
    def mut(f,p,h,i=i):f['field_matrix'][i]['in_minimal']=not f['field_matrix'][i]['in_minimal'];return f,p,h
    generated_negative(case,mut);case+=1
for label in (x[1] for x in mod.SIX):
    def mut(f,p,h,label=label):
        h=h.replace(label,'incorrect label',1)
        p['preview_sha256']=hashlib.sha256(h.encode()).hexdigest()
        return f,p,h
    generated_negative(case,mut);case+=1
for k in ('source_count','full_field_count','minimal_field_count','minimal_excluded_field_count'):
    def mut(f,p,h,k=k):f[k]=0;return f,p,h
    generated_negative(case,mut);case+=1
for k in ('printed_full_fields','printed_shorter_fields','excluded_shorter_fields'):
    def mut(f,p,h,k=k):p[k]=0;return f,p,h
    generated_negative(case,mut);case+=1

class TestRealPreviewFixture(unittest.TestCase):
    def test_preview_exact_wording_with_synthetic_receipts(self):
        # Verifies this full preview's semantics. NOT source-authenticated R248.
        real=(ROOT/'audits/r249_family_card_reader_disclosure_draft.html').read_text()
        f,p=receipts(real)
        result=mod.inspect(f,p,real)
        self.assertEqual(result['source_to_reader_six_field_parity'],
                         'OBSERVED_NOT_APPROVED')

if __name__ == "__main__": unittest.main()
