'use strict';
// OFFLINE ONLY. No network, tracking cookies, user identifiers, subscriber or merchant credentials.
// "qualified_sessions" must be independently reconciled by the first-party analytics owner.
// "paid_orders" must be independently settled and reconciled from Payhip/merchant reports.
// This module is not wired to WordPress and must not infer a purchase from a CTA or a click.
function isNonnegativeInt(v){return Number.isSafeInteger(v) && v>=0;}
function requireProof(p,scope){return Boolean(p && p.status==='VERIFIED' && p.scope===scope && typeof p.reference==='string' && p.reference.length>=6 && /^[a-zA-Z0-9._:/#-]+$/.test(p.reference));}
function summarizeCohort(cohort){
 if (!cohort || ![7,30].includes(cohort.days)) return {status:'NOT_COMPUTABLE',reason:'unsupported cohort'};
 if (!/^2026-\d{2}-\d{2}$/.test(cohort.start_date||'') || !/^2026-\d{2}-\d{2}$/.test(cohort.end_date||''))return {status:'NOT_COMPUTABLE',reason:'date evidence missing'};
 if(!isNonnegativeInt(cohort.qualified_sessions)||cohort.qualified_sessions===0||!requireProof(cohort.session_proof,'qualified_human_sessions'))return {status:'NOT_COMPUTABLE',reason:'no independent qualified-human session denominator'};
 if(!isNonnegativeInt(cohort.orders_confirmed)|| !isNonnegativeInt(cohort.gross_cents)||!isNonnegativeInt(cohort.refunds_cents)||!isNonnegativeInt(cohort.fees_cents)||!isNonnegativeInt(cohort.settled_cents))return {status:'NOT_COMPUTABLE',reason:'merchant amounts or order count missing'};
 if(!requireProof(cohort.merchant_proof,'settled_orders_fees_refunds'))return {status:'NOT_COMPUTABLE',reason:'merchant settlement evidence missing'};
 if(cohort.refunds_cents+cohort.fees_cents>cohort.gross_cents||cohort.gross_cents-cohort.refunds_cents-cohort.fees_cents!==cohort.settled_cents)return {status:'INVALID',reason:'settlement reconciliation failed'};
 if(cohort.orders_confirmed>cohort.qualified_sessions)return {status:'INVALID',reason:'attribution denominator conflict'};
 const net=cohort.settled_cents/100;
 return {status:'VERIFIED',days:cohort.days,qualified_sessions:cohort.qualified_sessions,orders_confirmed:cohort.orders_confirmed,net_usd:net,paid_conversion_rate:cohort.orders_confirmed/cohort.qualified_sessions,net_revenue_per_1000_qualified_sessions_usd:Math.round((net*1000/cohort.qualified_sessions)*100)/100,warning:cohort.orders_confirmed<30||cohort.qualified_sessions<1000?'TINY_SAMPLE_DONT_INFER_CAUSAL_LIFT':null};
}
function safeCampaign(input){
 const allowed=/^[a-z0-9][a-z0-9_-]{1,79}$/;
 if(!input||!['youtube','tiktok','instagram','facebook','pinterest','x','bluesky'].includes(input.utm_source)||input.utm_medium!=='organic_social'||!allowed.test(input.utm_campaign||'')||!allowed.test(input.asset_id||''))return null;
 return {utm_source:input.utm_source,utm_medium:'organic_social',utm_campaign:input.utm_campaign,utm_content:input.asset_id};
}
// Never accept an affiliate_click, PDF reveal, generic signup count or analytics pageview as paid settlement proof.
module.exports={summarizeCohort,safeCampaign};
