// Run after checkout: node --test mind/mind-wandering-zen12-r41/tests.mjs
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {ENABLED,validateSynthetic,collect,outbound,summarizeSynthetic} from "./privacy-attribution.mjs";
const root=dirname(fileURLToPath(import.meta.url));
const read=name=>readFileSync(join(root,name),"utf8");
const A=read("zen12-text-only.wp.html"),B=read("zen12-video-option.wp.html");
const hub=read("mind-hub-comparison.wp.html"),article=read("investigation.wp.html");
const captions=read("film-captions.vtt"),matrix=read("claim-and-permission-matrix.csv");
const getCore=s=>s.match(/<div data-core-guide="same-a-b">([\s\S]*?)<\/div><aside/)[1];
test("substantive A/B guides are byte-identical",()=>assert.equal(getCore(A),getCore(B)));
test("no active merchant links",()=>{for(const h of [A,B,hub]) assert.doesNotMatch(h,/<a\s[^>]*href="https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i)});
test("near-offer disclosure and disabled control",()=>{
 for(const h of [A,B]){let p=h.lastIndexOf('class="fv-affiliate-hold"'),q=h.indexOf("<button",p);assert(p>=0&&q>p);assert.match(h.slice(p,q),/may earn a commission at no additional cost to you/);assert.match(h.slice(q,q+250),/disabled aria-disabled="true"/)}
});
test("no active scripts forms iframes autoplay",()=>{for(const h of [A,B,hub]){assert.doesNotMatch(h,/<form\b|<iframe\b|<script\b|<video\b[^>]*\bautoplay\b|onclick\s*=/i);assert.doesNotMatch(h,/(?:utm_source=|ref=affiliate|affiliate_id=|click_id=)/i)}});
test("optional film is truthful unhosted static poster",()=>{assert.match(B,/not hosted/);assert.doesNotMatch(B,/<video\b|<audio\b|<source\b/i);assert.doesNotMatch(A,/class="fv-film"/);assert.match(B,/<details><summary>/);assert.match(B,/<svg\s[^>]*role="img"/)});
test("caption timeline spans 40 seconds in six cues",()=>{assert.match(captions,/^WEBVTT/);assert.match(captions,/00:00:00\.000 --> 00:00:06\.000/);assert.match(captions,/00:00:34\.000 --> 00:00:40\.000/);assert.equal((captions.match(/-->/g)||[]).length,6)});
test("science article cited and merchant-free",()=>{assert.match(article,/10\.1016\/j\.neuroimage\.2011\.07\.008/);assert.match(article,/Puys/);assert.doesNotMatch(article,/(zen12\.com|inspire3\.com|data-affiliate)/i)});
test("claims matrix includes evidence and permissions",()=>{assert(matrix.split("\n").length>65);assert.match(matrix,/SELLER_OUTCOME_UNPROVEN/);assert.match(matrix,/FTC/);assert.match(matrix,/COMMERCE_PERMISSIONS/)});
test("privacy hard-off and rejects personal data",()=>{
 assert.equal(ENABLED,false);assert.equal(collect({}),false);assert.equal(outbound({}),false);
 const e={topic:"zen12_guide",variant:"text_only",channel:"search",action:"guide_view"};
 assert.deepEqual(validateSynthetic(e),e);
 for(const f of ["email","ip","url","visitorId","referrer"])assert.equal(validateSynthetic({...e,[f]:"value"}),null);
 assert.equal(validateSynthetic({...e,channel:"https://example.com/?email=me"}),null);
 assert.equal(validateSynthetic({...e,topic:"__proto__"}),null);assert.equal(validateSynthetic(null),null);
 assert.equal(summarizeSynthetic(Array(9).fill(e)).length,0);
 assert.equal(summarizeSynthetic(Array(10).fill(e)).length,1);
 assert.equal(summarizeSynthetic(Array(10).fill(e),9).length,0);
});

test("regression guards kill deliberately unsafe edits",()=>{
 const merchant=A.replace("</article>",'<a href="https://zen12.com/getstarted">Pay</a></article>');
 const active=A.replace('disabled aria-disabled="true"','');
 const noNear=A.replace(/(<aside class="fv-affiliate-hold"[^>]*>[\s\S]*?)may earn a commission at no additional cost to you/,'$1');
 const form=B.replace("</article>",'<form><input type="email"></form></article>');
 const autoplay=B.replace("</article>",'<video autoplay src="x.mp4"></video></article>');
 const bad=[merchant,active,noNear,form,autoplay];
 const merchantGuard=h=>!/<a\s[^>]*href="https?:\/\/(?:www\.)?zen12\.com/i.test(h);
 const buttonGuard=h=>{const p=h.lastIndexOf('class="fv-affiliate-hold"'),q=h.indexOf("<button",p);return p>=0&&/disabled aria-disabled="true"/.test(h.slice(q,q+250))};
 const nearGuard=h=>{const p=h.lastIndexOf('class="fv-affiliate-hold"'),q=h.indexOf("<button",p);return p>=0&&h.slice(p,q).includes("may earn a commission at no additional cost to you")};
 assert.equal(merchantGuard(merchant),false);
 assert.equal(buttonGuard(active),false);
 assert.equal(nearGuard(noNear),false);
 assert.match(form,/<form\b/);
 assert.match(autoplay,/<video\b[^>]*autoplay/);
 assert.equal(bad.length,5);
});
