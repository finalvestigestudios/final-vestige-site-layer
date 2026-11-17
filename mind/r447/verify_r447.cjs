/* Run after checking out the R447 draft branch: node mind/r447/verify_r447.cjs */
"use strict";
const fs=require("node:fs"),path=require("node:path");
const names=["THE_HAND_THAT_WASNT_YOURS.md","ZEN12_A_TEXT_ONLY.html","ZEN12_B_OPTIONAL_42S_CONCEPT.html","R447_42S_ORIGINAL_POSTER.svg","R447_42S_ORIGINAL_CAPTIONS.vtt","MIND_HUB_WORDPRESS_SOURCE_ONLY.html","PRODUCT_CLAIM_SOURCE_PARTNER_MATRIX.json","OFFER_FUNNEL_ATTRIBUTION_AND_ACCEPTANCE.md"];
const F={};for(const n of names)F[n]=fs.readFileSync(path.join(__dirname,n),"utf8");
const verify=function verify(F){
 let checks=[];let ck=(name,pass)=>checks.push({name,pass:!!pass});
 const A=F["ZEN12_A_TEXT_ONLY.html"],B=F["ZEN12_B_OPTIONAL_42S_CONCEPT.html"],H=F["MIND_HUB_WORDPRESS_SOURCE_ONLY.html"],V=F["R447_42S_ORIGINAL_CAPTIONS.vtt"],P=F["R447_42S_ORIGINAL_POSTER.svg"],R=F["THE_HAND_THAT_WASNT_YOURS.md"],E=F["OFFER_FUNNEL_ATTRIBUTION_AND_ACCEPTANCE.md"];
 let M;try{M=JSON.parse(F["PRODUCT_CLAIM_SOURCE_PARTNER_MATRIX.json"])}catch(e){M={claims:[],commercial_release_gates:[],sources:{}};}
 ck("article deep original editorial",R.split(/\s+/).length>=1800);
 for(const needle of ["Botvinick","proprioceptive drift","asynchronous","1998","2011","2022","2023","Puységur","disagreement","paywalled","not a retail product"]){ck("article has evidence "+needle,R.toLowerCase().includes(needle.toLowerCase()))}
 ck("article lists primary doi",R.includes("10.1038/35784"));ck("article links canonical archive",R.includes("finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"));
 for(const [id,s] of [["A",A],["B",B],["H",H]]){
 ck(id+" one main opening",(s.match(/<main\b/g)||[]).length===1);
 ck(id+" one main closing",(s.match(/<\/main>/g)||[]).length===1);
 ck(id+" has language",s.includes('<html lang="en">'));
 ck(id+" viewport",s.includes('name="viewport"'));
 ck(id+" robots noindex",s.includes('content="noindex,nofollow"'));
 ck(id+" has h1",(s.match(/<h1\b/g)||[]).length===1);
 ck(id+" no scripts",!/<script\b/i.test(s));
 ck(id+" no iframe",!/<iframe\b/i.test(s));
 ck(id+" no injected forms",!/<form\b/i.test(s));
 ck(id+" no tracking pixel",!/analytics\.|googletagmanager|facebook\.com\/tr|doubleclick|dataLayer/i.test(s));
 ck(id+" no active merchant href",!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots|affiliates\.inspire3)\.com/i.test(s));
 ck(id+" no forced motion/autoplay",!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(s));
 ck(id+" keyboard focus styles",s.includes(":focus-visible"));
 ck(id+" reduced motion",s.includes("prefers-reduced-motion"));
 ck(id+" owned live focus link",s.includes('href="https://finalvestige.com/focus/"'));
 ck(id+" no price countdown",!/buy now|limited time|only today|\\$[0-9]+/i.test(s));
 }
 for(const [id,s] of [["A",A],["B",B]]){
  ck(id+" exactly one offer button",(s.match(/<button\b/g)||[]).length===1);
  ck(id+" native disabled",/<button\b[^>]*\bdisabled\b/.test(s));
  ck(id+" disclosures precede button",s.indexOf("Affiliate disclosure")<s.indexOf("<button"));
  ck(id+" disclosure and button adjacency",s.slice(s.indexOf("Affiliate disclosure"),s.indexOf("<button")).length<460);
  ck(id+" no active offer",s.includes("Commercial offer inactive")&&s.includes("View verified Zen12 offer — unavailable"));
  ck(id+" seller claim explicitly limited",s.includes("not a conclusion Final Vestige can substantiate"));
  ck(id+" self test substantive",s.includes("One useful test before any purchase"));
  ck(id+" no personal endorsement",s.includes("We have not used, purchased"));
 }
 let filmbegin=B.indexOf('<section class="box film"'),filmend=B.indexOf("</section>",filmbegin);
 let Bneutral=filmbegin>=0?B.slice(0,filmbegin)+B.slice(filmend+"</section>".length):"";
 ck("A/B complete buyer content parity",A===Bneutral);
 ck("B optional film only",filmbegin>0&&B.includes("Video concept only"));
 ck("B full static transcript",B.includes("0–7s.")&&B.includes("35–42s."));
 ck("B poster filename",B.includes('src="R447_42S_ORIGINAL_POSTER.svg"'));
 ck("poster static SVG",P.includes("<svg")&&P.includes("<title")&&P.includes("<desc")&&!/<script|<foreignObject|<animate|onload=/i.test(P));
 ck("VTT header",V.startsWith("WEBVTT"));
 ck("VTT six cues",(V.match(/-->/g)||[]).length===6);
 ck("VTT ends 42sec",V.includes("00:00:42.000"));
 ck("H four stream paths",["Perception &amp; attention","History of suggestion","Practice &amp; reflection","Tools under review"].every(t=>H.includes(t)));
 ck("H live change-blindness",H.includes("2026/11/02/change-blindness/"));
 ck("H does not link unpublished public article",!H.includes("href=\"https://finalvestige.com/mind/"));
 ck("E three creator choices",["Change blindness:","The rubber hand:","Puységur:"].every(t=>E.includes(t)));
 ck("E revenue denominator caution",E.includes("NOT COMPUTABLE"));
 ck("E event distinction",E.includes("affiliate_click")&&E.includes("merchant_confirmed_purchase")&&E.includes("settled_net_revenue"));
 ck("E 7/30 cohorts",E.includes("Seven-day and thirty-day cohorts"));
 ck("E no invented creator IDs",E.includes("Creator asset ID = UNVERIFIED"));
 ck("matrix at least 30 claims",M.claims.length>=30);
 ck("matrix 28 closed release gates",M.commercial_release_gates.length===28&&M.commercial_release_gates.every(g=>g.status==="HOLD"));
 ck("matrix public sources >= 15",Object.keys(M.sources).length>=15);
 ck("matrix no invented revenue",M.metrics?.status==="NOT COMPUTABLE"&&M.metrics?.observed_paid_orders===null);
 ck("matrix no authenticated partner",M.claims.some(c=>c.id==="partner-rights"&&c.status==="NOT AUTHENTICATED"));
 ck("matrix seller efficacy held",M.claims.some(c=>c.id==="zen12-onehour"&&c.status==="UNSUBSTANTIATED PRODUCT-SPECIFIC"));
 ck("matrix every claim sourced",M.claims.every(c=>Array.isArray(c.source_urls)&&c.source_urls.length&&c.source_urls.every(u=>u.startsWith("https://"))));
 return checks;
};
const checks=verify(F),failures=checks.filter(x=>!x.pass);
for(const x of checks)console.log((x.pass?"PASS ":"FAIL ")+x.name);
console.log(JSON.stringify({assertions:checks.length,passed:checks.length-failures.length,failed:failures.length}));
if(failures.length)process.exitCode=1;
