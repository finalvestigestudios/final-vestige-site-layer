'use strict';
// R315 read-only deterministic source-control tests. Run: node mind/r315/verify_r315.cjs
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const at = name => fs.readFileSync(path.join(__dirname,name),'utf8');
const a=at('ZEN12-A-TEXT-ONLY-PRESELL-REVIEW.html');
const b=at('ZEN12-B-OPTIONAL-42S-FILM-PRESELL-REVIEW.html');
const hub=at('MIND-FOUR-STREAM-WP-REVIEW-ONLY.html');
const article=at('THE-THIRD-TONE-THAT-WAS-NEVER-PLAYED-UNPUBLISHED.md');
const matrix=JSON.parse(at('CLAIM-SOURCE-PARTNER-AUTHORIZATION-MATRIX.json'));
const vtt=at('ORIGINAL-42S-STORYBOARD-CAPTIONS.vtt');
const acceptance=at('OFFER-FUNNEL-MEASUREMENT-AND-RELEASE-ACCEPTANCE.md');
let pass=0;function check(label,fn){fn();console.log('PASS '+label);pass++;}
const merchantLinks=/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)(?:\b|\/)/i;
const noDanger=/<\s*(?:script|iframe|form|input|video|audio)\b|\bautoplay\b|\bonclick\s*=|fetch\s*\(|gtag\s*\(/i;
function inspectHtml(h){
  assert.match(h,/<!doctype html>/i); assert.match(h,/<html lang="en">/);
  assert.match(h,/<meta name="robots" content="noindex,nofollow">/);
  assert.ok(!noDanger.test(h),'JS/form/autoplay/media prohibited until approved');
  assert.ok(!merchantLinks.test(h),'active product sale link prohibited');
  assert.match(h,/disabled aria-disabled="true"/);
  assert.match(h,/Affiliate disclosure:/i);
  assert.match(h,/commission at no (?:additional |extra )?cost/i);
  assert.match(h,/https:\/\/finalvestige\.com\/focus\//);
  assert.doesNotMatch(h,/\b(?:guaranteed brainwave|guaranteed health|proven zen12 results|100% focus|earned \$|commission earned)\b/i);
}
for(const [name,h] of [['A',a],['B',b],['hub',hub]]) check(name+' source safety',()=>inspectHtml(h));
check('A/B exact core buyer copy',()=>assert.equal(a.split('<article class="layout">')[1],b.split('<article class="layout">')[1]));
check('B film concept only',()=>{assert.match(b,/<figure class="film"/);assert.match(b,/<summary>Read the complete 42-second transcript<\/summary>/);assert.doesNotMatch(a,/<figure class="film"/);});
check('one existing lead funnel',()=>{for(const h of [a,b,hub])assert.ok(!/<form\b/i.test(h));});
check('all 18 commercial gates held',()=>{assert.equal(matrix.gates.length,18);for(const x of matrix.gates)assert.equal(x.status,'HARD_HOLD')});
check('claims cite defined sources',()=>{assert.ok(matrix.claims.length>=30);for(const c of matrix.claims){assert.ok(c.claim&&c.disposition);for(const id of c.source_ids)assert.ok(matrix.sources[id]);}});
check('three creator candidates not invented IDs',()=>{assert.equal(matrix.creator_topic_product_fit.length,3);for(const c of matrix.creator_topic_product_fit){assert.equal(c.video_asset_id,null);assert.equal(c.video_url,null)}});
check('revenue classification',()=>{assert.equal(matrix.money.state,'NOT COMPUTABLE');assert.match(acceptance,/settled_net_attributed_revenue/);assert.match(acceptance,/affiliate_click/);assert.match(acceptance,/merchant_confirmed_paid_order/);});
check('caption timings exactly 42 seconds',()=>{assert.ok(vtt.startsWith('WEBVTT'));const times=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];assert.equal(times.length,6);assert.equal(times[0][1],'00:00:00.000');assert.equal(times.at(-1)[2],'00:00:42.000');for(let i=1;i<times.length;i++)assert.equal(times[i-1][2],times[i][1]);});
check('article core source accuracy witnesses',()=>{for(const z of ['Five reported','eight reported','one reported mixed','g = 0.40','not a finding established','not a product review'])assert.ok(article.includes(z),'missing: '+z);});
check('no external active merchant links even in research hub',()=>{for(const h of [a,b,hub])assert.ok(!merchantLinks.test(h));});
check('near-link commission disclosure follows commercial heading',()=>{for(const h of [a,b,hub]){const p=h.indexOf('class="disclose'); const btn=h.indexOf('disabled aria-disabled="true"');assert.ok(p>0 && btn>p && btn-p<1500)}});
check('WCAG static constructs present',()=>{for(const h of [a,b,hub]){assert.match(h,/<main id=/);assert.match(h,/:focus-visible/);assert.match(h,/prefers-reduced-motion/);assert.match(h,/@media\(max-width:/);}});
const mutations=[
'<script src="https://example.com/a.js"></script>','<iframe src="https://example.com"></iframe>','<form action="/new-list"></form>',
'<input name="email">','<video autoplay></video>','<audio controls></audio>','<button onclick="send()">Go</button>',
'<a href="https://zen12.com/getstarted">BUY</a>','<a href="https://hypnosislive.com/mental-skills/total-focus">BUY</a>',
'<a href="https://brainwaveshots.com/focus-shot">BUY</a>','<a href="https://affiliates.inspire3.com/">JOIN</a>',
'<button>100% focus guaranteed</button>','<button>Proven Zen12 results</button>','<button>Guaranteed health</button>',
'<button>Commission earned $100</button>'
];
for (const [i,bad] of mutations.entries())check('unsafe mutation '+(i+1)+' rejected',()=>assert.throws(()=>inspectHtml(a+bad)));
console.log('R315 deterministic read-only source checks passed: '+pass+'/'+pass+'. Native Node environment required for this report. Browser/WordPress/checkout not covered.');
