'use strict';
// Read-only / offline. No publishing, analytics, mail, subscriber or network calls.
const MAX_WORDS = 55;
const MAX_CHARS = 300; // stricter than a *modeled* 350-character excerpt; not a Jetpack guarantee
const expectedKinds = ['editorial','editorial','commercial-review-pending','editorial','commercial-review-pending','editorial'];
const held = ['native_render_proven','merchant_approved','partner_email_permission_verified','valid_fv_postal_address_verified','unsubscribe_render_verified','founder_final_approval'];
const wordCount = x => String(x).trim().split(/\s+/).filter(Boolean).length;
function audit(doc) {
  const failures = [];
  if (!doc || typeof doc !== 'object') return {ok:false,failures:['missing document']};
  if (doc.status !== 'DRAFT_ONLY_NO_WORDPRESS_WRITES_NO_SENDS') failures.push('draft status missing');
  for (const k of held) if (doc[k] !== false) failures.push('release hold '+k);
  if (doc.recipient_eligible_count !== null) failures.push('recipient eligibility has not been verified');
  if (doc.email_format_seen !== 'excerpt') failures.push('source configuration changed since evidence snapshot');
  if (!Array.isArray(doc.issues) || doc.issues.length !== 6) return {ok:false,failures:[...failures,'six original slots required']};
  for(let j=0;j<6;j++) {
    const i=doc.issues[j], p='issue '+String(j+1).padStart(2,'0');
    if(!i || i.number!==j+1 || i.kind!==expectedKinds[j]) {failures.push(p+' kind/number mismatch');continue}
    for(const k of ['subject','preheader','excerpt','primary_action'])
      if(typeof i[k]!=='string'||!i[k].trim()) failures.push(p+' missing '+k);
    if(typeof i.excerpt!=='string') continue;
    if (i.excerpt.length>MAX_CHARS) failures.push(p+' excerpt >300 characters');
    if (wordCount(i.excerpt)>MAX_WORDS) failures.push(p+' excerpt >55 words');
    if (typeof i.primary_action==='string' && !i.excerpt.toLowerCase().includes(i.primary_action.toLowerCase())) failures.push(p+' CTA not visible in candidate');
    if (/https?:\/\/|\[\[|utm_|\baffiliate\s+link\s*:/i.test(i.excerpt)) failures.push(p+' unresolved or earning link in excerpt');
    if (i.kind==='commercial-review-pending') {
      if (i.guide_state!=='NOT_LIVE_NOT_APPROVED'||i.source_url!==null) failures.push(p+' commercial guide activation');
      if (!i.commercial_disclosure || !i.excerpt.includes(i.commercial_disclosure)) failures.push(p+' adjacent disclosure missing');
      if (!/may earn a commission/i.test(i.commercial_disclosure||'')) failures.push(p+' disclosure not candid');
    } else {
      if(i.guide_state!=='existing_editorial_destination'||!String(i.source_url).startsWith('https://finalvestige.com/')) failures.push(p+' missing first-party editorial evidence trail');
      if(i.commercial_disclosure) failures.push(p+' unintended sales disclosure');
    }
    if (/guaranteed improvement|clinically proven|cure your|secret miracle|limited time discount/i.test(i.excerpt)) failures.push(p+' unsupported promise');
  }
  return {ok:failures.length===0, failures, excerpt_model:'NOT_A_RECEIVED_EMAIL', send_ready:false, actual_delivery_proven:false, monetization_verified:false};
}
module.exports={audit,wordCount,MAX_CHARS,MAX_WORDS};
