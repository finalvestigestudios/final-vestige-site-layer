/* Standalone reproducible source-only Node test: node mind/r237/test_r237.cjs
   Source snapshots are NOT browser or merchant acceptance. No network or npm dependencies. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=(f)=>fs.readFileSync(path.join(__dirname,f),'utf8');
const a=read('zen12-presell-A.html'), b=read('zen12-presell-B.html'), h=read('mind-hub-preview.html');
const v=read('zen12-42s-concept.vtt'), m=JSON.parse(read('CLAIMS-AND-AUTHORIZATION.json'));
function checkHtml(s){
 assert(!/<(?:script|iframe|video|audio|form|input)\b/i.test(s),'no dynamic embed/form/input');
 assert(!/\bon(?:click|load|error|focus|submit|mouseover)\s*=/i.test(s),'no inline event handler');
 assert(!/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(s),'no active merchant anchor');
 const buttons=[...s.matchAll(/<button\b([^>]*)>/gi)];assert.equal(buttons.length,1,'one button');
 assert(/(?:^|\s)disabled(?:\s|=|$)/i.test(buttons[0][1]),'genuine disabled attribute');
 assert(s.includes('may earn a commission'),'plain-language disclosure');
}
[a,b,h].forEach(checkHtml);
assert.equal(b.replace(/<details class="card" id="optional-film">[\s\S]*?<\/details>/,''),a,'same buyer copy except optional film');
assert(!a.includes('id="optional-film"'));
assert(b.includes('id="optional-film"'));
assert(v.startsWith('WEBVTT'));
const tt=[...v.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
assert.equal(tt.length,7,'seven caption cues');
let e=0; for(const t of tt){const vals=t.slice(1).map(Number);let first=((vals[0]*60+vals[1])*60+vals[2])*1000+vals[3];let last=((vals[4]*60+vals[5])*60+vals[6])*1000+vals[7];assert.equal(first,e,'contiguous');assert(last>first);e=last;}assert.equal(e,42000,'42s');
assert.equal(m.sources.length,16); assert.equal(m.claims.length,25); assert.equal(m.gates.length,16);
assert(m.gates.every(x=>x.status==='HARD_HOLD'));assert.equal(m.commercial_activation,false);
assert(m.claims.every(x=>m.sources.some(s=>s.id===x.source_id)),'all claims reference sources');
assert.equal(m.revenue.net_revenue_per_1000_qualified_human_sessions,null);
console.log('PASS R237 source-only: A/B content parity, inactive buttons, disclosures, 42s captions, 16 sources/25 claims/16 held gates. Browser and merchant not tested.');


/* R239 reviewed refresh of inherited R237 frozen pins at prior R238 HEAD; any later modified article, buyer arm, hub,
   captions, matrix or revenue plan requires a separately reviewed pin refresh. */
function fnv32(text){let h=2166136261;for(let i=0;i<text.length;i++){h=Math.imul((h^text.charCodeAt(i)),16777619)>>>0;}return h.toString(16).padStart(8,'0');}
const expectedPins={
  "THE-HAND-THAT-NEVER-TOUCHED-HER-UNPUBLISHED.md": "5eb3e6eb",
  "zen12-presell-A.html": "1ad6e4c3",
  "zen12-presell-B.html": "4b264450",
  "mind-hub-preview.html": "3e940ac7",
  "zen12-42s-concept.vtt": "fdd2559c",
  "CLAIMS-AND-AUTHORIZATION.json": "45b24f19",
  "CREATOR-REVENUE-EXPERIMENT-RELEASE.md": "f6467816"
};
for(const [filename,digest] of Object.entries(expectedPins)){
 assert.equal(fnv32(read(filename)),digest,'source integrity: '+filename);
}
console.log('PASS R237 frozen source pins: '+Object.keys(expectedPins).length+' original artifacts.');
