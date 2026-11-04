'use strict';
/** Offline-only acceptance arithmetic for aggregate merchant evidence; NOT web instrumentation.
 * Never put order ID, buyer ID, email, IP or query strings here.
 * Run: node --test mind/r114/revenue-math.test.cjs
 */
const ALLOWED_EVENTS=Object.freeze(['qualified_landing','relevant_guide_click','confirmed_lead','affiliate_outbound_click','verified_merchant_order','verified_affiliate_commission','refund','fee']);
const ALLOWED_KEYS=new Set(['utm_source','utm_medium','utm_campaign','utm_content_asset_id','landing_slug','offer_slug','cohort_day','event_name']);
function validateSafeEvent(event) {
 if (!event || typeof event!=='object'||Array.isArray(event)) return false;
 if(Object.keys(event).some(k=>!ALLOWED_KEYS.has(k)))return false;
 if(!ALLOWED_EVENTS.includes(event.event_name))return false;
 if(Object.values(event).some(v=>typeof v!=='string'&&typeof v!=='number'))return false;
 if(event.utm_content_asset_id!==undefined&&!/^[A-Za-z0-9_-]{4,80}$/.test(String(event.utm_content_asset_id)))return false;
 if(event.utm_medium!==undefined && event.utm_medium!=='organic_social') return false;
 return true;
}
function nonNegInteger(n) {return Number.isSafeInteger(n)&&n>=0;}
function confirmedRevenue(cohort) {
 if(!cohort || cohort.source_proof!=='merchant_reconciled_and_firstparty_qualified' || cohort.attribution!=='verified')return {status:'NOT_COMPUTABLE',reason:'missing source or verified attribution',net_per_1000_cents:null};
 if(![7,30].includes(cohort.cohort_days))return {status:'NOT_COMPUTABLE',reason:'not an approved cohort',net_per_1000_cents:null};
 const money=['owned_gross_settled_cents','affiliate_commission_settled_cents','refunds_cents','chargebacks_cents','platform_fees_cents'];
 if(!money.every(k=>nonNegInteger(cohort[k])))return {status:'NOT_COMPUTABLE',reason:'missing or invalid financial components',net_per_1000_cents:null};
 if(!nonNegInteger(cohort.confirmed_paid_orders)||!nonNegInteger(cohort.qualified_human_sessions)||cohort.qualified_human_sessions===0)return {status:'NOT_COMPUTABLE',reason:'missing valid buyer/session counts',net_per_1000_cents:null};
 if(cohort.confirmed_paid_orders>cohort.qualified_human_sessions)return {status:'NOT_COMPUTABLE',reason:'order/session anomaly, audit attribution',net_per_1000_cents:null};
 if(cohort.qualified_human_sessions<20)return {status:'SUPPRESSED_SMALL_CELL',reason:'aggregate cell under 20 qualified sessions',net_per_1000_cents:null};
 const net=cohort.owned_gross_settled_cents+cohort.affiliate_commission_settled_cents-cohort.refunds_cents-cohort.chargebacks_cents-cohort.platform_fees_cents;
 return {status:'COMPUTABLE_WITH_SOURCE_EVIDENCE',net_settled_cents:net,
 net_per_1000_cents:Math.round(1000*net/cohort.qualified_human_sessions),
 confirmed_paid_order_rate:cohort.confirmed_paid_orders/cohort.qualified_human_sessions,
 small_sample_warning:cohort.qualified_human_sessions<200||cohort.confirmed_paid_orders<20};
}
module.exports={validateSafeEvent,confirmedRevenue};
