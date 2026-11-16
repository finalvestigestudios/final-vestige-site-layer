#!/usr/bin/env node
/** FV Mind R427 source-only release guard.
 * Read-only: node mind/r427/verify.mjs
 * No network requests, site writes or affiliate activation. Node 18+.
 */
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
const dir=dirname(fileURLToPath(import.meta.url));
const file=(name)=>readFileSync(join(dir,name),"utf8");
const data={
  article:file("THE_VOICE_CHANGED_WHEN_THE_MOUTH_MOVED.md"),
  hub:file("MIND_HUB_WORDPRESS_SOURCE_ONLY.html"),
  a:file("ZEN12_A_TEXT_BUYER_GUIDE.html"),
  b:file("ZEN12_B_OPTIONAL_FILM_CONCEPT.html"),
  vtt:file("ZEN12_FILM_42S.vtt"),
  matrix:JSON.parse(file("CLAIM_AND_PERMISSION_MATRIX.json")),
  conversion:file("CONVERSION_ACCEPTANCE_CREATOR_ROUTE.md")
};
const tests=[];function check(label, condition){tests.push({label,ok:!!condition});}
const allHtml=[data.a,data.b,data.hub];
const prohibitedMerchantAnchors=/<a\b[^>]*\bhref\s*=\s*["'](?:https?:\/\/)?(?:[^"'\/]*\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|inspire3\.com|affiliates\.inspire3\.com)(?:[\/?"'#]|$)/i;
const hiddenExfil=/(?:<script\b|<iframe\b|<form\b|fetch\s*\(|navigator\.sendBeacon|<img[^>]*https?:\/\/)/i;
const activePay=/(<a[^>]*\bhref\s*=\s*["'][^"']*(?:purchase|checkout|affiliate|track|ref=|hop=)[^"']*["'])/i;
const enabledPurchase=/<button\b(?=[^>]*purchase link)(?![^>]*\bdisabled\b)[^>]*>/i;
function disclose(s){return s.includes("Final Vestige may earn a commission at no additional cost to you");}
function commercialHold(s){return s.includes('type="button" disabled aria-disabled="true"')&&s.includes("Purchase link withheld");}
function safe(s){return !prohibitedMerchantAnchors.test(s)&&!hiddenExfil.test(s)&&!activePay.test(s);}
const filmPattern=/<details class="panel" aria-label="Optional forty-two-second original film storyboard">[\s\S]*?<\/details>/;
function parity(a,b){return b.replace(filmPattern,"")===a;}
function lines(s){return s.split(/\r?\n/);}
function cues(vtt){const blocks=vtt.trim().split(/\n\s*\n/).slice(1);return blocks.map(block=>{const m=block.match(/(\d\d):(\d\d):(\d\d)\.(\d{3})\s+-->\s+(\d\d):(\d\d):(\d\d)\.(\d{3})/);if(!m)return null;const t=(i)=>(+m[i]*3600+ +m[i+1]*60+ +m[i+2]+ +m[i+3]/1000);return {start:t(1),end:t(5)};});}
function wordcount(s){return (s.match(/[A-Za-z][A-Za-z'-]*/g)||[]).length;}
check("article >2300 words",wordcount(data.article)>2300);
check("article first-hand observation explicitly limited",data.article.includes("not a McGurk experiment")||data.article.includes("not a McGurk experiment".toUpperCase())||data.article.includes("not a McGurk experiment".replace("n","N")));
check("article sources original 1976 Nature",data.article.includes("10.1038/264746a0"));
check("article sources variability 2015",data.article.includes("PMC4580505"));
check("article sources 2018",data.article.includes("pone.0207160"));
check("article sources 2025",data.article.includes("PMC11987121"));
check("article references historical archive",data.article.includes("puysegurs-animal-magnetism-files"));
check("article links free Focus",data.article.includes("finalvestige.com/focus/"));
check("article distinguishes audio claims",data.article.includes("seller advertising"));
check("article original observation exercise",data.article.includes("Minutes 10–12"));
check("article no visitor outcome stated",!/(we tested Zen12|I used Zen12|my results improved)/i.test(data.article));
for(const [name,s] of [["A",data.a],["B",data.b],["hub",data.hub]]){
 check(name+" valid HTML lang/viewport",s.includes('<html lang="en">')&&s.includes('name="viewport"'));
 check(name+" reduced motion respected",s.includes("prefers-reduced-motion"));
 check(name+" focus visible",s.includes("focus-visible"));
 check(name+" no scripts, forms, iframe or external pixel",!hiddenExfil.test(s));
 check(name+" no merchant links",!prohibitedMerchantAnchors.test(s));
 check(name+" no active external paid CTA",!activePay.test(s));
 check(name+" no autoplay",!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(s));
 check(name+" no uncited performance guarantee",!/(guaranteed cognitive improvement|clinically proven to boost focus|treat anxiety)/i.test(s));
}
for(const [name,s] of [["A",data.a],["B",data.b]]){
 check(name+" conditional adjacent FTC disclosure",disclose(s));
 check(name+" native-disabled purchase button",commercialHold(s));
 check(name+" no other enabled purchase button",!enabledPurchase.test(s));
 check(name+" seller format and tiers",s.includes("48 MP3s")&&s.includes("24 MP3s"));
 check(name+" verified free route",s.includes('href="https://finalvestige.com/focus/"'));
 check(name+" provenance and buyer objections",s.includes("Five questions before you pay"));
 check(name+" no public price passed off as referred quote",s.includes("A cached public figure is not your price"));
}
check("film-only material is exactly one B inserted section",parity(data.a,data.b));
check("A contains no film section",!filmPattern.test(data.a));
check("B includes original poster SVG",data.b.includes("<svg")&&data.b.includes("Illustration only"));
check("B includes transcript",data.b.includes("Full narrated transcript (42 seconds)"));
check("B honestly describes unencoded/nonplayable status",data.b.includes("not been encoded"));
check("B caption file referenced in explanation",data.b.includes("WebVTT captions"));
const q=cues(data.vtt);
check("VTT file has WEBVTT header",data.vtt.startsWith("WEBVTT\n"));
check("VTT has six cues",q.length===6&&q.every(Boolean));
check("VTT intervals continuous 0..42",q.length===6&&q.every((x,i)=>x&&x.start===i*7&&x.end===(i+1)*7));
check("VTT no HTML or affiliate URL",!/<script|https?:\/\//i.test(data.vtt));
check("hub links only published source routes",["/2026/11/02/change-blindness/","/2026/11/02/mesmerism/","/free-resources/puysegurs-animal-magnetism-files/","/focus/"].every(p=>data.hub.includes(p)));
check("hub calls itself unpublished source",data.hub.includes("source prototype")&&data.hub.includes("not a WordPress CMS draft"));
check("hub has four streams",["Perception &amp; Attention","History of Suggestion","Practice &amp; Reflection","Tools Under Review"].every(x=>data.hub.includes(x)));
check("hub no new subscriber capture",!/<form|name="email"/i.test(data.hub));
check("hub conditional affiliate disclosure",disclose(data.hub));
check("matrix schema",data.matrix.schema==="fv-mind-claim-permission-v1");
check("matrix at least 30 claims",data.matrix.claims.length>=30);
check("matrix claims all have source",data.matrix.claims.every(x=>/^https:\/\//.test(x.source)));
check("matrix independent research included",data.matrix.claims.filter(x=>x.verdict==="independent_primary").length>=8);
check("matrix seller-only efficacy excluded",data.matrix.claims.filter(x=>x.verdict==="seller_efficacy_EXCLUDE").length>=3);
check("matrix 28 commercial gates held",data.matrix.commercial_gates.length===28&&data.matrix.commercial_gates.every(x=>x.state==="HOLD"));
check("matrix avoids claiming FV commission",data.matrix.claims.some(x=>x.id==="N01"&&x.verdict==="not_authenticated_HOLD"));
check("dossier has exact creator source routes",["change-blindness/","mesmerism/","puysegurs-animal-magnetism-files/"].every(x=>data.conversion.includes(x)));
check("dossier shows no matched media",data.conversion.includes("NO MATCH VERIFIED"));
check("dossier differentiates clicks from sales",data.conversion.includes("affiliate_click")&&data.conversion.includes("merchant_confirmed_purchase"));
check("dossier KPI and 7/30",data.conversion.includes("net_realized_revenue_per_1000")&&data.conversion.includes("7/30"));
check("dossier no duplicate tracking",data.conversion.includes("no new script")||data.conversion.includes("No new script")||data.conversion.includes("not duplicate scripts"));
check("dossier accurate hold",data.conversion.includes("HARD HOLD"));
const negatives=[
 ["hidden merchant anchor",()=>safe(data.a+'<a href="https://zen12.com/?ref=abcd">Buy</a>')],
 ["merchant hyperlink without path",()=>safe(data.a+'<a href="https://affiliates.inspire3.com">Go</a>')],
 ["added script",()=>safe(data.a+'<script src="/x.js"></script>')],
 ["added form",()=>safe(data.a+'<form action="/lead"></form>')],
 ["added pixel",()=>safe(data.a+'<img src="https://tracker.invalid/pixel">')],
 ["removed disclosure",()=>disclose(data.a.replace("Final Vestige may earn a commission at no additional cost to you",""))],
 ["removed disabled",()=>commercialHold(data.a.replace('type="button" disabled aria-disabled="true"','type="button"'))],
 ["copy divergence B",()=>parity(data.a,data.b.replace("The format is real enough","A different offer is now best"))],
 ["claim matrix gate open",()=>{const tampered=data.matrix.commercial_gates.map((g,i)=>i===0?{...g,state:"OPEN"}:g);return tampered.every(g=>g.state==="HOLD");}],
 ["unsafe checkout anchor",()=>safe(data.a+'<a href="https://merchant.invalid/checkout?hop=abc">click</a>')]
];
for(const [name,test] of negatives){let outcome=false;try{outcome=test()}catch{}check("mutation rejected: "+name,!outcome);}
const failures=tests.filter(x=>!x.ok);for(const t of tests)console.log((t.ok?"PASS":"FAIL")+" "+t.label);
console.log("TOTAL "+tests.length+" checks, "+(tests.length-failures.length)+" passed, "+failures.length+" failed.");
if(failures.length)process.exitCode=1;
