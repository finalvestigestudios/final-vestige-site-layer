#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path');
const names=["THE_WORD_THAT_STOPPED_COMPETING.md","ZEN12_A_TEXT_REVIEW.html","ZEN12_B_OPTIONAL_FILM_REVIEW.html","ZEN12_42S_CAPTIONS.vtt","PRODUCT_CLAIMS_AND_RELEASE_GATES.json","MIND_HUB_WORDPRESS_REVIEW_ONLY.html","CONVERSION_AND_ATTRIBUTION_ACCEPTANCE.md"];
function verify(f){
 const fail=[];let count=0;function c(n,v){count++;if(!v)fail.push(n)}
 const art=f["THE_WORD_THAT_STOPPED_COMPETING.md"],a=f["ZEN12_A_TEXT_REVIEW.html"],b=f["ZEN12_B_OPTIONAL_FILM_REVIEW.html"],v=f["ZEN12_42S_CAPTIONS.vtt"],h=f["MIND_HUB_WORDPRESS_REVIEW_ONLY.html"],g=f["CONVERSION_AND_ATTRIBUTION_ACCEPTANCE.md"];let x;
 try{x=JSON.parse(f["PRODUCT_CLAIMS_AND_RELEASE_GATES.json"])}catch{fail.push("valid matrix JSON");return {count,fail}}
 c("full article length",art.split(/\s+/).length>2000);
 for(const t of ["2002","2006","2024","2023","Puységur","twelve-minute","suggestion","Zen12","Hypnosis Live","Brainwave Shots"])c("article anchor "+t,art.toLowerCase().includes(t.toLowerCase()));
 for(const t of ["https://pubmed.ncbi.nlm.nih.gov/12470132/","https://pubmed.ncbi.nlm.nih.gov/16466414/","https://doi.org/10.1080/00207144.2024.2356856","https://pmc.ncbi.nlm.nih.gov/articles/PMC10198548/"])c("article source "+t,art.includes(t));
 for(const [label,s] of [["A",a],["B",b]]){
  c(label+" html lang and main",s.includes('<html lang="en">')&&s.includes("<main"));
  c(label+" responsive viewport",s.includes("width=device-width"));
  c(label+" robots draft",s.includes("noindex,nofollow"));
  c(label+" script-free",!/<script\b|onclick=|onload=/i.test(s));
  c(label+" form-free",!/<form\b/i.test(s));
  c(label+" actual disabled CTA",/<button[^>]*disabled[^>]*>/.test(s));
  const button=s.lastIndexOf('class="cta" disabled'),disclosure=s.lastIndexOf("Affiliate disclosure:");
  c(label+" near-CTA FTC disclosure",disclosure>0&&button>disclosure&&button-disclosure<1100);
  c(label+" no earning URL",!/<a[^>]*href=["'][^"']*(affiliates\.inspire3|\/hop\/|clickbank)[^"']*["']/i.test(s));
  c(label+" zero clickable seller links",!/<a[^>]*href=["\x27]https:\/\/(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(s));
  c(label+" no fake experience",s.includes("have not purchased or personally tested"));
  c(label+" only existing Focus signup",s.includes('href="https://finalvestige.com/focus/"'));
  c(label+" no active video/iframe",!/<video\b|<iframe\b/i.test(s));
  c(label+" no autoplay",!/<video[^>]*autoplay/i.test(s));
  c(label+" mobile reduced motion",s.includes("@media(max-width:600px)")&&s.includes("prefers-reduced-motion"));
 }
 const ma=a.match(/<main class="frame">([\s\S]*?)<\/main>/)?.[1],mb=b.match(/<main class="frame">([\s\S]*?)<\/main>/)?.[1]?.replace(/<section class="panel" id="film"[\s\S]*?<\/section>/,"");
 c("content parity exactly",!!ma&&ma===mb);
 c("video before offer",b.indexOf('id="film"')>=0&&b.indexOf('id="film"')<b.indexOf('id="offer"'));
 c("poster title+description",b.includes('aria-labelledby="poster-title poster-desc"')&&b.includes("<desc"));
 c("film 6-part transcript",b.includes("Read the complete accessible transcript")&&b.includes("00:35–00:42"));
 c("B links caption file",b.includes("ZEN12_42S_CAPTIONS.vtt"));
 c("VTT header",v.startsWith("WEBVTT"));
 c("VTT 6 cues",(v.match(/ --> /g)||[]).length===6);
 c("VTT ends 42 seconds",v.includes("00:00:42.000"));
 c("hub four streams",["Perception & Attention","History of Suggestion","Practice & Reflection","Tools Under Review"].every(s=>h.includes(s)));
 c("hub no new signup or script",!/<script\b|<form\b/i.test(h));
 c("hub only real article routes",h.includes("https://finalvestige.com/2026/11/02/change-blindness/")&&!h.includes('href="/mind/'));
 c("hub provenance and free resource",h.includes("Puységur")&&h.includes("52-page"));
 c("25 claims",x.claims.length>=25);
 c("28 gates",x.commercial_gates.length>=28);
 c("all gates closed",x.commercial_gates.every(z=>z.status==="CLOSED"));
 c("earning URL NULL",x.earning_url===null);
 c("no claimed paid results",x.merchant_verified_paid_order===null&&x.merchant_verified_affiliate_commission===null);
 c("unsubstantiated omitted",x.claims.filter(z=>z.classification.startsWith("unsupported")).every(z=>z.editorial_action.startsWith("OMIT")));
 c("claim source URLs",x.claims.every(z=>z.sources.length&&z.sources.every(url=>/^https:\/\//.test(url))));
 c("contract net unknown",g.includes("NOT COMPUTABLE")&&g.includes("qualified human")&&g.includes("refund"));
 c("creator ids unknown",g.includes("asset_id **NULL**")&&g.includes("TASK-008"));
 c("commercial hold",g.includes("No earning link may be enabled")&&g.includes("No WordPress CMS/draft/navigation write"));
 return {count,fail}
}
const files=Object.fromEntries(names.map(name=>[name,fs.readFileSync(path.join(__dirname,name),'utf8')]));
const r=verify(files);console.log(r.count+' source assertions',r.fail.length+' failures');if(r.fail.length){console.error(r.fail.join('\n'));process.exitCode=1;}
// Source checks only; no substitute for WordPress rendering/browser/performance/merchant verification.
