// Run: node mind/r380/verify.mjs from the repository root.
// Source-only checks; this is NOT real-browser WCAG, checkout, CI or product testing.
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const dir='mind/r380/';
const read=f=>readFileSync(dir+f,'utf8');
const a=read('ZEN12_A_EVIDENCE_FIRST.html'),b=read('ZEN12_B_OPTIONAL_FILM.html'),h=read('MIND_ARCHIVE_WORDPRESS_REVIEW_ONLY.html'),m=JSON.parse(read('CLAIM_EVIDENCE_AUTHORIZATION.json')),v=read('ORIGINAL_42S_CAPTIONS.vtt'),s=read('ORIGINAL_IDEOMOTOR_POSTER.svg'),d=read('CONVERSION_FIRST_ACCEPTANCE.md'),article=read('THE_PENDULUM_THAT_ANSWERED_BEFORE_YOU_DID.md');
const commonChecks=[['A',a],['B',b]];
for(const [n,t] of commonChecks){
  assert.match(t,/<button\b[^>]*\bdisabled\b[^>]*>/i,n+' native disable');
  assert.match(t,/may earn a commission at no additional cost to you/i,n+' disclosure');
  assert.ok(t.indexOf('may earn a commission') < t.indexOf('<button class="merchant"'),n+' disclosure before merchant CTA');
  assert.match(t,/<meta name="robots" content="noindex,nofollow,noarchive">/i);
  assert.match(t,/https:\/\/finalvestige\.com\/focus\//);
  assert.doesNotMatch(t,/<script\b|<iframe\b|<form\b|\bonclick\s*=|\bonload\s*=|\bautoplay\b(?=[\s=>])/i,n+' scripts/forms/autoplay');
  assert.doesNotMatch(t,/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i,n+' active seller link');
  assert.doesNotMatch(t,/<a\b[^>]*href=["'][^"']*(?:aff|ref|track|utm_campaign)=/i,n+' tracking URL');
  assert.doesNotMatch(t,/guaranteed focus|treats anxiety|clinically proven brainwave|one hour of meditation in twelve minutes as fact/i,n+' efficacy language');
  assert.match(t,/max-width:780px/);
  assert.match(t,/prefers-reduced-motion/);
}
assert.match(b,/ORIGINAL_IDEOMOTOR_POSTER\.svg/);
assert.match(b,/42-second original visual thought experiment/);
assert.doesNotMatch(a,/ORIGINAL_IDEOMOTOR_POSTER\.svg/);
const strip=s=>s.replace(/<figure class="film"[\s\S]*?<\/figure>/,'').replace('ZEN12 A Evidence First','ZEN12 B Optional Film'); // Titles intentionally differ; compare from shared body.
assert.ok(a.includes('<section><h2>The strange difference')&&b.includes('<section><h2>The strange difference'));
const extract=s=>s.slice(s.indexOf('<section><h2>The strange difference'),s.indexOf('</article>'));
assert.equal(extract(a),extract(b),'same substantive guide body');
assert.match(v,/^WEBVTT/);
assert.equal((v.match(/--> /g)||[]).length,6);
assert.match(v,/00:00:35\.000 --> 00:00:42\.000/);
assert.match(s,/<title id="title">/);
assert.match(s,/<desc id="desc">/);
assert.equal(m.claims.length,32);
assert.equal(Object.keys(m.release_gates).length,36);
assert.ok(Object.values(m.release_gates).every(g=>g.status==='HOLD'));
assert.match(h,/not a live route/i);
assert.match(h,/https:\/\/finalvestige\.com\/focus\//);
assert.doesNotMatch(h,/<script\b|<form\b|<iframe\b/i);
assert.match(d,/NOT COMPUTABLE/);
assert.match(d,/provider_confirmed_lead/);
assert.match(d,/merchant_confirmed_owned_order/);
assert.match(d,/actual_verified_asset_id/);
assert.match(article,/60 college students/);
assert.match(article,/situation-specific/);
assert.match(article,/Puységur/);
console.log('R380 independent static source policy checks passed — NOT native browser/merchant/CI proof.');
