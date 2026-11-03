// Run from this directory OR repository root: node --test path/to/test-r92.mjs
// Native Node 22+; offline, no dependencies, no network requests.
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {ACTIVATION,verifySynthetic,aggregateSynthetic,activateMerchantLink,collectLiveEvent,inferSalesFromClicks} from "./privacy-attribution.mjs";
const dir=dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(join(dir,n),"utf8");
const A=read("zen12-A-text.blocks.html"),B=read("zen12-B-film-concept.blocks.html"),hub=read("mind-hub-noncanonical.blocks.html"),claims=JSON.parse(read("claims-and-permissions.json")),article=read("investigation.md"),guide=read("zen12-guide.md");
const captions=read("film-captions.vtt"),renderer=read("film-renderer.py");
const publicPages=[A,B,hub];
const vendorHref=/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i;
const figure=/<figure class="film"[^>]*>[\s\S]*?<\/figure>/;
function sample(extra={}){return {synthetic:true,event:"guide_view",topic:"zen12-guide",source_bucket:"organic-search",variant:"A",...extra};}
test("source investigations contain identifiable scholarly DOI references",()=>{for(const doi of ["10.1037/0278-7393.21.4.803","10.1016/S0022-5371(74)80011-3","10.1111/j.1467-9280.1997.tb00417.x"])assert.ok(article.includes(doi))});
test("investigation has NO commercial solicitation",()=>{assert.doesNotMatch(article,/<a[^>]*href|affiliate link|Buy Zen12/i)});
test("claim matrix includes at least 30 explicit decisions and source rows",()=>{assert.ok(claims.claims.length>=30);assert.ok(claims.sources.length>=15)});
test("all launch gates are false",()=>assert.ok(Object.values(claims.release_gates).every(v=>v===false)));
test("matrix is explicitly synthetic and disallows affiliate URLs",()=>{assert.equal(claims.tracking_mode,"SYNTHETIC_ONLY");assert.equal(claims.current_live_affiliate_urls,0)});
test("A and B share identical substantive HTML",()=>{assert.match(B,figure);assert.equal(B.replace(figure,"").replace('data-fv-pilot="video-concept"','data-fv-pilot="text"'),A)});
test("A has no optional video figure, B exactly one",()=>{assert.doesNotMatch(A,figure);assert.equal((B.match(/data-fv-optional-film=/g)||[]).length,1)});
test("B has accessible text-first headings",()=>{assert.ok(B.indexOf("<h1 ")<B.indexOf("<figure "));assert.match(B,/role="img" aria-labelledby=/)});
test("B transcript includes all six timed scenes",()=>{for(const time of ["00–06s","06–12s","12–19s","19–26s","26–33s","33–40s"])assert.ok(B.includes(time))});
test("no unreachable, fake, autoplaying, external video element",()=>{for(const p of publicPages){assert.doesNotMatch(p,/<video\b|<iframe\b|<[^>]+\sautoplay(?:\s|=|>)|src=["\x27]https?:\/\/(?:player\.vimeo|youtube\.com\/embed)/i)}});
test("no merchant destination in any public candidate",()=>{for(const p of publicPages)assert.doesNotMatch(p,vendorHref)});
test("near-CTA affiliate disclosure within same aside",()=>{for(const p of [A,B]){const m=p.match(/<aside class="checkout"[\s\S]*?<\/aside>/);assert.ok(m);assert.match(m[0],/may earn a commission at no additional cost/);assert.match(m[0],/<button[^>]*\sdisabled\s/) }});
test("purchase controls are native disabled buttons not aria-only",()=>{for(const p of [A,B])assert.match(p,/<button type="button" disabled/)});
test("pages contain no duplicate signup, active tracker, or outbound JS",()=>{for(const p of publicPages){assert.doesNotMatch(p,/<form\b|wp:jetpack\/subscriptions|<script\b|<iframe\b|dataLayer|localStorage|navigator\.sendBeacon/i)}});
test("two public resources link only to verified FV links",()=>{for(const p of [A,B,hub])assert.match(p,/https:\/\/finalvestige\.com\/focus\//)});
test("hub has exactly four streams",()=>{for(const id of ["perception","suggestion","practice","tools"])assert.match(hub,new RegExp('id="'+id+'"'))});
test("no new top-level WordPress navigation write",()=>assert.doesNotMatch(hub,/<wp:navigation|wp:jetpack/i));
test("guide qualifies unsupported hour equivalence",()=>assert.match(guide,/does not establish|does not prove/i));
test("attribution hard disabled by default",()=>{assert.equal(ACTIVATION.collect_live,false);assert.equal(ACTIVATION.emit_merchant_click,false);assert.equal(ACTIVATION.ingest_partner_purchase_records,false)});
test("only categorical fields accepted",()=>{assert.deepEqual(verifySynthetic(sample()),sample());for(const e of [sample({email:"x@y.z"}),sample({url:"https://hi"}),sample({ip:"1.2.3.4"}),sample({timestamp:1}),sample({userAgent:"x"}),sample({synthetic:false}),sample({variant:"C"}),sample({source_bucket:"raw-google-url"})])assert.throws(()=>verifySynthetic(e))});
test("small cells suppressed, 20 distinct synthetic entries produce aggregate",()=>{const x=Array.from({length:19},()=>sample());assert.deepEqual(aggregateSynthetic(x),[]);x.push(sample());assert.deepEqual(aggregateSynthetic(x),[{dimensions:["guide_view","zen12-guide","organic-search","A"],count:20}])});
test("cannot lower privacy suppression threshold",()=>assert.throws(()=>aggregateSynthetic([sample()],19)));
test("no live events, merchant links, or conversion inference can be activated",()=>{assert.throws(activateMerchantLink);assert.throws(collectLiveEvent);assert.throws(inferSalesFromClicks)});

test("source-controlled renderer spans 480 frames and no network",()=>{assert.match(renderer,/W,H,FPS,SECS=540,960,12,40/);assert.match(renderer,/range\(FPS\*SECS\)/);assert.doesNotMatch(renderer,/requests\.|https:\/\/|urllib\.|socket\./i)});
test("six WebVTT cues cover exact full forty seconds",()=>{assert.match(captions,/^WEBVTT/);assert.equal((captions.match(/-->/g)||[]).length,6);assert.match(captions,/00:00:00\.000 --> 00:00:06\.000/);assert.match(captions,/00:00:33\.000 --> 00:00:40\.000/)});
