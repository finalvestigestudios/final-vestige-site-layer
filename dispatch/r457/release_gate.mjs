// Source-only Dispatch evidence gate. No network, I/O, emails, subscriber identifiers, or CMS writes.
const own = (obj, key) => Object.prototype.hasOwnProperty.call(obj ?? {}, key);
const yes = (obj, key) => own(obj, key) && obj[key] === true;
const documented = (obj, key) => yes(obj, key) && typeof obj[key+'_proof'] === 'string' && /^https:\/\//.test(obj[key+'_proof']);
export const REQUIRED_SHARED = Object.freeze(['consent_confirmed','welcome_received','native_preview_witnessed','publisher_postal_verified','rendered_unsubscribe_verified','sender_subject_verified','founder_release_approved']);
export const REQUIRED_MERCHANT = Object.freeze(['named_partner_approved','email_channel_allowed','issued_earning_link_verified','live_warmup_guide_verified','product_claims_reviewed','checkout_terms_verified','adjacent_disclosure_verified']);
export const EDITORIAL = Object.freeze([1,2,4,6]);
export const COMMERCIAL = Object.freeze([3,5]);
export function reconcile(snapshot) {
  const n=snapshot?.newsletter, s=snapshot?.stats_subscribers, f=snapshot?.stats_followers;
  if(!n || !s || !f || [n.confirmed,n.unconfirmed,s.email,s.reader,f.email,f.reader].some(v=>!Number.isSafeInteger(v)||v<0)) throw Error('invalid provider aggregate');
  return {provider_conflict:s.email!==f.email||s.reader!==f.reader, confirmed_provider:n.confirmed, unconfirmed_excluded:n.unconfirmed, separately_reported:{stats_subscribers:s,stats_followers:f}, independent_new_leads:null};
}
export function preflight(issue, proof, snapshot) {
  if(![1,2,3,4,5,6].includes(issue)) throw Error('unknown edition');
  const missing = REQUIRED_SHARED.filter(k=>!documented(proof,k));
  if(COMMERCIAL.includes(issue)) missing.push(...REQUIRED_MERCHANT.filter(k=>!documented(proof,k)));
  if(snapshot?.newsletter?.auto_send!==false) missing.push('default_email_sending_not_proved_off');
  if(snapshot?.newsletter?.content_format!=='full'&&snapshot?.newsletter?.content_format!=='excerpt') missing.push('email_content_format_missing');
  if(!yes(proof,'preview_subject_matches_wp_title')) missing.push('subject_to_wp_title_unverified');
  if(yes(proof,'source_contains_internal_markers')) missing.push('editorial_marker_leak');
  return {edition:issue, type:COMMERCIAL.includes(issue)?'commercial':'editorial', status:missing.length?'HOLD_UNSENT':'HUMAN_REVIEW_ONLY', missing};
}
export function revenue(data) {
  const d=data??{}, q=d.qualified_human_sessions, o=d.settled_orders;
  if(!Number.isSafeInteger(q)||q<=0||!Array.isArray(o)||!yes(d,'audited_source_attribution')||!yes(d,'complete_settlement_ledger')) return {net_revenue_per_1000:null,verified_paid_orders:null,reason:'NOT_COMPUTABLE'};
  if(o.some(x=>typeof x?.order_id!=='string'||!x.order_id||!['paid','refunded'].includes(x.status)||![x.gross,x.fees,x.refunds].every(z=>Number.isFinite(z)&&z>=0)||x.refunds>x.gross)) return {net_revenue_per_1000:null,verified_paid_orders:null,reason:'INVALID_SETTLEMENT'};
  const ids=new Set(o.map(x=>x.order_id)); if(ids.size!==o.length) return {net_revenue_per_1000:null,verified_paid_orders:null,reason:'DUPLICATE_ORDER'};
  const net=o.reduce((a,x)=>a+x.gross-x.fees-x.refunds,0);
  return {net_revenue_per_1000:Number((net*1000/q).toFixed(2)),verified_paid_orders:o.filter(x=>x.status==='paid').length,reason:'CALCULATED_FROM_ASSERTED_LEDGER'};
}
