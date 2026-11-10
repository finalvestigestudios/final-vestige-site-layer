"use strict";
/* R264 source-only tests; run: node mind/r264/test_r264.cjs
   Not merchant authorization, WP sanitization, browser a11y or revenue proof. */
const F=["THE-GORILLA-IN-THE-SCAN-UNPUBLISHED.md","CLAIM-PROOF-PARTNER-AND-REVENUE-GATES.json","ZEN12-A-TEXT-GUIDE-UNPUBLISHED.html","ZEN12-B-OPTIONAL-FILM-GUIDE-UNPUBLISHED.html","MIND-EVIDENCE-ARCHIVE-UNPUBLISHED-WP-PREVIEW.html","OFFER-FUNNEL-BLOCKER-EXPERIMENT-ACCEPTANCE.md"];
const G=["publisher_named_acceptance","issued_affiliate_url","specific_zen12_product_and_destination","website_channel_permission","social_channel_permission","email_channel_permission","approved_creative_usage_rights","exact_checkout_price_and_currency","merchant_tax_shipping_or_extra_charges","product_inclusion_equivalence_promo_vs_standard","refund_terms_specific_offer","merchant_refund_actual_process","buyer_facing_compliant_disclosure","first_party_event_definition_owner_signoff","merchant_confirmed_paid_commission_feed","founder_editorial_QA_release_approval"];
const ALLOW=["https://inspire3.com/","https://zen12.com/?no-popup=1","https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance"];
function withoutFilm(b){
 const i=b.indexOf('<section class="band wrap"><p class="label">OPTIONAL VIDEO /');
 if(i<0)return null;
 const j=b.indexOf("</section>",i);
 return j<0?null:b.slice(0,i)+b.slice(j+10);
}
function validate(f){
 const e=[];
 for(const name of F)if(typeof f[name]!=="string"||f[name].length<800)e.push("missing/short:"+name);
 if(e.length)return e;
 const [article,jtext,a,b,hub,plan]=F.map(n=>f[n]);
 let j;try{j=JSON.parse(jtext)}catch(x){return ["invalid JSON"]};
 if(j.status!=="DRAFT_UNPUBLISHED_COMMERCIAL_HARD_HOLD")e.push("not hardhold");
 if(j.sources?.length!==19||j.claims?.length!==32)e.push("sources or claims missing");
 if(new Set(j.sources?.map(x=>x.id)).size!==19||new Set(j.claims?.map(x=>x.id)).size!==32)e.push("duplicate source/claim");
 if(!j.claims?.every(x=>x.source_ids?.every(id=>j.sources.some(s=>s.id===id))))e.push("source link missing");
 if(j.commercial_gates?.length!==16||new Set(j.commercial_gates.map(x=>x.id)).size!==16||G.some(x=>!j.commercial_gates.some(g=>g.id===x)))e.push("gate list changed");
 if(j.commercial_gates?.some(x=>x.status!=="HARD_HOLD"||x.decision!=="NO_ACTIVATION"||x.evidence!==null))e.push("gate activated");
 const flags=["no_cms","no_site_nav","no_merge","no_deploy","no_email","no_social","no_spend","no_affiliate_activation","no_new_tracking"];
 if(flags.some(x=>j.release_bounds?.[x]!==true))e.push("release boundary lifted");
 if(j.funnel?.merchant_confirmed_paid_sale!=="UNKNOWN"||j.funnel?.settled_commission!=="UNKNOWN"||j.funnel?.net_revenue_per_1000_qualified_sessions!=="NOT_COMPUTABLE")e.push("fabricated payment");
 if(!article.includes("Twenty of the 24")||!article.includes("2024 review")||!article.includes("https://pubmed.ncbi.nlm.nih.gov/23863753/")||!article.includes("No affiliate URL or commercial recommendation"))e.push("article research or ethics boundary changed");
 if(/<script|<form|hop.clickbank/i.test(article))e.push("commercial markup in investigation");
 for(const [name,v] of [["A",a],["B",b],["hub",hub]]){
  if(/<(script|form|video|iframe|object|embed)\b/i.test(v)||/\bautoplay\s*=/i.test(v))e.push(name+":active UI/injected content");
  if(/(?:href|src)\s*=\s*["']\s*(javascript:|data:|\/\/)/i.test(v))e.push(name+":invalid scheme");
  const re=/href="([^"]+)"/g;let m;
  while((m=re.exec(v))!==null){
   const u=m[1];
   if(u.startsWith("https://")&&!ALLOW.includes(u))e.push(name+":unexpected external link");
   if(!u.startsWith("https://")&&!u.startsWith("/")&&!u.startsWith("#"))e.push(name+":unexpected href");
  }
  const di=v.indexOf("If you purchase through");const bi=v.indexOf("<button");
  if(di<0||bi<0||bi<di||bi-di>1200)e.push(name+":disclosure not beside offer");
  if(!v.includes('type="button" disabled aria-disabled="true"'))e.push(name+":active commercial control");
  if(!/no (earning|affiliate) link/i.test(v))e.push(name+":no hardhold explanation");
 }
 if(withoutFilm(b)!==a)e.push("A/B buyer text mismatch");
 if((b.match(/<li>/g)||[]).length!==7||!b.includes("00–06")||!b.includes("36–42")||!b.includes("00:00–00:42")||!b.includes('aria-labelledby="poster-title poster-desc"'))e.push("film 42s/accessibility metadata broken");
 if(a.includes("<svg"))e.push("A contains film");
 for(const u of ['href="/2026/11/02/change-blindness/"','href="/free-resources/puysegurs-animal-magnetism-files/"','href="/focus/"'])if(!hub.includes(u))e.push("hub broken:"+u);
 if(!hub.includes("NOT LIVE"))e.push("hub unpublished article incorrectly public");
 for(const t of ["confirmed_signup","subscribe","verified_paid_order","NOT COMPUTABLE","Grok retains","No additional script"])if(!plan.includes(t))e.push("measurement/ownership missing:"+t);
 return e;
}
function runSuite(original){
 const baseline=validate(original);
 if(baseline.length)throw Error("BASELINE FAIL "+baseline.join("|"));
 const tests=[];
 const edit=(id,filename,fn)=>tests.push([id,()=>({...original,[filename]:fn(original[filename])})]);
 const mat=(id,fn)=>edit(id,F[1],s=>JSON.stringify(fn(JSON.parse(s))));
 mat("gate approval",j=>(j.commercial_gates[0].status="APPROVED",j));
 mat("gate identity",j=>(j.commercial_gates[1].id="wrong",j));
 mat("gate evidence",j=>(j.commercial_gates[3].evidence="assumed",j));
 mat("release flag",j=>(j.release_bounds.no_cms=false,j));
 mat("fake order",j=>(j.funnel.merchant_confirmed_paid_sale="VERIFIED",j));
 mat("fake revenue",j=>(j.funnel.net_revenue_per_1000_qualified_sessions="8.22",j));
 mat("missing claim",j=>(j.claims.pop(),j));
 mat("broken citation",j=>(j.claims[0].source_ids=["S999"],j));
 mat("removed source",j=>(j.sources.pop(),j));
 mat("duplicate gate",j=>(j.commercial_gates[15]=j.commercial_gates[0],j));
 edit("inject form",F[2],s=>s+"<form><input name=email></form>");
 edit("inject script",F[3],s=>s+"<script>alert(1)</script>");
 edit("inject video autoplay",F[3],s=>s+"<video autoplay src=/v.mp4></video>");
 edit("inject iframe",F[4],s=>s+"<iframe src=/x></iframe>");
 edit("activate purchase",F[2],s=>s.replace('type="button" disabled aria-disabled="true"','type="button"'));
 edit("remove disclosure",F[2],s=>s.replace("If you purchase through that link, Final Vestige may earn a commission at no additional cost to you.",""));
 edit("insert merchant link",F[3],s=>s+"<a href=\"https://merchant.example.org/checkout\">Pay</a>");
 edit("change A price copy",F[2],s=>s.replace("48 MP3s","49 MP3s"));
 edit("change B package",F[3],s=>s.replace("48 MP3s","49 MP3s"));
 edit("break film caption",F[3],s=>s.replace("36–42","36–43"));
 edit("break film alt",F[3],s=>s.replace('aria-labelledby="poster-title poster-desc"',''));
 edit("break Focus link",F[4],s=>s.replace('href="/focus/"','href="/foqus/"'));
 edit("remove signup metric",F[5],s=>s.replaceAll("confirmed_signup","signup_click"));
 edit("remove creator owner",F[5],s=>s.replace("Grok retains","Grok seizes"));
 tests.push(["both variants altered identically",()=>{let z={...original};for(const k of [F[2],F[3]])z[k]=z[k].replace("If you purchase through that link, Final Vestige may earn a commission at no additional cost to you.","");return z}]);
 const misses=[];let rejected=0;
 for(const [name,fn] of tests){if(validate(fn()).length)rejected++;else misses.push(name)}
 if(misses.length)throw Error("UNDETECTED "+misses.join(", "));
 return {baseline:"PASS",negative_mutations_rejected:rejected,total_mutations:tests.length,source_files:F.length};
}
if(typeof module!=="undefined")module.exports={F,validate,runSuite};
if(typeof require==="function"&&typeof module!=="undefined"&&require.main===module){
 const fs=require("node:fs"),p=require("node:path");
 const files=Object.fromEntries(F.map(n=>[n,fs.readFileSync(p.join(__dirname,n),"utf8")]));
 try{console.log(JSON.stringify(runSuite(files),null,2))}catch(x){console.error(x.message);process.exitCode=1}
}
