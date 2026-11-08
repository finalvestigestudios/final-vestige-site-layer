// FV Mind R213 independent source-regression and mutation tests.
// Run from a complete repository checkout: node mind/r213/test_mind_r213.cjs
// No network, API keys, packages, analytics scripts, WordPress or merchant calls.
'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..');
const files={
 article:'mind/r213/the-voice-not-in-the-recording-MCGURK-UNPUBLISHED.md',
 hub:'mind/r213/mind-archive-MCGURK-FOUR-STREAM-WP-PREVIEW-UNPUBLISHED.html',
 matrix:'mind/r213/MCGURK-ZEN12-CLAIMS-OFFER-AUTHORIZATION.json',
 plan:'mind/r213/OFFER-FIRST-THREE-CREATOR-FITS-AB-REVENUE-ACCEPTANCE.md',
 previous:'mind/r212/the-glass-no-one-saw-MISINFORMATION-EFFECT-UNPUBLISHED.md',
 previousMatrix:'mind/r212/MISINFORMATION-ZEN12-SOURCE-CLAIM-COMMERCE-MATRIX.json',
 variantA:'mind/r210/zen12-mindless-reading-A-TEXT-UNPUBLISHED.html',
 variantB:'mind/r210/zen12-mindless-reading-B-OPTIONAL-42S-UNPUBLISHED.html'
};
function validate(f){
 const errors=[],check=(condition,message)=>{if(!condition)errors.push(message)};
 let m={},old={};try{m=JSON.parse(f.matrix)}catch{errors.push('matrix parses')};try{old=JSON.parse(f.previousMatrix)}catch{errors.push('previous matrix parses')};
 const a=f.article||'',h=f.hub||'',p=f.plan||'',vA=f.variantA||'',vB=f.variantB||'',prev=f.previous||'';
 check(a.split(/\s+/).length>=2600,'original investigation >=2600 words');
 check(/McGurk.*MacDonald/i.test(a)&&a.includes('UNPUBLISHED'),'original identity and unpublished');
 for(const u of ['https://doi.org/10.1038/264746a0','https://pubmed.ncbi.nlm.nih.gov/25802068/','https://doi.org/10.1371/journal.pone.0207160','https://pmc.ncbi.nlm.nih.gov/articles/PMC9894660/','https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance'])
   check(a.includes(u),'primary source '+u);
 check(/not a clinical guide|not a clinical|not a diagnostic/i.test(a),'nonclinical boundaries in investigation');
 check(!/href=["']https?:\/\/(?:www\.)?(?:awin1\.com|clickbank\.net)/i.test(a),'no earning URL in article');
 check(/id="mind-archive-r213"/.test(h),'hub labelled');
 for(const id of ['mind-perception','mind-history','mind-practice','mind-tools'])check(h.includes('id="'+id+'"'),'four stream '+id);
 check(/<button\b[^>]*\bdisabled\b/.test(h),'hub CTA natively disabled');
 check(/id="r213-disclosure"/.test(h)&&/aria-describedby="r213-disclosure r213-unavailable"/.test(h),'affiliate disclosure linked to CTA');
 check(/may earn a commission/.test(h),'adjacent plain-English commission disclosure');
 const buttonAt=h.indexOf('<button');check(buttonAt>0 && h.lastIndexOf('may earn a commission',buttonAt)>buttonAt-950,'disclosure immediately adjacent before button');
 check(!/<(?:script|form|iframe|video|audio)\b/i.test(h),'no scripts, duplicate forms, remote embeds or autoplay');
 check(!/href=["']https?:\/\/(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)/i.test(h),'no live merchant links');
 check(h.includes('prefers-reduced-motion')&&h.includes(':focus-visible')&&h.includes('@media(max-width:420px)'),'accessible/reduced-motion/mobile CSS');
 check(h.includes('role="img"')&&h.includes('aria-label=')&&h.includes('<figcaption>'),'original diagram is described');
 check(h.includes('https://finalvestige.com/focus/')&&h.includes('UNPUBLISHED'),'existing free pathway and draft caveat');
 check(h.includes('R185')&&h.includes('noncanonical')===false || h.includes('R185'),'mentions editorial dedup'); // explicit R185
 check(m.schema==='fv-mind-r213/claims-authorization-2026-11-08','R213 schema');
 check(m.commercial_activated===false && m.affiliate_url===null,'zero commercial activation');
 check((m.source_registry||[]).length>=20 && (m.claims||[]).length>=30 && (m.release_gates||[]).length>=15,'source/claims/gate evidence coverage');
 check((m.claims||[]).some(x=>x.id==='P10'&&/EXCLUDE/.test(x.status)),'strong merchant outcome excluded');
 check((m.claims||[]).some(x=>x.id==='P13'&&/CONFLICTING/.test(x.status)),'public price discrepancy disclosed');
 check((m.release_gates||[]).every(x=>x.status==='OPEN'),'release remains gated');
 check(m.measurement?.current_kpi==='NOT_COMPUTABLE_NOT_ZERO','no invented revenue metric');
 check(m.verification_notes?.some(x=>x.includes('zero qualifying messages')),'bounded authorization check not claimed exhaustive');
 check(!m.source_registry.some(x=>!/^https:\/\//.test(x.url)),'all source registry URLs real https');
 check(p.includes('OFFER')||p.includes('Offer-first'),'offer-first plan');
 for(const term of ['R185','R200','R212','R210','TASK-008','qualified-human','refund','chargeback','UNPUBLISHED','NOT COMPUTABLE'])check(p.toLowerCase().includes(term.toLowerCase()),'plan includes '+term);
 check(/no direct|no raw IP|no raw email/i.test(p),'privacy contract');
 check(/42-second|42 second|42s/i.test(p),'optional 42sec video hypothesis');
 check(/HARD HOLD/.test(p),'no release');
 check(prev.toLowerCase().includes('forty-five')&&prev.includes('16 of 50')&&prev.includes('7 of 50')&&prev.includes('6 of 50'),'corrected 1974 full primary methods');
 check(prev.includes('N=129')&&prev.includes('N=195')&&prev.includes('75%')&&prev.includes('41%'),'corrected 1978 primary conditions');
 check(prev.includes('first')&&prev.includes('own words')&&prev.includes('NONCANONICAL'),'initial free account and duplicate status');
 check(old.source_refs?.filter(x=>x.url==='UNVERIFIED').length===2,'old matrix 2 placeholders');
 check(old.source_refs?.filter(x=>x.url!=='UNVERIFIED').length===18,'old matrix 18 linked sources');
 check(old.claims?.find(x=>x.id==='C18')?.status==='CONFLICTING_SELLER_PUBLIC_DISPLAY','old matrix price caveat corrected');
 for(const [k,v] of [['A',vA],['B',vB]]){
   check(/<button\b[^>]*\bdisabled\b/i.test(v),'R210 '+k+' CTA still disabled');
   check(/may earn a commission/i.test(v),'R210 '+k+' near-link disclosure');
   check(!/<(?:script|form|iframe)\b/i.test(v),'R210 '+k+' no additional tracking/forms/embed');
   check(!/href=["']https?:\/\/(?:zen12\.com|affiliates\.inspire3\.com)/i.test(v),'R210 '+k+' no unauthorized merchant link');
   check(/A public sales-page price is not a verified checkout price/.test(v),'R210 '+k+' pricing caveat retained');
 }
 check(/42-second|42 second|42s/.test(vB),'R210 B retains optional film distinction');
 return errors;
}
const baseline={};
for(const [key,file] of Object.entries(files))baseline[key]=fs.readFileSync(path.join(root,file),'utf8');
const failures=validate(baseline);
if(failures.length)throw Error('R213 baseline failed:\n- '+failures.join('\n- '));
const cases=[
 ['activate hub buy button','hub',x=>x.replace('type="button" disabled','type="button"')],
 ['remove nearby disclosure','hub',x=>x.replace('may earn a commission','might earn nothing')],
 ['inject marketing tracker','hub',x=>x.replace('</section>','<script src="https://external.example/pixel.js"></script></section>')],
 ['add duplicate email capture','hub',x=>x.replace('</section>','<form><input type="email"></form></section>')],
 ['add unauthorized affiliate URL','hub',x=>x.replace('</section>','<a href="https://zen12.com/hnp">Buy</a></section>')],
 ['break four-stream archive','hub',x=>x.replace('id="mind-history"','id="removed-history"')],
 ['remove image description','hub',x=>x.replace('role="img"','role="none"')],
 ['erase scientific primary source','article',x=>x.replaceAll('https://doi.org/10.1038/264746a0','REMOVED')],
 ['remove nonclinical boundary','article',x=>x.replaceAll('not a clinical guide','unrestricted clinical guidance')],
 ['activate account in matrix','matrix',x=>x.replace('"commercial_activated": false','"commercial_activated": true')],
 ['add fabricated affiliate URL','matrix',x=>x.replace('"affiliate_url": null','"affiliate_url": "https://pretend.invalid/123"')],
 ['invent conversion','matrix',x=>x.replace('"current_kpi": "NOT_COMPUTABLE_NOT_ZERO"','"current_kpi": "REVENUE_PROVEN"')],
 ['remove campaign map','plan',x=>x.replaceAll('TASK-008','UNRECONCILED_QUEUE')],
 ['remove film test requirement','plan',x=>x.replace(/42[ -]?(?:second|sec|s)/gi,'UNDEFINED_DURATION')],
 ['restore false memory experiment','previous',x=>x.replace('forty-five students','Uncounted students')],
 ['undo 1978 recognition precision','previous',x=>x.replaceAll('75%','unverified proportion')],
 ['restore wrong currency','previousMatrix',x=>x.replace('CONFLICTING_SELLER_PUBLIC_DISPLAY','PUBLIC_DISPLAY_ONLY')],
 ['activate inherited A CTA','variantA',x=>x.replace(/(<button\b[^>]*?)\bdisabled\b/i,'$1')],
 ['activate inherited B CTA','variantB',x=>x.replace(/(<button\b[^>]*?)\bdisabled\b/i,'$1')]
];
let rejected=0;for(const [name,key,fn] of cases){const changed=fn(baseline[key]);if(changed===baseline[key])throw Error('TEST INVALID no source mutation: '+name);const mutant={...baseline,[key]:changed};const res=validate(mutant);if(!res.length)throw Error('UNSAFE MUTATION ESCAPED: '+name);rejected++}
console.log('R213 BASELINE PASS 0 failures; MUTATION REJECTIONS '+rejected+'/'+cases.length);
console.log('Source checks only. NOT browser WCAG, native WordPress, CI, playable video, checkout or paid revenue evidence.');
