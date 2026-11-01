"use strict";
// Reproducible source checks (NOT a substitute for WP staging/browser WCAG or product evidence).
const NAMES=[
 "INVESTIGATION.md","investigation.wp.html","ZEN12_EVIDENCE_GUIDE.md",
 "zen12-guide-a.wp.html","zen12-guide-b.wp.html","mind-archive.wp.html",
 "film-poster.svg","zen12-40s.vtt","CLAIM_SOURCE_MATRIX.csv",
 "AB_TEST_AND_NAVIGATION.md","FILM_PROVENANCE_AND_QA.md","privacy-off.cjs"
];
function audit(f){
 const failures=[]; let count=0;
 const ok=(label,cond)=>{count++;if(!cond)failures.push(label)};
 for(const key of NAMES)ok("present: "+key,typeof f[key]==="string"&&f[key].length>50);
 if(failures.length)return {passed:count-failures.length,total:count,failures};
 const art=f["INVESTIGATION.md"],wp=f["investigation.wp.html"],guide=f["ZEN12_EVIDENCE_GUIDE.md"],
 A=f["zen12-guide-a.wp.html"],B=f["zen12-guide-b.wp.html"],hub=f["mind-archive.wp.html"],
 matrix=f["CLAIM_SOURCE_MATRIX.csv"],privacy=f["privacy-off.cjs"],vtt=f["zen12-40s.vtt"],poster=f["film-poster.svg"];
 const textOnly=B.replace(/<aside class="film" id="fv31-film"[\s\S]*?<\/aside>/,"").replace('data-fv-variant="B"','data-fv-variant="A"');
 ok("A/B copy parity",textOnly===A);
 ok("film B only",B.includes('id="fv31-film"')&&!A.includes('id="fv31-film"'));
 ok("B full transcript",B.includes("Read the full forty-second film transcript")&&B.includes("34–40:"));
 ok("film is offline, not simulated",B.includes("not a hosted player")||B.includes("not hosted player"));
 ok("article 1900+ words",art.trim().split(/\s+/).length>=1900);
 ok("guide 1700+ words",guide.trim().split(/\s+/).length>=1700);
 ok("original science",art.includes("10.1038/35048669")&&art.includes("10.1016/S0926-6410(02)00069-1"));
 ok("early brain evidence",art.includes("PMC2905511"));
 ok("2020 review",art.includes("10.1016/j.neubiorev.2020.09.006"));
 ok("historical source bridge",art.includes("puysegurs-animal-magnetism-files"));
 ok("article contains no commercial recommendation",!/buy zen12|affiliate purchase link|order zen12|commission disclosure/i.test(art));
 ok("static timeline not live flash",wp.includes("Static explanatory timeline")&&!/<canvas\b/i.test(wp));
 ok("two-science sources guide",guide.includes("10.1371/journal.pone.0286023")&&guide.includes("www.nccih.nih.gov/health/meditation"));
 ok("merchant features accurate",["Beginner","Premium","Advanced","24 MP3","48 MP3","white noise"].every(t=>guide.includes(t)));
 ok("no invented merchant price",!/(?:\$\d{2}|USD\s*\d{2})/.test(guide));
 ok("exact FTC sources",guide.includes("ftcs-endorsement-guides")&&guide.includes("health-products-compliance-guidance"));
 ok("reject hour claim as proof",guide.includes("does **not** adopt")&&guide.includes("product-specific"));
 for(const [tag,x] of [["A",A],["B",B]]){
  ok(tag+" labeled variant",x.includes('data-fv-variant="'+tag+'"'));
  ok(tag+" disabled button",/<button\s+type="button"\s+disabled\b/.test(x));
  ok(tag+" has disclosure",x.includes('class="disclosure"'));
  ok(tag+" disclosure before button",x.indexOf('class="disclosure"')<x.indexOf('<button type="button" disabled'));
  ok(tag+" no active affiliate link",!/<a[^>]+href=["']https?:\/\/(?:zen12\.com|affiliates\.inspire3\.com)/i.test(x));
  ok(tag+" no unapproved tracking",!/<script\b|<iframe\b|<form\b/i.test(x));
  ok(tag+" no media autoplay",!/<video\b|<audio\b|autoplay\b/i.test(x));
  ok(tag+" no event attrs",!/\son(?:click|load|error|submit|focus)\s*=/i.test(x));
  ok(tag+" no hollow link",!/href=["']#["']/i.test(x));
  ok(tag+" semantic heading",x.includes('aria-labelledby="fv31-guide-title"')&&x.includes('id="fv31-guide-title"'));
  ok(tag+" no forced signup",!x.includes("jetpack-subscriptions"));
  ok(tag+" Focus route existing",x.includes("https://finalvestige.com/focus/"));
  ok(tag+" declared copy-scoped CSS",x.includes(".fv-z12-31")&&!x.includes("body:has("));
  ok(tag+" reduced-motion safe",x.includes("prefers-reduced-motion"));
 }
 ok("hub existing real archive",hub.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"));
 ok("hub no unpublished /mind/ links",!hub.includes('href="/mind/'));
 ok("hub no form",!/<form\b|jetpack-subscriptions/i.test(hub));
 ok("hub alternate no merchant checkout",!/<a[^>]+href=["']https?:\/\/(?:zen12\.com|affiliates\.inspire3\.com)/i.test(hub));
 ok("hub scoped CSS",hub.includes(".fv-mind-r31"));
 ok("film poster title",poster.includes("<title")&&poster.includes("<desc")&&!poster.includes("<animate"));
 ok("5 captions",vtt.startsWith("WEBVTT")&&(vtt.match(/-->/g)||[]).length===5);
 ok("captions end at 40 seconds",vtt.includes("00:00:40.000"));
 ok("captions preserve actual R30 script",vtt.includes("The second hand hesitates.")&&vtt.includes("Twelve is not sixty."));
 ok("film origin acknowledged",f["FILM_PROVENANCE_AND_QA.md"].includes("PR #374")&&f["FILM_PROVENANCE_AND_QA.md"].includes("not in the public GitHub repository"));
 ok("measurement disabled",/const ENABLED\s*=\s*false/.test(privacy));
 ok("privacy k floor",privacy.includes("const K_MIN = 10"));
 ok("privacy refuses extra keys",privacy.includes('names.length !== 4'));
 ok("evidence matrix 50+ rows",matrix.trim().split("\n").length>=51);
 ok("merchant rights flagged",matrix.includes("Account-specific Inspire3 approval")&&matrix.includes("HARD HOLD"));
 ok("no new signup platform",!Object.values(f).some(v=>/mailchimp|convertkit|beehiiv\.com\/subscribe/i.test(v)));
 return {passed:count-failures.length,total:count,failures};
}
function mutatedNegativeControls(f){
 const cases=[
 ["enabled purchase",x=>x["zen12-guide-a.wp.html"]=x["zen12-guide-a.wp.html"].replace('<button type="button" disabled','<button type="button"')],
 ["disabled disclosure removed",x=>x["zen12-guide-a.wp.html"]=x["zen12-guide-a.wp.html"].replace('class="disclosure"','class="hidden"')],
 ["added merchant link",x=>x["zen12-guide-b.wp.html"]+='<a href="https://zen12.com/getstarted">Buy now</a>'],
 ["autoplay",x=>x["zen12-guide-b.wp.html"]+='<video autoplay src="unverified.mp4"></video>'],
 ["hidden user form",x=>x["mind-archive.wp.html"]+='<form><input name="email"></form>'],
 ["new iframe",x=>x["zen12-guide-a.wp.html"]+='<iframe src="https://seller.example"></iframe>'],
 ["copy-drift",x=>x["zen12-guide-b.wp.html"]=x["zen12-guide-b.wp.html"].replace("Beginner","Foundation")],
 ["privacy enabled",x=>x["privacy-off.cjs"]=x["privacy-off.cjs"].replace("const ENABLED = false","const ENABLED = true")],
 ["commerce article",x=>x["INVESTIGATION.md"]+="\nOrder Zen12 right now."],
 ["fake 1h proof",x=>x["ZEN12_EVIDENCE_GUIDE.md"]=x["ZEN12_EVIDENCE_GUIDE.md"].replace("does **not** adopt","does fully adopt")],
 ["unpublished archive path",x=>x["mind-archive.wp.html"]+='<a href="/mind/not-live/">Preview</a>'],
 ["missing captions",x=>x["zen12-40s.vtt"]="WEBVTT\n"],
 ["seller price",x=>x["ZEN12_EVIDENCE_GUIDE.md"]+="\nThe price is $99."],
 ["new JS event",x=>x["zen12-guide-b.wp.html"]+='<button onclick="send()">Track</button>']
 ];
 let killed=0;const missed=[];
 for(const [name,mutate] of cases){
  const copy={...f};mutate(copy);if(audit(copy).failures.length)killed++;else missed.push(name);
 }
 return {killed,total:cases.length,missed};
}
function run(f){const base=audit(f);const neg=mutatedNegativeControls(f);return {base,negative:neg,success:base.failures.length===0&&neg.missed.length===0};}
if(typeof module!=="undefined")module.exports={NAMES,audit,mutatedNegativeControls,run};
if(typeof require==="function"&&typeof module!=="undefined"&&require.main===module){
 const fs=require("fs"),path=require("path"),here=__dirname;
 const files=Object.fromEntries(NAMES.map(n=>[n,fs.readFileSync(path.join(here,n),"utf8")]));
 const result=run(files);console.log(JSON.stringify(result,null,2));if(!result.success)process.exitCode=1;
}
