// Mind R374 source-only deterministic safety verifier. Requires Node >=18, no network or dependencies.
// Run: node mind/r374/verify.mjs
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const dir = dirname(fileURLToPath(import.meta.url));
const load = name => readFileSync(join(dir,name),'utf8');
const A = load('ZEN12_A_TEXT_GUIDE.html');
const B = load('ZEN12_B_OPTIONAL_42S_STORYBOARD.html');
const hub = load('MIND_HUB_WP_SOURCE_ONLY.html');
const article = load('THE_RECORDING_WAS_NOT_THE_HYPNOTIST.md');
const vtt = load('ORIGINAL_42S_CAPTIONS.vtt');
const memo = load('CONVERSION_FIRST_ACCEPTANCE.md');
const matrix = JSON.parse(load('CLAIM_SOURCE_RIGHTS_MATRIX.json'));
let passed = 0;
function ok(yes,label){assert.ok(yes,label); passed++;}
function forbid(x,pattern,label){ok(!pattern.test(x),label);}
function checkGuide(x,tag){
 ok(x.includes('name="robots" content="noindex,nofollow,noarchive"'),tag+' noindex');
 ok(/<button[^>]*\sdisabled\b[^>]*>Merchant purchase unavailable/.test(x),tag+' native disabled');
 ok(/Final Vestige may earn a commission at no additional cost to you/.test(x),tag+' nearby readable disclosure');
 ok(x.indexOf('Prospective affiliate disclosure:') < x.indexOf('Merchant purchase unavailable'),tag+' disclosure precedes CTA');
 ok(x.includes('https://finalvestige.com/focus/'),tag+' existing free resource');
 ok(x.includes('zen12.com; reference only, no merchant hyperlink'),tag+' seller described without live merchant link');
 forbid(x,/<a\b[^>]*href="https?:\/\/zen12\.com/i,tag+' no active seller destination');
 forbid(x,/<form\b/i,tag+' no new form');
 forbid(x,/<(?:script|iframe)\b/i,tag+' no script/iframe');
 forbid(x,/<(?:video|audio)\b[^>]*autoplay/i,tag+' no autoplay');
 forbid(x,/<a\b[^>]*href="https?:\/\/(?:affiliates\.inspire3\.com|payhip\.com)/i,tag+' no earning destination');
 forbid(x,/<img\b[^>]+(?:pixel|track\.gif)/i,tag+' no marketing pixel');
}
checkGuide(A,'A');checkGuide(B,'B');
const match=B.match(/<section class="panel" data-variant="optional-storyboard"[\s\S]*?<\/section>/);
ok(Boolean(match),'B explicit optional panel');
ok(B.replace(match[0],'')===A,'identical buyer body A/B except film section');
ok(!A.includes('data-variant="optional-storyboard"'),'no film in control');
ok(B.includes('<svg')&&B.includes('<title id="art-title">')&&B.includes('<desc id="art-desc">'),'accessible original SVG');
ok(B.includes('<details>')&&B.includes('full voiceover transcript'),'text transcript');
ok(!B.includes('<video'),'not pretending to be playable');
const cues=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
ok(vtt.startsWith('WEBVTT'),'valid cue type');ok(cues.length===6,'six cue lines');
ok(cues[0][1]==='00:00:00.000'&&cues.at(-1)[2]==='00:00:42.000','42 seconds');
const parseTime=s=>{const p=s.split(':');return +p[0]*3600+(+p[1])*60+Number(p[2]);};
ok(cues.every((c,i)=>parseTime(c[1])<parseTime(c[2]) && (i===0||parseTime(c[1])>=parseTime(cues[i-1][2]))),'nonoverlapping chronologic cues');
ok(matrix.source_count===Object.keys(matrix.sources).length,'source count truthful');
ok(matrix.claims_count===matrix.claims.length,'claim count truthful');
ok(matrix.held_gate_count===matrix.commercial_release_gates.length,'release gate count truthful');
ok(matrix.commercial_release_gates.length>=30&&matrix.commercial_release_gates.every(g=>g.status==='HOLD'),'all merchant gates closed');
ok(matrix.claims.every(c=>matrix.sources[c.source]),'all claims source mapped');
ok(matrix.partner_verification.named_FV_account_approval==='UNKNOWN','no invented partner approval');
ok(article.trim().split(/\s+/).length>=1900,'substantive original investigation');
for(const term of ['Coué','22 randomized','Zen12','Puységur','methodological','Eason']) ok(article.includes(term),'article evidence term '+term);
ok(memo.includes('NOT COMPUTABLE'),'no invented realized net revenue');
ok(memo.includes('utm_medium=organic_social'),'canonical creator attribution medium');
ok(memo.includes('merchant_confirmed_purchase'),'confirmed purchase distinct event');
for(const s of ['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'])ok(hub.includes(s),'hub stream '+s);
ok(hub.includes('noindex,nofollow'),'hub is source-only');
forbid(hub,/<(?:form|script|iframe)\b/i,'hub no active writes');
const mutations=[
 [A,s=>s.replace(/\sdisabled\b/,'')],'BUTTON_ENABLED',
 [A,s=>s.replace('If you purchase through a future authorized link, Final Vestige may earn a commission at no additional cost to you.','')],'DISCLOSURE_REMOVED',
 [A,s=>s.replace('noindex,nofollow,noarchive','index,follow')],'INDEXABLE',
 [A,s=>s+'<form></form>'],'FORM_INJECTED',
 [A,s=>s+'<script src="https://tracker.test/a.js"></script>'],'SCRIPT_INJECTED',
 [A,s=>s+'<iframe src="https://example.test"></iframe>'],'IFRAME_INJECTED',
 [A,s=>s+'<video autoplay></video>'],'AUTOPLAY_VIDEO',
 [A,s=>s+'<a href="https://affiliates.inspire3.com/">Buy</a>'],'UNAPPROVED_EARNING_LINK'
];
let rejected=0;
for(const [baseline,mutate,label] of mutations){const changed=mutate(baseline);try{
 const safe=/<button[^>]*\sdisabled\b/.test(changed) && changed.includes('If you purchase through a future authorized link, Final Vestige may earn a commission at no additional cost to you.') && changed.includes('noindex,nofollow,noarchive') && !/<(?:form|script|iframe)\b/i.test(changed) && !/<video\b[^>]*autoplay/i.test(changed) && !/<a\b[^>]*href="https?:\/\/affiliates\.inspire3\.com/i.test(changed);
 assert.ok(safe,label+' should be rejected');}catch{rejected++;}}
ok(rejected===mutations.length,'all unsafe mutations rejected');
console.log('Mind R374 PASS '+passed+' static checks; '+rejected+'/'+mutations.length+' unsafe mutations rejected; no browser/merchant tests performed');
