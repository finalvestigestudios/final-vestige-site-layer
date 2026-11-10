"use strict";
/**
 * R270 regression of EXISTING held R268 A/B/hub + R269 matrix and R257 VTT.
 * This is an independent additive test; it does not change R269 source or
 * assert browser, accessibility, CMS, commissions, subscriber counts or sales.
 * Usage from repository root: node mind/r270/test_commercial_custody.cjs
 */
const fs=require("node:fs"), path=require("node:path");
const NAMES={
 a:"mind/r268/ZEN12-A-TEXT-UNPUBLISHED.html",
 b:"mind/r268/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html",
 hub:"mind/r268/MIND-ARCHIVE-UNPUBLISHED-PREVIEW.html",
 matrix:"mind/r269/ILLUSORY-TRUTH-PRODUCT-CLAIM-SOURCE-REVENUE-GATES.json",
 vtt:"mind/r257/zen12_42s_preview.vtt",
 article:"mind/r270/THE-DOORWAY-THAT-DIDNT-STEAL-YOUR-MEMORY-UNPUBLISHED.md"
};
const GATES=[
"named_inspire3_acceptance","issued_publisher_specific_earning_url","exact_zen12_offer_identity",
"current_authenticated_cart_total","refund_policy_scope_and_fulfillment",
"approved_web_promotion_channels","approved_email_promotion_channels",
"approved_creatives_or_swipe_terms","product_specific_claim_substantiation",
"affiliate_attribution_permissions","ftc_adjacent_disclosure_qa","signed_out_mobile_browser_qa",
"word_press_sanitization_qa","founder_commercial_release_approval",
"independent_settled_commission_report","verified_product_sales_and_refunds_reconciliation"
];
const CLAIM_STATUS=Object.freeze({
C01:"supported_in_1977_abstract",C02:"supported_abstract",
C03:"supported_abstract",C04:"supported_abstract",
C05:"supported_fulltext",C06:"supported_fulltext",C07:"supported_fulltext",
C08:"supported_in_task",C09:"supported_review_with_limits",
C10:"unsupported_do_not_claim",C11:"seller_statement_only",C12:"seller_statement_only",
C13:"seller_statement_unverified_fulfillment",C14:"seller_statement_only",
C15:"false_not_verified",C16:"false_not_verified",
C17:"regulator_guidance",C18:"regulator_guidance",C19:"observed_live_page",
C20:"not_verified",C21:"source_level_verified",C22:"false",C23:"unsupported_do_not_claim"
});
function check(f){
 const errors=[],bad=(ok,msg)=>{if(ok)errors.push(msg)};
 for(const key of Object.keys(NAMES))bad(typeof f[key]!=="string"||f[key].length<100,"missing "+key);
 if(errors.length)return errors;
 const choice=html=>html.slice(html.indexOf('<section id="choice">'),html.indexOf("</main>",html.indexOf('<section id="choice">')));
 bad(f.a.indexOf('<section id="choice">')<0||f.b.indexOf('<section id="choice">')<0||choice(f.a).length<4000||choice(f.a)!==choice(f.b),"buyer copy mismatch");
 const accepted=/^https:\/\/(?:finalvestige\.com|www\.ftc\.gov|www\.frontiersin\.org)(?:[\/?#]|$)/i;
 for(const [label,html] of [["A",f.a],["B",f.b],["Hub",f.hub]]){
  bad(!/<meta\b[^>]*name=["']robots["'][^>]*content=["']noindex,nofollow["']/i.test(html),label+" noindex missing");
  bad(/<\s*(?:script|form|input|iframe|video|audio|source|track|object|embed|picture|img|link|base)\b/i.test(html),label+" live resource/script/form/media");
  bad(/\bon[a-z]+\s*=|\bsrcdoc\s*=|\bautoplay\s*=|\bhttp-equiv\s*=\s*["']?refresh/i.test(html),label+" event/autoplay/refresh");
  bad(/@import\b|url\s*\(|\b(?:src|srcset|data|action|formaction|poster|background)\s*=/i.test(html),label+" hidden resource network vector");
  bad(/<\s*meta\b[^>]*http-equiv\s*=/i.test(html),label+" meta http-equiv");
  bad(/<\s*svg\b[^>]*\b(?:xmlns:xlink|href)\s*=/i.test(html),label+" unexpected svg reference");
  bad(/<\s*(?:use|image|foreignObject|feImage|animate|set)\b/i.test(html),label+" SVG external-capable node");
  const hrefs=[...html.matchAll(/\b(?:href|xlink:href)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/gi)];
  for(const h of hrefs){const u=h[1]??h[2]??h[3];bad(!/^#[A-Za-z0-9_-]+$/.test(u)&&!accepted.test(u),label+" disallowed href "+u)}
  const buttons=[...html.matchAll(/<button\b[^>]*>/gi)];
  bad(buttons.length!==1,label+" requires exactly one inert control");
  for(const match of buttons){
   const tag=match[0];
   bad(!/\bdisabled(?=[\s>])/i.test(tag)||!/\baria-disabled=["']true["']/i.test(tag)||!/\btype=["']button["']/i.test(tag),label+" enabled or submit control");
   bad(!/\bid=["']zen12-buy-button["']/i.test(tag),label+" unexpected button");
   const after=html.slice(match.index+tag.length);
   const close=after.indexOf("</button>");
   const near=after.slice(close+9,close+600);
   bad(close<0||!/^(\s|<!--.*?-->)*<p\b[^>]*\bid=["']affiliate-disclosure["']/is.test(near),label+" disclosure not directly adjacent");
   bad(!/commission/i.test(near)||!/additional cost/i.test(near),label+" disclosure not understandable");
  }
  bad(!html.includes("https://finalvestige.com/focus/"),label+" focus link absent");
  bad(!/There is no active affiliate link here now\./i.test(html),label+" commercial inactivity warning missing");
 }
 bad(/id=["']optional-film["']/.test(f.a),"control polluted");
 bad(!/id=["']optional-film["']/.test(f.b),"treatment missing");
 bad(/<\s*(?:video|source|audio|track)\b/i.test(f.b),"video falsely hosted");
 const cue=[...f.vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d+ --> (\d\d):(\d\d):(\d\d)\.\d+\n([^\n]+)/g)]
  .map(m=>({s:Number(m[1])*3600+Number(m[2])*60+Number(m[3]),e:Number(m[4])*3600+Number(m[5])*60+Number(m[6]),t:m[7].trim()}));
 const parts=[...f.b.matchAll(/<p data-time="(\d+)-(\d+)">([^<]+)<\/p>/g)]
  .map(m=>({s:Number(m[1]),e:Number(m[2]),t:m[3].split(" · ").slice(1).join(" · ").trim()}));
 bad(cue.length!==7||parts.length!==7,"wrong VTT cue count");
 if(cue.length===7&&parts.length===7)cue.forEach((p,i)=>bad(p.s!==i*6||p.e!==(i+1)*6||p.s!==parts[i].s||p.e!==parts[i].e||p.t!==parts[i].t,"cue mismatch "+i));
 bad(f.article.trim().split(/\s+/).length<2300,"article under 2300 words");
 for(const needle of ["2006","2011","2021","false alarms","working-memory","not a controlled comparison","Puységur","https://finalvestige.com/focus/"]){
  bad(!f.article.includes(needle),"missing editorial detail "+needle);
 }
 bad(/Zen12 (?:is proven|cures|treats|reprograms)/i.test(f.article),"product claim leakage into investigation");
 let m;try{m=JSON.parse(f.matrix)}catch{return errors.concat("invalid matrix JSON")}
 bad(m.decision!=="HARD_HOLD","hold lifted");
 bad(m.sources?.length!==20||new Set(m.sources.map(s=>s.id)).size!==20,"source inventory");
 bad(m.claims?.length!==23||new Set(m.claims.map(s=>s.id)).size!==23,"claim inventory");
 for(const [id,status] of Object.entries(CLAIM_STATUS)){bad(m.claims.find(c=>c.id===id)?.status!==status,"claim status changed "+id)}
 for(const c of m.claims??[])bad(!c.limit||!Array.isArray(c.source_ids)||!c.source_ids.length||c.source_ids.some(id=>!m.sources.some(s=>s.id===id)),"provenance "+c.id);
 bad(m.commercial_gates?.length!==16||GATES.some(g=>!m.commercial_gates.some(x=>x.id===g))||new Set(m.commercial_gates.map(x=>x.id)).size!==16,"gate set changed");
 for(const g of m.commercial_gates??[])bad(g.status!=="HARD_HOLD"||g.evidence!=="NOT_VERIFIED"||g.release_blocker!==true,"gate released "+g.id);
 for(const key of ["affiliate_approval","issued_earning_url","permitted_channels","approved_creatives","verified_checkout_total","commission_rate_for_fv"])bad(m.offer?.[key]!==null,"invented offer field "+key);
 for(const key of ["refund_fulfillment_verified","owned_mind_sku_verified","purchase_cta_active"])bad(m.offer?.[key]!==false,"unverified offer flag "+key);
 for(const key of ["qualified_human_sessions","affiliate_outbound","confirmed_signup","merchant_confirmed_paid_orders","partner_reported_paid_affiliate_conversions","refunds_and_fees","realized_net_revenue","net_revenue_per_1000_qualified_human_sessions"])bad(m.metric_contract?.[key]!==null,"fabricated metric "+key);
 for(const key of ["no_live_cms_edits","no_affiliate_activation","no_email_or_social_posts","no_new_forms_or_js","no_merge_or_deploy","no_spend","homepage_pr49_unchanged","canonical_mind_pr172_unchanged","owner_issue150_unchanged"])bad(m.release_controls?.[key]!==true,"boundary unset "+key);
 bad(m.media_custody?.hosted_playback!==false||m.media_custody?.real_browser_qa!==false,"media claim inflated");
 return errors;
}
const clone=f=>JSON.parse(JSON.stringify(f));
function fixtures(f){
 const out=[],add=(label,edit)=>{const copy=clone(f);edit(copy);if(JSON.stringify(copy)===JSON.stringify(f))throw Error("ineffective fixture "+label);out.push([label,copy])};
 for(const key of ["a","b","hub"]){
  add(key+" CSS request",o=>o[key]=o[key].replace("</style>","p{background:url(https://unsafe.invalid/pixel)}</style>"));
  add(key+" xlink resource",o=>o[key]=o[key].replace("</main>",'<svg><use xlink:href="https://unsafe.invalid/asset.svg#x"></use></svg></main>'));
  add(key+" extra enabled purchase",o=>o[key]=o[key].replace("</main>",'<button type="button">Buy now</button></main>'));
  add(key+" trigger form-action",o=>o[key]=o[key].replace("</main>",'<a formaction="https://unsafe.invalid/">go</a></main>'));
  add(key+" unlock purchase",o=>o[key]=o[key].replace(/<button\b[^>]*\bid=["']zen12-buy-button["'][^>]*>/i,tag=>tag.replace(/\sdisabled(?=[\s>])/i,"")));
  add(key+" replace affiliate disclosure",o=>o[key]=o[key].replace('id="affiliate-disclosure"','id="hidden-disclosure"'));
 }
 add("both variants secretly linked",o=>{o.a=o.a.replace("</main>",'<a href="https://zen12.com/secret/">BUY</a></main>');o.b=o.b.replace("</main>",'<a href="https://zen12.com/secret/">BUY</a></main>')});
 add("merchant source via CSS imported",o=>o.b=o.b.replace("</style>",'@import "https://tracking.invalid/x.css";</style>'));
 add("B transcript altered",o=>o.b=o.b.replace("Twelve minutes is an amount of time","Ten minutes guarantees improvement"));
 add("VTT shifted time",o=>o.vtt=o.vtt.replace("00:00:00.000 --> 00:00:06.000","00:00:01.000 --> 00:00:07.000"));
 add("source deleted",o=>{let m=JSON.parse(o.matrix);m.sources.pop();o.matrix=JSON.stringify(m)});
 add("fulltext downgraded silently",o=>{let m=JSON.parse(o.matrix);m.claims.find(x=>x.id==="C06").status="seller_statement_only";o.matrix=JSON.stringify(m)});
 add("seller statement promoted",o=>{let m=JSON.parse(o.matrix);m.claims.find(x=>x.id==="C12").status="supported_fulltext";o.matrix=JSON.stringify(m)});
 add("affiliate gate approval invented",o=>{let m=JSON.parse(o.matrix);m.commercial_gates[0].status="APPROVED";o.matrix=JSON.stringify(m)});
 add("commission invented",o=>{let m=JSON.parse(o.matrix);m.metric_contract.partner_reported_paid_affiliate_conversions=10;o.matrix=JSON.stringify(m)});
 add("article commercial endorsement",o=>o.article=o.article.replace("an unrelated seller's meditation","Zen12 is proven to reprogram the brain; an unrelated seller's meditation"));
 add("article emptied",o=>o.article="Summary.");
 return out;
}
module.exports={NAMES,check,fixtures};
if(require.main===module){
 const root=path.resolve(__dirname,"../.."),f={};
 for(const [k,p] of Object.entries(NAMES))f[k]=fs.readFileSync(path.join(root,p),"utf8");
 const base=check(f);if(base.length){console.error("BASE FAIL",base);process.exit(1)}
 let caught=0;const missed=[];
 for(const [label,copy] of fixtures(f)){if(check(copy).length)caught++;else missed.push(label)}
 console.log("R270 BASE PASS; distinct effective unsafe fixtures rejected "+caught+"/"+(caught+missed.length));
 if(missed.length){console.error("UNCAUGHT:",missed);process.exit(1)}
}
