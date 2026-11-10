"use strict";
/**
 * FV Mind R269 source-only integrity regression (no network, browser, CMS or merchant calls).
 * Run from repository root: node mind/r269/test_r269.cjs
 * Exports check / fixtures for isolated V8 re-execution against retrieved GitHub files.
 * This is NOT an automated browser, WordPress sanitizer or checkout acceptance test.
 */
const fs=require("node:fs"),path=require("node:path");
const NAMES={
  article:"mind/r269/THE-SENTENCE-THAT-BECAME-TRUE-BECAUSE-YOU-SAW-IT-AGAIN-UNPUBLISHED.md",
  matrix:"mind/r269/ILLUSORY-TRUTH-PRODUCT-CLAIM-SOURCE-REVENUE-GATES.json",
  plan:"mind/r269/ONE-OFFER-FOCUS-CONVERSION-REVENUE-AND-MEDIA-ACCEPTANCE.md",
  a:"mind/r268/ZEN12-A-TEXT-UNPUBLISHED.html",
  b:"mind/r268/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html",
  vtt:"mind/r257/zen12_42s_preview.vtt",
  hub:"mind/r268/MIND-ARCHIVE-UNPUBLISHED-PREVIEW.html"
};
const GATES=[
"named_inspire3_acceptance","issued_publisher_specific_earning_url","exact_zen12_offer_identity",
"current_authenticated_cart_total","refund_policy_scope_and_fulfillment","approved_web_promotion_channels",
"approved_email_promotion_channels","approved_creatives_or_swipe_terms","product_specific_claim_substantiation",
"affiliate_attribution_permissions","ftc_adjacent_disclosure_qa","signed_out_mobile_browser_qa",
"word_press_sanitization_qa","founder_commercial_release_approval",
"independent_settled_commission_report","verified_product_sales_and_refunds_reconciliation"
];
const BAD_CLAIMS=["C10","C15","C16","C20","C22","C23"];
function check(f){
 const errors=[];const bad=(yes,msg)=>{if(yes)errors.push(msg)};
 for(const k of Object.keys(NAMES))bad(typeof f[k]!=="string"||f[k].length<50,"missing source "+k);
 if(errors.length)return errors;
 const a=f.a,b=f.b,hub=f.hub,article=f.article,plan=f.plan;
 const A=a.slice(a.indexOf('<section id="choice">'),a.indexOf("</main>",a.indexOf('<section id="choice">')));
 const B=b.slice(b.indexOf('<section id="choice">'),b.indexOf("</main>",b.indexOf('<section id="choice">')));
 bad(A.length<4500||A!==B,"A/B purchase copy differs");
 function htmlCheck(html,label){
  const tags=[...html.matchAll(/<([a-z][\w:-]*)\b([^<>]*?)>/gi)];
  bad(/<\s*(script|form|input|iframe|video|audio|source|track|object|embed)\b/i.test(html),label+" active media/form/script");
  bad(/\bon[a-z]+\s*=|\bautoplay\s*=|\bsrcdoc\s*=|\bhttp-equiv\s*=\s*["']?refresh/i.test(html),label+" event handler/redirect/auto media");
  bad(/\bsrcset\s*=|@import\b|<\s*link\b|<\s*img\b/i.test(html),label+" remote or unresolved image/resource");
  bad(!/<meta\b[^>]*name=["']robots["'][^>]*noindex,nofollow/i.test(html),label+" noindex absent");
  for(const m of tags){if(m[1].toLowerCase()!=="a")continue;
    const href=m[2].match(/(?:^|\s)href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i);
    const u=href&&(href[1]??href[2]??href[3]);
    bad(!u,label+" href missing");
    if(u&&!/^#[A-Za-z0-9_-]+$/.test(u)&&!/^https:\/\/(finalvestige\.com|www\.ftc\.gov|www\.frontiersin\.org)(?:[/?#]|$)/i.test(u))
      errors.push(label+" disallowed href: "+u);
  }
  const buttons=[...html.matchAll(/<button\b[^>]*\bid=["']?zen12-buy-button\b[^>]*>/gi)];
  bad(buttons.length!==1,label+" missing/multiple purchase buttons");
  if(buttons.length===1){
    const tag=buttons[0][0];
    bad(!/\sdisabled(?=[\s>])/i.test(tag)||!/\baria-disabled=["']true["']/i.test(tag),label+" enabled/aria-invalid purchase");
    const aft=html.slice(buttons[0].index+tag.length);
    const end=aft.indexOf("</button>");
    bad(end<0||!/^\s*<p\b[^>]*\bid=["']affiliate-disclosure["']/i.test(aft.slice(end+9)),label+" disclosure not immediately after CTA");
    bad(!/commission/i.test(aft.slice(end,end+430))||!/additional cost/i.test(aft.slice(end,end+430)),label+" clear commission words absent adjacent");
  }
  bad(!html.includes("https://finalvestige.com/focus/"),label+" Focus route missing");
  bad(!/There is no active affiliate link here now\./i.test(html),label+" affiliate inactivity not explicit");
  bad(/guaranteed (?:health|wealth|mental|memory)|clinically proven Zen12|we personally tested Zen12/i.test(html),label+" fabricated efficacy");
 }
 htmlCheck(a,"A");htmlCheck(b,"B");htmlCheck(hub,"Hub");
 bad(/id=["']optional-film["']/i.test(a),"control has film");
 bad(!/id=["']optional-film["']/i.test(b),"treatment lacks film");
 bad(!/not hosted/i.test(b),"B lacks media custody warning");
 bad(!/source-controlled R257 WebVTT text/.test(b),"B does not identify source VTT");
 const cue=[...f.vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.\d+ --> (\d\d):(\d\d):(\d\d)\.\d+\n([^\n]+)/g)]
 .map(m=>({s:Number(m[1])*3600+Number(m[2])*60+Number(m[3]),e:Number(m[4])*3600+Number(m[5])*60+Number(m[6]),t:m[7]}));
 const parts=[...b.matchAll(/<p data-time="(\d+)-(\d+)">([^<]+)<\/p>/g)].map(m=>({s:Number(m[1]),e:Number(m[2]),t:m[3].split(" · ").slice(1).join(" · ")}));
 bad(cue.length!==7||parts.length!==7,"not seven full film cues");
 if(cue.length===7&&parts.length===7)for(let i=0;i<7;i++)bad(cue[i].s!==i*6||cue[i].e!==(i+1)*6||cue[i].s!==parts[i].s||cue[i].e!==parts[i].e||cue[i].t!==parts[i].t,"cue mismatch "+i);
 bad(article.split(/\s+/).length<2300,"editorial article below 2300 words");
 for(const item of ["31,184","182 studies","366 effect sizes","0.37","0.30 to 0.44","27 February 2026","Puységur","not a validated psychological test","UNPUBLISHED"]){
  if(item!=="not a validated psychological test")bad(!article.includes(item),"article missing: "+item);
 }
 bad(/I personally tried Zen12|our experience using Zen12|Zen12 clinically proven/i.test(article),"false personal or product result");
 bad(!article.includes("not a validated psychological test")&&!article.includes("not a validated psychological"),"informal exercise missing limitation");
 let m;try{m=JSON.parse(f.matrix)}catch(e){return errors.concat("matrix malformed JSON")}
 bad(m.decision!=="HARD_HOLD","commercial hold removed");
 bad(m.sources?.length!==20||new Set(m.sources.map(s=>s.id)).size!==20,"matrix source identities");
 bad(m.claims?.length!==23||new Set(m.claims.map(s=>s.id)).size!==23,"matrix claim count/identities");
 const status=Object.fromEntries(m.claims.map(x=>[x.id,x.status]));
 for(const id of BAD_CLAIMS)bad(!/unsupported|false|not_verified/i.test(status[id]||""),"disallowed positive claim: "+id);
 for(const c of m.claims)bad(!c.limit||!c.source_ids?.length||c.source_ids.some(id=>!m.sources.some(s=>s.id===id)),"claim provenance missing: "+c.id);
 bad(m.commercial_gates?.length!==16||new Set(m.commercial_gates.map(g=>g.id)).size!==16||GATES.some(id=>!m.commercial_gates.some(g=>g.id===id)),"exact 16 gates missing");
 for(const g of m.commercial_gates||[])bad(g.status!=="HARD_HOLD"||g.evidence!=="NOT_VERIFIED"||g.release_blocker!==true,"gate improperly cleared: "+g.id);
 for(const field of ["affiliate_approval","issued_earning_url","permitted_channels","approved_creatives","verified_checkout_total","commission_rate_for_fv"])
  bad(m.offer?.[field]!==null,"invented commercial value "+field);
 for(const field of ["refund_fulfillment_verified","owned_mind_sku_verified","purchase_cta_active"])
  bad(m.offer?.[field]!==false,"release flag should be false "+field);
 for(const field of ["qualified_human_sessions","affiliate_outbound","confirmed_signup","merchant_confirmed_paid_orders","partner_reported_paid_affiliate_conversions","refunds_and_fees","realized_net_revenue","net_revenue_per_1000_qualified_human_sessions"])
  bad(m.metric_contract?.[field]!==null,"invented metric "+field);
 for(const field of ["no_live_cms_edits","no_affiliate_activation","no_email_or_social_posts","no_new_forms_or_js","no_merge_or_deploy","no_spend","homepage_pr49_unchanged","canonical_mind_pr172_unchanged","owner_issue150_unchanged"])
  bad(m.release_controls?.[field]!==true,"boundary removed "+field);
 bad(m.media_custody?.rendered_r257_vtt_blob!=="e4e0a67ecac610d1c56fa904d52347a19f766469"||m.media_custody?.hosted_playback!==false||m.media_custody?.real_browser_qa!==false,"media custody misrepresentation");
 for(const t of ["#172","Issue #820","HARD HOLD","NO MATCH","affiliate_outbound","confirmed_signup","merchant_confirmed_purchase","7/30","no-JS","360/390/768/1440/1920","refunds","R257 WebVTT","not a WordPress CMS draft"])
  bad(!plan.toLowerCase().includes(t.toLowerCase()),"acceptance plan missing "+t);
 return errors;
}
const clone=f=>JSON.parse(JSON.stringify(f));
function fixtures(f){
 const tests=[];function add(name,fn){const o=clone(f);fn(o);if(Object.keys(f).every(k=>f[k]===o[k]))throw Error("ineffective fixture "+name);tests.push([name,o])}
 for(const [k,rx,to] of [
  
  ["a",'id="affiliate-disclosure"','id="different"'],["b",'id="affiliate-disclosure"','id="different"'],["hub",'id="affiliate-disclosure"','id="different"'],
  ["a",'https://finalvestige.com/focus/','https://example.org/a'],["b",'https://finalvestige.com/focus/','https://example.org/b'],
  ["b",'source-controlled R257 WebVTT text','some other screenplay']
 ])add("replace "+k+" "+rx,o=>o[k]=o[k].replace(rx,to));
 for(const key of ["a","b","hub"])add("Enable "+key+" exact CTA",o=>o[key]=o[key].replace(/<button\b[^>]*\bid=["']zen12-buy-button["'][^>]*>/i,tag=>tag.replace(/\sdisabled(?=\s|>)/i,"")));
 for(const [name,element] of [
 ["script","<script>alert(1)</script>"],["form","<form><input></form>"],["merchant","<a href=https://zen12.com/secret/>Go</a>"],
 ["jsURL",'<a href="javascript:alert(1)">Go</a>'],["handler",'<div onclick="alert(1)">test</div>'],
 ["autoplay",'<video autoplay src="a.mp4"></video>'],["pixel",'<img src="https://tracking.invalid/p.gif">'],
 ["srcset",'<picture srcset="https://pixel.invalid/a"></picture>'],["metaRefresh",'<meta http-equiv="refresh" content="0;url=https://evil.test">']
 ])add("B inject "+name,o=>o.b=o.b.replace("</main>",element+"</main>"));
 add("VTT cue altered",o=>o.vtt=o.vtt.replace("Twelve minutes is an amount of time","Ten minutes is an amount of time"));
 add("B cue altered",o=>o.b=o.b.replace("A listener may feel calmer.","A listener will certainly feel calmer."));
 add("B cue removed",o=>o.b=o.b.replace(/<p data-time="0-6">[^<]+<\/p>/,""));
 add("A/B buyer mismatch",o=>o.b=o.b.replace("The free comparison","The expensive comparison"));
 add("Article sample damaged",o=>o.article=o.article.slice(0,500));
 add("Article 2026 number changed",o=>o.article=o.article.replace("31,184","31,185"));
 add("Plan no-JS removed",o=>o.plan=o.plan.replace(/no-JS/g,"JavaScript only"));
 add("Matrix source deleted",o=>{let x=JSON.parse(o.matrix);x.sources.pop();o.matrix=JSON.stringify(x)});
 add("Matrix unsupported claim approved",o=>{let x=JSON.parse(o.matrix);x.claims.find(c=>c.id==="C10").status="proven";o.matrix=JSON.stringify(x)});
 add("Matrix gate deleted",o=>{let x=JSON.parse(o.matrix);x.commercial_gates.pop();o.matrix=JSON.stringify(x)});
 add("Matrix gate invented release",o=>{let x=JSON.parse(o.matrix);x.commercial_gates[0].status="APPROVED";o.matrix=JSON.stringify(x)});
 add("Matrix unknown offer URL invented",o=>{let x=JSON.parse(o.matrix);x.offer.issued_earning_url="https://placeholder.invalid";o.matrix=JSON.stringify(x)});
 add("Matrix fabricated merchant order",o=>{let x=JSON.parse(o.matrix);x.metric_contract.merchant_confirmed_paid_orders=1;o.matrix=JSON.stringify(x)});
 add("Matrix release controls lifted",o=>{let x=JSON.parse(o.matrix);x.release_controls.no_affiliate_activation=false;o.matrix=JSON.stringify(x)});
 return tests;
}
module.exports={NAMES,check,fixtures};
if(require.main===module){
 const root=path.resolve(__dirname,"../.."),f={};
 for(const [k,p] of Object.entries(NAMES))f[k]=fs.readFileSync(path.join(root,p),"utf8");
 const errors=check(f);if(errors.length){console.error("R269 BASE FAIL:",errors);process.exit(1)}
 const tests=fixtures(f);
 let caught=0;for(const [label,o] of tests){const issues=check(o);if(issues.length)caught++;else console.error("UNCAUGHT",label)}
 console.log("R269 baseline PASS; effective negative tests rejected",caught,"/",tests.length);
 if(caught!==tests.length)process.exit(1);
}
