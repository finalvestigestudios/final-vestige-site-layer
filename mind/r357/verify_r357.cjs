#!/usr/bin/env node
"use strict";
/** R357 static source-only verifier. No network, no merchant activity, no destructive mutation. Run: node mind/r357/verify_r357.cjs */
const fs=require("node:fs"); const path=require("node:path");const dir=__dirname;let passed=0;
function check(name,cond){if(!cond)throw new Error("FAIL "+name);passed++;console.log("PASS "+name)}
const load=n=>fs.readFileSync(path.join(dir,n),"utf8");
const a=load("ZEN12_A_EVIDENCE_GUIDE.html"),b=load("ZEN12_B_OPTIONAL_FILM_GUIDE.html"),hub=load("MIND_HUB_WORDPRESS_REVIEW_ONLY.html"),article=load("THE_BEAR_YOU_CANNOT_STOP_SEEING.md"),vtt=load("ORIGINAL_42S_CAPTIONS.vtt"),matrix=JSON.parse(load("CLAIM_SOURCE_AUTHORIZATION_MATRIX.json")),plan=load("CONVERSION_ACCEPTANCE.md");
const all=[a,b,hub];const unsafe=/<script\b|javascript:|<iframe\b|<form\b|<input\b|<video\b|<audio\b|\son(?:click|load|error|mouseover)=/i;
function safe(html){return !unsafe.test(html)&&!/<a[^>]+href=["'][^"']*(zen12|hypnosislive|brainwaveshots|inspire3)\.com/i.test(html)&&!/<button[^>]+(?:onclick|formaction)/i.test(html)}
check("A/B/Hub free of active forms scripts tracking merchant links",all.every(safe));
check("A and B semantically identical core",b.replace(/<figure class="reel"[\s\S]*?<\/figure>/,"")===a);
check("A and B HTML valid doctype", [a,b].every(s=>s.startsWith("<!doctype html>")&&s.includes("<main>")&&s.includes('lang="en"')));
check("A and B disabled commerce",[a,b].every(s=>/button type="button" disabled aria-disabled="true"/.test(s)));
check("FTC plain earning disclosure before control",[a,b].every(s=>s.indexOf("Affiliate disclosure:")>0&&s.indexOf("Affiliate disclosure:")<s.indexOf("Merchant purchase unavailable")));
check("no merchant active CTA",[a,b].every(s=>!s.includes("Buy Now")&&!s.includes('href="https://zen12.com/')));
check("no new signup",[a,b].every(s=>!/<form\b|type=["']email/i.test(s)));
check("no auto-playing video",[a,b].every(s=>!/<video\b|autoplay=/i.test(s)));
check("B transparent treatment not autoplay",b.includes("no hosted player")&&b.includes("does not include an encoded or embedded film"));
check("B transcript expandable",b.includes("<details>")&&b.includes("<summary>"));
check("VTT six scenes",vtt.startsWith("WEBVTT")&&(vtt.match(/-->/g)||[]).length===6);
check("VTT ends 42 seconds",vtt.includes("00:00:42.000"));
check("A/B preserve one free focus path",[a,b].every(s=>s.includes("https://finalvestige.com/focus/")));
check("hub only existing live routes",hub.includes("https://finalvestige.com/2026/11/02/change-blindness/")&&hub.includes("https://finalvestige.com/2026/11/02/mesmerism/"));
check("hub not published",hub.includes("Unpublished source-controlled"));
check("source claim count",matrix.claims.length>=30);
check("release gates all closed",matrix.release_gates.length>=25&&matrix.release_gates.every(g=>g.status==="HARD_HOLD"&&g.evidence===null));
check("no verified revenue fictionalized",matrix.revenue.verified_paid_orders===null&&matrix.revenue.net_revenue_usd_per_1000_qualified_sessions===null);
check("research citations survive",article.includes("pubmed.ncbi.nlm.nih.gov/3612492")&&article.includes("1745691619898795"));
check("no fabricated live R357 URL",!plan.includes("https://finalvestige.com/2026/11/13/the-bear"));
check("one canonical Focus lead",plan.includes("single email pathway")||plan.includes("existing single"));
const attack=[
 ["script",a.replace("</main>","<script>steal()</script></main>")],
 ["active link",a.replace('Merchant purchase unavailable — approval pending','<a href="https://zen12.com/?affiliate=guess">Buy</a>')],
 ["active form",a.replace("</main>",'<form><input type="email"></form></main>')],
 ["iframe",a.replace("</main>",'<iframe src="https://example.com"></iframe></main>')],
 ["onerror",a.replace("</main>",'<img src=x onerror=alert(1)></main>')],
 ["affiliate link",a.replace("</main>",'<a href="https://inspire3.com/">earn</a></main>')]
];
for(const [name,html] of attack)check("reject unsafe mutation "+name,!safe(html));
console.log("R357 "+passed+" source-level checks PASS. NOT a browser, CI, merchant or WordPress sanitizer run.");