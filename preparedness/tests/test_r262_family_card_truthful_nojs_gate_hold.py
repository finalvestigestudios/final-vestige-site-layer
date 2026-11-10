"""Synthetic R262 source/copy gate regressions; NO real browser/print claims."""
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / 'tools/r262_family_card_truthful_nojs_gate_hold.py'
spec = importlib.util.spec_from_file_location('r262', p)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

OLD = ('The form below still works and prints. Only the automatic reminders '
       'and the text download need JavaScript.')
NOTICE = ('Privacy: A printed card can be lost or photographed. Anyone who finds it can read it.')


def original():
    return ('<style>@media print { .pa-card-mainhide { display: none!important; } }</style>\n'
            '<form class="pa-sheet pa-card-mainhide" id="rc" onsubmit="return false">\n'
            '<button id="rc-print" hidden>Print</button><button id="rc-reset" hidden>Clear</button>\n'
            '<div id="rc-preview"></div>\n'
            '<noscript><p>' + OLD + '</p></noscript>\n'
            '<noscript><div class="pa-printsheet"><div class="pa-foldcard">blank card</div></div></noscript>\n'
            '<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>\n'
            '<script>$(\'rc-live\').hidden = false;\n'
            "$('rc-print').hidden = false; $('rc-print').addEventListener('click', function () { window.print(); });\n"
            "$('rc-reset').hidden = false; $('rc-reset').addEventListener('click', function () { form.reset(); render(); });\n"
            '</script>\n<p>{{cite:shelter-ready-plan}}</p>\n<p>{{link:family-communication-plan|Guide}}</p>')


class FakeR261:
    PATH = 'content/tools/family-reunification-card.body.html'
    def __init__(self, *, flawed=False): self.flawed = flawed
    def propose(self, raw, *, expected_blob):
        s = raw.decode('utf-8')
        prior = s.replace(OLD, r.R261_INACCURATE, 1)
        prior = prior.replace('<script>', '<p>' + NOTICE + '</p><script>', 1)
        prior = prior.replace('blank card</div>', 'blank card<p>' + NOTICE + '</p></div>', 1)
        receipt = {'state': r.HOLD, 'original_git_blob': expected_blob,
                   'draft_git_blob': r.git_blob(prior.encode('utf-8')),
                   'changed_anchor_count': 3, 'draft_notice_occurrences': 2,
                   'release_authorized': False, 'privacy_certified': False,
                   'independent_qd_pass': False}
        if self.flawed: receipt['release_authorized'] = True
        return prior, receipt


def check(source=None, fake=None):
    source = original() if source is None else source
    raw = source.encode('utf-8')
    return r.propose(raw, fake or FakeR261(), expected_original_blob=r.git_blob(raw))


class Positive(unittest.TestCase):
    def test_state(self): self.assertEqual(check()[1]['state'], r.HOLD)
    def test_claim(self): self.assertIn(r.CORRECTED, check()[0])
    def test_old_claim_absent(self): self.assertNotIn(r.R261_INACCURATE, check()[0])
    def test_reminders_absent(self): self.assertNotIn('automatic reminders',check()[0])
    def test_download_absent(self): self.assertNotIn('text download',check()[0])
    def test_print_privacy_twice(self): self.assertEqual(check()[0].count(NOTICE),2)
    def test_exact_changed_step(self):
        candidate, receipt = check()
        prior, _ = FakeR261().propose(original().encode(),expected_blob=r.git_blob(original().encode()))
        self.assertEqual(candidate.replace(r.CORRECTED,r.R261_INACCURATE,1),prior)
        self.assertEqual(receipt['review_only_claim_replacements'],1)
    def test_diff_blob(self):
        candidate, receipt = check()
        self.assertEqual(receipt['r262_candidate_blob'],r.git_blob(candidate.encode()))
        self.assertNotEqual(receipt['r261_candidate_blob'],receipt['r262_candidate_blob'])
    def test_links_unchanged(self):
        candidate,_ = check()
        self.assertEqual(r.CITATION_TOKEN.findall(candidate),r.CITATION_TOKEN.findall(original()))
    def test_hold_flags(self):
        receipt=check()[1]
        for key in ('privacy_certified','medical_safety_verified','independent_qd_pass','source_review_approved',
                    'merchant_approved','release_authorized','public_published'):
            with self.subTest(key=key): self.assertIs(receipt[key],False)
    def test_original_not_modified(self): self.assertIn(OLD,original())
    def test_affordance_count(self): self.assertEqual(check()[1]['required_static_affordances'],len(r.CONTROL_ANCHORS))
    def test_no_raw_body_in_receipt(self): self.assertNotIn('blank card',str(check()[1]))
    def test_source_pin_invalid(self):
        with self.assertRaisesRegex(ValueError,'pin mismatch'): r.propose(original().encode(),FakeR261())
    def test_bad_pin(self):
        with self.assertRaisesRegex(ValueError,'malformed original pin'): r.propose(original().encode(),FakeR261(),expected_original_blob='BAD')
    def test_bad_type(self):
        for payload in (None,'hi',b'',b'\0',b'x'*3_000_001):
            with self.subTest(payload=repr(payload)[:20]), self.assertRaises(ValueError):
                r.propose(payload,FakeR261())
    def test_bad_r261_receipt(self):
        with self.assertRaisesRegex(ValueError,'custody'): check(fake=FakeR261(flawed=True))
    def test_missing_r261(self):
        with self.assertRaisesRegex(ValueError,'missing authenticated'): check(fake=object())
    def test_audit_offline(self):
        source=original().encode()
        class StubR261(FakeR261): pass
        stub=StubR261()
        with self.assertRaisesRegex(ValueError, 'pin mismatch'):
            r.audit(object(), lambda root, path: source, stub)


class Adversarial(unittest.TestCase): pass


def mutate_test(needle, replacement):
    def test(self):
        source=original()
        self.assertIn(needle,source)
        modified=source.replace(needle,replacement,1)
        self.assertNotEqual(source,modified)
        with self.assertRaises(ValueError): check(source=modified)
    return test

for i,anchor in enumerate(r.CONTROL_ANCHORS):
    setattr(Adversarial,f'test_missing_affordance_{i:02d}',mutate_test(anchor, '<removed/>'))
    setattr(Adversarial,f'test_duplicate_affordance_{i:02d}',mutate_test(anchor,anchor+anchor))
for i,character in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    anchor=r.CONTROL_ANCHORS[i % len(r.CONTROL_ANCHORS)]
    setattr(Adversarial,f'test_corrupt_affordance_{i:02d}',mutate_test(anchor,anchor[:5]+character+anchor[6:]))
setattr(Adversarial,'test_claim_removed',mutate_test(OLD,'The form works without scripts.'))
setattr(Adversarial,'test_claim_doubled',mutate_test(OLD,OLD+OLD))

if __name__=='__main__': unittest.main()
