"use strict";
/* Reproducible with Node from repo root:
 * node mind/r121/verify-r121.cjs
 * Offline tests only. No web, WP, purchase, analytics or cookies.
 */
function audit({article,decision,html,registry,contract}) {
  const results=[];
  const test=(name,passed)=>{results.push({name,pass:Boolean(passed)});};
  const refs=new Set(registry.source_registry.map(s=>s.id));
  test("original editorial draft has no affiliate link",!/<a\s+[^>]*href=["'][^"']*(?:inspire3|zen12|brainwaveshots|hypnosislive)/i.test(article));
  test("research history source Hasher 1977",article.includes("10.1016/S0022-5371(77)80012-1"));
  test("review 51 studies",article.includes("51 studies")&&article.includes("1088868309352251"));
  test("Fazio known-falsehood result cited",article.includes("26301795")&&article.includes("Knowledge continued to matter"));
  test("Pennycook 2018 result cited",article.includes("PMC6279465"));
  test("Brashier mitigation qualified",article.includes("31473395")&&article.includes("under specific conditions"));
  test("historical bridge not product endorsement",article.includes("retroactively validate")&&article.includes("animal magnetism"));
  test("science vs purchasing results separated",article.includes("did not measure actual purchases"));
  test("free exercise is explicitly unvalidated",article.includes("not a validated psychological intervention"));
  test("independent study sources count >=5",registry.source_registry.filter(x=>x.kind.includes("experiment")||x.kind==="meta_analysis").length>=5);
  test("all source IDs unique",refs.size===registry.source_registry.length);
  test("all claims cite existing sources",registry.claim_decisions.every(x=>x.support.length&&x.support.every(id=>refs.has(id))));
  test("merchant price representations treated conditionally",registry.claim_decisions.find(x=>x.id==="Z4").classification==="REJECT_PRICE_VARIABILITY"&&decision.includes("different page-specific promotions"));
  test("unsubstantiated health/wealth rejected",registry.claim_decisions.find(x=>x.id==="Z3").classification==="DO_NOT_ASSERT_UNSUBSTANTIATED");
  test("hour equivalence rejected",registry.claim_decisions.find(x=>x.id==="Z2").classification==="DO_NOT_ASSERT_UNSUBSTANTIATED");
  test("named acceptance unverified",registry.claim_decisions.find(x=>x.id==="Z7").classification==="UNVERIFIED_NO_PUBLISH");
  test("no released merchant permission",Object.values(registry.approvals).every(v=>v===false));
  test("null commission and sale proof",registry.revenue.status==="NOT_COMPUTABLE"&&registry.revenue.net_revenue_per_1000===null);
  test("no fabricated Grok asset IDs",registry.creator_topic_fit.every(x=>x.asset_id===null&&x.platform_url===null));
  test("never send traffic to unpublished attentional blink",registry.creator_topic_fit.find(x=>x.id==="attentional-blink").live_article===null);
  const linkHrefs=[...html.matchAll(/<a\b[^>]*href="([^"]+)"/gi)].map(m=>m[1]);
  test("only existing first-party Focus link",linkHrefs.length===1&&linkHrefs[0]==="https://finalvestige.com/focus/");
  test("no seller URL clickable, including ordinary offer",!/<a\b[^>]*href="https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i.test(html));
  test("disabled purchase button",/<button\b[^>]*\sdisabled(?:\s|>)[^>]*>Merchant review pending/.test(html));
  test("prospective commission adjacent to disabled button",/Prospective affiliate disclosure:[\s\S]{1,300}Final Vestige may earn a commission[\s\S]{1,250}<button\b[^>]*\sdisabled(?:\s|>)/.test(html));
  test("clear source/claim separation",html.includes("not evidence")&&html.includes("What remains unproved"));
  test("no duplicate email/signup form",!/<form\b/i.test(html)&&!/<input\b/i.test(html));
  test("no added analytics tracking script",!/<script\b|<iframe\b|<link\b[^>]*https?:/i.test(html));
  test("no autoplay tags",!/<(?:audio|video)[^>]*\bautoplay\b/i.test(html));
  test("no nested main landmark",!/<main\b/i.test(html));
  test("heading and transcript accessible",/<section\b[^>]*aria-labelledby="fv-r121-title"/.test(html)&&html.includes("<details>")&&html.includes("<summary>"));
  test("40-second transcript complete",["0–7 s","7–14 s","14–21 s","21–28 s","28–35 s","35–40 s"].every(t=>html.includes(t)));
  test("storyboard not presented as real MP4",html.includes("No MP4, embedded player")&&html.includes("Caption windows are an editorial specification"));
  test("motion reduced accessibility",html.includes("prefers-reduced-motion:reduce"));
  test("mobile narrow breakpoint",html.includes("@media(max-width:700px)"));
  test("no unapproved CMS changes described",decision.includes("no WordPress publish")&&decision.includes("no Dispatch or Focus modifications"));
  test("report missing Payhip proof",decision.includes("seller's own authenticated inventory"));
  test("one primary merchant candidate",decision.includes("Zen12 Premium")&&decision.includes("HOLD_ALL_MERCHANT_CTA"));
  test("no medical guarantee",html.includes("not proof")&&html.includes("medical results"));
  const none=contract.calculateRevenue({window_days:7,source_kind:"affiliate",qualified_human_sessions:null});
  test("unknown attribution refuses revenue math",none.status==="NOT_COMPUTABLE");
  const clickOnly=contract.calculateRevenue({window_days:30,source_kind:"affiliate",affiliate_clicks:100});
  test("outbound click count cannot become sales",clickOnly.status==="INVALID");
  test("PII email field rejected",contract.validateAggregate({email:"nobody@example.com"}).length>0);
  test("customer ID rejected",contract.validateAggregate({customer_id:"C1"}).length>0);
  test("IP address rejected",contract.validateAggregate({ip_address:"127.0.0.1"}).length>0);
  test("random event/source fields rejected",contract.validateAggregate({event_type:"merchant_paid_order"}).length>0);
  test("asset ID validation blocks embedded URL",contract.validateAggregate({asset_id:"x?email=a@b.com"}).length>0);
  const sample={
    cohort:"2026-11-04",window_days:7,source_kind:"affiliate",qualified_human_sessions:200,
    confirmed_paid_orders:6,settled_income_cents:10000,refunds_reversals_cents:500,fees_cents:100,
    merchant_verified:true,qualified_sessions_verified:true,attribution_verified:true,refund_fee_reconciled:true,
    asset_id:"grok-verified-123",utm_source:"tiktok",utm_medium:"organic_social",utm_campaign:"mind_pilot_2026_11"
  };
  const calc=contract.calculateRevenue(sample);
  test("synthetic verified sample computes expected net",calc.net_revenue_cents===9400&&calc.net_revenue_per_1000_qualified_humans_cents===47000);
  test("synthetic sample rate uses paid orders not outbound",calc.paid_conversion_rate===0.03);
  test("tiny sample explicit warning",calc.warning==="SMALL_SAMPLE_DESCRIPTIVE_ONLY");
  test("false merchant verification closes gate",contract.calculateRevenue({...sample,merchant_verified:false}).status==="NOT_COMPUTABLE");
  test("unreconciled refunds close gate",contract.calculateRevenue({...sample,refund_fee_reconciled:false}).status==="NOT_COMPUTABLE");
  test("uncorroborated attribution closes gate",contract.calculateRevenue({...sample,attribution_verified:false}).status==="NOT_COMPUTABLE");
  test("unverified sessions close gate",contract.calculateRevenue({...sample,qualified_sessions_verified:false}).status==="NOT_COMPUTABLE");
  test("zero sessions close denominator",contract.calculateRevenue({...sample,qualified_human_sessions:0}).status==="NOT_COMPUTABLE");
  test("negative fees refused",contract.calculateRevenue({...sample,fees_cents:-2}).status==="INVALID");
  test("invalid cohort length refused",contract.calculateRevenue({...sample,window_days:5}).status==="INVALID");
  test("noninteger money refused",contract.calculateRevenue({...sample,fees_cents:2.5}).status==="INVALID");
  test("invalid unverified social platform rejected",contract.calculateRevenue({...sample,utm_source:"TikTok&email"}).status==="INVALID");
  test("no personally identifying output in synthetic calculation",!JSON.stringify(calc).includes("grok-verified-123")&&!JSON.stringify(calc).includes("2026-11-04"));
  const failed=results.filter(t=>!t.pass);
  return {total:results.length,passed:results.length-failed.length,failed:failed.map(f=>f.name),results};
}
module.exports=audit;
if(typeof require!=="undefined" && require.main===module){
  const fs=require("node:fs"), path=require("node:path");
  const root=path.join(__dirname);
  const read=name=>fs.readFileSync(path.join(root,name),"utf8");
  const result=audit({
    article:read("illusory-truth-investigation.md"),
    decision:read("one-offer-conversion-decision.md"),
    html:read("zen12-unpublished-review-insert.html"),
    registry:JSON.parse(read("claims-and-merchant-gates.json")),
    contract:require("./attribution-contract.cjs")
  });
  for(const item of result.results)process.stdout.write((item.pass?"PASS ":"FAIL ")+item.name+"\n");
  process.stdout.write(result.passed+"/"+result.total+" passed\n");
  if(result.failed.length)process.exitCode=1;
}
