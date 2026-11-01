'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const get=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const a=get('ZEN12-WP-VARIANT-A.html'),b=get('ZEN12-WP-VARIANT-B.html'),art=get('INVESTIGATION.md'),wp=get('INVESTIGATION-WP-DRAFT.html'),hub=get('HUB-WP-DRAFT.html'),matrix=get('EVIDENCE-MATRIX.csv');
let checks=0;
function check(name,fn){fn();checks++;}
function safe(page){return !['href="https://zen12.com/getstarted"','<form','<iframe','<video',' autoplay',' onclick=','<script'].some(token=>page.includes(token))&&page.includes('may earn a commission at no additional cost to you.')&&page.includes('disabled aria-disabled="true"');}
check('original manuscript size',()=>assert.ok(art.split(' ').length>1500));
check('wp manuscript',()=>assert.ok(wp.includes('The Hand You Could See but Did Not Own')));
check('no merchant in investigation',()=>assert.ok(!wp.includes('zen12.com')&&!wp.includes('commission')));
check('primary studies',()=>assert.ok(art.includes('10.1038/35784')&&art.includes('10.1371/journal.pone.0021659')&&art.includes('10.3389/fnhum.2022.834492')));
check('safe variants',()=>assert.ok(safe(a)&&safe(b)));
check('same R33 evidence note',()=>assert.ok(a.includes('data-r33-shared="true"')&&b.includes('data-r33-shared="true"')));
check('disabled CTA',()=>assert.ok(a.includes('Product link not yet authorized')&&b.includes('Product link not yet authorized')));
check('optional B only',()=>assert.ok(!a.includes('data-variant-only="B"')&&b.includes('data-variant-only="B"')));
check('real film unhosted',()=>assert.ok(!b.includes('<video')&&!b.includes('autoplay')));
check('existing Focus preserved',()=>assert.ok(a.includes('finalvestige.com/focus/')));
check('alternate hub remains unpublished',()=>assert.ok(hub.includes('unpublished')||hub.includes('UNPUBLISHED')));
check('matrix expanded',()=>assert.ok(matrix.trim().split('\n').length>=81));
check('research entries',()=>assert.ok(matrix.includes('RHI61')&&matrix.includes('FTC78')&&matrix.includes('AFF75')));
check('film caption ends at 40s',()=>assert.ok(get('FILM.vtt').includes('00:00:40.000')));
check('telemetry hard off',()=>assert.ok(get('privacy-off.cjs').includes('ENABLED=false')));
check('privacy synthetic selftests',()=>assert.ok(require('./privacy-off.cjs').selfTest().passed>=20));
const mutations=[
 a.replace('disabled aria-disabled="true"',''),
 a.replace('may earn a commission at no additional cost to you.',''),
 a.replace('</article>','<iframe src="https://example.com"></iframe></article>'),
 b.replace('</article>','<video autoplay></video></article>'),
 b.replace('</article>','<form><input type="email"></form></article>'),
 b.replace('</article>','<script src="https://example.com/script.js"></script></article>')
];
mutations.forEach((m,i)=>check('bad mutation '+i,()=>assert.equal(safe(m),false)));
console.log(JSON.stringify({status:'PASS',assertions:checks,privacyAssertions:require('./privacy-off.cjs').selfTest().passed,activeAffiliateLinks:0}));
