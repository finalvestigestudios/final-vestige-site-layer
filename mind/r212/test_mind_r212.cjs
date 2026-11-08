// FV Mind R212 — deterministic source-safety tests; no packages, no network, no CMS.
// Native execution: node mind/r212/test_mind_r212.cjs
'use strict';
const fs=require('node:fs'),path=require('node:path');
const names={
 article:'mind/r212/the-glass-no-one-saw-MISINFORMATION-EFFECT-UNPUBLISHED.md',
 hub:'mind/r212/mind-archive-FOUR-STREAM-WP-SOURCE-PREVIEW-UNPUBLISHED.html',
 block:'mind/r212/disclosed-zen12-context-block-INACTIVE.html',
 matrix:'mind/r212/MISINFORMATION-ZEN12-SOURCE-CLAIM-COMMERCE-MATRIX.json',
 plan:'mind/r212/CONVERSION-RELEASE-EXPERIMENT-AND-CREATOR-FIT.md',
 corrected:'mind/r211/the-twenty-knots-coue-autosuggestion-UNPUBLISHED.md',
 correctedMatrix:'mind/r211/COUE-ZEN12-TOTAL-FOCUS-CLAIM-PROOF-COMMERCE-GATES.json',
 correctedTest:'mind/r211/test_mind_r211.cjs'
};
function validate(f) {
 const failures=[],ok=(v,message)=>{if(!v)failures.push(message);};
 let j={},old={};try{j=JSON.parse(f.matrix)}catch{failures.push('matrix valid JSON')}
 try{old=JSON.parse(f.correctedMatrix)}catch{failures.push('corrected matrix valid JSON')}
 ok((f.article||'').split(/\s+/).length>=2600,'new investigation >=2600 words');
 for(const url of [
 'https://doi.org/10.1016/S0022-5371(74)80011-3',
 'https://pubmed.ncbi.nlm.nih.gov/621467/',
 'https://doi.org/10.1101/lm.94705',
 'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/',
 'https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'])
   ok(f.article.includes(url),'article source '+url);
 ok(/UNPUBLISHED/.test(f.article)&&/no commercial recommendation/i.test(f.article),'investigation not endorsed/published');
 ok(f.article.includes('The film contained none.')&&f.article.includes('A mistaken answer is not proof'),'methodological boundary');
 ok(!/https?:\/\/(?:www\.)?(?:awin1\.com|clickbank\.net)\//i.test(f.article),'no earning URL in article');
 for(const x of ['hub','block']){
  const h=f[x]||'';
  ok(/<button[^>]*\bdisabled\b/i.test(h),'native disabled '+x);
  ok(/may earn a commission/i.test(h),'adjacent disclosure '+x);
  ok(!/<(?:script|form|iframe|video|audio)\b/i.test(h),'no scripts/forms/embeds '+x);
  ok(!/href=["']https?:\/\/(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)/i.test(h),'no merchant link '+x);
 }
 ok(/id="fv-mind-r212-disclosure"/.test(f.block)&&/aria-describedby="fv-mind-r212-disclosure"/.test(f.block),'block disclosure referenced correctly');
 ok(/id="comm-disclose"/.test(f.hub)&&/aria-describedby="comm-disclose"/.test(f.hub),'hub disclosure referenced correctly');
 ok(['stream-perception','stream-history','stream-practice','stream-tools'].every(x=>f.hub.includes('id="'+x+'"')),'four clear streams');
 ok(f.hub.includes('The Glass No One Saw')&&f.hub.includes('UNPUBLISHED')&&f.hub.includes('href="https://finalvestige.com/focus/"'),'hub links only published Focus, draft no invented URL');
 ok(f.hub.includes('prefers-reduced-motion')&&f.hub.includes('max-width:820px')===false&&f.hub.includes('max-width')===false,'media and style scoped'); // guard layout uses @media(max-width) not max-width property
 ok(j.schema==='fv-mind-r212/commercial-claims-v1'&&j.source_refs?.length===20&&j.claims?.length===30&&j.gates?.length===14,'claim/source/gate matrix complete');
 ok(j.gates?.every(x=>x.status==='OPEN'),'all merchant/release gates open');
 ok(j.public_affiliate_activation===false&&j.approved_earning_url===null&&j.account_specific_partner_acceptance==='UNVERIFIED','merchant locked');
 ok(j.measurement_contract?.no_direct_identity_tracking===true&&j.measurement_contract?.no_new_third_party_scripts===true&&j.measurement_contract?.no_duplicate_forms===true&&j.measurement_contract?.no_pii===true,'privacy flags fail closed');
 ok(j.measurement_contract?.paid_conversion_not_outbound_click===true&&j.measurement_contract?.kpi_current==='NOT_COMPUTABLE_NOT_ZERO','revenue not inferred from clicks');
 ok((j.measurement_contract?.cohorts||[]).join(',')==='7,30','7 and 30 day outcomes');
 ok((j.claims||[]).find(x=>x.id==='C15')?.status==='SELLER_EFFICACY_CLAIM_EXCLUDE','zen12 hour-equivalence excluded');
 ok((j.claims||[]).find(x=>x.id==='C21')?.status==='UNVERIFIED_HARD_HOLD','individual authorization not invented');
 ok(f.plan.includes('TASK-008')&&f.plan.includes('Grok retains')&&f.plan.includes('NOT COMPUTABLE')&&f.plan.includes('No name, email'),'creator and conversion data safeguards');
 ok(f.plan.includes('UNRENDERED')&&f.plan.includes('A text-only')&&f.plan.includes('30 paid orders'),'existing A/B experiment preserved, sample caution');
 ok(f.corrected.includes('## An eighteenth-century shadow: Puységur')&&f.corrected.includes('https://pubmed.ncbi.nlm.nih.gov/26301795/')&&f.corrected.includes('116 analyzed'),'Praxxis corrections applied');
 ok(old.measurement_contract?.direct_identity_tracking===false&&old.measurement_contract?.third_party_new_scripts===false,'old privacy flags correct');
 ok(old.source_refs?.some(s=>s.id==='P06')&&old.claims?.some(c=>c.id==='C27'),'old source ledger correction');
 ok(f.correctedTest.includes('enable identity tracking')&&f.correctedTest.includes('enable third-party scripts'),'old source tests fixed');
 return failures;
}
function mutationSuite(f){
 const changes=[
 ['enable CTA',x=>x.block=x.block.replace('<button type="button" disabled','<button type="button"')],
 ['strip block disclosure',x=>x.block=x.block.replace('may earn a commission','is not compensated')],
 ['strip hub disclosure',x=>x.hub=x.hub.replace('may earn a commission','is not compensated')],
 ['activate hub CTA',x=>x.hub=x.hub.replace('<button type="button" disabled','<button type="button"')],
 ['add merchant buying link',x=>x.block+='\n<a href="https://zen12.com/hnp">Buy</a>'],
 ['inject tracker',x=>x.hub+='\n<script src="https://tracker.invalid/t.js"></script>'],
 ['duplicate signup',x=>x.hub+='\n<form><input name="email"></form>'],
 ['delete anchor relationship',x=>x.block=x.block.replace('aria-describedby="fv-mind-r212-disclosure"','aria-describedby="missing"')],
 ['remove FTC source',x=>x.article=x.article.replace('https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance','missing_source')],
 ['remove primary 1978',x=>x.article=x.article.replace('https://pubmed.ncbi.nlm.nih.gov/621467/','missing_source')],
 ['invent approved affiliate',x=>{const a=JSON.parse(x.matrix);a.account_specific_partner_acceptance='APPROVED';x.matrix=JSON.stringify(a)}],
 ['activate affiliate',x=>{const a=JSON.parse(x.matrix);a.public_affiliate_activation=true;x.matrix=JSON.stringify(a)}],
 ['register active URL',x=>{const a=JSON.parse(x.matrix);a.approved_earning_url='https://fake.invalid';x.matrix=JSON.stringify(a)}],
 ['permit direct identity tracking',x=>{const a=JSON.parse(x.matrix);a.measurement_contract.no_direct_identity_tracking=false;x.matrix=JSON.stringify(a)}],
 ['permit third party script',x=>{const a=JSON.parse(x.matrix);a.measurement_contract.no_new_third_party_scripts=false;x.matrix=JSON.stringify(a)}],
 ['permit duplicate email form',x=>{const a=JSON.parse(x.matrix);a.measurement_contract.no_duplicate_forms=false;x.matrix=JSON.stringify(a)}],
 ['infer sale from click',x=>{const a=JSON.parse(x.matrix);a.measurement_contract.paid_conversion_not_outbound_click=false;x.matrix=JSON.stringify(a)}],
 ['fabricate net revenue',x=>{const a=JSON.parse(x.matrix);a.measurement_contract.kpi_current='$500';x.matrix=JSON.stringify(a)}],
 ['falsify efficacy',x=>{const a=JSON.parse(x.matrix);a.claims.find(z=>z.id==='C15').status='CLINICALLY_PROVEN';x.matrix=JSON.stringify(a)}],
 ['fake clearance',x=>{const a=JSON.parse(x.matrix);a.gates[0].status='PASSED';x.matrix=JSON.stringify(a)}],
 ['erase Coué correction',x=>x.corrected=x.corrected.replace('## An eighteenth-century shadow','## A nineteenth-century shadow')]
 ];
 const misses=[],pass=[];
 for(const [id,change] of changes){const v={...f};change(v);if(JSON.stringify(v)===JSON.stringify(f))misses.push('VACUOUS:'+id);else if(validate(v).length===0)misses.push('ESCAPED:'+id);else pass.push(id)}
 return {attempted:changes.length,rejected:pass.length,misses};
}
function loadLocal(){const root=path.resolve(__dirname,'../..'),files={};for(const [key,p] of Object.entries(names))files[key]=fs.readFileSync(path.join(root,p),'utf8');return files}
if(require.main===module){
 const f=loadLocal(),issues=validate(f),mutations=mutationSuite(f);
 console.log(JSON.stringify({result:issues.length||mutations.misses.length?'FAIL':'PASS',issues,mutations},null,2));
 if(issues.length||mutations.misses.length)process.exitCode=1;
}
module.exports={names,validate,mutationSuite};
