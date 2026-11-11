/* R291 cumulative source QA — not a browser, WCAG audit, settlement or production clearance.
 * Native: node mind/r291/verify_r291.cjs at repository root.
 * Also exports audit(files) and mutations(files) for a read-only isolated JS runner.
 * FNV checksums are regression signatures, NOT cryptographic authenticity.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const P = {
  article:'mind/r291/THE-FACE-THAT-LOOKED-NORMAL-UPSIDE-DOWN-UNPUBLISHED.md',
  hub:'mind/r291/MIND-THATCHER-ARCHIVE-UNPUBLISHED.html',
  matrix:'mind/r291/THATCHER-PRIMARY-SOURCE-COMMERCIAL-CLAIM-MATRIX.json',
  renderer:'mind/r291/render_original_thatcher_short.py',
  video:'mind/r291/ORIGINAL-42S-OPTIONAL-VIDEO-INSERT-UNPUBLISHED.html',
  plan:'mind/r291/ONE-OFFER-ORIGINAL-VIDEO-CONVERSION-AND-RELEASE-ACCEPTANCE.md',
  a:'mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html',
  b:'mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html'
};
const expected = {"source":{"simons1999":"aebbc5d5","simons2010":"b6f3b55e","drew2013":"48a80052","wallisch2023":"bfb6d47a","fvChange":"85c8c266","fvPuysegur":"4b096ad0","fvFocus":"504560e6","fvLibrary":"668f8d7a","zen12order":"f3f4e117","zen12welcome":"6afd3da9","inspire3":"5944a1cb","inspireAffiliate":"165ab44c","hypnosisfocus":"f15cf469","brainwavefocus":"eb0d9baf","ftcEndorse":"2ddc6e27","ftcHealth":"fd0797fd","fvDisclosure":"31bb1d0c","fvEditorial":"b66d4387","thompson1980":"0f75103e","bartlett1993":"5f10369b","rakover1999":"4e0a7a71","psalta2014":"5d8beed7","psaltaNeural":"01e88db1","fvJournalLive":"0c21b01e","brainwaveFaqExact":"9f3f02f4","hypnosisFaqExact":"264f43f7"},"claim":{"G001":"45e625da","G002":"dcf867b5","G003":"4843b245","G004":"645db227","G005":"77d99339","G006":"839ebe79","G007":"7b9f25b3","G008":"396f5191","G009":"9e7f89ed","G010":"a25364d4","G011":"bede9a37","G012":"ae66fe84","G013":"e1eebdb4","G014":"d63a0883","G015":"dc5b7f4c","G016":"d55e93d1","G017":"236952f0","G018":"44172c53","G019":"decc4295","G020":"1f0c1357","G021":"3bf51d0f","G022":"980116fe","G023":"6fdba197","G024":"a5fb26d4","G025":"0e5ef7e0","G026":"82ccfe18","G027":"02797ae5","G028":"d3a2aaf9","T001":"e2548e6b","T002":"d2e92022","T003":"b49fbfbf","T004":"b7e0443e","T005":"b3791aa3","T006":"867262ab","T007":"11f50b96","T008":"6a8867b7","T009":"db4795ba","T010":"50def045","T011":"fae00039","T012":"53a46281","T013":"f400d26c","T014":"7a06ce09","T015":"e691f95a","T016":"438f65a1","T017":"aff93e23","T018":"cab78002"},"gate":["actual_refund_fulfillment_not_assumed","allowed_email_promotion","allowed_promotional_channels","approved_creative_rights","authorized_publisher_identity","browser_accessibility_mobile_QA","claim_substantiation_review","exact_checkout_terms","founder_commercial_approval","founder_production_release_approval","issued_earning_url","named_publisher_acceptance","original_video_rights_and_captions","privacy_measurement_approval","proximate_disclosure_QA","refund_policy_confirmed","verified_destination_route","verified_offer_price_if_used"],"legacy":{"a":"ed05f7c4","b":"7a5e3be1"}};
function hash(s) {let h=2166136261;for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619)>>>0;return h.toString(16).padStart(8,'0')}
function requireEq(ok,msg,e){if(!ok)e.push(msg)}
function audit(files) {
 const e=[];let m;
 for(const [k,p] of Object.entries(P))requireEq(typeof files[p]==='string'&&files[p].length>0,'missing source '+p,e);
 if(e.length)return e;
 try{m=JSON.parse(files[P.matrix])}catch(_){return ['invalid JSON']}
 const ids=x=>new Set(x.map(y=>y.id));
 requireEq(m.publication!=='LIVE'&&m.commercial!=='LIVE','falsified live status',e);
 requireEq(Array.isArray(m.sources)&&m.sources.length===26,'source roster changed',e);
 requireEq(Array.isArray(m.claims)&&m.claims.length===46,'claim roster changed',e);
 requireEq(ids(m.sources).size===26&&ids(m.claims).size===46,'duplicate source/claim ID',e);
 requireEq(JSON.stringify(Object.keys(m.release_gates).sort())===JSON.stringify(expected.gate),'commercial gate identity altered',e);
 for(const [key,v] of Object.entries(m.release_gates||{}))requireEq(v.status==='HARD_HOLD','gate '+key+' changed',e);
 for(const s of m.sources||[])requireEq(expected.source[s.id]===hash(JSON.stringify(s)),'source ID URL scope changed '+s.id,e);
 for(const c of m.claims||[]){requireEq(ids(m.sources).has(c.source_id),'unresolved claim '+c.id,e);requireEq(expected.claim[c.id]===hash(JSON.stringify(c)),'claim/source/decision changed '+c.id,e)}
 for(const [id,fp] of Object.entries(expected.source))requireEq(m.sources.some(x=>x.id===id)&&fp.length===8,'source omitted '+id,e);
 for(const [id,fp] of Object.entries(expected.claim))requireEq(m.claims.some(x=>x.id===id)&&fp.length===8,'claim omitted '+id,e);
 requireEq(m.creator_routes.length===3&&m.creator_routes.every(x=>x.asset_id===null&&x.go_live===false&&x.video_url===null),'invented creator asset/launch',e);
 requireEq(m.canonical_presell.length===2&&m.canonical_presell.includes(P.a)&&m.canonical_presell.includes(P.b),'canonical A/B changed',e);
 requireEq(m.pilot_design.commercial_clicks_must_be_disabled===true&&m.pilot_design.no_traffic_assignment===true,'pilot falsely activated',e);
 requireEq(m.pilot_design.video_status==='ORIGINAL_STATIC_42_SECOND_STORYBOARD_NOT_PLAYABLE','legacy B playback misrepresented',e);
 requireEq(m.commercial_revenue_status!=='VERIFIED_PAID_REVENUE','paid sale fabricated',e);
 requireEq(hash(files[P.a])===expected.legacy.a,'inherited full A buyer guide modified',e);
 requireEq(hash(files[P.b])===expected.legacy.b,'inherited full B buyer guide modified',e);
 for(const key of ['hub','video','a','b']){
  const h=files[P[key]];
  requireEq(/<html\b[^>]*lang=["']en["']/i.test(h),'missing HTML language '+key,e);
  requireEq(/<meta\b[^>]*name=["']viewport["']/i.test(h),'missing mobile viewport '+key,e);
  requireEq(!/<(?:script|form|iframe|object|embed)\b/i.test(h),'prohibited active embed/form '+key,e);
  requireEq(!/<(?:img|source|track)\b[^>]*\b(?:src|srcset)=["'](?:https?:)?\/\//i.test(h),'remote media pixel '+key,e);
  requireEq(!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(h),'active merchant earning link '+key,e);
  requireEq(!/on(?:click|load|error|mouseover)\s*=/i.test(h),'inline event handler '+key,e);
  const allButtons=[...h.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]);
  requireEq(allButtons.length>=1&&allButtons.every(x=>/\sdisabled(?:[\s>=])/i.test(x)),'enabled button '+key,e);
  requireEq(/commission/i.test(h)&&/no additional cost/i.test(h),'missing monetary disclosure '+key,e);
  requireEq(/https:\/\/finalvestige\.com\/focus\//i.test(h),'missing existing Focus route '+key,e);
  requireEq(/(?:unpublished|not published)/i.test(h),'false publication scope '+key,e);
 }
 const hub=files[P.hub],vid=files[P.video],article=files[P.article],renderer=files[P.renderer],plan=files[P.plan];
 requireEq(/<p class=["']disclosure["'][^>]*>/.test(vid)&&vid.indexOf('Potential affiliate disclosure')<vid.indexOf('<button'),'video disclosure not adjacent',e);
 requireEq(hub.indexOf('Potential affiliate relationship')<hub.indexOf('<button'),'hub disclosure position missing',e);
 requireEq(!/\bautoplay\b/i.test(vid.match(/<video\b[^>]*>/i)?.[0]||''),'autoplay enabled',e);
 requireEq(/<video\b(?=[^>]*\bcontrols\b)(?=[^>]*preload=["']none["'])[^>]*>/i.test(vid),'missing optional native controls + preload none',e);
 requireEq(/<track\b[^>]*kind=["']captions["']/i.test(vid),'missing caption track',e);
 requireEq(/<details>[\s\S]*?<summary>[\s\S]*?0–6s/i.test(vid),'missing readable transcript',e);
 requireEq(!/\bzen12\.com\/getstarted\b/i.test(vid),'unapproved raw merchant destination in playback UI',e);
 requireEq(/subprocess\.run/.test(renderer)&&/ffmpeg/.test(renderer)&&/captions\.vtt/.test(renderer)&&/poster\.png/.test(renderer),'render recipe missing',e);
 requireEq(/-t","42"/.test(renderer),'render length not 42s',e);
 requireEq(/Thompson/.test(article)&&/Bartlett/.test(article)&&/Psalta/.test(article)&&/Puységur/.test(article),'missing research sources',e);
 requireEq(/not.*product-specific|not.*meditation|cannot verify|cannot substantiate|cannot establish/i.test(article),'source limitation missing',e);
 requireEq(/NOT COMPUTABLE/i.test(plan)&&/HARD HOLD/i.test(plan),'realized revenue or release hold missing',e);
 requireEq(/verified.*commission|commission.*cleared/i.test(plan)&&/refund/i.test(plan)&&/qualified_human_sessions/i.test(plan),'net revenue validation absent',e);
 return e;
}
function mutants(files){
 const cases=[];
 const add=(title,key,edit)=>{const f={...files};const before=f[P[key]];f[P[key]]=edit(before);if(f[P[key]]===before)throw Error('NO OP mutant '+title);cases.push([title,f])};
 add('enable hub buy','hub',s=>s.replace('type="button" disabled','type="button"'));
 add('enable video buy','video',s=>s.replace('type="button" disabled','type="button"'));
 add('enable inherited A','a',s=>s.replace(/\sdisabled(?=[\s>=])/i,''));
 add('enable inherited B','b',s=>s.replace(/\sdisabled(?=[\s>=])/i,''));
 add('remove hub disclosure','hub',s=>s.replace('Potential affiliate relationship:','No information:'));
 add('remove video disclosure','video',s=>s.replace('Potential affiliate disclosure:','No information:'));
 add('add popup form','hub',s=>s.replace('</main>','<form><input type="email"></form></main>'));
 add('add external script','hub',s=>s.replace('</body>','<script src="https://example.com/p.js"></script></body>'));
 add('add pixel','video',s=>s.replace('</body>','<img src="https://tracker.example/pixel"></body>'));
 add('add inline handler','video',s=>s.replace('type="button"','onclick="alert(1)" type="button"'));
 add('add merchant href','hub',s=>s.replace('</footer>','<a href="https://zen12.com/getstarted">Buy</a></footer>'));
 add('add external iframe','video',s=>s.replace('</main>','<iframe src="https://example.com"></iframe></main>'));
 add('autoplay','video',s=>s.replace('<video controls','<video autoplay controls'));
 add('preload auto','video',s=>s.replace('preload="none"','preload="auto"'));
 add('strip captions','video',s=>s.replace('kind="captions"','kind="subtitles"'));
 add('no transcript','video',s=>s.replace('0–6s:','Intro:'));
 add('invalid artist source','article',s=>s.replace('Peter Thompson','Peter Thomson'));
 add('remove evidentiary limit','article',s=>s.replace('They offer reasons to ask sharper questions of evidence, not a license to dismiss witnesses.','They prove every witness is always wrong.'));
 add('remove rev calculation','plan',s=>s.replace('NOT COMPUTABLE','NOT TRACKED'));
 add('change renderer length','renderer',s=>s.replace('"-t","42"','"-t","60"'));
 add('remove renderer captions','renderer',s=>s.replace('captions.vtt','fake.ext'));
 add('alter A copy','a',s=>s.replace('Money Back','Money Bonus'));
 add('alter B copy','b',s=>s.replace('Money Back','Money Bonus'));
 for (const [name,change] of [
  ['make affiliate approved',j=>{j.release_gates.issued_earning_url.status='APPROVED'}],
  ['wrong valid claim source',j=>{j.claims[0].source_id=j.sources[2].id}],
  ['alter source URL',j=>{j.sources[0].url='https://example.com/study'}],
  ['alter source scope',j=>{j.sources[0].scope='Proves instant focus'}],
  ['alter claim meaning',j=>{j.claims[0].statement='Audio guaranteed'}],
  ['remove gate',j=>{delete j.release_gates.founder_production_release_approval}],
  ['fake published Grok ID',j=>{j.creator_routes[0].asset_id='injected'}],
  ['fake live creator',j=>{j.creator_routes[0].go_live=true}],
  ['fake video hosted',j=>{j.pilot_design.video_status='LIVE_PLAYABLE'}],
  ['fake approved campaign',j=>{j.pilot_design.no_traffic_assignment=false}],
  ['rewrite canonical A ref',j=>{j.canonical_presell[0]='mind/secret.html'}],
  ['remove claim',j=>{j.claims.pop()}],
  ['fake paid outcome',j=>{j.commercial_revenue_status='VERIFIED_PAID_REVENUE'}],
  ['approved attribution',j=>{j.pilot_design.commercial_clicks_must_be_disabled=false}]
 ])add(name,'matrix',s=>{const j=JSON.parse(s);change(j);return JSON.stringify(j)});
 return cases;
}
const read=()=>Object.fromEntries(Object.values(P).map(p=>[p,fs.readFileSync(path.join(process.cwd(),p),'utf8')]));
if (require.main===module) {
 const files=read();
 const errors=audit(files);
 if (errors.length)throw Error('BASELINE FAIL:\n'+errors.join('\n'));
 const cases=mutants(files);
 const passed=cases.filter(([_,f])=>audit(f).length).length;
 if(passed!==cases.length)throw Error('Mutation test escape '+(cases.length-passed)+'/'+cases.length);
 console.log('R291 PASS | baseline valid; '+passed+'/'+cases.length+' invalid modifications rejected; A/B inherited bytes loaded; 18 gates held.');
}
module.exports={audit,mutants,P,expected,hash};
