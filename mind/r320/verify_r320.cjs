#!/usr/bin/env node
"use strict";
/* Mind R320 source-only regression suite. No network, no user-data, no mutation of files.
   Run: node mind/r320/verify_r320.cjs
   Applies to source-only unpublished specimens; passing does NOT imply browser, WP or merchant QA. */
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const ROOT=__dirname;
const read=(name)=>fs.readFileSync(path.join(ROOT,name),"utf8");
const files={
  article:read("THE-BEAR-THAT-RETURNED-UNPUBLISHED.md"),
  a:read("ZEN12-A-EVIDENCE-FIRST-TEXT-REVIEW.html"),
  b:read("ZEN12-B-OPTIONAL-42S-STORYBOARD-REVIEW.html"),
  vtt:read("ORIGINAL-42S-CAPTIONS-CONCEPT.vtt"),
  hub:read("MIND-EVIDENCE-ARCHIVE-WP-REVIEW-ONLY.html"),
  matrix:read("SOURCE-CLAIM-OFFER-AND-COMMERCE-GATES.json"),
  dossier:read("OFFER-FUNNEL-CONVERSION-QA-RELEASE-ACCEPTANCE.md")
};
const filmBlock=/<figure class="film"[\s\S]*?<\/figure>/;
const assertions=[];
function must(name,fn){fn();assertions.push(name)}
function rejection(name,fn){assert.throws(fn,undefined,name);assertions.push("reject:"+name)}
function structuralBuyer(html){
  assert.match(html,/<!doctype html>/i);
  assert.match(html,/<html lang="en">/);
  assert.match(html,/<meta name="viewport"/);
  assert.match(html,/<main id="main"/);
  assert.match(html,/<h1>[^<]+<\/h1>/);
  assert.match(html,/<button[^>]*\bdisabled\b[^>]*>[^<]*unavailable<\/button>/i);
  assert.match(html,/Prospective affiliate disclosure:/);
  assert.match(html,/may earn a commission/);
  assert.match(html,/<button[\s\S]*?<\/button>\s*<p class="disclosure">/);
  assert.match(html,/https:\/\/finalvestige\.com\/focus\//);
  assert.match(html,/https:\/\/zen12\.com\/about/);
  assert.match(html,/https:\/\/zen12\.com\/getstarted/);
  assert.match(html,/https:\/\/www\.ftc\.gov|https:\/\/finalvestige\.com\/affiliate-disclosure/);
  assert.match(html,/@media\(max-width:760px\)/);
  assert.match(html, /prefers-reduced-motion/);
  assert.doesNotMatch(html,/<\s*(script|iframe|form|video|audio)\b/i);
  assert.doesNotMatch(html,/(?:\bonload\s*=|\bonclick\s*=|\bonerror\s*=|\bfetch\s*\(|\blocalStorage\b|\bgtag\s*\(|\bpixel\s*\()/i);
  assert.doesNotMatch(html,/utm_(source|content|campaign)=[^"\s]/i);
  assert.doesNotMatch(html,/(href|action)="[^"]*(affiliate_id|ref_id|aff_id|hop=|clickbank|&tid=)/i);
  assert.doesNotMatch(html,/(guaranteed (focus|results)|heals? anxiety|cures? (stress|depression)|rewires? your brain)/i);
  assert.doesNotMatch(html,/<a[^>]*href="https:\/\/(?:www\.)?zen12\.com\/getstarted"[^>]*>\s*(?:buy|shop|order|checkout)/i);
}
must("A buyer structurally safe",()=>structuralBuyer(files.a));
must("B buyer structurally safe",()=>structuralBuyer(files.b));
must("B only difference is optional film unit",()=>assert.equal(files.b.replace(filmBlock,""),files.a));
must("A contains no film element",()=>assert.doesNotMatch(files.a,filmBlock));
must("B contains exactly one optional film with text transcript",()=>{assert.equal((files.b.match(/<figure class="film"/g)||[]).length,1);assert.match(files.b,/<details><summary>Read the complete 42-second narration transcript<\/summary>/);assert.match(files.b,/role="img" aria-labelledby=/)});
must("WebVTT has exactly six nonoverlapping cues and 42s end",()=>{
  const cues=[...files.vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
  assert.equal(cues.length,6);let last=0;
  cues.forEach(x=>{let st=(+x[1]*3600+ +x[2]*60+ +x[3])*1000+ +x[4];let en=(+x[5]*3600+ +x[6]*60+ +x[7])*1000+ +x[8];assert.ok(st>=last && en>st);last=en});assert.equal(last,42000);assert.match(files.vtt,/^WEBVTT/);
});
must("Scientific manuscript is substantive and has evidence caveats",()=>{assert.ok(files.article.trim().split(/\s+/).length>1800);for(const s of ["1987","2001","2020","2023","Puységur","not Zen12","source"]){assert.match(files.article,new RegExp(s,"i"))}assert.match(files.article,/https:\/\/pubmed\.ncbi\.nlm\.nih\.gov\/3612492/);assert.match(files.article,/https:\/\/doi\.org\/10\.1126\/sciadv\.adh5292/)});
must("Hub four streams and preserved existing route",()=>{assert.equal((files.hub.match(/class="section" id="/g)||[]).length,4);for(const s of ['id="perception"','id="history"','id="practice"','id="tools"','https://finalvestige.com/focus/','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'])assert.ok(files.hub.includes(s));assert.match(files.hub,/<button disabled/);assert.doesNotMatch(files.hub,/<\s*(script|form|iframe)\b/i);assert.match(files.hub,/prefers-reduced-motion/)});
const m=JSON.parse(files.matrix);
must("Matrix twenty exact URLs and 35 classified claims",()=>{assert.equal(m.sources.length,20);assert.equal(m.claims.length,35);const ids=new Set(m.sources.map(s=>s.id));assert.equal(ids.size,m.sources.length);for(const s of m.sources){assert.ok(s.url.startsWith("https://"));assert.ok(!s.url.includes("YOUR_"))}for(const c of m.claims){for(const k of c.sources)assert.ok(ids.has(k),"missing source "+k)}});
must("All eighteen permission gates remain HARD_HOLD",()=>{assert.equal(m.holds.length,18);assert.ok(m.holds.every(h=>h.status==="HARD_HOLD"));assert.equal(m.commercial_activation,"HARD_HOLD")});
must("Three creator entries disclose missing IDs and unlaunched draft",()=>{assert.equal(m.creator_to_product_fit.length,3);assert.ok(m.creator_to_product_fit.every(x=>x.asset_id===null && x.platform_post_url===null));assert.equal(m.creator_to_product_fit[2].landing_status,"UNPUBLISHED")});
must("No unearned paid success language",()=>{assert.equal(m.measurement.status,"NOT_COMPUTABLE");assert.ok(files.dossier.includes("NOT COMPUTABLE"));assert.ok(files.dossier.includes("NO COMMERCIAL ACTIVATION"));assert.match(files.dossier,/qualified human sessions/);assert.match(files.dossier,/merchant_confirmed_paid_order/)});
const attacks=[
  ["active buy link",s=>s.replace('<button type="button" disabled aria-disabled="true">','<a href="https://zen12.com/getstarted?aff_id=123">').replace('</button>','</a>')],
  ["remove disabled",s=>s.replace(' disabled aria-disabled="true"','')],
  ["remove disclosure",s=>s.replace('Prospective affiliate disclosure:','')],
  ["new form",s=>s.replace("</main>","<form action='/new-list'><input></form></main>")],
  ["script tracker",s=>s.replace("</body>","<script>gtag('event','sale')</script></body>")],
  ["iframe",s=>s.replace("</body>","<iframe src='https://seller.example'></iframe></body>")],
  ["autoplay",s=>s.replace("</body>","<video autoplay></video></body>")],
  ["external UTM",s=>s.replace("</body>","<a href='https://example.com/?utm_source=tiktok'>x</a></body>")],
  ["affiliate query",s=>s.replace('https://zen12.com/getstarted','https://zen12.com/getstarted?aff_id=abcdef')],
  ["unsupported guarantee",s=>s.replace('You cannot buy a scientific guarantee','Guaranteed focus! You cannot buy a scientific guarantee')]
];
for(const [name,mutate] of attacks){rejection(name,()=>structuralBuyer(mutate(files.a)));}
rejection("B text drift",()=>assert.equal(files.b.replace(filmBlock,"").replace("You can buy the structure","You can buy more structure"),files.a));
rejection("invalid caption end",()=>assert.equal(files.vtt.replace("00:00:42.000","00:00:43.000").includes("00:00:42.000"),true));
rejection("open commercial gate",()=>assert.ok(m.holds.map((x,i)=>i===0?{...x,status:"APPROVED"}:x).every(x=>x.status==="HARD_HOLD")));
rejection("invent creator asset ID",()=>assert.ok(m.creator_to_product_fit.map((x,i)=>i===0?{...x,asset_id:"fictional"}:x).every(x=>x.asset_id===null)));
console.log("PASS",assertions.length,"source assertions and adversarial checks; no native browser, WP, lead, merchant or video outcome tested.");
