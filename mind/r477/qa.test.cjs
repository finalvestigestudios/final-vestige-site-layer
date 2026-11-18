'use strict';
/* Offline reproducible regression suite. Run: node --test qa.test.cjs
   Structural tests only: NOT browser/WCAG, approved commerce, hosted video or paid sales. */
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=read('ZEN12_A_TEXT_ONLY_UNPUBLISHED.html'),B=read('ZEN12_B_OPTIONAL_FILM_UNPUBLISHED.html'),H=read('MIND_HUB_GUTENBERG_SOURCE_ONLY.html'),V=read('OPTIONAL_42S_TRANSCRIPT_CAPTIONS.vtt'),P=read('OFFER_FUNNEL_CONVERSION_AND_GROK_HANDOFF.md'),ART=read('THE_QUESTION_THAT_PUT_GLASS_ON_THE_ROAD.md'),M=JSON.parse(read('PRODUCT_CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const core=s=>s.replace(/<section aria-labelledby="film-title"[\s\S]*?<\/section>/,'').replace(/guide [AB]/g,'guide X').replace(/data-variant="[AB]"/g,'data-variant="X"');
test('guide A/B substantive copy identical except film & variant',()=>assert.equal(core(A),core(B)));
test('film storyboard is optional and contains accessible transcript',()=>{assert.match(B,/42-second source-note film/);assert.match(B,/<details>/);assert.match(B,/Read complete 42-second film transcript/);});
test('VTT six consecutive 7-second cues end 42 seconds',()=>{let m=[...V.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)].map(x=>[x[1],x[2]]);assert.equal(m.length,6);assert.equal(m[0][0],'00:00:00.000');assert.equal(m[5][1],'00:00:42.000');for(let i=1;i<6;i++)assert.equal(m[i-1][1],m[i][0]);});
for(const [k,html] of [['A',A],['B',B]]){
test(k+' native-disabled CTA and earlier adjacent affiliate disclosure',()=>{let b=html.match(/<section class="offer"[\s\S]*?<\/section>/)?.[0];assert.ok(b);assert.match(b,/<button[^>]*disabled[^>]*>/);assert.ok(b.indexOf('Affiliate disclosure:')<b.indexOf('<button'));});
test(k+' has no merchant affiliate href or tracking tokens',()=>{assert.doesNotMatch(html,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i);assert.doesNotMatch(html,/(?:\?|&)aff(?:iliate)?=|clickid=|refid=/i);});
test(k+' has no scripts, remote iframes, forms or external signup',()=>assert.doesNotMatch(html,/<script\b|<iframe\b|<form\b|<input\b|on(?:click|load|error)\s*=/i));
test(k+' noindex responsive focus and reduced motion',()=>{assert.match(html,/noindex,nofollow/);assert.match(html,/name="viewport"/);assert.match(html,/:focus-visible/);assert.match(html,/prefers-reduced-motion:reduce/);});
test(k+' offers free live Focus rather than gated email signup',()=>assert.match(html,/https:\/\/finalvestige\.com\/focus\//));
test(k+' includes neutral FTC evidence citation',()=>assert.match(html,/ftc\.gov\/business-guidance\/resources\/ftcs-endorsement-guides/));
test(k+' does not present seller guarantee or discount as verified',()=>{assert.match(html,/seller assertions/);assert.doesNotMatch(html,/guaranteed results|buy now|coupon code VZ54/i);});
}
test('hub retains four streams, no capture duplication',()=>{for(const t of ['id="attention"','id="suggestion"','id="practice"','id="tools"'])assert.ok(H.includes(t));assert.doesNotMatch(H,/<form\b|<script\b/);});
test('hub is source-only and noindex',()=>{assert.match(H,/noindex,nofollow/);assert.match(H,/Not a published WordPress page/);});
test('article contains original source URLs',()=>{for(const x of ['10.1016/S0022-5371(74)80011-3','pubmed.ncbi.nlm.nih.gov/621467','10.1002/acp.4202','puysegurs-animal-magnetism-files'])assert.ok(ART.includes(x));});
test('article retains denominator and source-uncertainty',()=>{assert.match(ART,/16 in the \*smashed\* condition/);assert.match(ART,/Most people in \*\*all three\*\* conditions/);});
test('matrix sources, claims, hard gates structured',()=>{assert.ok(M.claims.length>=20);assert.ok(M.source_registry.length>=14);assert.ok(M.release_gates.length>=15);assert.ok(M.claims.every(c=>c.id&&c.claim&&c.decision));});
test('all commercial release gates closed',()=>assert.ok(M.release_gates.every(g=>g.status!=='PASS'&&g.status!=='VERIFIED')));
test('no earning URL, pixel, new list or paid SaaS',()=>{assert.equal(M.rendering_and_privacy.affiliate_url,null);assert.equal(M.rendering_and_privacy.promotion_active,false);assert.equal(M.rendering_and_privacy.tracking_scripts_added,0);assert.equal(M.rendering_and_privacy.new_signup_forms,0);assert.equal(M.rendering_and_privacy.paid_saas,false);});
test('revenue contract does not count affiliate click as paid order',()=>{assert.match(P,/affiliate_outbound/);assert.match(P,/merchant_confirmed_purchase/);assert.match(P,/net_revenue_per_1000_qualified_human_sessions/);});
test('creator matches remain unverified',()=>{assert.match(P,/UNMATCHED/);assert.match(P,/asset_id/);});
test('mutation enabling purchase CTA is detected',()=>{let bad=A.replace(/<button type="button" disabled aria-disabled="true">/,'<button type="button">');assert.doesNotMatch(bad,/<button[^>]*disabled[^>]*>/);});
test('mutation introducing product link is detected',()=>{let bad=B+'<a href="https://zen12.com/?affiliate=fake">BUY</a>';assert.match(bad,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\.com/i);});
test('mutation adding duplicate form is detected',()=>assert.match(A+'<form><input type="email"></form>',/<form\b|<input\b/));