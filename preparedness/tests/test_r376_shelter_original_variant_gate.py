"""Adversarial deterministic R376 source-loss custody tests; synthetic data ONLY."""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CODE = Path(__file__).resolve().parents[1] / "tools/r376_shelter_original_variant_gate.py"
spec = importlib.util.spec_from_file_location("r376_gate", CODE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    pins = [{"branch": f"original-branch-{i}", "sha": f"{i + 1:040x}"} for i in range(9)]
    manifest = {"schema_version": 1, "repository": gate.REPO,
                "release_state": "DRAFT_HARD_HOLD", "article_count": 35,
                "conflict_count": 9, "branch_pins": pins, "objects": []}
    body = {"schema_version": 1, "repository": gate.REPO,
            "release_state": "DRAFT_HARD_HOLD", "source_manifest_git_blob": gate.MANIFEST_BLOB,
            "selected_original": None, "body_conflicts": [], "publication_approved": False}
    meta = {"schema_version": 1, "repository": gate.REPO,
            "release_state": "DRAFT_HARD_HOLD", "original_selected_version": None,
            "original_manifest_branch_pins": copy.deepcopy(pins),
            "original_object_conflicts": [], "qualified_safety_approved": False}
    for i, path in enumerate(sorted(gate.REQUIRED)):
        originals = [{"branch": pins[0]["branch"], "sha": f"{100+i*2:040x}"},
                     {"branch": pins[1]["branch"], "sha": f"{101+i*2:040x}"}]
        manifest["objects"].append({"path": path, "variants": originals, "selected_sha": None})
        if path.endswith(".body.html"):
            versions = [{"branch": original["branch"], "sha": original["sha"],
                         "words": 2000 + j*200, "unique_citation_ids": ["legitimate-source-a", "legitimate-source-b"],
                         "blocks_missing_vs_first": 3 if j else 0,
                         "blocks_added_vs_first": 4 if j else 0,
                         "removed_citation_ids": []} for j, original in enumerate(originals)]
            body["body_conflicts"].append({"path": path, "all_original_variant_blobs": originals,
                                            "decision": "NO_AUTO_SELECT_PENDING_HUMAN_SAFETY_SOURCE_REVIEW",
                                            "variants": versions})
        else:
            versions = [{"branch": original["branch"], "sha": original["sha"],
                         "publish": "draft", "safety_state": "pending",
                         "source_use_count": 13+j,
                         "removed_source_use": []} for j, original in enumerate(originals)] if path.endswith(".meta.json") else [
                         {"branch": o["branch"], "sha": o["sha"], "keys": ["sources"]} for o in originals]
            meta["original_object_conflicts"].append({"path": path, "all_original_variants": originals,
                               "decision": "ORIGINAL_VERSIONS_PRESERVED_HUMAN_REVIEW_REQUIRED",
                               "variants": versions})
    return manifest, body, meta


class TestBaseline(unittest.TestCase):
    def test_synthetic_fixture_remains_hard_held(self):
        r = gate.validate(*fixture())
        self.assertEqual(r["status"], "HUMAN_ADJUDICATION_HARD_HOLD")
        self.assertEqual(r["conflicts"], 9)
        self.assertFalse(r["publication_approved"])
        self.assertFalse(r["qualified_safety_approved"])
        self.assertFalse(r["paid_offer_approved"])
        self.assertTrue(r["source_reading_depth_or_citation_review"])

    def test_bad_types_fail_closed(self):
        for bad in (None, [], "", 5, False):
            with self.subTest(bad=repr(bad)):
                self.assertEqual(gate.validate(bad, {}, {})["status"], "INVALID_HARD_HOLD")

    def test_missing_files_cli_exit_two(self):
        p = subprocess.run([sys.executable, str(CODE), "/missing/original-manifest.json",
                            "/missing/body.json", "/missing/meta.json"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)["status"], "INVALID_HARD_HOLD")

    def test_git_blob_format(self):
        raw = b"review-only\n"
        import hashlib
        sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.assertEqual(gate.git_blob(raw), sha)

    def test_synthetic_cli_must_fail_original_source_identity(self):
        with tempfile.TemporaryDirectory() as d:
            files=[]
            for i, x in enumerate(fixture()):
                p=Path(d)/f"{i}.json";p.write_text(json.dumps(x));files.append(str(p))
            p=subprocess.run([sys.executable,str(CODE),*files],capture_output=True,text=True)
            self.assertEqual(p.returncode,2)
            self.assertEqual(json.loads(p.stdout)["status"],"INVALID_HARD_HOLD")
            self.assertTrue(any("fingerprint drift" in z for z in json.loads(p.stdout)["issues"]))


class TestAdversarialMutations(unittest.TestCase):
    """Dynamically registered independent tests below, not just subtest-count inflation."""
    pass


def register(name, mutate):
    def test(self):
        docs=list(fixture())
        mutate(*docs)
        report=gate.validate(*docs)
        self.assertEqual(report["status"], "INVALID_HARD_HOLD", name)
        self.assertTrue(report["issues"])
        self.assertFalse(report["publication_approved"])
    setattr(TestAdversarialMutations, "test_"+name, test)


for docname, index in (("manifest",0),("body",1),("meta",2)):
    for field, value in (("schema_version",2),("repository","not-fv"),
                         ("release_state","APPROVED"),("approval",True),
                         ("publication_approved",True),("qd_pass",True),
                         ("release_ready",True),("commercial_checkout_approved",True)):
        register(docname+"_"+field, lambda a,b,c,index=index,field=field,value=value:
                 [a,b,c][index].__setitem__(field,value))

for field,value in (("article_count",34),("conflict_count",8),
                    ("branch_pins",[]),("branch_pins",[{"branch":"x", "sha":"bad"}]),
                    ("objects",[])):
    register("manifest_"+field+"_"+str(len(str(value))),
             lambda a,b,c,field=field,value=value:a.__setitem__(field,copy.deepcopy(value)))

for field,value in (("source_manifest_git_blob","0"*40),
                    ("selected_original","unauthorized"),("body_conflicts",[])):
    register("body_"+field+"_root",lambda a,b,c,field=field,value=value:b.__setitem__(field,value))

for field,value in (("original_selected_version","followup"),
                    ("original_manifest_branch_pins",[]),("original_object_conflicts",[])):
    register("meta_"+field+"_root",lambda a,b,c,field=field,value=value:c.__setitem__(field,value))

for idx in range(4):
    for mutation in ("lose_body_variant","alter_body_sha","alter_body_branch","select_body",
                     "remove_body_citations","negative_body_words","erase_body_review"):
        def bad(a,b,c,idx=idx,mutation=mutation):
            row=b["body_conflicts"][idx]
            if mutation=="lose_body_variant":row["variants"].pop()
            if mutation=="alter_body_sha":row["variants"][0]["sha"]="f"*40
            if mutation=="alter_body_branch":row["variants"][0]["branch"]="untrusted"
            if mutation=="select_body":row["all_original_variant_blobs"][0]["sha"]="e"*40
            if mutation=="remove_body_citations":row["variants"][0]["unique_citation_ids"]=["a","a"]
            if mutation=="negative_body_words":row["variants"][0]["words"]=-1
            if mutation=="erase_body_review":row["decision"]="APPROVED"
        register(f"body{idx}_"+mutation,bad)

for idx in range(5):
    for mutation in ("lose_meta_version","alter_meta_sha","alter_meta_branch","select_meta","erase_meta_review"):
        def bad(a,b,c,idx=idx,mutation=mutation):
            row=c["original_object_conflicts"][idx]
            if mutation=="lose_meta_version":row["variants"].pop()
            if mutation=="alter_meta_sha":row["variants"][0]["sha"]="f"*40
            if mutation=="alter_meta_branch":row["variants"][0]["branch"]="untrusted"
            if mutation=="select_meta":row["all_original_variants"][0]["sha"]="e"*40
            if mutation=="erase_meta_review":row["decision"]="APPROVED"
        register(f"meta{idx}_"+mutation,bad)

for idx in range(4):
    for mutation in ("approve_publish","approve_safety","empty_source_count"):
        def bad(a,b,c,idx=idx,mutation=mutation):
            row=c["original_object_conflicts"][idx]
            if mutation=="approve_publish":row["variants"][0]["publish"]="publish"
            if mutation=="approve_safety":row["variants"][0]["safety_state"]="approved"
            if mutation=="empty_source_count":row["variants"][0]["source_use_count"]=0
        register(f"meta{idx}_"+mutation,bad)


if __name__=="__main__":unittest.main()
