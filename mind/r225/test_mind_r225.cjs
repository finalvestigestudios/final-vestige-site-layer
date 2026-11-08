/* FV Mind R225 — source-only regression. Run from repo root:
   node mind/r225/test_mind_r225.cjs
   This checks text/source constraints. It DOES NOT prove browser a11y, merchant eligibility, video playback, revenue or WordPress rendering.
*/
'use strict';
const fs=require('node:fs'),path=require('node:path');
const read=(name,dir=__dirname)=>fs.readFileSync(path.join(dir,name),'utf8');
const source={
 article:read('the-suggestion-without-hypnosis-UNPUBLISHED.md'),
 hub:read('mind-archive-four-stream-WP-SOURCE-UNPUBLISHED.html'),
 a:read('zen12-proof-decision-A-TEXT-UNPUBLISHED.html'),
 b:read('zen12-proof-decision-B-OPTIONAL-42S-UNRENDERED.html'),
 vtt:read('zen12-r225-42s.vtt'),
 matrix:JSON.parse(read('CLAIM-PROOF-PARTNER-REVENUE-GATES.json')),
 plan:read('OFFER-FUNNEL-CREATOR-REVENUE-RELEASE-PROTOCOL.md'),
 oldArticle:read('../r223/the-pendulum-that-answered-IDEOMOTOR-UNPUBLISHED.md'),
 oldReview:read('../r224/the-half-second-gap-meditation-attention-EVIDENCE-REVIEW-UNPUBLISHED.md'),
 oldMatrix:JSON.parse(read('../r224/ATTENTION-MEDITATION-ZEN12-SOURCES-CLAIMS-AUTHORIZATION.json')),
 oldValidator:read('../r224/test_mind_r224.cjs')
};
const gateIds='named_publisher_approval social_channel_permission email_channel_permission issued_earning_url tracking_and_payout_terms seller_creative_rights exact_checkout_price_and_terms refund_terms_and_process product_claim_independent_substantiation adjacent_FTC_disclosure commerce_button_or_link_release video_render_captions_transcript browser_mobile_a11y_performance WordPress_sanitization_and_link_QA founder_release_approval settled_revenue_and_qualified_human_data'.split(' ');
const locked={
 Z01:'SELLER_FEATURE_NOT_DELIVERY_VERIFIED',Z02:'SELLER_FEATURE_NOT_DELIVERY_VERIFIED',Z03:'SELLER_FEATURE_NOT_DELIVERY_VERIFIED',
 Z04:'DATED_PUBLIC_PRICE_NOT_FINAL_CHECKOUT',Z05:'SELLER_REFUND_PROMISE_NOT_FULFILLMENT_VERIFIED',
 Z06:'UNSUBSTANTIATED_PRODUCT_SPECIFIC_DO_NOT_ADOPT',Z07:'UNSUBSTANTIATED_PRODUCT_SPECIFIC_DO_NOT_ADOPT',Z08:'UNSUBSTANTIATED_PRODUCT_SPECIFIC_DO_NOT_ADOPT',
 S01:'INDEPENDENT_TASK_SPECIFIC_EVIDENCE',S02:'INDEPENDENT_TASK_SPECIFIC_EVIDENCE',
 S03:'INDEPENDENT_INTERVENTION_OTHER_THAN_PRODUCT',S04:'INDEPENDENT_INTERVENTION_OTHER_THAN_PRODUCT',
 H01:'HISTORICAL_CATALOG_PROVENANCE_ONLY',H02:'PUBLISHED_EDITORIAL_ROUTE',
 F01:'PUBLISHED_FUNNEL_ROUTE_NOT_CONFIRMED_LEAD',F02:'PUBLISHED_EXISTING_FUNNEL_NO_DUPLICATION',
 A01:'PUBLISHER_ACCEPTANCE_NOT_VERIFIED',A02:'EARNING_LINK_AND_PERMISSION_HARD_HOLD',
 A03:'OWNED_MIND_SKU_UNVERIFIED',A04:'LEAD_ATTRIBUTION_UNVERIFIED',
 A05:'PAID_CONVERSION_UNVERIFIED',A06:'NOT_COMPUTABLE',X01:'UNRENDERED_NOT_LIVE'
};
function check(d){
 const err=[],m=d.matrix;
 for(const [label,s] of [['hub',d.hub],['A',d.a],['B',d.b]]){
  if(/<\s*(?:script|iframe|form|input|video|audio|source)\b/i.test(s))err.push(label+':external-or-form');
  if(/\son[a-z]+\s*=/i.test(s))err.push(label+':inline-events');
  if(/\b(?:href|formaction|data-url)\s*=\s*['"]?\s*(?:https?:\/\/)?(?:[^\s'">]*\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|awin1\.com|clickbank\.com)/i.test(s))err.push(label+':seller-active-link');
  if(/\b(?:gtag|fbq)\s*\(|localStorage|sessionStorage|data-affiliate-id/i.test(s))err.push(label+':tracker');
  if(!/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(s))err.push(label+':noindex');
  if(!/:focus-visible/.test(s)||!/prefers-reduced-motion:reduce/.test(s))err.push(label+':source-a11y');
  let buttons=[...s.matchAll(/<button\b[^>]*>/gi)].map(v=>v[0]);
  if(buttons.length!==1)err.push(label+':exactly-one-button');
  for(const btn of buttons){
    if(!/\sdisabled(?:\s|>|=)/i.test(btn)||!/aria-disabled="true"/.test(btn))err.push(label+':disabled-button');
    if(/\s(?:href|on[a-z]+|formaction|data-url)\s*=/i.test(btn))err.push(label+':button-active-attrs');
  }
  const p=s.indexOf('Affiliate disclosure:');
  const b=s.search(/<button\b/i);
  if(p<0||b<0||p>b||b-p>320)err.push(label+':adjacent-disclosure');
 }
 const norm=x=>x.replaceAll('TEXT A','VARIANT').replaceAll('OPTIONAL FILM B','VARIANT').replace(/<details class="film"[\s\S]*?<\/details>/,'');
 if(norm(d.a)!==norm(d.b))err.push('ab:only-film-diff');
 if(!/video file yet|no video file/i.test(d.b)||/<video\b/i.test(d.b))err.push('b:not-playable-yet');
 const film=d.b.match(/<details class="film"[\s\S]*?<\/details>/)?.[0]||'';
 if(!film)err.push('b:optional-film');
 const captions=[...d.vtt.matchAll(/\d\d:\d\d:\d\d\.\d{3} --> \d\d:\d\d:\d\d\.\d{3}\s*\n([^\n]+)/g)].map(x=>x[1].trim());
 const transcript=[...film.matchAll(/<li><strong>[^<]+<\/strong> ([^<]+)<\/li>/g)].map(x=>x[1].trim());
 if(captions.length!==5||transcript.length!==5||captions.some((s,i)=>s!==transcript[i])||!d.vtt.includes('00:00:33.000 --> 00:00:42.000'))err.push('b:caption-parity-42s');
 if(m.commercial_release!=='UNPUBLISHED_HARD_HOLD')err.push('matrix:release');
 const gates=m.gates||[];
 if(gates.length!==16||new Set(gates.map(x=>x.id)).size!==16||gateIds.some(id=>!gates.some(x=>x.id===id&&x.status==='HARD_HOLD')))err.push('matrix:all-hard-hold-gates');
 const sources=m.sources||[],claims=m.claims||[];
 const ids=sources.map(x=>x.id),cids=claims.map(x=>x.id);
 if(sources.length!==17||new Set(ids).size!==17||sources.some(x=>!/^https:\/\//.test(x.url)))err.push('matrix:sources');
 if(claims.length!==23||new Set(cids).size!==23||cids.some(id=>!(id in locked))||Object.keys(locked).some(id=>!cids.includes(id)))err.push('matrix:complete-claim-identities');
 for(const c of claims){
  if(!c.statement||!c.limit||c.status!==locked[c.id])err.push('claim:'+c.id+':status-or-text');
  if(!Array.isArray(c.source_ids)||!c.source_ids.length||c.source_ids.some(id=>!ids.includes(id)))err.push('claim:'+c.id+':source');
 }
 const c=id=>claims.find(x=>x.id===id);
 if(!/twelve minutes equals an hour/i.test(c('Z06')?.statement||''))err.push('matrix:unsupported-Z06-identity');
 if(!/public affiliate website or seller catalog proves no publisher-specific acceptance/i.test(c('A01')?.statement||''))err.push('matrix:affiliate-not-approved-identity');
 if(!/per thousand qualified-human sessions/i.test(c('A06')?.statement||''))err.push('matrix:net-kpi');
 if(!/37\.9% lower chance/.test(d.oldArticle)||/This is a relative chance statement|relative-risk interpretation/.test(d.oldArticle))err.push('inherited:R223-statistical-overinterpretation');
 if(!/pooled practitioners and novices/.test(d.oldMatrix.claims.find(x=>x.id==='C28')?.statement||'')||!/C37:'public_affiliate_portal_not_publisher_permission'/.test(d.oldValidator))err.push('inherited:R224-claim-lock');
 if(!/between-group|across practitioners and novices|practitioners and novices together/.test(d.oldReview)||!/21 studies at high risk of bias/.test(d.oldReview))err.push('inherited:R224-review-corrections');
 if(d.article.split(/\s+/).length<2000||!/2006/.test(d.article)||!/without a hypnotic induction/.test(d.article)||!/UNPUBLISHED_RESEARCH_DRAFT/.test(d.article))err.push('article:substantive-original-research');
 if(!/UNPUBLISHED|unpublished/i.test(d.plan)||!/NOT COMPUTABLE/.test(d.plan)||!/ZERO OR NEGATIVE/.test(d.plan))err.push('plan:honest-revenue');
 if(!/SV9m07PFTYk/.test(d.plan)||!/utm_content/.test(d.plan)||!/merchant_confirmed_paid_sale/.test(d.plan))err.push('plan:creator-funnel');
 return [...new Set(err)];
}
const clone=d=>JSON.parse(JSON.stringify(d));
const mutations=[
 ['enabled first button',x=>{x.a=x.a.replace(/ disabled aria-disabled="true"/,' aria-disabled="false"');}],
 ['enabled second button',x=>{x.a=x.a.replace('</div>\n<h2 id="reading">','<button>Buy today</button></div>\n<h2 id="reading">');}],
 ['remove offer disclosure',x=>{x.b=x.b.replace('Affiliate disclosure:','Commercial note:');}],
 ['active seller link quoted',x=>{x.a+='<a href="https://zen12.com/hnp?affiliate=fake">Purchase</a>';}],
 ['active seller link unquoted',x=>{x.a+='<a href=https://zen12.com/hnp>Purchase</a>';}],
 ['inject tracking script',x=>{x.hub+='<script>gtag("event")</script>';}],
 ['insert signup form',x=>{x.hub+='<form><input name="email"></form>';}],
 ['add event handler',x=>{x.hub+='<a onclick="buy()">Buy</a>';}],
 ['remove robots',x=>{x.b=x.b.replace('content="noindex,nofollow"','content="index,follow"');}],
 ['alter A/B primary copy',x=>{x.b=x.b.replace('Can a recording make meditation simpler? Yes.','Guaranteed meditation gains.');}],
 ['fake B playable media',x=>{x.b+='<video controls autoplay></video>';}],
 ['mismatch captions',x=>{x.vtt=x.vtt.replace('A recording can make a daily routine simpler.','Audio cures every problem.');}],
 ['delete final caption',x=>{x.vtt=x.vtt.replace('Read the evidence first. You can try a quiet twelve-minute pause for free.','');}],
 ['rename partner gate',x=>{x.matrix.gates.find(g=>g.id==='named_publisher_approval').id='approved';}],
 ['approve email rights',x=>{x.matrix.gates.find(g=>g.id==='email_channel_permission').status='APPROVED';}],
 ['remove settled revenue gate',x=>{x.matrix.gates=x.matrix.gates.filter(g=>g.id!=='settled_revenue_and_qualified_human_data');}],
 ['fabricate affiliate permission claim',x=>{x.matrix.claims.find(c=>c.id==='A01').status='APPROVED';}],
 ['fabricate owned Mind SKU',x=>{x.matrix.claims.find(c=>c.id==='A03').status='VERIFIED';}],
 ['convert seller health claim to proof',x=>{x.matrix.claims.find(c=>c.id==='Z07').status='PROVEN';}],
 ['fabricate time-equivalence result',x=>{x.matrix.claims.find(c=>c.id==='Z06').status='independent_RCT';}],
 ['erase source provenance',x=>{x.matrix.claims.find(c=>c.id==='Z05').source_ids=[];}],
 ['inject fake source',x=>{x.matrix.claims.find(c=>c.id==='Z04').source_ids=['M999'];}],
 ['drop final claim',x=>{x.matrix.claims.pop();}],
 ['rename last claim',x=>{x.matrix.claims.find(c=>c.id==='X01').id='X01_release';}],
 ['tamper specific unsupported claim text',x=>{x.matrix.claims.find(c=>c.id==='Z06').statement='Clinically proven results in twelve minutes';}],
 ['rewrite acceptance as approved',x=>{x.matrix.claims.find(c=>c.id==='A01').statement='Final Vestige is an approved Inspire3 affiliate';}],
 ['corrupt QA correction C28',x=>{x.oldMatrix.claims.find(c=>c.id==='C28').statement='P3b change correlated only among retreat practitioners';}],
 ['remove C37 validator lock',x=>{x.oldValidator=x.oldValidator.replace("C37:'public_affiliate_portal_not_publisher_permission'",'');}],
 ['reintroduce invented relative chance statement',x=>{x.oldArticle+=' This is a relative chance statement';}],
 ['remove review bias caveat',x=>{x.oldReview=x.oldReview.replace('21 studies at high risk of bias','21 trials without risk concerns');}],
 ['invent paid revenue',x=>{x.plan=x.plan.replace('NOT COMPUTABLE','1000 USD PROFIT').replace('NOT COMPUTABLE','1000 USD PROFIT');}],
 ['erase actual creator ID',x=>{x.plan=x.plan.replace('SV9m07PFTYk','UNVERIFIED_NEW_ID');}],
];
function run(){
 const baseline=check(source);
 const rejects=mutations.map(([name,mutate])=>{let copy=clone(source);mutate(copy);return [name,check(copy)];});
 const escaped=rejects.filter(x=>x[1].length===0);
 console.log('Mind R225 SOURCE-ONLY BASELINE ERRORS:',baseline.length,baseline.join('|'));
 console.log('Mutation rejection:',rejects.length-escaped.length,'/',rejects.length);
 if(escaped.length)console.log('ESCAPED MUTATIONS:',escaped.map(x=>x[0]).join(', '));
 console.log('Not tested: native browser/WCAG/Lighthouse, CMS, video MP4/playback, actual partner checkout, paid transactions.');
 if(baseline.length||escaped.length)process.exitCode=1;
}
run();
module.exports={check,source,mutations};
