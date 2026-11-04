"use strict";
/* NO SEND; NO NETWORK; NO LIST ACCESS. All outputs review candidates only. */
const FOCUS="https://finalvestige.com/focus/";
const PDF="https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf";
const editorial=Object.freeze({1:"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",2:"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",4:"https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/",6:PDF});
function result(status,url=null){return Object.freeze({status,candidate_url:url,allowed_to_send:false,confirmed_signup:false,paid_sale:false});}
function emailCandidate({issue,state,consent,eligible,pdf_http_verified}={}){
 const n=Number(issue);
 if(!Number.isInteger(n)||n<1||n>6)return result("HOLD_INVALID_ISSUE");
 if(n===3||n===5)return result("HOLD_MERCHANT");
 if(["suppressed","unsubscribed"].includes(state))return result("HOLD_SUPPRESSION");
 if(state!=="subscribed_email"||consent!==true||eligible!==true)return result("HOLD_ELIGIBILITY");
 if(n===6&&pdf_http_verified!==true)return result("HOLD_PDF_HTTP");
 return result("REVIEW_ONLY",editorial[n]);
}
function socialCandidate({platform,asset_id,cluster="mind"}={}){
 const channels=["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"];
 if(!channels.includes(platform))return result("HOLD_PLATFORM");
 if(typeof asset_id!=="string"||!/^[A-Za-z0-9][A-Za-z0-9_-]{2,63}$/.test(asset_id))return result("HOLD_ASSET_ID");
 if(!["mind","mysteries","history","preparedness"].includes(cluster))return result("HOLD_CLUSTER");
 const params={utm_source:platform,utm_medium:"organic_social",utm_campaign:cluster+"_pilot_2026_11",utm_content:asset_id};
 return result("REVIEW_ONLY",FOCUS+"?"+Object.entries(params).map(([k,v])=>k+"="+encodeURIComponent(v)).join("&"));
}
function evidenceEvent(kind,settled=false){
 return Object.freeze({kind:kind||"unknown",confirmed_signup:kind==="authoritative_wordpress_optin",paid_sale:kind==="merchant_order"&&settled===true,realized_net_revenue:null});
}
function apolloSubject(subject){
 if(typeof subject!=="string"||!subject.trim())return "HOLD_SUBJECT";
 if(/fourteen\s+seconds/i.test(subject))return "HOLD_NUMERIC_PROVENANCE";
 return "REVIEW_ONLY";
}
function fieldbookMedia(m){
 return Object.freeze({metadata_found:!!m&&m.id===1737&&m.mime_type==="application/pdf"&&m.source_url===PDF&&m.filesize===599946,http_verified:false,page_count_verified:false,inbox_received:false});
}
module.exports=Object.freeze({FOCUS,PDF,editorial,emailCandidate,socialCandidate,evidenceEvent,apolloSubject,fieldbookMedia});
