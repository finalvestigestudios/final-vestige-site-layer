/* Mind R255 — source-only negative/control test.
 * Run: node mind/r255/test_r255.cjs
 * No network requests, no plugins, no paid endpoints, no CMS writes.
 * Run only against materialized repo checkout containing mind/r255 files.
 */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const dir = __dirname;
const read = name => fs.readFileSync(path.join(dir,name),"utf8");
const names = [
  "ZEN12-A-TEXT-UNPUBLISHED.html",
  "ZEN12-B-OPTIONAL-42S-FILM-CONCEPT-UNPUBLISHED.html",
  "THE-SOUND-THAT-WAS-SUPPOSED-TO-CHANGE-YOUR-BRAIN-UNPUBLISHED.md",
  "CONVERSION-FIRST-OFFER-CREATOR-AB-ACCEPTANCE.md",
  "CLAIM-SOURCE-PARTNER-REVENUE-GATES.json"
];
const baseline = Object.fromEntries(names.map(n => [n,read(n)]));
const asJSON = s => JSON.parse(s);
const removeFilm = s => s.replace(/<section aria-labelledby="film">[\s\S]*?<\/section>/,"");
function validate(f) {
  const A = f[names[0]], B = f[names[1]], article = f[names[2]], plan = f[names[3]], m = asJSON(f[names[4]]);
  assert(A && B && article && plan);
  for(const [variant,html] of [["A",A],["B",B]]) {
    assert(html.startsWith("<!doctype html>"),variant+": valid HTML start");
    assert(/<html lang="en">/.test(html),variant+": language");
    assert(/name="viewport"/.test(html),variant+": viewport");
    assert(/name="robots" content="noindex,nofollow"/.test(html),variant+": draft noindex");
    assert(/<main>/.test(html) && /<h1>/.test(html),variant+": semantic main");
    assert(!/<script\b|<form\b|<iframe\b|<video\b|<audio\b|<link\b|<source\b|<img\b[^>]*src\s*=/i.test(html),variant+": no third party, autoplay, scripts or second forms");
    assert(!/\son(?:load|click|submit|error|mouseover)\s*=/i.test(html),variant+": no handler injection");
    assert(!/<a\b[^>]*href\s*=\s*["'][^"']*(?:zen12|inspire3|hypnosislive|brainwaveshots|payhip)/i.test(html),variant+": no active seller/earning/payment URL");
    assert((html.match(/<button\b/g)||[]).length===1,variant+": exactly one commercial control");
    assert(/<button\b[^>]*\bdisabled\b[^>]*>View merchant offer — unavailable<\/button>/.test(html),variant+": real disabled native control");
    assert(html.includes('id="disclosure"') && html.includes('aria-describedby="disclosure purchase-hold"'),variant+": accessible disclosure");
    const c=html.indexOf('<p id="disclosure"'), b=html.indexOf('<button');
    assert(c>=0 && b>c && b-c < 700,variant+": FTC near-button clear prose");
    assert(/may earn a commission at no extra cost to you/i.test(html),variant+": disclosure not euphemistic");
    assert(!/\b(?:guaranteed cure|clinically proven to boost|hour.of.meditation in twelve minutes is proven|earn \$[0-9]+ a day)\b/i.test(html),variant+": no unsubstantiated FV effectiveness claims");
    assert(html.includes('href="/focus/"'),variant+": existing Focus route");
    assert(/prefers-reduced-motion/.test(html),variant+": reduced motion");
    assert(/:focus-visible/.test(html),variant+": focus indicator");
    assert(/@media\(max-width:680px\)/.test(html),variant+": small screen layout");
    assert(/2023 EEG review/.test(html) && /not a Zen12/i.test(html),variant+": source boundary");
  }
  assert(!A.includes('id="film"'),"A must be strictly text guide");
  assert(B.includes('id="film"') && B.includes("<details>") && B.includes("<summary>"),"B optional no-JS panel");
  assert(B.includes('<svg class="poster" role="img" aria-labelledby="arttitle artdesc"'),"B SVG accessible");
  for(const t of ["FORMAT</text>","MECHANISM</text>","OUTCOME</text>"])assert(B.includes(t),"Poster actual labels "+t);
  assert(/An illustrated clock marked 12 minutes appears beside three labeled rectangular cards: FORMAT, MECHANISM and OUTCOME/.test(B),"accurate accessible SVG description");
  const captions=[...B.matchAll(/(00:\d{2})–(00:\d{2}) —/g)];
  assert.equal(captions.length,7,"seven caption/transcript segments");
  let previous=0;
  for(const [,start,end] of captions) {
    const toSec=t=>parseInt(t.slice(0,2))*60+parseInt(t.slice(3));
    const s=toSec(start), e=toSec(end);
    assert(s===previous && e-s===6 && e<=42,"contiguous six second segments");
    previous=e;
  }
  assert.equal(previous,42);
  assert.equal(removeFilm(B).replace("Unpublished B","Unpublished A"),A,"A/B guide parity outside optional film");
  assert(article.length > 9000 && article.includes("### Primary and official source ledger") && article.includes("A tone can be measured"),"substantial original sourced investigation");
  assert(article.includes("not a head-to-head trial") && article.includes("does not, by itself"),"specific inference safeguards");
  assert(plan.includes("OFFER → FUNNEL STEP") && plan.includes("NOT COMPUTABLE") && plan.includes("TASK-008"),"conversion contract");
  assert(plan.includes("not a confirmed live deep link") && plan.includes("66 results"),"creator and source caution");
  assert.equal(m.sources.length,15,"source ledger 15");
  assert.equal(m.claims.length,25,"claims ledger 25");
  assert.equal(m.authorization_gates.length,16,"release gate count");
  assert(m.authorization_gates.every(g=>g.status==="HARD_HOLD" && g.cleared_at===null && g.evidence===null),"all gates hard held");
  assert(m.claims.some(c=>c.id==="C07" && c.status==="unsupported_product_effect"),"hour equivalence not promoted");
  assert(m.claims.some(c=>c.id==="C15" && c.status==="unverified_private_eligibility"),"partner named approval unknown");
  assert(m.claims.some(c=>c.id==="C20" && c.status==="unverified_inventory"),"owned paid Mind SKU unknown");
  assert(m.claims.some(c=>c.id==="C25" && c.status==="not_verified"),"Puységur URL not invented");
  assert(m.conversion_events.affiliate_click.includes("NEVER paid order"),"affiliate click not a sale");
  assert(m.conversion_events.main_kpi.includes("null when data missing"),"no fabricated net revenue");
  assert.equal(m.release,"HARD_HOLD");
  return true;
}
validate(baseline);
const negatives=[
  [names[0],s=>s.replace(' disabled aria-describedby',' aria-describedby')],
  [names[1],s=>s.replace(' disabled aria-describedby',' aria-describedby')],
  [names[0],s=>s.replace('may earn a commission','may have a connection')],
  [names[1],s=>s.replace('id="disclosure"','id="unlinked"')],
  [names[0],s=>s.replace('href="/focus/"','href="https://zen12.com/hnp"')],
  [names[1],s=>s.replace('href="/focus/"','href="https://affiliates.inspire3.com/c/unknown"')],
  [names[0],s=>s.replace("<main>","<script>track()</script><main>")],
  [names[1],s=>s.replace("<main>","<form><input></form><main>")],
  [names[0],s=>s.replace("<main>","<iframe src='tracker'></iframe><main>")],
  [names[1],s=>s.replace("<main>","<img src='https://other.test/pixel'><main>")],
  [names[0],s=>s.replace("View merchant offer — unavailable","Buy now")],
  [names[0],s=>s.replace('content="noindex,nofollow"','content="index,follow"')],
  [names[1],s=>s.replace('href="/focus/"','href="/new-subscribe/"')],
  [names[1],s=>s.replace('id="film"','id="uncontrolled-film"')],
  [names[1],s=>s.replace('FORMAT</text>','OPTIONS</text>')],
  [names[1],s=>s.replace('An illustrated clock marked 12 minutes','A person standing in a field')],
  [names[1],s=>s.replace('00:36–00:42','00:36–00:55')],
  [names[1],s=>s.replace('00:24–00:30','00:24–00:35')],
  [names[1],s=>s.replace('00:18–00:24','00:18–00:29')],
  [names[1],s=>s.replace('00:12–00:18','00:12–00:17')],
  [names[1],s=>s.replace('00:00–00:06','00:01–00:06')],
  [names[0],s=>s.replace('@media(max-width:680px)','@media(max-width:100px)')],
  [names[0],s=>s.replace(':focus-visible',':focuz-visible')],
  [names[2],s=>s.replace("A tone can be measured","Audio always causes benefit")],
  [names[3],s=>s.replace("NOT COMPUTABLE","ZERO SALES")],
  [names[3],s=>s.replace("TASK-008","TASK-008-DELETED")],
  [names[4],s=>s.replace('"status": "HARD_HOLD"','"status": "CLEARED"')],
  [names[4],s=>s.replace('"cleared_at": null','"cleared_at": "2026-11-09"')],
  [names[4],s=>s.replace('"release": "HARD_HOLD"','"release": "LIVE"')],
  [names[4],s=>s.replace('"unsupported_product_effect"','"verified_therapeutic_claim"')],
  [names[4],s=>s.replace('"unverified_private_eligibility"','"approved"')],
  [names[4],s=>s.replace('"unverified_inventory"','"live_paid_mind_sku"')],
  [names[4],s=>s.replace('"not_verified"','"verified_live"')],
  [names[4],s=>s.replace('NEVER paid order','IS a paid order')],
  [names[4],s=>s.replace('null when data missing','zero when data missing')]
];
let rejected=0;
for(const [name,mutate] of negatives){const edited=mutate(baseline[name]); assert.notEqual(edited,baseline[name],"negative case must alter file");const specimen={...baseline,[name]:edited};try{validate(specimen)}catch(e){rejected++;continue}throw Error("UNDETECTED mutation: "+name+" case "+rejected)}
assert.equal(rejected,negatives.length);
console.log(JSON.stringify({baseline:"PASS",negative_rejections:rejected,total_mutations:negatives.length,files:names.length,note:"SOURCE-ONLY Node checks; no browser/WP/merchant or live commerce tests"},null,2));
