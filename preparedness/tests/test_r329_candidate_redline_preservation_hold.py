"""R329 synthetic/adversarial cases. These cannot qualify emergency or privacy safety."""
import copy
import json
import unittest
from preparedness.tools import r329_candidate_redline_preservation_hold as gate

FILL = " Families need a practiced contact plan and a reliable paper copy before an outage. " * 18
A = ("<section id='intro'><h2 id='act-h'>Actions</h2><p>"
     "call 911 for anything life-threatening{{cite:shelter-fcc-comms}}</p>"
     "<p>Tool keeps what you type on your own device." + FILL + "</p>"
     "<p>{{link:family-reunification-card|Card}}</p>"
     "<a href='/preparedness/'>Archive</a></section>")
T = ("<section id='intro'><h2 id='act-h'>Actions</h2><p>"
     "call 911 for anything life-threatening and use text messages rather than calls for everything else."
     "{{cite:shelter-ready-tech}}</p><p>It is not sent or saved. Closing the tab clears it."
     + FILL + "</p><p>{{link:family-communication-plan|Guide}}</p>"
     "<form onsubmit='return false'><input id='name' type='text'>"
     "<button type='button' onclick='print()'>Print</button></form>"
     "<a href='/preparedness/'>Archive</a></section>")
A_META = {"n":15,"slug":"family-communication-plan","section":"family-communication",
          "track":"modern","status":{"editorial":"drafted","publish":"draft"},
          "safety_review":{"state":"pending","reviewer":None,"date":None},
          "related":["family-reunification-card"],"source_use":{"shelter-fcc-comms":"FCC planning"}}
T_META = {"n":104,"slug":"family-reunification-card","section":"field-tools",
          "track":"modern","kind":"tool","status":{"editorial":"drafted","publish":"draft"},
          "safety_review":{"state":"pending","reviewer":None,"date":None},
          "related":["family-communication-plan"],"source_use":{"shelter-ready-tech":"Ready.gov"},
          "description":"Nothing is stored."}

def fixture():
    before={"a_body":A.encode(),"t_body":T.encode(),
            "a_meta":json.dumps(A_META).encode(),"t_meta":json.dumps(T_META).encode()}
    a=A.replace("call 911 for anything life-threatening",
                "seek immediate police, fire or ambulance help through local emergency services")
    a=a.replace("keeps what you type on your own device",
                "requires independent privacy testing before any tool recommendation")
    t=T.replace("call 911 for anything life-threatening",
                "seek immediate police, fire or ambulance help through local emergency services")
    t=t.replace("use text messages rather than calls for everything else",
                "check whether emergency texting is available locally and use the appropriate service")
    t=t.replace("It is not sent or saved", "Browser storage and network behavior remain unverified")
    t=t.replace("Closing the tab clears it", "Verify data handling independently before release")
    tm=copy.deepcopy(T_META);tm["description"]="Privacy has not been independently verified."
    proposed={"a_body":a.encode(),"t_body":t.encode(),
              "a_meta":before["a_meta"],"t_meta":json.dumps(tm).encode()}
    return before,proposed

def body(role,old,new):
    def fn(d):
        d[role]=d[role].decode().replace(old,new).encode()
    return fn

def meta(role,key,value):
    def fn(d):
        j=json.loads(d[role]);j[key]=value;d[role]=json.dumps(j).encode()
    return fn

def nested(role,key,field,value):
    def fn(d):
        j=json.loads(d[role]);j[key][field]=value;d[role]=json.dumps(j).encode()
    return fn

MUTATIONS={
    "a_old_911":body("a_body","seek immediate police, fire or ambulance help through local emergency services","call 911 for anything life-threatening"),
    "t_old_911":body("t_body","seek immediate police, fire or ambulance help through local emergency services","call 911 for anything life-threatening"),
    "a_privacy":body("a_body","requires independent privacy testing before any tool recommendation","keeps what you type on your own device"),
    "t_sms":body("t_body","check whether emergency texting is available locally and use the appropriate service","use text messages rather than calls for everything else"),
    "t_privacy":body("t_body","Browser storage and network behavior remain unverified","It is not sent or saved"),
    "t_close":body("t_body","Verify data handling independently before release","Closing the tab clears it"),
    "t_meta_privacy":meta("t_meta","description","Nothing is stored."),
    "a_cite_missing":body("a_body","{{cite:shelter-fcc-comms}}",""),
    "t_cite_missing":body("t_body","{{cite:shelter-ready-tech}}",""),
    "a_extra_cite":body("a_body","</section>","{{cite:unsupported}}</section>"),
    "t_extra_cite":body("t_body","</section>","{{cite:unsupported}}</section>"),
    "a_source_use":meta("a_meta","source_use",{"other":"false source"}),
    "t_source_use":meta("t_meta","source_use",{"other":"false source"}),
    "a_card_link_missing":body("a_body","{{link:family-reunification-card|Card}}",""),
    "t_guide_link_missing":body("t_body","{{link:family-communication-plan|Guide}}",""),
    "a_href_missing":body("a_body","<a href='/preparedness/'>Archive</a>",""),
    "t_href_missing":body("t_body","<a href='/preparedness/'>Archive</a>",""),
    "a_heading_missing":body("a_body","id='act-h'","id='renamed'"),
    "t_heading_missing":body("t_body","id='act-h'","id='renamed'"),
    "a_duplicate_id":body("a_body","</section>","<p id='act-h'>duplicate</p></section>"),
    "t_duplicate_id":body("t_body","</section>","<p id='act-h'>duplicate</p></section>"),
    "a_reading_depth":body("a_body",FILL,""),
    "t_reading_depth":body("t_body",FILL,""),
    "t_form_post":body("t_body","<form onsubmit='return false'>","<form method='POST'>"),
    "t_form_action":body("t_body","<form onsubmit='return false'>","<form action='/submit'>"),
    "t_event_changed":body("t_body","onclick='print()'","onclick='submit()'"),
    "t_new_name":body("t_body","<input id='name' type='text'>","<input id='name' name='child_phone' type='text'>"),
    "t_new_action":body("t_body","type='button'","formaction='https://example.com/collect' type='button'"),
    "a_external_script":body("a_body","</section>","<script src='https://example.com/a.js'></script></section>"),
    "t_external_script":body("t_body","</section>","<script src='https://example.com/a.js'></script></section>"),
    "a_inline_script":body("a_body","</section>","<script>fetch('/collect')</script></section>"),
    "t_inline_script":body("t_body","</section>","<script>fetch('/collect')</script></section>"),
    "a_inline_style":body("a_body","</section>","<style>body{display:none}</style></section>"),
    "t_inline_style":body("t_body","</section>","<style>body{display:none}</style></section>"),
    "a_iframe":body("a_body","</section>","<iframe src='https://example.com'></iframe></section>"),
    "t_iframe":body("t_body","</section>","<iframe src='https://example.com'></iframe></section>"),
    "a_live":nested("a_meta","status","publish","published"),
    "t_live":nested("t_meta","status","publish","published"),
    "a_approved":nested("a_meta","safety_review","state","approved"),
    "t_approved":nested("t_meta","safety_review","state","approved"),
    "a_reviewer":nested("a_meta","safety_review","reviewer","invented"),
    "t_reviewer":nested("t_meta","safety_review","reviewer","invented"),
    "a_date":nested("a_meta","safety_review","date","2026-11-13"),
    "t_date":nested("t_meta","safety_review","date","2026-11-13"),
    "a_wrong_number":meta("a_meta","n",104),
    "t_wrong_number":meta("t_meta","n",102),
    "a_wrong_slug":meta("a_meta","slug","family-reunification-card"),
    "t_wrong_slug":meta("t_meta","slug","reunification-plan"),
    "a_wrong_section":meta("a_meta","section","field-tools"),
    "t_wrong_section":meta("t_meta","section","family-communication"),
    "a_wrong_track":meta("a_meta","track","lost-ways"),
    "t_wrong_track":meta("t_meta","track","lost-ways"),
    "t_wrong_kind":meta("t_meta","kind","article"),
    "a_drop_related":meta("a_meta","related",[]),
    "t_drop_related":meta("t_meta","related",[]),
    "a_duplicate_related":meta("a_meta","related",["family-reunification-card"]*2),
    "t_duplicate_related":meta("t_meta","related",["family-communication-plan"]*2),
}
class GuardTests(unittest.TestCase):
    def test_structurally_clean_still_not_approved(self):
        a,b=fixture();r=gate.inspect(a,b)
        self.assertEqual(r["state"],gate.HARD_HOLD)
        self.assertEqual(r["errors"],[])
        self.assertFalse(r["qualified_approval"])
        self.assertTrue(all(x is False for x in r["release"].values()))
    def test_originals_are_git_pin_required(self):
        a,b=fixture()
        r=gate.audit(lambda p:next(a[k] for k,(q,_) in gate.original.DOCS.items() if p==q),
                     lambda p:next(b[k] for k,(q,_) in gate.original.DOCS.items() if p==q))
        self.assertEqual(r["state"],"INVALID_HARD_HOLD")
        self.assertEqual(r["original_blobs_verified"],0)
    def test_reject_missing_candidate_role(self):
        a,b=fixture();b.pop("t_meta")
        self.assertEqual(gate.inspect(a,b)["state"],"INVALID_HARD_HOLD")
    def test_reject_non_bytes(self):
        a,b=fixture();b["t_body"]="not bytes"
        self.assertEqual(gate.inspect(a,b)["state"],"INVALID_HARD_HOLD")
    def test_reject_non_utf8(self):
        a,b=fixture();b["a_body"]=b"\xff"
        self.assertEqual(gate.inspect(a,b)["state"],"INVALID_HARD_HOLD")
    def test_reject_unchanged_original(self):
        a,b=fixture();b["a_body"]=a["a_body"]
        self.assertEqual(gate.inspect(a,b)["state"],"INVALID_HARD_HOLD")
    def test_reject_duplicate_metadata_json_keys(self):
        a,b=fixture();b["t_meta"]=b["t_meta"][:-1]+b',"n":104}'
        self.assertEqual(gate.inspect(a,b)["state"],"INVALID_HARD_HOLD")
    def test_reject_invalid_metadata_json(self):
        a,b=fixture();b["t_meta"]=b"{"
        self.assertEqual(gate.inspect(a,b)["state"],"INVALID_HARD_HOLD")

def make_bad_case(name,mutation):
    def check(self):
        a,b=fixture();mutation(b)
        r=gate.inspect(a,b)
        self.assertEqual(r["state"],"INVALID_HARD_HOLD",name)
        self.assertTrue(r["errors"],name)
        self.assertTrue(all(v is False for v in r["release"].values()))
    check.__name__="test_reject_"+name
    return check
for _name,_mutation in MUTATIONS.items():
    setattr(GuardTests,"test_reject_"+_name,make_bad_case(_name,_mutation))
if __name__ == "__main__": unittest.main()
