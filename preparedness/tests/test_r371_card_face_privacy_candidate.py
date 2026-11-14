"""R371 synthetic/adversarial tests; NEVER claims true Tool #104 or WordPress safety."""
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve()
MODULE = HERE.parents[1] / 'tools' / 'r371_card_face_privacy_candidate.py'
spec = importlib.util.spec_from_file_location('r370', MODULE)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def fixture():
    return ('<section>{{cite:shelter-cdc-reunification}}<p>A printed card can be lost</p>'
            '<style>.pa-card-mainhide { display: none !important; }'
            '.pa-printpage-note { display: block; font-size: 8pt; }' + m.CSS_ANCHOR + '</style>'
            '<form class="pa-sheet pa-card-mainhide" id="rc" onsubmit="return false" >form</form>'
            '<noscript><div>JavaScript is off. The form below still works and prints. '
            'Only the automatic reminders and the text download need JavaScript.</div></noscript>'
            + m.NOJS_OLD + m.NOJS_FACES[0] + '<p>Contact</p></div>' + m.NOJS_FACES[1] + '<p>Care</p></div></div></noscript>'
            '<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>'
            '<script>function face(title, rows) {' + m.FACE_ANCHOR + 'return d;} function render() { ' + m.JS_OLD + ' }</script></section>')

class Candidate(unittest.TestCase):
    def test_candidate_notice_added_to_both_print_modes(self):
        q=m.build_candidate(fixture())
        self.assertEqual(q.count(m.NOJS_NEW),1); self.assertEqual(q.count(m.JS_NEW),1)
        self.assertIn('pa-printpage-note',q)
    def test_no_js_copy_is_truthful(self):
        q=m.build_candidate(fixture())
        self.assertIn(m.COPY_NEW,q)
        self.assertNotIn(m.COPY_OLD,q)
    def test_unsafe_changes_not_approved(self):
        self.assertTrue(all(v is False for v in m.RELEASE_FLAGS.values()))
    def test_candidate_is_deterministic(self):
        self.assertEqual(m.build_candidate(fixture()),m.build_candidate(fixture()))
    def test_original_preserved(self):
        s=fixture();m.build_candidate(s);self.assertIn(m.COPY_OLD,s)
    def test_citations_unchanged(self):
        s=fixture(); q=m.build_candidate(s)
        self.assertEqual(q.count('{{cite:'),s.count('{{cite:'))
    def test_no_js_hidden_form_preserved(self):
        self.assertIn('<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>',m.build_candidate(fixture()))
    def test_no_js_form_submitting_unchanged(self):
        self.assertEqual(m.build_candidate(fixture()).count('onsubmit="return false"'),1)
    def test_candidate_is_not_release(self):
        self.assertFalse(m.RELEASE_FLAGS['card_cutout_warning_verified'])
    def test_source_hash_is_git_blob(self):
        x=b'hello'; self.assertEqual(m.git_blob(x),hashlib.sha1(b'blob 5\0hello').hexdigest())
    def test_diff_constructible(self):
        import difflib
        s=fixture();q=m.build_candidate(s)
        self.assertTrue(''.join(difflib.unified_diff(s.splitlines(True),q.splitlines(True))))
    def test_reject_missing_tree(self):
        with tempfile.TemporaryDirectory() as t:
            v=m.review(pathlib.Path(t));self.assertEqual(v['status'],'INVALID_HARD_HOLD')
    def test_source_missing_remains_release_hold(self):
        with tempfile.TemporaryDirectory() as t:
            v=m.review(pathlib.Path(t));self.assertFalse(v['may_publish'])
    def test_no_source_is_not_fake_approval(self):
        with tempfile.TemporaryDirectory() as t:
            v=m.review(pathlib.Path(t));self.assertFalse(v['qd_pass'])
    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as t:
            base=pathlib.Path(t);p=base/m.PATH;p.parent.mkdir(parents=True);p.symlink_to('/etc/hosts');
            v=m.review(base);self.assertIn('symlink_source_refused',str(v['errors']))
    def test_refuse_fabricated_meta(self):
        with tempfile.TemporaryDirectory() as t:
            base=pathlib.Path(t);p=base/m.PATH;p.parent.mkdir(parents=True);p.write_text(fixture());
            q=base/m.META;q.write_text('{}');
            self.assertIn('source_ref_changed',str(m.review(base)['errors']))
    def test_cli_returns_hard_hold(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(m.main(['--root',t]),2)

class CutoutCandidate(unittest.TestCase):
    def test_candidate_places_warning_in_scripted_face(self):
        self.assertIn("d.appendChild(el('p', 'pa-card-caution'", m.build_candidate(fixture()))
    def test_candidate_places_warning_in_nojs_front(self):
        self.assertIn(m.NOJS_FACES[0] + '<p class="pa-card-caution">' + m.CARD_WARNING,
                      m.build_candidate(fixture()))
    def test_candidate_places_warning_in_nojs_back(self):
        self.assertIn(m.NOJS_FACES[1] + '<p class="pa-card-caution">' + m.CARD_WARNING,
                      m.build_candidate(fixture()))
    def test_card_warning_count_in_candidate(self):
        self.assertEqual(m.build_candidate(fixture()).count(m.CARD_WARNING), 5)
    def test_only_candidate_changes_and_original_stays_same(self):
        src=fixture();m.build_candidate(src);self.assertNotIn('pa-card-caution',src)
    def test_print_css_notice_rule_in_candidate(self):
        self.assertIn(m.CSS_EXTRA,m.build_candidate(fixture()))
    def test_reject_duplicate_original_face_factory(self):
        with self.assertRaises(ValueError):
            m.build_candidate(fixture().replace(m.FACE_ANCHOR,m.FACE_ANCHOR*2))
    def test_reject_missing_nojs_front_face(self):
        with self.assertRaises(ValueError):
            m.build_candidate(fixture().replace(m.NOJS_FACES[0],''))
    def test_reject_missing_nojs_back_face(self):
        with self.assertRaises(ValueError):
            m.build_candidate(fixture().replace(m.NOJS_FACES[1],''))
    def test_reject_already_modified_card_candidate(self):
        with self.assertRaises(ValueError):m.build_candidate(m.build_candidate(fixture()))
    def test_retain_citation_order(self):
        src=fixture();out=m.build_candidate(src)
        import re
        self.assertEqual(re.findall(r'{{cite:[^}]+}}',src),re.findall(r'{{cite:[^}]+}}',out))
    def test_no_permission_to_merge_or_publish(self):
        self.assertFalse(m.RELEASE_FLAGS['may_merge']);self.assertFalse(m.RELEASE_FLAGS['may_publish'])
    def test_no_independent_child_privacy_approval(self):
        self.assertFalse(m.RELEASE_FLAGS['privacy_approved'])
    def test_no_real_paper_test_claim(self):
        self.assertFalse(m.RELEASE_FLAGS['physical_print_verified'])
    def test_no_verified_merchants_claim(self):
        self.assertFalse(m.RELEASE_FLAGS['verified_paid_orders'])


class MutationCases(unittest.TestCase):
    pass

# Parameterized adversarial removals and additions: each independently fails closed.
REMOVALS = sorted(set([*m.CHECKS.values(),m.NOJS_OLD,m.COPY_OLD,m.JS_OLD,m.FACE_ANCHOR,m.CSS_ANCHOR,*m.NOJS_FACES]))
for i,needle in enumerate(REMOVALS):
    def make_case(needle=needle):
        def test(self):
            with self.assertRaises(ValueError):
                m.build_candidate(fixture().replace(needle,''))
        return test
    setattr(MutationCases,'test_missing_guard_%02d'%i,make_case())
for i,needle in enumerate((m.NOJS_OLD,m.COPY_OLD,m.JS_OLD)):
    def make_case(needle=needle):
        def test(self):
            with self.assertRaises(ValueError):
                m.build_candidate(fixture().replace(needle,needle+needle))
        return test
    setattr(MutationCases,'test_duplicate_anchor_%02d'%i,make_case())
for i, needle in enumerate((m.NOJS_OLD,m.COPY_OLD,m.JS_OLD)):
    def make_case(needle=needle):
        def test(self):
            with self.assertRaises(ValueError):
                m.build_candidate(fixture().replace(needle,needle.swapcase()))
        return test
    setattr(MutationCases,'test_changed_anchor_%02d'%i,make_case())
# 40 repeatable value-preserving perturbations in unrelated document areas.
for i in range(40):
    def make_case(i=i):
        def test(self):
            raw=fixture()+('<p>Unrelated appendix '+str(i)+'! '*((i%5)+1)+'</p>')
            self.assertEqual(m.build_candidate(raw).count(m.NOJS_NEW),1)
            self.assertIn('Unrelated appendix '+str(i),m.build_candidate(raw))
        return test
    setattr(MutationCases,'test_unrelated_reading_depth_%02d'%i,make_case())

if __name__=='__main__':unittest.main()
