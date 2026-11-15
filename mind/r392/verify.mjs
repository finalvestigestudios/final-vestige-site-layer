// Offline R392 source/safety checks. Run: node mind/r392/verify.mjs
import fs from "node:fs"; import assert from "node:assert/strict";
const read=n=>fs.readFileSync(new URL(n,import.meta.url),"utf8");
const a=read("ZEN12_A.html"),b=read("ZEN12_B.html"),h=read("MIND_HUB.html"),v=read("CAPTIONS.vtt"),p=read("CLAIM_MATRIX.json"),m=read("BRAID_SUGGESTION_INVESTIGATION.md");const claims=JSON.parse(p);
let n=0;function ck(ok,label){assert.ok(ok,label);n++}
ck(b.includes("<aside class=\"film\">"),"B optional storyboard");const start=b.indexOf('<aside class="film">');const end=b.indexOf("</aside>",start);ck(start>0 && end>start && a===b.slice(0,start)+b.slice(end+8),"A/B text parity");ck(!a.includes("<aside class=\"film\">"),"A no storyboard");
ck(a.includes('disabled aria-disabled="true"')&&b.includes('disabled aria-disabled="true"'),"native disabled controls");
ck(a.includes("Prospective commission disclosure")&&b.includes("Prospective commission disclosure"),"near control disclosure");
ck(!a.includes("<script")&&!b.includes("<script")&&!h.includes("<script"),"no trackers");
ck(!a.includes("<form")&&!b.includes("<form")&&!h.includes("<form"),"no duplicate email forms");
ck(!a.includes(" autoplay=")&&!b.includes(" autoplay="),"no autoplay");
ck(!a.includes("zen12.com/secret")&&!b.includes("zen12.com/secret"),"no promo deep link");
ck(claims.release_gates.every(g=>g.state==="HOLD"),"all commercial holds");
ck(claims.products[0].issued_link==="WITHHELD","no earning URL");
ck(v.startsWith("WEBVTT")&&v.split(" --> ").length===7,"six caption cues");
ck(m.includes("https://pubmed.ncbi.nlm.nih.gov/16466414/"),"2006 scientific source");
ck(m.includes("https://content.www.wellcomecollection.org/works/demkv24m"),"1843 primary catalogue");
ck(h.includes("https://finalvestige.com/focus/"),"single Focus route");
ck(!a.includes("href=\"https://affiliates.inspire3.com"),"no affiliate portal purchase");
ck(!a.includes("guaranteed health outcome"),"no guarantee");
console.log("PASS",n,"/",n,"static checks. Browser/merchant tests UNTESTED.");
