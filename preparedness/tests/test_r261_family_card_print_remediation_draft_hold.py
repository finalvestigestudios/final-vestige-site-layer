"""R261 offline regression suite. Synthetic only; no live browser/QD claims."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools/r261_family_card_print_remediation_draft_hold.py'
spec = importlib.util.spec_from_file_location('r261', MODULE)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def fixture():
    return ('''<style>@media print { .pa-card-mainhide { display: none !important; } '''
            '''.pa-printpage-note { display: block; } }</style>\n'''
            '''<div class="pa-card-mainhide">A printed card can be lost</div>\n'''
            '''<noscript><p>''' + r.NOJS_OLD + '''</p></noscript>\n'''
            + r.FALLBACK + '''<p><b>Household:</b> __________</p>'''
            '''</div></div></noscript>\n<script>pr.appendChild(el('p', 'pa-printpage-note', '''
            + "'" + r.JS_NOTE + "'" + '''));</script>\n'''
            '''<p>{{cite:shelter-ready-plan}}{{link:family-communication-plan|Guide}}</p>''')


def run_fixture(text=None):
    src = (fixture() if text is None else text).encode('utf-8')
    return r.propose(src, expected_blob=r.git_blob(src))


class Positive(unittest.TestCase):
    def test_hold(self): self.assertEqual(run_fixture()[1]['state'], r.HOLD)
    def test_exact_notice_twice(self): self.assertEqual(run_fixture()[0].count(r.NOTICE), 2)
    def test_js_note(self): self.assertIn(r.JS_NOTE + ' ' + r.NOTICE, run_fixture()[0])
    def test_nojs_notice(self): self.assertIn(r.FALLBACK_NEW, run_fixture()[0])
    def test_nojs_claim(self): self.assertIn(r.NOJS_NEW, run_fixture()[0])
    def test_old_claim_absent(self): self.assertNotIn(r.NOJS_OLD, run_fixture()[0])
    def test_evidence_preserved(self): self.assertIn('{{cite:shelter-ready-plan}}', run_fixture()[0])
    def test_canonical_link_preserved(self): self.assertIn('{{link:family-communication-plan|Guide}}', run_fixture()[0])
    def test_original_unmodified(self): self.assertEqual(fixture().count('A printed card can be lost'), 1)
    def test_distinct_blobs(self):
        draft, info = run_fixture(); self.assertNotEqual(info['original_git_blob'], info['draft_git_blob'])
        self.assertEqual(info['draft_git_blob'], r.git_blob(draft.encode()))
    def test_no_approval_flags(self):
        for key in ('privacy_certified','medical_safety_verified','independent_qd_pass',
                    'source_review_approved','merchant_approved','release_authorized','public_published'):
            with self.subTest(key=key): self.assertFalse(run_fixture()[1][key])
    def test_field_not_removed(self): self.assertIn('Household:', run_fixture()[0])
    def test_original_sha_enforced(self):
        with self.assertRaises(ValueError): r.propose(fixture().encode())
    def test_receipt_has_no_sensitive_card_content(self):
        self.assertNotIn('Household:', str(run_fixture()[1]))
    def test_draft_in_memory(self): self.assertEqual(run_fixture()[1]['changed_anchor_count'], 3)
    def test_utf8(self):
        raw=fixture().replace('Guide','Guía').encode('utf-8'); self.assertTrue(r.propose(raw,expected_blob=r.git_blob(raw)))


MUTATIONS = [
    ('missing_js', "'" + r.JS_NOTE + "'", "'Other note'"),
    ('missing_fallback', r.FALLBACK, '<noscript><div class="other">'),
    ('missing_nojs',r.NOJS_OLD,'Other functionality claim'),
    ('double_js', "'" + r.JS_NOTE + "'", "'" + r.JS_NOTE + "' + '" + r.JS_NOTE + "'"),
    ('duplicate_fallback',r.FALLBACK, r.FALLBACK+r.FALLBACK),
    ('duplicate_nojs',r.NOJS_OLD,r.NOJS_OLD+r.NOJS_OLD),
    ('injected_notice',r.JS_NOTE,r.JS_NOTE+' '+r.NOTICE),
    ('removed_print','@media print','@media screen'),
]
# Additional distinct malformed anchors, all rejected before any candidate is emitted.
for i,ch in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    MUTATIONS.append((f'changed_anchor_{i:02d}', r.JS_NOTE,
                      r.JS_NOTE[:5] + ch + r.JS_NOTE[6:]))


class Adversarial(unittest.TestCase):
    def test_invalid_input(self):
        for src in (None, '', b'', b'\0', b'\xff', b'x'*3_000_001):
            with self.subTest(size=str(src)[:20]), self.assertRaises(ValueError):
                r.propose(src,expected_blob='a'*40)
    def test_invalid_pin(self):
        for sha in (None,7,'','a'*39,'A'*40,'z'*40):
            with self.subTest(sha=sha),self.assertRaises(ValueError):
                r.propose(fixture().encode(),expected_blob=sha)
    def test_identity_mismatch(self):
        src=fixture().encode()
        with self.assertRaisesRegex(ValueError,'source identity'):
            r.propose(src+b' ',expected_blob=r.git_blob(src))


def mutation_test(before,after):
    def test(self):
        original=fixture(); self.assertIn(before,original)
        updated=original.replace(before,after,1); self.assertNotEqual(updated,original)
        with self.assertRaises(ValueError): run_fixture(updated)
    return test

for name,before,after in MUTATIONS:
    setattr(Adversarial,'test_'+name,mutation_test(before,after))

if __name__=='__main__': unittest.main()
