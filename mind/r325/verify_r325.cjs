/* Final Vestige Mind R325: offline source-level checks. No web traffic, network, merchant, CMS, or analytics writes.
 * Run: node mind/r325/verify_r325.cjs
 * Requires Node builtin fs/path/assert only. This is source QA, not browser, WCAG or release certification.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = __dirname;
const read = (p) => fs.readFileSync(path.join(root,p),'utf8');
const filenames = {
  article:'THE-DOORWAY-THAT-DID-NOT-ALWAYS-ERASE-THE-THOUGHT-UNPUBLISHED.md',
  A:'ZEN12-A-TEXT-EVIDENCE-PRESELL-REVIEW.html',
  B:'ZEN12-B-OPTIONAL-42S-STORYBOARD-REVIEW.html',
  vtt:'ORIGINAL-42S-CAPTIONS.vtt',
  hub:'MIND-ARCHIVE-FOUR-STREAM-WORDPRESS-REVIEW-ONLY.html',
  matrix:'SOURCE-CLAIM-OFFER-AND-COMMERCIAL-HOLDS.json',
  dossier:'CONVERSION-FIRST-OFFER-FUNNEL-SOURCE-AND-RELEASE-DOSSIER.md'
};
const content=Object.fromEntries(Object.entries(filenames).map(([k,p])=>[k,read(p)]));
const check=(v,msg)=>assert.ok(v,msg);
let passed=0;
function test(name,fn){fn();passed++;console.log('PASS '+name);}
function salesSecure(html){
  check(!/<script\b/i.test(html),'new script prohibited');
  check(!/<form\b/i.test(html),'new form prohibited');
  check(!/<iframe\b/i.test(html),'iframe prohibited');
  check(!/<video\b/i.test(html),'unencoded video cannot be presented as playable');
  check(!/<audio\b/i.test(html),'no embedded seller audio');
  check(!/\bautoplay\b/i.test(html),'autoplay prohibited');
  check(!/href=["']https?:\/\/(?:www\.)?(?:inspire3\.com|zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(html),'merchant href prohibited before approval');
  check(/type="button" disabled aria-disabled="true"/i.test(html),'merchant button must be genuinely disabled');
  const disclosure=html.indexOf('Prospective affiliate disclosure:');
  const button=html.indexOf('Merchant purchase link withheld');
  check(disclosure>=0 && button>disclosure && button-disclosure<600,'adjacent clear FTC disclosure required');
  check(html.includes('Final Vestige may earn a commission'), 'explicit plain commission explanation required');
  check(html.includes('https://finalvestige.com/focus/'),'one free Focus route must remain');
  check(html.includes('noindex,nofollow'),'all prototypes noindex/nofollow');
  check(html.includes('prefers-reduced-motion'),'reduce-motion support');
}
function checkAandB(a,b){
  salesSecure(a);salesSecure(b);
  const start='<p class="eyebrow">';
  check(a.includes(start)&&b.includes(start),'buyer core start');
  assert.equal(a.slice(a.indexOf(start)),b.slice(b.indexOf(start)),'A/B substantive buyer copy must match');
  check(!a.includes('class="storyboard"'),'A must not contain story media');
  check(b.includes('not playable video'),'B truthfully declares storyboard limitations');
  check(b.includes('<svg')&&b.includes('<details')&&b.includes('<summary'),'B requires readable poster and full transcript without JS');
  check(b.includes('00:00')===false,'VTT lives separately');
}
function sourceIntegrity(obj){
  check(obj.status==='UNPUBLISHED_HARD_HOLD','release hold');
  check(obj.affiliate_links_active===false&&obj.merchant_direct_links_in_buyer_html===false,'merchant activation hold');
  check(obj.sources.length>=18,'evidence source coverage');
  check(obj.claims.length>=30,'claim matrix coverage');
  check(obj.authorization_gates.length===18&&obj.authorization_gates.every(g=>g.status==='HARD_HOLD'),'all 18 commercial gates held');
  const ids=new Set(obj.sources.map(x=>x.id));
  for(const c of obj.claims)for(const ref of c.refs)check(ids.has(ref),'unresolved source ref '+ref);
  const categories=new Set(obj.claims.map(c=>c.classification));
  check(categories.has('seller_unsubstantiated_efficacy'),'seller claims tagged');
  check(categories.has('independently_sourced'),'independent science tagged');
  check(categories.has('measurement_error'),'click-vs-sale errors rejected');
  check(obj.creator_topic_crosswalk.length===3,'three actual topics');
  check(obj.creator_topic_crosswalk.every(c=>c.media_asset_id===null && c.approved_url===null),'no invented social asset');
  check(obj.measurement.computed_kpi==='NOT_COMPUTABLE','no fake revenue');
}
test('independent article contains 2006/2021/2024 source comparison',()=>{
  check(content.article.includes('pubmed.ncbi.nlm.nih.gov/17128613'),'2006 source');
  check(content.article.includes('10.1186/s40359-021-00536-3'),'2021 failed broad replication');
  check(content.article.includes('PMC11401123'),'2024 study');
  check(content.article.includes('false alarms'),'signal detection distinction');
  check(content.article.includes('Puységur'),'archive connection');
  check(content.article.split(/\s+/).length>=1800,'substantial original investigation');
});
test('A and B safe, meaningful comparison',()=>checkAandB(content.A,content.B));
test('captions complete and 42 sec',()=>{
  check(content.vtt.startsWith('WEBVTT'),'VTT header');
  check((content.vtt.match(/-->/g)||[]).length===6,'six cues');
  check(content.vtt.includes('00:00:42.000'),'ends at 42 seconds');
});
test('four-stream hub is accessible no-JS and noncommercial',()=>{
  check(content.hub.includes('id="perception"')&&content.hub.includes('id="history"')&&content.hub.includes('id="practice"')&&content.hub.includes('id="tools"'),'four streams');
  check(content.hub.includes('https://finalvestige.com/focus/'),'existing lead funnel');
  check(!/<script\b|<form\b|<iframe\b/i.test(content.hub),'no scripts or signup cloning');
  check(!/href=["']https?:\/\/(?:www\.)?(zen12|inspire3|brainwaveshots|hypnosislive)\./i.test(content.hub),'no seller href');
});
test('all claim sources and partner holds internally consistent',()=>sourceIntegrity(JSON.parse(content.matrix)));
test('revenue proof and ownership plan retained',()=>{
  check(content.dossier.includes('NOT COMPUTABLE')&&content.dossier.includes('settled'),'net revenue not claimed');
  check(content.dossier.includes('P0')&&content.dossier.includes('Praxxis')&&content.dossier.includes('Grok'),'P0 and creator boundaries');
});
const mutants=[
  ['merchant href',s=>s.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/getstarted"')],
  ['active button',s=>s.replace('type="button" disabled aria-disabled="true"','type="button"')],
  ['missing disclosure',s=>s.replace('Prospective affiliate disclosure:','No conflict:')],
  ['new form',s=>s.replace('</main>','<form action="/subscribe"><input></form></main>')],
  ['new script',s=>s.replace('</main>','<script>alert(1)</script></main>')],
  ['new iframe',s=>s.replace('</main>','<iframe src="https://seller.example"></iframe></main>')],
  ['autoplay',s=>s.replace('</main>','<video autoplay></video></main>')],
  ['new vendor link',s=>s.replace('</main>','<a href="https://hypnosislive.com/mental-skills/total-focus">Buy</a></main>')],
  ['no free route',s=>s.replaceAll('https://finalvestige.com/focus/','#') ],
  ['no robots control',s=>s.replace('noindex,nofollow','index,follow')],
  ['no reduced motion',s=>s.replace('prefers-reduced-motion','prefers-big-motion')],
  ['no earning explanation',s=>s.replaceAll('Final Vestige may earn a commission','we support this')],
];
let rejected=0;
for(const [name,fn] of mutants){
  const a=fn(content.A);
  try{salesSecure(a); if(name==='no free route')check(a.includes('https://finalvestige.com/focus/'),'must retain focus');}
  catch(e){rejected++;continue;}
  throw new Error('FAILED TO REJECT '+name);
}
for(const [name,fn] of [
 ['seller gate opened',o=>{o.authorization_gates[0].status='APPROVED'}],
 ['invented creator ID',o=>{o.creator_topic_crosswalk[0].media_asset_id='invented'}],
 ['fake revenue',o=>{o.measurement.computed_kpi='100'}],
 ['missing source',o=>{o.claims[0].refs=['MISSING']}],
 ['false offer activation',o=>{o.affiliate_links_active=true}],
]){
 const mutated=JSON.parse(content.matrix);fn(mutated);
 try{sourceIntegrity(mutated)}catch(e){rejected++;continue}
 throw new Error('FAILED TO REJECT '+name);
}
console.log('RESULT: '+passed+' source suites PASS; '+rejected+'/'+(mutants.length+5)+' synthetic unsafe mutations rejected; NONE of this is live browser, WordPress, video or settlement QA.');
