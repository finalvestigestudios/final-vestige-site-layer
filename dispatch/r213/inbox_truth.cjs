'use strict';
// Final Vestige Dispatch R213: deterministic SOURCE-ONLY email preview truth audit.
// Pure CommonJS. Does not contact a network, read subscribers, render Jetpack, or send mail.
function visibleText(markup) {
  if (typeof markup !== 'string') throw Error('HTML source required');
  return markup
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<head\b[\s\S]*?<\/head>/gi, ' ')
    .replace(/<(style|script|template)\b[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/\s+/g, ' ')
    .trim();
}
function attributeLinks(markup) {
  return Array.from(markup.matchAll(/<a\b[^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*>/gi), x=>x[1]);
}
function safeTrackingUrl(input) {
  if (typeof input !== 'string' || /[\r\n]/.test(input)) return false;
  let u;
  try { u = new URL(input); } catch(_) { return false; }
  if (u.protocol !== 'https:' || u.hostname !== 'finalvestige.com' || u.username || u.password || u.hash) return false;
  const allowed = new Set(['utm_source','utm_medium','utm_campaign','utm_content']);
  for (const k of u.searchParams.keys()) if (!allowed.has(k)) return false;
  const medium = u.searchParams.get('utm_medium');
  if (medium && medium !== 'email') return false;
  const source = u.searchParams.get('utm_source');
  if (source && source !== 'dispatch') return false;
  const campaign = u.searchParams.get('utm_campaign');
  if (campaign && !/^dispatch_pilot_20\d{2}_\d{2}$/.test(campaign)) return false;
  const content = u.searchParams.get('utm_content');
  if (content && !/^issue_(0[1-6])_(editorial|zen12|total_focus)$/.test(content)) return false;
  // Never put subscriber email, email hash, client ID, click ID or campaign-specific identity in URLs.
  if (/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(input)) return false;
  if (/(subscriber|recipient|person_id|token|click_id|gclid|fbclid)/i.test(input)) return false;
  return true;
}
function audit(entry, html, eml, plain) {
  if (!entry || !Number.isInteger(entry.issue) || entry.issue < 1 || entry.issue > 6) throw Error('issue identity required');
  if (!['editorial','commercial-review-pending'].includes(entry.kind)) throw Error('unknown issue kind');
  if (!entry.subject || !entry.preheader) throw Error('subject/preheader required');
  const visible = visibleText(html);
  const h1 = ((html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i)||[])[1]||'').replace(/<[^>]*>/g,'').trim();
  const links = attributeLinks(html);
  const reason = [];
  const htmlReview = /REVIEW ONLY|UNSENT|NOT APPROVED|NOT A SENDABLE EMAIL/i.test(visible);
  const missingPublisherPostal = /\[\[VALID_FINAL_VESTIGE_POSTAL_ADDRESS_REQUIRED\]\]/.test(html);
  const unverifiedUnsubscribe = /\[\[JETPACK_UNSUBSCRIBE_MUST_BE_VERIFIED\]\]/.test(html);
  const preheaderFirst = visible.startsWith(entry.preheader);
  // This X-header is private specimen metadata, not a portable inbox preview field.
  const metadataOnlyPreheader = /^X-FV-Intended-Preheader:/mi.test(eml);
  const senderIsInvalid = /review@dispatch\.invalid/i.test(eml);
  const realJetpackRender = false; // Cannot be inferred from offline HTML/MIME.
  const realProviderWelcomeReceipt = false; // Requires an authorized actual received message.
  const merchantAllowed = false; // Requires account-specific rights from Mind/affiliate owner.
  const hasEarningHref = links.some(x=>/(awin1\.com|affiliates\.inspire3|clickbank\.net)/i.test(x));
  if (h1 !== entry.subject) reason.push('subject_h1_mismatch');
  if (!preheaderFirst) reason.push('preheader_not_first_source_visible_text');
  if (metadataOnlyPreheader) reason.push('x_header_is_not_a_standard_inbox_preheader');
  if (htmlReview) reason.push('review_scaffolding_present_in_body');
  if (missingPublisherPostal) reason.push('publisher_postal_placeholder');
  if (unverifiedUnsubscribe) reason.push('unsubscribe_placeholder');
  if (senderIsInvalid) reason.push('synthetic_invalid_sender_not_jetpack');
  if (/REVIEW ONLY|DO NOT SEND/i.test(plain)) reason.push('plaintext_review_scaffolding');
  if (hasEarningHref) reason.push('unexpected_active_earning_link');
  if (entry.kind === 'commercial-review-pending') reason.push('merchant_email_rights_and_live_guide_unverified');
  reason.push('provider_rendering_and_eligible_audience_unverified');
  reason.push('founder_final_send_approval_not_granted');
  return {
    issue:entry.issue,
    kind:entry.kind,
    declared_subject:entry.subject,
    declared_preheader:entry.preheader,
    source_visible_opening:visible.slice(0,165),
    source_h1_matches_subject:h1 === entry.subject,
    source_preheader_first:preheaderFirst,
    specimen_x_header_is_only_metadata:metadataOnlyPreheader,
    review_scaffold_in_body:htmlReview,
    placeholder_postal:missingPublisherPostal,
    placeholder_unsubscribe:unverifiedUnsubscribe,
    specimen_invalid_sender:senderIsInvalid,
    verified_native_jetpack_render:realJetpackRender,
    verified_received_welcome:realProviderWelcomeReceipt,
    verified_partner_email_permission:merchantAllowed,
    earning_href_present:hasEarningHref,
    preview_diagnostic_only:true,
    release:'HOLD_UNSENT',
    additional_commercial_hold:entry.kind === 'commercial-review-pending',
    blockers:reason
  };
}
function subscriberAssessment(snapshot) {
  if (!snapshot || !snapshot.subscribers || !snapshot.followers) throw Error('source-qualified snapshot required');
  const s=snapshot.subscribers, f=snapshot.followers;
  for (const n of [s.total,s.confirmed,s.unconfirmed,f.wpcom,f.email])
    if (!Number.isInteger(n)||n<0) throw Error('nonnegative count required');
  return {
    provider_counters:{total:s.total,confirmed:s.confirmed,unconfirmed_requests:s.unconfirmed},
    follower_counters:{wordpress_com:f.wpcom,email_only:f.email},
    nonadditive_counters:true,
    email_eligible_unique_recipients:null,
    provider_confirmed_signup_events:null,
    welcome_delivered:null,
    note:'No joins, totals or revenue can be inferred from these separate dashboard measures.'
  };
}
if (typeof module !== 'undefined') module.exports = {visibleText, attributeLinks, safeTrackingUrl, audit, subscriberAssessment};
