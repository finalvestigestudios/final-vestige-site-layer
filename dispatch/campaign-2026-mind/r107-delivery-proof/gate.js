/* Dispatch R107: offline, fail-closed; no network, mail, personal data or WP writes. */
(function(root){"use strict";
const SOURCE=["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"];
function int(v){return Number.isInteger(v)&&v>=0}
function subscribers(s){
 if(!s||!["total","confirmed","unconfirmed","suppressed"].every(k=>int(s[k])))
  return {status:"INVALID_AGGREGATES",reachable:null};
 return {status:"EMAIL_RECEIVING_STATUS_NOT_VERIFIED",reachable:null,
  note:"WordPress not-confirmed records excluded from total. Do not sum counts or treat Reader followers as email subscribers.",
  total:s.total,confirmed:s.confirmed,unconfirmed:s.unconfirmed,
  readerFollowers:s.readerFollowers??null,emailFollowers:s.emailFollowers??null};
}
function socialUtm(x){
 return !!x&&Object.keys(x).sort().join(",")==="utm_campaign,utm_content,utm_medium,utm_source"&&
 SOURCE.includes(x.utm_source)&&x.utm_medium==="organic_social"&&
 /^(mind|history|mysteries|preparedness)_pilot_2026_11$/.test(x.utm_campaign)&&
 typeof x.utm_content==="string"&&/^[A-Za-z0-9._-]{4,64}$/.test(x.utm_content);
}
const PATHS=["/focus/","/dispatch/","/2026/11/02/change-blindness/","/free-resources/puysegurs-animal-magnetism-files/"];
function emailCta(raw,issue){
 if(!Number.isInteger(issue)||issue<1||issue>6||typeof raw!=="string")return false;
 const prefix="https://finalvestige.com", idx=raw.indexOf("?");
 if(!raw.startsWith(prefix+"/")||idx<0||raw.includes("#"))return false;
 if(!PATHS.includes(raw.slice(prefix.length,idx)))return false;
 const parts=raw.slice(idx+1).split("&");if(parts.length!==4)return false;
 const out={};for(const part of parts){const p=part.split("=");if(p.length!==2||
  !/^utm_(?:source|medium|campaign|content)$/.test(p[0])||Object.hasOwn(out,p[0])||!p[1]||
  !/^[A-Za-z0-9_-]+$/.test(p[1]))return false;out[p[0]]=p[1];}
 return Object.keys(out).length===4&&out.utm_source==="dispatch"&&out.utm_medium==="email"&&
 out.utm_campaign==="dispatch_mind_pilot_2026_11"&&
 out.utm_content==="issue"+String(issue).padStart(2,"0");
}
function plan(x){
 return Array.isArray(x)&&x.length===6&&x.every((v,i)=>v.number===i+1&&
 v.kind===([3,5].includes(i+1)?"commercial_reserved":"editorial")&&
 v.status===([3,5].includes(i+1)?"HOLD_MERCHANT":"HOLD"));
}
const RECEIPT_FIELDS=["html_checked","plaintext_checked","footer_verified",
 "publisher_postal_verified","optout_link_function_verified","unsubscribe_suppression_verified"];
function receipt(r){
 if(!r||r.kind!=="actual_jetpack_received_newsletter"||r.origin!=="authorised_receipt_rfc5322")
  return {verified:false,reason:"NOT_RECEIVED_NEWSLETTER"};
 const missing=RECEIPT_FIELDS.filter(f=>r[f]!==true);
 return {verified:!missing.length,reason:missing.length?"MISSING_"+missing.join(","):"SELF_ATTESTED_REQUIRES_INDEPENDENT_REVIEW"};
}
const OFFER_FIELDS=["rights_cleared","merchant_active","live_offer_url_verified",
 "fulfillment_verified","refund_terms_verified","merchant_paid_order_reporting",
 "email_permission_if_affiliate","privacy_review","published_presell_guide_verified"];
function offer(x){
 if(!Array.isArray(x)||x.length!==1)return {eligible:false,reason:"ONE_OFFER_REQUIRED"};
 if(!x[0]||typeof x[0].id!=="string"||!x[0].id.trim())return {eligible:false,reason:"INVALID_OFFER_ID"};
 const missing=OFFER_FIELDS.filter(f=>x[0][f]!==true);
 return {eligible:missing.length===0,reason:missing.length?missing.join(","):"SELF_ATTESTED_NOT_MERCHANT_VERIFIED"};
}
function release(i){
 const x=i||{},missing=[];
 if(!plan(x.editions))missing.push("EXACT_SIX_SLOT_VERSION");
 if(!x.founder_creative||!x.founder_send||!x.founder_audience)missing.push("FOUNDER_APPROVAL");
 if(!x.authoritative_eligible_recipients)missing.push("REACHABLE_RECIPIENTS");
 if(!x.welcome_received_and_pdf_opened)missing.push("RECEIVED_WELCOME_PDF");
 if(!x.native_jetpack_preview)missing.push("REAL_EXCERPT_PREVIEW");
 if(!receipt(x.receipt).verified)missing.push("RECEIVED_LEGAL_FOOTER_OPT_OUT");
 if(!x.one_approved_offer)missing.push("SINGLE_VERIFIED_OFFER");
 return {status:"HOLD_UNSENT",missing,send_enabled:false};
}
root.FVDispatchR107={subscribers,socialUtm,emailCta,plan,receipt,offer,release};
})(typeof globalThis==="object"?globalThis:this);
