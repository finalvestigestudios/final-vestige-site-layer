// R449 source-only release guard. Run: node mind/r449/check_r449.mjs
// No network, API credentials, personal data, or writes required.
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import assert from 'node:assert/strict';
const dir=dirname(fileURLToPath(import.meta.url));
const read=f=>readFileSync(join(dir,f),'utf8');
const A=read('ZEN12_A_TEXT_ONLY.html'), B=read('ZEN12_B_42S_FILM_CONCEPT.html');
const hub=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html');
const article=read('THE_GORILLA_IN_THE_LUNG_SCAN.md');
const vtt=read('ZEN12_42S_CAPTIONS.vtt');
const svg=read('ZEN12_42S_POSTER.svg');
const matrix=JSON.parse(read('CLAIM_SOURCE_PARTNER_RELEASE_MATRIX.json'));
const plan=read('OFFER_CREATOR_FUNNEL_REVENUE_ACCEPTANCE.md');
let n=0;const check=(label,fn)=>{fn();n++;process.stdout.write('PASS '+String(n).padStart(2,'0')+' '+label+'\n')};
for(const [label,page] of [['A',A],['B',B],['hub',hub]]) {
  check(label+' doctype',()=>assert.match(page,/^<!doctype html>/i));
  check(label+' language',()=>assert.match(page,/<html lang="en">/));
  check(label+' one main',()=>assert.equal((page.match(/<main\b/g)||[]).length,1));
  check(label+' viewport',()=>assert.match(page,/name="viewport"/));
  check(label+' keyboard focus',()=>assert.match(page,/:focus-visible/));
  check(label+' mobile media',()=>assert.match(page,/@media\(max-width:/));
  check(label+' reduced motion',()=>assert.match(page,/prefers-reduced-motion/));
  check(label+' no Javascript',()=>assert.doesNotMatch(page,/<script\b|javascript:|onerror=|onclick=|onload=/i));
  check(label+' no additional signup',()=>assert.doesNotMatch(page,/<form\b|<input\b|mailchimp|convertkit|mailerlite/i));
  check(label+' no tracking pixel',()=>assert.doesNotMatch(page,/<iframe\b|<img[^>]*https?:\/\/|googletagmanager|facebook\.com\/tr\//i));
}
for(const [label,page] of [['A',A],['B',B]]) {
  check(label+' native disabled',()=>assert.match(page,/<button[^>]*\sdisabled(?:\s|=|>)[^>]*>/));
  check(label+' adjacent disclosure',()=>{const d=page.indexOf('Potential affiliate disclosure:');const b=page.indexOf('<button',d);assert.ok(d>0&&b>d&&b-d<530)});
  check(label+' no merchant active links',()=>assert.doesNotMatch(page,/<a\b[^>]*href=["']https?:\/\/(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\./i));
  check(label+' no prices or coupons',()=>assert.doesNotMatch(page,/\$[0-9]|coupon code|discount ends tonight/i));
  check(label+' product caution',()=>assert.match(page,/no independent product-specific trial/i));
  check(label+' free route',()=>assert.match(page,/https:\/\/finalvestige.com\/focus\//));
  check(label+' no autoplay or hidden videoplayer',()=>assert.doesNotMatch(page,/<video\b[^>]*\bautoplay\b|<video\b|<audio\b/i));
}
check('control absent film module',()=>assert.doesNotMatch(A,/id="film-concept"/));
check('B film concept present',()=>assert.match(B,/id="film-concept"/));
check('shared substantive copy byte-identical',()=>{const cut=x=>x.slice(x.indexOf('<main id="content">'),x.indexOf('</main>')+7);assert.equal(cut(A),cut(B))});
check('poster local',()=>assert.match(B,/src="\.\/ZEN12_42S_POSTER.svg"/));
check('poster inert',()=>assert.doesNotMatch(svg,/<script|<foreignObject|onload=|href=|xlink:href=/i));
check('poster accessible label',()=>assert.match(svg,/<title id="title">/));
check('captions WEBVTT',()=>assert.match(vtt,/^WEBVTT/));
check('six caption cues',()=>assert.equal((vtt.match(/-->/g)||[]).length,6));
check('last caption ends at 42s',()=>assert.match(vtt,/00:00:42\.000/));
check('hub four streams',()=>['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'].forEach(s=>assert.ok(hub.includes(s),s)));
check('hub not claiming public gorilla URL',()=>assert.match(hub,/no invented live URL/));
check('article exact numbers',()=>['20 of 24','12 actually fixated','547 milliseconds','2024','Puységur'].forEach(s=>assert.ok(article.includes(s),s)));
check('article limitation on clinical errors',()=>assert.match(article,/cannot tell us how often real clinical diagnoses/i));
check('article no external activated commercial link',()=>assert.doesNotMatch(article,/utm_affiliate=|ref=[^ ]*zen12|affiliate_click.*\bhref=/i));
check('evidence matrix count consistent',()=>assert.equal(matrix.claim_count,matrix.claim_rows.length));
check('source keys valid',()=>{const ids=new Set(matrix.public_sources.map(s=>s.id));matrix.claim_rows.forEach(c=>c.source_ids.forEach(id=>assert.ok(ids.has(id),id)))});
check('unique claim ids',()=>assert.equal(new Set(matrix.claim_rows.map(c=>c.id)).size,matrix.claim_rows.length));
check('release gate count 28',()=>assert.equal(matrix.release_gates.length,28));
check('all release gates closed',()=>assert.ok(matrix.release_gates.every(g=>g.passed===false)));
check('merchant no go',()=>assert.equal(matrix.no_paid_offer,true));
check('not an authenticated paid FV owned product',()=>assert.equal(matrix.owned_product_fallback.paid_sku_verified,false));
check('plan separates outbound click from paid settlement',()=>assert.match(plan,/affiliate_click.*outbound|affiliate_click.*NOT sale/s));
check('plan protects existing newsletter',()=>assert.match(plan,/Jetpack/));
check('plan defines founder approval',()=>assert.match(plan,/founder authorization|Founder/));
process.stdout.write('PASS ALL '+n+' static source assertions; native browser/WP/CI/merchant checks NOT RUN\n');
