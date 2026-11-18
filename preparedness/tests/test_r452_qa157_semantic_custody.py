"""R452 synthetic adversarial structural tests; NOT native safety QA."""
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "r452_qa157_semantic_custody.py"
spec = importlib.util.spec_from_file_location("r452", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
P = gate.PATHS


def fixture():
    household = ("do not switch off the main breaker as a drill. "
                 "Leave smoke and carbon monoxide alarms and medical supplies powered.")
    medicine = ("Talk to your pharmacist about a refrigerated medicine interim-use "
                "and replacement plan. {{cite:start-cdc-pyh-prescriptions}}")
    sources = {"sources": [{"id":"start-redcross-older-adults", "kind":"nonprofit",
                            "url":"https://redcross.example/older", "publisher":"American Red Cross",
                            "supports":"Read the emergency support network instructions."},
                           {"id":"start-other", "kind":"agency", "url":"https://agency.example/plan",
                            "publisher":"Agency", "supports":"Read household plans."}]}
    slate = [{"slug":f"article-{i}","n":i,"title":f"Article {i}","section":"start-here",
              "track":"modern","status":"drafted-pending-safety-review","gate":i%4==0}
             for i in range(1,36)]
    for i, slug in zip(range(1,5),sorted(gate.CRITICAL)):
        slate[i-1]["slug"] = slug
        slate[i-1]["gate"] = True
    tax = {"slate":slate,"base_path":"/preparedness/"}
    payload = {P[0]:household.encode(), P[1]:medicine.encode(),
               P[2]:json.dumps(sources).encode(), P[3]:json.dumps(tax).encode()}
    return payload


def run(qa=None, candidate=None):
    qa = qa or fixture()
    candidate = candidate or dict(qa)
    pins_qa = [gate.git_blob(qa[p]) for p in P]
    pins_candidate = [gate.git_blob(candidate[p]) for p in P]
    return gate.assess(qa,candidate,pins_qa,pins_candidate)

class Basic(unittest.TestCase):
    def test_safe_synthetic_fixture_remains_hard_hold(self):
        r=run()
        self.assertEqual(r["release_state"],"DRAFT_HARD_HOLD")
        self.assertEqual(r["source_review"],"NOT_APPROVED")
        self.assertEqual(r["article_count"],35)
        self.assertEqual(r["original_source_ids_retained"],2)
    def test_git_blob_algorithm(self):
        self.assertEqual(gate.git_blob(b"test"),"30d74d258442c7c65512eafab474568dd706c430")
    def test_extra_gate_preserved(self):
        qa=fixture(); cur=dict(qa);obj=json.loads(cur[P[3]]);obj["slate"][6]["gate"]=True
        cur[P[3]]=json.dumps(obj).encode();self.assertIn(obj["slate"][6]["slug"],run(qa,cur)["additional_review_gates_preserved"])
    def test_exact_path_required(self):
        qa=fixture(); del qa[P[0]]
        with self.assertRaises(gate.CustodyError): gate.assess(qa, fixture())
    def test_actual_production_pins_not_synthetic(self):
        with self.assertRaises(gate.CustodyError): gate.assess(fixture(),fixture())

# Each generated case is a separately discovered unittest method. Mutations are
# deliberately independently pinned to test semantics, not real-world safety.
def make_mutation(index, change):
    def test(self):
        qa=fixture(); cur=dict(qa)
        change(cur)
        with self.assertRaises(gate.CustodyError):run(qa,cur)
    test.__name__=f"test_adversarial_{index:02d}"
    return test

MUTATIONS=[]
for phrase in ("do not switch off the main breaker","smoke and carbon monoxide alarms","medical"):
    MUTATIONS.append(lambda cur,p=phrase:cur.__setitem__(P[0],cur[P[0]].replace(p.encode(),b"")))
MUTATIONS.append(lambda cur:cur.__setitem__(P[0],cur[P[0]]+b" Switch off the main power for an evening"))
for phrase in ("refrigerated medicine","pharmacist","interim-use","replacement plan", "{{cite:start-cdc-pyh-prescriptions}}"):
    MUTATIONS.append(lambda cur,p=phrase:cur.__setitem__(P[1],cur[P[1]].replace(p.encode(),b"")))
for n in range(1,36):
    def change(cur,n=n):
        obj=json.loads(cur[P[3]]); obj["slate"][n-1]["status"]="published"
        cur[P[3]]=json.dumps(obj).encode()
    MUTATIONS.append(change)
for n in range(1,36):
    def change(cur,n=n):
        obj=json.loads(cur[P[3]]); obj["slate"][n-1]["slug"]="illegitimate-new-url-"+str(n)
        cur[P[3]]=json.dumps(obj).encode()
    MUTATIONS.append(change)
for n in range(1,5):
    def change(cur,n=n):
        obj=json.loads(cur[P[3]]); obj["slate"][n-1]["gate"]=False
        cur[P[3]]=json.dumps(obj).encode()
    MUTATIONS.append(change)
for field in ("url","publisher","supports","kind"):
    def change(cur,f=field):
        obj=json.loads(cur[P[2]]); obj["sources"][0][f]="" if f!="kind" else "regulator"
        cur[P[2]]=json.dumps(obj).encode()
    MUTATIONS.append(change)
for k,change in enumerate(MUTATIONS,1):
    setattr(Basic,f"test_adversarial_{k:02d}",make_mutation(k,change))

if __name__ == "__main__":unittest.main()
