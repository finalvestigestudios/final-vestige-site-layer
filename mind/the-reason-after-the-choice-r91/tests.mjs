/**
 * Run at repo root:
 * node --test mind/the-reason-after-the-choice-r91/tests.mjs
 * A safety check suite, not production approval.
 */
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {ATTRIBUTION_ENABLED,MIN_REPORTING_GROUP,validateSyntheticEvent,summarizeSyntheticEvents} from "./attribution.mjs";
const here=dirname(fileURLToPath(import.meta.url));
const file=n=>readFileSync(join(here,n),"utf8");
const a=file("zen12-text-only.blocks.html"), b=file("zen12-with-film.blocks.html"), core=file("zen12-guide-core.blocks.html");
const hub=file("mind-hub-noncanonical.blocks.html"), investigation=file("investigation.md");
const matrix=JSON.parse(file("claims-and-activation.json"));
const articleSegment=h=>h.slice(h.indexOf('<article class="fv-r91-guide"'),h.indexOf('</article>')+'</article>'.length);
test("A/B contain identical substantive guide after removing optional film",()=>{assert.equal(articleSegment(a),core);assert.equal(articleSegment(b).replace(/\n<figure class="fv-r91-film"[\s\S]*?<\/figure>/,""),core)});
test("A/B both carry disclosure adjacent to a genuinely disabled button",()=>{
 for(const h of [a,b]){const section=h.match(/<section class="fv-r91-offer"[^>]*>[\s\S]*?<\/section>/)?.[0];assert.ok(section);assert.match(section,/Affiliate disclosure:/);
 const buttons=[...section.matchAll(/<button\b([^>]*)>/g)];assert.equal(buttons.length,1);assert.match(buttons[0][1],/(?:^|\s)disabled(?:\s|=|$)/);
 assert.ok(section.indexOf("Affiliate disclosure:")<section.indexOf("<button"));
 assert.doesNotMatch(section,/<a\b|\bhref=|onclick=|data-affiliate=/i);}
});
test("No clickable merchant links in either variant",()=>{for(const h of [a,b])assert.doesNotMatch(h,/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com)/i)});
test("There are no web tracking tags, forms, embeds, or event handlers",()=>{
 for(const h of [a,b,hub]){assert.doesNotMatch(h,/<(?:script|iframe|form|input)\b/i);assert.doesNotMatch(h,/\bon(?:click|load|error|submit)\s*=/i);assert.doesNotMatch(h,/gtag\(|fbq\(|pixel|localStorage|document\.cookie/i);}
});
test("A/B contain no live video URL and cannot autoplay",()=>{for(const h of [a,b]){assert.doesNotMatch(h,/(?:autoplay|<video\b|<source\b|\.mp4(?:["'?\s]|$))/i);}});
test("The film variant has accessible SVG title, visible fallback and six cues",()=>{
 assert.match(b,/<svg\b[^>]*role="img"[^>]*aria-labelledby=/);
 assert.match(b,/<title id="fv-r91-poster-title">/);
 assert.match(b,/<details open>/);
 assert.equal((b.match(/<li>\d+–\d+s:/g)||[]).length,6);
});
test("No evidence claim of a successful video conversion test",()=>{assert.doesNotMatch(a+b,/video (?:increases|doubled|improves) conversion(?:s| rates)/i);});
test("Guide explains the seller's actual configurations",()=>{for(const n of ["12 minutes","12 levels","four listening styles","48 MP3s","24 MP3s"])assert.ok(core.includes(n),n)});
test("Guide disavows unsupported hour-equivalence and product-specific efficacy",()=>{assert.match(core,/Neither wording/);assert.match(core,/not a clinical trial of Zen12/);});
test("Investigative article isolated from earning language",()=>{assert.doesNotMatch(investigation,/href="https?:\/\/zen12|earn a commission|affiliate purchase link/i);assert.ok(investigation.split(/\s+/).length>1700)});
test("Hub has exactly four distinct streams and uses known live pages",()=>{for(const s of ["Perception &amp; attention","History of suggestion","Practice &amp; reflection","Tools under review"])assert.match(hub,new RegExp(s));assert.match(hub,/2026\/11\/02\/mesmerism/);assert.match(hub,/2026\/11\/02\/change-blindness/);});
test("No redundant mailing-list forms",()=>{assert.doesNotMatch(hub+a+b,/<form\b/i);assert.match(hub,/existing Dispatch\/Jetpack funnel/)});
test("Seller, evidence and regulatory sources are distinct",()=>{assert.ok(matrix.sources.length>=20);assert.ok(matrix.claims.length>=30);assert.ok(matrix.sources.find(s=>s.id==="S08").url==="https://zen12.com/hnp");assert.ok(matrix.sources.find(s=>s.id==="S15").url.includes("ftc.gov"));});
test("No activation gate inadvertently enabled",()=>{assert.ok(Object.keys(matrix.activation_gates).length>=20);assert.ok(Object.values(matrix.activation_gates).every(v=>v===false));assert.equal(matrix.meta.earning_url,null);assert.equal(matrix.meta.partner_approval_verified,false)});
test("No raw price, commission or claim of product trial",()=>{assert.equal(matrix.meta.price,null);assert.equal(matrix.meta.commission_rate,null);assert.equal(matrix.meta.review_not_product_trial,true)});
test("Tracking is disabled and reporting threshold is 20",()=>{assert.equal(ATTRIBUTION_ENABLED,false);assert.equal(MIN_REPORTING_GROUP,20)});
const valid={topic:"choice-blindness",surface:"organic",action:"guide_view",variant:"text"};
test("Synthetic permitted event validation",()=>{assert.deepEqual(validateSyntheticEvent(valid),valid)});
test("Reject raw URL, email, referrer, IP and visitor ID",()=>{for(const k of ["url","email","referrer","ip","visitor_id","utm_campaign"]){assert.throws(()=>validateSyntheticEvent({...valid,[k]:"sensitive"}));}});
test("Reject invalid categoricals",()=>{assert.throws(()=>validateSyntheticEvent({...valid,surface:"spam"}));assert.throws(()=>validateSyntheticEvent({...valid,topic:"anything"}));});
test("Small groups are suppressed",()=>{assert.deepEqual(summarizeSyntheticEvents(Array(19).fill(valid)),[]);assert.equal(summarizeSyntheticEvents(Array(20).fill(valid))[0].count,20)});
test("Different variants are aggregated separately",()=>{assert.deepEqual(summarizeSyntheticEvents([...Array(19).fill(valid),{...valid,variant:"film"}]),[])});
