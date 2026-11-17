#!/usr/bin/env node
// R437 source-only safety and A/B parity verifier. Run: node mind/r437/verify.mjs
// This is NOT a real-browser, merchant, WordPress, video-playback, or analytics test.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';
const dir = dirname(fileURLToPath(import.meta.url));
const read = f => readFileSync(join(dir,f),'utf8');
const A=read('ZEN12_A_TEXT_ONLY.html');
const B=read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
const HUB=read('MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html');
const VTT=read('ZEN12_42S_CONCEPT.vtt');
const ARTICLE=read('THE_FACE_THAT_CHANGED_WHEN_TURNED.md');
const CLAIMS=JSON.parse(read('CLAIM_SOURCE_AND_PERMISSION_MATRIX.json'));
const PLAN=read('CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md');
let n=0;
function check(condition,message){assert.ok(condition,message);n++;}
check(CLAIMS.schema==='fv-mind-claim-and-authorization-v1','schema');
check(CLAIMS.release_status==='UNPUBLISHED_COMMERCIAL_HARD_HOLD','release status');
check(CLAIMS.claims.length>=30,'claim coverage');
check(CLAIMS.release_gates.length===28,'gate count');
check(CLAIMS.release_gates.every(g=>g.status==='HOLD'),'all gates HOLD');
check(Object.keys(CLAIMS.source_urls).length>=16,'source URLs');
check(CLAIMS.claims.every(c=>c.source_keys.every(k=>Object.hasOwn(CLAIMS.source_urls,k))),'claim-source references');
check(CLAIMS.claims.every(c=>/^(supported|seller|unsubstantiated|unsupported|contested|research|not-|false|dynamic|required)/.test(c.status)),'claim statuses explicit');
check(CLAIMS.claims.filter(c=>c.kind.includes('efficacy')||c.kind.includes('mechanism')).every(c=>c.editorial_action.match(/exclude|attribute/)),'product efficacy not adopted');
check(ARTICLE.split(/\s+/).length>=2000,'substantive manuscript');
for(const url of ['doi.org/10.1068/p090483','pubmed.ncbi.nlm.nih.gov/20942363','doi.org/10.1177/0956797613501521','puysegurs-animal-magnetism-files'])check(ARTICLE.includes(url),'article provenance '+url);
for(const h of [A,B,HUB]){check(/<html lang="en">/.test(h),'language');check(/<meta name="viewport"/.test(h),'viewport');check(/name="robots" content="noindex,nofollow"/.test(h),'unpublished metadata');check(!/<script\b/i.test(h),'no scripts');check(!/<iframe\b/i.test(h),'no iframes');check(!/<form\b/i.test(h),'no duplicate forms');check(!/<(?:video|audio)[^>]*\\sautoplay(?:\\s|>)/i.test(h),'no autoplay attribute');check(!/<a\s[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|hypnosislive|brainwaveshots|inspire3|affiliates\.inspire3)\./i.test(h),'no merchant anchors');check(!/fetch\(|localStorage|sessionStorage|gtag\(|pixel\b/i.test(h),'no tracking JS');check(/:focus-visible/.test(h),'focus styles');check(/@media\(max-width:/.test(h),'responsive styles');}
for(const h of [A,B]){check(h.includes('may earn a commission'),'explicit prospective FTC disclosure');check(h.includes('disabled aria-disabled="true"'),'inert merchant CTA');check(h.indexOf('may earn a commission')<h.indexOf('View approved Zen12 offer'),'disclosure before button');check(h.indexOf('View approved Zen12 offer')-h.indexOf('may earn a commission')<500,'disclosure adjacent to CTA');check(h.includes('https://finalvestige.com/focus/'),'existing single Focus route');check(h.includes('not</strong> used or independently tested'),'no claimed personal experience');check(h.includes('https://zen12.com/secret/'),'exact seller source retained in text');}
const buyer=h=>h.slice(h.indexOf('<section id="who">'),h.indexOf('</main>'));
check(buyer(A)===buyer(B),'A and B substantive buyer copy byte-identical');
check(!A.includes('OPTIONAL 42-SECOND FILM'),'A text-only');
check(B.includes('OPTIONAL 42-SECOND FILM'),'B optional film clearly labeled');
check(B.includes('<svg')&&B.includes('<title id="posterTitle">')&&B.includes('<desc id="posterDesc">'),'original accessible SVG poster');
check(B.includes('<details>')&&B.includes('<summary>'),'no-JS optional transcript');
check(B.includes('not an encoded playable film'),'truthful unencoded status');
check(VTT.startsWith('WEBVTT'),'caption grammar header');
check((VTT.match(/-->/g)||[]).length===6,'six caption cues');
check(VTT.includes('00:00:35.000 --> 00:00:42.000'),'42-sec timing');
check(HUB.includes('four')===false||HUB.includes('PERCEPTION & ATTENTION'),'hub streams');
for(const text of ['PERCEPTION & ATTENTION','HISTORY OF SUGGESTION','PRACTICE & REFLECTION','TOOLS UNDER REVIEW'])check(HUB.includes(text),'four stream '+text);
check(HUB.includes('already published')||HUB.includes('Already published'),'existing change blindness canonical');
check(PLAN.includes('UNMATCHED'),'video media IDs not invented');
check(PLAN.includes('NOT COMPUTABLE'),'revenue metric truth');
check(PLAN.includes('refund')&&PLAN.includes('qualified human'),'net revenue quality');
check(!/net revenue[^\n]*[$][0-9]+/i.test(PLAN),'no invented realized revenue');
check(PLAN.includes('Grok')&&PLAN.includes('Praxxis')&&PLAN.includes('Claude'),'ownership');
check(PLAN.includes('50:50'),'controlled allocation hypothesis');
console.log('R437 SOURCE SAFETY & AB PARITY: '+n+'/'+n+' assertions PASS (source-level ONLY; no hosted CI/browser/merchant proof)');
