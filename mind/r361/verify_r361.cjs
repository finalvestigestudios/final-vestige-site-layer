// R361 reproducible offline safety/integrity review. Usage: node mind/r361/verify_r361.cjs
// Static source assertions only: NOT browser, checkout, scientific efficacy or WordPress tests.
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=__dirname,read=n=>fs.readFileSync(path.join(root,n),"utf8");
const a=read("ZEN12_A_TEXT.html"),b=read("ZEN12_B_OPTIONAL_42S.html"),
 hub=read("MIND_HUB_REVIEW_ONLY.html"),article=read("THE_HYPNOSIS_APP_PROBLEM.md"),
 plan=read("CONVERSION_ACCEPTANCE_AND_OWNER_HANDOFF.md"),vtt=read("ORIGINAL_42S_CAPTIONS.vtt"),
 matrix=JSON.parse(read("CLAIM_SOURCE_AND_COMMERCE_GATES.json"));
let checks=0;
function ok(cond,description){assert.ok(cond,description);checks++;} 
function refuse(fn,description){assert.throws(fn,description);checks++;}
function evaluate(html){
 assert.match(html,/<!doctype html>/i);
 assert.match(html,/<html lang="en">/);
 assert.match(html,/<meta name="viewport"/);
 assert.match(html,/class="disclosure"[^>]*>Affiliate disclosure:/);
 assert.match(html,/<button class="disabled" type="button" disabled aria-disabled="true">Purchase link not enabled<\/button>/);
 assert.ok(html.indexOf('class="disclosure"')<html.indexOf('class="disabled"'));
 assert.ok(html.indexOf('class="disabled"')-html.indexOf('class="disclosure"')<600);
 assert.doesNotMatch(html,/<script\b|<form\b|<iframe\b|<video\b|<audio\b/i);
 assert.doesNotMatch(html,/<a\b[^>]*href="https:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots|affiliates\.inspire3)\./i);
 assert.doesNotMatch(html,/\bautoplay\b(?=[^<]*\b(?:src|controls)\b)/i);
 assert.doesNotMatch(html,/\bguarantees? (?:mental|focus|cognitive|health)\b|I (?:personally )?(?:used|purchased) Zen12/i);
 assert.match(html,/Seven Day Focus Fieldbook/);
 assert.match(html,/noindex,nofollow/);
 return true;
}
for(const [n,h] of [["A",a],["B",b]]){
 for(const [label,exp] of [
 ["native disabled CTA",/<button class="disabled" type="button" disabled aria-disabled="true">/],
 ["adjacent disclosure",/class="disclosure"[^>]*>Affiliate disclosure:/],
 ["free focus",/href="https:\/\/finalvestige.com\/focus\/"/],
 ["noindex",/noindex,nofollow/],
 ["seller price attributed",/seller (?:page )?displayed|displayed <strong>\$87\.99/i],
 ["product-specific scientific caution",/not independently substantiated/i],
 ["no monetization before approval",/currently no active affiliate link/i],
 ["meta mobile viewport",/name="viewport"/],
 ["no JavaScript",/<main id="content">/],
 ["article trust link",/href="https:\/\/finalvestige.com\/2026\/11\/02\/mesmerism\/"/],
 ["page language",/<html lang="en">/],
 ["own offer HTML semantics",/<section class="offer" aria-labelledby="offer">/]
]) ok(exp.test(h),n+": "+label);
 ok(evaluate(h),n+" aggregate html safety");
}
const start='<section aria-labelledby="reason">',end='</main>';
const core=h=>h.slice(h.indexOf(start),h.indexOf(end));
ok(core(a)===core(b),"A/B exact substantive main content parity");
ok(b.includes('class="film"')&&!a.includes('class="film"'),"Film difference intentional");
ok(b.includes('<summary>Read the full 42-second narration treatment</summary>'),"Visible optional transcript");
ok(b.includes('<svg viewBox="0 0 960 540" role="img"'),"SVG poster has text equivalents");
ok(!b.includes('<video ')&&!b.includes('<audio '),"B storyboard clearly unplayable");
ok(hub.includes('Perception &amp; attention')&&hub.includes('History of suggestion')&&hub.includes('Practice &amp; reflection')&&hub.includes('Tools under review'),"Four streams");
ok(!/<form\b|<script\b|<iframe\b|href="https:\/\/zen12/i.test(hub),"Hub has no form/scripts/merchant link");
ok(hub.includes('The unreliab')&&!hub.includes('href="/mind/'),"Hub editorial without inventing published R361");
ok(article.includes('**168 met the review')&&article.includes('**four reported inclusion')&&article.includes('not a controlled efficacy test'),"Hypnosis review scope");
ok(article.includes('have **not** purchased or used')&&article.includes('no purchase link'),"No fake experience");
ok(article.includes('https://doi.org/10.1080/00207144.2024.2434085'),"Source DOI present");
ok(article.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),"Primary archive bridge");
ok(matrix.claims.length===30,"Exactly 30 classified claims");
ok(Object.keys(matrix.source_inventory).length===18,"18 source URLs");
ok(matrix.gates.length===32&&matrix.gates.every(g=>g.state==="CLOSED"&&g.pass_evidence===null),"All 32 commercial gates closed");
ok(matrix.net_revenue_per_1000_qualified_human_sessions===null&&matrix.rate_state==="NOT_COMPUTABLE","No invented revenue denominator");
ok(matrix.claims.filter(c=>c.decision.startsWith("REJECT")).length>=8,"At least eight rejected claims");
ok(matrix.claims.some(c=>c.id==="R361-10"&&c.decision==="REJECT_UNSUBSTANTIATED"),"Reject hour-equivalence outcome");
ok(matrix.claims.some(c=>c.id==="R361-03"&&c.decision==="HOLD_UNVERIFIED"),"Affiliate approval remains unknown");
ok(plan.includes('Grok owns videos')&&plan.includes('as a production task'),"Grok ownership held");
ok(plan.includes('NOT COMPUTABLE')&&plan.includes('qualified_human_sessions'),"Revenue denominator contract");
ok(plan.includes('No live CMS')&&plan.includes('PR #172'),"Other ownership/release gates");
ok(vtt.startsWith('WEBVTT\n')&&(vtt.match(/-->/g)||[]).length===6,"6 caption cues");
ok(vtt.includes("00:00:35.000 --> 00:00:42.000"),"Timed 42-second end");
const bad=[
 ["remove native disabled",a.replace('type="button" disabled aria-disabled="true"','type="button"')],
 ["seller href injection",a.replace('Purchase link not enabled','<a href="https://zen12.com/">Buy now</a>')],
 ["extra script",a.replace('</main>','<script src="https://example.com/t.js"></script></main>')],
 ["extra subscription form",a.replace('</main>','<form><input type="email"></form></main>')],
 ["missing disclosure",a.replace('Affiliate disclosure:','General note:')],
 ["fake testimonial",a.replace('</main>','<p>I personally used Zen12 and recommend it.</p></main>')],
 ["unsafe guarantee",a.replace('</main>','<p>This guarantees focus for everyone.</p></main>')],
 ["film autoplay",b.replace('</main>','<video src="/video.mp4" autoplay></video></main>')]
];
for(const [label,h] of bad)refuse(()=>evaluate(h),"Must reject "+label);
console.log(JSON.stringify({result:"PASS",assertions:checks,negative_mutations_rejected:bad.length,disclaimer:"static offline assertions; no native browser, CMS, merchant or revenue validation"},null,2));
