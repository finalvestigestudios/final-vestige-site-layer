/* Mind R280 source-custody and commercialization tests.
   Node: node mind/r280/verify_r280.cjs [repo root defaults process.cwd()].
   V8: evaluate this file, then call verify({A,B,matrix,article}) and adversarialTests.
   These are STATIC safety checks, NOT browser QA, hosted video, merchant checkout,
   affiliate permission or payment settlement evidence. */
function verify(files){
  const errors=[];
  const bad=(msg)=>errors.push(msg);
  const A=files.A||"",B=files.B||"",article=files.article||"";
  let m;try{m=typeof files.matrix==="string"?JSON.parse(files.matrix):files.matrix;}catch(e){bad("Matrix JSON invalid");return errors;}
  if(!m||!Array.isArray(m.permissions)){bad("Missing gates");return errors;}
  if(m.commercial_mode!=="HARD_HOLD"||m.publication!=="UNPUBLISHED")bad("Publication/commercial status changed");
  if(m.permissions.length!==16||m.permissions.some(g=>g.status!=="HARD_HOLD"))bad("Authorization gate incorrectly cleared");
  if(new Set(m.permissions.map(x=>x.id)).size!==16)bad("Duplicated authorization gate");
  if(m.source_register.length<15||m.claims.length<20)bad("Evidence register weakened");
  const sourceIds=new Set(m.source_register.map(x=>x.id));
  for(const c of m.claims){for(const id of c.sources||[])if(!sourceIds.has(id))bad("Unknown source ID: "+id);}
  const requiredClaimIds=["ZEN12_EQUIV","ZEN12_FREE_CONSENT","HYPNOSIS_FOCUS","BWS_ALLDAY","FTC_ADJACENCY","FIELD_BOOK","REVENUE"];
  for(const id of requiredClaimIds)if(!m.claims.some(c=>c.id===id))bad("Missing claim: "+id);
  if(m.claims.find(c=>c.id==="ZEN12_EQUIV")?.classification!=="UNSUBSTANTIATED_EFFICACY")bad("Hour-equivalence falsely substantiated");
  if(m.offer_inventory.length!==5||m.offer_inventory.some(o=>o.paid_order_verified||o.refund_verified||o.affiliate_commission_verified||o.price_authenticated))bad("Commercial verification forged");
  if(m.offer_inventory.filter(o=>o.offer_link!==null).some(o=>o.id!=="fv_focus_fieldbook"))bad("Unauthorized earning link in matrix");
  if(!m.creator_routes ||m.creator_routes.length!==3)bad("Three creator routes missing");
  for(const route of m.creator_routes)if(route.grok_asset_id!==null)bad("Unauthenticated internal asset identifier");
  if(m.creator_routes[1]?.public_video_id!=="SV9m07PFTYk")bad("Historical public video match corrupted");
  if(!m.measurement_contract.no_personal_identifiers||!m.measurement_contract.no_duplicate_scripts)bad("Tracking contract weakened");
  if(!m.measurement_contract.events.includes("merchant_confirmed_paid_order")||!m.measurement_contract.events.includes("affiliate_outbound_click")||!m.measurement_contract.events.includes("cleared_commission"))bad("Revenue stage distinctions removed");
  if(m.experiment.media_status!=="STATIC_STORYBOARD_AND_TIMED_TRANSCRIPT_ONLY"||m.experiment.hold!=="NOT_LIVE_NO_PLAYABLE_MEDIA")bad("False live video experiment");
  if(m.experiment.video_duration_seconds!==42)bad("Video timeline changed");
  for(const [name,html] of [["A",A],["B",B]]){
    if(!html.includes('data-experiment="'+name+'"')||!html.includes('data-publication="unpublished"')||!html.includes('data-commerce="hold"'))bad(name+" publication control weakened");
    if(!html.includes('content="noindex,nofollow"'))bad(name+" draft indexing enabled");
    if(/<\s*(script|form|iframe|input|object|embed|audio|video)\b/i.test(html))bad(name+" active scripting/form/embed added");
    if(/@import|<\s*link\b|<\s*img\b|\b(?:src|srcset)\s*=/i.test(html))bad(name+" third-party loading resource added");
    if(/url\s*\(/i.test(html))bad(name+" CSS-loaded resource added");
    if(/<button[^>]*\btype="submit"|<button(?![^>]*\bdisabled\b)[^>]*>/i.test(html))bad(name+" purchasing control enabled");
    if(/href=["']https?:\/\/(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(html))bad(name+" unauthorized merchant hyperlink");
    if(/href=["'](?!#|https:\/\/(?:finalvestige\.com|pubmed\.ncbi\.nlm\.nih\.gov|doi\.org|www\.ftc\.gov)\/)[^"']+["']/i.test(html))bad(name+" unapproved outbound href");
    if(!/<button[^>]*disabled[^>]*>[\s\S]*?<\/button>\s*<p class="disclosure">[\s\S]{0,400}may earn a commission/i.test(html))bad(name+" missing adjacent honest disclosure");
    if(!html.includes("will receive the merchant's newsletter")&&!html.includes("merchant's newsletter"))bad(name+" seller newsletter consent disappeared");
    if(!html.includes("existing optional Dispatch signup")||!html.includes("no new subscription list"))bad(name+" Focus identity separation removed");
    if(!html.includes("source")||!html.includes("111 randomized")||!html.includes("fourteen EEG")&&!html.includes("fourteen EEG"))bad(name+" scientific grounding missing");
    if(!html.includes("Affiliate offer unavailable"))bad(name+" disabled CTA missing");
    if(/verified (?:affiliate|paid) (?:sale|commission)|we tested (?:Zen12|the product)/i.test(html))bad(name+" forged purchase/experience claim");
  }
  if(A.includes('data-experiment-only="video-storyboard"'))bad("Text-only A includes storyboard");
  if(!B.includes('data-experiment-only="video-storyboard"')||!B.includes("There is no playable hosted video here."))bad("B film status false");
  if(!B.includes("<details>")||!B.includes("<summary>")||!B.includes("<svg")||!B.includes("<desc"))bad("B accessible poster missing");
  const segments=["00:00–00:06","00:06–00:12","00:12–00:18","00:18–00:24","00:24–00:30","00:30–00:36","00:36–00:42"];
  for(const seg of segments)if(!B.includes(seg))bad("B timed transcript missing "+seg);
  const normalize=(html)=>html.replace(/<section class="section" aria-labelledby="film" data-experiment-only="video-storyboard">[\s\S]*?<\/section>/,"").replace(/data-experiment="[AB]"/,'data-experiment="X"').replace(/<title>Is Zen12 Worth Considering\? \| Final Vestige draft [AB]<\/title>/,"<title>SAME</title>");
  if(normalize(A)!==normalize(B))bad("A/B purchasing content diverges beyond film");
  const requiredArticle=["https://zen12.com/hnp","https://zen12.com/freeaudio","https://pubmed.ncbi.nlm.nih.gov/37578065/","https://pubmed.ncbi.nlm.nih.gov/37205669/","https://doi.org/10.1111/acps.13225","https://finalvestige.com/focus/"];
  for(const link of requiredArticle)if(!article.includes(link))bad("Source removed from manuscript: "+link);
  if(!article.includes("No earning link is active") && !article.includes("No earning link is active in this document"))bad("Manuscript marketing status ambiguous");
  return errors;
}
function adversarialTests(files){
 const cases=[];
 const add=(name,changes)=>cases.push({name,changes});
 const replace=(s,a,b)=>s.replace(a,b);
 add("button enabled",f=>f.A=replace(f.A,'<button type="button" disabled','<button type="button"'));
 add("buy button enabled B",f=>f.B=replace(f.B,'<button type="button" disabled','<button type="button"'));
 add("seller earning link A",f=>f.A+= '<a href="https://zen12.com/hnp?ref=abcd">buy now</a>');
 add("seller earning link B",f=>f.B+='<a href="https://affiliates.inspire3.com/x">buy</a>');
 add("JS tracker A",f=>f.A+='<script src="https://analytics.example/script.js"></script>');
 add("inline JS B",f=>f.B+='<script>console.log(1)</script>');
 add("pixel A",f=>f.A+='<img src="https://analytics.example/pixel">');
 add("hidden tracking image B",f=>f.B+='<img src="https://bad.example/pixel" width="1">');
 add("css exfil A",f=>f.A+='<style>.x{background:url(https://bad.example/1)}</style>');
 add("css import B",f=>f.B+='<style>@import "https://bad.example/x.css";</style>');
 add("external font A",f=>f.A+='<link href="https://bad.example/font.css" rel="stylesheet">');
 add("iframe B",f=>f.B+='<iframe src="https://zen12.com"></iframe>');
 add("subscription form A",f=>f.A+='<form><input type="email"></form>');
 add("subscription form B",f=>f.B+='<form></form>');
 add("video autoplay B",f=>f.B+='<video autoplay src="https://bad.example/v.mp4"></video>');
 add("alter A/B copy",f=>f.B=f.B.replace("The evidence has to match the claim.","The evidence is definitely in!"));
 add("remove FTC disclosure A",f=>f.A=f.A.replace("may earn a commission","may get a prize"));
 add("remove FTC disclosure B",f=>f.B=f.B.replace("may earn a commission","may get a prize"));
 add("remove merchant consent A",f=>f.A=f.A.replace("merchant's newsletter","hidden subscription"));
 add("remove merchant consent B",f=>f.B=f.B.replace("merchant's newsletter","hidden subscription"));
 add("publisher approved",f=>f.matrix.permissions[0].status="CLEARED");
 add("one gate deleted",f=>f.matrix.permissions.pop());
 add("duplicate gate",f=>f.matrix.permissions[2].id=f.matrix.permissions[3].id);
 add("fabricated paid order",f=>f.matrix.offer_inventory[0].paid_order_verified=true);
 add("fabricated cleared commission",f=>f.matrix.offer_inventory[0].affiliate_commission_verified=true);
 add("fabricated price",f=>f.matrix.offer_inventory[1].price_authenticated=true);
 add("fabricated refund",f=>f.matrix.offer_inventory[2].refund_verified=true);
 add("affiliate URL smuggling",f=>f.matrix.offer_inventory[0].offer_link="https://fake.example/earned");
 add("seller claim treated as proven",f=>f.matrix.claims.find(x=>x.id==="ZEN12_EQUIV").classification="PROVEN");
 add("missing health context",f=>f.matrix.claims=f.matrix.claims.filter(x=>x.id!=="BWS_ALLDAY"));
 add("unsupported citation ID",f=>f.matrix.claims[0].sources.push("FAKE_SOURCE"));
 add("falsely verified Grok asset",f=>f.matrix.creator_routes[1].grok_asset_id="fake123");
 add("fake creator public ID",f=>f.matrix.creator_routes[1].public_video_id="fake");
 add("rewrite metrics to clicks only",f=>f.matrix.measurement_contract.events=f.matrix.measurement_contract.events.filter(x=>x!=="merchant_confirmed_paid_order"));
 add("enable visitor PII",f=>f.matrix.measurement_contract.no_personal_identifiers=false);
 add("double analytics vendor",f=>f.matrix.measurement_contract.no_duplicate_scripts=false);
 add("video falsely live",f=>f.matrix.experiment.hold="LIVE");
 add("video false playable",f=>f.matrix.experiment.media_status="HOSTED_PLAYABLE");
 add("wrong captions",f=>f.B=f.B.replace("00:36–00:42","00:36–00:43"));
 add("poster aria removed",f=>f.B=f.B.replace("<desc","<invaliddesc"));
 add("missing source in manuscript",f=>f.article=f.article.replace("https://pubmed.ncbi.nlm.nih.gov/37205669/",""));
 add("site publish/indexing",f=>f.A=f.A.replace('content="noindex,nofollow"','content="index,follow"'));
 add("remove draft status",f=>f.B=f.B.replace('data-publication="unpublished"','data-publication="published"'));
 add("CTA text removed",f=>f.A=f.A.replace("Affiliate offer unavailable","Buy now"));
 add("missing direct free route",f=>f.A=f.A.replace("https://finalvestige.com/focus/","https://other.example.com/"));
 const failures=[];
 for(const t of cases){const f={A:files.A,B:files.B,article:files.article,matrix:JSON.parse(JSON.stringify(typeof files.matrix==="string"?JSON.parse(files.matrix):files.matrix))};t.changes(f);if(verify(f).length===0)failures.push(t.name);}
 return {total:cases.length,rejected:cases.length-failures.length,escaped:failures};
}
if(typeof require==="function"&&typeof module!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const d=__dirname;const files={A:fs.readFileSync(path.join(d,"ZEN12-DECISION-GUIDE-A-UNPUBLISHED.html"),"utf8"),B:fs.readFileSync(path.join(d,"ZEN12-DECISION-GUIDE-B-UNPUBLISHED.html"),"utf8"),article:fs.readFileSync(path.join(d,"TWELVE-MINUTES-IS-NOT-AN-HOUR-EVIDENCE-REVIEW-UNPUBLISHED.md"),"utf8"),matrix:fs.readFileSync(path.join(d,"OFFER-EVIDENCE-CONVERSION-AUTHORIZATION.json"),"utf8")};
 const base=verify(files),mut=adversarialTests(files);
 console.log(JSON.stringify({baseline:base.length===0?"PASS":"FAIL",errors:base,mutants:mut},null,2));
 process.exit(base.length===0&&mut.escaped.length===0?0:1);
}
