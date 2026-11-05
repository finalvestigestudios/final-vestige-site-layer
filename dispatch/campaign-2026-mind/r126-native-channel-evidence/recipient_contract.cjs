"use strict";
/** R126: read-only native WordPress channel interpretation; no send, no PII. */
const STATUSES=["Subscribed","Not subscribed","Not confirmed","Bounced","Emails paused","Not sending"];
const TYPES=["editorial","editorial","commercial","editorial","commercial","editorial"];
const ROUTES=[
"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",
"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",
null,
"https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/",
null,
"https://finalvestige.com/focus/"];
function ok(b,msg){if(!b)throw Error(msg);}
function count(x){return Number.isSafeInteger(x)&&x>=0;}
function time(t){return typeof t==="string"&&/^20\d\d-\d\d-\d\dT\d\d:\d\d/.test(t)&&!Number.isNaN(Date.parse(t));}
function pii(obj){return obj&&typeof obj==="object"&&Object.keys(obj).some(k=>/^(email|address|name|phone|ip|user_id|subscriber_id|token|cookie)$/i.test(k));}
function audit(x){
ok(x&&typeof x==="object"&&!pii(x),"PII or missing snapshot");
const n=x.newsletter,f=x.followers;
ok(n&&f&&n.site==="finalvestige.com"&&f.site===n.site,"site mismatch");
ok(n.provider==="wordpress_newsletter"&&f.provider==="jetpack_stats_followers","untrusted provider");
ok(time(n.observed_utc)&&time(f.observed_utc),"dated source required");
ok(n.counts&&f.counts&&f.partial===false,"partial or missing result");
for(const k of ["total","confirmed","unconfirmed","suppressed","paid","imported_last_24h"])
ok(count(n.counts[k]),"newsletter count: "+k);
for(const k of ["total","email","wpcom","comment"])
ok(count(f.counts[k]),"follower count: "+k);
let eligible=null;
if(x.authoritative_email_status_counts!==undefined){
const a=x.authoritative_email_status_counts;
ok(a&&a.provider==="native_subscribers_email_status"&&a.audited_scope==="full_site"&&time(a.observed_utc)&&!pii(a),"invalid email eligibility provenance");
ok(a.counts&&STATUSES.every(k=>count(a.counts[k])),"native email status categories incomplete");
eligible=a.counts.Subscribed;
}
return {reported_total:n.counts.total,reported_confirmed:n.counts.confirmed,
reported_unconfirmed:n.counts.unconfirmed,reported_imports24h:n.counts.imported_last_24h,
legacy_email_followers:f.counts.email,wpcom_followers:f.counts.wpcom,
newsletter_counts_additive:false,wpcom_follower_necessarily_ineligible:false,
verified_email_eligible_aggregate:eligible,verified_confirmed_signup_events:null,
verified_welcome_receipts:null,verified_paid_orders:null,
interpretation:eligible===null?"ELIGIBILITY_UNKNOWN":"PROVIDER_EMAIL_STATUS_AGGREGATE_ONLY",
release:"HOLD_ALL_UNSENT"};
}
function tag(url,n){
ok(Number.isSafeInteger(n)&&n>0&&n<7,"issue out of range");
ok(typeof url==="string"&&/^https:\/\/finalvestige\.com\/[A-Za-z0-9/_-]+\/$/.test(url),"no merchants, placeholders or dynamic/PII query");
return url+"?utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=dispatch_issue_"+String(n).padStart(2,"0");
}
function sequence(){
return TYPES.map((kind,i)=>({number:i+1,kind,source:"original PR #175 subject/CTA ledger",
state:"HOLD_UNSENT",cta_preview:ROUTES[i]?tag(ROUTES[i],i+1):null,
merchant_url:null,disclose_adjacent_to_offer:kind==="commercial",
repeat_signup_review:i===5,claimed_delivered:false,claimed_paid:false}));
}
function review(s){
ok(Array.isArray(s)&&s.length===6,"exact six");
ok(s.filter(x=>x.kind==="editorial").length===4&&s.filter(x=>x.kind==="commercial").length===2,"4:2 mix");
for(let i=0;i<6;i++){
const x=s[i];ok(x.number===i+1&&x.kind===TYPES[i],"revision drift");
ok(x.state==="HOLD_UNSENT"&&x.merchant_url===null&&!x.claimed_delivered&&!x.claimed_paid,"accidental activation/outcome");
ok(x.cta_preview===(ROUTES[i]?tag(ROUTES[i],i+1):null),"CTA not authorized");
if(x.kind==="commercial")ok(x.disclose_adjacent_to_offer===true,"missing commercial disclosure");
}
return {issues:6,editorial:4,commercial_reserved:2,sendable:0,merchant_active:0,status:"HOLD_ALL_UNSENT"};
}
function decision(a){ok(a&&a.release==="HOLD_ALL_UNSENT","validated audience required");
return {send:false,schedule:false,merchant:false,status:"HOLD_ALL_UNSENT",native_email_eligible:a.verified_email_eligible_aggregate,
still_required:["real native email status","native consent","actual completed welcome","genuine editor/inbox preview",
"publisher postal address","functional unsubscribe","named affiliate email permission",
"approved first-party guides","founder final approval","independently paid revenue"]};}
module.exports={STATUSES,audit,tag,sequence,review,decision};
