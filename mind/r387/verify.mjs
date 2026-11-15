#!/usr/bin/env node
// R387 standalone audit — no network access, external dependencies or live integrations.
// Execute: node mind/r387/verify.mjs  (from repository root or any directory).
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';
const here=dirname(fileURLToPath(import.meta.url));
const read=(name)=>readFileSync(join(here,name),'utf8');
const a=read('ZEN12_A_TEXT_GUIDE.html'),b=read('ZEN12_B_OPTIONAL_FILM_GUIDE.html');
const hub=read('MIND_ARCHIVE_WORDPRESS_REVIEW_ONLY.html');
const article=read('THE_HAND_THAT_WASNT_YOURS.md');
const svg=read('R387_ORIGINAL_VIDEO_POSTER.svg');
const vtt=read('R387_FILM_CAPTIONS.vtt');
const matrix=JSON.parse(read('CLAIM_SOURCE_RIGHTS_AND_REVENUE_MATRIX.json'));
const dossier=read('CONVERSION_FIRST_ACCEPTANCE_AND_HANDOFF.md');
let count=0;const check=(label,predicate)=>{count++;assert.ok(predicate,label);};
const buyerBody=(html)=>html.match(/<article>([\s\S]*?)<\/article>/)?.[1];
check('A-B substantive buyer copy identical',buyerBody(a)===buyerBody(b));
check('A has substantial copy',buyerBody(a).length>5500);
check('A text version lacks movie treatment',!a.includes('id="film"'));
check('B has optional film storyboard',b.includes('id="film"'));
check('B clearly says not playable',b.includes('not playable') || b.includes('not playback'));
for(const [name,html] of [['A',a],['B',b],['hub',hub]]){
check(name+' valid HTML landmark',/<!doctype html>/i.test(html)&&/<html lang="en">/.test(html)&&/<main>/.test(html));
check(name+' viewport',/name="viewport"/.test(html));
check(name+' noindex review',/name="robots" content="noindex,nofollow"/.test(html));
check(name+' no inline script',!/<script\b/i.test(html));
check(name+' no external iframe',!/<iframe\b/i.test(html));
check(name+' no form duplicate',!/<form\b/i.test(html));
check(name+' no external script tracking',!/<(?:script|img)[^>]+(?:googletagmanager|google-analytics|facebook\.com\/tr|tiktok\.com\/i18n)/i.test(html));
check(name+' no event-handler attrs',!/<[^>]+\son(?:click|load|error|submit|mouseover)\s*=/i.test(html));
check(name+' no autoplay attribute',!/<(?:audio|video)[^>]*\sautoplay\b/i.test(html));
check(name+' no affiliate link',!/<a\b[^>]*\bhref\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|inspire3|affiliates\.inspire3)\.com/i.test(html));
check(name+' no new newsletter signup form',!/<input\b[^>]+type\s*=\s*["']email/i.test(html));
check(name+' focus path stays approved',html.includes('https://finalvestige.com/focus/'));
check(name+' no-js readable',!/<noscript[^>]*>\s*must enable javascript/i.test(html));
check(name+' no motion trap',html.includes('prefers-reduced-motion:reduce'));
check(name+' keyboard focus visible',html.includes(':focus-visible'));
}
for(const [name,html] of [['A',a],['B',b]]){
check(name+' disclosure near disabled CTA',/prospective affiliate disclosure:[\s\S]{0,500}<button type="button" disabled>/i.test(html));
check(name+' native disabled purchase',/<button type="button" disabled>Merchant offer unavailable/.test(html));
check(name+' not aria-disabled-only',!/<button[^>]*aria-disabled=["']true["'][^>]*>Merchant offer/i.test(html));
check(name+' free practice',html.includes('Try a free, useful twelve-minute baseline'));
check(name+' product limitations',html.includes('not a clinical recommendation')===false&&html.includes('This page gives no clinical recommendation'));
check(name+' seller attribution',html.includes('Seller describes'));
check(name+' price is not checkout',html.includes('neither is an authenticated referred checkout price'));
check(name+' material affiliate expectation disclosed',html.includes('may earn a commission at no additional cost'));
check(name+' minimum objections', ['Will this replace','Is twelve minutes','Will it help','Is the public display','Can I trust'].every(v=>html.includes(v)));
}
check('film uses original poster',b.includes('R387_ORIGINAL_VIDEO_POSTER.svg'));
check('film transcript visible in no-js details',/<details>[\s\S]*?<summary>[\s\S]*?<\/details>/.test(b));
check('film has no live video file',!/<video\b/.test(b));
check('film alt is descriptive',/alt="Original flat illustration/.test(b));
check('vtt declares WEBVTT',vtt.startsWith('WEBVTT\n'));
const timestamps=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g)].map(m=>[+m[1]*3600+(+m[2])*60+(+m[3]),+m[4]*3600+(+m[5])*60+(+m[6])]);
check('six captions',timestamps.length===6);
check('caption full coverage',timestamps[0][0]===0&&timestamps.at(-1)[1]===42);
check('captions contiguous',timestamps.every((x,i)=>i===0||x[0]===timestamps[i-1][1]));
check('captions forward',timestamps.every(([s,e])=>e>s));
check('svg is original SVG',svg.includes('<svg xmlns="http://www.w3.org/2000/svg"'));
check('svg names figure',svg.includes('<title id="title">')&&svg.includes('<desc id="desc">'));
check('svg no script or foreign object',!/<script|<foreignObject|xlink:href|<image\b/i.test(svg));
check('svg no event handler',!/\son(?:load|click|error)\s*=/i.test(svg));
check('article min 2300 words',article.split(/\s+/).length>=2300);
for(const [tag,url] of [['nature','https://doi.org/10.1038/35784'],['plos','https://doi.org/10.1371/journal.pone.0021659'],['lush','https://doi.org/10.1525/collabra.325'],['slater','https://pmc.ncbi.nlm.nih.gov/articles/PMC9244625/'],['ftc','https://www.ftc.gov/business-guidance/']]){check('article source '+tag,article.includes(url));}
check('article historical ethics and distinction',article.includes('Puységur')&&article.includes('consent')&&article.includes('not a clinical'));
check('article no fake first-person use claim',!/I (?:bought|used|tested) Zen12/i.test(article));
check('matrix claims 30+',matrix.claims.length>=30);
check('matrix 36 gates',matrix.release_gates.length===36);
check('matrix all held',matrix.release_gates.every(g=>g.status==='HARD_HOLD'));
check('matrix 15 links',Object.keys(matrix.sources).length>=15);
check('matrix no issued link',matrix.commercial_snapshot.earning_url==='WITHHELD');
check('matrix no paid revenue assertion',matrix.commercial_snapshot.revenue_per_1000_qualified_sessions==='NOT COMPUTABLE');
check('matrix all claims have source+status',matrix.claims.every(c=>Boolean(c.id&&c.claim&&c.evidence_state&&c.source&&c.publication_rule)));
check('dossier maps 3 public creator routes',dossier.includes('/change-blindness/')&&dossier.includes('/mesmerism/')&&dossier.includes('/puysegurs-animal-magnetism-files/'));
check('dossier no fake asset IDs',dossier.includes('no immutable asset_id'));
check('dossier stores sale distinct from click',dossier.includes('affiliate_click')&&dossier.includes('merchant_confirmed_paid'));
check('dossier cohort definitions',dossier.includes('7- and 30-day'));
check('dossier no tracking deployment',dossier.includes('NO instrumentation deployed'));
check('dossier no PR contamination',dossier.includes('PR #49')&&dossier.includes('PR #172')&&dossier.includes('Issue #150'));
check('dossier no fake SKU',dossier.includes('no current payable owned-Mind offer'));
console.log('R387 source-only verifier PASS: '+count+' assertions. Does NOT verify browser accessibility, encoded video, WordPress, Jetpack, merchant checkout or settlements.');
