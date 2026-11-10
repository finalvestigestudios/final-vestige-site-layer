"""R263 negative safety witness: 60+ synthetic regressions, never real print QA."""
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / 'tools/r263_wallet_cutout_privacy_witness_hold.py'
spec = importlib.util.spec_from_file_location('r263', p)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

NOTICE = r.NOTICE_PREFIX + ' Anyone who finds it can read it.'
OLD = 'The form below still works and prints.'
CORRECTED = 'Use your browser Print command for the blank card.'
FIELDS = ['Household', 'Phone', 'Out-of-area contact', 'Out-of-area phone',
          'Meet first at', 'If not, meet at', 'School or childcare',
          'Reunification plan', 'Pick-up reminder', 'Caregiver',
          'Caregiver phone', 'Communication needs', 'Reviewed']

def original():
    first = ''.join('<p><b>'+n+':</b> blank</p>' for n in FIELDS[:6])
    second = ''.join('<p><b>'+n+':</b> blank</p>' for n in FIELDS[6:])
    nojs = (r.FALLBACK_START + r.FOLD_OPEN
            + '<div class="pa-face">' + first + '</div>'
            + '<div class="pa-face">' + second + '</div></div></div></noscript>')
    return ('<style>@media print {\n' + r.PRINT_CARD_CSS + ' other: 1; }\n'
            + r.PRINT_FACE_CSS + ' }</style>\n'
            + '<script>\n' + r.JS_FACE_START + '\n return document.createElement("div");\n}\n'
            + r.JS_FACE_END + '\n}\n'
            + r.JS_NOTE_PREFIX + " and fold it.'));\n"
            + 'for (var i = 0; i < copies; i++) {\n'
            + r.JS_CARD + '\n}\n</script>\n'
            + '<noscript><p>' + OLD + '</p></noscript>\n'
            + nojs + '\n{{cite:ready}} {{link:communications|guide}}')

class FakeR261:
    PATH = 'content/tools/family-reunification-card.body.html'
    def propose(self, raw, *, expected_blob):
        s = raw.decode('utf-8')
        assert r.git_blob(raw) == expected_blob
        s = s.replace('and fold it.', 'and fold it. '+NOTICE, 1)
        s = s.replace(r.FALLBACK_START, r.FALLBACK_START + '<p>'+NOTICE+'</p>', 1)
        return s, {'state':r.HOLD}

class FakeR262:
    CORRECTED = CORRECTED
    def __init__(self, fn=None, alter_receipt=None):
        self.fn = fn
        self.alter_receipt = alter_receipt
    def propose(self, raw, r261, *, expected_original_blob):
        s,_ = r261.propose(raw,expected_blob=expected_original_blob)
        s = s.replace(OLD,CORRECTED,1)
        if self.fn:
            s = self.fn(s)
        receipt = {
            'state':r.HOLD,'original_git_blob':expected_original_blob,
            'r262_candidate_blob':r.git_blob(s.encode()),
            'two_print_privacy_notices_retained':True,
            'citations_and_links_unchanged':True,'original_source_unchanged':True,
            **{k:False for k in r.REQUIRED_FALSE},
        }
        if self.alter_receipt:
            receipt.update(self.alter_receipt)
        return s,receipt

def check(source=None, fn=None, alter_receipt=None, pin=None):
    src=original() if source is None else source
    raw=src.encode('utf-8')
    return r.inspect(raw,FakeR261(),FakeR262(fn,alter_receipt),expected_original_blob=pin or r.git_blob(raw))

class Positive(unittest.TestCase):
    def test_witness_is_nonpassing(self):
        a=check()
        self.assertEqual(a['state'],r.HOLD)
        for field in ('wallet_cutout_has_privacy_warning','printed_card_privacy_resolved',
                      'actual_browser_and_physical_cutout_qa_completed',
                      'qualified_child_privacy_review_completed'):
            with self.subTest(field=field):self.assertIs(a[field],False)
    def test_two_print_page_warnings_are_not_on_cutout(self):
        a=check()
        self.assertTrue(a['javascript_warning_on_print_page_only'])
        self.assertTrue(a['nojs_warning_on_print_page_only'])
    def test_original_fields_retained(self): self.assertEqual(check()['nojs_source_field_count'],13)
    def test_print_clipping_witness(self): self.assertTrue(check()['print_css_face_overflow_hidden'])
    def test_child_release_hold(self): self.assertTrue(check()['requires_editorial_resolution_before_publication'])
    def test_original_sha(self): self.assertEqual(check()['original_git_blob'],r.git_blob(original().encode()))
    def test_draft_sha(self):
        text,_=FakeR262().propose(original().encode(),FakeR261(),expected_original_blob=r.git_blob(original().encode()))
        self.assertEqual(check()['r262_candidate_blob'],r.git_blob(text.encode()))
    def test_reject_changed_source_sha(self):
        with self.assertRaisesRegex(ValueError,'identity mismatch'):check(pin='0'*40)
    def test_reject_malformed_pin(self):
        with self.assertRaisesRegex(ValueError,'invalid source pin'):check(pin='BAD')
    def test_reject_bytes_type(self):
        with self.assertRaisesRegex(ValueError,'bytes'):r.inspect('str',FakeR261(),FakeR262())
    def test_reject_nul(self):
        with self.assertRaises(ValueError):r.inspect(b'abc\0',FakeR261(),FakeR262())
    def test_reject_prior_approval(self):
        with self.assertRaisesRegex(ValueError,'custody'):check(alter_receipt={'independent_qd_pass':True})
    def test_reject_prior_missing_boolean(self):
        with self.assertRaisesRegex(ValueError,'custody'):check(alter_receipt={'privacy_certified':None})
    def test_reject_wrong_prior_sha(self):
        with self.assertRaisesRegex(ValueError,'custody'):check(alter_receipt={'r262_candidate_blob':'1'*40})
    def test_reject_source_token_rewrite(self):
        with self.assertRaisesRegex(ValueError,'citation'):check(fn=lambda s:s.replace('{{cite:ready}}','{{cite:wrong}}'))
    def test_reject_added_notice_on_card_changes_witness(self):
        with self.assertRaises(ValueError):check(fn=lambda s:s.replace('<div class="pa-face">','<div class="pa-face">'+NOTICE,1))
    def test_reject_js_warning_on_card_changes_witness(self):
        with self.assertRaises(ValueError):check(fn=lambda s:s.replace('return document.createElement("div");','return document.createElement("div"); '+NOTICE))
    def test_reject_nojs_warning_removed(self):
        with self.assertRaises(ValueError):check(fn=lambda s:s.replace('<p>'+NOTICE+'</p>','',1))
    def test_reject_js_warning_removed(self):
        with self.assertRaises(ValueError):check(fn=lambda s:s.replace('and fold it. '+NOTICE,'and fold it.',1))
    def test_reject_duplicate_print_notice(self):
        with self.assertRaises(ValueError):check(fn=lambda s:s.replace('and fold it. '+NOTICE,'and fold it. '+NOTICE+' '+NOTICE,1))
    def test_reject_missing_js_card(self):
        with self.assertRaisesRegex(ValueError,'structure'):check(fn=lambda s:s.replace(r.JS_CARD,'//removed'))
    def test_reject_css_clipping_mutation(self):
        with self.assertRaisesRegex(ValueError,'print dimensions'):check(fn=lambda s:s.replace('overflow: hidden','overflow: visible'))
    def test_reject_nojs_card_count_mutation(self):
        with self.assertRaises(ValueError):check(fn=lambda s:s.replace(r.FOLD_OPEN,'<div class="other">'))
    def test_never_releases(self):
        a=check()
        for k in r.REQUIRED_FALSE:
            with self.subTest(k=k):self.assertIs(a[k],False)

# Every case mutates the *in-memory draft*, recomputes its candidate digest,
# and must still be rejected by semantic witness checks rather than a stale SHA.
MUTATIONS = [
    (f'field_{i}',f'<b>{f}:</b>',f'<i>{f}:</i>') for i,f in enumerate(FIELDS)
] + [
    ('card_'+str(i),frag,frag.replace('pa-','fx-',1)) for i,frag in enumerate([
      '<div class="pa-face">','<div class="pa-foldcard">',
      r.JS_CARD, r.JS_NOTE_PREFIX, r.PRINT_CARD_CSS,r.PRINT_FACE_CSS,
      r.JS_FACE_START, r.JS_FACE_END, r.FALLBACK_START,r.FALLBACK_CLOSE,
    ]) if 'pa-' in frag
] + [
    ('css_'+str(i),old,new) for i,(old,new) in enumerate([
      ('width: 7in','width: 8in'), ('height: 2.125in','height: 4in'),
      ('font-size: 7.5pt','font-size: 3pt'),('overflow: hidden','overflow: visible'),
      ('grid-template-columns: 1fr 1fr','grid-template-columns: 1fr'),
      ('border-right: 1px dashed #000','border-right: 0'),
      ('padding: .07in .1in','padding: .07in .2in'),
      ('line-height: 1.14','line-height: 0.8'),
    ])
] + [
    ('notice_'+str(i),old,new) for i,(old,new) in enumerate([
      (NOTICE,NOTICE.replace('photographed','copied')),
      (r.JS_NOTE_PREFIX,"pr.appendChild(el('p','fake', 'Cut out each card"),
      (r.JS_CARD,r.JS_CARD.replace("pr.appendChild(c)","pr.removeChild(c)")),
      (r.FALLBACK_START,'<noscript><div class="other">'),
      ('<div class="pa-face">','<div class="pa-fface">'),
      ('</div></div></div></noscript>','</div></div></noscript>'),
      (CORRECTED,'Automatic reminders and a text download are available.'),
      ('{{link:communications|guide}}','{{link:other|guide}}'),
    ])
]
# Additional unique semantic field alterations, to ensure >36 regression cases.
MUTATIONS += [
    (f'label_{i}',f'{f}:</b>',f'{f}!</b>') for i,f in enumerate(FIELDS)
]

def add_mutation_test(label,old,new):
    def test(self):
        before,_=FakeR262().propose(original().encode(),FakeR261(),expected_original_blob=r.git_blob(original().encode()))
        self.assertIn(old,before)
        with self.assertRaises(ValueError):
            check(fn=lambda s:s.replace(old,new,1))
    setattr(Adversarial,'test_mutate_'+label,test)

class Adversarial(unittest.TestCase):pass
for label,old,new in MUTATIONS:
    add_mutation_test(label,old,new)

if __name__=='__main__':unittest.main()
