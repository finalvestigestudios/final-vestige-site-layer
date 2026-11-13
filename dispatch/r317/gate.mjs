// Dispatch R317: NON-SENDING reviewer. Assesses claims and attribution, NEVER authorizes mail or purchases.
// Seller tier facts describe the November 12, 2026 official marketing page, not checkout/entitlement verification.
export const TIERS=Object.freeze({
 beginner:Object.freeze({levels:6,mp3s:24,portion:"first six"}),
 premium:Object.freeze({levels:12,mp3s:48,portion:"all twelve"}),
 advanced:Object.freeze({levels:6,mp3s:24,portion:"last six"})
});
export const CANONICAL_ISSUE03_BLOB="aeeef34efea0cc281f69901488e4501fea851245";
export function inspectTierClaims(copy=""){
 const problems=[];const s=String(copy);
 for(const sentence of s.split(/[\n.!?]+/).map(t=>t.toLowerCase().trim()).filter(Boolean)){
   if(/(?:zen12|program|package|tier).{0,75}(?:48\s*mp3|all\s*12\s*levels)/i.test(sentence)&&!/premium|complete|full\s+program|all\s+twelve\s+level/i.test(sentence))
     problems.push("UNQUALIFIED_FULL_PACKAGE");
   if(/(?:beginner|advanced).{0,70}(?:48\s*mp3|all\s*12\s*levels)/.test(sentence))
     problems.push("PARTIAL_TIER_MISDESCRIBED");
   if(/(?:premium).{0,70}(?:24\s*mp3|only\s*6\s*levels)/.test(sentence))
     problems.push("PREMIUM_MISDESCRIBED");
 }
 if(/(?:proven|guaranteed|clinically established).{0,45}(?:zen12|brainwave|same as an hour)/i.test(s))
   problems.push("UNSUBSTANTIATED_EFFICACY");
 if(/(?:zen12|inspire3).{0,80}(?:special discount|ends tonight|guaranteed results)/i.test(s))
   problems.push("UNVERIFIED_OFFER_OR_URGENCY");
 return [...new Set(problems)];
}
export function audienceSnapshot(d={}){
 const n=x=>Number.isInteger(x)&&x>=0?x:null;
 const total=n(d.total),confirmed=n(d.confirmed),unconfirmed=n(d.unconfirmed);
 const overlaid=total!==null&&confirmed!==null&&unconfirmed!==null&&confirmed+unconfirmed>total;
 return {total,confirmed,unconfirmed,suppressed:n(d.suppressed),
 overlapping_status_counts:overlaid,
 wpcom_followers:n(d.wpcom_followers),direct_email_followers:n(d.direct_email_followers),
 email_eligible_recipients:null,delivery_verified:false,confirmed_signup_event_verified:false,
 source:'WORDPRESS_AGGREGATE_ONLY_NOT_RECIPIENT_CONSENT'};
}
export function inspectRevenue(record={}){
 const missing=[];
 for(const f of ['qualified_human_sessions','settled_orders','gross_revenue','refunds','fees'])
  if(typeof record[f]!=='number'||!Number.isFinite(record[f])||record[f]<0)missing.push(f);
 if(record.orders_source!=='INDEPENDENT_SETTLEMENT')missing.push('independent_order_evidence');
 if(record.sessions_source!=='FIRST_PARTY_RECONCILED')missing.push('qualified_human_session_evidence');
 if(record.attribution_reconciled!==true)missing.push('order_to_session_attribution');
 if(record.qualified_human_sessions===0)missing.push('nonzero_session_denominator');
 if(missing.length)return {status:'NOT_COMPUTABLE',missing,net_revenue_per_1000:null};
 const net=record.gross_revenue-record.refunds-record.fees;
 return {status:'MODEL_ONLY_REQUIRES_REAL_WITNESS',net_revenue_per_1000:net*1000/record.qualified_human_sessions};
}
export function auditDraft({text='',html='',manifest={},snapshot={}}={}){
 const issue=manifest?.issues?.find?.(e=>e.number===3);
 const problems=inspectTierClaims(text);
 if(manifest?.mix?.editorial!==4||manifest?.mix?.commercial_review_pending!==2)problems.push('MIX_CHANGED');
 if(issue?.merchant_affiliate_url!==null||issue?.publish_state!=='hold')problems.push('MASTER_MERCHANT_HOLD_BROKEN');
 if(!text.includes('HOLD_UNSENT')||!text.includes('HOLD_MERCHANT')||!text.includes('NOT_ADOPTED'))problems.push('REVIEW_LABEL_MISSING');
 if(!text.includes('[[APPROVED_LIVE_ZEN12_GUIDE_REQUIRED'))problems.push('UNAPPROVED_CTA');
 if(!/Commercial disclosure.*Final Vestige may earn a commission/s.test(text))problems.push('DISCLOSURE_MISSING');
 if(!text.includes('[[FV_VALID_PHYSICAL_POSTAL_ADDRESS_REQUIRED]]')||!text.includes('[[RENDERED_UNSUBSCRIBE_REQUIRED]]'))problems.push('LEGAL_HOLD_NOT_VISIBLE');
 if(/<script|<form|<iframe|href\s*=\s*["'][^"']*(?:\?|ref=|aff=)/i.test(html))problems.push('UNSAFE_REVIEW_MARKUP');
 return {status:'HOLD_UNSENT',merchant:'HOLD_MERCHANT',candidate:'NOT_ADOPTED',issues:problems,eligible:audienceSnapshot(snapshot),send_allowed:false,merchant_link_allowed:false};
}