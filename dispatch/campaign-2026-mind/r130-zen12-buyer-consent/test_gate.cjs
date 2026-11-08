"use strict";
const {inspect}=require("./gate.cjs");
const fs=require("fs");
const path=require("path");
const root=__dirname;
const a={manifest:JSON.parse(fs.readFileSync(path.join(root,"offer_manifest.json"),"utf8")),markdown:fs.readFileSync(path.join(root,"issue03-optional.md"),"utf8"),plain:fs.readFileSync(path.join(root,"issue03-plain.txt"),"utf8"),html:fs.readFileSync(path.join(root,"issue03-preview.html"),"utf8")};
let passed=0;function check(name,fn){if(!fn())throw Error("FAIL "+name);passed++;}
const baseline=inspect(a);
check("baseline_draft_review_pass",()=>baseline.passed&&baseline.status==="HOLD_ALL_UNSENT"&&baseline.commercial_status==="HOLD_MERCHANT");
const mods=[
["sender_authorized",o=>o.manifest.send_authorized=true],
["approved_list",o=>o.manifest.approved_audience=true],
["permission_claim",o=>o.manifest.merchant_email_channel_permission="YES"],
["active_url",o=>o.manifest.earning_url="https://example.com/?ref=123"],
["live_guide",o=>o.manifest.guide_live=true],
["postal_fake",o=>o.manifest.publisher_postal_address_verified=true],
["unsubscribe_fake",o=>o.manifest.rendered_unsubscribe_verified=true],
["received_email_fake",o=>o.manifest.received_jetpack_preview_verified=true],
["recipient_fake",o=>o.manifest.recipient_eligibility_verified=true],
["welcome_fake",o=>o.manifest.delivered_fieldbook_verified=true],
["income_fake",o=>o.manifest.conversion_contract.net_revenue_usd=100],
["purchase_fake",o=>o.manifest.conversion_contract.verified_orders=2],
["sessions_fake",o=>o.manifest.conversion_contract.qualified_human_sessions=50],
["affiliate_ref_fake",o=>o.manifest.merchant_tracking_format="VERIFIED"],
["partner_creative_fake",o=>o.manifest.partner_approved_creative="VERIFIED"],
["product_price_fake",o=>o.manifest.final_price="$87.99"],
["product_refund_fake",o=>o.manifest.actual_refund_terms="1 year"],
["original_mix_drift",o=>o.manifest.campaign_mix.commercial_review_pending=4],
["orig_manuscripts_claim",o=>o.manifest.original_canonical_manuscripts_unchanged=false],
["guide_activated",o=>o.manifest.conversion_contract.destination="https://finalvestige.com/fake-guide/"],
["count_inferred",o=>o.manifest.subscriber_snapshot.email_eligible=3],
["count_added",o=>o.manifest.subscriber_snapshot.not_additive=false],
["data_consent_erased",o=>o.markdown=o.markdown.replace(/seller's newsletter/g,"special offer")],
["postal_hold_removed",o=>o.plain=o.plain.replace("[[VALID_POSTAL_ADDRESS_REQUIRED]]","some city")],
["unsub_hold_removed",o=>o.markdown=o.markdown.replace("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]","click here")],
["disclosure_removed",o=>o.markdown=o.markdown.replace("Commercial disclosure (beside","Tiny note (beside")],
["script_injected",o=>o.html+="<script>alert(1)</script>"],
["form_injected",o=>o.html+="<form action='#'></form>"],
["mobile_meta_removed",o=>o.html=o.html.replace('name="viewport"','name="wrong"')],
["source_nih_removed",o=>o.manifest.source_observations=o.manifest.source_observations.filter(x=>!x.source.includes("nccih.nih.gov"))],
["status_removed",o=>o.plain=o.plain.replace("HOLD_ALL_UNSENT","READY_TO_SEND")],
["preview_activated",o=>o.html=o.html.replace("GUIDE NOT LIVE","CLICK TO BUY")],
["unsent_status_removed",o=>o.html=o.html.replaceAll("UNSENT","SENT")]
];
for(const [name,mutate] of mods){let o=JSON.parse(JSON.stringify(a));mutate(o);check(name,()=>inspect(o).passed===false)}
console.log("PASS "+passed+"/"+(mods.length+1)+" (offline static and mutation checks; NOT native Jetpack or email)");
