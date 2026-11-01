import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {ATTRIBUTION_ENABLED,validateSynthetic,summarizeSynthetic,browserAttribution} from "./attribution.mjs";
const root=dirname(fileURLToPath(import.meta.url));
const read=f=>readFileSync(join(root,f),"utf8");
const a=read("presell-a-text-only.html"),b=read("presell-b-video-concept.html");
const guide=read("zen12-buyer-guide.md"),article=read("investigation.md"),hub=read("mind-archive-noncanonical.html"),csv=read("claims-permissions.csv"),vtt=read("film.vtt");
function core(x){const m=x.match(/<main id="fv53-[AB]-main"[^>]*>([\s\S]*?)<\/main>/);assert.ok(m,"guide core found");return m[1];}
function invariant(x){
 assert.match(x,/If you purchase through an approved link on this guide, Final Vestige may earn a commission/);
 assert.match(x,/<button type="button" disabled aria-disabled="true">Visit seller/);
 assert.doesNotMatch(x,/<a\s[^>]*href="https:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive)\.com/i);
 assert.doesNotMatch(x,/<(script|form|iframe|input)\b/i);
 assert.doesNotMatch(x,/\bonclick\s*=|\bonload\s*=|autoplay|https:\/\/.*(?:clickid|aff_id|affid)/i);
 const d=x.indexOf("If you purchase through an approved link"),c=x.indexOf('<button type="button" disabled',d);
 assert.ok(d>0&&c>d&&c-d<500,"commission disclosure adjacent to disabled control");
 assert.match(x,/aria-labelledby=/);assert.match(x,/class="fv53-skip"/);
}
test("source article original and substantive",()=>{
 assert.ok(article.trim().split(/\s+/).length>1500);
 for(const s of ["Peter Thompson","Bartlett","Lewis","Puységur","1980","1993","2001"])assert.ok(article.includes(s));
 assert.doesNotMatch(article,/Zen12|Hypnosis Live|Brainwave Shots/i);
});
test("exact merchant offer guide, independent limits",()=>{
 assert.ok(guide.trim().split(/\s+/).length>1300);
 for(const x of ["zen12.com/hnp","zen12.com/about","zen12.com/research","zen12.com/getstarted","24 MP3","48 MP3","twelve-minute","no price","cannot fill that gap"])assert.ok(guide.toLowerCase().includes(x.toLowerCase()),x);
});
test("same substantive A/B guide, no inactive presell drops",()=>{
 assert.equal(core(a),core(b));assert.ok(core(a).length>9500);
 invariant(a);invariant(b);
});
test("video B is honest and accessible with complete no-JS transcript",()=>{
 assert.doesNotMatch(a,/<svg\b/);assert.match(b,/<svg[^>]+role="img"/);
 assert.match(b,/<details>/);assert.match(b,/40-second film transcript/);
 assert.match(b,/not a participant test/i);
 assert.doesNotMatch(b,/<video\b|<audio\b|<iframe\b/);
});
test("noncanonical /mind/ never links to unlaunched route",()=>{
 invariant(hub.replace("<span>Zen12 independent guide — unpublished</span>",'<span>Zen12 independent guide — unpublished</span>') /* no active merchant */);
 assert.match(hub,/PR #172 is canonical/);
 assert.match(hub,/https:\/\/finalvestige.com\/focus\//);
 assert.doesNotMatch(hub,/href="https:\/\/finalvestige.com\/mind\//);
});
test("matrix has real-source distinctions and strong holds",()=>{
 let rows=csv.trim().split("\n");assert.ok(rows.length>=39);
 for(let x of ["hard_hold","hold_for_terms","exclude","allow_seller_only","FTC","no_authenticated_partner_record"])assert.ok(rows.join("\n").includes(x));
});
test("categorical validator rejects personal data and prototypes are OFF",()=>{
 assert.equal(ATTRIBUTION_ENABLED,false);assert.equal(browserAttribution().enabled,false);
 let clean={topic:"zen12",channel:"organic",variant:"A",action:"guide"};
 assert.equal(validateSynthetic(clean).topic,"zen12");
 for(const bad of [{...clean,email:"private@example.com"},{...clean,userId:"123"},{...clean,referrer:"https://private/?q=x"},{...clean,ip:"127.0.0.1"},{...clean,topic:"other"},null])assert.equal(validateSynthetic(bad),null);
 assert.deepEqual(summarizeSynthetic(Array(19).fill(clean)),[]);
 assert.equal(summarizeSynthetic(Array(20).fill(clean))[0].count,20);
});
test("captions cover exactly the 40-second schematic film",()=>{
 assert.ok(vtt.startsWith("WEBVTT"));
 assert.equal((vtt.match(/--> /g)||[]).length,6);
 assert.ok(vtt.includes("00:00:40.000"));
});
test("mutation guards catch forbidden active merchant links and fake play",()=>{
 const live=a.replace(/<button type="button" disabled aria-disabled="true">Visit seller — held for approval<\/button>/,'<a href="https://zen12.com/hnp">Buy Now</a>');
 assert.throws(()=>invariant(live));
 const script=b.replace("</section>","<script>fetch('/tracking')</script></section>");
 assert.throws(()=>invariant(script));
 const button=b.replace('disabled aria-disabled="true"','');
 assert.throws(()=>invariant(button));
});
