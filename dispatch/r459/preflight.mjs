// R459: local, non-sending source and rendered-copy QA. No network, tracking, email or WordPress writes.
import fs from 'node:fs';
import path from 'node:path';

export function auditIssue(source, html, plain) {
  const errors = [];
  const has = (ok, reason) => { if (!ok) errors.push(reason); };
  const links = [...html.matchAll(/<a\b[^>]*href="([^"]+)"/gi)].map(x => x[1]);
  const cta = source.cta.url;
  const norm = x => String(x).replace(/\s+/g, ' ').trim();
  has(source.kind === 'editorial', 'NOT_EDITORIAL');
  has(source.status === 'HOLD_UNSENT_FOUNDER_REVIEW_ONLY', 'UNSAFE_STATUS');
  has(typeof source.subject === 'string' && source.subject.length >= 12 && source.subject.length <= 80, 'BAD_SUBJECT_LENGTH');
  has(!/[\r\n]|\*\*/.test(source.subject), 'HEADER_CONTAMINATION');
  has(!/[\r\n]|\*\*/.test(source.preheader) && source.preheader.length >= 20, 'BAD_PREHEADER');
  has(plain.includes('Subject: ' + source.subject) && html.includes('<title>' + source.subject + ' — UNSENT REVIEW</title>'), 'SUBJECT_MISMATCH');
  has(plain.includes('Preheader: ' + source.preheader) && html.includes(source.preheader), 'PREHEADER_MISMATCH');
  has(source.blocks.filter(b => b.type === 'cta').length === 1, 'MULTIPLE_CTA_BLOCKS');
  has(links.filter(x => x === cta).length === 1 && plain.includes(cta), 'CTA_MISMATCH');
  has(source.sources.length >= 3 && source.sources.every(s => /^https:\/\/(www\.nasa\.gov|sma\.nasa\.gov)\//.test(s.url)), 'BAD_OFFICIAL_SOURCES');
  has(source.sources.every(s => html.includes(s.url) && plain.includes(s.url)), 'SOURCE_RENDER_MISMATCH');
  has(!/(refersion|inspire3\.com|zen12\.com|hypnosislive\.com)/i.test(html+plain), 'MERCHANT_IN_EDITORIAL');
  has(!/<script\b|<iframe\b|<form\b|<img\b|<video\b|<audio\b/i.test(html), 'UNSAFE_HTML_TAG');
  has(!/<link\b|@import|onerror=|onclick=|javascript:/i.test(html), 'REMOTE_OR_ACTIVE_HTML');
  has(/<html lang="en">/.test(html) && /<table role="presentation"/.test(html) && /<h1\b/.test(html), 'EMAIL_ACCESSIBILITY');
  has(!/https?:\/\/(?:www\.)?example\.com/i.test(html+plain), 'PLACEHOLDER_URL');
  has(html.includes(source.legal.address) && plain.includes(source.legal.address), 'POSTAL_HOLD_NOT_VISIBLE');
  has(html.includes(source.legal.unsubscribe) && plain.includes(source.legal.unsubscribe), 'UNSUB_HOLD_NOT_VISIBLE');
  has(/OFFLINE REVIEW ONLY/.test(html) && /HOLD_UNSENT/.test(plain), 'REVIEW_STATUS_NOT_VISIBLE');
  has(/source of ignition/i.test(norm(plain)) && /probable/i.test(norm(plain)), 'IGNITION_UNCERTAINTY_LOST');
  has(!/Fourteen seconds\./.test(source.subject) && !/Fourteen seconds\./.test(source.preheader), 'FALSE_PRECISION_HEADER');
  const actualSources = links.filter(x => x !== cta);
  has(actualSources.length === source.sources.length, 'SOURCE_LINK_COUNT');
  const copyPass = errors.length === 0;
  const l = source.legal || {};
  const releaseAllowed = copyPass &&
    l.native_preview_verified === true && l.founder_approved === true &&
    l.publisher_postal_verified === true && l.unsubscribe_verified === true &&
    l.consent_eligible_witnessed === true;
  return { copyPass, releaseAllowed, errors, issue: source.id, sourceCount: source.sources.length,
    ctaCount: links.filter(x => x === cta).length };
}

export function runOfflineAudit(folder) {
  const source = JSON.parse(fs.readFileSync(path.join(folder, 'ISSUE04_SOURCE_STRUCTURED.json'), 'utf8'));
  const html = fs.readFileSync(path.join(folder, 'ISSUE04_SUBSCRIBER_REVIEW.html'), 'utf8');
  const plain = fs.readFileSync(path.join(folder, 'ISSUE04_SUBSCRIBER_REVIEW.txt'), 'utf8');
  return auditIssue(source, html, plain);
}
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  const r = runOfflineAudit(path.dirname(process.argv[1]));
  console.log(JSON.stringify(r, null, 2));
  if (!r.copyPass || r.releaseAllowed) process.exitCode = 1;
}
