/* R145 offline audit. Run from repository root with: node mind/r145/test-r145.cjs
   This checks committed HTML/JSON/text. It DOES NOT replace a real browser, CI, checkout or accessibility test. */
"use strict";
const fs=require("node:fs"),assert=require("node:assert/strict"),path=require("node:path");
const here=__dirname;
const read=p=>fs.readFileSync(path.join(here,p),"utf8");
const a=read("zen12-premium-presell-a-review-only.html");
const b=read("zen12-premium-presell-b-review-only.html");
const article=read("expectancy-suggestion-investigation.md");
const plan=read("activation-decision-experiment-contract.md");
const raw=read("claim-source-commerce-gates.json");
const data=JSON.parse(raw);
let pass=0;
function check(name,fn){try{fn();pass++;process.stdout.write("PASS "+name+"\n")}catch(e){process.stderr.write("FAIL "+name+" "+e.message+"\n");throw e}}
function clean(s){return s.replace(/data-variant="[AB]"/,"").replace(/<!-- R145 unpublished pilot: [AB]/,"").replace(/<section class="film"[\s\S]*?<\/section>/,"")}
check("one exact Premium SKU both",()=>{for(const v of [a,b])assert.match(v,/Zen12 Premium/)});
check("12 / 4 / 48 exact product contents",()=>{for(const v of [a,b]){assert.match(v,/twelve levels/);assert.match(v,/four listening formats/);assert.match(v,/48 MP3s/)}});
check("seller source included",()=>{for(const v of [a,b])assert.match(v,/https:\/\/zen12\.com\/hnp/)});
check("date-stamped landing display not checkout",()=>{for(const v of [a,b]){assert.match(v,/November 5, 2026/);assert.match(v,/final checkout total is not verified/) }});
check("explicit seller limitations",()=>{for(const v of [a,b]){assert.match(v,/seller/);assert.match(v,/not independently tested/);}});
check("FTC disclosure in both",()=>{for(const v of [a,b])assert.match(v,/Final Vestige may earn a commission at no additional cost to you/)});
check("disclosure BEFORE purchasing button",()=>{for(const v of [a,b])assert(v.indexOf("Final Vestige may earn a commission")<v.indexOf("<button"))});
check("hard disabled purchasing controls",()=>{for(const v of [a,b])assert.match(v,/<button type="button" disabled aria-disabled="true">/)});
check("release HARD_HOLD both",()=>{for(const v of [a,b])assert.match(v,/data-release="HARD_HOLD"/)});
check("no active earning CTA anchors",()=>{for(const v of [a,b]){assert(!/<a[^>]*\b(?:affiliate|ref=|hop=|hoplink|clickbank)\b/i.test(v))}});
check("no forms or embedded scripts",()=>{for(const v of [a,b]){assert(!/<(script|form|iframe|video|audio)\b/i.test(v))}});
check("no external assets or pixels",()=>{for(const v of [a,b]){assert(!/(src\s*=|@import|url\s*\()/i.test(v))}});
check("no forced autoplay",()=>{for(const v of [a,b])assert(!/autoplay/i.test(v))});
check("no external merchant purchase button target",()=>{for(const v of [a,b])assert(!/<a[^>]*>[^<]*(?:Buy Now|Purchase Zen12|Checkout)[^<]*<\/a>/i.test(v))});
check("one native Focus link, no replacement signup",()=>{for(const v of [a,b])assert.match(v,/https:\/\/finalvestige\.com\/focus\//)});
check("keyboard visible focus",()=>{for(const v of [a,b])assert.match(v,/:focus-visible/)});
check("reduced motion preference",()=>{for(const v of [a,b])assert.match(v,/prefers-reduced-motion:reduce/)});
check("mobile width control",()=>{for(const v of [a,b])assert.match(v,/clamp\(/)});
check("native no-JS FAQ details",()=>{for(const v of [a,b])assert.match(v,/<details><summary>/)});
check("variant A no film",()=>assert(!/class="film"/.test(a)));
check("variant B original 40 second storyboard",()=>{assert.match(b,/class="film"/);assert.match(b,/00:34–00:40/);assert.match(b,/NOT playable/);});
check("variant B has alt-labeled poster",()=>assert.match(b,/role="img" aria-label=/));
check("B same buyer information as A",()=>assert.equal(clean(a),clean(b)));
check("investigation no product earning links",()=>{assert(!/\]\(https?:\/\/[^)]+(?:\?ref=|affiliate|hoplink|hop=)/i.test(article));assert.match(article,/Puységur/);});
check("investigation has cited scientific sources",()=>{for(const u of ["10.1002/ch.146","10.1371/journal.pone.0286023","10.1111/acps.13225"])assert(article.includes(u))});
check("ledger counts",()=>{assert(data.sources.length>=15);assert(data.claims.length>=20);assert(data.gates.length>=20)});
check("all commercial gates closed",()=>assert(data.gates.every(g=>g.verified===false && g.evidence===null)));
check("all creator IDs unknown",()=>assert(data.social_routes.every(x=>x.media_id===null && x.published_social_url===null)));
check("KPI not fabricated",()=>assert(data.commerce_measurement.kpi_net_per_1000===null));
check("fraudulent sale status absent",()=>assert(!/"verified":true/.test(raw)));
check("FTC URLs and purchase source",()=>{for(const x of ["www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides","www.ftc.gov/business-guidance/resources/health-products-compliance-guidance","https://zen12.com/hnp"])assert(raw.includes(x))});
check("plan has owned Payhip fallback and merchant outreach UNSENT",()=>{assert(plan.includes("Payhip"));assert(plan.includes("NOT SENT"));assert(plan.includes("written named partner approval"))});
check("no claimed net sales",()=>{assert(plan.includes("NOT COMPUTABLE")||plan.includes("NOT_COMPUTABLE"))});
check("30/7 day and 1000 session KPI",()=>{assert(plan.includes("30-day"));assert(plan.includes("1,000 qualified human sessions"))});
check("no off-topic homepage edits planned",()=>{assert(plan.includes("homepage PR #49"));assert(plan.includes("canonical Mind hub #172"))});
function shouldRejectDisclosureGone(html){return !/Final Vestige may earn a commission at no additional cost to you/.test(html)}
check("negative test disclosure removal flagged",()=>assert(shouldRejectDisclosureGone(a.replace("Final Vestige may earn a commission at no additional cost to you",""))));
function shouldRejectEnabled(html){return !/<button type="button" disabled aria-disabled="true">/.test(html)}
check("negative test enabled buying button flagged",()=>assert(shouldRejectEnabled(a.replace(" disabled aria-disabled=\"true\"",""))));
function shouldRejectScript(html){return /<(script|iframe|form)\b/i.test(html)}
check("negative test script injection flagged",()=>assert(shouldRejectScript(a+"<script>alert(1)</script>")));
function shouldRejectOpenGate(x){return x.gates.some(g=>g.verified!==false)}
check("negative test approval fabrication flagged",()=>assert(shouldRejectOpenGate({...data,gates:[{...data.gates[0],verified:true},...data.gates.slice(1)]})));
process.stdout.write("FINAL "+pass+" / "+pass+" structural + negative checks PASSED (offline source audit only)\n");
