/* R262 source-integrity and commercial HOLD regression.
 * Node: node mind/r262/test_r262.cjs
 * This does not call a merchant, install scripts, or simulate an actual sale.
 * Independent GitHub-blob pin verification requires reading blobs by connector.
 */
"use strict";
const relative={
 article:"THE-WORD-THAT-WOULD-NOT-STAY-QUIET-UNPUBLISHED.md",
 hub:"MIND-STROOP-HUB-WP-SOURCE-UNPUBLISHED.html",
 matrix:"CLAIM-PROOF-OFFER-REVENUE-HOLD.json",
 plan:"SINGLE-OFFER-CONVERSION-RELEASE-ACCEPTANCE.md"
};
const sourceBlobPins={
 article:"6ea585eae47a9708c26e6d28f72c5e00bd4345f1",
 hub:"32f8973c4b6efa651c01285a555ad84881538cca",
 matrix:"2b74b0a50bec3050ac50eded0d78fe8700365737",
 plan:"65902e23f88afb169925e56097961a2e118576a0"
};
const requiredGates=[
"publisher_named_acceptance","issued_affiliate_url","specific_zen12_product_and_destination",
"website_channel_permission","social_channel_permission","email_channel_permission",
"approved_creative_usage_rights","exact_checkout_price_and_currency",
"merchant_tax_shipping_or_extra_charges","product_inclusion_equivalence_promo_vs_standard",
"refund_terms_specific_offer","merchant_refund_actual_process","buyer_facing_compliant_disclosure",
"first_party_event_definition_owner_signoff","merchant_confirmed_paid_commission_feed",
"founder_editorial_QA_release_approval"
];
function validate(b){
 const fail=[];
 function check(condition,reason){if(!condition)fail.push(reason)}
 let j;
 try{j=JSON.parse(b.matrix);}catch(e){return ["matrix JSON invalid: "+String(e)]}
 const a=b.article,h=b.hub,p=b.plan;
 check(a.trim().split(/\s+/).length>=1800,"article < 1800 words");
 for(const phrase of ["Stroop","MacLeod","1935","47.0 seconds","74.3%","Puységur","https://finalvestige.com/focus/","Unpublished","No commerce","FTC"])
   check(a.includes(phrase),"article lacks "+phrase);
 check(a.includes("https://doi.org/10.1037/h0054651"),"original paper missing");
 check(a.includes("https://pubmed.ncbi.nlm.nih.gov/2034749/"),"theory review missing");
 check(!/href\s*=\s*["'][^"']*(zen12|inspire3|payhip)/i.test(a),"article commercial link");
 check(!/\]\(https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|payhip\.com)[^)]*\)/i.test(a),"article commercial markdown link");
 check(!/affiliate recommendation appears here|buy now|affiliate purchase link/i.test(a),"article commercial endorsement");
 check(/<html lang="en">/.test(h),"hub lang");
 check(/name="robots" content="noindex,nofollow"/.test(h),"hub not noindexed");
 check(/<meta name="viewport"/.test(h),"hub viewport");
 for(const id of ['perception','history','practice','tools'])check(h.includes('id="'+id+'"'),"hub missing stream "+id);
 for(const link of ['https://finalvestige.com/focus/','https://finalvestige.com/2026/11/02/change-blindness/','https://finalvestige.com/2026/11/02/mesmerism/','https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'])
   check(h.includes(link),"hub link missing "+link);
 check(/<button\b[^>]*\bdisabled\b[^>]*>Merchant link withheld/i.test(h),"commercial CTA not disabled");
 check(/may earn a commission/.test(h),"plain language commission disclosure missing");
 const cta=h.indexOf("Merchant link withheld"),dis=h.indexOf("may earn a commission",cta);
 check(cta>=0&&dis>cta&&dis-cta<500,"FTC disclosure not proximate to disabled CTA");
 check(!/<(?:script|iframe|form|video|audio)\b/i.test(h),"hub has forbidden script/iframe/form/media");
 check(!/\bon(?:load|click|error|mouseover)\s*=/i.test(h),"hub inline handler");
 check(!/href\s*=\s*["'][^"']*(?:zen12|inspire3|payhip)/i.test(h),"hub has merchant or affiliate link");
 check(!/autoplay/i.test(h.replace(/no autoplay/gi,"")),"hub autoplay");
 check(/<details>/.test(h)&&/<summary>/.test(h),"optional no-JS film absent");
 const times=[...h.matchAll(/<time>(\d\d:\d\d)–(\d\d:\d\d)<\/time>/g)].map(m=>[m[1],m[2]]);
 check(times.length===7,"not seven timed captions");
 if(times.length===7){check(times[0][0]==="00:00"&&times[6][1]==="00:42","captions do not cover 42 sec");for(let i=0;i<6;i++)check(times[i][1]===times[i+1][0],"caption gap "+i);}
 check(Array.isArray(j.sources)&&j.sources.length>=16,"source record count");
 check(Array.isArray(j.claims)&&j.claims.length>=16,"claim matrix count");
 check(j.claims.some(x=>x.id==="C04"&&x.editorial_handling==="PROHIBITED"),"clinical-test prohibition missing");
 check(j.claims.some(x=>x.id==="C10"&&x.classification==="SELLER_CLAIM_NOT_SUBSTANTIATED"),"seller efficacy caution missing");
 check(j.commercial_gates?.length===16,"not 16 commercial gates");
 const gates=(j.commercial_gates||[]).map(x=>x.id);
 check(new Set(gates).size===16&&requiredGates.every(id=>gates.includes(id)),"gate ID exact identities/uniqueness");
 check(j.commercial_gates?.every(g=>g.status==="HARD_HOLD"&&g.evidence===null),"commercial gate opened without proof");
 check(Object.values(j.release_bounds||{}).every(v=>v===false)&&Object.keys(j.release_bounds||{}).length===7,"release boundaries altered");
 check(j.commercial_status?.named_inspire3_acceptance==="NOT_VERIFIED","invented acceptance");
 check(j.commercial_status?.fv_owned_mind_product==="NOT_AUTHENTICATED","invented owned SKU");
 check(j.measurement?.realized_net_revenue_per_1000_qualified_human_sessions==="NOT_COMPUTABLE","invented paid outcome");
 check(j.measurement?.plan_only===true,"telemetry presented as live");
 check((j.social_join||[]).length===3&&j.social_join.every(s=>s.asset_id===null),"invented Grok media IDs");
 check((j.sources||[]).every(s=>/^https:\/\//.test(s.url)),"invalid evidence URLs");
 check(p.includes("NOT COMPUTABLE")&&p.includes("HARD HOLD"),"plan commercial uncertainty missing");
 check(p.includes("Claude")&&p.includes("Grok")&&p.includes("PR #49")&&p.includes("PR #172"),"ownership/release boundaries missing");
 check(!/commission paid: \$[1-9]/i.test(p),"fabricated payout");
 return fail;
}
function mutationTests(input){
 const cases=[];
 const change=(label,field,from,to)=>{const x={...input};x[field]=x[field].replace(from,to);if(x[field]===input[field])throw Error("ineffective mutation "+label);cases.push([label,x]);};
 change("broken headline science", "article","47.0 seconds","47 sec");
 change("missing review","article","https://pubmed.ncbi.nlm.nih.gov/2034749/","MISSING");
 change("merchant in investigation","article","## The simple answer that is not simple",'[Get Zen12](https://zen12.com/hnp)\n\n## The simple answer that is not simple');
 change("lost viewport","hub",'<meta name="viewport"','<meta name="vport"');
 change("lost noindex","hub",'noindex,nofollow','index,follow');
 change("delete focus","hub",'https://finalvestige.com/focus/','https://example.org/novalue');
 change("enable buy button","hub",'disabled aria-disabled="true"','class="active"');
 change("delete FTC notice","hub",'may earn a commission','does not mention any payment');
 change("separate disclosure","hub",'may earn a commission', ' '.repeat(900)+'may earn a commission');
 change("install script","hub",'</body>','<script src="https://stats.example/pixel.js"></script></body>');
 change("auto remote media","hub",'</body>','<iframe src="https://video.example/"></iframe></body>');
 change("new signup form","hub",'</body>','<form><input type="email"></form></body>');
 change("new audio player","hub",'</body>','<audio autoplay></audio></body>');
 change("commercial link","hub",'Merchant link withheld','<a href="https://zen12.com/hnp">Merchant link withheld</a>');
 change("remove details","hub",'<details>','<div>');
 change("remove caption","hub",'<time>00:00–00:06</time>','<span>missing caption</span>');
 const editMatrix=(label,fn)=>{const x={...input};const j=JSON.parse(x.matrix);fn(j);x.matrix=JSON.stringify(j);cases.push([label,x]);};
 editMatrix("delete gate",j=>j.commercial_gates.pop());
 editMatrix("duplicate gate",j=>j.commercial_gates[0].id=j.commercial_gates[1].id);
 editMatrix("approve without proof",j=>j.commercial_gates[0].status="VERIFIED");
 editMatrix("invent approval",j=>j.commercial_status.named_inspire3_acceptance="APPROVED");
 editMatrix("invent owned SKU",j=>j.commercial_status.fv_owned_mind_product="VERIFIED_SELLABLE");
 editMatrix("forge paid outcome",j=>j.measurement.realized_net_revenue_per_1000_qualified_human_sessions="400");
 editMatrix("forge social media id",j=>j.social_join[0].asset_id="fake-id");
 editMatrix("invent production telemetry",j=>j.measurement.plan_only=false);
 editMatrix("alter release boundary",j=>j.release_bounds.merchant_link=true);
 editMatrix("delete source",j=>j.sources.length=0);
 editMatrix("erase clinical prohibition",j=>j.claims.find(x=>x.id==="C04").editorial_handling="SUPPORTED");
 editMatrix("promote seller claim to proven",j=>j.claims.find(x=>x.id==="C10").classification="PROVEN");
 change("erase hard hold from plan","plan","HARD HOLD","NOT BLOCKED");
 change("erase revenue uncertainty","plan","NOT COMPUTABLE","1000 dollars");
 let rejects=0;const misses=[];
 for(const [name,mutant] of cases){if(validate(mutant).length)rejects++;else misses.push(name);}
 return {total:cases.length,rejected:rejects,misses};
}
if(typeof module!=="undefined") module.exports={validate,mutationTests,relative,sourceBlobPins};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const root=__dirname;
 const input=Object.fromEntries(Object.entries(relative).map(([k,f])=>[k,fs.readFileSync(path.join(root,f),"utf8")]));
 const baseline=validate(input),run=mutationTests(input);
 if(baseline.length||run.misses.length){console.error(JSON.stringify({baseline,run},null,2));process.exitCode=1;}
 else console.log(JSON.stringify({baseline:"PASS",mutation_rejected:run.rejected,total:run.total,scope:"SOURCE_ONLY_NO_BROWSER_OR_COMMERCE"},null,2));
}
