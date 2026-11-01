"""R44 private ZIP custody: adversarial, deterministic, zero-publication tests."""
from __future__ import annotations

from copy import deepcopy
from io import BytesIO
import hashlib
import json
import sys
from pathlib import Path
import unittest
import warnings
from zipfile import ZipFile, ZipInfo, ZIP_STORED, ZIP_DEFLATED

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from test_r43_offline_review_bundle import example, view
import reviewer_private_zip_gate as gate

class Case(unittest.TestCase):
    def setUp(self):
        self.packet, self.counts = example(uncited=True)
        self.pin42 = self.packet['fingerprint_sha256']
        self.rendered = view(self.packet, self.counts)
        self.pin43 = self.rendered['manifest']['fingerprint_sha256']
        self.out = gate.build_private_zip(
            self.packet, trusted_r42_sha256=self.pin42, expected=self.counts)
        self.data = self.out['zip_bytes']

    def verify(self, raw=None, **kw):
        return gate.verify_private_zip(
            self.data if raw is None else raw,
            trusted_r42_sha256=kw.pop('pin42', self.pin42),
            trusted_r43_sha256=kw.pop('pin43', self.pin43),
            expected=kw.pop('counts', self.counts), **kw)

    def reject(self, data=None, **kw):
        with self.assertRaises((gate.PrivateZipHold, ValueError, TypeError)):
            self.verify(self.data if data is None else data, **kw)

    def members(self):
        with ZipFile(BytesIO(self.data)) as archive:
            return {info.filename: archive.read(info.filename)
                    for info in archive.infolist()}

    def modify(self, member_name, new):
        members = self.members()
        members[member_name] = new
        return gate._archive(members)

    def manifest_edit(self, edit):
        members = self.members()
        payload = json.loads(members['review-manifest.json'])
        edit(payload)
        payload['fingerprint_sha256'] = gate.sha(gate.canonical({
            k: v for k, v in payload.items() if k != 'fingerprint_sha256'}))
        members['review-manifest.json'] = gate.canonical(payload) + b'\n'
        return gate._archive(members)

    def source_edit(self, edit):
        def inner(m):
            edit(m['source_R43_manifest'])
            m['source_R43_manifest']['fingerprint_sha256'] = gate.sha(
                gate.canonical({k: v for k, v in
                                m['source_R43_manifest'].items()
                                if k != 'fingerprint_sha256'}))
        return self.manifest_edit(inner)

    def synthetic_zip_with_metadata(self, *, date=gate.FIXED_TIME,
                                    mode=gate.FILE_MODE, method=ZIP_DEFLATED,
                                    annotation=b''):
        members = self.members()
        stream = BytesIO()
        with ZipFile(stream, mode='w', compression=method) as out:
            out.comment = annotation
            for name in sorted(members):
                info = ZipInfo(name, date_time=date)
                info.create_system = 3
                info.external_attr = mode
                info.compress_type = method
                out.writestr(info, members[name])
        return stream.getvalue()


class Positive(Case):
    def test_01_packet_unchanged(self):
        original = deepcopy(self.packet)
        gate.build_private_zip(self.packet, trusted_r42_sha256=self.pin42,
                               expected=self.counts)
        self.assertEqual(self.packet, original)

    def test_02_deterministic(self):
        second = gate.build_private_zip(self.packet, trusted_r42_sha256=self.pin42,
                                        expected=self.counts)
        self.assertEqual(self.data, second['zip_bytes'])

    def test_03_sha256_package(self):
        self.assertEqual(self.out['sha256_zip'], hashlib.sha256(self.data).hexdigest())

    def test_04_exact_members(self):
        self.assertEqual(self.out['member_count'], 6)

    def test_05_no_stale_html(self):
        self.assertEqual(self.out['manifest']['source_R43_manifest']['files'],
                         self.rendered['manifest']['files'])

    def test_06_zip_roundtrip(self):
        self.assertEqual(self.verify(), self.out['manifest'])

    def test_07_html_has_index(self):
        self.assertIn('index.html', self.members())

    def test_08_html_has_global_uncited_source(self):
        self.assertIn(b'unused-shared-source',
                      self.members()['global-source-variants.html'])

    def test_09_tool_not_dropped(self):
        self.assertIn('articles/water-planner.html', self.members())

    def test_10_all_three_dossiers(self):
        self.assertEqual(len([x for x in self.members() if x.startswith('articles/')]),3)

    def test_11_source_reading_preserved(self):
        self.assertIn(b'Full article-specific reading note 1',
                      self.members()['articles/first-guide.html'])

    def test_12_second_source_reading_preserved(self):
        self.assertIn(b'Full article-specific reading note 2',
                      self.members()['articles/old-ways.html'])

    def test_13_no_external_urls_as_links(self):
        self.assertNotIn(b'href="https://', self.members()['index.html'])

    def test_14_original_url_not_removed(self):
        self.assertIn(b'https://example.org/contributor-shared-source',
                      self.members()['global-source-variants.html'])

    def test_15_release_hold_root(self):
        self.assertEqual(self.out['manifest']['release_state'], 'HOLD')

    def test_16_release_hold_inner(self):
        self.assertEqual(self.out['manifest']['source_R43_manifest']['release_state'],
                         'HOLD')

    def test_17_no_authority(self):
        self.assertIn('NOT_EDITORIAL_OR_SAFETY_APPROVAL',
                      self.out['manifest']['machine_authority'])

    def test_18_all_flags_false(self):
        for flag in gate.FLAGS:
            self.assertIs(self.out['manifest'][flag], False)
            self.assertIs(self.out['manifest']['source_R43_manifest'][flag], False)

    def test_19_manifest_exact_bytes(self):
        m = self.members()['review-manifest.json']
        self.assertEqual(m, gate.canonical(self.verify()) + b'\n')

    def test_20_metadata(self):
        with ZipFile(BytesIO(self.data)) as z:
            self.assertEqual(len(z.infolist()), 6)
            for item in z.infolist():
                self.assertEqual(item.date_time, gate.FIXED_TIME)
                self.assertEqual(item.external_attr, gate.FILE_MODE)
                self.assertEqual(item.compress_type, ZIP_DEFLATED)

    def test_21_no_parent_change(self):
        self.assertEqual(self.verify()['parent_R42_fingerprint_sha256'],self.pin42)

    def test_22_no_renderer_change(self):
        self.assertEqual(self.verify()['parent_R43_fingerprint_sha256'],self.pin43)

    def test_23_private_only_manifest(self):
        self.assertEqual(self.verify()['privacy'],
                         'PRIVATE_REVIEW_ONLY_NO_PUBLIC_LINKS_OR_CMS_UPLOAD')

    def test_24_member_names_sorted(self):
        with ZipFile(BytesIO(self.data)) as z:
            self.assertEqual(z.namelist(), sorted(z.namelist()))

    def test_25_all_pages_hold_banner(self):
        for name, content in self.members().items():
            if name.endswith('.html'):
                self.assertIn(b'PRIVATE / UNVERIFIED / HOLD',content)

    def test_26_hash_valid_per_page(self):
        source=self.verify()['source_R43_manifest']
        for name, member in self.members().items():
            if name != 'review-manifest.json':
                self.assertEqual(source['files'][name]['sha256_utf8'],gate.sha(member))

    def test_27_manifest_not_a_signature(self):
        self.assertNotIn('signature', self.out['manifest'])

    def test_28_archive_bytes(self):
        self.assertIs(type(self.data),bytes)

    def test_29_empty_input_unavailable(self):
        with self.assertRaises(gate.PrivateZipHold):
            gate.verify_private_zip(b'',trusted_r42_sha256=self.pin42,
                                    trusted_r43_sha256=self.pin43,
                                    expected=self.counts)

    def test_30_safe_path_contract(self):
        self.assertTrue(gate.allowed('articles/old-ways.html'))
        self.assertFalse(gate.allowed('articles/../unsafe.html'))
        self.assertFalse(gate.allowed('articles/x.svg'))


class Negative(Case):
    def test_wrong_r42_pin(self):
        self.reject(pin42='a'*64)

    def test_wrong_r43_pin(self):
        self.reject(pin43='b'*64)

    def test_missing_r42_pin(self):
        self.reject(pin42='')

    def test_missing_r43_pin(self):
        self.reject(pin43=None)

    def test_invalid_census(self):
        self.reject(counts=[*self.counts])

    def test_wrong_article_count(self):
        self.reject(counts=(4,1,5,3,1,1))

    def test_missing_r42_build_pin(self):
        with self.assertRaises(gate.PrivateZipHold):
            gate.build_private_zip(self.packet,trusted_r42_sha256='',
                                   expected=self.counts)

    def test_wrong_r42_build_pin(self):
        with self.assertRaises(gate.PrivateZipHold):
            gate.build_private_zip(self.packet,trusted_r42_sha256='a'*64,
                                   expected=self.counts)

    def test_source_packet_mutation(self):
        altered=deepcopy(self.packet)
        altered['article_dossiers'][0]['title']='Another document'
        with self.assertRaises(gate.PrivateZipHold):
            gate.build_private_zip(altered,trusted_r42_sha256=self.pin42,
                                   expected=self.counts)

    def test_non_bytes_input(self):
        self.reject(self.data.decode('latin-1'))

    def test_none_input(self):
        self.reject(None if False else bytearray(self.data))

    def test_truncated(self):
        self.reject(self.data[:-20])

    def test_random(self):
        self.reject(b'ZZZZ')

    def test_appended_polyglot_payload(self):
        self.reject(self.data+b'<script>bad</script>')

    def test_prefixed_polyglot_payload(self):
        self.reject(b'HEADER'+self.data)

    def test_byte_mutation(self):
        changed=bytearray(self.data)
        changed[len(changed)//3]^=1
        self.reject(bytes(changed))

    def test_lost_html(self):
        m=self.members();m.pop('articles/old-ways.html')
        self.reject(gate._archive(m))

    def test_lost_global(self):
        m=self.members();m.pop('global-source-variants.html')
        self.reject(gate._archive(m))

    def test_lost_manifest(self):
        m=self.members();m.pop('review-manifest.json')
        self.reject(gate._archive(m))

    def test_extra_html(self):
        m=self.members();m['articles/unverified.html']=b'<!doctype html>'
        self.reject(gate._archive(m))

    def test_path_traversal(self):
        m=self.members();m['../unsafe.html']=m.pop('articles/old-ways.html')
        self.reject(gate._archive(m))

    def test_absolute_path(self):
        m=self.members();m['/tmp/unsafe.html']=m.pop('articles/old-ways.html')
        self.reject(gate._archive(m))

    def test_windows_escaped_path(self):
        m=self.members();m['articles\\bad.html']=m.pop('articles/old-ways.html')
        self.reject(gate._archive(m))

    def test_nested_path(self):
        m=self.members();m['articles/sub/old-ways.html']=m.pop('articles/old-ways.html')
        self.reject(gate._archive(m))

    def test_changed_claim_html(self):
        self.reject(self.modify('articles/first-guide.html',
                                b'<!doctype html>altered evidence'))

    def test_changed_global_source(self):
        self.reject(self.modify('global-source-variants.html',
                                b'<!doctype html>missing uncited material'))

    def test_changed_manifest(self):
        self.reject(self.modify('review-manifest.json',
                                b'{"release_state":"PASS"}'))

    def test_empty_html(self):
        self.reject(self.modify('articles/old-ways.html', b''))

    def test_non_utf8_html(self):
        self.reject(self.modify('articles/old-ways.html', b'\xff'))

    def test_wrong_source_entry_hash(self):
        self.reject(self.source_edit(lambda m:m['files']['index.html'].update(
            sha256_utf8='a'*64)))

    def test_wrong_source_entry_length(self):
        self.reject(self.source_edit(lambda m:m['files']['index.html'].update(
            bytes_utf8=0)))

    def test_missing_source_entry(self):
        self.reject(self.source_edit(lambda m:m['files'].pop('index.html')))

    def test_unknown_source_entry(self):
        self.reject(self.source_edit(lambda m:m['files'].update(
            {'articles/new.html':{'sha256_utf8':'a'*64,'bytes_utf8':123}})))

    def test_wrong_parent_r43(self):
        self.reject(self.manifest_edit(lambda m:m.update(
            parent_R43_fingerprint_sha256='c'*64)))

    def test_wrong_parent_r42(self):
        self.reject(self.manifest_edit(lambda m:m.update(
            parent_R42_fingerprint_sha256='d'*64)))

    def test_wrong_release_state(self):
        self.reject(self.manifest_edit(lambda m:m.update(release_state='PASS')))

    def test_wrong_authority(self):
        self.reject(self.manifest_edit(lambda m:m.update(machine_authority='PUBLISH')))

    def test_wrong_counts(self):
        self.reject(self.manifest_edit(lambda m:m['counts'].update(
            claim_reviews=9)))

    def test_false_privacy(self):
        self.reject(self.manifest_edit(lambda m:m.update(
            privacy='PUBLIC_DOWNLOAD')))

    def test_false_issue(self):
        self.reject(self.manifest_edit(lambda m:m.update(issue=1)))

    def test_false_schema(self):
        self.reject(self.manifest_edit(lambda m:m.update(schema_version=2)))

    def test_false_file_count(self):
        self.reject(self.manifest_edit(lambda m:m.update(
            file_count_including_manifest=100)))

    def test_noncanonical_json_whitespace(self):
        self.reject(self.modify('review-manifest.json',
                                b'  '+self.members()['review-manifest.json']))

    def test_metadata_wrong_timestamp(self):
        self.reject(self.synthetic_zip_with_metadata(date=(1981,1,1,0,0,0)))

    def test_metadata_wrong_permissions(self):
        self.reject(self.synthetic_zip_with_metadata(mode=0o100644<<16))

    def test_metadata_wrong_compression(self):
        self.reject(self.synthetic_zip_with_metadata(method=ZIP_STORED))

    def test_archive_comment(self):
        self.reject(self.synthetic_zip_with_metadata(annotation=b'not private'))

    def test_zip_over_budget(self):
        self.reject(max_plaintext_bytes=len(self.data)-1)

    def test_zip_extreme_limit(self):
        self.reject(max_plaintext_bytes=50)

    def test_duplicate_same_name(self):
        m=self.members()
        out=BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            with ZipFile(out,'w',compression=ZIP_DEFLATED) as z:
                for n in sorted(m):
                    z.writestr(n,m[n])
                z.writestr('index.html',m['index.html'])
        self.reject(out.getvalue())

    def test_false_source_release_state(self):
        self.reject(self.source_edit(lambda m:m.update(release_state='PASS')))

    def test_false_source_authority(self):
        self.reject(self.source_edit(lambda m:m.update(
            machine_authority='SAFETY_APPROVED')))

    def test_source_counts_drift(self):
        self.reject(self.source_edit(lambda m:m['counts'].update(
            global_shared_url_reviews=0)))

# Matrix: every human, safety, publication and reviewer-identity flag is
# forbidden at both archive and frozen R43 source-manifest layers.
for level in ('archive', 'source'):
    for flag in gate.FLAGS:
        def mk(lvl, key):
            def check(self):
                edit = lambda m:m.update({key:True})
                if lvl == 'archive':
                    self.reject(self.manifest_edit(edit))
                else:
                    self.reject(self.source_edit(edit))
            return check
        setattr(Negative,'test_reject_'+level+'_'+flag,mk(level,flag))

if __name__ == '__main__':
    unittest.main()
