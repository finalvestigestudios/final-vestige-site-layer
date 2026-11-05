'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=__dirname;
const read=name=>fs.readFileSync(path.join(root,name),'utf8');
const a=read('zen12-variant-a.html'), b=read('zen12-variant-b.html');
const matrix=JSON.parse(read('claim-source-matrix.json'));
const guide=read('buyer-guide.md'), article=read('historical-investigation.md'), hub=read('mind-hub-wordpress-draft.html');
let count=0; const test=(name,fn)=>{fn();++count;process.stdout.write('PASS '+name+'\n');};
for(const [label,html] of [['A',a],['B',b]]) {
test(label+' disclosure next to blocked checkout',()=>{assert.match(html,/Prospective affiliate disclosure:[\s\S]{0,500}<button[^>]+disabled/);});
test(label+' no merchant earning URL/link or active commerce',()=>{assert.doesNotMatch(html,/<a[^>]+href="[^"]*\?(?:[^"]*&)?(?:ref|aff|affiliate|aid)=/i);assert.doesNotMatch(html,/https?:\/\/payhip\.com\//);assert.match(html,/button type="button" disabled/);});
test(label+' no tracking scripts or email forms',()=>{assert.doesNotMatch(html,/<script\b|<form\b|<iframe\b|\sautoplay(?:\s|=|>)/i);});
test(label+' Focus and mobile essentials',()=>{assert.match(html,/https:\/\/finalvestige.com\/focus\//);assert.match(html,/name="viewport"/);assert.match(html,/:focus-visible/);assert.match(html,/@media\(max-width:700px\)/);assert.match(html,/prefers-reduced-motion/);});
test(label+' claims and seller privacy explained',()=>{assert.match(html,/seller-described features/);assert.match(html,/inspire3.com\/privacy/);assert.match(html,/newsletter/);});
}
test('B adds film only, A is text only',()=>{assert.doesNotMatch(a,/id="film-title"/);assert.match(b,/id="film-title"/);assert.match(b,/00:34–00:40/);assert.match(b,/storyboard, not playable video/);});
test('A and B common content exact',()=>{const scrub=s=>s.replace(/<section aria-labelledby="film-title">[\s\S]*?<\/section>/,'').replace(/Unpublished research prototype · [AB]/g,'Unpublished research prototype').replace(/draft [AB]/g,'draft').replace(/Variant [AB], unpublished/g,'Variant, unpublished'); assert.equal(scrub(a),scrub(b));});
test('all claims have source and distinct disposition',()=>{assert(matrix.claims.length>=15);matrix.claims.forEach(x=>{assert.match(x.source,/^https:\/\//);assert(x.disposition&&x.origin&&x.id);});});
test('all commercial gates closed and no affiliate URL',()=>{assert.equal(matrix.no_affiliate_url,true);assert(matrix.closed_gates.length>=15);assert.equal(matrix.metric_contract.status,'NOT_COMPUTABLE_NO_DENOMINATOR_OR_MERCHANT_SETTLEMENT');});
test('no invented sales or affiliate approval',()=>{assert.match(guide,/no approved earning link/i);assert.match(guide,/have not listened/i);assert.match(article,/No affiliate earning link/i);});
test('historical manuscript independently sourced, not medical sales copy',()=>{assert.match(article,/Project Gutenberg/);assert.match(article,/JAMA/);assert.match(article,/not Final Vestige medical advice/);assert.match(article,/not product-specific substantiation/i);});
test('hub published destinations only and no new form',()=>{assert.match(hub,/Change Blindness/);assert.match(hub,/puysegurs-animal-magnetism-files/);assert.match(hub,/finalvestige.com\/focus/);assert.doesNotMatch(hub,/<form\b|<script\b|https?:\/\/affiliates\.inspire3/i);});
test('three distinct nonfabricated creator routes',()=>{assert.equal(matrix.editorial_paths.length,3);assert(matrix.editorial_paths.every(x=>x.grok_asset_id===null));assert.equal(matrix.editorial_paths[2].published_url,null);});
process.stdout.write(count+' structural checks PASSED (native Node required to run this file).\n');
