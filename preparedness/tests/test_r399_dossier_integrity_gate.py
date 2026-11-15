"""R399 offline synthetic parity attacks (not source inspection or QD)."""
from __future__ import annotations
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import r399_dossier_integrity_gate as g

FIELDS=("branch","source_blob","fragment","publisher","kind","url","verified_on","human_link_check","supports_exact","reading_scope_notes_exact")

def fixture():
    sources=[]
    for i in range(5):
        variants=[]
        for j in range(2):
            variants.append({"branch":f"claude/prep-{i}-{j}","source_blob":f"{i+1}{j+1}"*20,
               "fragment":"preparedness/sources/fragments/shelter.json","publisher":"Official agency",
               "kind":"regulator","url":f"https://example.org/source-{i}","verified_on":"2026-11-15",
               "human_link_check":False,"supports_exact":f"Complete original claim {i}-{j}\nScope limitation line",
               "reading_scope_notes_exact":f"Read full source {i}-{j}; still unverified"})
        sources.append({"source_id":f"source-{i}","decision":"HUMAN_REVIEW_REQUIRED","selected_record":None,"variants":variants})
    forks=[]
    for i in range(9):
        v=[{"branch":f"claude/prep-shelter-{j}","git_blob_sha":f"{i+1}{j+1}"*20,"byte_length":2000+i+j} for j in range(3)]
        forks.append({"path":f"preparedness/content/articles/hold-{i}.body.html","decision":"HUMAN_REVIEW_REQUIRED","selected_sha":None,"variants":v})
    d={"publication_approved":False,"qualified_safety_approved":False,"merchant_offer_verified":False,
       "source_evidence_disputes":sources,"original_fork_disputes":forks,
       "shared_exact_url_review_groups":[{"url":f"https://example.org/alias-{i}"} for i in range(17)],
       "all_original_source_id_crosswalk":[{"source_id":f"cross-{i}","variants":[{}]*(2 if i<77 else 1)} for i in range(203)],
       "original_articles":[{"slug":f"article-{i}"} for i in range(35)]}
    raw=json.dumps(d,sort_keys=True,ensure_ascii=False).encode()
    mark=["# Dossier HARD HOLD","No source or manuscript selected","Qualified privacy review outstanding",g.blob(raw)]
    for s in sources:
        mark.append("### "+s["source_id"])
        for v in s["variants"]:
            mark.append("#### Original source candidate 1")
            mark.extend(g.literal(v[k]) for k in FIELDS)
    for f in forks:
        mark.append("### "+f["path"])
        for v in f["variants"]:
            mark.append("| `"+v["branch"]+"` | `"+v["git_blob_sha"]+"` | "+str(v["byte_length"])+" |")
    return d,raw,"\n".join(mark)


class DossierGateTests(unittest.TestCase):
    def setUp(self):
        self.d,self.raw,self.md=fixture()

    def audit(self,d=None,md=None,raw=None,pin=None):
        d=self.d if d is None else d
        md=self.md if md is None else md
        raw=self.raw if raw is None else raw
        return g.inspect(d,md,raw,pin=g.blob(self.raw) if pin is None else pin)

    def rejects(self,result,marker):
        self.assertEqual(result["integrity"],"FAIL")
        self.assertTrue(any(marker in k for k in result["failures"]),result["failures"])
        self.assertEqual(result["release"],g.HOLD)

    def test_baseline_integrity_pass_is_always_hold(self):
        r=self.audit()
        self.assertEqual(r["integrity"],"PASS")
        self.assertEqual(r["release"],g.HOLD)
        self.assertEqual((r["source_cases"],r["fork_cases"]),(5,9))

    def test_tampered_git_raw(self):
        self.rejects(self.audit(raw=self.raw+b" "),"docket_git_blob_mismatch")

    def test_docket_mismatch_even_if_digest_pin_changed(self):
        d=copy.deepcopy(self.d);d["source_evidence_disputes"][0]["variants"][0]["supports_exact"]="fake"
        self.rejects(self.audit(d=d),"docket_decoding_mismatch")

    def test_removed_hold_banner(self):
        self.rejects(self.audit(md=self.md.replace("No source or manuscript selected","none selected")),"hold_banner_missing")

    def test_missing_original_blob_marker(self):
        self.rejects(self.audit(md=self.md.replace(g.blob(self.raw),"not-available")),"original_blob_marker_missing")

    def test_wrong_pin(self):
        self.rejects(self.audit(pin="0"*40),"docket_git_blob_mismatch")

    def test_missing_one_candidate_heading(self):
        self.rejects(self.audit(md=self.md.replace("#### Original source candidate 1","candidate",1)),"source_candidate_count")

    def test_missing_fork_rows(self):
        self.rejects(self.audit(md=self.md.replace("| `claude/prep-shelter-0", "| `not-a-shelter-branch",20)),"fork_provenance_missing")

    def test_missing_qualified_review(self):
        self.rejects(self.audit(md=self.md.replace("Qualified privacy", "Open private")),"qualified_review_not_visible")

    def test_incorrect_source_inventory(self):
        d=copy.deepcopy(self.d);d["all_original_source_id_crosswalk"].pop()
        self.rejects(self.audit(d=d),"source_inventory_changed")

    def test_incorrect_article_inventory(self):
        d=copy.deepcopy(self.d);d["original_articles"].pop()
        self.rejects(self.audit(d=d),"article_inventory_changed")

    def test_incorrect_alias_inventory(self):
        d=copy.deepcopy(self.d);d["shared_exact_url_review_groups"].pop()
        self.rejects(self.audit(d=d),"case_counts_changed")

    def test_missing_source_dispute(self):
        d=copy.deepcopy(self.d);d["source_evidence_disputes"].pop()
        self.rejects(self.audit(d=d),"case_counts_changed")

    def test_missing_fork_dispute(self):
        d=copy.deepcopy(self.d);d["original_fork_disputes"].pop()
        self.rejects(self.audit(d=d),"case_counts_changed")

    def test_source_auto_selection(self):
        d=copy.deepcopy(self.d);d["source_evidence_disputes"][0]["selected_record"]="unapproved"
        self.rejects(self.audit(d=d),"source_auto_selected")

    def test_fork_auto_selection(self):
        d=copy.deepcopy(self.d);d["original_fork_disputes"][0]["selected_sha"]="1"*40
        self.rejects(self.audit(d=d),"fork_auto_selected")

    def test_human_link_check_is_never_approved(self):
        d=copy.deepcopy(self.d);d["source_evidence_disputes"][0]["variants"][0]["human_link_check"]=True
        self.rejects(self.audit(d=d),"false_human_link_check")

    def test_release_flags_fail(self):
        for key in ("publication_approved","qualified_safety_approved","merchant_offer_verified"):
            with self.subTest(key=key):
                d=copy.deepcopy(self.d);d[key]=True
                self.rejects(self.audit(d=d),"release_state_changed")

    def test_full_original_reading_note_required(self):
        phrase=self.d["source_evidence_disputes"][0]["variants"][0]["reading_scope_notes_exact"]
        self.rejects(self.audit(md=self.md.replace(g.literal(phrase),"    shortened text")),"source_field_missing")

    def test_multiline_original_support_required(self):
        phrase=self.d["source_evidence_disputes"][0]["variants"][0]["supports_exact"]
        self.rejects(self.audit(md=self.md.replace(g.literal(phrase),"    shortened text")),"source_field_missing")

    def test_cli_missing_inputs_exit_two(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(g.main(["--docket",t+"/none.json","--dossier",t+"/none.md"]),2)

    def test_cli_synthetic_never_reports_approval(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            (root/"docket.json").write_bytes(self.raw)
            (root/"dossier.md").write_text(self.md)
            self.assertEqual(g.main(["--docket",str(root/"docket.json"),"--dossier",str(root/"dossier.md")]),2)


for _i,_field in enumerate(FIELDS):
    for _j in range(2):
        def make(field=_field,j=_j):
            def test(self):
                v=self.d["source_evidence_disputes"][0]["variants"][j]
                s=g.literal(v[field]);self.rejects(self.audit(md=self.md.replace(s,"    TAMPERED",1)),"source_field_missing")
            return test
        setattr(DossierGateTests,f"test_source_field_{_i}_{_j}",make())

for _i in range(9):
    def make(i=_i):
        def test(self):
            f=self.d["original_fork_disputes"][i]
            row=f["variants"][0]
            line="| `"+row["branch"]+"` | `"+row["git_blob_sha"]+"` | "+str(row["byte_length"])+" |"
            self.rejects(self.audit(md=self.md.replace(line,"| TAMPERED |",1)),"fork_provenance_missing")
        return test
    setattr(DossierGateTests,f"test_fork_provenance_{_i}",make())

for _i in range(5):
    def make(i=_i):
        def test(self):
            sid=self.d["source_evidence_disputes"][i]["source_id"]
            self.rejects(self.audit(md=self.md.replace("### "+sid,"### TAMPERED",1)),"source_heading")
        return test
    setattr(DossierGateTests,f"test_source_heading_{_i}",make())

if __name__=="__main__":unittest.main()
