/* R281 rigorous STATIC pre-release test. Run from repo root:
   node mind/r281/verify_r281.cjs
   This does not validate real browser rendering, CMS sanitization or a merchant transaction. */
"use strict";
const REQUIRED_GATES=[
"named_FV_partner_acceptance","current_signed_affiliate_terms","permitted_website_channel",
"permitted_organic_social_channel","permitted_email_channel_if_used","issued_earning_URL",
"tracking_parameter_rules","current_exact_offer_page","authenticated_cart_total",
"refundable_item_terms","verified_refund_fulfillment_process","creative_audio_video_rights",
"substantiation_for_any_claim","full_browsers_a11y_security_QA","founder_release_approval",
"merchant_reported_settled_commissions"
];
const ALLOWED_HREFS=[
"#main","#decision","#evidence",
"https://finalvestige.com/2026/11/02/mesmerism/",
"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",
"https://finalvestige.com/focus/",
"https://pubmed.ncbi.nlm.nih.gov/37578065/",
"https://pubmed.ncbi.nlm.nih.gov/37205669/",
"https://doi.org/10.1111/acps.13225",
"https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking",
"https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance",
"https://finalvestige.com/affiliate-disclosure/"
];
function decode(s){
 return s.replace(/&#(x[0-9a-f]+|[0-9]+);?/gi,(_,num)=>String.fromCodePoint(num[0].toLowerCase()==="x"?parseInt(num.slice(1),16):parseInt(num,10)))
 .replace(/&(?:colon|sol|Tab|NewLine|quot|apos|amp);/gi,x=>({ "&colon;":":","&sol;":"/","&tab;":"\t","&newline;":"\n","&quot;":'"',"&apos;":"'","&amp;":"&" })[x.toLowerCase()]||x);
}
function tags(html){
 const out=[],re=/<\s*([a-z][a-z0-9:-]*)\b([^<>]*?)>/gi;let m;
 while((m=re.exec(html))){const attrs={};let a,part=m[2];
  const aRe=/([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;
  while((a=aRe.exec(part))){const name=a[1].toLowerCase();const value=decode(a[2]??a[3]??a[4]??"");(attrs[name]??=[]).push(value)}
  out.push({name:m[1].toLowerCase(),attrs,raw:m[0]});
 }
 return out;
}
function verify(input){
 const errors=[],bad=(e)=>errors.push(e);
 const A=input.A||"",B=input.B||"",article=input.article||"",investigation=input.investigation||"";
 let m,n;try{m=typeof input.matrix==="string"?JSON.parse(input.matrix):input.matrix;n=typeof input.r281matrix==="string"?JSON.parse(input.r281matrix):input.r281matrix;}catch(e){return ["Invalid claims JSON"];}
 if(!m||!n)return ["Missing matrices"];
 if(m.commercial_mode!=="HARD_HOLD"||m.publication!=="UNPUBLISHED")bad("R280 commercial mode not held");
 const gates=(m.permissions||[]).map(x=>x.id);
 if(JSON.stringify([...gates].sort())!==JSON.stringify([...REQUIRED_GATES].sort())||m.permissions.some(x=>x.status!=="HARD_HOLD"))bad("Exact R280 gate contract changed");
 if(n.commercial_status!=="HARD_HOLD"||n.publication!=="UNPUBLISHED"||n.authorization_gates?.held!==16||n.authorization_gates?.total!==16)bad("R281 hard hold changed");
 if((m.offer_inventory||[]).length!==5||m.offer_inventory.some(x=>x.paid_order_verified||x.refund_verified||x.affiliate_commission_verified||x.price_authenticated))bad("Offer falsified as paid or authenticated");
 if(m.offer_inventory.some(x=>x.offer_link!==null&&x.id!=="fv_focus_fieldbook"))bad("Unapproved merchant earning link in source matrix");
 if(!m.r281_editorial_corrections||m.r281_editorial_corrections.refund_limit!=="I07")bad("Correction provenance missing");
 const src=new Map((m.source_register||[]).map(x=>[x.id,x]));
 if(src.size!==(m.source_register||[]).length)bad("Duplicate R280 source ID");
 if(src.get("I07")?.url!=="https://hypnosislive.com/faq")bad("Seller refund FAQ origin changed");
 if(!src.get("S01")?.note?.includes("EXCLUDES one-session"))bad("Single-session exclusion removed from evidence matrix");
 if(!src.get("S03")?.note?.includes("n100"))bad("Acute pooled denominator weakened");
 for(const c of m.claims||[])for(const id of c.sources||[])if(!src.has(id))bad("Unknown R280 source "+id);
 const refund=(m.claims||[]).find(c=>c.id==="HYPNOSIS_REFUND");
 if(!refund||!refund.sources.includes("I07")||!refund.claim.includes("five"))bad("Material refund cap lost");
 if(m.claims.find(c=>c.id==="ZEN12_EQUIV")?.classification!=="UNSUBSTANTIATED_EFFICACY")bad("Hour equivalence upgraded to proof");
 if(n.sources?.length!==18||new Set(n.sources.map(s=>s.id)).size!==18)bad("R281 source register changed unexpectedly");
 const sourceIDs=new Set(n.sources.map(s=>s.id));
 if(!n.sources.every(x=>x.url.startsWith("https://")))bad("Insecure R281 source URL");
 if(n.claim_source_map?.length!==16||new Set(n.claim_source_map.map(c=>c.id)).size!==16)bad("R281 claim register changed");
 for(const c of n.claim_source_map||[])for(const id of c.basis||[])if(!sourceIDs.has(id))bad("Unmapped R281 claim source "+id);
 if(n.claim_source_map.find(c=>c.id==="ZEN12_EQUIV")?.level!=="UNSUBSTANTIATED_PRODUCT_SPECIFIC")bad("Branded benefit upgraded");
 if(n.claim_source_map.find(c=>c.id==="SETTLED_SALE")?.level!=="NOT_VERIFIED")bad("Commission fabricated");
 if(n.creator_topic_fit?.length!==3||n.creator_topic_fit.some(x=>x.internal_grok_asset_id!==null))bad("Invented Grok asset ID");
 if(n.conversion_pilot?.merchant_earning_url!==null||n.conversion_pilot?.experiment_live!==false||n.conversion_pilot?.variant_B_media!=="STATIC_POSTER_AND_7_TIMED_TRANSCRIPT_SEGMENTS_NOT_PLAYABLE")bad("Commerce or video improperly activated");
 if(n.conversion_pilot?.first_party_attribution?.affiliate_outbound_is_paid_sale!==false)bad("Clicks confused with sales");
 if(!n.conversion_pilot?.first_party_attribution?.privacy?.includes("no emails"))bad("Privacy promise removed");
 const allowed=ALLOWED_HREFS.slice().sort().join("|");
 for(const [name,html] of [["A",A],["B",B]]){
  if(!html.includes('data-publication="unpublished"')||!html.includes('data-commerce="hold"')||!html.includes('data-experiment="'+name+'"')||!html.includes('content="noindex,nofollow"'))bad(name+" publishing hold lost");
  if(/@import|url\s*\(|\\(?:6a|75|72|6c)/i.test(html))bad(name+" hidden CSS loading vector");
  let buttons=0,hrefs=[];
  for(const tag of tags(html)){
   const a=tag.attrs;
   if(["script","form","iframe","input","object","embed","audio","video","img","link","base","meta-refresh","foreignobject","use","animate","set"].includes(tag.name))bad(name+" disallowed active tag: "+tag.name);
   if(tag.name==="meta"&&(a["http-equiv"]||[]).some(x=>x.toLowerCase()==="refresh"))bad(name+" active meta refresh");
   for(const [attr,vals] of Object.entries(a)){
    if(attr.startsWith("on")||["src","srcset","srcdoc","formaction","action","data","poster","xlink:href"].includes(attr))bad(name+" unsafe attribute "+attr);
    if(attr==="style"&&vals.some(v=>/url\s*\(|@import/i.test(v)))bad(name+" inline remote resource");
    if(attr==="href")for(const v of vals){if(tag.name!=="a"||!ALLOWED_HREFS.includes(v))bad(name+" unapproved href "+v);hrefs.push(v)}
   }
   if(tag.name==="button"){buttons++;if(!("disabled" in a)||a.type?.[0]!=="button")bad(name+" enabled or submit button");}
  }
  if(buttons!==1)bad(name+" added or removed offer controls");
  if(hrefs.slice().sort().join("|")!==allowed)bad(name+" frozen source/navigation link contract changed");
  if(!/<button\b[^>]*\bdisabled\b[^>]*>[\s\S]*?<\/button>\s*<p class="disclosure">[\s\S]{0,400}may earn a commission/i.test(html))bad(name+" nonadjacent or omitted FTC disclosure");
  if(!html.includes("merchant's newsletter")||!html.includes("existing optional Dispatch signup")||!html.includes("no new subscription list"))bad(name+" separate merchant and FV consent lost");
  if(!html.includes("excluded one-session interventions"))bad(name+" mindfulness evidence caveat lost");
  if(!html.includes("Affiliate offer unavailable"))bad(name+" disabled commerce CTA removed");
 }
 if(A.includes('data-experiment-only="video-storyboard"')||!B.includes('data-experiment-only="video-storyboard"')||!B.includes("There is no playable hosted video here."))bad("A/B video status false");
 if(!B.includes("<details>")||!B.includes("<summary>")||!B.includes("<desc"))bad("B poster accessibility absent");
 for(const code of ["00:00–00:06","00:06–00:12","00:12–00:18","00:18–00:24","00:24–00:30","00:30–00:36","00:36–00:42"])if(!B.includes(code))bad("Missing B transcript "+code);
 const norm=x=>x.replace(/<section class="section" aria-labelledby="film" data-experiment-only="video-storyboard">[\s\S]*?<\/section>/,"").replace(/data-experiment="[AB]"/,'data-experiment="X"').replace(/<title>Is Zen12 Worth Considering\? \| Final Vestige draft [AB]<\/title>/,"<title>SAME</title>").replace(/Unpublished [AB] · No live merchant link/g,"Unpublished X · No live merchant link");
 if(norm(A)!==norm(B))bad("Commercial A/B content diverged");
 if(!article.includes("excluded one-session interventions")||!article.includes("three studies totaling 100")||!article.includes("five refunded sessions per year")||!article.includes("https://hypnosislive.com/faq"))bad("R280 editorial repairs absent");
 for(const url of ["10.1016/j.obhdp.2009.04.002","10.1287/orsc.2017.1184","s41599-025-05000-w","https://finalvestige.com/focus/"])if(!investigation.includes(url))bad("Original investigation lost its source "+url);
 if(/we tested Zen12|verified affiliate commission|guaranteed (?:focus|health)/i.test(article+investigation))bad("Fabricated result / efficacy guarantee");
 return errors;
}
function adversarialTests(files){
 const cases=[];
 const add=(name,edit)=>cases.push({name,edit});
 add("unquoted merchant URL",f=>f.A+='<a href=https://zen12.com/hnp?ref=unapproved>BUY</a>');
 add("whitespace merchant URL",f=>f.B+='<a href = "https://zen12.com/hnp">BUY</a>');
 add("entity encoded merchant URL",f=>f.A+='<a href="https&#58;//zen12.com/hnp">BUY</a>');
 add("javascript URI",f=>f.A+='<a href="javascript:alert(1)">offer</a>');
 add("svg xlink resource",f=>f.B+='<svg><use xlink:href="https://bad.example/a.svg#x"/></svg>');
 add("CSS url resource",f=>f.A+='<style>body{background:url(https://bad.example/1)}</style>');
 add("CSS import",f=>f.B+='<style>@import "https://bad.example/x";</style>');
 add("script tracker",f=>f.A+='<script src="https://bad.example/t.js"></script>');
 add("form capture",f=>f.B+='<form action="/capture"><input name="email"></form>');
 add("event handler",f=>f.A+='<p onclick="fetch(1)">unsafe</p>');
 add("meta refresh",f=>f.A+='<meta http-equiv="refresh" content="0;url=https://bad.example"/>');
 add("enabled button",f=>f.B=f.B.replace('<button type="button" disabled','<button type="button"'));
 add("second offer button",f=>f.A+='<button type="button" disabled>other</button>');
 add("missing disclosure",f=>f.A=f.A.replace('may earn a commission','could earn money'));
 add("lost merchant consent",f=>f.B=f.B.replace("merchant's newsletter","vendor messages"));
 add("lost single-session caveat",f=>f.A=f.A.replace('excluded one-session interventions','included single sessions'));
 add("wrong gate name",f=>f.matrix.permissions[0].id="made_up_partner_right");
 add("fake permission",f=>f.matrix.permissions[1].status="VERIFIED");
 add("fabricated paid order",f=>f.matrix.offer_inventory[0].paid_order_verified=true);
 add("unknown claim source",f=>f.r281matrix.claim_source_map[0].basis=["NONEXISTENT"]);
 add("fabricated Grok asset",f=>f.r281matrix.creator_topic_fit[0].internal_grok_asset_id="fake123");
 add("fabricated commission",f=>f.r281matrix.claim_source_map.find(x=>x.id==="SETTLED_SALE").level="VERIFIED");
 add("false video availability",f=>f.r281matrix.conversion_pilot.variant_B_media="PLAYABLE");
 add("changed quote from seller",f=>f.matrix.claims.find(x=>x.id==="ZEN12_EQUIV").classification="PROVEN");
 add("refund omitted",f=>f.article=f.article.replace("five refunded sessions per year","unlimited sessions"));
 add("missing R281 primary",f=>f.investigation=f.investigation.replaceAll("10.1287/orsc.2017.1184","no-source"));
 add("third-party pixel",f=>f.B+='<img src=https://bad.example/p.gif>');
 add("duplicate tracking claims",f=>f.r281matrix.conversion_pilot.first_party_attribution.affiliate_outbound_is_paid_sale=true);
 let passed=0;const failures=[];
 for(const t of cases){const copy=JSON.parse(JSON.stringify(files));t.edit(copy);if(verify(copy).length>0)passed++;else failures.push(t.name)}
 return {total:cases.length,rejected:passed,missed:failures};
}
if(typeof module!=="undefined")module.exports={verify,adversarialTests,tags};
if(typeof require==="function"&&typeof module!=="undefined"&&require.main===module){
 const fs=require("fs");const base="mind/r280/",r281="mind/r281/";
 const input={A:fs.readFileSync(base+"ZEN12-DECISION-GUIDE-A-UNPUBLISHED.html","utf8"),B:fs.readFileSync(base+"ZEN12-DECISION-GUIDE-B-UNPUBLISHED.html","utf8"),
 article:fs.readFileSync(base+"TWELVE-MINUTES-IS-NOT-AN-HOUR-EVIDENCE-REVIEW-UNPUBLISHED.md","utf8"),
 matrix:JSON.parse(fs.readFileSync(base+"OFFER-EVIDENCE-CONVERSION-AUTHORIZATION.json","utf8")),
 investigation:fs.readFileSync(r281+"THE-WORK-YOU-LEFT-BEHIND-FOLLOWED-YOU-UNPUBLISHED.md","utf8"),
 r281matrix:JSON.parse(fs.readFileSync(r281+"ATTENTION-RESIDUE-COMMERCE-CLAIM-AND-CREATOR-MATRIX.json","utf8"))};
 const errors=verify(input),result=adversarialTests(input);console.log(JSON.stringify({baseline:errors.length?"FAIL":"PASS",errors,adversarial:result}));
 if(errors.length||result.rejected!==result.total)process.exitCode=1;
}
