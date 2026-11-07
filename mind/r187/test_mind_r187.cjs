/* R187 source-level test. Run: node mind/r187/test_mind_r187.cjs
No website access, analytics, merchant buying or affiliate activation. */
"use strict";
const filemap={
 guide:"the-voice-in-the-headphones-hypnosis-evidence-BUYER-GUIDE-UNPUBLISHED.md",
 evidence:"claims-merchant-permissions-and-paid-proof-ledger.json",
 plan:"one-offer-creator-fit-privacy-ab-paid-revenue-ACCEPTANCE.md",
 hub:"mind-four-stream-archive-HUB-PREVIEW-UNPUBLISHED.html",
 whitebear:"../r186/white-bear-thought-suppression-INVESTIGATION-UNPUBLISHED.md",
 A:"../r186/zen12-A-independent-text-UNPUBLISHED.html",
 B:"../r186/zen12-B-optional-42s-concept-UNPUBLISHED.html"
};
function validate(f){
 const tests=[],failed=[];
 function check(label,pass){tests.push(label);if(!pass)failed.push(label);}
 for(const [k] of Object.entries(filemap))check("present "+k,typeof f[k]==="string"&&f[k].length>900);
 let j={};try{j=JSON.parse(f.evidence)}catch(_){}
 check("evidence 16+ actual source URLs",j.evidence?.length>=16&&j.evidence.every(x=>/^https:\/\//.test(x.url)));
 check("claim decisions 20+",j.claim_decisions?.length>=20);
 check("gates >=12",j.gates?.length>=12);
 check("affiliate activation explicitly off",j.affiliate_activation===false);
 check("earning URL null",j.affiliate_earning_url===null);
 check("publisher acceptance null",j.named_fv_publisher_approval===null);
 check("permitted channels null",j.permitted_promotional_channels===null);
 check("owned product not invented",j.verified_owned_payhip_mind_sku===null);
 check("purchases unknown",j.merchant_confirmed_purchases===null);
 check("commissions unknown",j.independently_paid_affiliate_commissions===null);
 check("qualified sessions unknown",j.qualified_human_sessions===null);
 check("net revenue unknown",j.realized_net_revenue===null);
 check("named authorization gate blocked",j.gates?.find(x=>x.id==="named_approval")?.state==="BLOCKED");
 check("signed partner link gate blocked",j.gates?.find(x=>x.id==="authorized_earning_link")?.state==="BLOCKED");
 check("official offer and FTC source",f.evidence.includes("https://hypnosislive.com/mental-skills/total-focus")&&f.evidence.includes("ftcs-endorsement-guides")&&f.evidence.includes("health-products-compliance-guidance"));
 check("guide exact seller distinction",f.guide.includes("33-minute, 47 MB")&&f.guide.includes("advertiser benefit claims"));
 check("guide independent apps review",f.guide.includes("679 unique apps")&&f.guide.includes("168")&&f.guide.includes("four"));
 check("guide clinical scoping limits",f.guide.includes("16 randomized controlled trials")&&f.guide.includes("does not evaluate Total Focus"));
 check("guide no commercial endorsement",f.guide.includes("no live affiliate recommendation")&&f.guide.includes("not a hands-on review"));
 check("guide Focus existing funnel",f.guide.includes("https://finalvestige.com/focus/")&&f.guide.includes("existing Dispatch/Jetpack"));
 check("guide independent primary research",f.guide.includes("10.1080/00207144.2024.2434085")&&f.guide.includes("10.1080/00207144.2025.2528232"));
 check("white bear explicitly told to think after suppression",f.whitebear.includes("instruction to think about the white bear")&&f.whitebear.includes("not an unconstrained, neutral no-instruction baseline"));
 check("both buyer HTML have actual FTC editorial links",[f.A,f.B].every(t=>t.includes('href="https://finalvestige.com/editorial-standards/"')&&t.includes("ftcs-endorsement-guides-what-people-are-asking")&&!t.includes("Our editorial standards, FTC disclosure guidance")));
 check("poster alt reflects actual graphic",f.B.includes("there is no white bear depicted")&&!f.B.includes("Poster showing a white bear inside"));
 check("both disabled merchant buttons",[f.A,f.B].every(t=>t.includes('<button type="button" disabled aria-disabled="true">')&&!/<button type="button">\s*Merchant offer/i.test(t)));
 check("disclosure immediately precedes disabled CTA",[f.A,f.B].every(t=>/class="disclosure"[^>]*>[\s\S]*?may earn a commission[\s\S]*?<\/p>\s*<button type="button" disabled/i.test(t)));
 check("no script iframe form in HTML",[f.A,f.B,f.hub].every(t=>!/<(?:script|iframe|form)\b/i.test(t)));
 check("no javascript autoplay or remote media in HTML",[f.A,f.B,f.hub].every(t=>!/\bon(?:click|error|load)\s*=|javascript:|<(?:video|audio|source)\b/i.test(t)));
 check("no live affiliate earning URL in HTML",[f.A,f.B,f.hub].every(t=>!/awin1\.com|clickbank|[?&](?:hop|affid|affiliate_id|ref)=/i.test(t)));
 check("noindex protected mockups",[f.A,f.B,f.hub].every(t=>t.includes('content="noindex,nofollow"')));
 check("one existing focus path remains",[f.A,f.B,f.hub].every(t=>t.includes('https://finalvestige.com/focus/')));
 check("R186 A/B controlled difference",f.B.replace(/<section id="optional-film"[\s\S]*?<\/section>/,"")===f.A);
 check("video only static 42-second optional",f.B.includes("00:37–00:42")&&f.B.includes("No playback, autoplay")&&f.B.includes('id="optional-film"'));
 check("hub 4 streams",["PERCEPTION & ATTENTION","HISTORY OF SUGGESTION","PRACTICE & REFLECTION","TOOLS UNDER REVIEW"].every(t=>f.hub.includes(t)));
 check("hub no live route claim",f.hub.includes("NOT A LIVE WORDPRESS ROUTE")&&f.hub.includes("No new subscribe form"));
 check("Grok ownership explicit",f.plan.includes("Grok and Praxxis own")&&f.plan.includes("actual_immutable_asset_id"));
 check("merchant sale separate from click",f.plan.includes("affiliate_click")&&f.plan.includes("merchant_confirmed_purchase")&&f.plan.includes("NOT COMPUTABLE"));
 check("release approval withheld",f.plan.includes("DO NOT publish or merge")&&f.plan.includes("explicit founder release"));
 return {tested:tests.length,passed:tests.length-failed.length,failed};
}
function mutations(f){
 const scenarios=[
 ["buy button enabled","A",s=>s.replace('type="button" disabled','type="button"')],
 ["B buy button enabled","B",s=>s.replace('type="button" disabled','type="button"')],
 ["hide disclosure","A",s=>s.replace('may earn a commission','absolutely free')],
 ["inject tracker","B",s=>s.replace("</body>",'<script src="https://tracker.example/p.js"></script></body>')],
 ["inject signup","hub",s=>s.replace("</body>",'<form action="https://send.example"><input></form></body>')],
 ["invent affiliate approval","evidence",s=>s.replace('"affiliate_activation": false','"affiliate_activation": true')],
 ["invent authorized link","evidence",s=>s.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://earn.example"')],
 ["invent paid order","evidence",s=>s.replace('"merchant_confirmed_purchases": null','"merchant_confirmed_purchases": 23')],
 ["invent revenue","evidence",s=>s.replace('"realized_net_revenue": null','"realized_net_revenue": 100')],
 ["invent denominator","evidence",s=>s.replace('"qualified_human_sessions": null','"qualified_human_sessions": 2000')],
 ["invent owned SKU","evidence",s=>s.replace('"verified_owned_payhip_mind_sku": null','"verified_owned_payhip_mind_sku": "made-up"')],
 ["remove source","guide",s=>s.replace(/10\.1080\/00207144\.2024\.2434085/g,"MISSING-DOI")],
 ["restore misleading white bear protocol","whitebear",s=>s.replace("instruction to think about the white bear","permission to think about the white bear")],
 ["erase real FTC href","B",s=>s.replace("ftcs-endorsement-guides-what-people-are-asking","wrong-ftc-reference")],
 ["false poster alt","B",s=>s.replace("there is no white bear depicted","there is a depicted white bear")],
 ["wreck A/B parity","A",s=>s.replace("Can twelve minutes make a routine—not a miracle?","A totally different offer")],
 ["remove 42s transcript","B",s=>s.replace("00:37–00:42","00:37–??")],
 ["erase noindex","hub",s=>s.replace('content="noindex,nofollow"','content="index,follow"')],
 ["enable iframe","hub",s=>s.replace("</body>",'<iframe src="https://external.example"></iframe></body>')],
 ["fake verified commission","evidence",s=>s.replace('"independently_paid_affiliate_commissions": null','"independently_paid_affiliate_commissions": 3')],
 ];
 let detected=0;let failed=[];
 for(const [name,key,mutate] of scenarios){const changed=mutate(f[key]);if(changed===f[key]){failed.push(name+" no-op");continue;}let trial=validate({...f,[key]:changed});if(trial.failed.length)detected++;else failed.push(name+" escaped");}
 return {total:scenarios.length,detected,failed};
}
module.exports={filemap,validate,mutations};
if(typeof require==="function"&&typeof process==="object"&&require.main===module){
 const fs=require("fs"),path=require("path"),f={};
 for(const [k,v] of Object.entries(filemap))f[k]=fs.readFileSync(path.resolve(__dirname,v),"utf8");
 const positive=validate(f),negative=mutations(f);
 console.log(JSON.stringify({positive,negative},null,2));
 if(positive.failed.length||negative.failed.length)process.exitCode=1;
}