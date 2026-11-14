#!/usr/bin/env node
/** R371 offline, read-only source gate. Requires Node >= 18. Never calls a network or broker. */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const root=dirname(fileURLToPath(import.meta.url));
const load=(name)=>readFileSync(join(root,name),'utf8');
const A=load('ZEN12_A_EVIDENCE_FIRST.html'),B=load('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
const HUB=load('MIND_HUB_WORDPRESS_REVIEW_ONLY.html'),VTT=load('ORIGINAL_42S_CAPTIONS.vtt');
const article=load('THE_FACE_THAT_WAS_WRONG_ONLY_WHEN_RIGHT.md');
const plan=load('CONVERSION_FIRST_ACCEPTANCE.md');
const matrix=JSON.parse(load('CLAIM_SOURCE_RIGHTS_MATRIX.json'));
let passed=0;
const check=(name,fn)=>{fn();passed++;process.stdout.write('PASS '+name+'\n')};
const noActiveAffiliate=(html)=>!/<a\b[^>]*href\s*=\s*["'](?:https?:\/\/)?(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com|inspire3\.com)/i.test(html);
const noDanger=(html)=>!/<(?:script|iframe|form|object|embed)\b|\bon(?:click|load|error|submit)\s*=|(?:pixel|googletagmanager|gtag\s*\()/i.test(html);
const disabledCTA=(html)=>/<button\b[^>]*\btype="button"[^>]*\bdisabled\b[^>]*>Merchant link unavailable/.test(html);
const disclosure=(html)=>{const s=html.indexOf('Prospective affiliate disclosure:');const b=html.indexOf('Merchant link unavailable — partner authorization pending');return s>=0&&b>=0&&s<b&&(b-s)<1100};
const holdGates=(m)=>m.commercial_release_gates.length===32&&m.commercial_release_gates.every(x=>x.status==='HOLD');
const noUnsupportedPromises=(html)=>!/(?:clinically proven Zen12|guaranteed cognitive improvements|we tested Zen12|proven to cure anxiety)/i.test(html);
for(const [name,html] of [['A',A],['B',B]]){
 check(name+' valid HTML',()=>assert.match(html,/^<!doctype html><html lang="en">/i));
 check(name+' viewport',()=>assert.match(html,/name="viewport"/));
 check(name+' noindex',()=>assert.match(html,/name="robots" content="noindex,nofollow"/));
 check(name+' skipped navigation',()=>assert.match(html,/<a class="skip" href="#main">/));
 check(name+' heading/main landmark',()=>{assert.match(html,/<main\b/);assert.match(html,/<h1>/)});
 check(name+' no active seller anchors',()=>assert.ok(noActiveAffiliate(html)));
 check(name+' no scripts/frames/forms/pixels',()=>assert.ok(noDanger(html)));
 check(name+' disabled native CTA',()=>assert.ok(disabledCTA(html)));
 check(name+' adjacent earning disclosure',()=>assert.ok(disclosure(html)));
 check(name+' no unsourced product guarantees',()=>assert.ok(noUnsupportedPromises(html)));
 check(name+' existing free Focus route',()=>assert.match(html,/href="\/focus\/"/));
 check(name+' exact Premium format',()=>assert.match(html,/12 sequential levels and 48 downloadable MP3s/));
 check(name+' checkout caveat',()=>assert.match(html,/not a verified checkout total/));
 check(name+' seller claims separated',()=>assert.match(html,/Final Vestige does not endorse it/));
 check(name+' no autoplay',()=>assert.ok(!/<video\b[^>]*autoplay/i.test(html)));
 check(name+' responsive and reduced motion',()=>{assert.match(html,/@media\(max-width:650px\)/);assert.match(html,/prefers-reduced-motion/)});
}
check('A/B equals after removing ONLY film',()=>{
 const start=B.indexOf('<section class="panel" aria-labelledby="film">');
 const end=B.indexOf('</section>',start);
 assert.ok(start>=0&&end>start);
 assert.equal(B.slice(0,start)+B.slice(end+'</section>'.length),A);
});
check('B includes self-describing original SVG',()=>{assert.match(B,/<svg\b/);assert.match(B,/<title id="face-title">/);assert.match(B,/<desc id="face-desc">/);});
check('B transcript readable without JS',()=>{assert.match(B,/<details>/);assert.match(B,/proposed 42-second transcript/);});
check('VTT signature',()=>assert.match(VTT,/^WEBVTT\n/));
check('VTT six cues',()=>assert.equal((VTT.match(/-->/g)||[]).length,6));
check('VTT ends 42 seconds',()=>assert.match(VTT,/00:00:42\.000/));
check('hub proposed not live',()=>assert.match(HUB,/Unpublished draft · Not an active \/mind\/ page/));
check('hub covers four streams',()=>{for(const x of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])assert.ok(HUB.includes(x))});
check('hub only known live links',()=>{assert.match(HUB,/href="\/focus\/"/);assert.match(HUB,/puysegurs-animal-magnetism-files/)});
check('hub no script or form',()=>assert.ok(noDanger(HUB)));
check('article primary source',()=>assert.ok(article.includes('10.1068/p090483')));
check('article counterevidence',()=>assert.ok(article.includes('10.1068/p6659')));
check('article no accidental product efficacy inference',()=>assert.match(article,/not a randomized trial of guided audio/));
check('article present limitations',()=>assert.ok(article.includes('not a validated replication')));
check('matrix claims minimum',()=>assert.ok(matrix.claims.length>=35));
check('matrix 32 gates HOLD',()=>assert.ok(holdGates(matrix)));
check('matrix no allowed product efficacy',()=>{for(const id of ['Z05','Z06','AU02','B03'])assert.ok(matrix.claims.find(c=>c.id===id)?.permission_to_state!=='yes')});
check('matrix distinguishes seller prices',()=>assert.ok(matrix.claims.find(c=>c.id==='Z03')?.classification==='seller-displayed-price'));
check('plan contains cohort windows',()=>assert.ok(plan.includes('7- and 30-day cohorts')));
check('plan preserves Grok role',()=>assert.ok(plan.includes('Grok owns making/publishing')));
check('plan no invented revenue',()=>assert.ok(plan.includes('NOT COMPUTABLE')));
check('plan no duplicated list',()=>assert.ok(plan.includes('one current Jetpack/Dispatch list')));
check('all source files have no affiliate href',()=>assert.ok(noActiveAffiliate(A)&&noActiveAffiliate(B)));
const mutations=[
 ['enable CTA',A.replace(/type="button" disabled/,'type="button"')],
 ['remove disclosure',A.replace(/<p class="disclosure">[\s\S]*?<\/p>/,'')],
 ['add active merchant link',A.replace('Merchant link unavailable — partner authorization pending','<a href="https://zen12.com/?aff=UNKNOWN">Buy</a>')],
 ['add third party script',A.replace('</head>','<script src="https://example.net/pixel.js"></script></head>')],
 ['add signup form',A.replace('</main>','<form><input type="email"></form></main>')],
 ['replace native disable with ARIA',A.replace('type="button" disabled','type="button" aria-disabled="true"')],
 ['drop checkout caveat',A.replace('not a verified checkout total','verified checkout price')],
 ['introduce unsupported product guarantee',A.replace('Final Vestige does not endorse it','clinically proven Zen12')],
 ['remove Focus route',A.replaceAll('href="/focus/"','href="/not-live/"')],
 ['add autoplay video',B.replace('</main>','<video autoplay></video></main>')]
];
let caught=0;
for(const [name,m] of mutations){
 const flagged=!disabledCTA(m)||!disclosure(m)||!noActiveAffiliate(m)||!noDanger(m)||!noUnsupportedPromises(m)||!m.includes('not a verified checkout total')||!m.includes('href="/focus/"')||/<video\b[^>]*autoplay/i.test(m);
 assert.ok(flagged, 'unsafe mutation escaped: '+name);caught++;
}
process.stdout.write('PASS '+caught+'/'+mutations.length+' injected unsafe mutations rejected\n');
process.stdout.write('R371 '+passed+' static checks PASS, '+caught+' mutation probes PASS. Does not cover real browser, WCAG, hosted video, checkout, partner acceptance, payout, WP, or deployment.\n');
