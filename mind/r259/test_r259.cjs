'use strict';
// R259 source-level guard. Native: node mind/r259/test_r259.cjs
// Only read local files; no network, WP writes, merchant activation or analytics.
// The same pure validator can be imported into a safe independent source-review runner.
const REQUIRED=[
  'mind/r259/THE-CHOICE-YOU-DIDNT-MAKE-UNPUBLISHED.md',
  'mind/r259/ZEN12-TERMS-DECISION-CARD-UNPUBLISHED.html',
  'mind/r259/CLAIM-SOURCE-PARTNER-REVENUE-HOLD.json',
  'mind/r259/OFFER-TO-REVENUE-CANONICAL-ACCEPTANCE.md',
  'mind/r257/zen12-text-only-A-UNPUBLISHED.html',
  'mind/r257/zen12-optional-film-B-UNPUBLISHED.html'
];
function validate(files){
 const errs=[];
 for(const p of REQUIRED)if(typeof files[p]!=='string'||files[p].length<400)errs.push('missing/short:'+p);
 if(errs.length)return errs;
 const article=files[REQUIRED[0]], html=files[REQUIRED[1]], plan=files[REQUIRED[3]];
 const A=files[REQUIRED[4]],B=files[REQUIRED[5]];
 let m;try{m=JSON.parse(files[REQUIRED[2]])}catch(e){return ['invalid JSON:'+e.message]}
 if(!/The Choice You Didn't Make/.test(article)||article.split(/\s+/).length<1900)errs.push('research article missing or too short');
 for(const s of ['10.1126/science.1111709','10.1016/j.cognition.2010.06.010','10.1371/journal.pone.0045457','69 percent','manipulated trials','Puységur','UNPUBLISHED'])if(!article.includes(s))errs.push('article source/scope:'+s);
 if(/we (personally |independently )?(purchased|used|tried|tested) Zen12/i.test(article)||/our customers (earned|benefited|improved)/i.test(article))errs.push('fabricated lived efficacy');
 if(!Array.isArray(m.sources)||m.sources.length<15||!Array.isArray(m.claims)||m.claims.length<18||!Array.isArray(m.commercial_gates)||m.commercial_gates.length!==16)errs.push('matrix completeness');
 if(m.partner_verified!==false||m.affiliate_link_authorized!==false||m.live_experiment!==false||m.commercial_gates.some(g=>g.status!=='HARD_HOLD'||g.verified_at!==null))errs.push('unauthorized partner/live gate');
 if(m.claims.find(c=>c.id==='C09')?.eligible_for_copy!==false||m.claims.find(c=>c.id==='C13')?.eligible_for_copy!==false)errs.push('unsupported benefit or revenue');
 if(m.owned_product_fallback?.status!=='UNKNOWN_NOT_AUTHENTICATED'||m.attribution_contract?.zero_denominator!=='NOT_COMPUTABLE')errs.push('fabricated fallback/metric');
 if(!m.attribution_contract?.events?.includes('merchant_confirmed_paid_commission')||!m.attribution_contract?.events?.includes('affiliate_outbound_click'))errs.push('outbound conflated with sale');
 if(!/noindex,nofollow/.test(html)||!/lang="en"/.test(html)||!/viewport/.test(html)||!/@media\(max-width:670px\)/.test(html))errs.push('responsive/noindex baseline');
 if(!/button type="button" disabled aria-disabled="true"/.test(html)||!/Purchase link unavailable/.test(html))errs.push('enabled or missing purchase blocker');
 const buttonIndex=html.indexOf('<button type="button" disabled');
 const discloseIndex=html.indexOf('Final Vestige may earn a commission');
 if(discloseIndex<0||buttonIndex<discloseIndex||buttonIndex-discloseIndex>1200)errs.push('material disclosure not adjacent');
 for(const [name,body] of [['html',html],['A',A],['B',B]]){
   if(/<\s*(?:script|iframe|video|audio|source|form)\b/i.test(body))errs.push('unauthorized tag:'+name);
   if(/\bon(?:click|load|error|submit|play|mouseenter)\s*=/i.test(body))errs.push('inline handler:'+name);
   if(/https?:\/\/(?:www\.)?(?:zen12|hypnosislive|inspire3|affiliates\.inspire3)\.[^\s"'<>]+/i.test(body.replaceAll(/(?:https?:\/\/)?zen12\.com\/hnp/g,''))) {
      // Seller URLs may only appear as inert research-source prose, never links.
      if(/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|inspire3|affiliates\.inspire3)\./i.test(body))
       errs.push('active merchant href:'+name);
   }
   if(/<a[^>]+(?:awin1\.com|tracking|ref=|affid=)/i.test(body))errs.push('affiliate/tracker href:'+name);
 }
 if(/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|inspire3|affiliates\.inspire3)\./i.test(html))errs.push('commercial link in card');
 if(/<\s*form\b/i.test(html)||/localStorage|fingerprint|gtag\(|fbq\(/i.test(html))errs.push('duplicate funnel or tracking');
 for(const s of ['not independently tested','twelve minutes','<details>','Seven Day Focus Fieldbook','one-year','NCCIH','Potential affiliate relationship'])if(!html.includes(s))errs.push('buyer guide missing:'+s);
 if(!/R257/.test(plan)||!/NOT COMPUTABLE/.test(plan)||!/7\/30-day/.test(plan)||!/Grok/.test(plan)||!/HARD HOLD/.test(plan))errs.push('acceptance evidence missing');
 if(!/disabled/.test(A)||!/disabled/.test(B)||!/earn a commission/.test(A)||!/earn a commission/.test(B))errs.push('inherited buyer controls/disclosure');
 if(/<\s*video\b/i.test(B)||/autoplay/i.test(B.match(/<video[^>]*>/i)?.[0]||''))errs.push('forced video');
 return errs;
}
function mutators(){
  const A=REQUIRED[0], H=REQUIRED[1], M=REQUIRED[2], P=REQUIRED[3], VA=REQUIRED[4], VB=REQUIRED[5];
  return [
   ['paper erased',A,s=>s.replace("The Choice You Didn't Make","The Hidden Choice")],
   ['missing 2005 DOI',A,s=>s.replace('10.1126/science.1111709','missing-primary')],
   ['missing 2010 DOI',A,s=>s.replace('10.1016/j.cognition.2010.06.010','missing')],
   ['missing 2012 DOI',A,s=>s.replace('10.1371/journal.pone.0045457','missing')],
   ['fabricated test use',A,s=>s+"\nWe independently tested Zen12 and found it works."],
   ['enabled button',H,s=>s.replace('button type="button" disabled aria-disabled="true"','button type="button"')],
   ['missing commission',H,s=>s.replace('Final Vestige may earn a commission','Final Vestige is uncompensated')],
   ['tracking link',H,s=>s.replace('</footer>','<a href="https://zen12.com/hnp?ref=999">buy</a></footer>')],
   ['injected web script',H,s=>s.replace('</footer>','<script src="https://analytics.example/x.js"></script></footer>')],
   ['injected form',H,s=>s.replace('</footer>','<form><input type="email"></form></footer>')],
   ['injected player',H,s=>s.replace('</footer>','<video autoplay src="x.mp4"></video></footer>')],
   ['injected event',H,s=>s.replace('<main>','<main onclick="track()">')],
   ['removed noindex',H,s=>s.replace('noindex,nofollow','index,follow')],
   ['removed focused resource',H,s=>s.replace('Seven Day Focus Fieldbook','New Signup Funnel')],
   ['wrong offer proof',M,s=>s.replace('"partner_verified": false','"partner_verified": true')],
   ['affiliate activated',M,s=>s.replace('"affiliate_link_authorized": false','"affiliate_link_authorized": true')],
   ['fake experiment live',M,s=>s.replace('"live_experiment": false','"live_experiment": true')],
   ['gate bypass',M,s=>s.replace('"status": "HARD_HOLD"','"status": "PASS"')],
   ['false earnings',M,s=>s.replace('"id": "C13",','"id": "C13", "eligible_for_copy": true,')],
   ['wrong zero denominator',M,s=>s.replace('"zero_denominator": "NOT_COMPUTABLE"','"zero_denominator": "0"')],
   ['fake fallback SKU',M,s=>s.replace('UNKNOWN_NOT_AUTHENTICATED','READY_FOR_SALE')],
   ['missing gate',M,s=>s.replace(/\{\s*"id": "publisher_named_acceptance"[\s\S]*?\},\s*/, '')],
   ['no 7/30 cohorts',P,s=>s.replaceAll('7/30-day','1-day')],
   ['R257 omitted',P,s=>s.replaceAll('R257','R200')],
   ['A forced media',VA,s=>s+'<video autoplay></video>'],
   ['B forced media',VB,s=>s+'<video autoplay></video>'],
   ['both forced media A',VA,s=>s+'<video autoplay></video>'],
   ['both forced media B',VB,s=>s+'<video autoplay></video>'],
  ];
}
function test(files){
 const baseline=validate(files); if(baseline.length)throw new Error('baseline failed: '+baseline.join(' | '));
 let rejected=0;const results=[];
 for(const [name,path,mutate] of mutators()){
  const sample={...files,[path]:mutate(files[path])};
  const errors=validate(sample);results.push({name,errors});
  if(!errors.length)throw new Error('failed to reject mutation: '+name);
  rejected++;
 }
 return {status:'PASS',baseline:'PASS',rejected,total:mutators().length,required:REQUIRED.length,details:results.map(x=>x.name)};
}
module.exports={REQUIRED,validate,test};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const root=path.resolve(__dirname,'../..');const files=Object.fromEntries(REQUIRED.map(p=>[p,fs.readFileSync(path.join(root,p),'utf8')]));
 const out=test(files);process.stdout.write(JSON.stringify(out,null,2)+'\n');
}
