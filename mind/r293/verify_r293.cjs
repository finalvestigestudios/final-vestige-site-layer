/* FV Mind R293 — offline source QA. From repo root: node mind/r293/verify_r293.cjs
   This is not CI, WCAG browser testing, a WordPress export, or verified revenue. */
"use strict";
const fs = typeof require !== "undefined" ? require("fs") : null;
const path = typeof require !== "undefined" ? require("path") : null;
const PATHS={
 article:"mind/r293/THE-CHOICE-YOU-NEVER-MADE-UNPUBLISHED.md",
 hub:"mind/r293/MIND-CHOICE-BLINDNESS-READING-ROOM-UNPUBLISHED.html",
 matrix:"mind/r293/CHOICE-BLINDNESS-PRODUCT-CLAIMS-REVENUE-GATES.json",
 plan:"mind/r293/ONE-OFFER-CONVERSION-QA-AND-CREATOR-HANDOFF.md",
 A:"mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html",
 B:"mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html"
};
const PINS={article:"ac029e74",hub:"c01b2971",matrix:"13908fa6",plan:"73bcfcef",A:"ed05f7c4",B:"7a5e3be1"};
const assert=(v,m)=>{if(!v)throw Error("R293 QA: "+m)};
function fnv(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return(h>>>0).toString(16).padStart(8,"0")}
function decode(s){return s.replace(/&#x([0-9a-f]+);?|&#([0-9]+);?|&colon;?|&sol;?|&Tab;?|&NewLine;?/gi,(m,h,n)=>h?String.fromCodePoint(parseInt(h,16)):n?String.fromCodePoint(+n):/^&colon/i.test(m)?":":/^&sol/i.test(m)?"/":/^&tab/i.test(m)?"\t":"\n")}
function checkHtml(h,label,strict){
 const s=decode(h).replace(/<!--[\s\S]*?-->/g,"");
 assert(/<!doctype html>/i.test(s),"doctype "+label);
 assert(!/<\s*(script|iframe|form|object|embed|link|base|input|textarea|select|canvas|audio|video|source|track|img|picture|svg)\b/i.test(s),"active/remote element "+label);
 assert(!/\son[a-z]+\s*=|\b(srcdoc|src|srcset|poster|action|formaction|ping|data-src|data-href)\s*=|@import\b|\burl\s*\(|\bexpression\s*\(/i.test(s),"remote/event attribute "+label);
 const b=[...s.matchAll(/<button\b([^>]*)>/gi)];
 assert(b.length===1,"exactly one buying button "+label);
 assert(/(?:^|\s)disabled(?:\s|=|$)/i.test(b[0][1]),"genuinely disabled "+label);
 const bi=s.indexOf(b[0][0]);const near=s.slice(Math.max(0,bi-1200),bi);
 assert(/may earn a commission/i.test(near)&&/no additional cost/i.test(near),"adjacent disclosure "+label);
 assert(/https:\/\/finalvestige\.com\/focus\//i.test(s),"free path "+label);
 if(strict){
   assert(/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(s),"noindex "+label);
   const anchors=[...s.matchAll(/<a\b([^>]*)>/gi)];
   assert(anchors.length>=8,"research navigation "+label);
   for(const [,attrs] of anchors){
     const m=attrs.match(/(?:^|\s)href\s*=\s*(["'])(.*?)\1/i);
     assert(m&&m[2],"quoted href only "+label);
     const url=m[2].trim();
     assert(!/^(javascript:|vbscript:|data:|file:|blob:|\/\/)/i.test(url),"unsafe href "+label);
     if(url.startsWith("#"))continue;
     assert(/^https:\/\//.test(url),"HTTPS-only "+label);
     const host=(url.match(/^https:\/\/([^/]+)/)||[])[1]||"";
     assert(/^(finalvestige\.com|portal\.research\.lu\.se|pubmed\.ncbi\.nlm\.nih\.gov|onlinelibrary\.wiley\.com|www\.ftc\.gov)$/.test(host),"allowlisted research host "+host);
   }
   assert(!/https:\/\/(?:www\.)?(zen12|hypnosislive|brainwaveshots|inspire3)\.com\//i.test(s),"no merchant URLs anywhere in preview");
 }
}
function validate(x,pin=true){
 for(const k of Object.keys(PATHS)){
   assert(typeof x[k]==="string"&&x[k].length>1000,"full source missing "+k);
   if(pin)assert(fnv(x[k])===PINS[k],"exact pinned bytes "+k);
 }
 const m=JSON.parse(x.matrix);
 assert(m.status==="UNPUBLISHED_HARD_HOLD","release identity");
 assert(m.sources?.length===24&&m.claims?.length===32&&m.authorization_gates?.length===18,"exact cardinality");
 assert(fnv(m.sources.map(s=>s.id+"|"+s.url).join("\n"))==="6c673689","source ID:URL truth binding");
 assert(fnv(m.claims.map(c=>c.id+"|"+c.source_ids.join(",")+"|"+c.decision).join("\n"))==="ab99e85a","claim ID:source:decision binding");
 assert(fnv(m.authorization_gates.map(g=>g.id+"|"+g.status).join("\n"))==="452942c4","gate identity binding");
 const ids=new Set(m.sources.map(s=>s.id)); assert(ids.size===24,"unique sources");
 for(const c of m.claims)assert(c.source_ids.length>0&&c.source_ids.every(id=>ids.has(id))&&c.limits.length>=8,"claim limitations "+c.id);
 assert(m.authorization_gates.every(g=>g.status==="HARD_HOLD"&&g.verified_at===null&&g.evidence===null&&!g.override_allowed),"18 hard holds");
 assert(Object.values(m.release).every(v=>v===false),"all live release actions off");
 const c=m.commercial_primary_hypothesis;
 assert(c.cta_disabled&&c.affiliate_earning_url===null&&c.price_to_quote===null&&c.commission_to_quote===null,"no commercial activation");
 assert(c.canonical_variants[0]===PATHS.A&&c.canonical_variants[1]===PATHS.B,"actual A+B path identities");
 assert(m.owned_fallback.verified_paid_mind_sku===null&&!m.owned_fallback.paid_checkout_approved,"no invented owned product");
 assert(m.creator_topic_fit.length===3&&m.creator_topic_fit.every(x=>x.post_asset_id===null&&x.post_url===null&&!x.campaign_live&&!x.media_rights_verified),"no fabricated Grok assets");
 assert(m.experiment.variant_B_currently_playable===false&&m.experiment.release_status==="HARD_HOLD","no playable video claim");
 assert(m.measurement_contract.live_events===false&&m.measurement_contract.no_PII&&m.measurement_contract.no_duplicate_tracking&&m.measurement_contract.no_duplicate_email_forms,"privacy measures off");
 assert(m.measurement_contract.net_revenue_per_1000_formula.includes("settled_FV_affiliate_commissions"),"affiliate cleared not basket revenue");
 checkHtml(x.hub,"hub",true);
 checkHtml(x.A,"A",false);checkHtml(x.B,"B",false);
 for(const k of ["A","B"])assert(x[k].includes("14-day refund-request window")&&x[k].includes("five refunded sessions")&&x[k].includes("fewer than half"),"refund restrictions "+k);
 assert(x.A.includes("Variant A / text only")&&x.B.includes("Variant B / optional film concept"),"A/B status");
 assert(x.B.includes("Storyboard only")&&x.B.includes("no playable video yet"),"static B is not media");
 assert(/71 pedestrians/.test(x.article)&&/40\.8%/.test(x.article)&&/five experiments/.test(x.article),"independent research study details");
 assert(/NOT COMPUTABLE/.test(x.plan)&&/cleared FV affiliate commissions/.test(x.plan),"net revenue truth");
 return {source_count:24,claim_count:32,gates:"18 HARD_HOLD",canonical_loaded:["A","B"],words:x.article.trim().split(/\s+/).length};
}
function mutationTests(x){
 const tests=[],modify=(name,fn)=>{let y={...x};try{fn(y);validate(y,false);tests.push({name,pass:false})}catch(e){tests.push({name,pass:true})}};
 const json=(y,fn)=>{let j=JSON.parse(y.matrix);fn(j);y.matrix=JSON.stringify(j)};
 modify("source URL swap",y=>json(y,j=>j.sources[0].url="https://fake.example"));
 modify("source ID replacement",y=>json(y,j=>j.sources[0].id="s24"));
 modify("claim source swap",y=>json(y,j=>j.claims[0].source_ids=["s19"]));
 modify("seller claim promoted to ALLOW",y=>json(y,j=>j.claims[17].decision="ALLOW"));
 modify("claim limitation erased",y=>json(y,j=>j.claims[4].limits=""));
 modify("gate count reduced",y=>json(y,j=>j.authorization_gates.pop()));
 modify("affiliate accepted fabricated",y=>json(y,j=>j.authorization_gates[0].status="APPROVED"));
 modify("sale link invented",y=>json(y,j=>j.commercial_primary_hypothesis.affiliate_earning_url="https://zen12.com/?ref=FAKE"));
 modify("price fabricated",y=>json(y,j=>j.commercial_primary_hypothesis.price_to_quote=9.99));
 modify("commission fabricated",y=>json(y,j=>j.commercial_primary_hypothesis.commission_to_quote="99%"));
 modify("owned SKU fabricated",y=>json(y,j=>j.owned_fallback.verified_paid_mind_sku="fake-sku"));
 modify("video hosted fabricated",y=>json(y,j=>j.experiment.variant_B_currently_playable=true));
 modify("creator ID invented",y=>json(y,j=>j.creator_topic_fit[0].post_asset_id="FAKE"));
 modify("creator live claimed",y=>json(y,j=>j.creator_topic_fit[1].campaign_live=true));
 modify("PII permission",y=>json(y,j=>j.measurement_contract.no_PII=false));
 modify("tracking enabled",y=>json(y,j=>j.measurement_contract.live_events=true));
 modify("duplicate optin allowed",y=>json(y,j=>j.measurement_contract.no_duplicate_email_forms=false));
 modify("merchant revenue replaced",y=>json(y,j=>j.measurement_contract.net_revenue_per_1000_formula="merchant_gross / clicks"));
 modify("WordPress release enabled",y=>json(y,j=>j.release.wordpress_write=true));
 modify("A and B same file",y=>json(y,j=>j.commercial_primary_hypothesis.canonical_variants[1]=PATHS.A));
 modify("disclosure erased",y=>y.hub=y.hub.replace("may earn a commission","might mention"));
 modify("purchase button enabled",y=>y.hub=y.hub.replace('type="button" disabled','type="button"'));
 modify("merchant checkout link inserted",y=>y.hub=y.hub.replace("</footer>",'<a href="https://zen12.com/getstarted">Buy</a></footer>'));
 modify("encoded unsafe URL inserted",y=>y.hub=y.hub.replace("</footer>",'<a href="java&#115;cript:alert(1)">click</a></footer>'));
 modify("unquoted merchant link inserted",y=>y.hub=y.hub.replace("</footer>",'<a href=https://zen12.com/getstarted>Buy</a></footer>'));
 modify("tracking pixel inserted",y=>y.hub=y.hub.replace("</footer>",'<img src="https://tracker.example/p"></footer>'));
 modify("remote CSS import",y=>y.hub=y.hub.replace("</style>","@import url('https://tracker.example/p');</style>"));
 modify("unsafe event handler",y=>y.hub=y.hub.replace('<main id="main"','<main onclick="alert(1)" id="main"'));
 modify("hidden form inserted",y=>y.hub=y.hub.replace("</footer>","<form><input></form></footer>"));
 modify("autoplay video inserted",y=>y.hub=y.hub.replace("</footer>",'<video autoplay src="fake.mp4"></video></footer>'));
 modify("A affiliate enabled",y=>y.A=y.A.replace('type="button" disabled','type="button"'));
 modify("B disclosure erased",y=>y.B=y.B.replace("may earn a commission","may provide information"));
 modify("A refund restrictions erased",y=>y.A=y.A.replace("five refunded sessions","unlimited refunds"));
 modify("B now playable falsely",y=>y.B=y.B.replace("Storyboard only","Video streaming"));
 modify("article sample erased",y=>y.article=y.article.replace("71 pedestrians","everyone"));
 modify("revenue denominator erased",y=>y.plan=y.plan.replaceAll("NOT COMPUTABLE","ZERO"));
 return {total:tests.length,rejected:tests.filter(t=>t.pass).length,missed:tests.filter(t=>!t.pass).map(t=>t.name)};
}
function fromDisk(root="."){return Object.fromEntries(Object.entries(PATHS).map(([k,p])=>[k,fs.readFileSync(path.join(root,p),"utf8")]))}
if(typeof module!=="undefined")module.exports={PATHS,PINS,fnv,validate,mutationTests,fromDisk};
if(typeof module!=="undefined"&&typeof require!=="undefined"&&require.main===module){
 const x=fromDisk(process.argv[2]||"."),base=validate(x,true),mut=mutationTests(x);
 console.log(JSON.stringify({baseline:"PASS",...base,mutants:mut},null,2));
 if(mut.rejected!==mut.total)process.exitCode=1;
}
