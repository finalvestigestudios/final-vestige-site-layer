/* R167 zero-dependency regression; run from repository root: node mind/r167/test_mind_r167.cjs
 * Static source checks only; not a substitute for native browser, WCAG audit or merchant confirmation.
 */
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=path.join(__dirname);const load=n=>fs.readFileSync(path.join(root,n),'utf8');
const article=load('invisible-gorilla-attention-is-an-assignment-UNPUBLISHED.md');
const guide=load('zen12-12-minutes-evidence-buyer-guide-UNPUBLISHED.md');
const html=load('invisible-gorilla-zen12-buyer-PREVIEW-UNPUBLISHED.html');
const matrix=JSON.parse(load('claims-and-closed-release-gates.json'));
const plan=load('creator-offer-net-revenue-contract.md');
function validate(){
assert.match(article,/Simons and Christopher Chabris|Simons and Chabris/);
assert.match(article,/2010 Simons|In 2010 Simons/);
assert.match(article,/Twenty-four radiologists/);
assert.match(article,/Eighty-three percent/);
assert.match(article,/do \*\*not\*\* show|does not establish|does not prove/);
assert.match(guide,/12 levels|twelve levels/);
assert.match(guide,/48 MP3/);
assert.match(guide,/seller/i);
assert.match(guide,/2026-11-06/);
assert.match(guide,/unverified|unsubstantiated|not independently/);
assert.ok(!/affiliate link: https?:\/\//i.test(guide));
assert.match(html,/<html lang="en">/);
assert.match(html,/<main id="main">/);
assert.match(html,/Skip to content/);
assert.match(html,/<svg[^>]*role="img"/);
assert.match(html,/<title id="art-title">/);
assert.match(html,/prefers-reduced-motion:reduce/);
assert.match(html,/@media\(max-width:740px\)/);
assert.match(html,/disabled aria-disabled="true"/);
assert.match(html,/If you purchase through an affiliate link, Final Vestige may earn a commission/);
assert.match(html,/No affiliate link is active/);
assert.match(html,/https:\/\/finalvestige\.com\/focus\//);
assert.match(html,/video produced|not a film/);
assert.doesNotMatch(html,/<(?:script|form|iframe|video)\b/i);
assert.doesNotMatch(html,/(?:href|action)\s*=\s*["'](?:https?:\/\/)?(?:affiliates\.inspire3|www\.awin1|payhip\.com|checkout\.)/i);
assert.doesNotMatch(html,/<a[^>]+(?:Buy now|Purchase|Get Started)[^>]*>/i);
assert.doesNotMatch(html,/<video\b|<input\b|\sonload\s*=|\sonclick\s*=/i);
assert.equal(matrix.status,'DRAFT_ONLY_HARD_HOLD');
assert.ok(matrix.sources.length>=12&&matrix.claims.length>=27&&matrix.gates.length>=25);
assert.ok(matrix.gates.every(x=>x.status==='CLOSED'));
assert.equal(matrix.authorization.affiliate_url,null);
assert.equal(matrix.authorization.affiliate_approved,null);
assert.equal(matrix.payhip_fallback.eligible_owned_mind_sku,null);
assert.equal(matrix.measurement.realized_net_revenue,null);
assert.equal(matrix.measurement.revenue_per_1000_qualified_human_sessions,null);
assert.match(plan,/NOT COMPUTABLE/);
assert.match(plan,/affiliate_click/);
assert.match(plan,/1000\*N\/Q/);
assert.match(plan,/Grok \+ Praxxis/);
assert.match(plan,/preload="none"/);
assert.match(plan,/seven-day|7- and 30-day/i);
}
validate();console.log('R167 baseline PASS source assertions/gates — source-only. Native browser and checkout NOT TESTED.');
