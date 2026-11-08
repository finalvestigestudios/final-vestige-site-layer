/* Mind R224 source-only regression. Run from repository root: node mind/r224/test_mind_r224.cjs
   No network, no third-party libraries, no merchant/WordPress interaction.
   DOES NOT prove browser WCAG, production UX, playable media, seller checkout or net sales.
*/
'use strict';
const fs=require('node:fs'),path=require('node:path');
const here=__dirname, parent=path.resolve(here,'../r223');
const read=(name,base=here)=>fs.readFileSync(path.join(base,name),'utf8');
const source={
 art:read('the-half-second-gap-meditation-attention-EVIDENCE-REVIEW-UNPUBLISHED.md'),
 hub:read('mind-archive-ATTENTION-WP-SOURCE-PREVIEW-UNPUBLISHED.html'),
 matrix:JSON.parse(read('ATTENTION-MEDITATION-ZEN12-SOURCES-CLAIMS-AUTHORIZATION.json')),
 plan:read('OFFER-FIRST-CREATOR-ATTRIBUTION-AB-PAID-REVENUE-RELEASE.md'),
 oldArt:read('the-pendulum-that-answered-IDEOMOTOR-UNPUBLISHED.md',parent),
 oldMatrix:JSON.parse(read('SOURCE-CLAIM-COMMERCE-GATES.json',parent)),
 a:read('zen12-R223-A-TEXT-UNPUBLISHED.html',parent),
 b:read('zen12-R223-B-OPTIONAL-42S-UNRENDERED.html',parent),
 vtt:read('zen12-42s-SCRIPT-LOCK.vtt',parent)
};
const requiredGateIds=['account_acceptance','permission_social','permission_email','issued_earning_url','affiliate_tracking_terms','merchant_checkout_final','merchant_refund_conditions','merchant_creative_rights','claim_substantiation','affiliate_disclosure_rendered','video_render_and_captions','browser_a11y_performance','site_qa_and_founder_release','published_guide','independent_paid_conversion','qualified_human_denominator'];
const lockedStatuses={
 C01:'merchant_description_only',C02:'merchant_description_only',C03:'merchant_description_only',
 C04:'merchant_description_only',C05:'observed_public_not_checkout',
 C06:'unsupported_product_specific_benefit_DO_NOT_ADOPT',C07:'unsupported_product_specific_health_claim_DO_NOT_ADOPT',
 C08:'unsupported_product_specific_performance_claim_DO_NOT_ADOPT',C09:'merchant_catalog_statement',
 C10:'regulatory_guidance',C11:'regulatory_guidance',C20:'verified_live_summary',
 C21:'UNVERIFIED_HARD_HOLD',C22:'UNVERIFIED_HARD_HOLD',C23:'UNVERIFIED_HARD_HOLD',
 C24:'FALSE_DO_NOT_COUNT',C25:'NOT_COMPUTABLE',
 C26:'independent_research_context_specific',C27:'independent_research_context_specific',
 C28:'independent_research_context_specific',C29:'independent_review',
 C30:'replicated_core_with_variation',C31:'meta_analysis_general_not_product',
 C32:'meta_analysis_general_not_product',C33:'unsupported_product_specific_benefit_DO_NOT_ADOPT',
 C34:'independent_research_abstract',C35:'reported_public_id_independent_handoff',C36:'UNVERIFIED_HARD_HOLD',C37:'public_affiliate_portal_not_publisher_permission'
};
function check(obj){
 if(/relative chance statement|37\\.9-percentage-point gap/.test(obj.oldArt))return ['oldArt:unproven-model-interpretation'];
 const c28=obj.matrix.claims.find(c=>c.id==='C28');
 if(!c28||!/pooled practitioners and novices/.test(c28.statement||''))return ['matrix:C28-EEG-pooled-correlation'];
 const e=[], m=obj.matrix;
 for(const [label,html] of [['hub',obj.hub],['A',obj.a],['B',obj.b]]){
  if(/<\s*(?:script|form|input|iframe|video|audio|source)\b/i.test(html))e.push(label+':no-unapproved-embeds-or-forms');
  if(/\son[a-z]+\s*=/i.test(html))e.push(label+':no-inline-events');
  if(/\b(?:href|formaction|data-url)\s*=\s*['"]?\s*(?:https?:\/\/)?(?:[^\s'">]*\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|awin1\.com|clickbank\.com)/i.test(html))e.push(label+':merchant-link');
  if(/(?:data-)?(?:affiliate|tracking)-id\s*=|\b(?:gtag|fbq)\s*\(|localStorage|sessionStorage/i.test(html))e.push(label+':tracking');
  if(!/<meta\s+name="robots"\s+content="noindex,nofollow"/.test(html))e.push(label+':robots');
  if(!/:focus-visible/.test(html))e.push(label+':keyboard-style');
  if(!/prefers-reduced-motion:reduce/.test(html))e.push(label+':reduce-motion');
  const buttons=[...html.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]);
  if(buttons.length!==1)e.push(label+':button-count');
  buttons.forEach(x=>{if(!/\sdisabled(?:\s|>|=)/i.test(x)||!/aria-disabled="true"/i.test(x))e.push(label+':native-disabled');
    if(/\s(?:on[a-z]+|href|formaction|data-url)\s*=/i.test(x))e.push(label+':activated-button');
  });
  const disclosure=html.toLowerCase().indexOf('affiliate disclosure:');
  if(disclosure<0 || !buttons.some(x=>html.slice(disclosure,disclosure+800).includes(x)))e.push(label+':adjacent-disclosure');
 }
 for(const key of ['matrix','oldMatrix']){
  const d=obj[key], gates=d.gates||[],ids=gates.map(x=>x.id);
  if(d.release!=='UNPUBLISHED_HARD_HOLD')e.push(key+':release');
  if(gates.length!==16||new Set(ids).size!==16)e.push(key+':gate-duplicates-or-count');
  for(const id of requiredGateIds)if(!gates.some(g=>g.id===id&&g.status==='HARD_HOLD'))e.push(key+':gate-'+id);
  const sources=d.sources||[],claims=d.claims||[];
  const sourceIds=sources.map(s=>s.id),claimIds=claims.map(c=>c.id);
  if(new Set(sourceIds).size!==sourceIds.length||sources.some(x=>!/^https:\/\//.test(x.url)))e.push(key+':source-validation');
  if(new Set(claimIds).size!==claimIds.length||claims.length!==(key==='matrix'?37:25))e.push(key+':claims-complete-and-unique');
  for(const [id,status] of Object.entries(lockedStatuses)){ if(key==='matrix' || Number(id.slice(1))<=25){ const row=claims.find(c=>c.id===id); if(!row || row.status!==status)e.push(key+':mandatory-claim-'+id); } }
  for(const c of claims){
    if(!Array.isArray(c.source_ids)||!c.source_ids.length||c.source_ids.some(id=>!sourceIds.includes(id)))e.push(key+':unlinked-claim-'+c.id);
    if(!c.status||!c.limit||!c.statement)e.push(key+':incomplete-claim-'+c.id);
    if(lockedStatuses[c.id]&&c.status!==lockedStatuses[c.id])e.push(key+':protected-status-'+c.id);
  }
  if(d.claims.find(c=>c.id==='C06')?.statement!=='Twelve minutes equals one hour advanced meditation')e.push(key+':claim-C06-identity');
  if(!/DO_NOT_ADOPT/.test(d.claims.find(c=>c.id==='C33')?.status||'') && key==='matrix')e.push(key+':C33-benefit');
 }
 if(!/lower chance|lower chance of predictive eye movements/i.test(obj.oldArt)||/percentage points/.test(obj.oldArt))e.push('oldArt:relative-vs-points');
 if(!/Eye tracking did not directly measure fingertip force/.test(obj.oldArt))e.push('oldArt:no-force-measurement');
 if(!/153 source rows and 16 dossiers/.test(obj.oldMatrix.claims.find(c=>c.id==='C20')?.statement||''))e.push('oldMatrix:source-provenance');
 if(!/2,855-word|2855-word|2,855 word/.test(obj.plan))e.push('plan:research-size');
 if(!/ZERO OR NEGATIVE/.test(obj.plan)||!/NOT COMPUTABLE/.test(obj.plan))e.push('plan:zero-negative-net');
 if(!/SV9m07PFTYk/.test(obj.plan)||!/not three authenticated/i.test(obj.plan))e.push('plan:creator-reconciliation');
 if(!/UNPUBLISHED_RESEARCH_DRAFT/.test(obj.art)||!/PLoS Biology|PLOS Biology/.test(obj.art))e.push('art:research-sources');
 if(obj.art.split(/\s+/).length<2300)e.push('art:substance');
 if(!/does not|do not|not evidence/i.test(obj.art))e.push('art:caution');
 if(!/UNRENDERED|video not rendered/.test(obj.b)||/<video\b/i.test(obj.b))e.push('B:video-unready');
 const film=obj.b.match(/<details class="film"[\s\S]*?<\/details>/);
 if(!film)e.push('B:optional-film');
 else{
  const normalize=x=>x.replace(/OPTIONAL 42S B|TEXT A/g,'VARIANT').replace(/<details class="film"[\s\S]*?<\/details>/,'');
  if(normalize(obj.b)!==normalize(obj.a))e.push('AB:core-copy-differs');
  const cues=[...obj.vtt.matchAll(/\d\d:\d\d:\d\d\.\d{3} --> \d\d:\d\d:\d\d\.\d{3}\s*\n([^\n]+)/g)].map(x=>x[1].trim());
  const narrated=[...film[0].matchAll(/<li><strong>[^<]+<\/strong>\s*([^<]+)<\/li>/g)].map(x=>x[1].trim());
  if(cues.length!==5||narrated.length!==5||cues.some((x,i)=>x!==narrated[i])||!/00:00:35.000 --> 00:00:42.000/.test(obj.vtt))e.push('B:VTT-versus-transcript');
 }
 return [...new Set(e)];
}
const clone=x=>JSON.parse(JSON.stringify(x));
const cases=[
 ['invent C37 publisher approval',d=>{d.matrix.claims.find(x=>x.id==='C37').status='VERIFIED_APPROVAL';}],
 ['rename C37 approval row',d=>{d.matrix.claims.find(x=>x.id==='C37').id='C37_approved';}],
 ['replace corrected C28 with intensive-only correlation',d=>{d.matrix.claims.find(x=>x.id==='C28').statement='Slagter intensive group P3b correlation alone';}],
 ['restore unsupported logistic effect interpretation',d=>{d.oldArt+=' This is a relative chance statement';}],
 ['approve seller claim C06',d=>{d.matrix.claims.find(x=>x.id==='C06').status='independent_research';}],
 ['fabricate clinical claim C07',d=>{d.matrix.claims.find(x=>x.id==='C07').status='clinically_proven';}],
 ['fabricate brain effect C08',d=>{d.matrix.claims.find(x=>x.id==='C08').status='scientifically_verified';}],
 ['declare C21 affiliate approved',d=>{d.matrix.claims.find(x=>x.id==='C21').status='VERIFIED';}],
 ['declare C22 tracking link approved',d=>{d.matrix.claims.find(x=>x.id==='C22').status='APPROVED';}],
 ['declare C23 Payhip right',d=>{d.matrix.claims.find(x=>x.id==='C23').status='VERIFIED';}],
 ['convert source C33 to product proof',d=>{d.matrix.claims.find(x=>x.id==='C33').status='proven';}],
 ['fabricate owned SKU C36',d=>{d.matrix.claims.find(x=>x.id==='C36').status='VERIFIED';}],
 ['delete claim C07',d=>{d.matrix.claims=d.matrix.claims.filter(x=>x.id!=='C07');}],
 ['duplicate source S17',d=>{d.matrix.sources.push({...d.matrix.sources[16]});}],
 ['claim missing source',d=>{d.matrix.claims[0].source_ids=['S999'];}],
 ['missing last gate',d=>{d.matrix.gates.pop();}],
 ['duplicate last gate',d=>{d.matrix.gates[0].id=d.matrix.gates[1].id;}],
 ['missing claim provenance',d=>{d.matrix.claims[0].source_ids=[];}],
 ['change old R223 C06',d=>{d.oldMatrix.claims.find(x=>x.id==='C06').status='PROVEN';}],
 ['change old R223 approval',d=>{d.oldMatrix.claims.find(x=>x.id==='C21').status='ACCEPTED';}],
 ['alter historic factual qualification',d=>{d.oldArt=d.oldArt.replace('37.9% lower chance','37.9 percentage points');}],
 ['remove fingertip force caveat',d=>{d.oldArt=d.oldArt.replace('Eye tracking did not directly measure fingertip force','Researchers measured fingertip force');}],
 ['activate hub button',d=>{d.hub=d.hub.replace(' type="button" disabled',' type="button"');}],
 ['activate A button',d=>{d.a=d.a.replace(' type="button" disabled',' type="button"');}],
 ['add second enabled hub button',d=>{d.hub=d.hub.replace('</main>','<button>Buy now</button></main>');}],
 ['delete hub disclosure',d=>{d.hub=d.hub.replace('Affiliate disclosure:','Hidden incentive:');}],
 ['unquoted checkout link',d=>{d.hub=d.hub.replace('</footer>','<a href=https://zen12.com/hnp>Go</a></footer>');}],
 ['insert onfocus',d=>{d.hub=d.hub.replace('href="#investigations"','onfocus=alert(1) href="#investigations"');}],
 ['insert script',d=>{d.hub=d.hub.replace('</head>','<script src="tracker.js"></script></head>');}],
 ['insert signup form',d=>{d.hub=d.hub.replace('</main>','<form><input type=email></form></main>');}],
 ['fabricate content size',d=>{d.art=d.art.slice(0,400);}],
 ['erase revenue qualification',d=>{d.plan=d.plan.replace('ZERO OR NEGATIVE','UP ONLY');}],
 ['invent Grok match',d=>{d.plan=d.plan.replace('SV9m07PFTYk','MADEUP');}],
 ['alter captions',d=>{d.vtt=d.vtt.replace('forty-eight recordings','miracle cure');}],
 ['copy disparity',d=>{d.b=d.b.replace('The hardest part of a short meditation routine','Instant enlightenment awaits');}],
 ['film marked playable',d=>{d.b=d.b.replace('video not rendered','already online').replace('UNRENDERED','PLAYABLE');}]
];
const baseline=check(source);
const mutations=cases.map(([name,fn])=>{const d=clone(source);fn(d);return {name,errors:check(d)};});
const escaped=mutations.filter(x=>!x.errors.length).map(x=>x.name);
const summary={baseline_errors:baseline,mutations:mutations.length,rejected:mutations.length-escaped.length,escaped};
process.stdout.write(JSON.stringify(summary,null,2)+'\n');
if(baseline.length||escaped.length)process.exit(1);
