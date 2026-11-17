"""Synthetic, no-write safety probes for R436: not an authentic WordPress QA pass."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / 'tools' / 'r436_outside_main_semantic_custody_gate.py'
spec = importlib.util.spec_from_file_location('r436', SRC)
r436 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r436)


def html(out='<footer>For help check local authority instructions.</footer>',
         link='<a href="/preparedness/">Free checklist</a>',
         main='<p>Use verified official resources before acting.</p>',
         extra=''):
    return ('<!doctype html><html><head><title>Evidence</title></head><body><main>' + main +
            '</main>' + out + link + extra + '</body></html>').encode()


class R436SemanticCustody(unittest.TestCase):
    def test_clean_pair(self):
        self.assertEqual(r436.pair_review(html(), html())['errors'], [])

    def test_old_r435_same_href_inventory_with_changed_label(self):
        a = html(); b = html(link='<a href="/preparedness/">Pay us first</a>')
        self.assertNotEqual(r436.pair_review(a,b)['wordpress']['control_binding_sha256'],
                            r436.pair_review(a,b)['preview']['control_binding_sha256'])
        self.assertIn('CONTROL_ACCESSIBLE_NAME_OR_DESTINATION_DRIFT', r436.pair_review(a,b)['errors'])

    def test_old_r435_same_anchor_inventory_but_footer_changed(self):
        a=html(); b=html(out='<footer>Do not consult local authorities.</footer>')
        self.assertIn('OUTSIDE_MAIN_SAFETY_OR_CTA_COPY_DRIFT',r436.pair_review(a,b)['errors'])

    def test_wordcount_can_grow_while_safety_line_changes(self):
        a=html(); b=html(out='<footer>All safe, no caveats.</footer>'+ '<p>Extra historical narrative. </p>'*20)
        self.assertIn('OUTSIDE_MAIN_SAFETY_OR_CTA_COPY_DRIFT',r436.pair_review(a,b)['errors'])

    def test_swapped_link_bindings_same_destinations(self):
        a=html(link='<a href="/preparedness/">Official</a><a href="/focus/">Free Fieldbook</a>')
        b=html(link='<a href="/focus/">Official</a><a href="/preparedness/">Free Fieldbook</a>')
        self.assertIn('CONTROL_ACCESSIBLE_NAME_OR_DESTINATION_DRIFT', r436.pair_review(a,b)['errors'])

    def test_hard_hold_is_permanent(self):
        x = r436.hold([], {'errors':[]}, [])
        self.assertFalse(x['eligible']);self.assertFalse(x['publication_approved']);self.assertFalse(x['qualified_safety_approved'])
        self.assertIsNone(x['net_revenue_per_1000_qualified_human_sessions'])

    def test_no_unverified_manifest(self):
        with patch.object(r436,'load_parent',side_effect=ValueError):
            x=r436.audit({'articles':[]},{},{},test_only=True)
        self.assertIn('PARENT_R435_AUDIT_UNAVAILABLE',x['errors'])

    def test_unpaired_record(self):
        with patch.object(r436,'load_parent') as load:
            load.return_value.audit.return_value={'errors':[]}
            x=r436.audit({'articles':[{'slug':'article-one'}]},{},{},test_only=True)
        self.assertIn('MISSING_PAIR:article-one',x['errors'])

    def test_missing_evidence_exit_2(self):
        p=subprocess.run([sys.executable,'-I',str(SRC),'/no/manifest','/no/lock','/no/exports'],capture_output=True,text=True,timeout=6)
        self.assertEqual(p.returncode,2);self.assertIn('DRAFT_HARD_HOLD',p.stdout)

    def test_missing_aria_id(self):
        p=r436.inspect(html(link='<a href="/preparedness/" aria-labelledby="no-such-id"></a>'))
        self.assertIn('ARIA_REFERENCE_MISSING_OR_DUPLICATED',p['errors'])

    def test_valid_html_void_elements_not_false_unclosed(self):
        raw=b'<!doctype html><html><head><meta charset="utf-8"><link rel="canonical" href="/preparedness/"></head><body><main><img src="/x.png"><input type="text" aria-label="Name"><br>hello</main></body></html>'
        self.assertNotIn('UNCLOSED_DOCUMENT_OR_CONTROL',r436.inspect(raw)['errors'])

    def test_nested_accessible_labels_preserved(self):
        p=r436.inspect(html(link='<a href="/preparedness/"><strong>Start</strong> here</a>'))
        self.assertEqual(p['errors'],[])

    def test_invalid_bytes_fail_closed(self):
        for data in (None, {}, b'1', b'\0'*30, b'\xff'*30, b'a'*(r436.MAX_BYTES+1)):
            with self.subTest(value=type(data).__name__):
                with self.assertRaises((ValueError, UnicodeError)):
                    r436.inspect(data)

    def test_mutated_attributes(self):
        cases=[
            ('aria-label','aria-label="Official safety"'),
            ('aria-labelledby','aria-labelledby="different"'),
            ('aria-describedby','aria-describedby="note"'),
            ('title','title="Urgent buy now"'),
            ('target','target="_blank"'),
            ('rel','rel="sponsored"'),
            ('download','download="secret.txt"'),
            ('referrerpolicy','referrerpolicy="unsafe-url"'),
            ('hreflang','hreflang="fr"'),
            ('role','role="button"'),
        ]
        for key,addition in cases:
            with self.subTest(key=key):
                b=html(link=f'<a href="/preparedness/" {addition}>Free checklist</a>')
                self.assertIn('CONTROL_ACCESSIBLE_NAME_OR_DESTINATION_DRIFT',r436.pair_review(html(),b)['errors'])

    def test_mutated_footer_safety_context(self):
        sentences=['Do not call emergency services.', 'Water advisory can be ignored.',
            'No first aid review needed.', 'No sources were checked.',
            'Do not seek qualified medical advice.', 'Buy before reading the free guide.',
            'We automatically share child contact details.', 'Ignore local evacuation orders.',
            'Verified means no review needed.', 'Pay before accessing emergency information.',
            'This preservation method always works.', 'The medicine dosage is always safe.',
            'Children should use the same plan as adults.', 'Evacuation may be skipped.',
            'No emergency phone number is needed.', 'Panic is a productive strategy.',
            'School pickup names can be public.', 'No printer needed.',
            'Equipment failure is impossible.', 'Affiliate clicks equal revenue.']
        for s in sentences:
            with self.subTest(sentence=s):
                b=html(out='<footer>'+s+'</footer>')
                self.assertIn('OUTSIDE_MAIN_SAFETY_OR_CTA_COPY_DRIFT',r436.pair_review(html(),b)['errors'])

    def test_main_only_text_mutation(self):
        b=html(main='<p>Altered procedure but identical footer.</p>')
        errors=r436.pair_review(html(),b)['errors']
        self.assertIn('FULL_DOCUMENT_READING_COPY_DRIFT',errors)
        self.assertNotIn('OUTSIDE_MAIN_SAFETY_OR_CTA_COPY_DRIFT',errors)

    def test_whitespace_normalization(self):
        a=html(link='<a href="/preparedness/">Free  checklist</a>')
        b=html(link='<a href="/preparedness/">Free checklist</a>')
        self.assertNotIn('CONTROL_ACCESSIBLE_NAME_OR_DESTINATION_DRIFT',r436.pair_review(a,b)['errors'])

    def test_main_absent(self):
        p=r436.inspect(b'<html><body><p>No main</p></body></html>')
        self.assertIn('MISSING_OR_DUPLICATE_MAIN',p['errors'])

    def test_same_document_determinism(self):
        p=r436.inspect(html()); self.assertEqual(p,r436.inspect(html()))

    def test_empty_link_name(self):
        p=r436.inspect(html(link='<a href="/preparedness/"></a>'))
        self.assertIn('UNNAMED_INTERACTIVE_CONTROL',p['errors'])

    def test_unexpected_endtag(self):
        p=r436.inspect(html(extra='</strong>'))
        self.assertIn('UNEXPECTED_END_TAG',p['errors'])

    def test_no_network_or_cms_libs(self):
        data=SRC.read_text()
        for term in ('requests.', 'urllib.request', 'httpx.', 'subprocess.run(', 'wordpress_xmlrpc', 'wp_remote_post'):
            with self.subTest(term=term): self.assertNotIn(term,data)


if __name__=='__main__': unittest.main()
