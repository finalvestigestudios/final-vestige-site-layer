import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
const folder=dirname(fileURLToPath(import.meta.url));
const f=n=>readFileSync(join(folder,n),'utf8');
const a=f('zen12-text-only.blocks.html'),b=f('zen12-film-option.blocks.html');
const editorial=f('investigation.md'),editorialHtml=f('investigation.blocks.html');
const guide=f('zen12-independent-guide.md'),hub=f('mind-hub-alternative.blocks.html');
const matrix=f('claims-and-permissions.csv'),caption=f('captions.vtt');
const core=s=>(s.match(/<article[^>]+data-core="zen12-independent-guide"[^>]*>([\s\S]*?)<\/article>/)||[])[1];
const hrefs=s=>[...s.matchAll(/href="([^"]+)"/g)].map(m=>m[1]);
function scanRisk(s) {
 const bad=[];
 if (hrefs(s).some(h=>/zen12\.com|inspire3\.com|hypnosislive\.com|clickbank|hop\.click/i.test(h)))bad.push('merchant-link');
 if (/<script\b|<form\b|<iframe\b|<input\b/i.test(s)) bad.push('scripts-forms-embeds');
 if (/<video\b[^>]*\bautoplay|<audio\b[^>]*\bautoplay/i.test(s))bad.push('autoplay');
 if (!/Affiliate disclosure:/i.test(s))bad.push('disclosure');
 if (!/<button\b[^>]*\bdisabled\b/i.test(s))bad.push('enabled-offer');
 if (/on(click|load|error)\s*=|fetch\s*\(|sendBeacon\s*\(/i.test(s))bad.push('active-tracker');
 return bad;
}
for (const [n,x] of [['text',a],['film',b]]) {
 test(n+' exactly one h1',()=>assert.equal((x.match(/<h1\b/g)||[]).length,1));
 test(n+' no unsafe checkout or instrumentation',()=>assert.deepEqual(scanRisk(x),[]));
 test(n+' has nearby disclosure and genuinely disabled offer',()=>{
  const n=x.indexOf('Affiliate disclosure:');
  const btn=x.indexOf('<button ',n);
  assert.ok(n>0&&btn>n&&btn-n<1100);
  assert.match(x.slice(btn,btn+150),/\bdisabled\b/);
 });
 test(n+' no seller hrefs',()=>assert.ok(hrefs(x).every(h=>!/zen12|inspire3|clickbank|hypnosislive/.test(h))));
 test(n+' existing Focus link only',()=>assert.ok(hrefs(x).some(h=>h.includes('/focus/'))));
}
test('A/B substantive guide byte-equivalent',()=>assert.equal(core(a),core(b)));
test('A/B same substantial unmodified guide',()=>assert.ok(core(a).length>12000));
test('source guide retains editor-only exact seller citations',()=>assert.match(guide,/https:\/\/zen12\.com\/hnp/));
test('investigation is evidence-first with no vendor endorsement',()=>{
 assert.ok(editorial.split(/\s+/).length>1500);assert.doesNotMatch(editorial,/Zen12|Inspire3|affiliate/i);
});
test('investigation has primary science URLs',()=>{assert.match(editorial,/10\.1038\/35784/);assert.match(editorial,/10\.1371\/journal\.pone\.0021659/)});
test('editorial WordPress HTML is readable without scripts',()=>{assert.match(editorialHtml,/<article>/);assert.doesNotMatch(editorialHtml,/<script\b|<iframe\b|<form\b/i)});
test('canonical hub not replaced by alternate',()=>{assert.match(hub,/Not a live route/);assert.doesNotMatch(hub,/<form\b|<script\b|<iframe\b/i)});
test('50+ source-mapped claims',()=>assert.ok(matrix.split('\n').filter(r=>r.startsWith('"M')).length>=50));
test('caption file covers exact forty seconds',()=>{assert.match(caption,/WEBVTT/);assert.match(caption,/00:00:34\.000 --> 00:00:40\.000/);assert.equal((caption.match(/ --> /g)||[]).length,6)});
test('film is honest offline static preview',()=>{assert.match(b,/not a video player/);assert.match(b,/Full accessible transcript/);assert.doesNotMatch(b,/<video\b|<iframe\b/i)});
const inject=[
 ['affiliate-enabled',a.replace('<button type="button" disabled','<button type="button"')],
 ['merchant-embedded',a.replace('</article>','<a href="https://zen12.com/hnp">BUY</a></article>')],
 ['disclosure-missing',a.replace('Affiliate disclosure:','Editorial note:')],
 ['form-added',a.replace('</article>','<form method="post"></form></article>')],
 ['script-added',a.replace('</article>','<script>fetch("https://x.invalid")</script></article>')],
 ['iframe-added',a.replace('</article>','<iframe src="https://x.invalid"></iframe></article>')],
 ['autoplay-added',a.replace('</article>','<video autoplay></video></article>')],
 ['tracker-added',a.replace('</article>','<span onclick="sendBeacon()">x</span></article>')]
];
for(const [n,mutated] of inject)test('mutation detector catches '+n,()=>assert.ok(scanRisk(mutated).length>0));
