// R442 pure, offline-only conversion evidence evaluator. Never sends, stores or calls external services.
export const expected={editorial:[1,2,4,6],commercial:[3,5],issue03:"Zen12",issue05:"Hypnosis Live"};
export function classifySignup(x){
 if(!x||x.provider!=="jetpack"||x.event!=="newsletter_subscription_confirmed"||
    x.status!=="Subscribed"||x.email_subscriber!==true||x.consent_scope!=="dispatch"||
    x.consent_granted!==true||typeof x.opaque_transition_id!=="string"||
    x.opaque_transition_id.length<8||!Number.isFinite(Date.parse(x.observed_at||"")))
   return {confirmed:false,reason:"NO_AUTHORITATIVE_OPT_IN_TRANSITION"};
 return {confirmed:true,id:x.opaque_transition_id};
}
export function uniqueSignups(rows){
 if(!Array.isArray(rows)) return null;
 const keys=new Set();
 for(const x of rows){const z=classifySignup(x);if(z.confirmed) keys.add(z.id);}
 return keys.size;
}
export function qualifiedSocialTag(x){
 if(!x||typeof x!=="object")return false;
 return x.utm_medium==="organic_social"&&
  ["youtube","tiktok","instagram","facebook","pinterest","x","bluesky"].includes(x.utm_source)&&
  typeof x.utm_campaign==="string"&&/^[a-z0-9_]{6,80}$/.test(x.utm_campaign)&&
  typeof x.utm_content==="string"&&/^[A-Za-z0-9_-]{8,100}$/.test(x.utm_content);
}
export function netPerThousand(cohort){
 if(!cohort||!["7d","30d"].includes(cohort.window)||cohort.matured!==true||
    !Number.isInteger(cohort.qualified_human_sessions)||cohort.qualified_human_sessions<=0||
    !Array.isArray(cohort.settlements)||cohort.settlements.length===0) return null;
 let net=0;
 for(const s of cohort.settlements){
  if(s.source!=="independent_merchant_report"||s.state!=="settled"||
     typeof s.opaque_order_id!=="string"||s.opaque_order_id.length<3||
     ![s.gross,s.fees,s.refunds].every(n=>typeof n==="number"&&Number.isFinite(n)&&n>=0))
    return null;
  net+=s.gross-s.fees-s.refunds;
 }
 return Math.round(net*100000/cohort.qualified_human_sessions)/100;
}
export function commercialRelease(x){
 const required=["partner_approved","specific_email_permission","exact_sku",
 "merchant_issued_affiliate_url","live_approved_firstparty_guide","verified_current_terms",
 "merchant_claims_reviewed","fv_physical_address_in_received_email",
 "functional_optout_in_received_email","native_jetpack_preview","founder_final_release"];
 return {send_authorized:false,requirements_complete:required.every(k=>x?.[k]===true),
 missing:required.filter(k=>x?.[k]!==true),status:"HOLD_UNSENT"};
}
