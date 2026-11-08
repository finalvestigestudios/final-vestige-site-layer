'use strict';
// R227 executable source-level negative mutation tests; NOT a browser, WordPress, merchant, or settlement check.
// Native: node mind/r227/test_mind_r227.cjs
const FILES={article:'the-man-in-the-suit-INVISIBLE-GORILLA-UNPUBLISHED.md',matrix:'SOURCE-CLAIM-ELIGIBILITY-RELEASE-MATRIX.json',a:'zen12-R227-A-TEXT-UNPUBLISHED.html',b:'zen12-R227-B-OPTIONAL-42S-UNRENDERED.html',vtt:'zen12-R227-42s.vtt',hub:'mind-four-stream-attention-WP-SOURCE-UNPUBLISHED.html',plan:'OFFER-FIRST-CREATOR-FIT-AB-ATTRIBUTION-RELEASE.md'};
const EXPECTED_CLAIMS={"B01":"PRIMARY_STUDY_BOUNDED","B02":"PRIMARY_STUDY_BOUNDED","B03":"HISTORICAL_PRIMARY_BOUNDED","B04":"PRIMARY_STUDY_BOUNDED","B05":"BOUNDARY_NOT_EXTRAPOLATE","B06":"PRIMARY_STUDY_BOUNDED","Z01":"SELLER_DESCRIBED_ONLY","Z02":"SELLER_DESCRIBED_ONLY","Z03":"SELLER_DESCRIBED_ONLY","Z04":"SELLER_PROMISE_NOT_FULFILLMENT_VERIFIED","Z05":"PRICE_AND_CHECKOUT_UNVERIFIED","Z06":"PRODUCT_SPECIFIC_EFFICACY_UNSUBSTANTIATED","Z07":"PRODUCT_SPECIFIC_EFFICACY_UNSUBSTANTIATED","Z08":"PRODUCT_SPECIFIC_EFFICACY_UNSUBSTANTIATED","H01":"SELLER_DESCRIBED_ONLY","H02":"SELLER_PROMISE_NOT_FULFILLMENT_VERIFIED","H03":"PRODUCT_SPECIFIC_EFFICACY_UNSUBSTANTIATED","R01":"INDEPENDENT_RCT_NOT_ZEN12","R02":"INDEPENDENT_RCT_NOT_EQUIVALENCE","R03":"INDEPENDENT_REVIEW_NOT_ZEN12","E01":"GOVERNMENT_GUIDANCE","E02":"GOVERNMENT_GUIDANCE","A01":"PUBLISHER_APPROVAL_UNVERIFIED","A02":"HARD_HOLD","F01":"PROVIDER_CONFIRMED_LEADS_UNVERIFIED","F02":"OWNED_SALE_NOT_VERIFIED","F03":"REVENUE_NOT_COMPUTABLE","G01":"CREATOR_MATCH_UNVERIFIED","D01":"EXISTING_FUNNEL_PRESERVE"};
const EXPECTED_GATES=["named_publisher_approval","permitted_website_channel","permitted_social_channel","permitted_email_channel","issued_affiliate_earning_url","commission_cookie_and_tracking_terms","settlement_refund_reversal_terms","exact_product_benefit_proof","current_checkout_total","seller_refund_terms_and_real_fulfillment","owned_payhip_rights_cleared_mind_sku","owned_payhip_checkout_and_delivery","provider_confirmed_jetpack_leads","grok_asset_ids_post_urls_and_mobile_routes","first_party_metrics_privacy_review","founder_prod_release_approval"];
const REQUIRED_SOURCES=["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14","S15","S16","S17","S18","S19","S20"];
const REQUIRED_STUDIES=['https://doi.org/10.1068/p281059','https://doi.org/10.1177/0956797613479386','https://pmc.ncbi.nlm.nih.gov/articles/PMC3563049/'];
const tags=(html,name)=>[...html.matchAll(new RegExp('<'+name+'\\b[^>]*>','gi'))].map(x=>x[0]);
const attrs=t=>{let a={};const rx=/([\w:-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;const s=t.replace(/^<\w+\b/i,'').replace(/>$/,'');let m;while((m=rx.exec(s)))a[m[1].toLowerCase()]=m[2]??m[3]??m[4]??'';return a};
const sansVideo=s=>s.replace(/<!-- OPTIONAL_FILM_START -->[\s\S]*?<!-- OPTIONAL_FILM_END -->/g,'');
function check(f){
 const errs=[],bad=s=>errs.push(s);let data;
 try{data=JSON.parse(f.matrix)}catch(e){return ['invalid JSON']}
 if(data.state!=='UNPUBLISHED_NOT_AUTHORIZED'||data.commerce?.activated!==false||data.commerce?.affiliate_earning_url!==null||data.commerce?.publisher_approval_document!==null||data.commerce?.enabled_checkout_controls!==0||data.commerce?.net_revenue_per_1000_qualified_human_sessions!=='NOT_COMPUTABLE')bad('commercial activated or fabricated');
 if(data.release_gates?.length!==EXPECTED_GATES.length)bad('gate count');
 for(const id of EXPECTED_GATES){const r=(data.release_gates||[]).filter(g=>g.id===id);if(r.length!==1||r[0].status!=='HARD_HOLD')bad('gate identity/status '+id)}
 const src=new Map((data.sources||[]).map(x=>[x.id,x.url]));
 if(src.size!==REQUIRED_SOURCES.length||data.sources?.length!==REQUIRED_SOURCES.length)bad('source registry count/dupes');
 for(const id of REQUIRED_SOURCES)if(!src.has(id)||!/^https:\/\//.test(src.get(id)))bad('missing source '+id);
 if(data.claims?.length!==Object.keys(EXPECTED_CLAIMS).length)bad('claim registry count');
 for(const [id,status] of Object.entries(EXPECTED_CLAIMS)){const r=(data.claims||[]).filter(c=>c.id===id);if(r.length!==1||r[0].status!==status||!r[0].source_ids?.length||r[0].source_ids.some(s=>!src.has(s)))bad('claim identity/status/provenance '+id)}
 for(const [key,html]of [['a',f.a],['b',f.b],['hub',f.hub]]){
  if(!/<html lang="en"/.test(html)||!/<meta name="viewport"/.test(html)||!/<meta name="robots" content="noindex,nofollow"/.test(html))bad(key+' noindex/access');
  if(/<script\b|<iframe\b|<form\b|<input\b|<video\b|<audio\b|<source\b|<object\b|<embed\b/i.test(html))bad(key+' external player/form/script');
  if(/\bon\w+\s*=|javascript\s*:/i.test(html))bad(key+' event handler');
  if(/href\s*=\s*["']?[^\s"'<>]*(?:zen12\.com|inspire3\.com|hypnosislive\.com|awin1|checkout|payhip|clickbank)/i.test(html))bad(key+' commercial link active');
  const bs=tags(html,'button');
  if(bs.length!==1)bad(key+' button count');
  for(const t of bs){const a=attrs(t);if(a.type!=='button'||!('disabled' in a)||a['aria-disabled']!=='true'||'formaction' in a||'onclick' in a)bad(key+' button activation')}
  if(!/may earn a commission at no extra cost/i.test(html))bad(key+' near-button disclosure removed');
  const bp=html.indexOf('<button');const dc=html.lastIndexOf('may earn a commission',bp);if(dc<0||bp-dc>950)bad(key+' disclosure too far from CTA');
  if(!/https:\/\/finalvestige\.com\/focus\//.test(html))bad(key+' missing existing Focus');
  if(!/prefers-reduced-motion/.test(html)||!/focus-visible/.test(html))bad(key+' a11y source');
  if(/target\s*=\s*["']?_blank/i.test(html))bad(key+' external tab');
  if(/<a\b[^>]*href\s*=\s*["']?\s*(?:http:|\/\/)/i.test(html))bad(key+' insecure link');
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);if(new Set(ids).size!==ids.length)bad(key+' repeated ID');
 }
 if(!f.b.includes('<!-- OPTIONAL_FILM_START -->')||f.a.includes('<!-- OPTIONAL_FILM_START -->')||sansVideo(f.b)!==f.a)bad('AB parity/optional only');
 if(!f.b.includes('no playable video')&&!f.b.includes('not a playable video'))bad('film falsely playable');
 const cues=[...f.vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})\n([^\n]+)/g)];
 if(cues.length!==5)bad('missing captions');
 let t=0;const seconds=s=>{let x=s.split(':');return Number(x[0])*3600+Number(x[1])*60+Number(x[2])};
 for(const c of cues){if(seconds(c[1])!==t||!f.b.includes(c[3]))bad('caption continuity/transcript');t=seconds(c[2])}if(t!==42)bad('film duration mismatch');
 for(const x of REQUIRED_STUDIES)if(!f.article.includes(x))bad('article missing primary research '+x);
 if(!/no affiliate endorsement/i.test(f.article)||!/no clinical|no commercial recording/i.test(f.article))bad('investigation commercial boundary');
 if(!/SV9m07PFTYk/.test(f.plan)||!/NOT_COMPUTABLE/.test(f.plan)||!/merchant_confirmed_paid_order/.test(f.plan)||!/provider_confirmed_focus_signup/.test(f.plan))bad('conversion contract');
 return [...new Set(errs)];
}
function mutationCases(f){
 const out=[],change=(label,k,val)=>out.push({label,files:{...f,[k]:val}});
 for(const k of ['a','b','hub']){
  change(k+' extra live CTA',k,f[k].replace('</main>','<button type="button">Buy</button></main>'));
  change(k+' native enable',k,f[k].replace(' disabled aria-disabled="true"',''));
  change(k+' disclosure removed',k,f[k].replace(/may earn a commission at no extra cost/i,'gives you a nice deal'));
  change(k+' JS click',k,f[k].replace('<main', '<main onclick="alert(1)"'));
  change(k+' thirdparty JS',k,f[k].replace('</main>','<script src="//analytics.evil/script.js"></script></main>'));
  change(k+' duplicate email list',k,f[k].replace('</main>','<form><input name="email"></form></main>'));
  change(k+' merchant link',k,f[k].replace('</main>','<a href=https://zen12.com/hnp>Go to seller</a></main>'));
  change(k+' noindex removed',k,f[k].replace('<meta name="robots" content="noindex,nofollow">',''));
  change(k+' Focus removed',k,f[k].replaceAll('https://finalvestige.com/focus/','/no-focus/'));
 }
 for(const id of EXPECTED_GATES){
  const d=JSON.parse(f.matrix);d.release_gates.find(x=>x.id===id).status='APPROVED';change('gate promoted '+id,'matrix',JSON.stringify(d));
  const rm=JSON.parse(f.matrix);rm.release_gates=rm.release_gates.filter(x=>x.id!==id);change('gate removed '+id,'matrix',JSON.stringify(rm));
 }
 for(const id of Object.keys(EXPECTED_CLAIMS)){
  const d=JSON.parse(f.matrix);d.claims.find(x=>x.id===id).status='VERIFIED_AND_APPROVED';change('claim forged '+id,'matrix',JSON.stringify(d));
  const ren=JSON.parse(f.matrix);ren.claims.find(x=>x.id===id).id=id+'_RENAMED';change('claim renamed '+id,'matrix',JSON.stringify(ren));
  const rm=JSON.parse(f.matrix);rm.claims=rm.claims.filter(x=>x.id!==id);change('claim removed '+id,'matrix',JSON.stringify(rm));
 }
 change('AB drift','b',f.b.replace('twelve levels and 48 MP3','eleven levels and 48 MP3'));
 change('film removed','b',sansVideo(f.b));
 change('captions removed','vtt',f.vtt.replace('People can miss an event they could have seen. Attention is selective.',''));
 change('source vanished','article',f.article.replace('https://doi.org/10.1068/p281059','NO_DOI'));
 change('revenue fabricated','plan',f.plan.replaceAll('NOT_COMPUTABLE','CLICK_IS_SALE'));
 return out;
}
function run(f){const baseline=check(f),mutations=mutationCases(f),slipped=mutations.filter(x=>!check(x.files).length).map(x=>x.label);return{pass:!baseline.length&&!slipped.length,baseline_violations:baseline,mutations_total:mutations.length,mutations_rejected:mutations.length-slipped.length,slipped}}
if(typeof module!=='undefined')module.exports={FILES,EXPECTED_CLAIMS,EXPECTED_GATES,check,mutationCases,run};
if(typeof require==='function'&&typeof module!=='undefined'&&require.main===module){const fs=require('fs'),path=require('path'),f={};for(const [k,p]of Object.entries(FILES))f[k]=fs.readFileSync(path.join(__dirname,p),'utf8');const r=run(f);console.log(JSON.stringify(r,null,2));process.exitCode=r.pass?0:1;}
