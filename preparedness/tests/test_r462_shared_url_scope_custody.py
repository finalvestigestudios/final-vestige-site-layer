"""R462 synthetic/adversarial source-scope mutation suite. Never a safety or release PASS."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "tools" / "r462_shared_url_scope_custody.py"
spec = importlib.util.spec_from_file_location("r462", PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture():
    a = {"id":"a","url":"https://agency.example/plan","publisher":"Agency A",
         "supports":"first half","verified_on":"2026-10-01"}
    b = {"id":"b","url":"https://agency.example/plan","publisher":"Agency B",
         "supports":"second half","verified_on":"2026-10-02"}
    c = {"id":"c","url":"https://agency.example/other","publisher":"Agency C",
         "supports":"third section","verified_on":None}
    sources = {"preparedness/sources/register.json":[a,c],
               "preparedness/sources/fragments/start.json":[b]}
    roster = [{"origin":"base","path":"preparedness/sources/register.json",
               "git_blob_sha":"a"*40,"count":2},
              {"origin":"start","path":"preparedness/sources/fragments/start.json",
               "git_blob_sha":"b"*40,"count":1}]
    identities = [{"origin":"base","id":"a","row_index":0},
                  {"origin":"start","id":"b","row_index":0}]
    variants = [{"origin":"base","source_file":roster[0]["path"],
                 "row_index":0,"source":copy.deepcopy(a)},
                {"origin":"start","source_file":roster[1]["path"],
                 "row_index":0,"source":copy.deepcopy(b)}]
    group = {"url":a["url"],"canonical_url":a["url"],"review_status":m.REVIEW,
             "reviewer":None,"reviewed_on":None,
             "identities":identities,"variants":variants}
    crosswalk = {"schema_version":1,
                 "status":"DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED",
                 "source_files":roster,"raw_source_rows":3,"unique_source_urls":2,
                 "duplicate_url_groups":1,"groups":[group]}
    return crosswalk,sources

class TestCrosswalk(unittest.TestCase):
    def test_valid_fixture_remains_hard_hold(self):
        c,s=fixture();out=m.audit(c,s,expected=(3,2,1))
        self.assertEqual((out["different_id_groups"],out["different_scope_groups"]), (1,1))
        self.assertFalse(out["may_publish"])
        self.assertFalse(out["qualified_qd_pass"])
    def test_original_row_order_independent(self):
        c,s=fixture()
        c["groups"][0]["identities"].reverse()
        c["groups"][0]["variants"].reverse()
        self.assertEqual(m.audit(c,s,expected=(3,2,1))["shared_url_review_groups"],1)
    def test_scope_mutation_rejected(self):
        c,s=fixture();c["groups"][0]["variants"][0]["source"]["supports"]="different"
        with self.assertRaises(m.CrosswalkHold):
            m.audit(c,s,expected=(3,2,1))
    def test_nine_origin_pin_rejected_on_drift(self):
        c,s=fixture()
        sn={"repository":m.REPO,"qualified_qd_pass":False,"release_state":m.HOLD,
            "candidate":{"sources":{"register.json":"a"*40,
              "fragments/start.json":"b"*40},"articles":{str(i):{} for i in range(35)}},
            "origins":{str(i):{} for i in range(9)}}
        self.assertEqual(m.audit(c,s,sn,expected=(3,2,1))["state"],"URL_SCOPE_REVIEW_HARD_HOLD")
        sn["candidate"]["sources"]["register.json"]="c"*40
        with self.assertRaises(m.CrosswalkHold):
            m.audit(c,s,sn,expected=(3,2,1))
    def test_json_duplicate_keys_rejected(self):
        with self.assertRaises(m.CrosswalkHold):
            json.loads('{"a":1,"a":2}',object_pairs_hook=m.no_duplicates)
    def test_git_hash_is_real_blob_sha(self):
        self.assertEqual(m.git_blob(b"hello\n"),"ce013625030ba8dba906f756967f9e9ca394464a")
    def test_pinned_read_does_not_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/"x").write_text("{}")
            (root/"y").symlink_to(root/"x")
            with self.assertRaises(m.CrosswalkHold):
                m.read_pinned(root,"y",m.git_blob(b"{}"))
    def test_pinned_read_rejects_other_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/"x").write_text("{}")
            with self.assertRaises(m.CrosswalkHold):
                m.read_pinned(root,"x","0"*40)

def mutate(index,c,s):
    g=c["groups"][0]
    mutations=[
        lambda:g.update(url="https://other.example"),
        lambda:g.update(canonical_url="https://other.example"),
        lambda:g.update(review_status="approved"),
        lambda:g.update(reviewer="Anon"),
        lambda:g.update(reviewed_on="2026-11-18"),
        lambda:g["identities"].pop(),
        lambda:g["identities"][0].update(id="b"),
        lambda:g["identities"][0].update(origin="start"),
        lambda:g["identities"][0].update(row_index=1),
        lambda:g["variants"].pop(),
        lambda:g["variants"][0].update(origin="start"),
        lambda:g["variants"][0].update(row_index=1),
        lambda:g["variants"][0].update(source_file="wrong.json"),
        lambda:g["variants"][0]["source"].update(supports="unread"),
        lambda:g["variants"][0]["source"].update(publisher="fabricated"),
        lambda:g["variants"][0]["source"].update(verified_on="2026-11-18"),
        lambda:g["variants"][0]["source"].update(url="https://other.example"),
        lambda:g["variants"][0]["source"].update(id="b"),
        lambda:c.update(groups=[]),
        lambda:c["groups"].append(copy.deepcopy(g)),
        lambda:c.update(raw_source_rows=4),
        lambda:c.update(unique_source_urls=3),
        lambda:c.update(duplicate_url_groups=2),
        lambda:c.update(status="QD_PASS"),
        lambda:c.update(schema_version=2),
        lambda:c.update(source_files=[]),
        lambda:c["source_files"].pop(),
        lambda:c["source_files"][0].update(origin="start"),
        lambda:c["source_files"][0].update(count=3),
        lambda:c["source_files"][0].update(path="missing.json"),
        lambda:c["source_files"][0].update(extra=True),
        lambda:c["source_files"].append(copy.deepcopy(c["source_files"][0])),
        lambda:s[c["source_files"][0]["path"]].pop(),
        lambda:s[c["source_files"][0]["path"]][0].update(url="https://changed.example"),
        lambda:s[c["source_files"][0]["path"]][0].update(id="d"),
        lambda:s[c["source_files"][0]["path"]][0].update(supports="unread"),
        lambda:s[c["source_files"][0]["path"]][0].update(publisher="fabricated"),
        lambda:s[c["source_files"][0]["path"]][0].update(verified_on=None),
        lambda:s[c["source_files"][1]["path"]][0].update(url="https://changed.example"),
        lambda:s[c["source_files"][1]["path"]][0].update(id="d"),
        lambda:s[c["source_files"][1]["path"]][0].update(supports="unread"),
        lambda:s[c["source_files"][1]["path"]][0].update(publisher="fabricated"),
        lambda:s[c["source_files"][1]["path"]][0].update(verified_on=None),
        lambda:s.pop(c["source_files"][0]["path"]),
        lambda:s.update({"extra.json":[]}),
        lambda:c["source_files"][0].update(count=4),
        lambda:c["source_files"][1].update(count=99),
        lambda:g["identities"].append(copy.deepcopy(g["identities"][0])),
        lambda:g["variants"].append(copy.deepcopy(g["variants"][0])),
    ]
    mutations[index]()

for index in range(49):
    def make_test(n):
        def run(self):
            c,s=fixture();mutate(n,c,s)
            with self.assertRaises((m.CrosswalkHold,KeyError,TypeError)):
                m.audit(c,s,expected=(3,2,1))
        return run
    setattr(TestCrosswalk, "test_adversarial_%02d"%index, make_test(index))

if __name__ == "__main__":
    unittest.main()
