'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {assess,aggregate}=require('./release_contract.cjs');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'offer-proof-ledger.json'),'utf8'));
const a=fs.readFileSync(path.join(__dirname,'issue03-conditional.txt'),'utf8');
const b=fs.readFileSync(path.join(__dirname,'issue05-conditional.txt'),'utf8');
let n=0;function check(cond,msg){assert.ok(cond,msg);n++;}
check(data.campaign.editorial.join(',')==='1,2,4,6','four editorial');
check(data.campaign.commercial_reserved.join(',')==='3,5','two commercial');
check(data.campaign.canonical_pr===175,'master retained');
check(data.campaign.original_head.length===40,'master SHA');
check(data.wp_readonly.email_new_posts_by_default===false,'auto-sends disabled');
check(data.wp_readonly.email_content_format==='excerpt','transport known');
check(data.wp_readonly.reported_total===2,'known total');
check(data.wp_readonly.reported_unconfirmed===2,'pending separate');
check(data.wp_readonly.followers_email===0,'email follower diagnostic separate');
check(data.wp_readonly.reachable_email_recipients===null,'eligible audience unknown');
check(data.attribution.realized_net_per_1000_qualified_humans===null,'revenue unknown');
for(const issue of [1,2,3,4,5,6]){
 const decision=assess(issue,data);
 check(decision.allowed_to_send===false,'no send '+issue);
 check(decision.status===(issue===3||issue===5?'HOLD_MERCHANT':'HOLD_UNSENT'),'hold '+issue);
}
for(const [num,s] of [[3,a],[5,b]]){
 check(s.startsWith('THE DISPATCH — ISSUE '+String(num).padStart(2,'0')),'issue identity');
 check(s.includes('HOLD_UNSENT / HOLD_MERCHANT'),'commercial hold');
 check(s.includes('DISCLOSURE BESIDE CTA:'),'near CTA disclosure');
 check(s.indexOf('DISCLOSURE BESIDE CTA:')>s.indexOf('PRIMARY CTA — NOT ACTIVE:'),'disclosure immediately near');
 check((s.match(/PRIMARY CTA — NOT ACTIVE:/g)||[]).length===1,'one primary CTA');
 check(s.includes('[[APPROVED_LIVE_'),'inactive guide placeholder');
 check(s.includes('[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]'),'no fake address');
 check(s.includes('[[ACTUAL_JETPACK_UNSUBSCRIBE_NOT_YET_VERIFIED]]'),'no fake unsubscribe');
 check(!/\b(?:guaranteed (?:result|cure|income)|clinically proven to reprogram)\b/i.test(s),'no hype');
 check(s.includes('https://finalvestige.com/editorial-standards/'),'editorial standards source');
 check(s.includes('SOURCE NOTES'),'sources');
 check(s.slice(0,420).toLowerCase().includes('commission'),'disclosure context first 420 chars');
}
check(a.includes('https://zen12.com/hnp'),'exact Zen12 seller');
check(b.includes('https://hypnosislive.com/mental-skills/total-focus'),'exact Total Focus seller');
check(a.includes('https://pubmed.ncbi.nlm.nih.gov/37205669/'),'science context');
check(data.merchant.zen12.email_marketing_permission===null,'no false Zen12 acceptance');
check(data.merchant.total_focus.email_marketing_permission===null,'no false Total Focus acceptance');
check(aggregate(data).eligible_email_recipients===null,'reachability null');
check(aggregate(data).net_per_1000_qualified_sessions===null,'revenue null');
check(aggregate(data).confirmed_paid_orders===null,'orders null');
assert.throws(()=>assess(7,data),RangeError);n++;
const fake=structuredClone(data);fake.compliance={physical_fv_postal_address_verified:true,received_unsubscribe_verified:true,confirmed_eligible_recipient_count:2,received_email_preview_verified:true,precise_native_subject_preheader_verified:true,founder_final_send_approval:true};
check(assess(3,fake).allowed_to_send===false,'still merchant hold');
fake.merchant.zen12={affiliate_accepted:true,email_marketing_permission:true,exact_tracking_link:'https://example.org/test',independent_guide_live:true,checkout_price_verified:true,refund_at_checkout_verified:true,purchaser_data_reporting_approved:true};
check(assess(3,fake).status==='FOUNDER_REVIEW_ONLY','even synthetic proofs only human review');
check(assess(3,fake).allowed_to_send===false,'never autonomously send');
check(assess(5,fake).status==='HOLD_MERCHANT','separate merchant gates');
check(assess(4,fake).status==='FOUNDER_REVIEW_ONLY','editorial separately reviewable');
console.log(n+' source and synthetic checks PASS; no email sent.');
