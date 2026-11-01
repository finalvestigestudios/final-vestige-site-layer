import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {join,dirname} from "node:path";
import {fileURLToPath} from "node:url";
import {ATTRIBUTION_ENABLED,MIN_GROUP_SIZE,validateSyntheticEvent,recordVisitorEvent,aggregateSyntheticTest} from "./attribution.mjs";

const dir=dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(join(dir,n),"utf8");
const A=read("presell-a-text.wp.html"), B=read("presell-b-optional-film.wp.html");
const core=read("zen12-guide-core.wp.html"),investigation=read("investigation.wp.html");
const matrix=read("claims-permissions.csv"),ledger=read("source-ledger.md");
const vtt=read("film.vtt"),guide=read("zen12-guide.md");
const disclosures=html=>html.match(/class="fv-disclosure"/g)||[];
const merchantAnchors=html=>/<a\b[^>]*href\s*=\s*["'][^"']*(?:zen12\.com|inspire3\.com|affiliates\.inspire3)/i.test(html);
function safePresell(html){
  const buttons=[...html.matchAll(/<button\b[^>]*>[\s\S]*?<\/button>/g)].map(m=>m[0]);
  return buttons.length===2 && buttons.every(b=>/\bdisabled\b/.test(b)&&/\baria-disabled="true"/.test(b)) &&
    disclosures(html).length===2 &&
    !merchantAnchors(html) &&
    !/<(?:script|iframe|form|input)\b/i.test(html) &&
    !/<video\b/i.test(html) && !/\bautoplay\b\s*=\s*["']?true/i.test(html);
}
function extractCore(html){
  const start=html.indexOf('<div class="fv-prose" id="fv-r56-guide-core">');
  assert.ok(start>0,"guide core exists");
  const end=html.indexOf("</div>",start);
  assert.ok(end>start,"guide core closing tag");
  return html.slice(start,end+6);
}
const example=Object.freeze({source:"organic",variant:"A",topic:"zen12-guide",event:"qualified_outbound_click"});
test("Both A and B contain precisely identical substantive guide bytes",()=>{
  assert.equal(extractCore(A),core);
  assert.equal(extractCore(B),core);
  assert.equal(extractCore(A),extractCore(B));
});
test("Both variants are commercially inert by construction",()=>{
  assert.ok(safePresell(A));assert.ok(safePresell(B));
});
test("Disclosure directly precedes each disabled offer control",()=>{
  for(const html of [A,B]){
    const re=/<button\b[^>]*disabled[^>]*>/g;
    const positions=[...html.matchAll(re)].map(m=>m.index);
    assert.equal(positions.length,2);
    for(const position of positions){
      let prior=html.slice(Math.max(0,position-850),position);
      assert.match(prior,/Final Vestige may earn a commission at no additional cost to you/);
    }
  }
});
test("No merchant is reachable from a reader-facing hyperlink",()=>{
  for(const html of [A,B,investigation])assert.equal(merchantAnchors(html),false);
});
test("Video candidate has authentic static explanatory media, not an unhosted fake player",()=>{
  assert.doesNotMatch(A,/<svg\b[^>]*role="img"[^>]*aria-labelledby="clockTitle/);
  assert.match(B,/<svg\b[^>]*role="img"[^>]*aria-labelledby="clockTitle clockDesc"/);
  assert.match(B,/<details>[\s\S]*?<summary>Read the complete film transcript/);
  assert.match(B,/00–07:[\s\S]*?34–40:/);
  assert.doesNotMatch(B,/<video\b|<iframe\b|preload="auto"/);
});
test("Strong semantic headings and shared no-JS responsive design",()=>{
  for(const html of [A,B,investigation]){
    assert.match(html,/<h1>/);
    assert.match(html,/@media\(max-width:790px\)/);
    assert.match(html,/@media\(prefers-reduced-motion:reduce\)/);
    assert.match(html,/:focus-visible/);
    assert.doesNotMatch(html,/<script\b|<form\b/);
  }
});
test("Reader can reach the actual published Focus and Puységur assets without a new signup",()=>{
  for(const html of [A,B]){
    assert.match(html,/href="https:\/\/finalvestige.com\/focus\/"/);
    assert.match(html,/href="https:\/\/finalvestige.com\/free-resources\/puysegurs-animal-magnetism-files\/"/);
    assert.doesNotMatch(html,/type="email"|<form\b/);
  }
});
test("Chronostasis article contains primary research and no sales buttons",()=>{
  assert.match(investigation,/Yarrow/);
  assert.match(investigation,/Hodinott-Hill/);
  assert.match(investigation,/10\.1038\/35104551/);
  assert.match(investigation,/12401174/);
  assert.doesNotMatch(investigation,/<button\b|may earn a commission/);
});
test("Guide states unsupported seller claims are not product-specific scientific proof",()=>{
  assert.match(guide,/cannot substantiate these product-specific outcomes/);
  assert.match(guide,/not a Zen12 trial/);
  assert.match(guide,/No earning link is active in this draft/);
  assert.match(guide,/mobile phone number/);
});
test("Actual seller page and independent scientific-source ledger are explicit",()=>{
  for(const href of ["https://inspire3.com/","https://zen12.com/hnp","https://zen12.com/about","https://zen12.com/research","https://zen12.com/getstarted","https://inspire3.com/privacy/","https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety"]){
    assert.ok(ledger.includes(href),href);
  }
  assert.match(ledger,/2026-11-01/);
});
test("Claim permission matrix records 62 independently dispositioned decisions",()=>{
  const lines=matrix.trim().split("\n");
  assert.equal(lines.length-1,62);
  for(const id of ["C001","S011","P001","A004","A005","A009","A019"])
    assert.ok(matrix.includes('"'+id+'"'),id);
  assert.match(matrix,/HARD HOLD/);
  assert.match(matrix,/REJECT/);
});
test("Attribution never captures events and rejects extra identifying fields",()=>{
  assert.equal(ATTRIBUTION_ENABLED,false);
  assert.equal(recordVisitorEvent(example),null);
  assert.throws(()=>validateSyntheticEvent({...example,email:"person@example.com"}));
  assert.throws(()=>validateSyntheticEvent({...example,ip:"1.2.3.4"}));
  assert.throws(()=>validateSyntheticEvent({...example,order_id:"abc"}));
  assert.throws(()=>validateSyntheticEvent({...example,full_referrer:"https://example.org/?secret=1"}));
});
test("Privacy allowlist rejects malicious/inapplicable categories",()=>{
  assert.deepEqual(validateSyntheticEvent(example),example);
  assert.throws(()=>validateSyntheticEvent({...example,source:"https://personal.example?q=private"}));
  assert.throws(()=>validateSyntheticEvent({...example,event:"purchase"}));
  assert.throws(()=>validateSyntheticEvent({...example,variant:"C"}));
  assert.throws(()=>validateSyntheticEvent(null));
});
test("Synthetic aggregation suppresses groups with fewer than twenty records",()=>{
  assert.equal(MIN_GROUP_SIZE,20);
  assert.equal(aggregateSyntheticTest(Array(19).fill(example)).length,0);
  const result=aggregateSyntheticTest(Array(20).fill(example));
  assert.deepEqual(result,[{...example,count:20}]);
});
test("Synthetic source and variant are not combined across groups",()=>{
  const r=aggregateSyntheticTest([...Array(19).fill(example),...Array(20).fill({...example,variant:"B"})]);
  assert.equal(r.length,1);assert.equal(r[0].variant,"B");assert.equal(r[0].count,20);
});
test("Caption track has six contiguous cues totaling precisely forty seconds",()=>{
  const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
  assert.equal(cues.length,6);
  const sec=(h,m,s,ms)=>Number(h)*3600+Number(m)*60+Number(s)+Number(ms)/1000;
  let expected=0;
  for(const cue of cues){
    const start=sec(...cue.slice(1,5)),end=sec(...cue.slice(5,9));
    assert.equal(start,expected);assert.ok(end>start);expected=end;
  }
  assert.equal(expected,40);
});
test("Unsafe release mutations fail closed: link activation, form, script, disclosure or controls",()=>{
  const mutations=[
    A.replace(/disabled aria-disabled="true"/g,'aria-disabled="false"'),
    A.replace(/class="fv-disclosure"/g,'class="notice"'),
    A.replace("</main>",'<a href="https://zen12.com/getstarted">Buy now</a></main>'),
    A.replace("</main>",'<script src="https://tracker.example/pixel.js"></script></main>'),
    A.replace("</main>",'<form><input type="email"></form></main>'),
    A.replace("</main>",'<iframe src="https://other.example"></iframe></main>'),
    A.replace("</main>",'<video controls preload="auto" autoplay></video></main>')
  ];
  for(const mutated of mutations)assert.equal(safePresell(mutated),false);
});
