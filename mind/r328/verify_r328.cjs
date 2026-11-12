#!/usr/bin/env node
"use strict";
/**
 * R328: native offline source-level contract tests.
 * Usage: node mind/r328/verify_r328.cjs
 * No network, browser, merchant calls, data capture or production writes.
 */
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const root = __dirname;
const load = name => fs.readFileSync(path.join(root,name), "utf8");
const A = load("ZEN12-A-BUYER-GUIDE-REVIEW.html");
const B = load("ZEN12-B-OPTIONAL-42S-STORYBOARD-REVIEW.html");
const hub = load("MIND-HUB-FOUR-STREAM-WP-REVIEW-ONLY.html");
const article = load("THE-TABLE-MOVED-THE-HANDS-SAID-THEY-HADNT.md");
const vtt = load("ORIGINAL-42S-CAPTIONS.vtt");
const dossier = load("CONVERSION-ATTRIBUTION-RELEASE-ACCEPTANCE.md");
const matrix = JSON.parse(load("SOURCE-CLAIM-PARTNER-GATES.json"));
const checks = [];
const check = (name, predicate) => { assert.ok(predicate(),name); checks.push(name); };
function buyerSafety(html) {
  return (
    !/<(?:script|iframe|form|audio|video|object|embed)\b/i.test(html) &&
    !/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(html) &&
    !/<a\b[^>]*href\s*=\s*["'][^"']*(?:checkout|buy-now|aff_id|affiliate_id|ref=)/i.test(html) &&
    !/\bautoplay\b\s*=/i.test(html) &&
    /<button\b[^>]*\bdisabled\b[^>]*aria-disabled=["']true["'][^>]*>Zen12 merchant offer/i.test(html) &&
    html.includes("No merchant link is currently active.") &&
    html.indexOf("Affiliate disclosure:") > -1 &&
    html.indexOf("Affiliate disclosure:") < html.indexOf("Zen12 merchant offer — not yet available") &&
    html.includes("https://finalvestige.com/focus/") &&
    html.includes("What you would receive") &&
    html.includes("Reasons to consider it. Reasons not to.") &&
    html.includes("product-specific") &&
    !/\b(guaranteed focus|cure anxiety|passive brain reprogramming proven|money guarantee|limited time!|I have used this)\b/i.test(html)
  );
}
check("A inactive merchant and adjacent disclosure",()=>buyerSafety(A));
check("B inactive merchant and adjacent disclosure",()=>buyerSafety(B));
check("A/B substantive-copy equivalence",()=>B.replace(/<section class="film"\b[\s\S]*?<\/section>/,"").replace("A/B prototype B","A/B prototype A")===A);
check("one optional storyboard with readable transcript",()=>B.includes('<details>')&&B.includes('Complete 42-second transcript'));
check("film original poster is inline SVG not remote asset",()=>B.includes('<svg viewBox="0 0 720 355"')&&!B.includes("https://player.vimeo.com"));
check("captions 00 to 42s",()=>vtt.startsWith("WEBVTT")&&vtt.includes("00:00:42.000"));
check("six caption intervals",()=> (vtt.match(/-->/g)||[]).length===6);
check("semantic headings and skip link",()=>A.includes('href="#main"')&&B.includes('id="main"'));
check("responsive layout and reduced motion",()=>A.includes("@media(max-width:700px)")&&B.includes("prefers-reduced-motion"));
check("no script or form in hub",()=>!/<(?:script|form|iframe|input)\b/i.test(hub));
check("hub no-JS practice",()=>hub.includes('<details>')&&hub.includes('<summary>'));
check("hub four streams",()=>["PERCEPTION &amp; ATTENTION","HISTORY OF SUGGESTION","PRACTICE &amp; REFLECTION","TOOLS UNDER REVIEW"].every(s=>hub.includes(s)));
check("hub only public verified internal links",()=>hub.includes("/2026/11/02/mesmerism/")&&hub.includes("/free-resources/puysegurs-animal-magnetism-files/")&&hub.includes("/focus/"));
check("article original substantial depth",()=>article.trim().split(/\s+/).length>1700);
check("article Faraday source",()=>article.includes("Experimental Investigation of Table-Moving")&&article.includes("1853"));
check("article modern research",()=>article.includes("Cantergi")&&article.includes("40-centimeter")&&article.includes("80-centimeter"));
check("article agency nuance",()=>article.includes("sense of agency")&&article.includes("not a medical"));
check("article no sales link",()=>!article.includes("affiliate_id=")&&!article.includes("checkout?ref="));
check("matrix 20 sources",()=>matrix.source_records.length===20);
check("matrix 20 scientific/commercial claims",()=>matrix.claims.length===20);
check("matrix 18 closed gates",()=>matrix.commercial_gates.length===18 && matrix.commercial_gates.every(g=>g.status==="HOLD"));
check("matrix issued affiliate URL withheld",()=>matrix.affiliate_status==="UNVERIFIED" && matrix.private_dashboard_authenticated===false);
check("all Grok IDs null",()=>matrix.grok_asset_links.length===3&&matrix.grok_asset_links.every(r=>r.asset_id===null&&r.confirmed_published_url===null));
check("dossier includes conversion contract",()=>dossier.includes("qualified-human sessions")&&dossier.includes("merchant-confirmed"));
check("dossier states KPI not computable",()=>dossier.includes("NOT COMPUTABLE"));
check("dossier maintains release authority",()=>dossier.includes("Founder")&&dossier.includes("Claude")&&dossier.includes("Praxxis"));
const bad=[
  ["script",A+'<script src="https://example.com/track.js"></script>'],
  ["iframe",A+'<iframe src="https://example.com"></iframe>'],
  ["form",A+'<form action="/lead"><input name="email"></form>'],
  ["active merchant link",A+'<a href="https://zen12.com/getstarted">Buy</a>'],
  ["affiliate id link",A+'<a href="https://example.com/?affiliate_id=123">Buy</a>'],
  ["enabled merchant button",A.replace('disabled aria-disabled="true"','type="submit"')],
  ["removed disclosure",A.replace("Affiliate disclosure:","Disclosed elsewhere:")],
  ["removed focus route",A.replaceAll("https://finalvestige.com/focus/","/newsletter/")],
  ["autoplay",A+'<video autoplay="autoplay"></video>'],
  ["guaranteed efficacy",A+" Guaranteed focus"],
  ["removed product explanation",A.replace("What you would receive","Something")],
  ["personal testimonial",A+" I have used this"],
];
let rejected=0;
for(const [name,mutant] of bad){assert.equal(buyerSafety(mutant),false, "Unsafe mutation escaped: "+name);rejected++;}
console.log("R328 native source checks PASS:",checks.length,"baseline;",rejected,"unsafe mutation fixtures rejected.");
console.log("Not tested: native WordPress, browser WCAG, CSP, Payhip, affiliate dashboard, consent/Jetpack or paid sales.");
