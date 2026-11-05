"use strict";
/**
 * UNPUBLISHED offline reconciliation contract. No browser scripts, cookies,
 * visitor IDs, merchant credentials, or network calls.
 * Use only aggregate, independently evidenced merchant settlements.
 */
const K=["date","asset_id","utm_campaign"];
const PII=/\b(?:email|e-?mail|phone|address|ip_address|user_agent|buyer_id|customer_id|first_name|last_name|fullname|session_id)\b/i;
const DATE=/^\d{4}-\d{2}-\d{2}$/;
const ID=/^[a-z0-9][a-z0-9_-]{2,80}$/i;
function assertClean(o,kind){
 if(!o||typeof o!=="object"||Array.isArray(o))throw Error(kind+": object required");
 for(const key of Object.keys(o))if(PII.test(key))throw Error(kind+": buyer/visitor identifier forbidden: "+key);
 for(const key of K)if(typeof o[key]!=="string"||(key==="date"?!DATE.test(o[key]):!ID.test(o[key])))throw Error(kind+": invalid "+key);
 if(!Number.isFinite(Date.parse(o.date+"T00:00:00Z")))throw Error(kind+": invalid date");
 if(o.date>new Date().toISOString().slice(0,10))throw Error(kind+": future cohort");
}
function whole(n,k){if(!Number.isSafeInteger(n)||n<0)throw Error(k+" must be a nonnegative safe integer");return n;}
function validateSession(s){
 assertClean(s,"session");whole(s.qualified_human_sessions,"qualified_human_sessions");
 if(s.qualified_human_sessions>100000000)throw Error("implausible aggregate sessions");
 if(s.audit_status!=="verified_human_exclusion")throw Error("qualified human exclusion not verified");
 if(!/^audit:[a-z0-9_-]{5,80}$/i.test(s.proof_ref||""))throw Error("first-party proof_ref missing");
 return s;
}
function validateSettlement(s){
 assertClean(s,"settlement");
 if(!["affiliate","first_party"].includes(s.offer_type))throw Error("invalid offer_type");
 if(s.authorization!==true||s.statement_verified!==true||s.complete!==true)throw Error("missing partner permission or complete merchant proof");
 if(!/^merchant:[a-z0-9_-]{5,80}$/i.test(s.proof_ref||""))throw Error("merchant proof_ref missing");
 for(const k of ["paid_orders","gross_cents","refund_cents","fees_cents","commission_cents"])whole(s[k],k);
 if(s.offer_type==="affiliate"&&s.gross_cents!==0)throw Error("affiliate gross sales not earned revenue");
 if(s.offer_type==="first_party"&&s.commission_cents!==0)throw Error("first-party cannot count affiliate commission");
 const proceeds=s.offer_type==="affiliate"?s.commission_cents:s.gross_cents;
 if(s.refund_cents+ s.fees_cents>proceeds)throw Error("negative net cohort requires explicit adjustment ledger");
 return s;
}
function key(s){return K.map(k=>s[k]).join("|");}
function reconcile({sessions,settlements,period_days=7,as_of}){
 if(![7,30].includes(period_days))throw Error("only 7/30 day cohort windows supported");
 if(!DATE.test(as_of||"")||!Number.isFinite(Date.parse(as_of+"T00:00:00Z")))throw Error("as_of date required");
 if(as_of>new Date().toISOString().slice(0,10))throw Error("as_of cannot be future");
 if(!Array.isArray(sessions)||!Array.isArray(settlements))throw Error("arrays required");
 // Only completed dates; caller must prove complete coverage of source/merchant statements.
 const start=new Date(Date.parse(as_of+"T00:00:00Z")-(period_days-1)*86400000).toISOString().slice(0,10);
 const inside=x=>x.date>=start&&x.date<=as_of;
 const sx=sessions.filter(inside).map(validateSession), mx=settlements.filter(inside).map(validateSettlement);
 const unique=new Set();
 for(const s of sx){if(unique.has("s:"+key(s)))throw Error("duplicate session cohort");unique.add("s:"+key(s));}
 for(const s of mx){const k="m:"+key(s)+":"+s.offer_type;if(unique.has(k))throw Error("duplicate settlement cohort");unique.add(k);}
 if(!sx.length||!mx.length)return {status:"NOT_COMPUTABLE",period_days,reason:"Missing verified qualified human denominator or merchant settlement"};
 const sKeys=new Set(sx.map(key));
 if(mx.some(x=>!sKeys.has(key(x))))return {status:"NOT_COMPUTABLE",period_days,reason:"Merchant cohort cannot be matched to qualified first-party session cohort"};
 if(!mx.every(x=>x.statement_verified&&x.complete))return {status:"NOT_COMPUTABLE",period_days,reason:"Incomplete authoritative merchant records"};
 const qualified=sx.reduce((t,x)=>t+x.qualified_human_sessions,0);
 if(qualified===0)return {status:"NOT_COMPUTABLE",period_days,reason:"Zero qualified-human denominator"};
 const orders=mx.reduce((t,x)=>t+x.paid_orders,0);
 const earned=mx.reduce((t,x)=>t+(x.offer_type==="affiliate"?x.commission_cents:x.gross_cents),0);
 const refunds=mx.reduce((t,x)=>t+x.refund_cents,0),fees=mx.reduce((t,x)=>t+x.fees_cents,0);
 return {status:"VERIFIED_AGGREGATE_ONLY",period_days,start_date:start,end_date:as_of,qualified_human_sessions:qualified,confirmed_paid_orders:orders,earned_gross_cents:earned,refund_cents:refunds,fees_cents:fees,realized_net_cents:earned-refunds-fees,paid_conversion_rate:orders/qualified,net_revenue_per_1000_qualified_sessions_cents:Math.round((earned-refunds-fees)*1000/qualified),sample_warning:qualified<1000||orders<30?"TINY_SAMPLE":"",limitation:"Aggregate outcomes only; does not identify individual customers or prove per-visitor causal attribution"};
}
module.exports={validateSession,validateSettlement,reconcile};
