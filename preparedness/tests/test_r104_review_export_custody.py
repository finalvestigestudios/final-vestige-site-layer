"""R104 private source/citation packet round-trip custody: synthetic/adversarial.

No tests mutate the actual repository. All disk fixtures use OS scratch dirs.
A passing custody test is not a human claim, URL or medical safety review.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "tools"))
import build
import r102_author_scoped_collision_workorder as r102
import r103_collision_offline_reviewer_handoff as r103
import r104_review_export_custody as gate


class RealCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = gate.original_packet()
        cls.payload = gate.create_payload(cls.original)
        cls.manifest = json.loads(cls.payload[gate.MANIFEST])
        cls.lib = build.Library()
        cls.slugs = sorted(cls.lib.articles)

    def test_entire_inventory(self):
        self.assertEqual(len(self.slugs), 36)
        self.assertEqual(self.manifest["original_article_drafts"], 35)
        self.assertEqual(self.manifest["complete_tool_drafts"], 1)
        self.assertEqual(self.manifest["unfinished_tools"], 5)
        self.assertEqual(self.manifest["unreviewed_literal_url_groups"], 30)

    def test_manifest_is_original_parent_bound(self):
        self.assertEqual(self.manifest["r103_export_packet_sha256"],
                         self.original["sha256_seal"])
        self.assertEqual(self.manifest["r102_corpus_sha256"],
                         self.original["r102_corpus_sha256"])

    def test_manifest_seal(self):
        self.assertEqual(self.manifest["sha256_seal"],
                         r102.digest({k:v for k,v in self.manifest.items()
                                      if k != "sha256_seal"}))

    def test_manifest_is_not_an_attestation(self):
        self.assertIs(self.manifest["sha256_is_not_a_signature_or_human_attestation"],True)
        self.assertIs(self.manifest["may_merge"],False)
        self.assertIs(self.manifest["may_publish"],False)
        for field in ("human_source_review","human_claim_review",
                      "qualified_safety_review","independent_QD",
                      "browser_and_wordpress_QA"):
            self.assertEqual(self.manifest[field],"NOT_REVIEWED")

    def test_file_inventory_exact(self):
        self.assertEqual(len(self.payload),5)
        self.assertEqual(set(self.payload),
                         {key for key,_ in gate.EXPORTS} | {gate.MANIFEST})
        self.assertEqual([x["name"] for x in self.manifest["exports"]],
                         [name for name,_ in gate.EXPORTS])

    def test_every_export_byte_hash_exact(self):
        for row in self.manifest["exports"]:
            binary=self.payload[row["name"]]
            self.assertEqual(row["byte_count"],len(binary))
            self.assertEqual(row["sha256"],hashlib.sha256(binary).hexdigest())

    def test_exact_csv_matches_parent(self):
        for name,kind in gate.EXPORTS[1:3]:
            self.assertEqual(self.payload[name],
                             r103.csv_text(self.original,kind).encode("utf-8"))

    def test_html_static_source_and_review_cues(self):
        h=self.payload[gate.EXPORTS[0][0]].decode("utf-8")
        self.assertEqual(h.count("<section>"),30)
        self.assertNotIn("<script",h)
        self.assertNotIn("<a href",h)
        self.assertIn("PRIVATE DRAFT",h)
        self.assertIn("No source or claim has been approved",h)

    def test_repeat_deterministic_generation(self):
        self.assertEqual(self.payload,gate.create_payload(self.original))

    def test_source_scopes_original_one_to_one(self):
        self.assertEqual(self.manifest["source_variant_rows"],
                         self.original["variant_rows"])
        self.assertEqual(self.manifest["collision_citation_occurrences"],
                         self.original["collision_citation_occurrences"])

    def test_groups_are_original_fingerprints(self):
        self.assertEqual(len(self.manifest["groups"]),30)
        for group, exported in zip(self.original["groups"],self.manifest["groups"]):
            self.assertEqual(exported["group_sha256"] if "group_sha256" in exported
                             else exported["original_group_sha256"],
                             group["group_sha256"])
            self.assertEqual(exported["citation_occurrences"],
                             group["citation_occurrences"])

    def test_offline_emit_then_recheck_exact(self):
        with tempfile.TemporaryDirectory(prefix="fv-r104-custody-") as td:
            result=gate.emit_dir(td,self.payload)
            self.assertEqual(result["files"],5)
            self.assertEqual(gate.verify_dir(td,self.payload),result)

    def test_recheck_from_independent_replay(self):
        with tempfile.TemporaryDirectory(prefix="fv-r104-replay-") as td:
            gate.emit_dir(td,self.payload)
            result=gate.verify_dir(td)
            self.assertEqual(result["groups_unreviewed"],30)
            self.assertFalse(result["may_publish"])


def group_check(i):
    def test(self):
        g=self.original["groups"][i]
        m=self.manifest["groups"][i]
        self.assertEqual(m["group_number"],i+1)
        self.assertEqual(m["original_group_sha256"],g["group_sha256"])
        self.assertEqual(m["literal_url_sha256"],
                         r102.digest(g["literal_url_NOT_VERIFIED"]))
        self.assertEqual(m["variant_count"],g["variant_count"])
        self.assertEqual(m["citation_occurrences"],g["citation_occurrences"])
        self.assertEqual(g["human_review"],"NOT_REVIEWED")
        self.assertFalse(g["may_publish"])
    return test

for _i in range(30):
    setattr(RealCorpus,"test_literal_source_group_%02d"%(_i+1),group_check(_i))


def article_check(i):
    def test(self):
        slug=self.slugs[i]
        meta=self.lib.articles[slug]
        self.assertEqual(meta["status"]["publish"],"draft")
        self.assertEqual(self.lib.article_origins.get(slug) is not None,True)
        uses=[r for g in self.original["groups"] for r in g["rows"]
              if r["article_slug"]==slug]
        self.assertTrue(all(r["article_origin"]==self.lib.article_origins[slug]
                            for r in uses))
        self.assertTrue(all(r["human_claim_review"]=="NOT_REVIEWED" for r in uses))
    return test

for _i in range(36):
    setattr(RealCorpus,"test_original_author_draft_%02d"%(_i+1),article_check(_i))


class Adversarial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=gate.original_packet()
        cls.payload=gate.create_payload(cls.original)

    def setUp(self):
        self.td=tempfile.TemporaryDirectory(prefix="fv-r104-adversarial-")
        self.addCleanup(self.td.cleanup)
        gate.emit_dir(self.td.name,self.payload)
        self.folder=Path(self.td.name)

    def corrupt(self,name,change):
        path=self.folder/name
        path.write_bytes(change(path.read_bytes()))
        with self.assertRaises(gate.Gate):
            gate.verify_dir(str(self.folder),self.payload)

    def test_reject_one_changed_source_byte(self):
        self.corrupt(gate.EXPORTS[1][0],
                     lambda b:b.replace(b"NOT_REVIEWED",b"YES_REVIEWED",1))

    def test_reject_reordered_citation_csv(self):
        self.corrupt(gate.EXPORTS[2][0],
                     lambda b:b.replace(b"\r\n",b"\n",1))

    def test_reject_html_warning_removed(self):
        self.corrupt(gate.EXPORTS[0][0],
                     lambda b:b.replace(b"PRIVATE DRAFT",b"PRIVATE DRAFT".replace(b"DRAFT",b"FINAL"),1))

    def test_reject_summary_promotion(self):
        self.corrupt(gate.EXPORTS[3][0],
                     lambda b:b.replace(b'"may_publish": false',
                                         b'"may_publish": true',1))

    def test_reject_self_resealed_manifest(self):
        def change(b):
            x=json.loads(b)
            x["human_source_review"]="APPROVED"
            x["sha256_seal"]=r102.digest({k:v for k,v in x.items() if k!="sha256_seal"})
            return (r102.canonical(x)+"\n").encode("utf-8")
        self.corrupt(gate.MANIFEST,change)

    def test_reject_manifest_only_truncation(self):
        self.corrupt(gate.MANIFEST,lambda b:b[:-1])

    def test_reject_extra_tracking_file(self):
        (self.folder/"tracking.js").write_text("console.log('tracking')",encoding="utf-8")
        with self.assertRaises(gate.Gate):
            gate.verify_dir(str(self.folder),self.payload)

    def test_reject_missing_html(self):
        (self.folder/gate.EXPORTS[0][0]).unlink()
        with self.assertRaises(gate.Gate):
            gate.verify_dir(str(self.folder),self.payload)

    def test_reject_duplicate_citation_export(self):
        path=self.folder/gate.EXPORTS[2][0]
        path.write_bytes(path.read_bytes()+b"\r\n")
        with self.assertRaises(gate.Gate):
            gate.verify_dir(str(self.folder),self.payload)

    def test_reject_renamed_file(self):
        old=self.folder/gate.EXPORTS[2][0]
        old.rename(self.folder/"citations-verified.csv")
        with self.assertRaises(gate.Gate):
            gate.verify_dir(str(self.folder),self.payload)

    def test_reject_symlink_file(self):
        real=self.folder/gate.EXPORTS[1][0]
        other=self.folder/"saved"
        real.rename(other)
        try:
            real.symlink_to(other)
        except (OSError,NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(gate.Gate):
            gate.verify_dir(str(self.folder),self.payload)

    def test_reject_symlink_directory(self):
        link=self.folder.parent/(self.folder.name+"-link")
        try:
            link.symlink_to(self.folder,target_is_directory=True)
        except (OSError,NotImplementedError):
            self.skipTest("symlinks unavailable")
        try:
            with self.assertRaises(gate.Gate):
                gate.verify_dir(str(link),self.payload)
        finally:
            link.unlink()

    def test_emit_never_overwrites(self):
        with self.assertRaises(gate.Gate):
            gate.emit_dir(str(self.folder),self.payload)

    def test_refuse_export_inside_repo(self):
        with self.assertRaises(gate.Gate):
            gate.safe_directory(str(ROOT/"tests"))

    def test_refuse_nonexistent_directory(self):
        with self.assertRaises(gate.Gate):
            gate.verify_dir(str(self.folder/"not-found"),self.payload)

    def test_release_flag_forgery(self):
        bad=copy.deepcopy(self.original)
        bad["may_publish"]=True
        bad["sha256_seal"]=r102.digest({k:v for k,v in bad.items() if k!="sha256_seal"})
        with self.assertRaises(gate.Gate):
            gate.create_payload(bad)

    def test_human_source_review_promotion(self):
        bad=copy.deepcopy(self.original)
        bad["human_source_and_claim_review"]="APPROVED"
        bad["sha256_seal"]=r102.digest({k:v for k,v in bad.items() if k!="sha256_seal"})
        with self.assertRaises(gate.Gate):
            gate.create_payload(bad)

    def test_independent_qd_promotion(self):
        bad=copy.deepcopy(self.original)
        bad["independent_QD"]="PASS"
        bad["sha256_seal"]=r102.digest({k:v for k,v in bad.items() if k!="sha256_seal"})
        with self.assertRaises(gate.Gate):
            gate.create_payload(bad)

    def test_resealed_original_source_record_forgery(self):
        bad=copy.deepcopy(self.original)
        row=bad["groups"][0]["rows"][0]
        row["source_or_context_original_json_NOT_VERIFIED"] = '{"supports":"approved"}'
        bad["sha256_seal"]=r102.digest({k:v for k,v in bad.items() if k!="sha256_seal"})
        with self.assertRaises(gate.Gate):
            gate.create_payload(bad)

    def test_resealed_citation_reading_scope_forgery(self):
        bad=copy.deepcopy(self.original)
        row=next(r for g in bad["groups"] for r in g["rows"]
                 if r["record_kind"]=="CITATION_OCCURRENCE")
        row["author_source_use_or_recorded_support"]="invented claim support"
        bad["sha256_seal"]=r102.digest({k:v for k,v in bad.items() if k!="sha256_seal"})
        with self.assertRaises(gate.Gate):
            gate.create_payload(bad)

    def test_group_count_change(self):
        bad=copy.deepcopy(self.original)
        bad["literal_url_groups"]=29
        bad["sha256_seal"]=r102.digest({k:v for k,v in bad.items() if k!="sha256_seal"})
        with self.assertRaises(gate.Gate):
            gate.create_payload(bad)


if __name__=="__main__":
    unittest.main()
