// Mind R382 — Reproducible source-level release guard. Run: node mind/r382/verify.mjs
// No network, dependencies or external trackers. This does NOT replace browser/WP/commerce tests.
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
const root = dirname(fileURLToPath(import.meta.url));
const load = f => readFileSync(join(root,f),'utf8');
const names = {
 article:'THE_CHOICE_YOU_DIDNT_MAKE.md',
 a:'ZEN12_A_EVIDENCE_BUYER_GUIDE.html',
 b:'ZEN12_B_OPTIONAL_42S_STORYBOARD.html',
 vtt:'ZEN12_42S_CAPTIONS.vtt',
 hub:'MIND_ARCHIVE_WORDPRESS_REVIEW_ONLY.html',
 claims:'CLAIM_EVIDENCE_RIGHTS_MATRIX.json',
 plan:'CONVERSION_FIRST_ACCEPTANCE_AND_HANDOFF.md'
};
const files = Object.fromEntries(Object.entries(names).map(([key,f])=>[key,load(f)]));
const matrix = JSON.parse(files.claims);
let passes=0;
const check=(ok,label)=>{if(!ok)throw new Error('FAIL '+label);passes++;};
const has=(key,s)=>files[key].includes(s);
const badMerchantLink=html=>/<a\s[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)(?:\/|["'])/i.test(html);
const badPurchase=html=>/<(?!button\b)[a-z]+[^>]*\b(?:affiliate_ref|commission_id|clickid)=/i.test(html);
const unsafeButton=html=>!/<button\s+class="cta"\s+type="button"\s+disabled\s+aria-describedby="offer-status">/.test(html);
const noDisclose=html=>!/<div class="disclosure"><strong>Affiliate disclosure:<\/strong>[\s\S]{0,300}<\/div>\s*<button class="cta"/.test(html);
const scriptsOrForms=html=>(/<script\b|<form\b|<iframe\b|<img\b[^>]*src=["']https?:\/\/|<video\b[^>]*\bautoplay(?:\s|=|>)/i.test(html));
const ctaChecks=html=>!badMerchantLink(html)&&!unsafeButton(html)&&!noDisclose(html)&&!scriptsOrForms(html)&&!badPurchase(html);
check(files.article.trim().split(/\s+/).length >= 2000,'substantive manuscript >= 2k');
check(has('article','10.1126/science.1111709'),'original experiment DOI');
check(has('article','10.1016/j.cognition.2010.06.010'),'replication extension DOI');
check(has('article','10.1016/j.concog.2006.09.004'),'introspection paper DOI');
check(has('article','Puységur'),'history source bridge');
check(/a reproduction of Johansson/.test(files.article),'original free demo not false experimental replication');
check(/diagnostic test or therapy/.test(files.article),'nonclinical/efficacy restraint');
check(has('article','no affiliate promotion'),'no hidden commercial recommendation');
check(has('a','<!doctype html>'),'A complete document');
check(has('b','<!doctype html>'),'B complete document');
check(/<html lang="en">/.test(files.a),'A language set');
check(/<html lang="en">/.test(files.b),'B language set');
check(/name="viewport"/.test(files.a),'A viewport');
check(/name="viewport"/.test(files.b),'B viewport');
check(/name="robots" content="noindex,nofollow"/.test(files.a),'A unindexed');
check(/name="robots" content="noindex,nofollow"/.test(files.b),'B unindexed');
check(ctaChecks(files.a),'A no merchant link, native hold and adjacent disclosure');
check(ctaChecks(files.b),'B no merchant link, native hold and adjacent disclosure');
check(has('a','https://finalvestige.com/focus/'),'A existing free funnel only');
check(has('b','https://finalvestige.com/focus/'),'B existing free funnel only');
check(!/<form\b/i.test(files.a),'no duplicate signup A');
check(!/<form\b/i.test(files.b),'no duplicate signup B');
check(!/<script\b/i.test(files.a),'no analytics JS A');
check(!/<script\b/i.test(files.b),'no analytics JS B');
check(!/<video\b[^>]*\bautoplay/i.test(files.b),'no forced play');
check(has('b','Original vector poster'),'video poster source described');
check(has('b','role="img" aria-labelledby'),'poster accessible name');
check(has('b','<details>')&&has('b','<summary>'),'native no-JS storyboard toggle');
check(has('b','not yet playable'),'no false playable media claim');
check(has('b','00:35–00:42'),'42s complete timed transcript');
check(files.vtt.startsWith('WEBVTT'),'WebVTT proper signature');
check((files.vtt.match(/-->/g)||[]).length===6,'exactly six VTT cues');
check(has('vtt','00:00:42.000'),'captions end at 42s');
check(has('vtt','00:00:00.000'),'captions start at zero');
check(!/\b(?:webcam|pixel|autoplay=)["']/i.test(files.vtt),'captions only');
const bWithoutFilm=files.b.replace(/<aside class="panel film"[\s\S]*?<\/aside>(?=<section aria-labelledby="objections">)/,'');
check(bWithoutFilm===files.a,'A/B identical substantive copy apart from optional film');
check(has('a','@media(max-width:730px)'),'responsive narrow layout');
check(has('a','prefers-reduced-motion'),'motion preference');
check(has('a',':focus-visible'),'visible focus');
check(has('hub','The Mind &amp; Perception Archive'),'hub title and hierarchy');
check(has('hub','Perception &amp; Attention'),'hub stream perception');
check(has('hub','History of Suggestion'),'hub stream historical');
check(has('hub','Practice &amp; Reflection'),'hub stream practical');
check(has('hub','Tools Under Review'),'hub stream buyer tools');
check(has('hub','https://finalvestige.com/2026/11/02/mesmerism/'),'hub internal history link');
check(has('hub','https://finalvestige.com/focus/'),'hub existing single free funnel');
check(!/<form\b|<script\b/i.test(files.hub),'hub no new forms and script');
check(has('hub','Not a saved WordPress draft'),'hub CMS-status transparency');
check(matrix.claims_count===matrix.claims.length && matrix.claims_count>=30,'matrix 30+ individually grounded claims');
check(Object.keys(matrix.release_gates).length>=30,'matrix has substantive release gates');
check(Object.values(matrix.release_gates).every(x=>x.state==='HOLD'),'all commercial gates closed');
check(matrix.affiliate_earning_url===null,'merchant earning link unknown');
check(matrix.verified_paid_sale===null,'no fabricated paid sale');
check(matrix.net_revenue_per_1000_qualified_sessions===null,'no invented KPI');
check(matrix.claims.some(x=>x.id==='C14'&&x.evidence_status==='UNSUBSTANTIATED'),'unverified Zen12 benefits blocked');
check(matrix.claims.some(x=>x.id==='C22'&&x.evidence_status==='UNVERIFIED'),'partner approval remains unknown');
check(matrix.claims.some(x=>x.id==='C27'&&x.evidence_status==='REJECTED'),'click is not sale');
check(has('plan','7-/30-day'),'cohort definition documented');
check(has('plan','qualified-human'),'attribution denominator specified');
check(has('plan','actual platform URL'),'no invented creator IDs');
check(has('plan','NO actual encoded'),'clear video limitation');
check(has('plan','Praxxis independently'),'creator lane separation');
check(!/https:\/\/(?:www\.)?zen12\.com\/\?/.test(files.a),'no fabricated ref in A');
check(!/https:\/\/(?:www\.)?zen12\.com\/\?/.test(files.b),'no fabricated ref in B');
check(Object.keys(names).length===7,'seven independently loaded source files');
const mutations=[
 ['new merchant anchor',()=>ctaChecks(files.a.replace('Purchase link withheld','<a href="https://zen12.com/">Buy now</a> Purchase link withheld'))],
 ['native disabled removed',()=>ctaChecks(files.a.replace('type="button" disabled','type="button" aria-disabled="true"'))],
 ['disclosure removed',()=>ctaChecks(files.a.replace('Affiliate disclosure:','Optional note:'))],
 ['tracking script inserted',()=>ctaChecks(files.a.replace('</head>','<script src="https://tracker.example/test.js"></script></head>'))],
 ['signup form inserted',()=>ctaChecks(files.a.replace('</footer>','<form><input type="email"></form></footer>'))],
 ['auto video inserted',()=>ctaChecks(files.b.replace('</footer>','<video autoplay controls></video></footer>'))],
 ['merchant link in B',()=>ctaChecks(files.b.replace('not yet available','<a href="https://affiliates.inspire3.com/">Activate</a>'))],
 ['iframe vendor embed',()=>ctaChecks(files.b.replace('</footer>','<iframe src="https://vendor.invalid"></iframe></footer>'))],
 ['merchant direct link',()=>ctaChecks(files.a.replace('Source audit:', '<a href="https://hypnosislive.com/">Seller</a> Source audit:'))],
 ['disabled replaced with aria',()=>ctaChecks(files.b.replace('type="button" disabled','type="button" aria-disabled="true"'))]
];
for(const [name,fn] of mutations)check(fn()===false,'unsafe mutation rejected: '+name);
const digest=createHash('sha256').update(Object.entries(files).map(([k,v])=>k+'\n'+v).join('\n')).digest('hex');
console.log(JSON.stringify({result:'PASS',assertions:passes,mutations_rejected:mutations.length,source_file_count:Object.keys(names).length,synthetic_digest_sha256:digest,limitations:'Static source check only: no browser/WP sanitization, native playback, merchant checkout, Jetpack confirmation or production CI.'},null,2));
