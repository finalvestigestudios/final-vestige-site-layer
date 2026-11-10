"use strict";
const {test}=require("node:test");const assert=require("node:assert/strict");
const {check}=require("./route_contract.js");const fixture=require("./OFFER_ROUTE_CONTRACT.json");
const sample=()=>JSON.parse(JSON.stringify(fixture));
test("baseline is REVIEW-ONLY",()=>assert.deepEqual(check(sample()),{pass:true,errors:[]}));
const changes=[
["send approval",x=>x.founder_send_approval=true],
["sent status",x=>x.state="READY"],
["auto email",x=>x.wordpress.auto_new_posts=true],
["invented eligible recipients",x=>x.actual_email_eligible_audience=3],
["claimed welcome receipt",x=>x.verified_welcome_receipt=true],
["claimed unsubscribe",x=>x.verified_received_unsubscribe=true],
["invented paid order",x=>x.metrics.confirmed_paid_orders=1],
["invented net revenue",x=>x.metrics.realized_net_revenue=1],
["invented ROI",x=>x.metrics.net_revenue_per_1000_qualified_human_sessions=1],
["incorrect platform attribution",x=>x.metrics.source_rule="utm_source=grok;utm_medium=video"],
["merchant free email list conflation",x=>x.offers.zen12.merchant_free_trial_separate_newsletter=false],
["merchant price claimed",x=>x.offers.zen12.price=37],
["seller price conflict ignored",x=>x.offers["hypnosis-total-focus"].observed_price_variance=false],
["affiliate approval claimed",x=>x.offers.zen12.verified_fv_affiliate_approval=true],
["affiliate email approval claimed",x=>x.offers.zen12.verified_email_marketing_permission=true],
["invented merchant URL",x=>x.offers.zen12.verified_earning_url="https://zen12.com/hnp?aff=1"],
["invented local guide",x=>x.offers.zen12.verified_live_fv_guide="https://finalvestige.com/mind/zen12"],
["unearned product efficacy",x=>x.offers.zen12.product_specific_efficacy_verified=true],
["unsubscribe assumed",x=>x.release_gates.functional_opt_out=true],
["misplaced disclosure",x=>x.editions[2].disclosure_at_offer=false],
["removed commission disclosure",x=>x.editions[4].disclosure=""],
["commercial issue reclassified",x=>x.editions[4].type="editorial"],
["vendor URL as email CTA",x=>x.editions[2].cta="https://zen12.com/welcome"],
["faux first-party domain",x=>x.editions[0].cta="https://finalvestige.com.evil.com/focus/"],
["userinfo domain spoof",x=>x.editions[0].cta="https://finalvestige.com@evil.com/focus/"],
["open redirect",x=>x.editions[0].cta="https://finalvestige.com/focus/?redirect=https://zen12.com/welcome"],
["missing issue",x=>x.editions.pop()]
];
for(const [name,fn] of changes){test("refuses "+name,()=>{const c=sample();fn(c);assert.equal(check(c).pass,false,name)})}
