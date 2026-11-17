// Node 18+ read-only static QA for R436. Not a substitute for browser, CI or merchant verification.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),read=n=>fs.readFileSync(path.join(here,n),'utf8');
const A=read('ZEN12_A_TEXT.html'),B=read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html'),H=read('MIND_ARCHIVE_SOURCE_ONLY.html');
const art=read('THE_STRANGER_WHO_CHANGED.md'),C=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json')),V=read('film.vtt'),X=read('CONVERSION_ACCEPTANCE.md');
const buyer=s=>s.split('<!-- BUYER START -->')[1]?.split('<!-- BUYER END -->')[0];
const tests=[
['real-world original DOI',art.includes('10.3758/BF03208840')],
['flicker primary DOI',art.includes('10.1111/j.1467-9280.1997.tb00427.x')],
['meditator null result retained',art.includes('sustained inattentional blindness')],
['history source cited',art.includes('puysegurs-animal-magnetism-files')],
['single existing free lead cited',art.includes('https://finalvestige.com/focus/')],
['identical A/B buyer copy',buyer(A)===buyer(B)],
['B film only',!A.includes('id="film-concept"')&&B.includes('id="film-concept"')],
['B transcript included',B.includes('full timed narration and caption concept')],
['B poster original',read('poster.svg').includes('DID YOU NOTICE THE CHANGE?')],
['B caption duration',V.includes('00:00:42.000')],
['disclosure near commercial section',[A,B].every(s=>s.includes('id="commercial"')&&s.includes('may earn a commission'))],
['disabled merchant buttons',[A,B].every(s=>s.includes('type="button" disabled'))]
];

// Add production guard assertions without executing any side effects.
tests.push(['no vendor purchase href',[A,B].every(s=>!/<a[^>]*href=["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(s))]);
tests.push(['no scripts/iframes/forms/video',[A,B,H].every(s=>!/<(script|iframe|form|video)\b/i.test(s))]);
tests.push(['noindex draft only',[A,B,H].every(s=>s.includes('noindex,nofollow'))]);
tests.push(['4 archive streams',['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'].every(s=>H.includes(s))]);
tests.push(['23 sourced claims',C.claims.length===23]);
tests.push(['28 HOLD gates',C.gates.length===28&&C.gates.every(x=>x.status==='HOLD')]);
tests.push(['duplicate page safeguarded',C.live_duplicate_risk.includes('already exists')&&X.includes('already a live')]);
tests.push(['no false sale math',X.includes('NOT COMPUTABLE')&&X.includes('affiliate_outbound')]);
tests.push(['no active sales in source',A.includes('no active earning or seller purchase link')]);
let failures=0;for(const [label,pass] of tests){if(!pass)failures++;console.log((pass?'PASS ':'FAIL ')+label)}console.log((tests.length-failures)+'/'+tests.length+' assertions');if(failures)process.exitCode=1;
