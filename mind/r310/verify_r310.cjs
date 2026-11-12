#!/usr/bin/env node
'use strict';
/* Native Node source-only regression checks; no network, CMS, analytics or affiliate writes.
 * Run: node mind/r310/verify_r310.cjs
 */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../..');
const paths={a:'mind/r308/ZEN12-A-TEXT-REVIEW-ONLY.html',b:'mind/r308/ZEN12-B-OPTIONAL-STORYBOARD-REVIEW-ONLY.html',old:'mind/r308/THE-NAME-THAT-CROSSED-THE-ROOM-UNPUBLISHED.md',oldLedger:'mind/r308/EXACT-SELLER-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json',article:'mind/r310/THE-GLASS-THAT-WAS-NEVER-ON-THE-ROAD-UNPUBLISHED.md',register:'mind/r310/SOURCE-CLAIM-OFFER-AND-ATTRIBUTION-GATES.json',accept:'mind/r310/ONE-OFFER-CONVERSION-CLAIM-AND-RELEASE-ACCEPTANCE.md'};
const load=()=>Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,fs.readFileSync(path.join(ROOT,p),'utf8')]));
function failures(f){
  const e=[],need=(condition,message)=>{if(!condition)e.push(message);};
  let d,o;try{d=JSON.parse(f.register);}catch(_){e.push('register JSON');}
  try{o=JSON.parse(f.oldLedger);}catch(_){e.push('older register JSON');}
  const a=f.a||'',b=f.b||'',old=f.old||'',article=f.article||'',accept=f.accept||'';
  for(const [name,html] of [['A',a],['B',b]]){
    need(html.includes('nine of the 26 participants who actually heard their own names'),name+' denominator');
    need(!html.includes('34.6% of a sample of 34'),name+' old denominator');
    need(/<button\b(?=[^>]*\bdisabled(?:\s|=|>))[^>]*>Merchant offer unavailable pending verification<\/button>/.test(html),name+' native disabled button');
    const offer=html.match(/<section class="offer"[\s\S]*?<\/section>/)?.[0]||'';
    need(offer.indexOf('Affiliate disclosure:')>=0&&offer.indexOf('Affiliate disclosure:')<offer.indexOf('<button'),name+' adjacent FTC disclosure');
    need(!/<(?:script|form|iframe)\b/i.test(html),name+' scripts/forms');
    need(!/href=["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|affiliates\.inspire3)\.com/i.test(html),name+' unapproved affiliate seller link');
    need(html.includes('noindex,nofollow'),name+' noindex');
    need((html.match(/https:\/\/finalvestige\.com\/focus\//g)||[]).length>=2,name+' single fieldbook destination');
  }
  need(b.includes('Optional 42-second film treatment — concept, not playable media'), 'film treatment absent');
  need(b.includes('No streaming asset, controls, autoplay or media download has been published'), 'fake playable film');
  const norm=x=>x.replace(/<details class="panel" id="optional-film">[\s\S]*?<\/details>/,'').replace('Review only B','Review only A');
  need(norm(a)===norm(b),'A/B copy mismatch');
  need(old.includes('nine of 26 participants exposed to their own name'),'old research corrected numerator');
  need(old.includes('eight no-name controls'),'old research corrected controls');
  need(!old.includes('34.6% of a sample of 34'),'old research old denominator');
  const w=o?.sources?.find(s=>s.id==='W1995');
  need(Boolean(w&&w.scope.includes('nine of 26')&&w.scope.includes('eight no-name controls')),'old JSON corrected denominator');
  need(w?.depth==='author_hosted_full_paper_printed_pages_256_257_and_pubmed_abstract','old source reading depth');
  need(article.includes('16 of 50')&&article.includes('seven of 50')&&article.includes('six of 50'),'Loftus-Palmer counts');
  need(article.includes('no broken glass in the film')&&article.includes('150 students')&&article.includes('45 students'),'two experiments/no-glass boundary');
  need(article.includes('not a direct readout of the contents of memory'),'anti-overclaim boundary');
  need(!/href=["']https?:\/\/(?:www\.)?zen12\.com/i.test(article),'commercial link in investigation');
  if(d){
    const ids=new Set((d.sources||[]).map(x=>x.id));
    need(d.sources?.length>=16&&d.claims?.length>=29,'source/claim count');
    need(d.claims?.every(c=>Array.isArray(c.source_ids)&&c.source_ids.every(id=>ids.has(id))),'invalid source crossref');
    need(d.authorization_gates?.length===18&&d.authorization_gates.every(g=>g.status==='HARD_HOLD'&&g.proof===null),'unapproved commercial activation');
    need(d.creator_paths?.length===3&&d.creator_paths.every(p=>p.asset_id===null&&p.published_media_verified===false),'fictional creator ID');
    need(d.offer_priority?.every(o=>o.cta==='disabled'&&o.is_sellable_by_fv==='NOT_VERIFIED'),'purchase enabled');
    need(d.measurement?.value==='NOT_COMPUTABLE'&&d.measurement?.numerator_status==='NOT_VERIFIED','fake paid earnings');
  }
  need(accept.includes('HARD HOLD')&&accept.includes('NOT COMPUTABLE'),'release/financial evidence hold');
  return e;
}
const baseline=load();
assert.deepEqual(failures(baseline),[],'baseline source invalid');
const mutants=[
 ['A denominator',x=>x.a=x.a.replace('nine of the 26 participants','34.6% of a sample of 34 participants')],
 ['B denominator',x=>x.b=x.b.replace('nine of the 26 participants','34.6% of a sample of 34 participants')],
 ['old denominator',x=>x.old=x.old.replace('nine of 26 participants','nine of 34 participants')],
 ['old control',x=>x.old=x.old.replace('eight no-name controls','eight fictional controls')],
 ['old ledger',x=>{const d=JSON.parse(x.oldLedger);d.sources.find(s=>s.id==='W1995').scope='34 total with 34.6%';x.oldLedger=JSON.stringify(d);}],
 ['old source depth',x=>{const d=JSON.parse(x.oldLedger);d.sources.find(s=>s.id==='W1995').depth='abstract';x.oldLedger=JSON.stringify(d);}],
 ['A enable purchase',x=>x.a=x.a.replace('type="button" disabled','type="button"')],
 ['B enable purchase',x=>x.b=x.b.replace('type="button" disabled','type="button"')],
 ['A FTC missing',x=>x.a=x.a.replace('Affiliate disclosure:','Commercial note:')],
 ['B FTC missing',x=>x.b=x.b.replace('Affiliate disclosure:','Commercial note:')],
 ['A merchant link',x=>x.a+='<a href="https://zen12.com/getstarted">BUY</a>'],
 ['B merchant link',x=>x.b+='<a href="https://hypnosislive.com/mental-skills/total-focus">BUY</a>'],
 ['A script',x=>x.a+='<script>track()</script>'],
 ['B signup form',x=>x.b+='<form></form>'],
 ['A noindex',x=>x.a=x.a.replace('noindex,nofollow','index,follow')],
 ['B text drift',x=>x.b=x.b.replace('buying a sequence of files','buying a miracle sequence of files')],
 ['B fake film',x=>x.b=x.b.replace('No streaming asset, controls, autoplay or media download has been published','Playable film live')],
 ['article first count',x=>x.article=x.article.replace('16 of 50','46 of 50')],
 ['article second count',x=>x.article=x.article.replace('seven of 50','seven of 500')],
 ['article no glass',x=>x.article=x.article.replace('no broken glass in the film','glass in the film')],
 ['article cohort',x=>x.article=x.article.replace('150 students','1500 students')],
 ['article memory',x=>x.article=x.article.replace('not a direct readout of the contents of memory','a direct readout of memory')],
 ['article merchant',x=>x.article+='<a href="https://zen12.com/getstarted">BUY</a>'],
 ['bad JSON',x=>x.register='{broken'],
 ['missing source',x=>{let d=JSON.parse(x.register);d.claims[0].source_ids=['UNKNOWN_SOURCE'];x.register=JSON.stringify(d);}],
 ['affiliate gate flip',x=>{let d=JSON.parse(x.register);d.authorization_gates[0].status='APPROVED';x.register=JSON.stringify(d);}],
 ['fabricated asset',x=>{let d=JSON.parse(x.register);d.creator_paths[0].asset_id='FAKE_000';x.register=JSON.stringify(d);}],
 ['purchase activated',x=>{let d=JSON.parse(x.register);d.offer_priority[0].cta='live';x.register=JSON.stringify(d);}],
 ['invented revenue',x=>{let d=JSON.parse(x.register);d.measurement.value='999';x.register=JSON.stringify(d);}],
 ['release flag',x=>x.accept=x.accept.replaceAll('HARD HOLD','APPROVED')]
];
let rejected=0;for(const [name,modify] of mutants){const copy={...baseline};modify(copy);assert.ok(failures(copy).length>0,'mutation not rejected: '+name);rejected++;}
console.log(JSON.stringify({status:'PASS',baseline:'PASS',rejected_mutants:rejected,scope:Object.values(paths),runtime:process.version},null,2));
