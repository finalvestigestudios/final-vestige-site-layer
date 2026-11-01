/** Native Node 20+ reproducible semantic guardrails; not a substitute for real browser WCAG/Lighthouse. */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {ENABLED, selfTest} from './attribution-hard-off.mjs';
const read = name => fs.readFileSync(new URL(name, import.meta.url),'utf8');
const a=read('zen12-a-text.wp.html'), b=read('zen12-b-film.wp.html');
const inv=read('choice-blindness-investigation.wp.html'),hub=read('mind-hub-alternative.wp.html');
const article=read('choice-blindness-investigation.md'), guide=read('zen12-evidence-guide.md');
const claims=read('claims-and-permissions.tsv'), sources=read('source-register.tsv'),vtt=read('choice-film-captions.vtt');
let passed=0,mutations=0;
function ok(predicate,why){assert.ok(predicate,why);passed++}
function core(markup){const id='<div id="fvz-guide-core">'; assert.ok(markup.includes(id)); return markup.split(id)[1]}
function noMerchantAnchor(markup){return !/<a\\b[^>]*\\bhref=["']https:\\/\\/(?:zen12\\.com|(?:www\\.)?inspire3\\.com|hypnosislive\\.com|affiliates\\.inspire3\\.com)/i.test(markup)}
function disclosureSafe(markup){const d=markup.indexOf('may earn a commission at no additional cost to you'); const c=markup.indexOf('Merchant link withheld — approval pending');return d>=0&&c>d&&markup.slice(d,c).length<2000}
function noActiveComponents(markup){return !/<(?:script|iframe|form|video)\\b/i.test(markup)&&!/<a\\b[^>]*\\bhref=["'][^"']*(?:affiliate|checkout|zen12\\.com)/i.test(markup)}
function coreSafe(markup){return disclosureSafe(markup)&&noMerchantAnchor(markup)&&noActiveComponents(markup)}
ok(core(a)===core(b),'A and B guide cores byte-for-byte equal');
for(const [name,s] of [['A',a],['B',b]]){
 ok(disclosureSafe(s),name+' disclosure adjacent and before inert CTA');
 ok(noMerchantAnchor(s),name+' no merchant live source links');
 ok(noActiveComponents(s),name+' no scripts/iframe/form/video/buying anchor');
 ok(s.includes('Merchant link withheld — approval pending'),name+' inert purchase status');
 ok(s.includes('Beginner')&&s.includes('Premium')&&s.includes('Advanced'),name+' exact tiers');
 ok(s.includes('24 MP3')&&s.includes('48 MP3'),name+' package file counts');
 ok(s.includes('2023'),name+' independent research review');
 ok(s.includes('https://finalvestige.com/focus/'),name+' one existing Focus route');
 ok(!/href=["']\\/mind\\//i.test(s),name+' no unlaunched hub link');
 ok(s.includes('@media(max-width:760px)'),name+' responsive CSS breakpoint');
 ok(s.includes(':focus-visible'),name+' visible keyboard focus');
 ok(s.includes('prefers-reduced-motion:reduce'),name+' reduced motion');
}
ok(b.includes('40-second thought experiment')&&b.includes('Read the full proposed film transcript'),'B has optional educational transcript');
ok(!a.includes('Read the full proposed film transcript'),'A has no film');
ok(b.includes('No autoplay')&&b.includes('not been produced or hosted'),'B not misleading');
ok(/WEBVTT/.test(vtt)&&/00:00:40\\.000/.test(vtt),'VTT spec 40 seconds');
ok(/role="img"/.test(b)&&/<title id="fvz-poster-title">/.test(b),'poster inline accessible title');
ok(!/commission|Zen12|purchase link/i.test(inv),'investigation commercially independent');
ok(/Puységur/.test(inv)&&/10\\.1126\\/science\\.1111709/.test(inv),'investigation primary source and historical bridge');
ok(!/<(?:script|iframe|form)\\b/i.test(hub),'alternate hub no scripts or forms');
ok(!/href=["']\\/mind\\//.test(hub),'no fabricated live /mind/');
ok(/153/.test(article)&&/16 case dossiers/.test(article),'historical provenance');
ok(/five reported findings/.test(guide)&&/eight reported conflicting/.test(guide),'systematic-review denominators');
ok(claims.split('\\n').length>=65,'large evidence claim matrix');
ok(sources.split('\\n').length>=19,'source list');
ok(ENABLED===false,'attribution hard disabled');
const privacy=selfTest();ok(privacy.passed>=16&&privacy.enabled===false,'synthetic privacy safety suite');
const attacks=[
 s=>s.replace('may earn a commission at no additional cost to you',''),
 s=>s.replace('Merchant link withheld — approval pending','<a href="https://zen12.com/getstarted">Buy now</a>'),
 s=>s.replace('Merchant link withheld — approval pending','<a href="https://affiliates.inspire3.com/?id=bogus">Get it</a>'),
 s=>s.replace('Merchant link withheld — approval pending','<iframe src="https://example.com"></iframe>'),
 s=>s.replace('Merchant link withheld — approval pending','<form><input type="email"></form>'),
 s=>s.replace('Merchant link withheld — approval pending','<script>alert(1)</script>'),
 s=>s.replace('Merchant link withheld — approval pending','<video autoplay src="https://example.com/video.mp4"></video>')
];
for(const [i,attack] of attacks.entries()){if(!coreSafe(attack(a)))mutations++;else throw Error('Unsafe mutation escaped '+i)}
console.log('R36 QA: '+passed+'/'+passed+' source and privacy assertions PASS; '+mutations+'/'+attacks.length+' dangerous mutations caught; privacy self-test '+privacy.passed+'/'+privacy.passed+' PASS. No browser, CI or purchase flow tested.');
