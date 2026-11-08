'use strict';
/* R207 source-only regression guard. Run: node mind/r207/test_mind_r207.cjs
 * Not a substitute for real browser WCAG, native WordPress, merchant or CI QA.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const dir = __dirname;
const read = n => fs.readFileSync(path.join(dir,n), 'utf8');
const a = read('zen12-A-TEXT-UNPUBLISHED.html');
const b = read('zen12-B-OPTIONAL-42S-UNPUBLISHED.html');
const hub = read('mind-four-stream-WP-SOURCE-PREVIEW-UNPUBLISHED.html');
const vtt = read('zen12-optional-film-UNRENDERED.vtt');
const article = read('the-song-that-stole-a-sentence-AUDIO-ATTENTION-UNPUBLISHED.md');
const plan = read('OFFER-FIRST-REVENUE-AND-CREATOR-HANDOFF-UNPUBLISHED.md');
const m = JSON.parse(read('AUDIO-CLAIM-SOURCE-COMMERCE-MATRIX.json'));
let count = 0;
function test(label, run) {
  run(); count++;
  process.stdout.write('PASS ' + count + ': ' + label + '\n');
}
function noActiveMarkup(html) {
  assert.doesNotMatch(html, /<script\b|<iframe\b|<form\b|<video\b|autoplay\s*=|<link\b[^>]*href=|<img\b[^>]*src=["']https?:/i);
  assert.doesNotMatch(html, /<a\b[^>]*href=["'](?:https?:)?\/\/(?:www\.)?awin1\.com|[?&](?:aff_id|subid|clickref)=/i);
}
function guideCompliant(html) {
  assert.match(html, /<button\b[^>]*\sdisabled(?:\s|>)/);
  assert.match(html, /may earn a commission at no additional cost to you/);
  assert.match(html, /No personal product trial/);
  assert.match(html, /merchant/i);
  noActiveMarkup(html);
  const p=html.indexOf('may earn a commission at no additional cost to you');
  const q=html.indexOf('<button',p);
  assert(p>=0 && q>=0 && q-p<500,'adjacent disclosure within 500 chars of button');
}
function validateCaptions(txt){ assert.match(txt,/^WEBVTT\\s/m); assert.match(txt,/00:00:42\\.000/); const cues=[...txt.matchAll(/(\\d{2}:\\d{2}:\\d{2}\\.\\d{3}) --> (\\d{2}:\\d{2}:\\d{2}\\.\\d{3})/g)];assert(cues.length>=2,'timed caption cues');}
function validateCommerceMatrix(x){ assert(x.authorization_gates.length>0); x.authorization_gates.forEach(g=>assert.equal(g.state,'OPEN'));assert.equal(x.measurement.status,'NOT_COMPUTABLE');assert.match(x.measurement.formula,/settled_owned_product_receipts/);assert.match(x.measurement.formula,/cleared_affiliate_commissions/);assert.doesNotMatch(x.measurement.formula,/confirmed_paid_orders\\s*\\+/); }
const clipStart=b.indexOf('<section id="optional-film">');
const clipEnd=b.indexOf('<section id="why">',clipStart);
test('all three HTML previews language marked English',()=>[a,b,hub].forEach(x=>assert.match(x,/<html lang="en">/)));
test('source-only previews carry noindex',()=>[a,b,hub].forEach(x=>assert.match(x,/<meta name="robots" content="noindex,nofollow">/)));
test('A guide remains natively disabled and near-disclosed',()=>guideCompliant(a));
test('B guide remains natively disabled and near-disclosed',()=>guideCompliant(b));
test('Mind archive hub has disabled CTA and adjacent disclosure',()=>{assert.match(hub,/<button\b[^>]*\sdisabled(?:\s|>)/);assert.match(hub,/may earn a commission at no additional cost to you/);});
test('no active scripts, forms, remote media or affiliate earning refs',()=>[a,b,hub].forEach(noActiveMarkup));
test('B film has one optional section',()=>assert(clipStart>0&&clipEnd>clipStart));
test('A/B all commercial guide core is identical',()=>assert.equal((b.slice(0,clipStart)+b.slice(clipEnd)).replace(' — optional film',''),a));
test('B original SVG poster is described with title and desc',()=>{assert.match(b,/<svg\b/);assert.match(b,/<title id="poster-title">/);assert.match(b,/<desc id="poster-desc">/);assert.match(b,/<figcaption>/);});
test('film is not falsely described as rendered playback',()=>{assert.doesNotMatch(b,/<video\b/);assert.match(b,/No playable film/);});
test('caption draft validates actual timed cues',()=>validateCaptions(vtt));
test('caption draft ends at 42 seconds',()=>assert.match(vtt,/00:00:42\.000/));
test('guide preserves single existing Focus pathway',()=>[a,b,hub].forEach(x=>assert.match(x,/https:\/\/finalvestige\.com\/focus\//)));
test('Mind hub has four unique streams',()=>['perception','history','practice','tools'].forEach(id=>assert.match(hub,new RegExp('id="'+id+'"'))));
test('no outbound public link to unpublished study slug',()=>assert.doesNotMatch(hub,/href=["']\/mind\//));
test('research article is substantive',()=>assert(article.split(/\s+/).length>1900));
test('research article contains scholarly refs',()=>['10.1177/1745691617747398','10.1177/0305735610376261','10.1518/001872001775992462'].forEach(s=>assert(article.includes(s))));
test('article does not carry an active commercial affiliate link',()=>assert.doesNotMatch(article,/awin1\.com|ref=(?:affiliate|paid)/));
test('claim matrix all source IDs resolve',()=>{const ids=new Set(m.sources.map(s=>s.id));m.claims.forEach(c=>c.source_ids.forEach(id=>assert(ids.has(id))));});
test('source IDs are unique',()=>assert.equal(new Set(m.sources.map(s=>s.id)).size,m.sources.length));
test('claim IDs are unique',()=>assert.equal(new Set(m.claims.map(c=>c.id)).size,m.claims.length));
test('all commercial activation gates remain open',()=>validateCommerceMatrix(m));
test('claimed paid outcomes remain NOT COMPUTABLE',()=>assert.equal(m.measurement.status,'NOT_COMPUTABLE'));
test('financial formula uses amounts not unitless order counts',()=>{assert.match(m.measurement.formula,/settled_owned_product_receipts/);assert.match(m.measurement.formula,/cleared_affiliate_commissions/);assert.doesNotMatch(m.measurement.formula,/confirmed_paid_orders\s*\+/);});
test('merchant-click and paid conversion are separate',()=>{assert(m.measurement.chain.includes('merchant_confirmed_paid_conversion'));assert(m.measurement.chain.includes('merchant_outbound_click_if_authorized'));});
test('seven and thirty day cohorts declared',()=>assert.deepEqual(m.measurement.cohorts,[7,30]));
test('Grok actual asset IDs not invented',()=>m.creator_funnel.forEach(x=>assert(!/^[0-9]{5,}$/.test(x.asset_id))));
test('unpublished research receives no real external route',()=>assert.equal(m.creator_funnel.at(-1).published_destination,null));
test('existing source vendor efficacy stays unsubstantiated',()=>assert(m.claims.some(c=>c.decision==='EXCLUDE_UNSUBSTANTIATED')));
test('plan includes economic conversion and no-activation stance',()=>{assert.match(plan,/NOT COMPUTABLE/);assert.match(plan,/no purchase referral/i);});
test('plan preserves homepage, canonical Mind and Dispatch',()=>['#49','#150','#172','#174'].forEach(x=>assert(plan.includes(x))));
test('no tests accidentally permit billing or email events',()=>assert.doesNotMatch(a+b+hub,/<form\b|<script\b|<iframe\b/i));
let mutations = 0;
function rejectMutant(name, fn) {assert.throws(fn,undefined,name);mutations++;process.stdout.write('BLOCK '+mutations+': '+name+'\n');}
rejectMutant('purchase enabled',()=>guideCompliant(a.replace(/<button class="disabled" type="button" disabled/,'<button class="disabled" type="button"')));
rejectMutant('affiliate disclosure removed',()=>guideCompliant(a.replace('may earn a commission at no additional cost to you','')));
rejectMutant('new tracking code',()=>noActiveMarkup(a+'<script>alert(1)</script>'));
rejectMutant('new email subscriber form',()=>noActiveMarkup(hub+'<form action="/subscribe">'));
rejectMutant('embedded third-party video',()=>noActiveMarkup(b+'<iframe src="https://youtube.com/embed/foo">'));
rejectMutant('affiliate earning destination introduced',()=>noActiveMarkup(a+'<a href="https://www.awin1.com/cread.php?x=y">buy</a>'));
rejectMutant('unapproved active video',()=>noActiveMarkup(b+'<video controls preload="auto"></video>'));
rejectMutant('missing required noindex',()=>assert.match(a.replace('noindex,nofollow','index,follow'),/<meta name="robots" content="noindex,nofollow">/));
rejectMutant('invalid captions',()=>validateCaptions(vtt.replace('WEBVTT','BROKEN')));
rejectMutant('invented closed merchant gate',()=>validateCommerceMatrix({...m,authorization_gates:m.authorization_gates.map((g,i)=>i===0?{...g,state:'CLOSED'}:g)}));
rejectMutant('wrong revenue order count units',()=>assert.doesNotMatch('confirmed_paid_orders + cleared_affiliate_commissions',/confirmed_paid_orders\s*\+/));
rejectMutant('fabricated net revenue',()=>validateCommerceMatrix({...m,measurement:{...m.measurement,status:'VERIFIED_REVENUE'}}));
process.stdout.write('R207 PASS '+count+' assertions; '+mutations+' unsafe changes detected. Source only: NOT browser/CI/WordPress/checkout/paid proof.\n');
