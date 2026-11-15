// R396 no-dependency, fail-closed static source verifier.
// Run from repo root: node mind/r396/verify.mjs
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
const dir=dirname(fileURLToPath(import.meta.url));
const load=f=>readFileSync(join(dir,f),"utf8");
const A=load("ZEN12_A.html"),B=load("ZEN12_B_OPTIONAL_FILM.html");
const M=JSON.parse(load("CLAIM_RIGHTS_MATRIX.json"));
const V=load("GORILLA_42S.vtt"),H=load("MIND_HUB_SOURCE.html");
const R=load("THE_GORILLA_IN_THE_READING_ROOM.md");
let count=0;function check(condition,label){count++;if(!condition)throw new Error("FAIL "+label);}
const merchantHosts=["zen12.com","inspire3.com","affiliates.inspire3.com","hypnosislive.com","brainwaveshots.com"];
function noMerchantLinks(html){const hrefs=[...html.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);return hrefs.every(url=>!merchantHosts.some(host=>url==="https://"+host || url.startsWith("https://"+host+"/") || url==="http://"+host || url.startsWith("http://"+host+"/")));}
for(const [label,h] of [["A",A],["B",B]]){
 check(h.includes('lang="en"'),label+" language");
 check(h.includes('name="viewport"'),label+" viewport");
 check(h.includes('href="#main"'),label+" skip");
 check(h.includes('prefers-reduced-motion'),label+" reduced motion");
 check(h.includes('focus-visible'),label+" keyboard");
 check(h.includes('disabled aria-disabled="true"'),label+" truly disabled commerce control");
 check(h.includes("may earn a commission at no additional cost to you"),label+" proximity disclosure");
 check(h.indexOf("may earn a commission")<h.indexOf('class="disabled"'),label+" disclosure before CTA");
 check(noMerchantLinks(h),label+" merchant links withheld");
 check(!/<script\b|<form\b|<iframe\b|\sautoplay\s*=|<video\b/i.test(h),label+" no active media/scripting/forms");
 check(h.includes("https://finalvestige.com/focus/"),label+" existing free funnel");
 check(!h.includes("100% guaranteed benefit"),label+" no guaranteed benefit");
}
function stripFilm(s){const marker='<section class="panel" aria-labelledby="film-title">';const begin=s.indexOf(marker);if(begin<0)return s;const end=s.indexOf("</section>",begin);if(end<0)throw Error("film section missing end");return s.slice(0,begin)+s.slice(end+"</section>".length);}
check(stripFilm(A)===stripFilm(B),"identical A/B non-film buyer copy");
check(!A.includes("film-title")&&B.includes("film-title"),"film only in B");
check((V.match(/ --> /g)||[]).length===6,"six subtitle cues");
check(V.includes("00:00:42.000"),"42-second caption duration");
const clip=B.match(/<summary>Read the complete 42-second film transcript and captions<\/summary><p>([\s\S]*?)<\/p>/);
check(Boolean(clip),"full transcript visible in B");
const compact=x=>x.toLowerCase().replace(/[^\p{L}\p{N}]+/gu," ").trim().replace(/\s+/g," ");
const vttText=V.split(/\n/).filter(x=>x.trim()&&!x.startsWith("WEBVTT")&&!x.includes("-->")).join(" ");
check(Boolean(clip)&&compact(vttText)===compact(clip[1]),"exact transcript/VTT word parity");
check(M.release_gates.length===16 && M.release_gates.every(x=>x.state==="HOLD"),"16 gates held");
check(M.claims.length===22 && M.sources.length===15,"22 claims and 15 source records");
check(M.claims.find(x=>x.id==="C13")?.classification==="unverified","publisher approval not invented");
check(M.claims.find(x=>x.id==="C22")?.classification==="unverified","no paid conversion invented");
check(M.sources.some(x=>x.url.includes("ftc.gov")),"FTC sources present");
check(!/<script\b|<form\b|<iframe\b|\sautoplay\s*=/i.test(H),"hub inert");
check(R.includes("10.1068/p281059")&&R.includes("10.1177/0956797613479386"),"primary research DOIs");
check(R.includes("not a documented archival incident"),"constructed story clearly labeled");
check(R.trim().split(/\s+/).length>=2000,"substantive original investigation");
console.log("PASS "+count+" static repository checks; this does not validate browser, CMS, video playback, signup or commerce.");