"use strict";
const a=require("./route_contract.cjs");let passed=0;
function t(label,yes){if(!yes)throw Error("FAILED: "+label);passed++;}
const r=(issue,extra={})=>a.emailCandidate({issue,state:"subscribed_email",consent:true,eligible:true,pdf_http_verified:true,...extra});
for(const n of [1,2,4,6]){t("editorial "+n,r(n).status==="REVIEW_ONLY");t("first party "+n,r(n).candidate_url.startsWith("https://finalvestige.com/"));t("no send "+n,!r(n).allowed_to_send);}
for(const n of [3,5]){t("merchant hold "+n,r(n).status==="HOLD_MERCHANT");t("merchant no link "+n,r(n).candidate_url===null);}
t("existing subscriber gets PDF",r(6).candidate_url===a.PDF&&r(6).candidate_url!==a.FOCUS);
t("PDF retrieval proof required",r(6,{pdf_http_verified:false}).status==="HOLD_PDF_HTTP"&&r(6,{pdf_http_verified:false}).candidate_url===null);
for(const state of ["suppressed","unsubscribed"])t("suppressed "+state,r(6,{state}).status==="HOLD_SUPPRESSION");
for(const state of ["unconfirmed","reader_only","unknown"])t("ineligible "+state,r(6,{state}).status==="HOLD_ELIGIBILITY");
t("no consent",r(6,{consent:false}).status==="HOLD_ELIGIBILITY");
t("no reachability",r(6,{eligible:null}).status==="HOLD_ELIGIBILITY");
t("bad issue",r(7).status==="HOLD_INVALID_ISSUE");
t("bad issue name",r("X").status==="HOLD_INVALID_ISSUE");
t("no fabricated asset id",a.socialCandidate({platform:"tiktok"}).status==="HOLD_ASSET_ID");
t("no PII as asset id",a.socialCandidate({platform:"tiktok",asset_id:"user@example.com"}).candidate_url===null);
t("invalid platform",a.socialCandidate({platform:"other",asset_id:"asset_123"}).status==="HOLD_PLATFORM");
t("invalid cluster",a.socialCandidate({platform:"tiktok",asset_id:"asset_123",cluster:"wealth"}).status==="HOLD_CLUSTER");
const sc=a.socialCandidate({platform:"tiktok",asset_id:"asset_123"});
t("UTM medium",sc.candidate_url.includes("utm_medium=organic_social"));
t("UTM real ID",sc.candidate_url.includes("utm_content=asset_123"));
t("social candidate not live",sc.status==="REVIEW_ONLY"&&!sc.allowed_to_send);
for(const kind of ["fieldbook_download","pdf_open","form_submit","confirmation_click","affiliate_outbound"]){t("no signup "+kind,!a.evidenceEvent(kind).confirmed_signup);t("no sale "+kind,!a.evidenceEvent(kind).paid_sale);}
t("native confirmed lead",a.evidenceEvent("authoritative_wordpress_optin").confirmed_signup&&!a.evidenceEvent("authoritative_wordpress_optin").paid_sale);
t("unsettled no sale",!a.evidenceEvent("merchant_order",false).paid_sale);
t("settled still unknown net",a.evidenceEvent("merchant_order",true).realized_net_revenue===null);
t("original Apollo number blocked",a.apolloSubject("Fourteen seconds. A much longer explanation.")==="HOLD_NUMERIC_PROVENANCE");
t("nonnumeric title review",a.apolloSubject("Apollo 1: no simple cause")==="REVIEW_ONLY");
t("blank title blocked",a.apolloSubject("")==="HOLD_SUBJECT");
const m={id:1737,mime_type:"application/pdf",source_url:a.PDF,filesize:599946};
t("verified media metadata",a.fieldbookMedia(m).metadata_found);
t("not HTTP",!a.fieldbookMedia(m).http_verified);
t("not 52-page proof",!a.fieldbookMedia(m).page_count_verified);
t("not welcome receipt",!a.fieldbookMedia(m).inbox_received);
t("wrong size",!a.fieldbookMedia({...m,filesize:100}).metadata_found);
t("always no send",[1,2,3,4,5,6].every(n=>!r(n).allowed_to_send));
module.exports={passed};
if(require.main===module)console.log(passed+" synthetic assertions passed; no real sends or conversions");
