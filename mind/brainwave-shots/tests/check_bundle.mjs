/* Pure ECMAScript source-integrity QA; host passes an object of filename=>text.
 * Zero dependency, zero network or CMS calls, reproducible on the actual PR head.
 */
export function audit(files){
 const checks=[];const check=(name,pass,details="")=>checks.push({name,pass:!!pass,details});
 const html=files["page-focus-shot-guide.blocks.html"]||"";
 const article=files["article-change-blindness.md"]||"";
 const readme=files["README.md"]||"";
 const copy=files["offer-copy-map.md"]||"";
 const tracking=files["attribution-and-experiment.md"]||"";
 const video=files["video-storyboard.md"]||"";
 let data={};try{data=JSON.parse(files["offer-claims.json"]||"{}")}catch(e){check("matrix JSON parses",false,String(e))}
 const count=s=>s.replace(/<[^>]+>/g," ").trim().split(/\s+/).filter(Boolean).length;
 check("seven core documents",["page-focus-shot-guide.blocks.html","article-change-blindness.md","README.md","offer-copy-map.md","attribution-and-experiment.md","video-storyboard.md","offer-claims.json"].every(x=>typeof files[x]==="string"&&files[x].length>200));
 check("29+ audited claims",data.claims?.length>=29);
 check("14+ specific citations",data.sources?.length>=14);
 check("claim IDs unique",new Set((data.claims||[]).map(x=>x.id)).size===data.claims?.length);
 check("each claim has verdict",data.claims?.every(x=>typeof x.disposition==="string"&&x.disposition.length>5));
 const ids=new Set((data.sources||[]).map(x=>x.id));
 check("each claim sources exist",data.claims?.every(x=>x.source_ids?.length>0&&x.source_ids.every(s=>ids.has(s))));
 check("official focus shot and faq sources",["vendor_focus","vendor_faq"].every(x=>ids.has(x)));
 check("source links are full URLs",data.sources?.every(x=>x.url?.startsWith("https://")));
 check("inert affiliate and partner status",data.affiliate_url===null&&data.partner_approval_verified===false&&data.status==="DRAFT_NONCOMMERCIAL_NO_PARTNER_URL");
 check("no invented price",data.price===null&&data.price_verified_at_checkout===false);
 check("no first hand or audio audit",data.audio_file_tested===false&&data.audio_technical_analysis===false&&data.purchase_tested===false);
 check("merchant outcomes rejected",["B08","B09","B10","B11","B12"].every(x=>data.claims?.find(c=>c.id===x)?.disposition.startsWith("REJECT")));
 check("binaural not mistaken for isochronic",data.claims?.find(x=>x.id==="B21")?.disposition==="REJECT_DIFFERENT_STIMULUS");
 check("article long-form >1200 words",count(article)>1200,count(article));
 check("historical article free of merchant promotions",!article.includes("brainwaveshots.com")&&!article.includes("Affiliate disclosure:")&&!article.includes("buy now"));
 check("historical article primary sources",article.includes("10.3758/BF03208840")&&article.includes("psychologicalscience.org"));
 check("historical article live free focus",article.includes("https://finalvestige.com/focus/"));
 check("guide substantive >1100 words",count(html)>1100,count(html));
 check("accessible single H1", (html.match(/<h1\b/g)||[]).length===1 && html.includes('aria-labelledby="bws-title"'));
 check("responsive breakpoints 460 and 850",html.includes("max-width:460px")&&html.includes("max-width:850px"));
 check("focus style and reduced motion",html.includes(":focus-visible")&&html.includes("prefers-reduced-motion:reduce"));
 check("no scripts iframes or autoplay",!/<script\b|<iframe\b|autoplay\s*=|gtag\(|fbq\(/i.test(html));
 check("no active affiliate or checkout links",!/<a[^>]+href=["'][^"']*(?:affiliates\.inspire3|checkout|hoplink|clickbank)[^"']*["']/i.test(html));
 check("inert merchant CTA",html.includes('aria-disabled="true"')&&html.includes("awaiting authorization"));
 check("on-page disclosure near locked CTA",html.includes("Affiliate disclosure:")&&html.indexOf("Affiliate disclosure:")<html.indexOf('aria-disabled="true"'));
 check("free fieldbook active",html.includes('href="https://finalvestige.com/focus/"'));
 check("actual merchant offer factual citation",html.includes("https://brainwaveshots.com/focus-shot"));
 check("seller safety caveat and refund limits",html.includes("epilepsy")&&html.includes("six-month")&&html.includes("refund"));
 check("research scope qualified",html.includes("isochronic")&&html.includes("binaural")&&html.includes("not a clinical evaluation"));
 check("offer map product specific",copy.includes("Focus Shot")&&copy.includes("isochronic")&&copy.includes("FAQ"));
 check("attribution not installed",tracking.includes("no tracking installed")&&tracking.includes("disabled until"));
 check("video is proposal not invented production",video.includes("NOT A FINISHED VIDEO")&&video.includes("00:31"));
 check("homepage and newsletter protected",readme.includes("PR #49")&&readme.includes("Issue #174")&&readme.includes("No production edits"));
 return {passed:checks.filter(c=>c.pass).length,total:checks.length,failed:checks.filter(c=>!c.pass),checks};
}
