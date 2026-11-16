#!/usr/bin/env node
/* FV Mind R424 — read-only, no-network source integrity and commercial safety verifier.
   node mind/r424/VERIFY_R424.mjs
   Exit 1 on failed checks. These checks do not replace browser, WP sanitizer,
   affiliate merchant or Jetpack provider evidence. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const base=path.dirname(fileURLToPath(import.meta.url));
const read=n=>fs.readFileSync(path.join(base,n),'utf8');
const files={
 article:read('THE_GORILLA_WAS_NEVER_INVISIBLE.md'),
 A:read('ZEN12_A_TEXT_GUIDE.html'),
 B:read('ZEN12_B_OPTIONAL_FILM.html'),
 hub:read('MIND_ARCHIVE_WP_SOURCE_ONLY.html'),
 matrix:read('CLAIM_SOURCE_PERMISSION_MATRIX.json'),
 vtt:read('ZEN12_OPTIONAL_42S.vtt'),
 acceptance:read('CONVERSION_ACCEPTANCE_CREATOR_CROSSWALK.md')
};
const checks=[], failures=[];
function test(label,yes){checks.push(label);if(!yes)failures.push(label);}
function phrase(s,p){return s.includes(p);}
function audit(f){
 const t=(label,ok)=>test(label,ok);
 const m=JSON.parse(f.matrix);
 t('article original length',f.article.trim().split(/\s+/).length>=2000);
 for(const [name,url] of Object.entries({
   'primary 1999':'https://doi.org/10.1068/p281059',
   'primary 2013':'https://doi.org/10.1177/0956797613479386',
   'primary 2010':'https://doi.org/10.1068/i0386',
   'Puységur':'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/',
   'FTC endorsement':'https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking'
 })) t('article source '+name,phrase(f.article,url));
 t('article no product evidence leap',phrase(f.article,'did not test meditation'));
 t('article original 12-minute practice',phrase(f.article,'Minutes 10–12'));
 t('article not published',phrase(f.article,'UNPUBLISHED'));
 for(const name of ['A','B','hub']){
   const v=f[name];
   t(name+' document and language',v.includes('<!doctype html>')&&v.includes('lang="en"'));
   t(name+' viewport',phrase(v,'name="viewport"'));
   t(name+' no javascript',!/<script\b/i.test(v));
   t(name+' no iframe',!/<iframe\b/i.test(v));
   t(name+' no autoplay',!/\bautoplay\b/i.test(v));
   t(name+' no signup forms',!/<form\b/i.test(v));
   t(name+' no third party analytics',!/googletagmanager|google-analytics|facebook\.com\/tr|pixel\.|gtag\(/i.test(v));
   t(name+' no activated affiliate merchant links',!/<a\b[^>]*href=["'][^"']*(?:affiliates\.inspire3|affiliate[_-]|clickbank|checkout|\/order(?:\/|["'?]))/i.test(v));
   t(name+' no referral query tokens',!/(?:[?&](?:aff_id|affiliate|ref|hop|tid|subid)=)/i.test(v));
   t(name+' readable small screen styles',phrase(v,'max-width:680px'));
   t(name+' keyboard focus indication',phrase(v,'focus-visible'));
   t(name+' noindex draft',phrase(v,'noindex,nofollow'));
 }
 t('A has visible purpose',phrase(f.A,'Can a 12-minute recording'));
 t('B has visible purpose',phrase(f.B,'Can a 12-minute recording'));
 const section=v=>v.slice(v.indexOf('<section class="section" id="why">'),v.indexOf('</main>'));
 t('A/B identical substantive guide',section(f.A)===section(f.B) && section(f.A).length>5000);
 for(const name of ['A','B']){
   const v=f[name],c=v.match(/<div class="commercial"[\s\S]*?<\/div>/)?.[0]||'';
   t(name+' adjacent clear financial disclosure',/disclose[\s\S]*?Final Vestige may earn a commission at no additional cost to you/.test(c));
   t(name+' buyer action disabled at HTML level',/<button[^>]+disabled\b/.test(c));
   t(name+' no merchant purchase href in offer',!/<a\b[^>]+href=/.test(c));
   t(name+' no guaranteed 1h in 12m product claims',phrase(v,'seller claim')||phrase(v,'seller asserts')||phrase(v,'seller assertions')||phrase(v,'seller promises'));
   t(name+' no seller price asserted for FV',!/(\$|USD|£)\s*\d/.test(v));
   t(name+' one original free step',phrase(v,'Seven Day Focus Fieldbook'));
   t(name+' source citations',phrase(v,'https://doi.org/10.1068/p281059')&&phrase(v,'https://zen12.com/'));
 }
 t('A has no storyboard',!phrase(f.A,'Optional 42-second original film'));
 t('B optional original storyboard',phrase(f.B,'Optional 42-second original film'));
 t('B poster is inline svg',phrase(f.B,'<svg xmlns="http://www.w3.org/2000/svg"'));
 t('B no fake playable video',!/<video\b|<audio\b/.test(f.B));
 t('B transcript expandable',phrase(f.B,'<details>')&&phrase(f.B,'complete 42-second narration'));
 t('B six timed transcript cues',(f.B.match(/<strong>00:/g)||[]).length===6);
 t('VTT syntax',f.vtt.startsWith('WEBVTT'));
 const cues=[...f.vtt.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)];
 t('VTT six caption cues',cues.length===6);
 const seconds=s=>{const x=s.split(':');return +x[0]*3600 + +x[1]*60+parseFloat(x[2]);};
 t('VTT covers exactly 42 seconds',cues.length===6&&seconds(cues[0][1])===0&&seconds(cues[5][2])===42);
 t('VTT no gaps or overlaps',cues.length===6&&cues.every((v,i)=>seconds(v[2])>seconds(v[1])&&(i===0||seconds(cues[i-1][2])===seconds(v[1]))));
 t('VTT transcript scientific boundary',phrase(f.vtt,'does not show it improves focus'));
 t('matrix 32 labeled claims',m.claims.length===32&&new Set(m.claims.map(x=>x.id)).size===32);
 t('matrix 28 closed gates',m.release_gates.length===28&&m.release_gates.every(g=>g.state==='HOLD'&&g.verified===false&&g.blocking===true));
 t('matrix source IDs resolve',m.claims.every(c=>Boolean(m.source_urls[c.source_id])));
 t('matrix explicit excluded seller efficacy',m.claims.filter(c=>c.kind==='seller efficacy').every(c=>c.status.includes('excluded')&&!c.release_eligible));
 t('matrix revenue unknown not fabricated',m.commercial_stats.net_revenue_per_1000_qualified_humans==='NOT_COMPUTABLE');
 t('hub four streams', ['01 / ATTENTION','02 / SUGGESTION','03 / FIELDWORK','04 / TOOLS UNDER REVIEW'].every(x=>phrase(f.hub,x)));
 t('hub article no fake public link',phrase(f.hub,'NO public URL')||phrase(f.hub,'not yet a public URL'));
 t('hub only existing Focus path',phrase(f.hub,'https://finalvestige.com/focus/'));
 t('acceptance three routes',(f.acceptance.match(/https:\/\/finalvestige\.com\/2026\/11\/02\//g)||[]).length>=2);
 t('acceptance qualified denominator',phrase(f.acceptance,'qualified-human campaign sessions'));
 t('acceptance paid not click',phrase(f.acceptance,'A commission or buyer')||phrase(f.acceptance,'A commission'));
 t('acceptance founder gate',phrase(f.acceptance,'founder'));
 t('acceptance no unauthorized live writes',phrase(f.acceptance,'No WordPress draft/live CMS'));
 return failures;
}
audit(files);
if(process.argv.includes('--mutation-self-test')){
 function isolate(mut){
  const snapshot=checks.length, failStart=failures.length;
  audit({...files,...mut});const bad=failures.length>failStart;
  checks.length=snapshot;failures.length=failStart;return bad;
 }
 const badCases=[
  ['enabled purchase button',{A:files.A.replace('type="button" disabled','type="button"')}],
  ['disclosure removed',{A:files.A.replace('Final Vestige may earn a commission at no additional cost to you','Our picks are great')}],
  ['hidden merchant anchor',{A:files.A.replace('<!-- never -->','').replace('</body>','<a href="https://affiliates.inspire3.com/ref?a=1">Pay</a></body>')}],
  ['autoplay injected',{B:files.B.replace('</body>','<video autoplay></video></body>')}],
  ['tracking injected',{hub:files.hub.replace('</body>','<script src="https://google-analytics.com/x.js"></script></body>')}],
  ['gate unheld',{matrix:JSON.stringify({...JSON.parse(files.matrix),release_gates:JSON.parse(files.matrix).release_gates.map((g,i)=>i?g:{...g,state:'PASS'})})}],
  ['citation removed',{article:files.article.replace('https://doi.org/10.1068/p281059','citation omitted')}],
  ['caption gap',{vtt:files.vtt.replace('00:00:14.000 --> 00:00:21.000','00:00:15.000 --> 00:00:21.000')}]
 ];
 for(const [label,mut] of badCases){const ok=isolate(mut);test('unsafe mutation detected: '+label,ok);}
}
console.log(JSON.stringify({checks:checks.length,passes:checks.length-failures.length,failures,mode:process.argv.includes('--mutation-self-test')?'adversarial':'standard'},null,2));
if(failures.length)process.exit(1);
