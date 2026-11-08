'use strict';
// Mind R226 source-only safeguards. Native CLI: node mind/r226/test_mind_r226.cjs
// This script verifies source, NOT real browser, WordPress sanitization, merchant or paid results.
const FILES = {
 article:'the-voice-in-the-recording-SELF-HYPNOSIS-EVIDENCE-UNPUBLISHED.md',
 matrix:'SELLER-CLAIMS-CLINICAL-EVIDENCE-AUTHORIZATION-GATES.json',
 a:'zen12-r226-A-TEXT-ONLY-UNPUBLISHED.html',
 b:'zen12-r226-B-OPTIONAL-42S-UNRENDERED.html',
 vtt:'zen12-r226-42s.vtt',
 hub:'mind-archive-FOUR-STREAM-WP-PREVIEW-UNPUBLISHED.html',
 plan:'OFFER-FIRST-CREATOR-FIT-AB-ATTRIBUTION-ACCEPTANCE.md'
};
const GATES = ['named_publisher_approval','permitted_website_channel','permitted_social_channel','permitted_email_channel','account_issued_earning_link','commission_tracking_terms','settlement_and_reversal_terms','exact_product_claim_proof','current_checkout_total','current_refund_terms_and_fulfillment','owned_payhip_rights_cleared_sku','owned_product_checkout_and_delivery','provider_confirmed_focus_lead','grok_asset_media_destination_reconciled','first_party_attribution_review','founder_release_approval'];
const LOCKED_CLAIMS = {
 Z06:'UNSUBSTANTIATED_EXCLUDE_AS_BENEFIT',Z07:'UNSUBSTANTIATED_PRODUCT_CLAIM_EXCLUDE',Z08:'UNSUBSTANTIATED_PRODUCT_CLAIM_EXCLUDE',
 H04:'UNSUBSTANTIATED_PRODUCT_CLAIM_EXCLUDE',A01:'INDIVIDUAL_PERMISSION_UNVERIFIED',A02:'HARD_HOLD',F02:'OWNED_SALE_NOT_VERIFIED',F03:'SETTLEMENT_UNVERIFIED'
};
const URLS = ['https://inspire3.com/','https://zen12.com/hnp','https://hypnosislive.com/mental-skills/total-focus','https://hypnosislive.com/faq','https://eprints.bournemouth.ac.uk/31277/','https://pubmed.ncbi.nlm.nih.gov/36526937/','https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance','https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking'];
function tags(html,name){return Array.from(html.matchAll(new RegExp('<'+name+'\\b[^>]*>','gi')),m=>m[0])}
function attrs(tag){const r={};const s=tag.replace(/^<\w+\b/i,'').replace(/>$/,'');const rx=/([\w:-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;let m;while((m=rx.exec(s)))r[m[1].toLowerCase()]=m[2]??m[3]??m[4]??'';return r}
function plain(html){return html.replace(/<!-- OPTIONAL_FILM_START -->[\s\S]*?<!-- OPTIONAL_FILM_END -->/g,'').replace(/<title>Zen12 Premium decision guide — [AB] —/g,'<title>Zen12 Premium decision guide —');}
function check(f){
 const e=[], fail=x=>e.push(x); let m=null;
 try{m=JSON.parse(f.matrix)}catch(err){fail('matrix unparseable: '+err.message);return e}
 if(m.state!=='UNPUBLISHED_NOT_AUTHORIZED'||m.commerce?.activated!==false||m.commerce?.affiliate_earning_url!==null||m.commerce?.authoritative_affiliate_approval!==null)fail('commercial activation or approval falsely asserted');
 const gids=(m.release_gates||[]).map(x=>x.id);
 if(gids.length!==GATES.length||new Set(gids).size!==GATES.length)fail('gate count/uniqueness');
 for(const id of GATES){const arr=(m.release_gates||[]).filter(x=>x.id===id);if(arr.length!==1||arr[0].status!=='HARD_HOLD')fail('missing or weakened gate '+id)}
 const sources=new Map((m.sources||[]).map(x=>[x.id,x]));
 if(sources.size!==m.sources?.length||m.sources?.length<20)fail('source register missing or duplicated');
 for(const u of URLS)if(!m.sources.some(x=>x.url===u))fail('mandatory source missing: '+u);
 const ids=(m.claims||[]).map(x=>x.id);if(new Set(ids).size!==ids.length||ids.length<26)fail('claim count or duplicate');
 for(const [id,state] of Object.entries(LOCKED_CLAIMS)){const arr=m.claims.filter(x=>x.id===id);if(arr.length!==1||arr[0].status!==state)fail('claim identity/status weakened '+id);if(!arr[0]?.source_ids?.length||arr[0].source_ids.some(s=>!sources.has(s)))fail('claim provenance '+id)}
 for(const c of m.claims)if(!c.source_ids?.length||c.source_ids.some(s=>!sources.has(s)))fail('invalid source reference '+c.id);
 for(const [k,h] of [['a',f.a],['b',f.b],['hub',f.hub]]){
  if(!/<html\s+lang=["']en["']/i.test(h)||!/<meta\s+name=["']viewport["']/i.test(h))fail(k+' missing responsive language/viewport');
  if(!/<meta\s+name=["']robots["']\s+content=["']noindex,nofollow["']/i.test(h))fail(k+' must remain unpublished noindex');
  if(/<script\b|<iframe\b|<form\b|<input\b|<video\b|<audio\b|<source\b|<object\b|<embed\b/i.test(h))fail(k+' added external script, form, or playable media');
  if(/\bon\w+\s*=/i.test(h)||/javascript\s*:/i.test(h))fail(k+' event handler or JS URL');
  if(/(?:affiliate|awin1|clickbank|payhip|checkout|cart)[^\n]{0,100}href\s*=|href\s*=\s*["']?[^\s"'>]*(?:awin1|affiliates\.inspire3|checkout|clickbank|payhip)/i.test(h))fail(k+' suspicious commercial/earning href');
  const bt=tags(h,'button');if(bt.length!==1)fail(k+' changed number of merchant controls');
  for(const t of bt){const a=attrs(t);if(!('disabled' in a)||a['aria-disabled']!=='true'||a.type!=='button'||'onclick' in a||'formaction' in a||'data-checkout' in a)fail(k+' enabled or hijacked commercial button')}
  const words=h.slice(Math.max(0,h.indexOf('<div class="offer"')),h.indexOf('</aside>')>0?h.indexOf('</aside>'):h.length);
  if(!/may earn a commission/i.test(words)||!/extra cost|no extra cost/i.test(words))fail(k+' adjacent disclosure missing');
  if(!/https:\/\/finalvestige\.com\/focus\//.test(h))fail(k+' existing Focus pathway missing');
  if(!/prefers-reduced-motion/.test(h)||!/focus-visible/.test(h))fail(k+' a11y CSS missing');
  if(/target\s*=\s*["']?_blank/i.test(h))fail(k+' unsafe new window');
  const idSet=new Set();for(const a of tags(h,'section').concat(tags(h,'header')).concat(tags(h,'div'))){const id=attrs(a).id;if(id){if(idSet.has(id))fail(k+' duplicate element id '+id);idSet.add(id)}}
 }
 if(!f.a.includes('independent')||!f.b.includes('independent'))fail('independent editorial statement missing');
 if(!/OPTIONAL_FILM_START/.test(f.b)||/OPTIONAL_FILM_START/.test(f.a))fail('film must be optional only in B');
 if(!/UNRENDERED|unrendered/.test(f.b)||!/no video file/i.test(f.b))fail('B falsely implies rendered media');
 if(plain(f.a)!==plain(f.b))fail('A/B guide copy diverged beyond optional film');
 const cues=[...f.vtt.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)\n([^\n]+)/g)];
 if(cues.length!==5)fail('not five VTT cues');
 const secs=s=>{const p=s.split(':');return +p[0]*3600+ +p[1]*60+ +p[2]};
 let t=0;for(const c of cues){if(secs(c[1])!==t)fail('caption gap or overlap');t=secs(c[2]);if(!f.b.includes(c[3]))fail('caption text differs from transcript')};if(t!==42)fail('caption timing not 42 seconds');
 for(const u of ['https://eprints.bournemouth.ac.uk/31277/','https://pubmed.ncbi.nlm.nih.gov/36526937/','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'])if(!f.article.includes(u))fail('article missing primary/historical evidence '+u);
 if(!/no affiliate endorsement|no referral link|no price recommendation/i.test(f.article))fail('article editorial-commerce separation absent');
 for(const s of ['SV9m07PFTYk','NOT_COMPUTABLE','confirmed_focus_subscriber','affiliate_outbound','merchant_confirmed_paid_sale','1000*N/Q'])if(!f.plan.includes(s))fail('conversion attribution acceptance missing '+s);
 return [...new Set(e)];
}
function mutationCases(f){
 const ms=[];const put=(label,key,content)=>ms.push({label,files:{...f,[key]:content}});
 for(const k of ['a','b','hub']){
  put(k+' new enabled button',k,f[k].replace('</main>','<button type="button">Buy instantly</button></main>'));
  put(k+' remove native disabled',k,f[k].replace(/\sdisabled\saria-disabled=["']true["']/,''));
  put(k+' remove commission disclosure',k,f[k].replace(/may earn a commission/i,'might provide a nice link'));
  put(k+' inject JS event',k,f[k].replace('<main ', '<main onclick="window.location=\'https://evil.example\'" '));
  put(k+' inject script',k,f[k].replace('</main>','<script src="//tracker.example/p.js"></script></main>'));
  put(k+' inject form',k,f[k].replace('</main>','<form><input name="email"></form></main>'));
  put(k+' inject unquoted checkout',k,f[k].replace('</main>','<a href=https://evil.example/checkout/pay>Buy now</a></main>'));
  put(k+' remove noindex',k,f[k].replace(/<meta\s+name=["']robots["']\s+content=["']noindex,nofollow["']>/,''));
 }
 for(const id of GATES){
  const parsed=JSON.parse(f.matrix),row=parsed.release_gates.find(g=>g.id===id);row.status='APPROVED';
  put('gate approved '+id,'matrix',JSON.stringify(parsed));
  const gone=JSON.parse(f.matrix);gone.release_gates=gone.release_gates.filter(g=>g.id!==id);
  put('gate deleted '+id,'matrix',JSON.stringify(gone));
 }
 for(const [id] of Object.entries(LOCKED_CLAIMS)){const parsed=JSON.parse(f.matrix);parsed.claims.find(c=>c.id===id).status='VERIFIED_APPROVED';put('evidence fabricated '+id,'matrix',JSON.stringify(parsed))}
 put('film removed','b',f.b.replace(/<!-- OPTIONAL_FILM_START -->[\s\S]*?<!-- OPTIONAL_FILM_END -->/,''));
 put('A/B drift','b',f.b.replace('twelve sequential levels','eleven sequential levels'));
 put('caption missing','vtt',f.vtt.replace('Try twelve quiet minutes for free. Then decide what a library is worth to you.',''));
 put('sale invented','plan',f.plan.replace('NOT_COMPUTABLE','PAID_SALE_INFERRED'));
 put('article source gone','article',f.article.replace('https://eprints.bournemouth.ac.uk/31277/','NO_LINK'));
 return ms;
}
function run(f){const baseline=check(f);const m=mutationCases(f);const slipped=[];for(const x of m)if(check(x.files).length===0)slipped.push(x.label);return{baseline_violations:baseline,mutations_total:m.length,mutations_rejected:m.length-slipped.length,slipped,pass:baseline.length===0&&slipped.length===0}}
if(typeof module!=='undefined')module.exports={FILES,GATES,LOCKED_CLAIMS,check,mutationCases,run};
if(typeof require==='function'&&typeof module!=='undefined'&&require.main===module){
 const fs=require('fs'),path=require('path'),base=__dirname,files={};
 for(const [k,v] of Object.entries(FILES))files[k]=fs.readFileSync(path.join(base,v),'utf8');
 const result=run(files);console.log(JSON.stringify(result,null,2));process.exitCode=result.pass?0:1;
}
