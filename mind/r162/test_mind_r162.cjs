'use strict';
/**
 * R162 source-level commercial, editorial, privacy and release regressions.
 * Native: node mind/r162/test_mind_r162.cjs
 * No dependencies or network. Does not certify browser/WordPress/merchant outcomes.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const dirname = __dirname;
const files = {
  article: 'the-transfer-problem-meditation-evidence.md',
  html: 'zen12-transfer-gap-offer-review-UNPUBLISHED.html',
  matrix: 'verified-seller-claims-and-closed-release-gates.json',
  funnel: 'one-offer-funnel-fit-and-attribution-contract.md'
};
function load() {
  const result={};
  for (const [key,file] of Object.entries(files)) result[key]=fs.readFileSync(path.join(dirname,file),'utf8');
  return result;
}
function assertSource(raw) {
  const m = JSON.parse(raw.matrix);
  const checks = [
    ['research byline unpublished',()=>raw.article.includes('UNPUBLISHED') && raw.article.includes('The Transfer Problem')],
    ['research long-form',()=>raw.article.trim().split(/\s+/).length >= 1800],
    ['research scientific sources',()=>raw.article.includes('https://doi.org/10.1111/nyas.15095') && raw.article.includes('https://doi.org/10.1371/journal.pone.0286023')],
    ['mindfulness meta outcomes bounded',()=>raw.article.includes('111 randomized controlled trials') && raw.article.includes('9,538 participants')],
    ['audio category error disclosed',()=>raw.article.includes('not every type of rhythmic audio') && raw.article.includes('not the finding')],
    ['research not a sell page',()=>raw.article.includes('commercial_links: none') && !/awin1\.com|hop\.clickbank/i.test(raw.article)],
    ['free original test',()=>raw.article.includes('timer for three minutes') && raw.article.includes('not a treatment')],
    ['science and history separation',()=>raw.article.includes('historical') && raw.article.includes('cannot validate Zen12')],
    ['FTC from primary',()=>raw.article.includes('www.ftc.gov/business-guidance/resources/health-products-compliance-guidance')],
    ['bounded exact seller product',()=>raw.html.includes('12 levels') && raw.html.includes('48 MP3 recordings')],
    ['observed seller price date',()=>raw.html.includes('November 5, 2026') && raw.html.includes('$87.99')],
    ['checkout disambiguation',()=>raw.html.includes('not a verified checkout total')],
    ['seller refund represented as advertised',()=>raw.html.includes('advertised') && raw.html.includes('one-year money-back guarantee')],
    ['unsupported efficacy corrected',()=>raw.html.includes('does not establish product-specific Zen12 equivalence') && raw.html.includes('did not test')],
    ['no active product/merchant href',()=>!/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|brainwaveshots\.com|hypnosislive\.com)/i.test(raw.html)],
    ['no affiliate earning links',()=>!/(awin1\.com|hop\.clickbank|clickbank\.net|[?&](?:aff_id|affid|affiliate_id|hop)=)/i.test(raw.html)],
    ['commercial physically disabled',()=>/<button\b[^>]*\sdisabled(?:\s|>)[^>]*>Merchant purchase link withheld/.test(raw.html)],
    ['no claims of first-hand use',()=>!/we personally tested|we personally used|we tried zen12/i.test(raw.html)],
    ['no active purchase call to action',()=>!/<a\b[^>]*>(?:\s*(?:Buy now|Purchase|Shop Now|Get Zen12)\s*)<\/a>/i.test(raw.html)],
    ['nearby plain commission disclosure',()=>{let k=raw.html.indexOf('Prospective commission disclosure');let b=raw.html.indexOf('Merchant purchase link withheld');return k>=0 && b>k && b-k<650;}],
    ['active first-party Focus CTA only',()=>raw.html.includes('href="https://finalvestige.com/focus/"')],
    ['one mailing list',()=>!/<form\b|<input\b/i.test(raw.html) && raw.html.includes('existing Jetpack signup')],
    ['no external script trackers',()=>!/<script\b|<iframe\b|<link\s+[^>]*stylesheet|<img\b[^>]*https?:\/\//i.test(raw.html)],
    ['no fake media player',()=>!/<video\b|<audio\b|\sautoplay(?:\s|=|>)/i.test(raw.html)],
    ['honest storyboard not video',()=>raw.html.includes('not playable') && raw.html.includes('00:35–00:42')],
    ['transcript available no-JS',()=>raw.html.includes('<details>') && raw.html.includes('<summary>')],
    ['keyboard and reduced motion',()=>raw.html.includes('focus-visible') && raw.html.includes('prefers-reduced-motion')],
    ['responsive design',()=>raw.html.includes('max-width:760px') && raw.html.includes('grid-template-columns:1fr')],
    ['static skip link',()=>raw.html.includes('href="#fv-mind-r162-evidence"') && raw.html.includes('id="fv-mind-r162-evidence"')],
    ['reference integrity',()=>raw.html.includes('https://doi.org/10.1111/nyas.15095') && raw.html.includes('FTC endorsement guidance')],
    ['source register count',()=>m.source_refs.length>=14],
    ['claim decisions count',()=>m.claim_decisions.length>=35],
    ['release gate count',()=>m.release_gates.length>=42],
    ['all hard hold',()=>m.release_decision==='HARD_HOLD' && m.release_gates.every(x=>x.status==='CLOSED')],
    ['authorization null',()=>m.affiliate.publisher_approved===null && m.affiliate.valid_tracking_url===null && m.affiliate.allowed_channels===null],
    ['affiliate sale null',()=>m.affiliate.confirmed_sale===null && m.affiliate.commission===null],
    ['owned paid fallback unverified',()=>m.owned_fallback.paid_sku===null && m.owned_fallback.rights_clearance===null && m.owned_fallback.checkout===null],
    ['net per 1k missing',()=>m.net_revenue_per_1000_qualified_sessions===null && m.net_revenue_status.includes('NOT_COMPUTABLE')],
    ['no claims of tested video',()=>m.video.produced===false && m.video.playable===false && m.video.experiment_run===false],
    ['time accuracy',()=>m.merchant_observed_price.status==='seller_page_only_not_checkout' && m.merchant_observed_price.date==='2026-11-05'],
    ['no synthetic checkout metrics',()=>!/"(?:net_revenue_per_1000_qualified_sessions|confirmed_sale|commission)"\s*:\s*[1-9]/.test(raw.matrix)],
    ['no claims of live edits',()=>m.changes_to_live_systems===0],
    ['clear 7d 30d cohort',()=>raw.funnel.includes('7d|30d') && raw.funnel.includes('tiny-sample')],
    ['qualified denominator',()=>raw.funnel.includes('qualified_human_sessions')],
    ['no fabricated video IDs',()=>raw.funnel.includes('ASSET_ID_FROM_GROK') && raw.funnel.includes('null') ],
    ['separate click and paid conversion',()=>raw.funnel.includes('affiliate_outbound') && raw.funnel.includes('merchant_confirmed_order') && raw.funnel.includes('settlement')],
    ['no purchase claims',()=>raw.funnel.includes('NOT_COMPUTABLE') && raw.funnel.includes('No authenticated')],
    ['no second list',()=>raw.funnel.includes('native Jetpack subscription list') && raw.funnel.includes('no new form')],
    ['A/B ethical and text complete',()=>raw.funnel.includes('A / control') && raw.funnel.includes('B / treatment') && raw.funnel.includes('neither A nor B can be called a commercial conversion test') ],
    ['ownership boundaries',()=>raw.funnel.includes('Grok retains') && raw.funnel.includes('Homepage flagship PR #49')],
    ['missing WP links noted',()=>raw.funnel.includes('#1922') && raw.funnel.includes('#1377')],
    ['no paid product invention',()=>raw.funnel.includes('do not reclassify the free') && m.owned_fallback.paid_sku===null]
  ];
  let passed=0;
  for (const [name,fn] of checks) {
    try { assert.equal(Boolean(fn()),true,name); passed++; }
    catch(e){throw Error('BASELINE RULE FAILED: '+name+'; '+e.message);}
  }
  return passed;
}
function mutate(base,fn){let s={...base};fn(s);return s;}
const adversarial=[
 ['activate merchant URL',s=>{s.html=s.html.replace('<button type="button" disabled','<a href="https://zen12.com/buy"');}],
 ['remove disabled attribute',s=>{s.html=s.html.replace(' disabled aria-disabled',' aria-disabled');}],
 ['add affiliate network',s=>{s.html+='\n<a href="https://www.awin1.com/click?x=1">Purchase</a>';}],
 ['add third-party script',s=>{s.html+='\n<script src="https://analytics.example.invalid/track.js"></script>';}],
 ['add newsletter form',s=>{s.html+='\n<form><input name="email"></form>';}],
 ['remove FTC disclaimer',s=>{s.html=s.html.replace('Prospective commission disclosure','Disclosure missing');}],
 ['remove free CTA',s=>{s.html=s.html.replace('https://finalvestige.com/focus/','/none/');}],
 ['remove reduced motion',s=>{s.html=s.html.replace('prefers-reduced-motion','motion-ignored');}],
 ['remove keyboard focus',s=>{s.html=s.html.replaceAll('focus-visible','focus-ignored');}],
 ['insert autoplay video',s=>{s.html+='\n<video autoplay src="test.mp4"></video>';}],
 ['claim video already playable',s=>{s.matrix=s.matrix.replace('"produced": false','"produced": true');}],
 ['affiliate approved without proof',s=>{s.matrix=s.matrix.replace('"publisher_approved": null','"publisher_approved": true');}],
 ['commission asserted',s=>{s.matrix=s.matrix.replace('"commission": null','"commission": 400');}],
 ['invent a paid SKU',s=>{s.matrix=s.matrix.replace('"paid_sku": null','"paid_sku": "fictional"');}],
 ['clear release gates',s=>{s.matrix=s.matrix.replace('"status": "CLOSED"','"status": "OPEN"');}],
 ['release decision bypass',s=>{s.matrix=s.matrix.replace('"release_decision": "HARD_HOLD"','"release_decision": "READY"');}],
 ['invent net revenue',s=>{s.matrix=s.matrix.replace('"net_revenue_per_1000_qualified_sessions": null','"net_revenue_per_1000_qualified_sessions": 500');}],
 ['rewrite seller price as checkout',s=>{s.html=s.html.replace('not a verified checkout total','verified checkout total');}],
 ['omit central research source',s=>{s.article=s.article.replace('https://doi.org/10.1111/nyas.15095','not-a-source');}],
 ['invent a video media ID',s=>{s.funnel=s.funnel.replace('ASSET_ID_FROM_GROK','invented-video-0001');}],
 ['turn video A/B into a victory claim',s=>{s.funnel=s.funnel.replace('neither A nor B can be called a commercial conversion test','A/B experiment proven profitable');}],
 ['claim copied experience',s=>{s.html=s.html.replace('does not assume we have tried the recordings','we personally tested Zen12 and recommend it');}],
 ['remove transcript',s=>{s.html=s.html.replace('<summary>Read the full timed narration','<p>Read the full timed narration');}],
 ['erase no live edits evidence',s=>{s.matrix=s.matrix.replace('"changes_to_live_systems": 0','"changes_to_live_systems": 1');}]
];
function run(){
 const raw=load(),baseline=assertSource(raw);
 let negatives=0;for (const [name,fn] of adversarial){const dirty=mutate(raw,fn);let detected=false;try{assertSource(dirty);}catch(e){detected=true;} assert.ok(detected,'MUTATION WAS NOT CAUGHT: '+name);negatives++;}
 const result={baseline_assertions:baseline,negative_mutations_detected:negatives,negative_mutations_total:adversarial.length,stage:'SOURCE_LEVEL_ONLY',native_node:false,real_browser:false,live_wordpress:false,affiliate_checkout:false};
 process.stdout.write('Mind R162 source test PASS '+JSON.stringify(result)+'\n');return result;
}
if(require.main===module){run();}
module.exports={run,assertSource};
