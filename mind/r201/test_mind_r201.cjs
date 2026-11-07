"use strict";
/**
 * Mind R201 source-only regression. Run in a full checkout:
 * node mind/r201/test_mind_r201.cjs
 * This is not a browser/WCAG/checkout test.
 */
const fs = require("node:fs");
const path = require("node:path");
const d=__dirname;
const read=n=>fs.readFileSync(path.join(d,n),"utf8");
const art=read("self-hypnosis-the-skill-versus-the-recording-UNPUBLISHED.md");
const hub=read("mind-four-stream-WORDPRESS-CONTENT-PREVIEW-UNPUBLISHED.html");
const a=read("zen12-evidence-A-TEXT-UNPUBLISHED.html");
const b=read("zen12-evidence-B-OPTIONAL-42S-UNPUBLISHED.html");
const plan=read("CONVERSION-FIRST-CREATOR-FIT-AB-VERIFIED-PAID-ACCEPTANCE.md");
const matrix=JSON.parse(read("SELF-HYPNOSIS-ZEN12-VERIFIED-CLAIMS-AND-COMMERCE-GATES.json"));
let passed=0, negative=0;
function ok(v,name){if(!v)throw Error("FAIL: "+name);passed++}
function checkDisabled(s){return /<button\b[^>]*\bdisabled\b[^>]*>/.test(s)}
function checkDisclosure(s){let i=s.indexOf("may receive a commission");if(i<0)i=s.indexOf("may earn a commission");const btn=s.indexOf("<button",i);return i>=0&&btn>i&&btn-i<1000}
function noActiveCommerce(s){return !/(?:awin1\.com\/cread|hop\.clickbank|affiliate_id=|refid=|utm_affiliate=|onclick\s*=|<a[^>]+href=["'][^"']*\b(affiliate|checkout|buy-now)\b)/i.test(s)}
function noRemoteRuntime(s){return !/<\s*(script|iframe|form|audio|video)\b/i.test(s)&&!/<link[^>]+rel=["']stylesheet["']/i.test(s)&&!/<img[^>]+src=["']https?:/i.test(s)}
function noFalseClaims(s){return !/guaranteed (?:to cure|income|result)|clinically proven Zen12|you will cure|we personally tested (?:Zen12|Total Focus)/i.test(s)}
function normalizeB(s){return s.replace(/<section class="panel" id="optional-film"[\s\S]*?<\/section>/,"").replace("B: optional film","A: text only")}
for(const [n,s] of [["guide A",a],["guide B",b],["hub",hub]]){ok(s.includes("<!doctype html>"),n+" HTML");ok(/<html lang="en">/.test(s),n+" language");ok(/<meta name="viewport"/.test(s),n+" viewport");ok(/<meta name="robots" content="noindex,nofollow"/.test(s),n+" noindex draft");ok(/class="skip"[^>]+href="#main"|href="#main" class="skip"/.test(s),n+" skip navigation");ok(/<main id="main">/.test(s),n+" main landmark");ok(/:focus-visible/.test(s),n+" visible focus");ok(/prefers-reduced-motion:reduce/.test(s),n+" reduced motion");ok(/@media\(max-width:420px\)/.test(s),n+" small viewport");ok(noRemoteRuntime(s),n+" no JS/form/media/embed");ok(noActiveCommerce(s),n+" no earning URL");ok(noFalseClaims(s),n+" no fabricated guarantees");ok(checkDisabled(s),n+" native purchase disabled");ok(checkDisclosure(s),n+" adjacent disclosure")}
ok(normalizeB(b)===a,"A/B content and terms parity after film removal");
ok(!a.includes('id="optional-film"')&&b.includes('id="optional-film"'),"film B only");
ok(b.includes("viewBox=")&&b.includes("<title id=\"poster-title\"")&&b.includes("<desc id=\"poster-desc\""),"accessible original SVG poster");
ok(b.includes("00–07")&&b.includes("37–42")&&b.includes("transcript"),"42s timed transcript");
ok(!/<video[^>]*autoplay/i.test(b),"no forced playback");
ok((a.match(/class="btn" href="https:\/\/finalvestige.com\/focus\/"/g)||[]).length===1,"one primary Focus CTA guide");
ok((hub.match(/https:\/\/finalvestige.com\/focus\//g)||[]).length===2,"existing Focus in hub only");
ok(/2019/.test(art)&&/22 randomized controlled trials/i.test(art),"self hypnosis RCT review scoped");
ok(/recordings of hypnosis delivered by someone else/i.test(art),"audio versus taught distinction");
ok(/Puységur/.test(art)&&/1784/.test(art),"historical bridge");
ok(/not.*clinical|not.*treatment/i.test(art),"nonclinical exercise limits");
ok(art.split(/\s+/).length>=1800,"article substantive");
ok(/https:\/\/eprints.bournemouth.ac.uk\/31277\//.test(art),"source direct");
ok(/$87\.99/.test(a)&&/November 7, 2026/.test(a),"seller price dated not fixed future");
ok(/not a checked-out total/i.test(a),"checkout not inferred");
ok(matrix.sources.length>=18&&matrix.claims.length>=30&&matrix.gates.length>=25,"matrix coverage");
const sourceIds=new Set(matrix.sources.map(s=>s.id));
ok(sourceIds.size===matrix.sources.length,"unique source ids");
for(const c of matrix.claims){ok(c.source_ids.every(id=>sourceIds.has(id)),"claim source resolves "+c.id);ok(Boolean(c.decision)&&Boolean(c.limits),"claim decision and scope "+c.id)}
ok(matrix.gates.every(g=>g.status==="OPEN"),"all authorization and release gates explicitly unresolved");
ok(matrix.earning_link===null&&matrix.individual_partner_approval==="UNVERIFIED","partner not invented");
ok(matrix.verified_owned_mind_sku===null&&matrix.verified_checkout===null,"owned fallback not invented");
ok(matrix.realized_net_revenue_per_1000_qualified_humans==="NOT_COMPUTABLE","net revenue not fabricated");
ok(matrix.attribution.pii_allowed===false&&matrix.attribution.first_party_only===true,"no PII");
ok(/confirmed_signup/.test(plan)&&/qualified_campaign_landing/.test(plan)&&/merchant_confirmed_order/.test(plan),"funnel event separation");
ok(/NOT COMPUTABLE|NOT_COMPUTABLE/.test(plan),"cannot assume cash");
ok(/2026_11/.test(plan)&&/utm_content/.test(plan)&&/asset_id/.test(plan),"asset-id UTM mapping");
ok(/NO.*LIVE|NOT LIVE/i.test(plan),"unpublished link guard");
ok(/Dispatch/.test(plan)&&/Praxxis/.test(plan)&&/Grok/.test(plan),"ownership");
ok(/no-JS/.test(plan)&&/WCAG/.test(plan),"a11y verification gates");
const checks=[
 [s=>checkDisabled(s),s=>s.replace(" disabled aria-describedby"," aria-describedby")],
 [s=>checkDisclosure(s),s=>s.replace(/may receive a commission|may earn a commission/,"may receive a reward")],
 [s=>noActiveCommerce(s),s=>s+"<a href='https://awin1.com/cread.php?a=1'>buy</a>"],
 [s=>noRemoteRuntime(s),s=>s+"<script src='https://example.org/t.js'></script>"],
 [s=>noRemoteRuntime(s),s=>s+"<form action='https://capture.example'><input></form>"],
 [s=>noRemoteRuntime(s),s=>s+"<iframe src='https://x.example'></iframe>"],
 [s=>noFalseClaims(s),s=>s+" guaranteed to cure anxiety"],
];
for(const [validator,mutate] of checks){for(const s of [a,b,hub]){if(!validator(s))throw Error("invalid test seed");if(validator(mutate(s)))throw Error("mutation escaped");negative++}}
const failSources=structuredClone(matrix);failSources.claims[0].source_ids.push("MADE_UP");
ok(!failSources.claims.every(c=>c.source_ids.every(id=>sourceIds.has(id))),"invalid source caught");
const failGates=structuredClone(matrix);failGates.gates[0].status="VERIFIED";
ok(!failGates.gates.every(g=>g.status==="OPEN"),"premature activation caught");
const failMoney=structuredClone(matrix);failMoney.realized_net_revenue_per_1000_qualified_humans=0;
ok(failMoney.realized_net_revenue_per_1000_qualified_humans!=="NOT_COMPUTABLE","zero false report caught");
negative+=3;
console.log("R201 STATIC: "+passed+"/"+passed+" assertions PASS; "+negative+"/"+negative+" unsafe mutations rejected. NOT browser, CI, partner, checkout or paid-sale proof.");
