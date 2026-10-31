/* Mind R10 exact-source, no-network QA; execute: node mind/meditation-attention-r10/qa.cjs */
"use strict";
function audit(input){
 const {feature,page,ledger,conversion,readme}=input;
 const results=[];
 const check=(name,test)=>results.push({name,pass:!!test});
 const row=id=>ledger.claims.find(x=>x.id===id);
 const wc=s=>s.trim().split(/\s+/).filter(Boolean).length;
 check("original investigation >= 2300 words",wc(feature)>=2300);
 check("fully written article not placeholder",!/\b(?:TODO|lorem ipsum|TBD)\b/i.test(feature));
 check("article clearly notes retreat vs product",feature.includes("not a randomized test of a short commercial program"));
 check("specific PLOS study design",feature.includes("17 practitioners")&&feature.includes("23 meditation-interested novices"));
 check("2021 and 2024 counterweight",feature.includes("2021 review")&&feature.includes("2024 meta-analysis"));
 for(const t of ["Raymond","Slagter","Millett","Zainal","Puységur","Zen12"])check("feature includes "+t,feature.includes(t));
 check("published source trail",feature.includes("Source trail / checked October 30, 2026"));
 check("full WordPress page included",page.length>17000);
 check("single HTML h1",(page.match(/<h1\b/g)||[]).length===1);
 check("semantic page label",page.includes('aria-labelledby="fv-r10-title"'));
 const ids=[...page.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
 check("unique HTML IDs",ids.length===new Set(ids).size);
 check("all internal anchors resolve",[...page.matchAll(/href="#([^"]+)"/g)].every(x=>ids.includes(x[1])));
 check("original PLOS linked",page.includes("journals.plos.org/plosbiology/article"));
 check("multiple independent sources",(page.match(/pubmed\.ncbi\.nlm\.nih\.gov/g)||[]).length>=4);
 check("no scripts forms embeds",!/<(?:script|form|iframe|object|embed)\b/i.test(page));
 check("no player loaded",!/<(?:video|audio|source)\b/i.test(page));
 check("no direct seller href",!/href=["']https?:\/\/(?:zen12|inspire3|hypnosislive|brainwaveshots|subliminal)/i.test(page));
 check("no affiliate cloaking",!/(?:bit\.ly|tinyurl\.com|[?&](?:hop|aff(?:iliate)?|clickid|subid|utm_source)=)/i.test(page));
 check("no merchant-buy link",!/<a[^>]+>[^<]*(?:buy now|checkout|seller link)/i.test(page));
 check("no second signup",!/<input\b|<textarea\b|<button[^>]+type="submit"/i.test(page));
 check("no tracking and PII capture",!/(?:gtag\(|fbq\(|dataLayer\.push|google-analytics\.com|connect\.facebook\.net|localStorage|document\.cookie)/i.test(page));
 check("existing free Focus href",page.includes('href="https://finalvestige.com/focus/"'));
 check("existing Puységur href",page.includes('href="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"'));
 check("clear offer disclosure",page.includes("If you purchase through a future approved earning link, Final Vestige may earn a commission at no additional cost to you"));
 const dis=page.indexOf("Potential affiliate relationship"),cta=page.indexOf("Seller link unavailable pending verification");
 check("disclosure directly precedes commercial CTA",dis!==-1&&cta>dis&&cta-dis<1150);
 check("CTA inert span",/<span class="fv-r10-disabled" role="status"[^>]*>Seller link unavailable pending verification<\/span>/.test(page));
 check("commerce explicitly independent",page.includes("not part of the scientific conclusions"));
 check("editorial/affiliate policies linked",page.includes("https://finalvestige.com/affiliate-disclosure/")&&page.includes("https://finalvestige.com/editorial-standards/"));
 check("static exhibit cannot claim to measure blink",page.includes("static version deliberately cannot measure an attentional blink"));
 check("progressive details control",page.includes("<details><summary>"));
 check("keyboard focus",page.includes(":focus-visible"));
 check("reduced motion",page.includes("prefers-reduced-motion:reduce"));
 check("mobile breakpoint",page.includes("@media(max-width:700px)"));
 check("touch target minimum",page.includes("min-height:44px"));
 check("no unpublished slugs activated",!page.includes('href="/mind/'));
 check("ledger 14 sources",ledger.sources.length===14);
 check("ledger 35 claims",ledger.claims.length===35);
 check("unique source ids",new Set(ledger.sources.map(x=>x.id)).size===ledger.sources.length);
 check("unique claim ids",new Set(ledger.claims.map(x=>x.id)).size===ledger.claims.length);
 check("all source ids resolve",ledger.claims.every(x=>x.source_ids.length>0&&x.source_ids.every(k=>ledger.sources.some(s=>s.id===k))));
 check("rejected speed equivalence",row("c24")?.disposition==="reject_no_product_specific_substantiation");
 check("rejected EEG sales inference",row("c14")?.disposition==="reject");
 check("rejected retreat-to-Zen12 inference",row("c26")?.disposition==="reject_category_error");
 check("affiliate status unknown",ledger.affiliate.partner_approval==="unverified");
 check("earning URL null",ledger.affiliate.approved_tracking_url===null);
 check("mutating checkout pricing withheld",ledger.affiliate.pricing==="withheld");
 check("sales not inferred",row("c35")?.disposition==="reject");
 check("privacy-preserving A/B specified",conversion.includes("without cookies, ID, fingerprint")&&conversion.includes("A/B hypothesis"));
 check("pre-registration and non-tracking",conversion.includes("minimum exposure")&&conversion.includes("No extra Jetpack form"));
 check("Founder and Dispatch coordination",conversion.includes("founder release authorization")&&conversion.includes("Dispatch #174"));
 check("protects existing Focus welcome",conversion.includes("existing Jetpack Focus welcome"));
 check("source path documented",readme.includes("node mind/meditation-attention-r10/qa.cjs"));
 check("no premature release",readme.includes("NOT live")&&readme.includes("HOLD"));
 function lum(hex){const v=hex.match(/\w\w/g).map(x=>parseInt(x,16)/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4);return .2126*v[0]+.7152*v[1]+.0722*v[2];}
 for(const [fg,bg] of [["#eee9df","#0b0f10"],["#d0c9bc","#0b0f10"],["#ddb47a","#0b0f10"],["#f6d5a5","#0b0f10"],["#d0c9bc","#131b1c"],["#f0dfc6","#131b1c"],["#ebe4d9","#2a302f"]]){const a=lum(fg.slice(1)),b=lum(bg.slice(1));check("WCAG numeric contrast "+fg+" on "+bg,(Math.max(a,b)+.05)/(Math.min(a,b)+.05)>=4.5);}
 return {passes:results.filter(x=>x.pass).length,total:results.length,failures:results.filter(x=>!x.pass).map(x=>x.name),results};
}
if(typeof module!=="undefined")module.exports={audit};
if(typeof require==="function"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const dir=__dirname,f=n=>fs.readFileSync(path.join(dir,n),"utf8");
 const fixture={feature:f("feature.md"),page:f("page-meditation-attention.blocks.html"),ledger:JSON.parse(f("claim-evidence-ledger.json")),conversion:f("conversion-and-qa.md"),readme:f("README.md")};
 const r=audit(fixture);
 for(const x of r.results)console.log((x.pass?"PASS ":"FAIL ")+x.name);
 console.log("SOURCE AUDIT "+r.passes+"/"+r.total);
 const clone=()=>JSON.parse(JSON.stringify(fixture));
 const muts=[
 x=>{x.page=x.page.replace("Potential affiliate relationship","No disclosure label");},
 x=>{x.page=x.page.replace("If you purchase through a future approved earning link, Final Vestige may earn a commission at no additional cost to you","Buy now");},
 x=>{x.page+="<script>gtag('config','UA-foo')</script>";},
 x=>{x.page+='<form><input type="email"></form>';},
 x=>{x.page+='<a href="https://zen12.com/getstarted">buy now</a>';},
 x=>{x.page=x.page.replace("prefers-reduced-motion:reduce","prefers-more-motion:reduce");},
 x=>{x.page=x.page.replace('id="fv-r10-offer"','id="fv-r10-read"');},
 x=>{x.page=x.page.replace('href="https://finalvestige.com/focus/"','href="/mind/unpublished"');},
 x=>{x.ledger.claims.find(y=>y.id==="c24").disposition="supported";},
 x=>{x.ledger.affiliate.approved_tracking_url="https://example.com/unapproved";},
 x=>{x.feature=x.feature.replace("17 practitioners","17 buyers");},
 x=>{x.ledger.sources.pop();}
 ];
 let killed=0;
 for(let i=0;i<muts.length;i++){const x=clone();muts[i](x);const bad=audit(x);const caught=bad.passes<bad.total;console.log((caught?"KILLED ":"SURVIVED ")+("mutant-"+(i+1)));if(caught)killed++;}
 console.log("MUTATION "+killed+"/"+muts.length);
 if(r.failures.length||killed!==muts.length)process.exitCode=1;
}
