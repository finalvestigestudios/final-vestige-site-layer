'use strict';
/* Run from this folder: node --test qa.test.cjs
   Source-only deterministic tests. They do NOT constitute WordPress, browser, consent,
   checkout, partner-approval or live A/B testing. */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=read('ZEN12_A_TEXT_GUIDE.html');
const B=read('ZEN12_B_OPTIONAL_FILM_GUIDE.html');
const HUB=read('MIND_HUB_WP_SOURCE_ONLY.html');
const ARTICLE=read('THE_CHOICE_YOU_NEVER_MADE.md');
const SVG=read('ZEN12_POSTER.svg');
const VTT=read('ZEN12_FILM_CAPTIONS.vtt');
const MATRIX=JSON.parse(read('CLAIM_PERMISSION_AND_REVENUE_MATRIX.json'));
const stripFilm=x=>x.replace(/<section class="panel" aria-labelledby="film">[\s\S]*?<\/section>/,'').replace(/\n(?=<section aria-labelledby="demo")/,'');
const disclosures=x=>{const c=x.match(/<section class="cta"[\s\S]*?<\/section>/);return c?c[0]:'';};
const unsafe=x=>/(<script\b|<iframe\b|<form\b|onload\s*=|onclick\s*=|fetch\s*\(|dataLayer|googletagmanager|fbq\s*\()/i.test(x);
test('A and B share precisely the same core copy, excluding optional film component',()=>assert.equal(stripFilm(B),A));
test('A/B have no executable scripts, tracking or extra capture forms',()=>{for(const x of [A,B,HUB])assert.equal(unsafe(x),false)});
test('A/B have disabled native commercial actions and cannot navigate merchant',()=>{for(const x of [A,B]){assert.match(x,/<button[^>]*disabled[^>]*>/);assert.doesNotMatch(x,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i);}});
test('A/B pair disclosure with the inactive button in one section',()=>{for(const x of [A,B]){const t=disclosures(x);assert.match(t,/Prospective affiliate disclosure:/);assert.match(t,/may earn a commission/i);assert.match(t,/<button[^>]+disabled/);}});
test('Consent and no earnings attribution remain explicit in plan',()=>{const x=read('OFFER_TO_REALIZED_NET_REVENUE_ACCEPTANCE.md');assert.match(x,/NOT COMPUTABLE/);assert.match(x,/affiliate_click/);assert.match(x,/settled/);assert.match(x,/no personal identifiers/i);});
test('No sponsored URLs or seller tracking tags are active',()=>{for(const x of [A,B,HUB])assert.doesNotMatch(x,/href=["'][^"']+(?:ref=|aff_id=|hop=|clickid=|utm_source=affiliate)/i);});
test('Source-only publication and privacy hold remain visible',()=>{for(const x of [A,B,HUB]){assert.match(x,/noindex,nofollow/);assert.match(x,/Unpublished|unpublished/);}});
test('Poster is original static SVG with size and zero external script',()=>{assert.match(SVG,/<svg[^>]+viewBox="0 0 960 540"/);assert.doesNotMatch(SVG,/<(?:script|foreignObject|image)\b/i);});
test('Six caption cues cover contiguous forty-two seconds',()=>{let cues=[...VTT.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)].map(m=>({s:+m[1]*3600 + +m[2]*60 + +m[3] + +m[4]/1000,e:+m[5]*3600 + +m[6]*60 + +m[7] + +m[8]/1000}));assert.equal(cues.length,6);assert.equal(cues[0].s,0);assert.equal(cues.at(-1).e,42);for(let i=0;i<cues.length;i++){assert.ok(cues[i].e>cues[i].s);if(i)assert.equal(cues[i-1].e,cues[i].s)}});
test('Image has useful alternative text and optional transcript exists',()=>{assert.match(B,/<img[^>]+alt="Golden outlined circles/);assert.match(B,/<details>/);assert.match(B,/Read the full 42-second script and captions/);assert.match(B,/ZEN12_FILM_CAPTIONS\.vtt/);});
test('The same existing Jetpack/Focus route is the sole free capture path',()=>{for(const x of [A,B,HUB])assert.match(x,/https:\/\/finalvestige\.com\/focus\//);});
test('Responsive keyboard, zoom and reduced-motion base CSS is present',()=>{for(const x of [A,B,HUB]){assert.match(x,/name="viewport"/);assert.match(x,/focus-visible/);assert.match(x,/prefers-reduced-motion/);}});
test('Hub has four topic streams and no new signup form',()=>{for(const x of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])assert.ok(HUB.includes(x)||HUB.includes(x.replaceAll('&amp;','&')));assert.doesNotMatch(HUB,/<form\b/i);});
test('Article meets source and method expectations',()=>{assert.ok(ARTICLE.trim().split(/\s+/).length>=1800);for(const x of ['10.1126/science.1111709','10.1371/journal.pone.0060554','10.1002/acp.3062','puysegurs-animal-magnetism-files'])assert.ok(ARTICLE.includes(x));assert.match(ARTICLE,/not.*proof|not.*establish/i);});
test('Claim matrix is valid and every decision names a source and limits',()=>{assert.equal(MATRIX.claims.length,30);assert.equal(MATRIX.gates.length,30);for(const c of MATRIX.claims){assert.ok(c.sources.length&&c.sources.every(s=>s.startsWith('https://')));assert.ok(c.decision&&c.limitations);}});
test('Every commercial gate stays closed',()=>{for(const g of MATRIX.gates)assert.equal(g.status,'HOLD');assert.equal(MATRIX.affiliate_url,null);assert.equal(MATRIX.commission_rate,null);assert.equal(MATRIX.net_revenue_per_1000_qualified_sessions,null);});
test('Unproven benefits and account permission cannot be promoted',()=>{const x=MATRIX.claims;for(const k of ['C11','C12','C13','C14','C19','C20','C21'])assert.ok(/withhold|prohibited|NOT_VERIFIED/.test(x.find(c=>c.id===k).decision));});
test('Synthetic unsafe link is rejected by the seller-link predicate',()=>{const injected=A.replace('</body>','<a href="https://zen12.com/?aff_id=unsafe">BUY</a></body>');assert.match(injected,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i);});
test('Synthetic script injection triggers the safety predicate',()=>{assert.equal(unsafe(A+'<script src="https://example.org/pixel.js"></script>'),true);});
test('Source assets contain no PII/email capture or hard-coded paid prices',()=>{for(const x of [A,B,HUB]){assert.doesNotMatch(x,/type=["']email["']/i);assert.doesNotMatch(x,/\$\d{2,}|€\d{2,}/);}});
