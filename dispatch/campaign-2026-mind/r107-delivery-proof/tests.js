/* Synthetic source-safe tests; run by Node or an independent JS runtime. */
(function(root){"use strict";
function run(g){const a=[];const check=(name,f)=>{try{if(!f())throw Error("assertion failed");a.push({name,ok:true})}
 catch(e){a.push({name,ok:false,error:String(e)})}};
const p=Array.from({length:6},(_,i)=>({number:i+1,kind:[3,5].includes(i+1)?"commercial_reserved":"editorial",status:[3,5].includes(i+1)?"HOLD_MERCHANT":"HOLD"}));
const s={total:2,confirmed:2,unconfirmed:2,suppressed:0,readerFollowers:2,emailFollowers:0};
const c={utm_source:"youtube",utm_medium:"organic_social",utm_campaign:"mind_pilot_2026_11",utm_content:"YT_01"};
const url=n=>"https://finalvestige.com/focus/?utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue"+String(n).padStart(2,"0");
const r={kind:"actual_jetpack_received_newsletter",origin:"authorised_receipt_rfc5322",html_checked:true,plaintext_checked:true,footer_verified:true,publisher_postal_verified:true,optout_link_function_verified:true,unsubscribe_suppression_verified:true};
const o={id:"synthetic_only",rights_cleared:true,merchant_active:true,live_offer_url_verified:true,fulfillment_verified:true,refund_terms_verified:true,merchant_paid_order_reporting:true,email_permission_if_affiliate:true,privacy_review:true,published_presell_guide_verified:true};
check("ambiguous counts never equal reachable",()=>g.subscribers(s).reachable===null);
check("conflicting totals kept",()=>g.subscribers(s).unconfirmed===2&&g.subscribers(s).total===2);
check("negative counts invalid",()=>g.subscribers({...s,confirmed:-1}).status==="INVALID_AGGREGATES");
check("fractional counts invalid",()=>g.subscribers({...s,total:2.2}).status==="INVALID_AGGREGATES");
check("zero recipients not invented",()=>g.subscribers({...s,total:0,confirmed:0,unconfirmed:0}).reachable===null);
check("social UTM valid",()=>g.socialUtm(c));
for(const [name,mutation] of [["unknown source",{utm_source:"pinterest_ad"}],["email medium",{utm_medium:"email"}],
 ["wrong month",{utm_campaign:"mind_pilot_2026_10"}],["blank asset",{utm_content:""}],
 ["email PII",{utm_content:"name@example.com"}],["visitor id",{visitor:"x"}]])
 check("social invalid "+name,()=>!g.socialUtm({...c,...mutation}));
check("six issues preserved",()=>g.plan(p));
check("commercial promotion blocked",()=>!g.plan(p.map(v=>({...v,...(v.number===3?{status:"READY"}:{})}))));
check("missing issue blocked",()=>!g.plan(p.slice(1)));
check("wrong issue type blocked",()=>!g.plan(p.map(v=>({...v,...(v.number===5?{kind:"editorial"}:{})}))));
for(const n of [1,2,3,4,5,6])check("email valid issue "+n,()=>g.emailCta(url(n),n));
check("reject wrong issue",()=>!g.emailCta(url(1),2));
check("reject user PII",()=>!g.emailCta(url(1)+"&email=alice%40example.com",1));
check("reject affiliate merchant",()=>!g.emailCta(url(3).replace("finalvestige.com","zen12.com"),3));
check("reject lookalike domain",()=>!g.emailCta(url(3).replace("finalvestige.com","finalvestige.com.evil.org"),3));
check("reject http",()=>!g.emailCta(url(3).replace("https","http"),3));
check("reject unverified guide",()=>!g.emailCta(url(3).replace("/focus/","/mind/zen12-guide/"),3));
check("reject duplicate params",()=>!g.emailCta(url(1)+"&utm_content=issue01",1));
check("reject fragments",()=>!g.emailCta(url(1)+"#a",1));
check("reject encoded identifier",()=>!g.emailCta(url(2).replace("issue02","%69ssue02"),2));
check("confirmation email is not newsletter",()=>!g.receipt({...r,kind:"subscription_confirmation"}).verified);
check("static HTML not actual receipt",()=>!g.receipt({...r,origin:"offline_preview"}).verified);
check("full synthetic receipt model only self attested",()=>g.receipt(r).reason==="SELF_ATTESTED_REQUIRES_INDEPENDENT_REVIEW");
for(const k of ["html_checked","plaintext_checked","footer_verified","publisher_postal_verified","optout_link_function_verified","unsubscribe_suppression_verified"])
 check("reject missing "+k,()=>!g.receipt({...r,[k]:false}).verified);
check("one fully attested synthetic offer",()=>g.offer([o]).eligible);
check("zero offers rejected",()=>!g.offer([]).eligible);
check("two offers rejected",()=>!g.offer([o,o]).eligible);
for(const k of ["rights_cleared","merchant_active","live_offer_url_verified","fulfillment_verified","refund_terms_verified","merchant_paid_order_reporting","email_permission_if_affiliate","privacy_review","published_presell_guide_verified"])
 check("reject offer missing "+k,()=>!g.offer([{...o,[k]:false}]).eligible);
check("release always held",()=>g.release({editions:p}).status==="HOLD_UNSENT");
check("fabricated all true cannot enable send",()=>g.release({editions:p,founder_creative:true,founder_send:true,founder_audience:true,authoritative_eligible_recipients:true,welcome_received_and_pdf_opened:true,native_jetpack_preview:true,receipt:r,one_approved_offer:true}).send_enabled===false);
return {passed:a.filter(x=>x.ok).length,total:a.length,failed:a.filter(x=>!x.ok)};
}
root.FVDispatchR107Tests={run};
})(typeof globalThis==="object"?globalThis:this);

/* Optional native Node execution: node tests.js. Never sends or calls a network API. */
if (typeof process !== "undefined" && process.versions && process.versions.node &&
    typeof require === "function" && require.main === module) {
  require("./gate.js");
  const result = globalThis.FVDispatchR107Tests.run(globalThis.FVDispatchR107);
  console.log(JSON.stringify(result, null, 2));
  if (result.failed.length) process.exitCode = 1;
}
