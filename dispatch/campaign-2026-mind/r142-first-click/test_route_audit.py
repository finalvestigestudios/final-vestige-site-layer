"""Offline source-level safety and conversion-routing regression; no network or emails."""
import pathlib,json,copy,unittest
ROOT=pathlib.Path(__file__).resolve().parent
DATA=json.loads((ROOT/"route-audit.json").read_text(encoding="utf8"))
DOCS=json.loads((ROOT/"source-ledger.json").read_text(encoding="utf8"))
def audit(d):
    e=[]
    issues=d.get("issues",[])
    if len(issues)!=6 or [r.get("n") for r in issues]!=[1,2,3,4,5,6]:e.append("six issues")
    kinds=[r.get("type") for r in issues]
    if kinds.count("editorial")!=4 or kinds.count("commercial-review-pending")!=2:e.append("4:2")
    if d.get("status")!="REVIEW_ONLY_HOLD_UNSENT":e.append("send held")
    if any(v is not False for v in d.get("flags",{}).values()):e.append("active implementation")
    f=d.get("facts",{})
    if f.get("eligible_recipients") is not None or f.get("delivered_welcome") is not None:e.append("unverified consent")
    if f.get("net_revenue_per_1000_qualified_humans") is not None or f.get("independently_verified_paid_orders") is not None:e.append("fake sales")
    if any(f.get(k) is not False for k in ("publisher_address_verified","unsub_inbox_verified","merchant_email_permission_verified")):e.append("false legal gate")
    if len(issues)==6:
      if issues[0].get("proposal")==issues[1].get("proposal"):e.append("duplicate consecutive CTA")
      if issues[5].get("proposal")=="https://finalvestige.com/focus/":e.append("repeat signup loop")
      for r in issues:
        n=r.get("n"); u=r.get("proposal")
        if n in (3,5):
          if u is not None or r.get("state")!="HOLD_MERCHANT":e.append(f"merchant {n} activated")
        else:
          if not isinstance(u,str) or not u.startswith("https://finalvestige.com/"):e.append(f"offsite {n}")
    return e
class RouteSafety(unittest.TestCase):
    def test_base(self):self.assertEqual(audit(DATA),[])
    def test_four_two(self):
      d=copy.deepcopy(DATA);d["issues"][0]["type"]="commercial-review-pending";self.assertIn("4:2",audit(d))
    def test_hold(self):
      d=copy.deepcopy(DATA);d["status"]="SEND_APPROVED";self.assertIn("send held",audit(d))
    def test_no_wp_write(self):
      d=copy.deepcopy(DATA);d["flags"]["wordpress_post_create"]=True;self.assertIn("active implementation",audit(d))
    def test_no_merchant_03(self):
      d=copy.deepcopy(DATA);d["issues"][2]["proposal"]="https://zen12.com/?aff=unknown";self.assertTrue(any("merchant 3" in x for x in audit(d)))
    def test_no_merchant_05(self):
      d=copy.deepcopy(DATA);d["issues"][4]["proposal"]="https://hypnosislive.com/ref=1";self.assertTrue(any("merchant 5" in x for x in audit(d)))
    def test_consent_unknown(self):
      d=copy.deepcopy(DATA);d["facts"]["eligible_recipients"]=3;self.assertIn("unverified consent",audit(d))
    def test_welcome_unknown(self):
      d=copy.deepcopy(DATA);d["facts"]["delivered_welcome"]=3;self.assertIn("unverified consent",audit(d))
    def test_no_sales(self):
      d=copy.deepcopy(DATA);d["facts"]["independently_verified_paid_orders"]=1;self.assertIn("fake sales",audit(d))
    def test_legal_not_attested(self):
      d=copy.deepcopy(DATA);d["facts"]["publisher_address_verified"]=True;self.assertIn("false legal gate",audit(d))
    def test_duplicate(self):
      d=copy.deepcopy(DATA);d["issues"][0]["proposal"]=d["issues"][1]["proposal"];self.assertIn("duplicate consecutive CTA",audit(d))
    def test_loop(self):
      d=copy.deepcopy(DATA);d["issues"][5]["proposal"]="https://finalvestige.com/focus/";self.assertIn("repeat signup loop",audit(d))
    def test_offsite(self):
      d=copy.deepcopy(DATA);d["issues"][0]["proposal"]="https://malicious.test/click";self.assertIn("offsite 1",audit(d))
    def test_assets(self):
      self.assertTrue(any(r["id"]==1737 and not r["download_verified"] for r in DOCS["wordpress"]))
    def test_no_names_or_tokens(self):
      s=json.dumps(DATA)+json.dumps(DOCS)
      for key in ('"subscriber_email"','"customer_email"','"recipient_id"','"email_token"'):self.assertNotIn(key,s)
    def test_drafts_have_legal_holds(self):
      for name in ("issue01-change-blindness-optional.md","issue06-fieldbook-revisit-optional.md"):
        body=(ROOT/name).read_text(encoding="utf8")
        self.assertIn("UNSENT",body);self.assertIn("VALID_POSTAL_ADDRESS_REQUIRED",body);self.assertIn("JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED",body)
    def test_research_source(self):
      text=(ROOT/"issue01-change-blindness-optional.md").read_text(encoding="utf8")
      self.assertIn("10.1111/j.1467-9280.1997.tb00427.x",text)
      self.assertIn("10.3758/BF03208840",text)
if __name__=="__main__":unittest.main()
