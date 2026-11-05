/* Final Vestige Mind R154 -- read-only source validation; Node 18+; no network, dependencies, payments or CMS writes.
 * Run from repository root: node mind/r154/test_mind_r154.cjs
 * Adversarial tests deliberately mutate IN-MEMORY copies only.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const dir = __dirname;
const load = file => fs.readFileSync(path.join(dir,file),'utf8');
const files = {
 article:load('meta-awareness-mind-wandering-investigation.md'),
 html:load('mind-archive-commercial-bridge-REVIEW-ONLY.html'),
 matrix:load('claims-authorization-revenue-gates.json'),
 plan:load('one-offer-creator-conversion-acceptance.md')
};
let count=0;let mutations=0;
function eq(ok,msg){if(!ok)throw Error('FAILED: '+msg);count++}
function audit(d){
 const problems=[];const check=(ok,msg)=>{if(!ok)problems.push(msg)};
 let j;
 try{j=JSON.parse(d.matrix)}catch(e){return ['matrix malformed JSON']}
 const h=d.html,md=d.article,plan=d.plan;
 const rawButton=h.match(/<button\b[^>]*>/i);
 check(Boolean(rawButton && /\sdisabled(?:\s|>|=)/i.test(rawButton[0])),'merchant control must be HTML-disabled');
 check(/data-commercial-approved="false"/.test(h),'merchant approval must be false');
 check(/data-release="HARD_HOLD"/.test(h),'commercial release must be hard-hold');
 const buyer=h.indexOf('class="buyer"'),disc=h.indexOf('class="disclosure"'),btn=h.indexOf('<button');
 check(buyer>=0&&disc>buyer&&btn>disc&&btn-disc<1000,'plain earning disclosure must be adjacent and before button');
 check(/If you purchase through a future authorized link, Final Vestige may earn a commission/.test(h),'plain meaningful earning disclosure');
 check(/href="https:\/\/finalvestige\.com\/focus\/"/.test(h),'existing Focus CTA required');
 check(!/<form\b/i.test(h),'no replacement signup form');
 check(!/<script\b/i.test(h),'no scripts or duplicate analytics');
 check(!/<iframe\b/i.test(h),'no autoplay embed or third party iframe');
 check(!/href="[^"]*(?:affiliates\.inspire3|\/track\?|\/click\?|affiliate_id=)/i.test(h),'no active earning outbound');
 check(!/<a[^>]+(?:buy|purchase|checkout)[^>]*href=/i.test(h),'no merchant purchase anchor');
 check(/max-width:690px/.test(h),'mobile layout breakpoint');
 check(/:focus-visible/.test(h),'visible keyboard focus styles');
 check(/prefers-reduced-motion/.test(h),'reduced motion support');
 check(/data-video-status="STORYBOARD_ONLY"/.test(h),'no claim playable film');
 check(!/<video\b[^>]*autoplay/i.test(h),'no forced video playback');
 check(/<details>/.test(h),'native no-JS disclosure detail');
 check(!/required\s*=\s*["']?true/i.test(h),'no mandatory sign-up element');
 check(md.split(/\s+/).length>=1800,'substantive original investigation minimum');
 check(md.includes('https://pubmed.ncbi.nlm.nih.gov/17874601/'),'meta-awareness primary source');
 check(md.includes('https://pubmed.ncbi.nlm.nih.gov/23538911/'),'mindfulness trial primary source');
 check(md.includes('https://doi.org/10.1146/annurev-psych-010814-015331'),'review source');
 check(md.includes('https://finalvestige.com/focus/'),'native Focus fieldbook only');
 check(/no affiliate earning link/i.test(md),'editorial no earning link');
 check(/seller descriptions and seller outcome claims/i.test(md),'seller claims clearly separated');
 check(!/guarantee(?:d|s)? (?:mental|clinical|financial|productivity|wealth) (?:benefits|returns|results)/i.test(md),'no commercial guarantees');
 check(Array.isArray(j.claims)&&j.claims.length>=25,'claim matrix breadth');
 check(Array.isArray(j.release_gates)&&j.release_gates.length>=30,'release matrix breadth');
 check(j.release_gates.every(g=>g.status==='CLOSED'),'all release gates must be closed');
 check(j.eligible_for_affiliate_activation===false,'affiliate activation hard hold');
 check(j.eligible_for_publication===false,'publication hard hold');
 check(j.net_revenue_per_1000_qualified_sessions===null,'unknown KPI must be null not zero or fabricated');
 check(j.affiliate_commissions_settled===null,'no fake commissions');
 check(j.paid_attributable_orders===null,'no fake orders');
 check(j.claims.every(c=>/^https:\/\//.test(c.source)),'all claims must map to source URLs');
 check(j.claims.some(c=>c.disposition==='REJECT_SELLER_CLAIM'),'seller benefit rejected');
 check(j.claims.some(c=>c.disposition==='UNKNOWN_HARD_HOLD'),'approval missing');
 check(plan.includes('utm_content=REAL_GROK_ASSET_ID'),'no invented Grok asset ID');
 check(plan.includes('merchant_confirmed_purchase'),'purchase event separate from affiliate outbound');
 check(plan.includes('settled_net_revenue'),'settlement tracked separately');
 check(plan.includes('NOT COMPUTABLE'),'truthful missing KPI');
 check(/A\/B — text-only vs optional video/.test(plan),'preserve controlled video experiment');
 check(plan.includes('360/390/768/1440'),'mobile acceptance contract');
 check(!/PIXEL_ID=[0-9]+|GROK_MEDIA_ID=[0-9]+/.test(plan),'no invented media identifiers');
 return problems;
}
const defects=audit(files);
eq(defects.length===0,'exact source audit: '+defects.join('; '));
const matrix=JSON.parse(files.matrix);
eq(matrix.claims.length>=25,'25+ source claim decisions');
eq(matrix.release_gates.length>=30,'30+ hard release gates');
eq(matrix.source_urls.s09==='https://hypnosislive.com/mental-skills/total-focus','exact merchant URL');
eq(matrix.source_urls.s12.includes('ftcs-endorsement-guides'),'FTC disclosure reference');
eq(files.html.includes('aria-describedby="m154-hold"'),'disabled button explanation accessible');
eq(files.article.includes('The word you missed is still there.'),'original ending retained');
eq(files.plan.includes('no-JS'),'no-JS commercial plan');
eq(files.plan.includes('refund'),'refund handling');
eq(files.plan.includes('No automated inference'),'no fabricated downstream purchase inferred');
eq(/This independent investigation does \*\*not\*\* endorse a paid product/.test(load('../r153/unfinished-task-attention-residue-investigation.md')),'QA correction to inherited R153 present');
const adversarial=[
 ['enable purchase button',d=>{d.html=d.html.replace('type="button" disabled','type="button"')}],
 ['assert affiliate approval',d=>{d.html=d.html.replace('data-commercial-approved="false"','data-commercial-approved="true"')}],
 ['remove proximate disclosure',d=>{d.html=d.html.replace('class="disclosure"','class="undeclared"')}],
 ['erase plain compensation warning',d=>{d.html=d.html.replace('If you purchase through a future authorized link, Final Vestige may earn a commission','Click here for more information')}],
 ['inject analytics script',d=>{d.html+='<script src="https://vendor.invalid/m.js"></script>'}],
 ['inject competing signup',d=>{d.html+='<form action="/signup"><input></form>'}],
 ['inject iframe tracking',d=>{d.html+='<iframe src="https://vendor.invalid"></iframe>'}],
 ['activate affiliate earning anchor',d=>{d.html+='<a href="https://affiliates.inspire3.com/track?affid=fake">Buy</a>'}],
 ['open commercial gate',d=>{const x=JSON.parse(d.matrix);x.release_gates[0].status='OPEN';d.matrix=JSON.stringify(x)}],
 ['fabricate affiliate readiness',d=>{const x=JSON.parse(d.matrix);x.eligible_for_affiliate_activation=true;d.matrix=JSON.stringify(x)}],
 ['fabricate revenue',d=>{const x=JSON.parse(d.matrix);x.net_revenue_per_1000_qualified_sessions=999;d.matrix=JSON.stringify(x)}],
 ['remove required Focus route',d=>{d.html=d.html.replace('href="https://finalvestige.com/focus/"','href="#nowhere"')}],
 ['replace study source',d=>{d.article=d.article.replace('https://pubmed.ncbi.nlm.nih.gov/23538911/','[missing study]')}],
 ['fabricate Grok media ID',d=>{d.plan+='\nGROK_MEDIA_ID=23456789'}],
 ['corrupt claims JSON',d=>{d.matrix='{'}]
];
for(const [name,mutator] of adversarial){const v={...files};mutator(v);const hits=audit(v);if(hits.length===0)throw Error('Mutation escaped: '+name);mutations++}
console.log('Mind R154 read-only structural checks PASS: '+count+' assertions; adversarial unsafe modifications caught: '+mutations+'/'+adversarial.length+'.');
console.log('Release remains CLOSED; no browser, CI, seller checkout or paid-order verification performed.');
