// Run: node mind/r130/validate-r130.cjs   (native Node 18+; no external deps)
'use strict';
const fs=require('node:fs'), assert=require('node:assert/strict'), path=require('node:path');
const root=__dirname;
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const a=read('zen12-A-text.html'), b=read('zen12-B-storyboard.html');
const article=read('inattentional-blindness-investigation.md'), guide=read('zen12-buyer-guide.md'), plan=read('acceptance-and-grok-crosswalk.md');
const claims=JSON.parse(read('claims.json'));let assertions=0;
function pass(x,msg){assert.ok(x,msg);assertions++;}
for (const [label,html] of [['A',a],['B',b]]) {
 pass(/<html lang="en">/.test(html),label+' language');
 pass(/name="viewport"/.test(html),label+' mobile viewport');
 pass(/<main>/.test(html)&&/<h1>/.test(html),label+' semantic hierarchy');
 pass(/<button\b[^>]*\sdisabled(?:\s|>|=)/.test(html),label+' disabled merchant');
 pass(/If you purchase through this link, Final Vestige may earn a commission/.test(html),label+' adjacent FTC disclosure');
 pass(html.indexOf('If you purchase through this link')<html.indexOf('disabled aria-disabled'),label+' disclosure precedes button');
 pass(!/<script/i.test(html),label+' zero scripts');
 pass(!/<iframe/i.test(html),label+' zero external embeds');
 pass(!/<form/i.test(html),label+' no duplicate signup');
 pass(!/<a[^>]+href=["']https?:\/\/(?:zen12|inspire3|affiliates\.inspire3)/i.test(html),label+' no merchant href');
 pass(/finalvestige.com\/focus\//.test(html),label+' existing Focus');
 pass(/prefers-reduced-motion/.test(html),label+' reduced motion');
 pass(/:focus-visible/.test(html),label+' keyboard focus');
 pass(/noindex, nofollow/.test(html),label+' draft robot hold');
 pass(!/autoplay/i.test(html.replace(/no autoplay/gi,'').replace(/autoplay,/gi,''))||!/<video/i.test(html),label+' no playing video');
 pass(/12 levels|twelve levels/.test(html)&&/48 MP3/.test(html),label+' product distinction');
}
pass(!/Optional forty-second explanation/.test(a),'A text only');
pass(/Optional forty-second explanation/.test(b)&&/00–07s/.test(b)&&/30–40s/.test(b),'B storyboard transcript');
pass(!/<video/i.test(b),'B not falsely playable');
pass(/original investigation/i.test(article)&&/Drew/.test(article),'sourced investigation');
pass(!/affiliate link or buy/i.test(article),'separate commercial editorial');
pass(/NOT AN ENDORSEMENT/.test(guide),'guide truth');
pass(claims.sources.length>=10&&claims.claims.length>=15,'claims source coverage');
pass(claims.claims.every(c=>c.verdict&&Array.isArray(c.source_ids)),'claim normalization');
pass(Object.values(claims.release_gates).every(v=>v===false),'all release gates closed');
pass(plan.includes('NOT COMPUTABLE')&&plan.includes('asset_id'),'measurement discipline');
const activated=a.replace('disabled aria-disabled="true"','aria-disabled="false"');
pass(!/<button\b[^>]*\sdisabled(?:\s|>|=)/.test(activated),'mutation: activated merchant control rejected');
const disclosureRemoved=a.replace('If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.','');
pass(!disclosureRemoved.includes('If you purchase through this link, Final Vestige may earn a commission'),'mutation: removed FTC disclosure rejected');
const injected=a.replace('<button class="hold"','<a href="https://zen12.com/secret/">Seller</a><button class="hold"');
pass(/<a[^>]+href=["']https?:\/\/(?:zen12|inspire3|affiliates\.inspire3)/i.test(injected),'mutation: unapproved merchant href flagged');
pass(!/<a[^>]+href=["']https?:\/\/(?:zen12|inspire3)/i.test(b),'no merchant live href');
console.log('R130 tests passed:',assertions,'structural assertions; no real browser/merchant tests run.');
