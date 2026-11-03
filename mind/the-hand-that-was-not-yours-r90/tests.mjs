/**
 * Mind R90 source-controlled regression suite.
 * Run locally from repository root:
 * node --test mind/the-hand-that-was-not-yours-r90/tests.mjs
 * Tests assert safety invariants; successful tests DO NOT authorize publication.
 */
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {ATTRIBUTION_ENABLED,MIN_AGGREGATE_GROUP,validateSyntheticEvent,summarizeSyntheticEvents} from "./attribution.mjs";
const here=dirname(fileURLToPath(import.meta.url));
const load=n=>readFileSync(join(here,n),"utf8");
const a=load("zen12-a.blocks.html"), b=load("zen12-b.blocks.html"), core=load("zen12-guide-core.html");
const hub=load("mind-hub-noncanonical.blocks.html"), iv=load("investigation.md"), matrix=JSON.parse(load("claims-and-gates.json"));
const stripOutside=html=>html.slice(html.indexOf('<article class="fv-r90-guide"'),html.indexOf('</article>')+'</article>'.length);
test("A and B embed byte-identical substantive guide",()=>{assert.equal(stripOutside(a),core);assert.equal(stripOutside(b),core)});
test("No live affiliate URLs or merchant outbound anchors inside disabled offer",()=>{for(const h of [a,b]){const seg=h.slice(h.indexOf('<section class="fv-r90-offer"'),h.indexOf('</section>',h.indexOf('<section class="fv-r90-offer"'))+10);assert.doesNotMatch(seg,/<a\s/i);assert.doesNotMatch(seg,/(href=|data-affiliate=|onclick=|window\.location)/i)}});
test("No clickable seller destinations anywhere in either unpublished variant",()=>{for(const h of [a,b]) assert.doesNotMatch(h,/<a\\b[^>]*href=["']https:\\/\\/(?:zen12\\.com|inspire3\\.com|affiliates\\.inspire3\\.com)/i)});
test("Native disabled control, not merely aria-disabled",()=>{for(const h of [a,b]) assert.match(h,/<button\b[^>]*\bdisabled(?:\s|>|=)/i)});
test("Clear commission disclosure precedes control in both variants",()=>{for(const h of [a,b]){const p=h.indexOf("If a future authorized earning link");const q=h.indexOf('<button type="button" disabled');assert.ok(p>=0&&q>p&&q-p<350)}});
test("No third-party media, autoresponse, forms, or executable scripts",()=>{for(const h of [a,b,hub]) assert.doesNotMatch(h,/<(?:script|iframe|form)\b|<video\b[^>]*autoplay|on[a-z]+\s*=|fetch\s*\(/i)});
test("Variant B conveys media is a nonplayable concept, never fake playback",()=>{assert.match(b,/not hosted or playable/i);assert.match(b,/Original 9:16 poster concept/);assert.doesNotMatch(b,/<video\b|<iframe\b/i)});
test("Film transcript accessible without JS, six timed scenes",()=>{assert.match(b,/<details[^>]+open>/i);const list=b.split('<section class="fv-r90-film"')[1].split('</section>')[0];assert.equal((list.match(/<li><time>/g)||[]).length,6);assert.match(list,/00:34–00:40/)});
test("Investigation is commercial-free and source-aware",()=>{assert.match(iv,/Botvinick/);assert.match(iv,/Lush/);assert.doesNotMatch(iv,/affiliate link|buy now|purchase through|commission/i)});
test("Hub links real published resources only",()=>{assert.match(hub,/https:\/\/finalvestige\.com\/focus\//);assert.match(hub,/puysegurs-animal-magnetism-files/);assert.doesNotMatch(hub,/<form\b/i);assert.match(hub,/noncanonical|noncanonical WordPress/i)});
test("Claims catalog includes original science, official merchant and FTC",()=>{assert.ok(matrix.sources.length>=15);assert.ok(matrix.claims.length>=30);assert.ok(matrix.sources.some(x=>x.url.includes("ftc.gov")));assert.ok(matrix.sources.some(x=>x.url.includes("zen12.com/hnp")))});
test("All required release gates remain hard false",()=>{assert.ok(Object.keys(matrix.release_gates).length>=18);assert.ok(Object.values(matrix.release_gates).every(v=>v===false));assert.equal(matrix.meta.affiliate_url,null)});
test("Research is not confused with Zen12-specific efficacy",()=>{assert.ok(matrix.claims.find(x=>x.id==="c12").status.includes("unsubstantiated"));assert.ok(matrix.claims.find(x=>x.id==="c18").status.includes("false"))});
test("Attribution off, without external network, cookies, or local storage",()=>{assert.equal(ATTRIBUTION_ENABLED,false);const src=load("attribution.mjs");assert.doesNotMatch(src,/\b(fetch|sendBeacon|XMLHttpRequest|localStorage|sessionStorage|document\.cookie)\s*\(/i)});
test("Data validation rejects PII/untrusted payloads",()=>{const item={event:"guide_view",topic:"zen12",source:"organic"};assert.equal(validateSyntheticEvent(item).topic,"zen12");for(const k of ["email","ip","referrer","url","click_id","utm_content","user_agent"]){assert.throws(()=>validateSyntheticEvent({...item,[k]:"test@example.com"}))}assert.throws(()=>validateSyntheticEvent({...item,source:"https://bad.example"}))});
test("Aggregation suppresses small cells and retains k>=20",()=>{const row={event:"guide_view",topic:"zen12",source:"organic"};assert.deepEqual(summarizeSyntheticEvents(Array.from({length:MIN_AGGREGATE_GROUP-1},()=>row)),[]);const result=summarizeSyntheticEvents(Array.from({length:MIN_AGGREGATE_GROUP},()=>row));assert.equal(result.length,1);assert.equal(result[0].count,20)});
test("Privacy mutation: prototype or unknown event is rejected",()=>{assert.throws(()=>validateSyntheticEvent(Object.create(null)));assert.throws(()=>validateSyntheticEvent({event:"sale",topic:"zen12",source:"organic"}))});
test("Guide contains free exercise and exact offer options",()=>{for(const t of ["twelve levels","four styles","forty-eight MP3s","Beginner","Advanced","three different occasions"]){assert.ok(core.toLowerCase().includes(t.toLowerCase())||t==="three different occasions"&&core.includes("three different occasions"),t)}});
