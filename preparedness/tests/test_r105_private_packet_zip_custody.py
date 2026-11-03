"""R105 private transport adversarial + exact 35-article/one-tool evidence tests.

No working-tree writes; disk fixtures only in TemporaryDirectory. A pass
is ZIP custody, never independent claim, citation or qualified safety approval.
"""
from __future__ import annotations

import copy
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import r104_review_export_custody as r104
import r105_private_packet_zip_custody as gate


class Corpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.payload = gate.original_payload()
        cls.archive = gate.encode_zip(cls.payload)
        cls.manifest = json.loads(cls.payload[r104.MANIFEST])
        cls.slugs = sorted(cls.lib.articles)

    def test_all_original_drafts(self):
        self.assertEqual(len(self.slugs), 36)
        self.assertEqual(self.manifest["original_article_drafts"], 35)
        self.assertEqual(self.manifest["complete_tool_drafts"], 1)
        self.assertEqual(self.manifest["unfinished_tools"], 5)

    def test_source_crosswalk_scope_unchanged(self):
        self.assertEqual(self.manifest["unreviewed_literal_url_groups"], 30)
        self.assertEqual(len(self.manifest["groups"]), 30)
        self.assertGreater(self.manifest["source_variant_rows"], 30)
        self.assertGreater(self.manifest["collision_citation_occurrences"], 0)

    def test_parent_packets_verbatim(self):
        self.assertEqual(tuple(self.payload), gate.NAMES)
        self.assertEqual(self.payload, r104.create_payload(r104.original_packet()))

    def test_exact_deterministic_archive_bytes(self):
        self.assertEqual(self.archive, gate.encode_zip(self.payload))

    def test_independent_replay_archive_bytes(self):
        self.assertEqual(self.archive, gate.original_archive())

    def test_header_trailer_and_all_members(self):
        with zipfile.ZipFile(io.BytesIO(self.archive), "r") as zf:
            self.assertEqual(tuple(zf.namelist()), gate.NAMES)
            self.assertEqual(zf.comment, b"")
            for info in zf.infolist():
                self.assertEqual(info.date_time, gate.DOS_TIME)
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(info.external_attr, gate.MODE)
                self.assertEqual(info.flag_bits, 0)
                self.assertEqual(info.extra, b"")
                self.assertEqual(info.comment, b"")
                self.assertEqual(zf.read(info), self.payload[info.filename])

    def test_explicit_machine_hold(self):
        out = gate.verify_bytes(self.archive, expected=self.archive,
                                expected_payload=self.payload)
        self.assertFalse(out["may_merge"])
        self.assertFalse(out["may_publish"])
        self.assertEqual(out["release_state"], "HOLD")
        self.assertEqual(out["human_source_claim_safety_and_QD_review"], "NOT_REVIEWED")
        self.assertEqual(out["source_url_groups_pending_human_review"], 30)

    def test_compatible_dry_check(self):
        self.assertEqual(gate.verify_bytes(self.archive)["entries"], 5)

    def test_scratch_only_emit_verify(self):
        with tempfile.TemporaryDirectory(prefix="fv-r105-private-") as td:
            report = gate.emit_dir(td)
            archive = Path(td) / gate.ZIP_NAME
            self.assertEqual(report["archive_sha256"], gate.digest(self.archive))
            self.assertEqual(archive.read_bytes(), self.archive)
            self.assertEqual(gate.verify_file(str(archive)), report)

    def test_never_clobber_scratch(self):
        with tempfile.TemporaryDirectory(prefix="fv-r105-no-clobber-") as td:
            gate.emit_dir(td)
            with self.assertRaises(gate.Gate):
                gate.emit_dir(td)

    def test_untrusted_location_in_repo_rejected(self):
        with self.assertRaises(r104.Gate):
            gate.emit_dir(str(ROOT / "tests"))

    def test_reject_wrong_name_and_missing_path(self):
        with tempfile.TemporaryDirectory(prefix="fv-r105-rename-") as td:
            path = Path(td) / "claimed-approved.zip"
            path.write_bytes(self.archive)
            with self.assertRaises(gate.Gate):
                gate.verify_file(str(path))
            with self.assertRaises(gate.Gate):
                gate.verify_file(str(Path(td) / gate.ZIP_NAME))

    def test_symlink_to_export_rejected(self):
        with tempfile.TemporaryDirectory(prefix="fv-r105-link-") as td:
            original = Path(td) / "real.zip"
            original.write_bytes(self.archive)
            alias = Path(td) / gate.ZIP_NAME
            try:
                alias.symlink_to(original)
            except (OSError, NotImplementedError):
                self.skipTest("no symlink support")
            with self.assertRaises(gate.Gate):
                gate.verify_file(str(alias))


def group_case(index):
    def test(self):
        record = self.manifest["groups"][index]
        self.assertEqual(record["group_number"], index + 1)
        self.assertEqual(len(record["original_group_sha256"]), 64)
        self.assertGreaterEqual(record["variant_count"], 2)
        self.assertGreaterEqual(record["citation_occurrences"], 1)
        self.assertFalse(self.manifest["may_publish"])
        self.assertEqual(self.manifest["human_source_review"], "NOT_REVIEWED")
    return test


def article_case(index):
    def test(self):
        slug = self.slugs[index]
        article = self.lib.articles[slug]
        self.assertEqual(article["status"]["publish"], "draft")
        self.assertIn(slug, self.lib.article_origins)
        self.assertFalse(self.manifest["may_publish"])
    return test


for _i in range(30):
    setattr(Corpus, "test_original_collision_%02d" % (_i + 1), group_case(_i))
for _i in range(36):
    setattr(Corpus, "test_original_article_or_tool_%02d" % (_i + 1),
            article_case(_i))


class Adversarial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = gate.original_payload()
        cls.original = gate.encode_zip(cls.payload)

    def reject(self, altered: bytes):
        with self.assertRaises(gate.Gate):
            gate.verify_bytes(altered, expected=self.original,
                              expected_payload=self.payload)

    def rebuild(self, change_name=None, change_meta=None, change_data=None,
                reverse=False, omit_last=False, duplicate=False, comment=b""):
        """Generate intentionally untrusted ZIPs using the public ZIP format."""
        buf = io.BytesIO()
        names = list(gate.NAMES)
        if reverse:
            names.reverse()
        if omit_last:
            names.pop()
        if duplicate:
            names.append(names[0])
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED,
                             allowZip64=False) as zf:
            for i, name in enumerate(names):
                info = zipfile.ZipInfo(change_name if change_name and i == 0
                                       else name, gate.DOS_TIME)
                info.create_system = 3
                info.external_attr = gate.MODE
                info.compress_type = zipfile.ZIP_STORED
                if change_meta:
                    change_meta(info, i)
                raw = self.payload[name]
                if change_data and i == 0:
                    raw = change_data(raw)
                zf.writestr(info, raw)
            zf.comment = comment
        return buf.getvalue()

    def test_refuse_approval_text_in_one_entry(self):
        self.reject(self.rebuild(change_data=lambda b:
            b.replace(b"PRIVATE DRAFT", b"PUBLIC READY ", 1)))

    def test_refuse_rewritten_original_csv_even_with_valid_crc(self):
        name = gate.NAMES[1]
        altered = copy.deepcopy(self.payload)
        altered[name] = altered[name].replace(b"NOT_REVIEWED", b"APPROVED____", 1)
        self.reject(gate.encode_zip(altered))

    def test_refuse_resealed_manifest_approval(self):
        altered = copy.deepcopy(self.payload)
        record = json.loads(altered[r104.MANIFEST])
        record["human_claim_review"] = "APPROVED"
        altered[r104.MANIFEST] = json.dumps(record, sort_keys=True).encode()
        self.reject(gate.encode_zip(altered))

    def test_refuse_missing_entry(self):
        self.reject(self.rebuild(omit_last=True))

    def test_refuse_repeated_entry(self):
        self.reject(self.rebuild(duplicate=True))

    def test_refuse_reordered_evidence(self):
        self.reject(self.rebuild(reverse=True))

    def test_refuse_absolute_path(self):
        self.reject(self.rebuild(change_name="/tmp/claim-approved.html"))

    def test_refuse_zip_slip(self):
        self.reject(self.rebuild(change_name="../../README.md"))

    def test_refuse_subdirectory_instead_of_flat_evidence(self):
        self.reject(self.rebuild(change_name="records/" + gate.NAMES[0]))

    def test_refuse_renamed_verified_claim(self):
        self.reject(self.rebuild(change_name="reviewed-source-claims.html"))

    def test_refuse_altered_timestamp(self):
        self.reject(self.rebuild(change_meta=lambda info, i:
            setattr(info, "date_time", (2026, 11, 3, 0, 0, 0)) if i == 0 else None))

    def test_refuse_unix_executable_bit(self):
        self.reject(self.rebuild(change_meta=lambda info, i:
            setattr(info, "external_attr", (stat.S_IFREG | 0o755) << 16)
            if i == 0 else None))

    def test_refuse_unix_symlink(self):
        self.reject(self.rebuild(change_meta=lambda info, i:
            setattr(info, "external_attr", (stat.S_IFLNK | 0o777) << 16)
            if i == 0 else None))

    def test_refuse_compressed_entry(self):
        self.reject(self.rebuild(change_meta=lambda info, i:
            setattr(info, "compress_type", zipfile.ZIP_DEFLATED)
            if i == 0 else None))

    def test_refuse_zip_comment(self):
        self.reject(self.rebuild(comment=b"SOURCES VERIFIED BY EDITOR"))

    def test_refuse_entry_comment(self):
        self.reject(self.rebuild(change_meta=lambda info, i:
            setattr(info, "comment", b"Approved!") if i == 0 else None))

    def test_refuse_entry_extra_header(self):
        self.reject(self.rebuild(change_meta=lambda info, i:
            setattr(info, "extra", b"\x0a\x00\x00\x00") if i == 0 else None))

    def test_refuse_nonzip_bytes(self):
        self.reject(b"NOT A ZIP")

    def test_refuse_truncated_zip(self):
        self.reject(self.original[:-11])

    def test_refuse_zip_with_trailing_payload(self):
        self.reject(self.original + b"<!-- concealed release approval -->")

    def test_refuse_zip_with_preamble(self):
        self.reject(b"APPROVED\n" + self.original)

    def test_refuse_zip_with_modified_first_byte(self):
        self.reject(b"A" + self.original[1:])

    def test_refuse_empty_zip(self):
        self.reject(b"")

    def test_refuse_oversized_blob_before_parsing(self):
        # In-memory check only; no giant fixture allocation.
        self.reject(b"0" * (gate.MAX_ARCHIVE_BYTES + 1))

    def test_bad_payload_filename_order(self):
        wrong = dict(reversed(list(self.payload.items())))
        with self.assertRaises(gate.Gate):
            gate.encode_zip(wrong)

    def test_bad_payload_missing_manifest(self):
        altered = dict(self.payload)
        del altered[r104.MANIFEST]
        with self.assertRaises(gate.Gate):
            gate.encode_zip(altered)

    def test_bad_payload_new_tracking_entry(self):
        altered = dict(self.payload)
        altered["tracker.js"] = b"fetch('https://example.org')"
        with self.assertRaises(gate.Gate):
            gate.encode_zip(altered)


def single_byte_attack(index):
    def test(self):
        location = (index * max(1, len(self.original) // 53))
        location = min(location, len(self.original) - 1)
        altered = bytearray(self.original)
        altered[location] ^= 0x01
        self.reject(bytes(altered))
    return test


for _i in range(50):
    setattr(Adversarial, "test_one_byte_archive_mutation_%02d" % (_i + 1),
            single_byte_attack(_i))


if __name__ == "__main__":
    unittest.main()
