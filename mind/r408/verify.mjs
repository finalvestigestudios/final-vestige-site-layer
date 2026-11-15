#!/usr/bin/env node
// R408 source-only release-gate verifier. Run: node mind/r408/verify.mjs
// No network, paid vendor, browser or CMS writes. A PASS is NOT live a11y or commerce QA.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const get=n=>fs.readFileSync(path.join(root,n),'utf8');
const A=get('ZEN12_TEXT_A.html'),B=get('ZEN12_OPTIONAL_FILM_B.html');
const H=get('MIND_ARCHIVE_SOURCE_ONLY.html');
const V=get('FILM_42S_CAPTIONS.vtt');
const M=JSON.parse(get('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const G=get('THE_EAR_HEARS_A_PATTERN.md');
const D=get('CONVERSION_GROK_RELEASE_DOSSIER.md');
let passed=0,failed=0;
function check(label,condition){if(condition){passed++; console.log('PASS '+label)}else{failed++;console.error('FAIL '+label)}}
function extractArticle(s){return s.match(/<article id="guide">[\s\S]*?<\/article>/)?.[0]??''}
function hasDisabledButton(s){return /<button\b[^>]*\bdisabled(?:\s|=|>)/i.test(s)}
function forbidden(s){return /<script\b|<iframe\b|<form\b|javascript\s*:|<video\b[^>]*\bautoplay\b|\son(?:click|load|error|submit|mouseover)\s*=/i.test(s)}
function disclosureNear(s){let n=s.indexOf('Prospective affiliate disclosure:');let b=s.indexOf('Purchase link withheld');return n!==-1&&b>n&&b-n<500}
function cues(s){return [...s.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})\n([^\n]+)/g)].map(m=>({start:(+m[1])*3600+(+m[2])*60+(+m[3])+(+m[4])/1000,end:(+m[5])*3600+(+m[6])*60+(+m[7])+(+m[8])/1000,text:m[9]}))}
const normalize=x=>x.replace(/\s+/g,' ').trim();
check('Both HTML variants contain same exact substantive article',extractArticle(A).length>4000&&extractArticle(A)===extractArticle(B));
check('A contains no optional film figure',!A.includes('Optional 42-second visual explainer'));
check('B has opt-in details, original SVG and a visible transcript',/<details\b/.test(B)&&/<svg\b/.test(B)&&/Full proposed 42-second transcript/.test(B));
check('No video autoplay or external player embedded',![A,B].some(x=>/<video\\b[^>]*\\bautoplay\\b|<iframe\\b/i.test(x)));

check('A native merchant button is disabled',hasDisabledButton(A));
check('B native merchant button is disabled',hasDisabledButton(B));
check('A adjacent commission disclosure',disclosureNear(A));
check('B adjacent commission disclosure',disclosureNear(B));
check('No prohibited scripts/forms/handlers/javascript links',[A,B,H].every(x=>!forbidden(x)));
check('Pages declare noindex',[A,B,H].every(x=>/name="robots" content="noindex,nofollow"/.test(x)));
check('Focus remains accessible through existing live route',[A,B,H].every(x=>x.includes('https://finalvestige.com/focus/')));
check('No merchant referral link',![A,B,H].some(x=>/<a[^>]+href="https?:\/\/(?:affiliates\.inspire3\.com|payhip\.com)/i.test(x)));
check('No second opt-in form',[A,B,H].every(x=>!/<form\b/i.test(x)));
check('A has a skip link and navigation',A.includes('href="#guide"')&&A.includes('aria-label="Pilot navigation"'));
check('B original SVG has accessible title and desc',B.includes('aria-labelledby="svg-title svg-desc"')&&B.includes('id="svg-title"')&&B.includes('id="svg-desc"'));
check('Responsive and reduced-motion styles',[A,B,H].every(x=>x.includes('prefers-reduced-motion'))&&H.includes('max-width:680px'));
check('Four distinct Mind streams', ['Perception &amp; attention','History of suggestion','Practice &amp; reflection','Tools under review'].every(x=>H.toLowerCase().includes(x.toLowerCase())));
check('Live source route included',H.includes('https://finalvestige.com/2026/11/02/change-blindness/'));
check('Four-stream hub contains no approved commerce',H.includes('No unapproved off-site purchase link'));
check('VTT header',V.startsWith('WEBVTT\n'));
const C=cues(V);
check('Exactly six timed cue blocks',C.length===6);
check('Cues contiguous from zero to 42s',C.length===6&&C[0].start===0&&C[5].end===42&&C.every((c,i)=>c.end>c.start&&(i===0||c.start===C[i-1].end)));
check('Caption text matches complete proposed transcript',normalize(C.map(x=>x.text).join(' '))===normalize(B.match(/<h3 id="transcript-title">[^<]+<\/h3><p>([^<]+)<\/p>/)?.[1]??''));
check('Claim register contains twenty evidence labels',M.claims.length===20);
check('Source register contains sixteen URLs',M.sources.length===16&&new Set(M.sources.map(s=>s.id)).size===16);
check('All sources use HTTPS',M.sources.every(s=>s.url.startsWith('https://')));
check('Every claim source ID resolves',M.claims.every(c=>c.source_ids.every(id=>M.sources.some(s=>s.id===id))));
check('All twenty-six commercial gates held',M.gates.length===26&&M.gates.every(g=>g.status==='HOLD'));
check('Partner acceptance explicitly unauthenticated',M.observations.affiliate_publisher_acceptance==='NOT_AUTHENTICATED');
check('Paid net / 1000 not computable',M.observations.realized_net_per_1000==='NOT_COMPUTABLE');
check('Investigation longform is substantial',G.trim().split(/\s+/).length>=1700);
check('No personal-use testimonial',!G.includes('I have used Zen12')&&!G.includes('we tested the recordings'));
check('Scientific research is not promoted as SKU proof',G.includes('not independently')&&G.includes('not evidence'));
check('Conversion dossier requires partner permission',D.includes('named Final Vestige partner acceptance'));
check('Creator rights/IDs remain unverified',D.includes('No actual Grok asset IDs'));
check('No invented owned Mind paid SKU',D.includes('No speculative fallback'));
check('Only source-only, no CMS instructions issued',D.includes('no CMS'));
check('FTC references present',M.sources.some(s=>s.id==='ftc_endorse')&&M.sources.some(s=>s.id==='ftc_health'));
function mustReject(name,mutated,pred){check('Negative gate: '+name,!pred(mutated))}
mustReject('enabled purchase',A.replace(/<button type="button" disabled /,'<button type="button" '),hasDisabledButton);
mustReject('missing disclosure',B.replace('Prospective affiliate disclosure:','Disclosure deleted'),disclosureNear);
mustReject('inserted inline script',A.replace('</body>','<script>alert(1)</script></body>'),x=>!forbidden(x));
mustReject('new subscription form',H.replace('</body>','<form method="get"></form></body>'),x=>!forbidden(x));
mustReject('forced video autoplay',B.replace('</body>','<video autoplay></video></body>'),x=>!forbidden(x));
mustReject('malicious Javascript href',H.replace('</body>','<a href="javascript:alert(1)">x</a></body>'),x=>!forbidden(x));
mustReject('closed gate flipped open',JSON.stringify(M).replace('"status":"HOLD"','"status":"ACTIVE"'),x=>JSON.parse(x).gates.every(g=>g.status==='HOLD'));
mustReject('caption truncation',V.replace('Learn what helps you begin. Then decide what convenience is worth.',''),x=>normalize(cues(x).map(c=>c.text).join(' '))===normalize(B.match(/<h3 id="transcript-title">[^<]+<\/h3><p>([^<]+)<\/p>/)?.[1]??''));
console.log('\n'+passed+' PASS / '+failed+' FAIL; source-only checks are not real browser, media playback, CMS, or merchant proof.');
if(failed)process.exitCode=1;
