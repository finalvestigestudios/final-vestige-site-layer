"use strict";
const fs=require("node:fs");
const path=require("node:path");
const assert=require("node:assert/strict");
const root=__dirname;
const read=(name)=>fs.readFileSync(path.join(root,name),"utf8");
const files={
  a:read("ZEN12_A_TEXT_REVIEW.html"),
  b:read("ZEN12_B_FILM_REVIEW.html"),
  article:read("THE_FACE_THAT_CHANGED_WHEN_TURNED_UPRIGHT.md"),
  hub:read("MIND_HUB_WP_REVIEW_ONLY.html"),
  docs:read("CONVERSION_ACCEPTANCE.md"),
  vtt:read("ZEN12_42S_CAPTIONS.vtt"),
  matrix:read("CLAIMS_AND_AUTHORIZATION.json")
};
function validate(s){
 const fail=[];
 const bad=(what,condition)=>{if(condition)fail.push(what)};
 let matrix;
 try{matrix=JSON.parse(s.matrix)}catch(e){fail.push("matrix parse");return fail}
 const base=(x)=>x.substring(x.indexOf('<main id="content">')).replace(/<section aria-labelledby="film">[\s\S]*?<\/section>/,"");
 bad("AB content parity",base(s.a)!==base(s.b));
 for(const k of ["a","b"]){
  const h=s[k];
  bad(k+" disclosure missing",!h.includes("Affiliate disclosure:"));
  bad(k+" disabled CTA missing",!/<button\b[^>]*\bdisabled\b[^>]*>/.test(h));
  bad(k+" disclosure not before CTA",h.indexOf("Affiliate disclosure:")>h.indexOf("Zen12 purchase link withheld"));
  bad(k+" new signup form",/<form\b/i.test(h));
  bad(k+" unsafe script",/<script\b/i.test(h));
  bad(k+" earning URL",/href="[^"]+(?:[?&](?:affiliate|aff_id|ref|hop|subid)=|go\.inspire3)/i.test(h));
  bad(k+" autoplay video",/<video[^>]*\bautoplay\b/i.test(h));
  bad(k+" source page absent",!h.includes("https://zen12.com/"));
  bad(k+" seller newsletter consent absent",!h.includes("seller's own newsletter"));
  bad(k+" Focus route absent",!h.includes("https://finalvestige.com/focus/"));
  bad(k+" skip link absent",!h.includes('href="#content"'));
  bad(k+" noindex absent",!h.includes("noindex,nofollow"));
 }
 bad("B missing original poster",!s.b.includes("<svg "));
 bad("B missing transcript",!s.b.includes("Read the full six-scene transcript"));
 bad("A accidentally includes film",s.a.includes("Read the full six-scene transcript"));
 bad("VTT invalid",!s.vtt.startsWith("WEBVTT")||(s.vtt.match(/ --> /g)||[]).length!==6||!s.vtt.includes("00:00:42.000"));
 bad("commercial gates open",Object.values(matrix.release_gates||{}).some(x=>x!==false)||Object.keys(matrix.release_gates||{}).length<20);
 bad("claim matrix thin",(matrix.claims||[]).length<18);
 bad("seller efficacy adopted",!matrix.claims.some(x=>x.id==="zen-equivalence"&&x.editorial==="DO NOT ADOPT"));
 bad("product authorization invented",!matrix.claims.some(x=>x.id==="affiliate-approval"&&x.editorial==="UNVERIFIED"));
 bad("article insufficient",s.article.split(/\s+/).length<1600);
 bad("historical link missing",!s.article.includes("puysegurs-animal-magnetism-files/"));
 bad("paid evidence conflated",!s.docs.includes("NOT COMPUTABLE")||!s.docs.includes("affiliate_outbound")||!s.docs.includes("merchant_confirmed_order"));
 bad("unverified asset omitted",(s.docs.match(/Asset ID \*\*NULL\*\*|asset_id = \*\*NULL\*\*|asset_id = \*\*NULL\*\*/g)||[]).length<1 && !s.docs.includes("asset_id = **NULL**"));
 bad("Hub links imaginary route",/href="\/mind\//.test(s.hub));
 bad("Hub lacks canonical sources",!s.hub.includes("https://finalvestige.com/focus/")||!s.hub.includes("puysegurs-animal-magnetism-files/"));
 return fail;
}
const problems=validate(files);assert.deepEqual(problems,[],problems.join("; "));
const mutations=[
 ["enabled CTA",(s)=>{s.a=s.a.replace(/<button type="button" disabled aria-disabled="true">/,'<button type="button">');}],
 ["removed disclosure",(s)=>{s.b=s.b.replace("Affiliate disclosure:","Nothing to disclose:");}],
 ["additional signup",(s)=>{s.a+="<form><input name=email></form>";}],
 ["third-party tracking",(s)=>{s.b+="<script src='https://tracker.invalid/x.js'></script>";}],
 ["opened merchant gate",(s)=>{const m=JSON.parse(s.matrix);m.release_gates.partner_approval=true;s.matrix=JSON.stringify(m);}],
 ["fabricated affiliate URL",(s)=>{s.a+='<a href="https://example.com/?aff_id=mock">Buy</a>'; }],
 ["false conversion baseline",(s)=>{s.docs=s.docs.replace("NOT COMPUTABLE","Net revenue proven");}],
 ["autoplay",(s)=>{s.b+='<video autoplay src="unapproved.mp4"></video>'; }]
];
let caught=0;
for(const [name,mutate] of mutations){
 const s={...files};mutate(s);const f=validate(s);
 if(!f.length)throw new Error("Mutation escaped: "+name);
 caught++;
}
console.log("PASS", Object.keys(files).length, "source files; all",mutations.length,"unsafe mutations rejected");
