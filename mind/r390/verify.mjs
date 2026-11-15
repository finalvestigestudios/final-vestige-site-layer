// R390 exact-source offline safety and parity verifier.
// Run from repository root: node mind/r390/verify.mjs
// Static checks cannot substitute for browser, CMS, partner or actual paid-sale tests.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dir = path.dirname(fileURLToPath(import.meta.url));
const read = (name) => fs.readFileSync(path.join(dir,name), "utf8");
const a=read("ZEN12_A_EVIDENCE_GUIDE.html");
const b=read("ZEN12_B_FILM_HYPOTHESIS.html");
const hub=read("MIND_HUB_SOURCE_DRAFT.html");
const article=read("THE_WORD_NO_ONE_SPOKE.md");
const poster=read("R390_ORIGINAL_POSTER.svg");
const vtt=read("R390_CAPTIONS.vtt");
const claims=JSON.parse(read("CLAIM_PROOF_AUTHORIZATION.json"));
const dossier=read("CONVERSION_FIRST_ACCEPTANCE.md");
let passed=0;let failed=0;
function requireTrue(cond,name){if(!cond){failed++;process.stderr.write("FAIL "+name+"\n");}else{passed++;process.stdout.write("PASS "+name+"\n");}}
function words(s){return s.trim().split(/\s+/).map(w=>w.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu,"")).filter(Boolean);}
const standard = b.replace(/<section class="film"[\s\S]*?<\/section>/,"").replace("draft B","draft A");
requireTrue(standard===a,"AB has identical substantive buyer copy and CSS except media");
requireTrue(words(article).length >=2200,"long original investigation >=2200 words");
for(const val of ["40 percent","55 percent","0.374","not a Zen12 product trial","not a scientific estimate","Puységur","SOURCE","editorial"]) {
  requireTrue(article.toLowerCase().includes(val.toLowerCase()),"article research/limitation anchor "+val);
}
for(const [nm,txt] of [["A",a],["B",b]]){
  requireTrue(/<html lang="en">/.test(txt),nm+" language");
  requireTrue(/name="viewport"/.test(txt),nm+" viewport");
  requireTrue(/name="robots" content="noindex,nofollow"/.test(txt),nm+" unpublished");
  requireTrue(/<button type="button" disabled aria-disabled="true">/.test(txt),nm+" disabled purchase control");
  requireTrue(/may earn a commission at no additional cost to you/i.test(txt),nm+" adjacent commission disclosure");
  requireTrue(/class="panel offer"[\s\S]*?class="disclosure"[\s\S]*?<button type="button" disabled/.test(txt),nm+" disclosure before CTA in same offer block");
  requireTrue(!/<script\b|<iframe\b|<form\b/i.test(txt),nm+" no scripts/iframes/forms");
  requireTrue(!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(txt),nm+" no autoplay media");
  requireTrue(!/\bhref=["']https?:\/\/(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com|inspire3\.com\/affiliates)/i.test(txt),nm+" no active seller or affiliate hyperlink");
  requireTrue(txt.includes("https://finalvestige.com/focus/"),nm+" one existing free resource route");
  requireTrue(!/Guaranteed (?:profit|healing|cure|brain|memory)/i.test(txt),nm+" no unsupported guarantee");
}
requireTrue(poster.includes("<svg")&&poster.includes("<title")&&poster.includes("<desc")&&!/<script\b|<foreignObject\b/i.test(poster),"SVG accessible native original without script");
requireTrue(/<img[^>]*alt="[^"]+"/.test(b),"B poster meaningful alt text");
requireTrue(b.includes("Optional 42-second")&&b.includes("<details>")&&b.includes("not playable"),"B explicit storyboard and full transcript");
requireTrue(vtt.startsWith("WEBVTT\n"),"valid WebVTT header");
const cueBlocks=vtt.trim().split(/\n\s*\n/).slice(1);
requireTrue(cueBlocks.length===6,"six caption cues");
requireTrue(cueBlocks.every((cb,i)=>cb.includes("00:00:"+String(i*7).padStart(2,"0")+".000 --> 00:00:"+String((i+1)*7).padStart(2,"0")+".000")),"caption timestamps cover 42 seconds");
const capText=cueBlocks.map(cb=>cb.split("\n").slice(2).join(" ")).join(" ");
const transcriptMatch=b.match(/<details>[\s\S]*?<p>([\s\S]*?)<\/p>/);
requireTrue(!!transcriptMatch,"B transcript block exists");
requireTrue(!!transcriptMatch&&words(capText).join("|")===words(transcriptMatch[1]).join("|"),"caption/transcript words identical");
requireTrue(/class="sections"/.test(hub)&&["01 \/ PERCEPTION","02 \/ HISTORY","03 \/ PRACTICE","04 \/ TOOLS"].every(x=>hub.includes(x)),"hub four editorial streams");
requireTrue(/prefers-reduced-motion/.test(hub)&&!/<script\b|<form\b|<iframe\b/.test(hub),"hub reduced motion and no duplicate forms");
requireTrue(/finalvestige.com\/focus\//.test(hub)&&/finalvestige.com\/free-resources\/puysegurs/.test(hub),"hub live source links");
requireTrue(Array.isArray(claims.claims)&&claims.claims.length===36,"36 sourced classified claim rows");
requireTrue(Object.keys(claims.sources).length===17,"17 explicit source URLs");
requireTrue(claims.claims.every(x=>x.id&&x.claim&&x.status&&Array.isArray(x.source_ids)&&x.source_ids.every(y=>y in claims.sources)),"all claim citations resolvable");
requireTrue(claims.claims.some(x=>x.id==="M05B"&&x.status==="DATED_SELLER_PROMO_SCREEN_ONLY"),"separate coupon-price route recorded as seller-only");
requireTrue(claims.gates.length===36&&claims.gates.every(x=>x.status==="HARD_HOLD"),"all 36 commercial gates held");
requireTrue(claims.commerce_status.affiliate_url===null&&claims.commerce_status.net_revenue_per_1000===null,"merchant and revenue fields null");
requireTrue(dossier.includes("NOT COMPUTABLE")&&dossier.includes("UNKNOWN")&&dossier.includes("HARD HOLD"),"dossier truthful unknown revenue/creator states");
requireTrue(dossier.includes("https://finalvestige.com/2026/11/02/change-blindness/")&&dossier.includes("https://finalvestige.com/2026/11/02/mesmerism/")&&dossier.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"),"three concrete creator-to-live-article paths");
requireTrue(!/href=["']https?:\/\/(?:zen12|hypnosislive|brainwaveshots)\.com/i.test(hub),"hub no active commerce destination");
process.stdout.write("\nR390 offline static checks: "+passed+" passed; "+failed+" failed. NOT a browser or commercial acceptance test.\n");
process.exitCode=failed?1:0;
