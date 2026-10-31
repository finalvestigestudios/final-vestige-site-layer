#!/usr/bin/env python3
"""Negative-control mutations against real R27 Chromium-rendered tagged PDF bytes."""
from __future__ import annotations
from pathlib import Path
import os
import tempfile
import unittest
from pypdf import PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DictionaryObject,
                           NameObject, TextStringObject)
from pdf_binary_security_r28 import audit_pdf_binary, PdfCustodyHold, NASA_PHOTOS

# GitHub QA standard: input an actual Chromium file, not a made-up PDF fixture.
SAMPLE = Path(os.environ.get('FV_R28_PDF_FIXTURE', '')).resolve() if os.environ.get('FV_R28_PDF_FIXTURE') else (Path(__file__).resolve().parent / 'r26-pdf-evidence' / 'apollo-r26-custody-390.pdf')


def name(key):
    return NameObject(key)


def new_action(kind: str, url: str | None = None):
    d = DictionaryObject({name('/S'): name(kind)})
    if url is not None:
        d[name('/URI')] = TextStringObject(url)
    return d


class PdfBinarySecurityR28(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SAMPLE.is_file():
            raise RuntimeError('No independently generated tagged Chromium input PDF')
        cls.source = SAMPLE

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fv-apollo-r28-')
        self.addCleanup(self.tmp.cleanup)

    def write_mutation(self, name_suffix, mutation):
        w = PdfWriter(clone_from=str(self.source))
        mutation(w)
        out = Path(self.tmp.name) / f'{name_suffix}.pdf'
        with out.open('wb') as f:
            w.write(f)
        return out

    def reject(self, kind, mutation, message):
        candidate = self.write_mutation(kind, mutation)
        with self.assertRaisesRegex(PdfCustodyHold, message):
            audit_pdf_binary(candidate)

    def test_real_chromium_sample_accepted(self):
        receipt = audit_pdf_binary(self.source)
        self.assertEqual(receipt['pages'], 3)
        self.assertEqual(receipt['nasa_photo_annotations'], 6)
        self.assertEqual(receipt['embedded_attachments'], 0)
        self.assertEqual(receipt['active_or_non_http_actions'], 0)
        self.assertGreater(receipt['reachable_pdf_dictionaries'], 100)

    def test_rewritten_clean_document_accepted(self):
        candidate = self.write_mutation('unchanged', lambda w: None)
        self.assertEqual(audit_pdf_binary(candidate)['status'], 'PASS_OFFLINE_BINARY_SAFETY_ONLY')

    def test_reject_document_javascript_open_action(self):
        self.reject('js_open', lambda w: w._root_object.update({name('/OpenAction'): new_action('/JavaScript')}), 'Disallowed PDF object key')

    def test_reject_embedded_file_name_tree(self):
        self.reject('embedded_tree', lambda w: w._root_object.update({name('/Names'): DictionaryObject({name('/EmbeddedFiles'): DictionaryObject()})}), 'Disallowed PDF object key')

    def test_reject_ordinary_attachments(self):
        self.reject('attachment', lambda w: w.add_attachment('extra.txt', b'not a NASA original'), 'Disallowed PDF object key')

    def test_reject_interactive_pdf_form(self):
        self.reject('acroform', lambda w: w._root_object.update({name('/AcroForm'): DictionaryObject()}), 'Disallowed PDF object key')

    def test_reject_page_additional_action(self):
        self.reject('page_aa', lambda w: w.pages[0].update({name('/AA'): DictionaryObject()}), 'Disallowed PDF object key')

    def test_reject_javascript_link_action(self):
        def alter(w):
            w.pages[0]['/Annots'][0].get_object()[name('/A')] = new_action('/JavaScript')
        self.reject('link_js', alter, 'Disallowed PDF object key|Disallowed active PDF action')

    def test_reject_launch_link_action(self):
        def alter(w):
            w.pages[0]['/Annots'][0].get_object()[name('/A')] = new_action('/Launch')
        self.reject('launch', alter, 'Disallowed active PDF action')

    def test_reject_non_nasa_link(self):
        def alter(w):
            w.pages[0]['/Annots'][0].get_object()[name('/A')] = new_action('/URI','https://attacker.invalid/redirect')
        self.reject('external_link', alter, 'Unapproved PDF URI')

    def test_reject_unreferenced_hidden_external_link(self):
        def alter(w):
            w._root_object[name('/ExtraReviewAction')] = new_action('/URI','https://attacker.invalid/')
        self.reject('hidden_link', alter, 'Unapproved PDF URI')

    def test_reject_file_attachment_annotation(self):
        def alter(w):
            w.pages[0]['/Annots'][0].get_object()[name('/Subtype')] = name('/FileAttachment')
        self.reject('attachment_annotation', alter, 'Disallowed PDF media/attachment annotation')

    def test_reject_missing_actual_tag_tree(self):
        self.reject('tag_tree', lambda w: w._root_object.pop('/StructTreeRoot'), 'Missing actual PDF structure tree')

    def test_reject_missing_parent_tree(self):
        def alter(w):
            w._root_object['/StructTreeRoot'].get_object().pop('/ParentTree')
        self.reject('parent_tree', alter, 'Incomplete PDF structure/parent tree')

    def test_reject_false_marked_flag(self):
        def alter(w):
            w._root_object['/MarkInfo'].get_object()[name('/Marked')] = BooleanObject(False)
        self.reject('tagged_false', alter, 'Tagged flag')

    def test_reject_unlabeled_document_language(self):
        self.reject('missing_lang', lambda w: w._root_object.pop('/Lang'), 'Missing English document language')

    def test_reject_missing_document_title_preference(self):
        def alter(w):
            w._root_object['/ViewerPreferences'].get_object()[name('/DisplayDocTitle')] = BooleanObject(False)
        self.reject('title_preference', alter, 'Viewer not configured')

    def test_reject_missing_nasa_source_annotation(self):
        def alter(w):
            links = w.pages[0]['/Annots'].get_object()
            del links[0]
        self.reject('missing_link', alter, 'Missing or unexpected source/report/policy annotation')

    def test_reject_duplicate_nasa_source_annotation(self):
        def alter(w):
            links = w.pages[0]['/Annots'].get_object()
            links.append(links[0])
        self.reject('duplicate', alter, 'One clickable annotation required')

    def test_reject_pdf_encryption(self):
        def alter(w):
            w.encrypt('user-key')
        self.reject('encryption', alter, 'PDF parser/catalog integrity failure|Encrypted PDF')

    def test_reject_non_link_annotation(self):
        def alter(w):
            w.pages[0]['/Annots'][0].get_object()[name('/Subtype')] = name('/Text')
        self.reject('text_annot', alter, 'Non-link annotation not permitted')


if __name__ == '__main__':
    unittest.main(verbosity=2)
