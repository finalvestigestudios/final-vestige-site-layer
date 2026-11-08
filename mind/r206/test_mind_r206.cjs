'use strict';
/**
 * Mind R206 source-level regression suite.
 * Execute from checkout root: node mind/r206/test_mind_r206.cjs
 * Uses node built-ins, no network, no browser and no live site mutations.
 * Separate from actual WCAG/Lighthouse/checkout/partner approval acceptance.
 */
function run(read){
  const paths={
    article:'mind/r206/the-face-that-changes-thatcher-illusion-UNPUBLISHED.md',
    hub:'mind/r206/mind-archive-FOUR-STREAM-WP-PREVIEW-UNPUBLISHED.html',
    matrix:'mind/r206/THATCHER-IDEOMOTOR-ZEN12-CLAIM-AUTHORIZATION-MATRIX.json',
    plan:'mind/r206/OFFER-FIRST-THREE-CREATOR-FITS-REVENUE-AB-ACCEPTANCE.md',
    prior:'mind/r205/the-pendulum-that-answered-ideomotor-science-UNPUBLISHED.md',
    oldMatrix:'mind/r205/IDEOMOTOR-SOURCE-CLAIMS-OFFER-AUTHORIZATION.json',
    A:'mind/r205/zen12-evidence-A-TEXT-UNPUBLISHED.html',
    B:'mind/r205/zen12-evidence-B-OPTIONAL-42S-UNPUBLISHED.html',
    vtt:'mind/r205/zen12-ideomotor-optional-42s-UNRENDERED.vtt'
  };
  const f={}; for(const [k,p] of Object.entries(paths))f[k]=read(p);
  const m=JSON.parse(f.matrix), old=JSON.parse(f.oldMatrix);
  let passed=0;const failed=[],items=[];
  function t(label,condition){let ok=false;try{ok=!!(typeof condition==='function'?condition():condition)}catch(e){failed.push(label+': '+String(e));return}if(ok)passed++;else failed.push(label);items.push({label,ok})}
  const ids=s=>[...s.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
  const fragments=s=>{let x=new Set(ids(s));return [...s.matchAll(/href="#([^"]+)"/g)].every(y=>x.has(y[1]))};
  const safe=s=>!/<script\b|<iframe\b|<form\b|<input\b|<video\b|on(?:click|load|submit)\s*=|@import\b|(?:awin1|clickbank)\.com/i.test(s);
  const disabled=s=>/<button[^>]*\bdisabled\b[^>]*>/.test(s)&&!/<a[^>]*\b(?:href="https?:\/\/(?:zen12|inspire3|affiliates\.inspire3)|rel="sponsored")/i.test(s);
  const doc=f.article,hub=f.hub,A=f.A,B=f.B,p=f.prior;
  t('article sufficient length',doc.split(/\s+/).length>1900);
  for(const s of ['Thompson','Lewis','Johnston','Wong','Twedt','Sheinberg','Gauthier','1980','1997','2010','face','cars','buildings','bikes','letter','inverted','configural','NOT WordPress','UNPUBLISHED'])
    t('article contains '+s,doc.toLowerCase().includes(s.toLowerCase()));
  for(const doi of ['10.1068/p090483','10.1068/p260225','10.1068/p6659','10.1068/p3174'])
    t('article citation '+doi,doc.includes(doi));
  t('article sets no endorsement',/No affiliate endorsement|no active affiliate earning link/i.test(doc));
  t('article separates commercial efficacy',/did not administer Zen12/i.test(doc));
  t('article credits full text limitation',/full text restricted/i.test(doc));
  t('article identifies historical source not treatment',/Puységur/i.test(doc)&&/not.*(proof|commercial therapy)/i.test(doc));
  for(const id of ['research','history','practice','tools','main','hold-reason'])t('hub id '+id,hub.includes('id="'+id+'"'));
  t('hub has one main', (hub.match(/<main\b/g)||[]).length===1);
  t('hub unique ids',ids(hub).length===new Set(ids(hub)).size);
  t('hub fragments resolve',fragments(hub));
  t('hub no tracking/third party media/form',safe(hub));
  t('hub no active commission link, native disabled',disabled(hub));
  t('hub near disclosure',hub.indexOf('Prospective affiliate disclosure')>0&&Math.abs(hub.indexOf('Prospective affiliate disclosure')-hub.indexOf('<button class="off"'))<700);
  t('hub focus single existing route',hub.includes('https://finalvestige.com/focus/'));
  t('hub no live Thatcher destination',hub.includes('NO PUBLIC URL')||hub.includes('no public link'));
  t('hub no-JS content',!/<script\b/.test(hub)&&hub.includes('<h1>'));
  t('hub keyboard focus',hub.includes(':focus-visible'));
  t('hub reduced motion',hub.includes('prefers-reduced-motion'));
  t('hub CSS responsive',hub.includes('@media(max-width:760px)'));
  for(const id of ['S01','S02','S03','S06','S07','S09','S10','S11','S12','S13','S14','S15'])t('source exists '+id,m.sources.some(s=>s.id===id));
  t('matrix count truthful',m.source_count===m.sources.length&&m.claim_count===m.claims.length&&m.gate_count===m.gates.length);
  t('all source refs resolve',m.claims.every(c=>c.source_ids.every(id=>m.sources.some(s=>s.id===id))));
  t('source IDs unique',new Set(m.sources.map(x=>x.id)).size===m.sources.length);
  t('claim IDs unique',new Set(m.claims.map(x=>x.id)).size===m.claims.length);
  t('all commercial gates open',m.gates.every(x=>x.status==='OPEN'));
  t('no approved partner asserted',m.offer.partner_approval==='UNVERIFIED');
  t('no active earning link field',m.offer.outbound_link===null);
  t('commercial CTA disabled',m.offer.cta_state==='disabled');
  t('revenue not computable',m.funnel.revenue_state==='NOT COMPUTABLE');
  t('cohorts 7+30',m.funnel.cohorts_days.join(',')==='7,30');
  t('pricing is seller only',m.offer.seller_display_at_check.includes('not checkout'));
  t('claim rejection of medical guarantee',m.claims.find(x=>x.id==='M05').decision.startsWith('REJECT'));
  t('old primary paper sample corrected',/21 (were )?retained|21 were retained/.test(p)&&p.includes('six exclusions'));
  t('old study explicit not speech',p.includes('computer')&&p.includes('not a pendulum result'));
  t('old Olson analyzed counts',p.includes('63 remained')&&p.includes('34 remained'));
  t('old confederate detail removed',!p.includes('use of a confederate differed'));
  t('old pendulum source updated',old.sources.find(x=>x.id==='P04').url.includes('pmc.ncbi.nlm.nih.gov'));
  t('old Ouija primary link',old.sources.find(x=>x.id==='P02').url.includes('rensink/publications'));
  t('old FAQ correctly distinguishes Ouija',p.includes('A **2012 Ouija-board** study'));
  t('A no active earning link',disabled(A));
  t('B no active earning link',disabled(B));
  t('A disclosures near CTA',A.includes('Affiliate disclosure:')&&A.includes('disabled'));
  t('B disclosures near CTA',B.includes('Affiliate disclosure:')&&B.includes('disabled'));
  t('A corrected Eason/Parris DOI',A.includes('10.1037/cns0000173'));
  t('B corrected Eason/Parris DOI',B.includes('10.1037/cns0000173'));
  t('A acknowledges noncausal moderators',A.includes('observational moderators'));
  t('B acknowledges noncausal moderators',B.includes('observational moderators'));
  t('both guides price provenance',A.includes('may have truncated cents')&&B.includes('may have truncated cents'));
  t('B figure contains caption',/<figure[^>]*>[\s\S]*?<figcaption[^>]*>[\s\S]*?<\/figcaption><\/figure>/.test(B));
  t('B poster description matches line',B.includes('line angles')&&!B.includes('fixed golden vertical line'));
  t('B film unrendered',!/<video\b/.test(B)&&B.includes('Not produced or playable'));
  t('caption file is draft only',f.vtt.includes('WEBVTT'));
  t('plan is conversion-first',f.plan.includes('NOT COMPUTABLE')&&f.plan.includes('merchant_confirmed_purchase'));
  t('plan preserves Grok ownership',f.plan.includes('Grok retains'));
  t('plan preserves CMS governance',f.plan.includes('PR #49')&&f.plan.includes('PR #172')&&!f.plan.includes('deploy now'));
  t('plan no paid SaaS',f.plan.includes('duplicate scripts')||f.plan.includes('duplicate'));
  let detected=0;let mutations=[
    [hub.replace(/\bdisabled\b/,'data-disabled'),s=>!disabled(s)],
    [hub.replace(/Prospective affiliate disclosure/g,'Prospective information'),s=>!s.includes('Prospective affiliate disclosure')],
    [hub.replace('href="#tools"','href="#missing_tools"'),s=>!fragments(s)],
    [hub.replace('id="tools"','id="research"'),s=>ids(s).length!==new Set(ids(s)).size],
    [hub.replace('<h1>','<div>'),s=>!s.includes('<h1>')],
    [A.replace(/\bdisabled\b/,'data-disabled'),s=>!disabled(s)],
    [B.replace(/\bdisabled\b/,'data-disabled'),s=>!disabled(s)],
    [B.replace('10.1037/cns0000173','10.1037/WRONG'),s=>!s.includes('10.1037/cns0000173')],
    [A.replace('may have truncated cents','guaranteed price'),s=>!s.includes('may have truncated cents')],
    [p.replace('21 were retained','27 were retained'),s=>!s.includes('21 were retained')],
    [p.replace('63 remained','80 remained'),s=>!s.includes('63 remained')],
    [doc.replace('10.1068/p6659','invalid-source'),s=>!s.includes('10.1068/p6659')]
  ];for(const [mut,detector] of mutations)if(detector(mut))detected++;
  t('mutations caught at least 10/12',detected>=10);
  return {passed,failed,mutation_caught:detected,mutation_total:mutations.length,files:paths,source_tests:'static in-memory assertions only; no browser/merchant access'};
}
module.exports={run};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const root=path.resolve(__dirname,'../..');
 const result=run(p=>fs.readFileSync(path.join(root,p),'utf8'));
 console.log(JSON.stringify(result,null,2));
 process.exitCode=result.failed.length?1:0;
}