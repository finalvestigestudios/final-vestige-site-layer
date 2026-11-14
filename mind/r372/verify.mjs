import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root=new URL('.',import.meta.url);
const read=n=>readFileSync(new URL(n,root),'utf8');
const A=read('ZEN12_A_TEXT_EVIDENCE_GUIDE.html'),B=read('ZEN12_B_OPTIONAL_42S_EVIDENCE_GUIDE.html');
const hub=read('MIND_HUB_SOURCE_ONLY.html'),vtt=read('ORIGINAL_42S_CAPTIONS.vtt'),article=read('THE_SURGEON_WHO_REFUSED_THE_MAGNET.md'),spec=read('CONVERSION_ACCEPTANCE_AND_CREATOR_HANDOFF.md'),data=JSON.parse(read('CLAIM_SOURCE_AND_RELEASE_MATRIX.json'));
let n=0;
function check(condition,message){assert.ok(condition,message);n++}
for(const [name,html] of [['A',A],['B',B],['hub',hub]]){
check(html.includes('<meta name="robots" content="noindex,nofollow">'),name+':noindex');
check(html.includes('<a class="skip"'),name+':skip-link');
check(html.includes('prefers-reduced-motion'),name+':reduced-motion');
check(!/<script\b|<iframe\b|<form\b|on(?:click|load|submit)\s*=|<meta[^>]+http-equiv\s*=\s*["']refresh/i.test(html),name+':no scripting/form/iframe/redirect');
check(!/https?:\/\/(?:zen12\.com|affiliates\.inspire3\.com)(?:\/[^"']*)?["']/i.test(html),name+':no merchant anchor');
}
for(const [name,html] of [['A',A],['B',B]]){
check(/<button\b[^>]+\sdisabled(?=[\s>])/.test(html),name+':native-disabled');
check(html.indexOf('Affiliate disclosure:')>0 && html.indexOf('Affiliate disclosure:')<html.indexOf('<button class="merchant"'),name+':adjacent-disclosure');
check((html.match(/<button class="merchant"/g)||[]).length===1,name+':one-merchant-control');
check(html.includes('href="/focus/"'),name+':single-existing-focus-route');
check(!/\bautoplay\b\s*(?:=|>|\s+\bmuted)/i.test(html),name+':no autoplay attr');
}
const cleaned=B.replace(/<aside class="film" data-test-film="true"[\s\S]*?<\/aside>/,'');
check(cleaned===A,'A/B:all substantive HTML identical except optional film module');
check((vtt.match(/--> /g)||[]).length===6,'six caption cues');
check(vtt.includes('00:00:35.000 --> 00:00:42.000'),'42sec final cue');
check(B.includes('data-test-film="true"')&&B.includes('Read the complete 42-second treatment and transcript'),'film and transcript present');
check(!A.includes('data-test-film="true"'),'control no film');
check(article.includes('James Braid')&&article.includes('2023 overview')&&article.includes('2024 systematic review'),'historical/clinical sources');
check(data.sources.length>=12&&data.claims.length>=35,'source-claim matrix complete');
check(Object.values(data.release.gates).length>=30 && Object.values(data.release.gates).every(x=>x===false),'release all gates held');
check(hub.includes('Proposed /mind/')&&hub.includes('not a WordPress CMS draft'),'honest hub status');
check(spec.includes('net revenue per 1,000')&&spec.includes('affiliate_outbound'),'revenue contract');
check(!/https?:\/\/(?:zen12\.com|affiliates\.inspire3\.com)\//.test(A),'no direct merchant click');
const mutants=[
A.replace('disabled aria-describedby','aria-describedby'),
A.replace('Affiliate disclosure:','Commercial notice:'),
A.replace('<button class="merchant"','<script>alert("bad")</script><button class="merchant"'),
A.replace('href="/focus/"','href="https://zen12.com/"'),
A.replace('</main>','<form action="https://example.com">submit</form></main>'),
A.replace('noindex,nofollow','index,follow'),
A.replace('type="button" disabled','type="button" aria-disabled="true"'),
A.replace('href="/focus/"','href="https://affiliates.inspire3.com/"')
];
let denied=0;
for (const m of mutants){
const isInvalid=!/<button\b[^>]+\sdisabled(?=[\s>])/.test(m)||!m.includes('Affiliate disclosure:')||/<script\b|<form\b/i.test(m)||/href="https:\/\/(?:zen12\.com|affiliates\.inspire3\.com)\//.test(m)||!m.includes('noindex,nofollow');
check(isInvalid,'must reject unsafe mutation '+denied);denied++;
}
console.log('PASS checks='+n+' unsafe_mutations_rejected='+denied+' release_gates='+Object.keys(data.release.gates).length+' word_count='+article.trim().split(/\s+/).length);
