// FV Mind R211 — source-controlled science/commercial/a11y guardrails.
// Native: node mind/r211/test_mind_r211.cjs
// No network access or external packages. Static assertions; NOT browser/WP/checkout/clinical review.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const names = {
  article:'mind/r211/the-twenty-knots-coue-autosuggestion-UNPUBLISHED.md',
  guide:'mind/r211/before-you-buy-focus-audio-ZEN12-VS-TOTAL-FOCUS-UNPUBLISHED.md',
  hub:'mind/r211/mind-archive-FOUR-STREAM-COUE-WP-PREVIEW-UNPUBLISHED.html',
  matrix:'mind/r211/COUE-ZEN12-TOTAL-FOCUS-CLAIM-PROOF-COMMERCE-GATES.json',
  plan:'mind/r211/OFFER-FIRST-CREATOR-FIT-PRIVACY-REVENUE-AB-ACCEPTANCE.md',
  r210article:'mind/r210/the-page-you-never-read-MIND-WANDERING-UNPUBLISHED.md',
  a:'mind/r210/zen12-mindless-reading-A-TEXT-UNPUBLISHED.html',
  b:'mind/r210/zen12-mindless-reading-B-OPTIONAL-42S-UNPUBLISHED.html',
  r210matrix:'mind/r210/CLAIM-SOURCE-OFFER-AUTHORIZATION-REVENUE-MATRIX.json'
};
function validate(f){
 const errors=[], check=(condition,label)=>{if(!condition)errors.push(label);};
 const j=(()=>{try{return JSON.parse(f.matrix)}catch{return {}}})();
 const prev=(()=>{try{return JSON.parse(f.r210matrix)}catch{return {}}})();
 check(f.article.trim().split(/\s+/).length>=2200,'Coué investigation >=2200 words');
 check(f.guide.trim().split(/\s+/).length>=1600,'buyer guide >=1600 words');
 for(const uri of ['https://www.gutenberg.org/files/27203/27203-h/27203-h.htm','https://pubmed.ncbi.nlm.nih.gov/19493324/','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/']){
   check(f.article.includes(uri),'primary article reference '+uri);
 }
 check(/UNPUBLISHED/.test(f.article)&&/not product-specific evidence|not product-specific proof|not product-specific|not proof of|not evidence for/.test(f.article),'history and commerce separated');
 check(f.guide.includes('https://hypnosislive.com/mental-skills/total-focus')&&f.guide.includes('https://hypnosislive.com/faq'),'exact item plus FAQ');
 check(f.guide.includes('maximum of five sessions per year')&&f.guide.includes('14-day'),'refund limit adjacent in guide');
 check(f.guide.includes('not purchased, listened')&&f.guide.includes('an authenticated Inspire3 publisher authorization')&&f.guide.includes('No earning link'),'non testimonial and gated sales');
 check(f.guide.includes('https://zen12.com/hnp')&&f.guide.includes('48 MP3'),'actual merchant offer not invented');
 check(f.hub.includes('UNPUBLISHED')&&f.hub.includes('href="https://finalvestige.com/focus/"'),'hub source-only with Focus');
 check(f.hub.includes('No subscriber is counted here'),'hub does not invent a confirmed lead');
 check(['stream-perception','stream-history','stream-practice','stream-tools'].every(x=>f.hub.includes('id="'+x+'"')),'four streams present');
 check(/<svg[\s\S]*?<title[\s\S]*?<desc/.test(f.hub),'original accessible SVG title description');
 check(/@media\(max-width:820px\)/.test(f.hub) && /prefers-reduced-motion/.test(f.hub),'responsive and reduced motion stylesheet');
 for(const key of ['hub','a','b']){
  const h=f[key];const discId=key==='hub'?'comm-disclose':'commDisclosure';
  const discPos=h.indexOf('id="'+discId+'"'),buttonPos=h.lastIndexOf('<button');
  check(discPos>=0 && buttonPos>discPos && buttonPos-discPos<950,'immediately adjacent disclosure '+key);
  check((h.match(/<button[^>]*\bdisabled\b/g)||[]).length===1,'native disabled CTA '+key);
  check(h.includes('Final Vestige may earn a commission'),'near-CTA truthful commission '+key);
  check(!/<script\b|<form\b|<iframe\b|<video\b|<audio\b|autoplay\s*=|<link\b/i.test(h),'no scripts forms videos autoplay or remote styles '+key);
  check(!/href="https:\/\/(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com|www\.awin1\.com)/i.test(h),'no merchant or earning outbound link '+key);
 }
 const normalizeB=f.b.replace(/<section class="film"[\s\S]*?<\/section>/,'').replace('EXPERIMENT B','EXPERIMENT A').replace('The video is a proposed storyboard/transcript only.','No video is present in this variant.');
 check(f.b.includes('Optional 42-second story concept') && f.b.includes('<details>') && !f.a.includes('<section class="film"'),'B optional media concept only');
 check(normalizeB===f.a,'identical A/B core except optional film and variant label');
 check(f.r210article.includes('Hayley A. Rahl')&&f.r210article.includes('**142 participants')&&f.r210article.includes('**four undergraduate readers**'),'independent R210 reviewer corrections included');
 check(f.r210article.includes('p = .19')&&f.r210article.includes('SART')&&f.r210article.includes('not statistically significant'),'Rahl and experience sampling results accurate');
 check(f.a.includes('142 analyzed')&&f.b.includes('142 analyzed')&&f.a.includes('behavioral go/no-go discrimination')&&f.b.includes('behavioral go/no-go discrimination'),'buyer variants incorporate Rahl correction');
 check((prev.claims||[]).find(c=>c.id==='C05')?.statement.includes('Rahl') &&
       (prev.claims||[]).find(c=>c.id==='C06')?.caveat.includes('acceptance-only'),'inherited R210 matrix corrected');
 check((prev.claims||[]).find(c=>c.id==='C13')?.caveat.includes('unresolved')===false,'avoid unsupported price fluctuation causality');
 check((j.source_refs||[]).length===18 && (j.claims||[]).length===26 && (j.gates||[]).length===16,'matrix source claim gate counts');
 check((j.gates||[]).every(g=>g.status==='OPEN'),'no false gate clearance');
 check(j.public_commerce_activation===false && j.commercial_link==='NONE_ACTIVE' && j.release==='HARD_HOLD','affiliate hard hold');
 check((j.claims||[]).find(c=>c.id==='C18')?.statement.includes('five sessions'),'Total Focus refund caveat in machine source');
 check((j.claims||[]).find(c=>c.id==='C13')?.status==='PRODUCT_SPECIFIC_PROOF_ABSENT_EXCLUDE','no unsupported Zen12 benefit');
 check((j.claims||[]).find(c=>c.id==='C20')?.status==='UNVERIFIED_HARD_HOLD','no invented partner approval');
 check(j.measurement_contract?.kpi_current==='NOT_COMPUTABLE' && j.measurement_contract?.click_not_sale===true && j.measurement_contract?.lead_not_sale===true,'truthful paid conversion measurement');
 check((j.measurement_contract?.cohorts_days||[]).join('/')==='7/30','cohorts defined');
 check(f.plan.includes('TASK-008')&&f.plan.includes('qualified_human_session')&&f.plan.includes('NOT COMPUTABLE'),'creator-to-revenue acceptance complete');
 check(f.plan.includes('no fingerprinting')&&f.plan.includes('No name, email')===false,'privacy safe');
 check(!/https?:\/\/(?:www\.)?(?:awin1\.com|clickbank\.net)\/[^\s\"]+/.test(f.guide),'no fabricated earning URL');
 return errors;
}
function loadLocal(){
 const root=path.resolve(__dirname,'../..'), f={};
 for(const [key,file] of Object.entries(names))f[key]=fs.readFileSync(path.join(root,file),'utf8');
 return f;
}
function mutationSuite(origin){
 const cases=[
 ['activate R210 A',x=>x.a=x.a.replace('<button type="button" disabled','<button type="button"')],
 ['activate R210 B',x=>x.b=x.b.replace('<button type="button" disabled','<button type="button"')],
 ['activate R211 hub',x=>x.hub=x.hub.replace('<button type="button" disabled','<button type="button"')],
 ['strip disclosure hub',x=>x.hub=x.hub.replace('Final Vestige may earn a commission','Reader may be compensated')],
 ['strip disclosure A',x=>x.a=x.a.replace('Final Vestige may earn a commission','Official deal guaranteed')],
 ['strip disclosure B',x=>x.b=x.b.replace('Final Vestige may earn a commission','Official deal guaranteed')],
 ['insert affiliate offer A',x=>x.a+='\n<a href="https://zen12.com/hnp">Buy now</a>'],
 ['insert tracking script B',x=>x.b+='\n<script src="https://analytics.example.test/x.js"></script>'],
 ['duplicate Focus form',x=>x.hub+='\n<form><input name="email"/></form>'],
 ['remove SVG accessible title',x=>x.hub=x.hub.replace('<title id="knot-title">','<p id="knot-title">')],
 ['erase refund limitation',x=>x.guide=x.guide.replace('maximum of five sessions per year','unlimited refunds')],
 ['assert seller proof',x=>{const j=JSON.parse(x.matrix);j.claims.find(c=>c.id==='C13').status='PROVEN';x.matrix=JSON.stringify(j)}],
 ['invent partner approval',x=>{const j=JSON.parse(x.matrix);j.claims.find(c=>c.id==='C20').status='APPROVED';x.matrix=JSON.stringify(j)}],
 ['turn affiliate activation on',x=>{const j=JSON.parse(x.matrix);j.public_commerce_activation=true;x.matrix=JSON.stringify(j)}],
 ['invent sales KPI',x=>{const j=JSON.parse(x.matrix);j.measurement_contract.kpi_current=199.99;x.matrix=JSON.stringify(j)}],
 ['introduce second paid signup',x=>x.hub=x.hub.replace('No subscriber is counted here','A subscriber is confirmed here')],
 ['omit human source / conversion plan',x=>x.plan=x.plan.replace('qualified_human_session','impression_only')],
 ['erase first-author correction',x=>x.r210article=x.r210article.replace('Hayley A. Rahl','Emily Lindsay')],
 ['deny N4 research',x=>x.r210article=x.r210article.replace('**four undergraduate readers**','**four hundred readers**')]
 ];
 let rejected=0;const misses=[];
 for(const [label,mutate] of cases){
  const v={...origin};mutate(v);if(validate(v).length>0)rejected++;else misses.push(label);
 }
 return {attempted:cases.length,rejected,misses};
}
if(require.main===module){
 const f=loadLocal(),errors=validate(f),mutations=mutationSuite(f);
 console.log(JSON.stringify({status:!errors.length&&!mutations.misses.length?'PASS':'FAIL',assertions:errors,mutations},null,2));
 if(errors.length || mutations.misses.length)process.exitCode=1;
}
module.exports={names,validate,mutationSuite};
