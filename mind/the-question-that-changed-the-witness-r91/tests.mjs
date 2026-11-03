import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {dirname,join} from "node:path";
import {fileURLToPath} from "node:url";
import {ENABLED,validateSynthetic,syntheticAggregate} from "./attribution.mjs";
const dir=dirname(fileURLToPath(import.meta.url));
const read=name=>readFileSync(join(dir,name),"utf8");
const a=read("zen12-a.blocks.html"),b=read("zen12-b.blocks.html"),core=read("zen12-guide-core.html"),hub=read("mind-hub-noncanonical.blocks.html"),article=read("investigation.md"),vtt=read("40-second-film-captions.vtt"),matrix=JSON.parse(read("claims-and-gates.json"));
test("A/B have identical complete guide text",()=>{for(const candidate of[a,b])assert(candidate.includes(core))});
test("B contains only additional storyboard, no fake playable file",()=>{assert(!a.includes("<section class=\"fv-r91-film\""));assert(b.includes("fv-r91-film-poster"));assert(b.includes("not a playable film"))});
for(const [label,html]of [["A",a],["B",b]]){
 test(label+" native disabled control",()=>assert.match(html,/<button\b[^>]*\sdisabled\b/i));
 test(label+" disclosure immediately before control",()=>{const c=html.indexOf("Affiliate disclosure for a future authorized link:"),p=html.indexOf("<button");assert(c>=0&&p>c&&p-c<450)});
 test(label+" merchant link zero even among references",()=>assert(!/<a\s[^>]*href=["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com)/i.test(html)));
 test(label+" no scripts, forms, third-party media, autoplay",()=>assert(!/<(?:script|form|iframe|video|audio)\b|\sautoplay(?:\s|=|>)|gtag\s*\(/i.test(html)));
 test(label+" links existing Focus resource",()=>assert(html.includes("https://finalvestige.com/focus/")));
 test(label+" reduced motion, mobile, focus visible",()=>{for(const needle of["prefers-reduced-motion","max-width:390px",":focus-visible"])assert(html.includes(needle))});
}
test("hub four streams and no new form",()=>{for(const s of["Perception &amp; attention","History of suggestion","Practice &amp; reflection","Tools under review"])assert(hub.includes(s));assert(!/<form\b/i.test(hub))});
test("investigation contains independent scholarly provenance and no affiliate endorsement",()=>{assert(article.trim().split(/\s+/).length>=1900);for(const x of["Loftus","Wiechert","Sherman","Brassil","Puységur"])assert(article.includes(x));assert(!/zen12|inspire3|affiliate|commission/i.test(article))});
test("caption timeline exactly six cues covering 40 seconds",()=>{const cues=vtt.match(/\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}/g)||[];assert.equal(cues.length,6);assert(cues[0].startsWith("00:00:00.000"));assert(cues[5].endsWith("00:00:40.000"))});
test("claims and gates source-backed",()=>{assert(matrix.sources.length>=20);assert(matrix.decisions.length>=35);assert(matrix.sources.every(s=>s.url.startsWith("https://")));assert(Object.keys(matrix.gates).length>=20);assert(Object.values(matrix.gates).every(v=>v===false));assert.equal(matrix.release,"HARD_HOLD")});
test("measurement is explicitly off",()=>assert.equal(ENABLED,false));
test("rejects all unexpected identifying fields",()=>{for(const bad of[{event:"guide_view",topic:"zen12",source:"organic",email:"x@y.z"},{event:"guide_view",topic:"zen12",source:"organic",referrer:"https://example.com"},{event:"guide_view",topic:"zen12",source:"https://example.com"},{event:"guide_view",topic:"zen12",source:"organic",ip:"1.2.3.4"},{event:"guide_view",topic:"zen12",source:"organic",url:"/foo"}])assert.throws(()=>validateSynthetic(bad))});
test("aggregate suppressed until at least 20 synthetic observations",()=>{const row={event:"guide_view",topic:"zen12",source:"organic"};assert.equal(syntheticAggregate(Array(19).fill(row)).length,0);assert.equal(syntheticAggregate(Array(20).fill(row))[0].count,20)});
