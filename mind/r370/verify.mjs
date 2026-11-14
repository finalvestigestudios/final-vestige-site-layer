import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import path from "node:path";
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(path.join(dir,n),"utf8");
const a=read("ZEN12_A_SOURCE_GUIDE.html"),b=read("ZEN12_B_FILM_CONCEPT.html"),hub=read("MIND_HUB_WP_REVIEW_ONLY.html"),article=read("WHEN_THE_GORILLA_MOVES_FASTER.md"),vtt=read("ORIGINAL_42S_CAPTIONS.vtt"),matrix=JSON.parse(read("CLAIM_SOURCE_AND_RELEASE_MATRIX.json")),plan=read("CONVERSION_FIRST_ACCEPTANCE.md");
let count=0;
function check(yes,label){assert.ok(yes,label);count++}
const articlePart=s=>s.match(/<article>([\s\S]*?)<\/article>/)?.[1];
const withoutFilm=s=>s.replace(/<aside class="panel film"[\s\S]*?<\/aside>/,"");
const activeSalesLinks=s=>/<a\b[^>]*href=["'][^"']*(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)[^"']*["']/i.test(s);
const isUnsafe=s=>/<script\b|<iframe\b|<form\b|\bonclick\s*=|\bonload\s*=|<video\b[^>]*autoplay|(?:src|href)=["']javascript:/i.test(s);
const noPricePromise=s=>!/guaranteed checkout price|pay just \$\d+/i.test(s);
const hasNativeDisabled=s=>/<button\b[^>]*\sdisabled(?:\s|>|=)[^>]*>Merchant review unavailable/i.test(s);
check(article.length>9500,"deep manuscript");check(article.includes("Wallisch")&&article.includes("Simons"),"study authors");check(article.includes("4,493"),"sample reporting");check(article.includes("research manuscript"),"editorial status");check(article.includes("https://doi.org/10.1073/pnas.2214930120"),"2023 primary");check(article.includes("https://doi.org/10.1068/p281059"),"1999 primary");check(article.includes("not a clinical trial"),"historical boundary");check(article.includes("not a product-specific"),"seller efficacy boundary");
for(const [name,s] of [["A",a],["B",b]]){check(s.includes('name="robots" content="noindex,nofollow"'),name+" private prototype");check(hasNativeDisabled(s),name+" native disabled");check(s.includes("Prospective affiliate disclosure:"),name+" adjacent disclosure");check(!activeSalesLinks(s),name+" no seller earning link");check(!isUnsafe(s),name+" no script/forms/iframe");check(s.includes("https://finalvestige.com/focus/"),name+" existing Focus route");check(s.includes("id=\"review\""),name+" commerce near disclosure");check(noPricePromise(s),name+" no checkout promise");}
check(articlePart(a)===withoutFilm(articlePart(b)),"A/B substantive parity");check(b.includes('role="img"')&&b.includes("<desc"),"accessible original SVG");check(b.includes("00:35–00:42"),"transcript covers 42s");check(vtt.startsWith("WEBVTT"),"VTT header");check((vtt.match(/-->/g)||[]).length===6,"six subtitle cues");check(vtt.includes("00:00:42.000"),"42s end");check(/00:00:00.000 --> 00:00:07.000/.test(vtt),"first cue timing");check(matrix.claim_count===matrix.claims.length,"matrix honest count");check(matrix.claims.length>=28,"matrix substantive");check(matrix.gates.length===32&&matrix.gates.every(g=>g.state==="HOLD"),"all 32 release gates HOLD");check(matrix.claims.some(x=>x.status==="unsupported-seller-efficacy"),"unsupported claims flagged");check(matrix.claims.some(x=>x.statement.includes("Final Vestige partner approval")&&x.status==="UNVERIFIED"),"partner rights unverified");check(matrix.claims.some(x=>x.status==="NOT_COMPUTABLE"),"revenue status uncomputed");check(hub.includes("UNPUBLISHED")&&hub.includes("noindex,nofollow"),"hub not live");check(!isUnsafe(hub)&&!activeSalesLinks(hub),"hub safe");check(hub.includes("Perception &amp; Attention")&&hub.includes("History of Suggestion")&&hub.includes("Practice &amp; Reflection")&&hub.includes("Tools Under Review"),"hub four streams");check(plan.includes("NOT COMPUTABLE")&&plan.includes("refund")&&plan.includes("affiliate_outbound"),"revenue contract");check(plan.includes("asset_id")&&plan.includes("Grok")&&plan.includes("Praxxis"),"creator provenance contract");check(plan.includes("UNPUBLISHED")&&plan.includes("no new analytics script"),"no launch or duplicate measurement");
const invalid=[
 ["enable-button",a.replace(/type="button" disabled/,'type="button"'),s=>hasNativeDisabled(s)],
 ["remove-disclosure",a.replace(/Prospective affiliate disclosure:/,""),s=>s.includes("Prospective affiliate disclosure:")],
 ["seller-link",a.replace("</article>",'<a href="https://zen12.com/?affiliate=fake">Buy</a></article>'),s=>!activeSalesLinks(s)],
 ["inject-script",a+"<script>alert(1)</script>",s=>!isUnsafe(s)],
 ["inject-form",a+'<form action="/email"></form>',s=>!isUnsafe(s)],
 ["inject-iframe",b+'<iframe src="https://video.example"></iframe>',s=>!isUnsafe(s)],
 ["drop-vtt-cue",vtt.replace(/00:00:35.000 --> 00:00:42.000[\s\S]*/,""),s=>(s.match(/-->/g)||[]).length===6],
 ["open-commerce-gate",JSON.stringify({...matrix,gates:matrix.gates.map((g,i)=>i===0?{...g,state:"PASS"}:g)}),s=>JSON.parse(s).gates.every(g=>g.state==="HOLD")],
 ["break-variant-parity",b.replace("one modest, safe task","one dangerous task"),s=>articlePart(a)===withoutFilm(articlePart(s))],
 ["aria-only-impostor",a.replace(/<button class="cta" type="button" disabled/,'<button class="cta" type="button" aria-disabled="true"'),s=>hasNativeDisabled(s)]
];
for(const [name,s,shouldPass] of invalid){check(!shouldPass(s),"unsafe mutation rejected: "+name)}
console.log("R370 PASS "+count+" exact local native Node assertions; unsafe mutations rejected "+invalid.length+"/"+invalid.length+". WARNING: Browser, CMS, checkout, Jetpack and hosted CI not exercised.");
