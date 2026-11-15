// Node 18+; offline static source verification. No network, WP, analytics or merchant interaction.
// Usage from repository root: node mind/r388/verify.mjs
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const load=n=>fs.readFileSync(path.join(dir,n),'utf8');
const fixture=()=>({
 a:load('ZEN12_A_TEXT_GUIDE.html'),
 b:load('ZEN12_B_OPTIONAL_FILM_GUIDE.html'),
 article:load('THE_SECOND_HAND_THAT_WAITED.md'),
 hub:load('MIND_HUB_SOURCE_ONLY.html'),
 poster:load('R388_POSTER.svg'),
 vtt:load('R388_42S_CAPTIONS.vtt'),
 matrix:JSON.parse(load('CLAIM_SOURCE_RIGHTS_MATRIX.json')),
 dossier:load('CONVERSION_ACCEPTANCE_GROK_HANDOFF.md')
});
const sellerHref=/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3|hypnosislive|brainwaveshots)\.com\b/i;
const noScripts=/<script\b|<iframe\b|<form\b|<video\b|<audio\b|<source\b/i;
const badGuaranteed=/(guaranteed (?:to|outcomes?|focus|results?)|proven to (?:cure|treat)|make.*\$\d+\s*(?:daily|weekly)|last chance to buy)/i;
const check=(f)=>{
 const e=[],push=(ok,msg)=>{if(!ok)e.push(msg)};
 push(/<!doctype html>/i.test(f.a)&&/<!doctype html>/i.test(f.b),'doctype A/B');
 push(/<html lang="en">/.test(f.a)&&/<html lang="en">/.test(f.b),'lang A/B');
 push(/<main id="main"/.test(f.a)&&/<main id="main"/.test(f.b),'main landmark');
 push(/href="#main"/.test(f.a)&&/href="#main"/.test(f.b),'skip links');
 push(/meta name="viewport"/.test(f.a)&&/meta name="viewport"/.test(f.b),'responsive meta');
 push(/name="robots" content="noindex,nofollow"/.test(f.a)&&/name="robots" content="noindex,nofollow"/.test(f.b),'draft noindex');
 push(/prefers-reduced-motion:reduce/.test(f.a)&&/prefers-reduced-motion:reduce/.test(f.b),'reduced motion');
 push(/:focus-visible/.test(f.a)&&/:focus-visible/.test(f.b),'keyboard focus style');
 push(!noScripts.test(f.a)&&!noScripts.test(f.b)&&!noScripts.test(f.hub),'no forms/scripts/embed');
 push(!sellerHref.test(f.a)&&!sellerHref.test(f.b)&&!sellerHref.test(f.hub),'no active merchant link');
 push((f.a.match(/<button[^>]+disabled\b/g)||[]).length===1,'A native disabled button');
 push((f.b.match(/<button[^>]+disabled\b/g)||[]).length===1,'B native disabled button');
 push(/Affiliate disclosure:[\s\S]{0,500}<button[^>]+disabled/.test(f.a),'A near-button disclosure');
 push(/Affiliate disclosure:[\s\S]{0,500}<button[^>]+disabled/.test(f.b),'B near-button disclosure');
 push(/No affiliate link is active/.test(f.a)&&/No affiliate link is active/.test(f.b),'future conditional earning status');
 push(/https:\/\/finalvestige.com\/focus\//.test(f.a)&&/https:\/\/finalvestige.com\/focus\//.test(f.b)&&/https:\/\/finalvestige.com\/focus\//.test(f.hub),'one existing Focus route');
 push(/12 levels/.test(f.a)&&/48 MP3/.test(f.a)&&/four audio styles/.test(f.a),'tier content facts');
 push(/not independently verified product-specific controlled evidence/i.test(f.a),'no claim transfer');
 push(/November 14, 2026/.test(f.a)&&/\$87\.99/.test(f.a)&&/not proof|could differ/i.test(f.a),'observed not final price');
 push(/one-year money-back promise/.test(f.a)&&/not independently verified refund/.test(f.a),'refund caution');
 push(!badGuaranteed.test(f.a)&&!badGuaranteed.test(f.b),'no guarantee/urgency promise');
 push(/<section aria-labelledby="film">/.test(f.b)&&!/<section aria-labelledby="film">/.test(f.a),'B only optional film');
 const clean=s=>s.replace(/<section aria-labelledby="film">[\s\S]*?<\/section>/,'').replace(/· [AB] · Final Vestige/g,'· X · Final Vestige');
 push(clean(f.a)===clean(f.b),'buyer copy A/B byte-identical absent optional film section and title');
 push(/<img[^>]*src="R388_POSTER\.svg"[^>]*alt="[^"]{25,}"/.test(f.b),'B poster alt text');
 push(/<details>/.test(f.b)&&/<summary>/.test(f.b)&&/R388_42S_CAPTIONS\.vtt/.test(f.b),'transcript accessible without JS');
 push(!/<video\b/i.test(f.b),'B is a nonplayable storyboard; no false playback');
 push(/^WEBVTT\s/m.test(f.vtt),'VTT header');
 const times=[...f.vtt.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)];
 push(times.length===6,'six caption cues');
 push(times[0]?.[1]==='00:00:00.000'&&times[5]?.[2]==='00:00:42.000','42s caption endpoints');
 push(/<title id="ttl">/.test(f.poster)&&/<desc id="desc">/.test(f.poster),'accessible original SVG poster');
 push(!/<image\b|<script\b|onload\s*=/.test(f.poster),'SVG no remote image/execution');
 push(f.article.trim().split(/\s+/).length>2100,'substantial original investigation');
 for(const token of ['10.1038/35104551','openaccess.city.ac.uk/id/eprint/335','10.1038/nn1488','10.1038/nn.2111','puysegurs-animal-magnetism-files','zen12.com','ftc.gov'])push(f.article.includes(token),'article source '+token);
 push((f.hub.match(/class="card"/g)||[]).length===4,'four Mind streams');
 push(/UNPUBLISHED SOURCE-ONLY PROTOTYPE/.test(f.hub),'hub source-only status');
 push(f.matrix.claims.length>=28,'claim matrix meaningful size');
 push(f.matrix.release_gates.length>=20,'release gates meaningful size');
 push(f.matrix.release_gates.every(g=>g.status==='HOLD'&&g.verified_proof===null),'all commerce gates HOLD');
 push(f.matrix.claims.some(c=>c.id==='A01'&&c.decision==='UNVERIFIED_HOLD'),'publisher approval hold');
 push(f.matrix.claims.some(c=>c.id==='S07'&&c.decision==='OMIT'),'extraordinary efficacy blocked');
 push(f.matrix.measurement_contract.affiliate_click_is_sale===false,'click not sale');
 push(f.matrix.measurement_contract.net_revenue_per_1000_qualified_sessions===null,'net revenue unknown');
 push(f.matrix.measurement_contract.no_new_tracking_script===true,'no duplicate scripts');
 push(f.dossier.includes('DO NOT')||f.dossier.includes('Do not'),'release restrictions in dossier');
 push(f.dossier.includes('NOT COMPUTABLE'),'unknown net metric explicit');
 push(/actual Grok asset_id|Actual Grok asset_id/.test(f.dossier),'real media IDs required');
 push(f.dossier.includes('https://finalvestige.com/2026/11/02/change-blindness/')&&f.dossier.includes('https://finalvestige.com/2026/11/02/mesmerism/')&&f.dossier.includes('puysegurs-animal-magnetism-files'),'three verified live route candidates');
 push(f.dossier.includes('utm_medium=organic_social'),'privacy-first social campaign specification');
 return e;
};
const original=fixture();
const failures=check(original);
if(failures.length){console.error('FAIL SOURCE AUDIT:',failures);process.exitCode=1;}else console.log('PASS source audit: '+(check.toString().match(/push\(/g)||[]).length+' declared checks, zero failures');
const mutations=[
 ['enableA',f=>f.a=f.a.replace('type="button" disabled','type="button"')],
 ['linkMerchantA',f=>f.a=f.a.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/getstarted"')],
 ['scriptA',f=>f.a=f.a.replace('</body>','<script>console.log(1)</script></body>')],
 ['fakeNoDiscloseB',f=>f.b=f.b.replace(/Affiliate disclosure:[\s\S]*?No affiliate link is active on this page\./,'No financial relationship information')],
 ['changeBuyerTextB',f=>f.b=f.b.replace('four audio styles per level','six audio styles per level')],
 ['createFormHub',f=>f.hub=f.hub.replace('</main>','<form action="/signup"><input name="email"></form></main>')],
 ['missingPosterAlt',f=>f.b=f.b.replace(/ alt="[^"]+"/,'')],
 ['removeCaption',f=>f.vtt=f.vtt.replace(/6\n00:00:35\.000 --> 00:00:42\.000[\s\S]*/, '')],
 ['wrongCommitClaim',f=>f.matrix.claims.find(c=>c.id==='S07').decision='include_qualified'],
 ['affiliateApprovedFabrication',f=>f.matrix.release_gates[0].status='PASS'],
 ['fakeSaleNumber',f=>f.matrix.measurement_contract.net_revenue_per_1000_qualified_sessions=999],
 ['productGuarantee',f=>f.a=f.a.replace('What the evidence cannot establish','Guaranteed focus results')]
];
let caught=0;
for(const [name,fn] of mutations){const f=structuredClone(original);fn(f);const errors=check(f);if(errors.length){caught++;console.log('REJECT mutation '+name+': '+errors[0]);}else{console.error('MISSED mutation '+name);process.exitCode=1;}}
console.log('Negative fixtures rejected: '+caught+'/'+mutations.length);
if(!failures.length&&caught===mutations.length) console.log('PASS: static release safeguards; browser, WP and paid merchant validation remain NOT RUN');
