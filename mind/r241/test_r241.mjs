#!/usr/bin/env node
// Mind R241 source-only fail-closed checks. Run: node mind/r241/test_r241.mjs
import fs from 'node:fs';
import assert from 'node:assert/strict';
const root = new URL('.', import.meta.url);
const read = n => fs.readFileSync(new URL(n, root), 'utf8');
const html = read('focus-shot-presell-WP-SOURCE-UNPUBLISHED.html');
const article = read('THE-FOUR-HOUR-FOCUS-PROMISE-UNPUBLISHED.md');
const plan = read('CONVERSION-REVENUE-ACCEPTANCE.md');
const matrix = JSON.parse(read('FOCUS-SHOT-CLAIM-SOURCE-AUTHORIZATION.json'));
function validate(h=html,m=matrix,a=article,p=plan) {
  assert.equal(m.public_activation,false);
  assert.equal(m.commercial_release_gates.length,16);
  for (const g of m.commercial_release_gates) { assert.equal(g.status,'HARD_HOLD'); assert.equal(g.verified,false); }
  assert.ok(m.claims.length>=20 && m.sources.length>=10);
  for (const c of m.claims) {assert.ok(m.sources.some(s=>s.id===c.source_id));assert.ok(c.statement && c.status);}
  assert.equal(m.permission_evidence.issued_url,null);
  for (const k of ['net_revenue_per_1000_qualified_sessions','qualified_human_sessions','orders','affiliate_confirmed_sales']) assert.equal(m.live_revenue[k],null);
  assert.match(h,/<button[^>]*\bdisabled\b[^>]*>/i);
  assert.match(h,/may earn a commission/i);
  assert.match(h,/aria-describedby="close-disclosure"/);
  assert.match(h,/id="close-disclosure"/);
  assert.ok(h.indexOf('id="close-disclosure"')<h.indexOf('id="r241held"'));
  assert.doesNotMatch(h,/<(?:script|form|iframe|video)\b/i);
  assert.doesNotMatch(h,/(?:href|action)\s*=\s*["'][^"']*(?:inspire3\.com|zen12\.com|brainwaveshots\.com|hypnosislive\.com|awin1\.com)/i);
  assert.doesNotMatch(h,/<a[^>]+rel=["'](?:sponsored|nofollow)["'][^>]*>/i);
  assert.match(h,/https:\/\/finalvestige\.com\/focus\//i);
  assert.match(h,/:focus-visible/); assert.match(h,/@media\(max-width:650px\)/);assert.match(h, /prefers-reduced-motion/);
  assert.match(a,/SELLER|seller/i); assert.match(a,/not findings from a test that Final Vestige conducted/i);
  assert.match(a,/four hours/i); assert.match(a,/not automatically be treated/i);
  assert.match(p,/NOT COMPUTABLE/);assert.match(p,/TASK-008/);assert.match(p,/R237 A\/B/);
  return true;
}
validate();
const bad = [
  h=>h.replace(' disabled aria-disabled="true"',' aria-disabled="false"'),
  h=>h.replace('may earn a commission','offers a guaranteed result'),
  h=>h.replace('id="close-disclosure"','id="missing-disclosure"'),
  h=>h.replace('aria-describedby="close-disclosure"',''),
  h=>h.replace('href="https://finalvestige.com/focus/"','href="https://brainwaveshots.com/focus-shot"'),
  h=>h+'<script src="https://tracking.invalid/x.js"></script>',
  h=>h+'<form method="post"></form>',
  h=>h+'<iframe src="https://tracking.invalid"></iframe>',
];
let rejected=0;for (const f of bad){try{validate(f(html));}catch{rejected++;}}
assert.equal(rejected,bad.length);
for(const index of [0,3,7,15]){const m=structuredClone(matrix);m.commercial_release_gates[index].status='APPROVED';assert.throws(()=>validate(html,m));rejected++;}
{const m=structuredClone(matrix);m.live_revenue.net_revenue_per_1000_qualified_sessions=100;assert.throws(()=>validate(html,m));rejected++;}
{const m=structuredClone(matrix);m.permission_evidence.issued_url="https://unknown.example/tracking";assert.throws(()=>validate(html,m));rejected++;}
{const m=structuredClone(matrix);m.claims[0].source_id='missing';assert.throws(()=>validate(html,m));rejected++;}
console.log('R241 PASS baseline; '+rejected+'/'+(bad.length+7)+' deliberately unsafe mutations rejected. This is SOURCE-LEVEL ONLY; not WP/browser/merchant QA.');
