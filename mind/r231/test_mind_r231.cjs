/* R231 source-level release guard; run: node mind/r231/test_mind_r231.cjs from repository root.
 * B is a non-playable storyboard concept, not video media. Browser/CMS/merchant tests separate.
 */
const path=require('node:path'),fs=require('node:fs');
const PREFIX=path.join('mind','r231');
const FILES={
 article:'the-detour-you-never-noticed-MIND-WANDERING-UNPUBLISHED.md',
 A:'zen12-A-text-only-WP-PREVIEW-UNPUBLISHED.html',
 B:'zen12-B-optional-42s-WP-PREVIEW-UNRENDERED.html',
 hub:'mind-archive-FOUR-STREAM-WP-PREVIEW-UNPUBLISHED.html',
 captions:'zen12-original-42-second-proposed-captions.vtt',
 matrix:'OFFER-CLAIM-SOURCE-RELEASE-GATES.json',
 plan:'OFFER-FUNNEL-BLOCKER-EXPERIMENT-REVENUE-ACCEPTANCE.md'
};
const EXPECTED_REGISTRY_DIGEST='7ccd19d6';
function fnv(s){let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return h.toString(16).padStart(8,'0')}
function matrixDigest(m){return fnv(JSON.stringify({sources:m.evidence_sources.map(x=>[x.id,x.url,x.type]),claims:m.claims.map(x=>[x.id,x.statement,x.status,x.evidence]),gates:m.release_gates.map(x=>[x.id,x.status])}))}
function normalize(s){return s.replace(/\s+/g,' ').trim()}
function scrubVideo(s){return s.replace(/<section aria-labelledby="optional-film" class="rule">[\s\S]*?<\/section>/i,'')}
function failures(files){
 const e=[];
 const chk=(ok,msg)=>{if(!ok)e.push(msg)};
 let m; try{m=JSON.parse(files.matrix)}catch(x){return['Matrix not JSON: '+x]}
 chk(m.sprint==='R231'&&m.draft_status==='UNPUBLISHED','draft identity');
 chk(m.evidence_sources.length===19 && m.claims.length===25 && m.release_gates.length===16,'matrix counts changed');
 chk(matrixDigest(m)===EXPECTED_REGISTRY_DIGEST,'protected source/claim/gate registry changed');
 chk(m.release_gates.every(x=>x.status==='HARD_HOLD'&&x.evidence===null),'gate not hard hold');
 chk(m.commerce.activated===false && m.commerce.approved_affiliate_earning_url===null,'commerce activated');
 chk(m.commerce.net_revenue_per_1000_qualified_human_sessions==='NOT_COMPUTABLE','invented net revenue');
 chk(m.privacy.new_tracking_script===false && m.privacy.duplicate_signup_form===false && m.privacy.active_merchant_links===false,'privacy guard changed');
 for (const name of ['A','B','hub']){
   const s=files[name]||'';
   chk(s.includes('<!-- wp:html -->')&&s.includes('<!-- /wp:html -->'),'WP wrapper '+name);
   chk((s.match(/<h1\b/gi)||[]).length===1,'H1 count '+name);
   chk(!/<script\b|<iframe\b|<form\b|<video\b|<audio\b/gi.test(s),'no scripts/embeds/forms/unrendered video '+name);
   chk(!/on(?:click|load|error|mouseover|focus)\s*=/gi.test(s),'no inline handlers '+name);
   chk(!/href\s*=\s*(?:"|')?\s*(?:https?:)?\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./gi.test(s),'no active merchant links '+name);
   chk(!/(?:utm_campaign|affiliate_click|ref=affiliate|commission_paid)=/gi.test(s),'no unverified event/url params '+name);
   chk(s.includes('https://finalvestige.com/focus/'),'one existing Focus route '+name);
   chk(s.includes(':focus-visible') && s.includes('prefers-reduced-motion') && s.includes('max-width:800px'),'mobile/accessibility CSS '+name);
   chk(!/<input\b/gi.test(s),'no input fields '+name);
 }
 for(const name of ['A','B']){
   const s=files[name]||'';
   chk(/<button\b[^>]*\sdisabled\b[^>]*>/i.test(s),'native disabled button '+name);
   chk(!/<button\b(?![^>]*\sdisabled\b)[^>]*>/i.test(s),'enabled button '+name);
   const d=s.indexOf('Affiliate disclosure:'); const b=s.indexOf('View the approved Zen12 offer');
   chk(d!==-1 && b>d && b-d<360,'adjacent commission disclosure '+name);
   chk(s.includes('No affiliate link is active here'),'no implied existing affiliate '+name);
   chk(s.includes('seller-described')&&s.includes('product-specific'),'proper seller/evidence qualifiers '+name);
   chk(!/\$\s*\d{2,}/.test(s),'no asserted price '+name);
 }
 chk(normalize(files.A)===normalize(scrubVideo(files.B)),'A/B content beyond film section differs');
 chk(files.B.includes('id="optional-film"')&&files.B.includes('42-second')&&files.B.includes('<svg')&&files.B.includes('<details>'),'film concept assets absent');
 chk((files.captions.match(/--> /g)||[]).length===5 && files.captions.includes('00:00:42.000'),'captions completeness');
 chk(files.B.includes('Some wandering is voluntary')&&files.captions.includes('Some wandering is voluntary'),'caption/transcript mismatch');
 chk(files.article.includes('No affiliate earning link is currently authorized')&&files.article.includes('replication')&&files.article.includes('two-week'),'investigation scientific/commercial limits');
 chk(!/https?:\/\/(?:zen12|brainwaveshots|hypnosislive)\.[^\s\]]+\?[^\s\]]*(?:aff|ref|subid)/gi.test(files.article),'no affiliate URL in investigation');
 chk(files.plan.includes('NOT COMPUTABLE')&&files.plan.includes('merchant-confirmed')&&files.plan.includes('HARD HOLD'),'conversion metrics/proof guard');
 return e;
}
function mutationSuite(files){
 const base=failures(files);if(base.length)return {baseline:base,accepted:0,rejected:0,misses:[]};
 let rejected=0,accepted=0,misses=[];
 const trial=(name,mod)=>{
    const altered={...files};mod(altered);
    const errs=failures(altered);if(errs.length)rejected++;else{accepted++;misses.push(name)}
 };
 trial('activate commerce',f=>{let o=JSON.parse(f.matrix);o.commerce.activated=true;f.matrix=JSON.stringify(o)});
 trial('fake sale',f=>{let o=JSON.parse(f.matrix);o.commerce.net_revenue_per_1000_qualified_human_sessions='9999';f.matrix=JSON.stringify(o)});
 trial('new tracker',f=>{let o=JSON.parse(f.matrix);o.privacy.new_tracking_script=true;f.matrix=JSON.stringify(o)});
 const m=JSON.parse(files.matrix);
 for(let i=0;i<m.claims.length;i++)trial('claim #'+i,f=>{const x=JSON.parse(f.matrix);x.claims[i].status='VERIFIED';f.matrix=JSON.stringify(x)});
 for(let i=0;i<m.evidence_sources.length;i++)trial('source #'+i,f=>{const x=JSON.parse(f.matrix);x.evidence_sources[i].url='https://invalid.example/';f.matrix=JSON.stringify(x)});
 for(let i=0;i<m.release_gates.length;i++)trial('gate #'+i,f=>{const x=JSON.parse(f.matrix);x.release_gates[i].status='APPROVED';f.matrix=JSON.stringify(x)});
 for (const name of ['A','B','hub']){
  trial('merchant anchor '+name,f=>{f[name]+='<a href=https://zen12.com/hnp>Buy now</a>'});
  trial('XSS '+name,f=>{f[name]+='<svg onload=alert(1)></svg>'});
  trial('tracking '+name,f=>{f[name]+='<script src="https://analytics.example/pixel.js"></script>'});
  trial('duplicate form '+name,f=>{f[name]+='<form><input name=email /></form>'});
 }
 for(const name of ['A','B']){
  trial('disclosure removal '+name,f=>{f[name]=f[name].replace('Affiliate disclosure:','')});
  trial('enabled button '+name,f=>{f[name]=f[name].replace('<button type="button" disabled','<button type="button"')});
  trial('false price '+name,f=>{f[name]+='<p>$999</p>'});
 }
 trial('missing film',f=>{f.B=f.B.replace(/<section aria-labelledby="optional-film" class="rule">[\s\S]*?<\/section>/i,'')});
 trial('caption damage',f=>{f.captions=f.captions.replace('00:00:42.000','00:00:12.000')});
 trial('invented author use',f=>{f.article=f.article.replace('No affiliate earning link is currently authorized','I personally used Zen12 and can verify its powers')});
 return {baseline:[],rejected,accepted,misses};
}
module.exports={failures,mutationSuite,FILES,EXPECTED_REGISTRY_DIGEST};
if(require.main===module){
 const dir=path.resolve(process.cwd(),PREFIX); const files={};
 for(const [k,v] of Object.entries(FILES))files[k]=fs.readFileSync(path.join(dir,v),'utf8');
 const r=mutationSuite(files);
 console.log(JSON.stringify(r,null,2)); if(r.baseline.length||r.accepted)process.exitCode=1;
}
