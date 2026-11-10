"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const {audit}=require("./campaign_integrity_gate.js");
const {check: r263}=require("../r263/route_contract.js");
const snapshot=require("../r263/OFFER_ROUTE_CONTRACT.json");
const original=require("../campaign-2026-mind/manifest.json");
const pair=()=>[structuredClone(snapshot),structuredClone(original)];
test("unaltered source pair is REVIEW-ONLY compliant (NOT send-authorized)",()=>{
  const [s,m]=pair();assert.deepEqual(audit(s,m),{pass:true,errors:[]});
  assert.equal(s.founder_send_approval,false);
});
test("R263 insufficiently validates an empty release_gates map",()=>{
  const [s,m]=pair();s.release_gates={};
  assert.equal(r263(s).pass,true,"regression proof: earlier checker accepts empty map");
  assert.equal(audit(s,m).pass,false,"R264 blocks the earlier bypass");
});
const mutations=[
["root field missing", (s)=>delete s.schema],
["root extra flag", (s)=>s.send_now=true],
["canonical missing", (s)=>delete s.canonical],
["canonical issue changed", (s)=>s.canonical.dispatch_issue=999],
["canonical extra", (s)=>s.canonical.fake_pr=1929],
["release gate missing", (s)=>delete s.release_gates.functional_opt_out],
["all release gates missing", (s)=>s.release_gates={}],
["extra approval-like release gate", (s)=>s.release_gates.seller_email_approval=true],
["positive received preview", (s)=>s.release_gates.received_jetpack_preview=true],
["partner list extra", (s)=>s.offers.other={}],
["Zen12 missing original official source", (s)=>s.offers.zen12.official_sources.pop()],
["Zen12 merchant source swapped", (s)=>s.offers.zen12.official_sources[0]="https://zen12.com.evil.example/"],
["Zen12 merchant source reordered", (s)=>s.offers.zen12.official_sources.reverse()],
["seller free-audio consent boundary flipped", (s)=>s.offers.zen12.merchant_free_trial_separate_newsletter=false],
["seller affiliate permission claimed", (s)=>s.offers.zen12.verified_email_marketing_permission=true],
["seller address used as publisher", (s)=>s.verified_received_fv_postal_address=true],
["Hypnosis Live source drift", (s)=>s.offers["hypnosis-total-focus"].official_sources[0]="https://fake.example/"],
["attribution rule adds harmful parameter", (s)=>s.metrics.source_rule+=";email=private@example.com"],
["attribution rule campaign changed", (s)=>s.metrics.source_rule=s.metrics.source_rule.replace("cluster_pilot_2026_11","other")],
["attribution rule wrong platform", (s)=>s.metrics.source_rule=s.metrics.source_rule.replace("actual_platform","grok")],
["fabricated paid orders", (s)=>s.metrics.confirmed_paid_orders=1],
["metrics new invented stage", (s)=>s.metrics.unverified_sales=1],
["subscriber counter not integer", (s)=>s.wordpress.confirmed_counter="3"],
["negative subscriber counter", (s)=>s.wordpress.unconfirmed_requests=-1],
["subscriber counter unknown", (s)=>delete s.wordpress.wpcom_followers_last_observed],
["promote audience as eligible", (s)=>s.actual_email_eligible_audience=3],
["campaign subject rewritten", (s)=>s.editions[0].subject="Free secrets!"],
["editorial CTA swapped", (s)=>s.editions[0].cta=s.editions[5].cta],
["issue 03 direct seller form", (s)=>s.editions[2].cta="https://zen12.com/welcome"],
["misleading commercial disclosure", (s)=>s.editions[2].disclosure="There is no affiliate relationship."],
["commercial edition release toggled", (s)=>s.editions[4].release="READY"],
["campaign issue count lowered", (s)=>s.editions.pop()],
["original manifest approved", (_s,m)=>m.status="READY"],
["original mix changed", (_s,m)=>m.mix.editorial=5],
["original preheader missing", (_s,m)=>m.issues[3].preheader=""],
["original subject changed", (_s,m)=>m.issues[0].subject="Other"],
["original selling link added", (_s,m)=>m.issues[2].merchant_affiliate_url="https://zen12.com/hnp"],
["original issue published", (_s,m)=>m.issues[1].publish_state="publish"],
["original CTA silently changed", (_s,m)=>m.issues[0].editorial_cta="https://finalvestige.com/mind/"],
["original issues truncated", (_s,m)=>m.issues.splice(0,1)]
];
for(const [name,mutate] of mutations){
  test("refuses "+name,()=>{const [s,m]=pair();mutate(s,m);
    const result=audit(s,m);assert.equal(result.pass,false,name);
    assert.ok(result.errors.length>0);
  });
}
