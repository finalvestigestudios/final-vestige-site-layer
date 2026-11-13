"""R331 adversarial-only fixtures: never authentic QA or release approval."""
import copy,hashlib,json,unittest
from preparedness.tools import r331_e325_claim_handoff_gate as gate

def fixture():
    source={}
    for role in ["a_body","t_body"]:
        anchors=list(dict.fromkeys(a for _,k,a,_ in CASES if k==role))
        source[role]="".join("<p>"+x+"</p>" for x in anchors).encode()
    for role,n,slug in [("a_meta",15,"family-communication-plan"),("t_meta",104,"family-reunification-card")]:
        anchors=[a for _,k,a,_ in CASES if k==role]
        source[role]=json.dumps({"n":n,"slug":slug,"status":{"editorial":"drafted","publish":"draft"},
          "safety_review":{"state":"pending","reviewer":None,"date":None},"source_use":{},
          "notes":" ".join(anchors)}).encode()
    m={"schema":gate.SCHEMA,"source_objects":{k:{"path":"preparedness/content/"+k,"git_blob_sha1":gate.PINNED[k]["git_blob_sha1"]} for k,v in source.items()},
       "original_review_witnesses":[{"id":i,"source_role":r,"exact_anchor":a,"editorial_candidate":e,
          "disposition":"UNRESOLVED_HUMAN_REVIEW","clearance":False} for i,r,a,e in CASES],
       "editorial_directions":{f"E325-{i:02d}":"review-only" for i in range(1,8)},
       "gates":{"independent_qd_pass":False,"publication_authorized":False}}
    return source,m

CASES=(
("A15-911-SCOPE","a_body","call 911 for anything life-threatening","E325-01"),
("T104-911-SCOPE","t_body","call 911 for anything life-threatening",None),
("T104-TEXT-EMERGENCY","t_body","use text messages rather than calls for everything else",None),
("A15-LOCAL-PRIVACY","a_body","keeps what you type on your own device","E325-04"),
("T104-PRIVACY-METADATA","t_meta","Nothing is stored.",None),
("A15-UNREVIEWED-CARD-LINK","a_body","{{link:family-reunification-card|","E325-04"),
("T104-PRINTED-CHILD-PRIVACY","t_body","A printed card can be lost",None),
("A15-MISSING-CHILD","a_body","If a child is missing after a disaster","E325-05"),
("T104-MISSING-CHILD","t_body","If a child is missing after a disaster",None),
("T104-SCHOOL-REUNIFICATION","t_body","School and childcare reunification",None),
("A15-CORDED-SERVICE","a_body","keep at least one corded telephone that does not depend on electricity","E325-02"),
("A15-REDCROSS-ARCHIVE","a_body","Red Cross takes welfare-check requests at 1-800-RED CROSS","E325-06"),
("A15-NCMEC-ORDER","a_body","If a child is missing after a disaster","E325-05"),
("T104-NCMEC-ORDER","t_body","If a child is missing after a disaster",None),
("A15-SCHOOL-LOCALITY","a_body",'Colorado\'s Office of School Safety describes reunification as "not a normal pick-up"',"E325-05"),
("T104-SCHOOL-LOCALITY","t_body","Colorado's Office of School Safety, as one state's example",None),
("A15-RESEARCH-NOT-OPENED","a_body","We did not open the Ready.gov fillable PDF card, the Red Cross's Reconnecting Families program","E325-06"),
)
class Review(unittest.TestCase):
    def setUp(self):self.src,self.m=fixture()
    def check(self):return gate.inspect(self.src,self.m,simulated=True)
    def test_valid_synthetic_always_held(self):
        r=self.check();self.assertEqual(r["state"],"DRAFT_HARD_HOLD",r["errors"])
        self.assertEqual(r["review_count"],17);self.assertFalse(r["release_authorized"])
    def test_real_only_rejects_synthetic_bytes(self):
        self.assertEqual(gate.inspect(self.src,self.m,simulated=False)["state"],"INVALID_HARD_HOLD")
    def test_forged_qd_rejected(self):
        self.m["gates"]["independent_qd_pass"]=True
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_forged_review_rejected(self):
        self.m["original_review_witnesses"][0]["clearance"]=True
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_missing_review_rejected(self):
        self.m["original_review_witnesses"].pop()
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_wrong_tool_identity_rejected(self):
        x=json.loads(self.src["t_meta"]);x["n"]=102;self.src["t_meta"]=json.dumps(x).encode()
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_unknown_editorial_direction(self):
        self.m["original_review_witnesses"][0]["editorial_candidate"]="E325-999"
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_duplicate_json_rejected(self):
        with self.assertRaises(ValueError):gate.strict_json(b'{"a":1,"a":2}')


    def test_forged_source_pin_rejected_even_with_matching_forged_bytes(self):
        self.m["source_objects"]["a_body"]["git_blob_sha1"]=gate.blob(self.src["a_body"])
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_substituted_source_path_rejected(self):
        self.m["source_objects"]["a_body"]["path"]="preparedness/content/articles/another.body.html"
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_forged_review_id_rejected(self):
        self.m["original_review_witnesses"][0]["id"]="FAKE-REVIEW-ITEM"
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_swapped_anchor_rejected(self):
        self.m["original_review_witnesses"][0]["exact_anchor"]="fake claim"
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def test_removed_release_gate_rejected(self):
        self.m["gates"].pop("independent_qd_pass")
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")

for idx,(rid,role,anchor,_) in enumerate(CASES):
    def removed(self,role=role,anchor=anchor):
        self.src[role]=self.src[role].replace(anchor.encode(),b"REMOVED")
        self.m["source_objects"][role]["git_blob_sha1"]=gate.PINNED[role]["git_blob_sha1"]
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    def repeated(self,role=role,anchor=anchor):
        self.src[role]+=b"<p>"+anchor.encode()+b"</p>"
        self.m["source_objects"][role]["git_blob_sha1"]=gate.blob(self.src[role])
        self.assertEqual(self.check()["state"],"INVALID_HARD_HOLD")
    setattr(Review,f"test_missing_original_{idx:02d}",removed)
    setattr(Review,f"test_duplicate_original_{idx:02d}",repeated)
