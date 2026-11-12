// Dispatch R316 — isolated, pure, never-sending source and compliance evidence gate.
// This software is an advisory QA checklist, not legal advice or send authorization.
// All expiry durations below are conservative internal review heuristics, not legal mandates.
export const TTL_DAYS={postal:30,unsubscribe:7,inbox:7,eligible_email:1,founder_final:7,account_acceptance:14,email_permission:14,creative_rights:14,affiliate_link:7,sales_page:2,terms:2,guide:1,claim_review:14};
export const ALLOWED_SOURCES={
postal:['github.com'],unsubscribe:['github.com','wordpress.com'],inbox:['github.com','wordpress.com'],
eligible_email:['wordpress.com'],founder_final:['github.com'],
account_acceptance:['affiliates.inspire3.com'],email_permission:['affiliates.inspire3.com'],
creative_rights:['affiliates.inspire3.com'],affiliate_link:['affiliates.inspire3.com'],
sales_page:['zen12.com','hypnosislive.com'],terms:['zen12.com','hypnosislive.com'],
guide:['finalvestige.com'],claim_review:['github.com']
};
export function validEvidence(p,type,now){
 if(!p||p.verified!==true||p.type!==type||!/^proof_[A-Za-z0-9_-]{6,64}$/.test(p.proof_id||''))return false;
 if(typeof p.url!=='string'||!/^https:\/\/[a-z0-9.-]+(?:\/[^\s?#]*)?$/i.test(p.url))return false;
 const host=p.url.match(/^https:\/\/([^/]+)/i)?.[1]?.toLowerCase();
 if(!ALLOWED_SOURCES[type]?.includes(host))return false;
 const age=Date.parse(now)-Date.parse(p.checked_at);
 if(!Number.isFinite(age)||age<0||age>TTL_DAYS[type]*86400000)return false;
 return true;
}
export function assessEdition(edition,evidence={},now){
 const blockers=[];
 const commercial=[3,5].includes(edition?.number);
 if(!edition||!Number.isInteger(edition.number)||edition.number<1||edition.number>6||!/^[a-f0-9]{40}$/.test(edition.source_blob||''))blockers.push('Original source identity failed');
 if(edition && edition.kind!==(commercial?'commercial-review-pending':'editorial'))blockers.push('Original 4:2 editorial allocation failed');
 const shared=['postal','unsubscribe','inbox','eligible_email','founder_final'];
 const merchant=['account_acceptance','email_permission','creative_rights','affiliate_link','sales_page','terms','guide','claim_review'];
 for(const type of [...shared,...(commercial?merchant:[])])
   if(!validEvidence(evidence[type],type,now))blockers.push('MISSING_OR_EXPIRED_'+type);
 if(edition?.ftc_purpose_review!==true)blockers.push('NO_FTC_PRIMARY_PURPOSE_WITNESS');
 if(edition?.real_inbox_preview!==true)blockers.push('NO_NATIVE_EMAIL_PREVIEW_WITNESS');
 if(commercial){
   if(edition.merchant_email_permission!==true)blockers.push('NO_ACCOUNT_SPECIFIC_EMAIL_PERMISSION');
   if(edition.disclosure_adjacent_verified!==true)blockers.push('NO_ADJACENT_AFFILIATE_DISCLOSURE');
   if(edition.guide_published!==true)blockers.push('NO_APPROVED_PUBLISHED_WARMUP_GUIDE');
   if(edition.affiliate_link!==null)blockers.push('NO_LIVE_AFFILIATE_LINKS_ALLOWED_IN_DRAFT');
 }
 return {edition:edition?.number,commercial,blockers,status:blockers.length?'HOLD_UNSENT':'HUMAN_REVIEW_CANDIDATE_ONLY',send_allowed:false};
}
export function assessCampaign(editions=[],evidence={},now){
 const results=editions.map(e=>assessEdition(e,evidence,now));
 const ids=new Set(results.map(x=>x.edition));
 const mix_valid=results.length===6&&ids.size===6&&[1,2,3,4,5,6].every(id=>ids.has(id))&&results.filter(x=>x.commercial).length===2;
 return {mix_valid,results,status:'HOLD_UNSENT',send_allowed:false,commercial_issues_hold:true,
 revenue_per_1000_qualified_human_sessions:'NOT_COMPUTABLE'};
}
