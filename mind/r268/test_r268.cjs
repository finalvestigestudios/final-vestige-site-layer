"use strict";
/**
 * FV Mind R268 SOURCE ONLY integrity gate.
 * Run: node mind/r268/test_r268.cjs from repository root.
 * No network, JS DOM, analytics, CMS, checkout, browser or external dependencies.
 * Independent real-browser, WordPress and merchant acceptance remain required.
 */
const NAMES = {
 article:"mind/r268/THE-WORD-THAT-STOPPED-SOUNDING-LIKE-A-WORD-UNPUBLISHED.md",
 a:"mind/r268/ZEN12-A-TEXT-UNPUBLISHED.html",
 b:"mind/r268/ZEN12-B-OPTIONAL-FILM-UNPUBLISHED.html",
 hub:"mind/r268/MIND-ARCHIVE-UNPUBLISHED-PREVIEW.html",
 matrix:"mind/r268/CLAIM-SOURCE-PRODUCT-REVENUE-GATES.json",
 plan:"mind/r268/CONVERSION-FIRST-AB-RELEASE-AND-OWNERSHIP.md"
};
const GATES=[
"named_inspire3_acceptance","issued_publisher_specific_earning_url","exact_zen12_offer_identity",
"current_authenticated_cart_total","refund_policy_scope_and_fulfillment","approved_web_promotion_channels",
"approved_email_promotion_channels","approved_creatives_or_swipe_terms","product_specific_claim_substantiation",
"affiliate_attribution_permissions","ftc_adjacent_disclosure_qa","signed_out_mobile_browser_qa",
"word_press_sanitization_qa","founder_commercial_release_approval",
"independent_settled_commission_report","verified_product_sales_and_refunds_reconciliation"
];
const ALLOWED_HOSTS = new Set(["finalvestige.com","www.ftc.gov","www.frontiersin.org"]);
function errorIf(errors,condition,description){if(condition)errors.push(description);}
function anchorHrefs(html){
  const result=[];
  for(const match of html.matchAll(/<a\b[^>]*>/gi)){
    const t=match[0];
    const m=t.match(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i);
    result.push(m?(m[1]||m[2]||m[3]):null);
  }
  return result;
}
function inspectHtml(html,tag,errors){
  const blocks=html.match(/<button\b[^>]*>/gi)||[];
  const button=blocks.find(x=>/\bid\s*=\s*["']?zen12-buy-button\b/i.test(x));
  errorIf(errors,!button,tag+": disabled commercial control absent");
  if(button){
    errorIf(errors,!/\sdisabled(?=\s|>)/i.test(button),tag+": commercial button not truly disabled");
    errorIf(errors,!/\baria-disabled\s*=\s*["']?true\b/i.test(button),tag+": aria-disabled absent");
    const at=html.indexOf(button),end=html.indexOf("</button>",at);
    const after=html.slice(end+9,end+360);
    errorIf(errors,end<0||!/^(\s*)<p\b[^>]*\bid\s*=\s*["']affiliate-disclosure["']/i.test(after),tag+": disclosure not immediately after disabled control");
  }
  errorIf(errors,!(html.includes("There is no active affiliate link here now.") || html.includes("There is no active affiliate link here now.")),tag+": no clear inactive-link statement");
  errorIf(errors,!/commission/i.test(html)||!/additional cost/i.test(html),tag+": commission disclosure inadequate");
  errorIf(errors,!html.includes("https://finalvestige.com/focus/"),tag+": Focus route absent");
  errorIf(errors,!/<meta[^>]*name=["']robots["'][^>]*noindex,nofollow/i.test(html),tag+": unpublished index hold missing");
  errorIf(errors,/<\s*(?:script|form|input|iframe|video|audio|source|track|canvas|object|embed)\b/i.test(html),tag+": active JS/form/media/dependency prohibited");
  errorIf(errors,/<\s*(?:meta[^>]+http-equiv\s*=\s*["']?refresh)\b/i.test(html),tag+": redirect prohibited");
  errorIf(errors,/\b(?:autoplay|onload|onclick|onerror|onmouseover|srcdoc)\s*=/i.test(html),tag+": active/auto media or inline handler");
  errorIf(errors,/\b(?:data-?price|commission-rate|payout|conversion-count|verified-sale)\s*=/i.test(html),tag+": unsourced monetary attribution metadata");
  for(const href of anchorHrefs(html)){
    if(!href){errors.push(tag+": anchor has no href");continue;} if(/^#[a-z0-9_-]+$/i.test(href))continue;
    const parsed=/^https:\/\/([^/#?]+)(?:[/?#]|$)/i.exec(href);
    if(!parsed || !ALLOWED_HOSTS.has(parsed[1].toLowerCase()))errors.push(tag+": unacceptable link "+href);
  }
  errorIf(errors,/<\s*a\b[^>]*\bhref\s*=\s*(?:"|'|)\s*(?:https?:\/\/)?(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(html),tag+": merchant link is unauthorized");
  errorIf(errors,/(?:guaranteed? (?:health|wealth|healing|memory|brain|results)|clinically proven Zen12|millionaire overnight)/i.test(html),tag+": unsubstantiated direct promise");
  errorIf(errors,/<img\b[^>]*\bsrc\s*=\s*(?:"https?:|'https?:|https?:)/i.test(html)||/<link\b[^>]*\bhref\s*=\s*(?:"https?:|'https?:|https?:)/i.test(html)||/@import\b/i.test(html),tag+": remote resource");
}
function getBuyer(html){
  const start=html.indexOf('<section id="choice">'),end=html.indexOf("</main>",start);
  return start<0||end<0?"":html.slice(start,end).trim();
}
function check(files){
 const errors=[];
 for(const key of Object.keys(NAMES))errorIf(errors,typeof files[key]!=="string"||files[key].length<100,key+": missing/empty source");
 if(errors.length)return errors;
 const {article,a,b,hub,plan,matrix}=files;
 inspectHtml(a,"A",errors);inspectHtml(b,"B",errors);inspectHtml(hub,"Hub",errors);
 errorIf(errors,getBuyer(a).length<5500,"A: buyer information insufficient");
 errorIf(errors,getBuyer(a)!==getBuyer(b),"A/B: unequal buyer text or links");
 errorIf(errors,/id="optional-film"/.test(a),"A: optional film leaked into control");
 errorIf(errors,!/id="optional-film"/.test(b),"B: optional poster/transcript absent");
 errorIf(errors,/<\s*(?:video|audio|script)\b/i.test(b),"B: active media or scripts");
 errorIf(errors,!/NOT HOSTED|not hosted/i.test(b),"B: missing non-hosted film caveat");
 const times=[...b.matchAll(/\bdata-time="(\d+)-(\d+)"/g)].map(m=>[+m[1],+m[2]]);
 errorIf(errors,times.length!==7,"B: captions not exactly seven intervals");
 for(let i=0;i<times.length;i++)if(times[i][0]!==i*6||times[i][1]!==i*6+6)errors.push("B: invalid sequential 42-second caption interval");
 errorIf(errors,!b.includes("complete seven-part, 42-second transcript"),"B: accessible transcript summary missing");
 errorIf(errors,!b.includes('aria-label="Original dark archival poster'),"B: source poster alt labeling missing");
 errorIf(errors,!hub.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"),"Hub: historical archive missing");
 errorIf(errors,!hub.includes("https://finalvestige.com/2026/11/02/change-blindness/"),"Hub: verified live investigation missing");
 errorIf(errors,!hub.includes('class="skip"'),"Hub: skip link missing");
 errorIf(errors,!hub.includes("prefers-reduced-motion"),"Hub: reduced motion style missing");
 errorIf(errors,!/not a live WordPress page/i.test(hub),"Hub: unpublished identity disclosure missing");
 const wordCount=article.trim().split(/\s+/).length;
 errorIf(errors,wordCount<1900,"Article: too thin");
 for(const s of ["14450948","14450946","10.3389/fpsyg.2017.02117","35287550","9564746","Puységur","artillery officer","No commercial CTA","UNPUBLISHED","Zen12"]){
   errorIf(errors,!article.toLowerCase().includes(s.toLowerCase()),"Article missing anchor: "+s);
 }
 errorIf(errors,!article.includes("not a validated test"),"Article: informal demonstration limit missing");
 errorIf(errors,/(?:I tried Zen12|we tried Zen12|our product improved)/i.test(article),"Article: fabricated review experience");
 let obj;try{obj=JSON.parse(matrix)}catch(e){return errors.concat("Matrix invalid JSON");}
 errorIf(errors,!Array.isArray(obj.sources)||obj.sources.length<18,"Matrix: documented research and vendor sources insufficient");
 errorIf(errors,!Array.isArray(obj.claims)||obj.claims.length<24,"Matrix: claim coverage insufficient");
 const ids=obj.claims.map(x=>x.id);
 errorIf(errors,new Set(ids).size!==obj.claims.length,"Matrix: duplicate claim identities");
 for(const id of ["C08","C09","C10","C11","C13","C14","C15","C19","C20","C21","C22","C24","C25"]){
   errorIf(errors,!ids.includes(id),"Matrix: missing claim "+id);
 }
 for(const c of obj.claims){
   errorIf(errors,!c.status||!Array.isArray(c.source_ids)||!c.limit,"Matrix: unclassified claim "+c.id);
   if(["C09","C12","C14","C15","C22","C24","C25","C26"].includes(c.id))
     errorIf(errors,!/UNSUBSTANTIATED|UNSUPPORTED|NOT_VERIFIED|FALSE/i.test(c.status),"Matrix: unsafe positive status "+c.id);
 }
 const gs=obj.commercial_gates??[],actual=gs.map(x=>x.id);
 errorIf(errors,gs.length!==16||actual.length!==new Set(actual).size||GATES.some(x=>!actual.includes(x)),"Matrix: exact 16 authorization gates not present");
 for(const g of gs)errorIf(errors,g.status!=="HARD_HOLD"||g.evidence!=="NOT_VERIFIED"||g.release_blocker!==true,"Matrix: commercial gate cleared "+g.id);
 const p=obj.product??{};
 for(const k of ["affiliate_destination","price_at_checkout","commission_rate_for_FV","merchant_sales","settled_affiliate_commissions"]){
   errorIf(errors,p[k]!==null,"Matrix: invented verified commercial field "+k);
 }
 for(const k of ["purchase_cta_active","refund_fulfillment_verified","channel_authorization_verified","owned_paid_mind_sku_validated"]){
   errorIf(errors,p[k]!==false,"Matrix: commercial release not held "+k);
 }
 const m=obj.measurement??{};
 for(const k of ["qualified_human_sessions","cta_clicks","confirmed_subscribers","merchant_confirmed_orders","affiliate_partner_confirmed_paid_conversions","realized_net_revenue","net_revenue_per_1000_qualified_sessions"]){
  errorIf(errors,m[k]!==null,"Matrix: invented metric "+k);
 }
 for(const k of ["no_live_wp_cms_writes","no_menu_changes","no_jetpack_changes","no_emails_sent","no_social_publishing","no_affiliate_activation","no_analytics_script_added","no_merge_or_deploy","no_spend"]){
  errorIf(errors,obj.release_boundaries?.[k]!==true,"Matrix: release boundary changed "+k);
 }
 for(const token of ["HARD HOLD","NO MATCH","affiliate_outbound","merchant_confirmed_purchase","confirmed_signup","revenue_per_1000_qualified_human_sessions","360/390/768/1440/1920","#172","TASK-008","no-JS","refunds","not a usable merchant link"]){
   errorIf(errors,!plan.toLowerCase().includes(token.toLowerCase()),"Plan: missing contract "+token);
 }
 return errors;
}
function deepCopy(o){return JSON.parse(JSON.stringify(o))}
function mutations(files){
 const out=[];
 function add(label,change){const f=deepCopy(files);change(f);if(Object.keys(files).every(k=>files[k]===f[k]))throw new Error("Ineffective mutation fixture: "+label);out.push([label,f]);}
 add("A enables buy",f=>f.a=f.a.replace("type=\"button\" disabled","type=\"button\""));
 add("B enables buy",f=>f.b=f.b.replace("type=\"button\" disabled","type=\"button\""));
 add("hub enables buy",f=>f.hub=f.hub.replace("id=\"zen12-buy-button\" disabled","id=\"zen12-buy-button\""));
 add("A removes disclosure",f=>f.a=f.a.replace('id="affiliate-disclosure"','id="missing-disclosure"'));
 add("B separates disclosure from button",f=>f.b=f.b.replace("</button>","</button><aside>Extra unrelated content</aside>"));
 add("hub removes disclosure",f=>f.hub=f.hub.replace('id="affiliate-disclosure"','id="missing-disclosure"'));
 add("A adds quoted merchant link",f=>f.a=f.a.replace("</main>",'<a href="https://zen12.com/secret/">Buy now</a></main>'));
 add("B adds unquoted merchant link",f=>f.b=f.b.replace("</main>",'<a href=https://zen12.com/hnp>Buy now</a></main>'));
 add("hub adds javascript URI",f=>f.hub=f.hub.replace("</main>",'<a href=javascript:alert(1)>go</a></main>'));
 add("A script injected",f=>f.a=f.a.replace("</main>","<script>window.analytics=1</script></main>"));
 add("B adds secondary email form",f=>f.b=f.b.replace("</main>",'<form><input type=email></form></main>'));
 add("hub adds remote tracking image",f=>f.hub=f.hub.replace("</main>",'<img src="https://tracker.example/pixel"></main>'));
 add("B autoplay video",f=>f.b=f.b.replace("</main>",'<video autoplay src="sample.mp4"></video></main>'));
 add("A iframe checkout",f=>f.a=f.a.replace("</main>",'<iframe src="https://zen12.com"></iframe></main>'));
 add("A removes Focus path",f=>f.a=f.a.replace(/https:\/\/finalvestige\.com\/focus\//g,"https://example.com/removed"));
 add("B drops film poster",f=>f.b=f.b.replace('id="optional-film"','id="deleted-film"'));
 add("B loses transcript",f=>f.b=f.b.replace('complete seven-part, 42-second transcript','No transcript provided'));
 add("B changes caption start",f=>f.b=f.b.replace('data-time="12-18"','data-time="13-18"'));
 add("B changes caption end",f=>f.b=f.b.replace('data-time="36-42"','data-time="36-43"'));
 add("B rewrites buyer copy",f=>f.b=f.b.replace("Zen12 Premium as described by its seller","Zen12 Premium as guaranteed by its seller"));
 add("A adds guaranteed clinical claim",f=>f.a=f.a.replace("</main>","<p>guaranteed healing</p></main>"));
 add("article removes early primary",f=>f.article=f.article.replace(/14450948/g,"MISSING"));
 add("article changes history",f=>f.article=f.article.replace("artillery officer","physician"));
 add("article fabricates personal use",f=>f.article=f.article.replace("Final Vestige has developed","We tried Zen12. Final Vestige has developed"));
 add("matrix commercial approval turned on",f=>{let x=JSON.parse(f.matrix);x.commercial_gates[0].status="CLEARED";f.matrix=JSON.stringify(x)});
 add("matrix missing exact gate",f=>{let x=JSON.parse(f.matrix);x.commercial_gates[4].id="something_else";f.matrix=JSON.stringify(x)});
 add("matrix invents revenue",f=>{let x=JSON.parse(f.matrix);x.measurement.realized_net_revenue=128.50;f.matrix=JSON.stringify(x)});
 add("matrix invents checkout price",f=>{let x=JSON.parse(f.matrix);x.product.price_at_checkout=37;f.matrix=JSON.stringify(x)});
 add("matrix invents affiliate URL",f=>{let x=JSON.parse(f.matrix);x.product.affiliate_destination="https://unapproved.example/earn";f.matrix=JSON.stringify(x)});
 add("matrix marks unsupported clinical claim supported",f=>{let x=JSON.parse(f.matrix);x.claims.find(c=>c.id==="C09").status="SUPPORTED";f.matrix=JSON.stringify(x)});
 add("matrix invents sold Mind product",f=>{let x=JSON.parse(f.matrix);x.product.owned_paid_mind_sku_validated=true;f.matrix=JSON.stringify(x)});
 add("matrix relaxes no-commerce release",f=>{let x=JSON.parse(f.matrix);x.release_boundaries.no_affiliate_activation=false;f.matrix=JSON.stringify(x)});
 add("matrix claims settled sale",f=>{let x=JSON.parse(f.matrix);x.product.settled_affiliate_commissions=5;f.matrix=JSON.stringify(x)});
 add("plan removes no-match",f=>f.plan=f.plan.replace("NO MATCH","UNVERIFIED"));
 add("plan erases settlement separation",f=>f.plan=f.plan.replace(/affiliate_outbound/g,"affiliate_sale"));
 return out;
}
function runSuite(files){
 const baseline=check(files);
 if(baseline.length)return {pass:false,baseline,mutations:[]};
 const cases=mutations(files),failures=[],labels=[];
 for(const [label,variant] of cases){const failuresFound=check(variant);if(!failuresFound.length)failures.push(label);else labels.push({label,rejected_by:failuresFound[0]});}
 return {pass:failures.length===0,baseline:[],tested:cases.length,rejected:labels.length,escaped:failures,examples:labels.slice(0,5)};
}
module.exports={NAMES,GATES,check,runSuite};
if(typeof require==="function"&&require.main===module){
 const fs=require("fs");
 const files=Object.fromEntries(Object.entries(NAMES).map(([k,p])=>[k,fs.readFileSync(p,"utf8")]));
 const result=runSuite(files);console.log(JSON.stringify(result,null,2));
 if(!result.pass)process.exitCode=1;
}