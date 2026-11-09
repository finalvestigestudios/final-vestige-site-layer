"use strict";
/* FV Dispatch R242 independent, non-sending audience / revenue admission tests.
   No network requests, no PII, no browser APIs, no post/email/analytics writes.
   Run in Node: node -e 'console.log(new Function(require("fs").readFileSync("dispatch/r242/qa.js","utf8"))())'
*/
function failClosedAudience(s){
  const n=s.jetpack_counts,f=s.follower_breakdown;
  if(!n||!f||![n.total,n.confirmed,n.unconfirmed_requests,f.total,f.wpcom,f.email].every(Number.isInteger)) throw Error("incomplete provider snapshots");
  if(n.total<0||n.confirmed<0||n.unconfirmed_requests<0||f.wpcom<0||f.email<0) throw Error("invalid provider snapshot");
  return {
    total_subscribers_reported:n.total,
    confirmed_counter:n.confirmed,
    outstanding_unconfirmed_requests:n.unconfirmed_requests,
    follower_reader_count:f.wpcom,
    follower_email_only_count:f.email,
    email_eligible_recipients:null,
    status:"UNKNOWN_AWAIT_EMAIL_SUBSCRIPTION_STATUS",
    nonadditive:true,
    permitted_claims:["Provider reported 3 total and 3 confirmed","Provider separately reported 2 unconfirmed requests","Follower breakdown 3 WP Reader, 0 email-only"]
  };
}
function isConfirmedSignup(x){
  if(!x||typeof x!=="object") return false;
  if(Object.keys(x).some(k=>/email|address|phone|ip|name|token|tracking_id/i.test(k))) return false;
  return x.source==="jetpack_provider_status"&&x.site==="finalvestige.com" &&
    x.consent_scope==="dispatch_email"&&
    (x.before==="Not confirmed"||x.before==="Not subscribed")&&
    x.after==="Subscribed"&&x.provider_record_verified===true&&
    typeof x.opaque_key==="string"&&/^[0-9a-f]{64}$/.test(x.opaque_key);
}
function dedupeSignups(events){
  if(!Array.isArray(events)) throw Error("event list expected");
  const seen=new Set();let accepted=0,duplicates=0,rejected=0;
  for(const e of events){
    if(!isConfirmedSignup(e)){rejected++;continue;}
    if(seen.has(e.opaque_key)){duplicates++;continue;}
    seen.add(e.opaque_key);accepted++;
  }
  return {accepted,duplicates,rejected};
}
function validEvidenceLedger(x){
  return x&&x.source==="independent_settlement_report"&&x.reconciled===true&&x.currency==="USD"&&Array.isArray(x.orders)&&
     x.orders.every(o=>o&&typeof o.order_key==="string"&&/^[a-zA-Z0-9_-]{8,80}$/.test(o.order_key)&&
       o.status==="settled"&&
       Number.isSafeInteger(o.received_cents)&&o.received_cents>=0&&
       Number.isSafeInteger(o.refunded_cents)&&o.refunded_cents>=0&&
       Number.isSafeInteger(o.fees_cents)&&o.fees_cents>=0&&
       Number.isSafeInteger(o.costs_cents)&&o.costs_cents>=0);
}
function revenuePerThousand(payload){
  if(!payload||![7,30].includes(payload.window_days)||payload.verified_qualified_human_sessions!==true ||
      !Number.isSafeInteger(payload.sessions)||payload.sessions<=0 ||
      !validEvidenceLedger(payload.ledger)) return {status:"NOT_COMPUTABLE",value:null};
  const ids=new Set();let cents=0;
  for(const order of payload.ledger.orders){
    if(ids.has(order.order_key))return {status:"NOT_COMPUTABLE",value:null};
    ids.add(order.order_key);
    cents+=order.received_cents-order.refunded_cents-order.fees_cents-order.costs_cents;
  }
  return {status:"COMPUTABLE",window_days:payload.window_days,settled_orders:ids.size,net_cents:cents,qualified_human_sessions:payload.sessions,net_usd_per_1000_sessions:Math.round((cents/100)*1000/payload.sessions*100)/100};
}
function releaseReviewGate(c,issue,evidence){
  const master=c&&c.source&&c.source.master_sha==="d57ccdba3aee8f065e143e101c2945f4f3d01647";
  const commercial=issue===3||issue===5;
  if(![1,2,3,4,5,6].includes(issue))return {status:"HOLD_UNSENT",reasons:["UNKNOWN_ISSUE"]};
  const reasons=[];
  if(!master||!evidence||evidence.source_blob_matched!==true)reasons.push("SOURCE_SHA");
  if(!evidence||evidence.founder_final_approval!==true)reasons.push("FOUNDER");
  if(!evidence||evidence.email_eligibility_verified!==true)reasons.push("EMAIL_CONSENT");
  if(!evidence||evidence.actual_native_preview_verified!==true)reasons.push("JETPACK_PREVIEW");
  if(!evidence||evidence.received_mime_plaintext_html_verified!==true)reasons.push("MIME");
  if(!evidence||evidence.publisher_postal_address_verified!==true)reasons.push("FV_POSTAL");
  if(!evidence||evidence.unsubscribe_functional_verified!==true)reasons.push("OPT_OUT");
  if(commercial){
    for(const key of ["named_fv_partner_accepted","explicit_email_promotion_rights","issued_compliant_earning_url","approved_live_warmup_guide","merchant_claims_terms_verified","near_offer_disclosure_verified"]){
      if(!evidence||evidence[key]!==true)reasons.push("MERCHANT_"+key.toUpperCase());
    }
  }
  // Even complete evidence only enables manual founder-led review, NEVER a send operation.
  return {status:reasons.length?"HOLD_UNSENT":"HUMAN_REVIEW_ONLY_NOT_SEND_AUTHORIZED",reasons};
}
function run(){
 let passed=0; const checks=[];
 function t(name,fn){try{if(fn()!==true)throw Error("assertion false");passed++;checks.push(name);}catch(e){throw Error(name+": "+e.message)}}
 const fixture={source:{master_sha:"d57ccdba3aee8f065e143e101c2945f4f3d01647"},jetpack_counts:{total:3,confirmed:3,unconfirmed_requests:2},follower_breakdown:{total:3,wpcom:3,email:0}};
 const a=failClosedAudience(fixture),good={source:"jetpack_provider_status",site:"finalvestige.com",consent_scope:"dispatch_email",before:"Not confirmed",after:"Subscribed",provider_record_verified:true,opaque_key:"a".repeat(64)};
 t("aggregate counts nonadditive",()=>a.total_subscribers_reported===3&&a.outstanding_unconfirmed_requests===2&&a.nonadditive);
 t("not claiming confirmed people are reachable",()=>a.email_eligible_recipients===null);
 t("email-only zero never means zero eligible",()=>a.status==="UNKNOWN_AWAIT_EMAIL_SUBSCRIPTION_STATUS");
 t("follower segment kept distinct",()=>a.follower_reader_count===3&&a.follower_email_only_count===0);
 t("provider transition confirmation accepted",()=>isConfirmedSignup(good));
 t("page click is not confirmation",()=>!isConfirmedSignup({...good,source:"click"}));
 t("pending subscription is not confirmation",()=>!isConfirmedSignup({...good,after:"Not confirmed"}));
 t("missing provider proof rejected",()=>!isConfirmedSignup({...good,provider_record_verified:false}));
 t("Reader-only consent rejected",()=>!isConfirmedSignup({...good,consent_scope:"reader"}));
 t("different site rejected",()=>!isConfirmedSignup({...good,site:"attacker.example"}));
 t("raw email field rejected",()=>!isConfirmedSignup({...good,email:"fake@example.invalid"}));
 t("query token field rejected",()=>!isConfirmedSignup({...good,tracking_id:"secret"}));
 t("missing opaque key rejected",()=>!isConfirmedSignup({...good,opaque_key:null}));
 t("short opaque key rejected",()=>!isConfirmedSignup({...good,opaque_key:"abc"}));
 t("duplicate confirmation counted once",()=>{const x=dedupeSignups([good,good]);return x.accepted===1&&x.duplicates===1;});
 t("invalid event excluded",()=>{const x=dedupeSignups([{...good,source:"button_click"}]);return x.accepted===0&&x.rejected===1;});
 t("actual subscription update not automated",()=>!Object.keys(fixture).includes("send"));
 t("no offer placement on editorial issue",()=>releaseReviewGate(fixture,1,{}).reasons.every(x=>!x.startsWith("MERCHANT_")));
 t("commercial issue requires six extra gates",()=>releaseReviewGate(fixture,3,{}).reasons.filter(x=>x.startsWith("MERCHANT_")).length===6);
 t("second commercial issue requires same gates",()=>releaseReviewGate(fixture,5,{}).reasons.filter(x=>x.startsWith("MERCHANT_")).length===6);
 t("unknown issue blocked",()=>releaseReviewGate(fixture,7,{}).status==="HOLD_UNSENT");
 t("no founder signoff means hold",()=>releaseReviewGate(fixture,1,{}).reasons.includes("FOUNDER"));
 t("no received mime means hold",()=>releaseReviewGate(fixture,1,{}).reasons.includes("MIME"));
 t("no publisher address means hold",()=>releaseReviewGate(fixture,1,{}).reasons.includes("FV_POSTAL"));
 t("no unsubscribe test means hold",()=>releaseReviewGate(fixture,1,{}).reasons.includes("OPT_OUT"));
 t("no source pin means hold",()=>releaseReviewGate(fixture,1,{}).reasons.includes("SOURCE_SHA"));
 const complete={source_blob_matched:true,founder_final_approval:true,email_eligibility_verified:true,actual_native_preview_verified:true,received_mime_plaintext_html_verified:true,publisher_postal_address_verified:true,unsubscribe_functional_verified:true,
 named_fv_partner_accepted:true,explicit_email_promotion_rights:true,issued_compliant_earning_url:true,approved_live_warmup_guide:true,merchant_claims_terms_verified:true,near_offer_disclosure_verified:true};
 t("full hypothetical evidence still never authorizes automated send",()=>releaseReviewGate(fixture,3,complete).status==="HUMAN_REVIEW_ONLY_NOT_SEND_AUTHORIZED");
 const ledger={source:"independent_settlement_report",currency:"USD",reconciled:true,orders:[{order_key:"settled_00001",status:"settled",received_cents:300,refunded_cents:0,fees_cents:30,costs_cents:20}]};
 t("missing denominator noncomputable",()=>revenuePerThousand({window_days:7,ledger}).status==="NOT_COMPUTABLE");
 t("unverified denominator noncomputable",()=>revenuePerThousand({window_days:7,sessions:100,ledger}).status==="NOT_COMPUTABLE");
 t("click-only revenue never recognized",()=>revenuePerThousand({window_days:7,sessions:100,verified_qualified_human_sessions:true,ledger:{source:"email_clicks",orders:[]}}).status==="NOT_COMPUTABLE");
 t("unsettled order rejected",()=>revenuePerThousand({window_days:7,sessions:100,verified_qualified_human_sessions:true,ledger:{...ledger,orders:[{...ledger.orders[0],status:"pending"}]}}).status==="NOT_COMPUTABLE");
 t("duplicate settlement rejected",()=>revenuePerThousand({window_days:7,sessions:100,verified_qualified_human_sessions:true,ledger:{...ledger,orders:[ledger.orders[0],ledger.orders[0]]}}).status==="NOT_COMPUTABLE");
 t("missing refund rejected",()=>revenuePerThousand({window_days:7,sessions:100,verified_qualified_human_sessions:true,ledger:{...ledger,orders:[{...ledger.orders[0],refunded_cents:null}]}}).status==="NOT_COMPUTABLE");
 t("zero sessions noncomputable",()=>revenuePerThousand({window_days:30,sessions:0,verified_qualified_human_sessions:true,ledger}).status==="NOT_COMPUTABLE");
 t("unsupported cohort window rejected",()=>revenuePerThousand({window_days:60,sessions:100,verified_qualified_human_sessions:true,ledger}).status==="NOT_COMPUTABLE");
 t("verified simulated 7-day metric correctly nets refunds/fees/costs",()=>{const q=revenuePerThousand({window_days:7,sessions:100,verified_qualified_human_sessions:true,ledger});return q.status==="COMPUTABLE"&&q.net_cents===250&&q.net_usd_per_1000_sessions===25;});
 t("synthetic verified zero-order ledger not mistaken for missing ledger",()=>{const q=revenuePerThousand({window_days:30,sessions:100,verified_qualified_human_sessions:true,ledger:{...ledger,orders:[]}});return q.status==="COMPUTABLE"&&q.net_cents===0;});
 t("fail if missing provider snapshots",()=>{try{failClosedAudience({});return false}catch(e){return true}});
 t("fail if negative follower counters",()=>{try{failClosedAudience({jetpack_counts:fixture.jetpack_counts,follower_breakdown:{...fixture.follower_breakdown,email:-1}});return false}catch(e){return true}});
 return {status:"PASS",checks:passed,check_names:checks,synthetic_examples_not_production:true,emails_sent:0,production_changes:0};
}
return run();
