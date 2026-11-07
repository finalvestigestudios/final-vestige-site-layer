'use strict';
/* Reproducible R196 source-level tests: run node mind/r196/test_mind_r196.cjs at repo root; not browser/CI/sale proof. */
const fs=require('fs');const paths={
  "article": "mind/r196/the-second-target-that-vanished-ATTENTIONAL-BLINK-UNPUBLISHED.md",
  "hub": "mind/r196/mind-four-stream-CONVERSION-FIRST-WP-DRAFT-UNPUBLISHED.html",
  "ledger": "mind/r196/ATTENTIONAL-BLINK-SOURCES-PRODUCT-PERMISSIONS-REVENUE-GATES.json",
  "plan": "mind/r196/ONE-OFFER-ATTENTIONAL-BLINK-GROK-AB-NET-REVENUE-PLAN.md",
  "prior": "mind/r195/the-word-that-fought-the-color-STROOP-INVESTIGATION-UNPUBLISHED.md",
  "priorledger": "mind/r195/STROOP-CLAIM-SOURCE-COMMERCE-PROOF-MATRIX.json",
  "a": "mind/r188/zen12-variant-A-independent-text-UNPUBLISHED.html",
  "b": "mind/r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html"
};
function evaluate(d){
const out=[],check=(name,yes)=>out.push({name,pass:!!yes}),j=x=>{try{return JSON.parse(x)}catch{return {}}},l=j(d.ledger),p=j(d.priorledger),src=l.sources||[],claims=l.claims||[],gates=l.gates||[],ids=new Set(src.map(x=>x.id));
const btn=s=>[...s.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]),disabled=s=>btn(s).length>0&&btn(s).every(x=>/\sdisabled(?=\s|=|>)/i.test(x)),hids=[...d.hub.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]),aria=[...d.hub.matchAll(/\baria-describedby="([^"]+)"/g)].flatMap(x=>x[1].split(/\s+/));
const reqA=["1500880","7707027","PMC1865565","16989545","00466.x","10.3758/APP.71.8.1683"];reqA.forEach(x=>check("primary/reference "+x,d.article.includes(x)));
check("article >=2500 words",d.article.split(/\s+/).length>=2500);
check("original research with editorial firewall",d.article.startsWith("# The Second Target That Vanished")&&d.article.includes("EDITORIAL FIREWALL"));
check("no health or product proof leap",d.article.includes("branded audio program")&&d.article.includes("not a trial of hypnosis recordings"));
check("no referral tokens",!/[?&](aff_id|affiliate_id|hop|refid)=|awin1\.com\/cread/i.test(d.article));
check("ungated research",d.article.includes("subscription is optional"));
check("new paper not linked as public",!d.hub.includes('href="https://finalvestige.com/mind/attentional-blink'));
check("HTML semantics",/<!doctype html>/i.test(d.hub)&&/lang="en"/.test(d.hub)&&/id="main"/.test(d.hub));
check("mobile/robots",/name="viewport"/.test(d.hub)&&/noindex,nofollow/.test(d.hub));
check("skip link",d.hub.includes('class="skip"')&&d.hub.includes('href="#main"'));
check("disabled merchant hub",disabled(d.hub));
check("disclosure target defined",d.hub.includes('id="commission-disclosure"')&&d.hub.includes('aria-describedby="commission-disclosure"'));
check("adjacent commission statement",d.hub.indexOf('id="commission-disclosure"')<d.hub.indexOf('<button class="disabled"')&&d.hub.includes("may earn a commission")&&d.hub.includes("no additional cost"));
check("no script/form/JS handlers",!/<script\b|<form\b|onload\s*=|onclick\s*=/i.test(d.hub));
check("no actual media and autoplay attributes",!/<video\b|<iframe\b|<audio\b|\sautoplay(?=\s|=|>)/i.test(d.hub));
check("responsive CSS",d.hub.includes("@media(max-width:740px)"));
check("reduced motion",d.hub.includes("prefers-reduced-motion:reduce"));
check("forced contrast",d.hub.includes("forced-colors:active"));
check("no duplicate HTML IDs",hids.length===new Set(hids).size);
check("ARIA references valid",aria.every(x=>hids.includes(x)));
check("no external font/tracking",!/@import|fonts\.googleapis|analytics\.js/i.test(d.hub));
check("public seller link clearly informational",d.hub.includes("informational seller source, NOT an affiliate link"));
check("exact live Focus URL present",d.hub.includes("https://finalvestige.com/focus/"));
check("Puységur source URL present",d.hub.includes("puysegurs-animal-magnetism-files"));
check("22+ sources",src.length>=22);
check("30+ claim decisions",claims.length>=30);
check("21+ release gates",gates.length>=21);
check("unique source IDs/HTTPS",ids.size===src.length&&src.every(x=>/^https:\/\//.test(x.url)));
check("claims have valid source reference",claims.every(x=>x.source_ids?.length&&x.source_ids.every(id=>ids.has(id))));
check("unique claim ids",new Set(claims.map(x=>x.id)).size===claims.length);
check("all release gates false",gates.every(x=>x.passed===false));
check("publisher not verified",l.publisher_acceptance==="NOT_VERIFIED");
check("no earning URL",l.affiliate_earning_url===null);
check("no paid order",l.paid_order_count===null);
check("no received commissions",l.received_affiliate_commissions===null);
check("no invented net result",l.verified_net_revenue_per_1000_qualified_humans==="NOT_COMPUTABLE");
check("equivalence not substantiated",claims.find(x=>x.id==="zen12_equivalence")?.decision==="UNSUBSTANTIATED_SELLER_CLAIM");
check("outbound not a paid sale",claims.find(x=>x.id==="verified_orders")?.decision==="FALSE_UNSAFE_PROXY");
check("gift not confirmed optin",claims.find(x=>x.id==="focus_lead_proxy")?.decision==="FALSE_UNSAFE_PROXY");
check("privacy-safe attribution plan",d.plan.includes("utm_content")&&d.plan.includes("No personal identifiers"));
check("denominator/cohorts",d.plan.includes("net_realized_revenue_per_1000")&&d.plan.includes("day 7")&&d.plan.includes("day 30"));
check("offer-step-blocker-owner table",d.plan.includes("Offer → funnel step → blocker"));
check("Grok keeps posting",d.plan.includes("Grok owns media creative"));
check("old A/B remain",d.plan.includes("zen12-variant-A")&&d.plan.includes("zen12-variant-B")&&disabled(d.a)&&disabled(d.b));
check("A/B no added forms/scripts",!/<script\b|<form\b/i.test(d.a+d.b));
check("video still unrendered",d.plan.includes("42-second storyboard"));
check("R195 exercise fixed",d.prior.includes("read the *words* aloud")&&!d.prior.includes("read the *letters* aloud"));
check("R195 exact adjusted timing",d.prior.includes("error-adjusted mean difference")&&d.prior.includes("110.3 versus 63.3"));
check("R195 source scope 115 studies",d.prior.includes("133 neuroimaging experiments across 115 studies"));
check("R195 2024 vs 2025",d.prior.includes("12 September 2024")&&d.prior.includes("2025 journal issue"));
check("R195 emotion variant precise",d.prior.includes("emotional-word color-naming"));
check("R195 ledger corrected",p.claims?.find(x=>x.id==="stroop_colorname")?.limits?.includes("110.3 vs 63.3")&&p.sources?.find(x=>x.id==="macleod1991")?.note?.includes("approximately 400"));
return out;
}
function negative(d){
const results=[],base=evaluate(d);
function mutate(name,key,fn){const x=evaluate({...d,[key]:fn(d[key])});results.push({name,detected:x.some((v,i)=>!v.pass&&base[i].pass)})}
mutate("hub button enabled","hub",s=>s.replace(/(<button\b[^>]*?)\sdisabled(?=\s|=|>)/i,"$1"));
mutate("A button enabled","a",s=>s.replace(/(<button\b[^>]*?)\sdisabled(?=\s|=|>)/i,"$1"));
mutate("B button enabled","b",s=>s.replace(/(<button\b[^>]*?)\sdisabled(?=\s|=|>)/i,"$1"));
mutate("disclosure erased","hub",s=>s.replace('id="commission-disclosure"','id="wrong"'));
mutate("commission erased","hub",s=>s.replace("may earn a commission","may have a feeling"));
mutate("cost disclosure erased","hub",s=>s.replace("no additional cost","an additional cost"));
mutate("external script inserted","hub",s=>s.replace("</body>",'<script src="https://bad.example/pixel"></script></body>'));
mutate("duplicate subscriber form","hub",s=>s.replace("</body>",'<form><input type="email"></form></body>'));
mutate("autoplay film inserted","hub",s=>s.replace("</body>",'<video autoplay src="x.mp4"></video></body>'));
mutate("robots changed","hub",s=>s.replace("noindex,nofollow","index,follow"));
mutate("reduced motion omitted","hub",s=>s.replace("prefers-reduced-motion:reduce","prefers-color-scheme:dark"));
mutate("contrast omitted","hub",s=>s.replace("forced-colors:active","forced-colors:none"));
mutate("duplicate id","hub",s=>s.replace('id="reviews"','id="history"'));
mutate("public source mislabeled","hub",s=>s.replace("informational seller source, NOT an affiliate link","guaranteed affiliate"));
mutate("new unpublished article rendered live","hub",s=>s.replace("UNPUBLISHED · ARTICLE UNDER EDITORIAL REVIEW",'<a href="https://finalvestige.com/mind/attentional-blink-second-target/">Live</a>'));
mutate("earning URL invented","ledger",s=>s.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://bad.example"'));
mutate("partner approval invented","ledger",s=>s.replace('"publisher_acceptance": "NOT_VERIFIED"','"publisher_acceptance": "APPROVED"'));
mutate("orders invented","ledger",s=>s.replace('"paid_order_count": null','"paid_order_count": 5'));
mutate("commission invented","ledger",s=>s.replace('"received_affiliate_commissions": null','"received_affiliate_commissions": 50'));
mutate("net figure invented","ledger",s=>s.replace('"NOT_COMPUTABLE"','"100.00"'));
mutate("release gate switched","ledger",s=>s.replace('"passed": false','"passed": true'));
mutate("claim source corrupted","ledger",s=>s.replace('"source_ids": [\n        "raymond1992"','"source_ids": [\n        "no-such-paper"'));
mutate("seller equivalence made proven","ledger",s=>s.replace('"UNSUBSTANTIATED_SELLER_CLAIM"','"PROVEN"'));
mutate("subscription made mandatory","article",s=>s.replace("subscription is optional","subscription is mandatory"));
mutate("original source deleted","article",s=>s.replace("pubmed.ncbi.nlm.nih.gov/1500880","example.com"));
mutate("Grok ownership overwritten","plan",s=>s.replace("Grok owns media creative","Mind owns media creative"));
mutate("old exercise wrong","prior",s=>s.replace("read the *words* aloud","read the *letters* aloud"));
mutate("adjusted means wrong","prior",s=>s.replace("110.3 versus 63.3","110.3 versus 53.3"));
mutate("review falsely more than 400","priorledger",s=>s.replace("approximately 400","400+"));
return results;
}
function run(){const d=Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,fs.readFileSync(p,'utf8')]));const c=evaluate(d),n=negative(d);const r={checks:{passed:c.filter(x=>x.pass).length,total:c.length,failed:c.filter(x=>!x.pass)},mutations:{detected:n.filter(x=>x.detected).length,total:n.length,missed:n.filter(x=>!x.detected)}};console.log(JSON.stringify(r,null,2));if(r.checks.passed!==r.checks.total||r.mutations.detected!==r.mutations.total)process.exitCode=1;return r;}
if(require.main===module)run();module.exports={paths,evaluate,negative,run};
