"use strict";
// R235 source-only regression. Native: node mind/r235/test_mind_r235.cjs.
// No WordPress, merchant, browser, sales or video playback tests.
const expected={"sources":"c52873af","claims":"8ed7f52d","gates":"d1252fa0","conversion_contract":"406420e3","pilot":"6e6aed17"};
function hash(x){const s=typeof x==="string"?x:JSON.stringify(x);let h=2166136261;for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619)>>>0;return h.toString(16).padStart(8,"0")}
function violations(f){
 const err=[],ok=(x,s)=>{if(!x)err.push(s)};
 let m;try{m=JSON.parse(f.matrix)}catch(_){return ["invalid matrix JSON"]}
 ok(m.status==="UNPUBLISHED_HARD_HOLD","commercial status");
 for(const k of Object.keys(expected))ok(hash(m[k])===expected[k],"identity "+k);
 ok(m.sources?.length===18&&m.claims?.length===25&&m.gates?.length===16,"counts");
 ok(m.gates?.every(x=>x.status==="HARD_HOLD"&&x.proof==="NONE_AUTHENTICATED"),"gates remain held");
 ok(m.conversion_contract?.net_revenue_1000==="NOT_COMPUTABLE","no invented revenue");
 ok(m.pilot?.randomization==="NOT_LIVE","not live");
 ok(f.guide.length>15000&&f.guide.includes("PMC3113981")&&f.guide.includes("merchant")&&f.guide.includes("newsletter"),"source guide remains");
 ok(f.article.includes("explicitly instructed to think about the white bear")&&f.article.includes("instructed expression period"),"original experimental method");
 ok(!f.article.includes("participants were invited to think about the bear"),"old inaccurate procedure");
 ok(![f.r232Article,f.r232Matrix,f.r233Guard].some(s=>s.includes("PMC3181779")),"wrong PMC removed");
 ok([f.r232Article,f.r232Matrix,f.r233Guard].every(s=>s.includes("PMC3113981")),"correct PMC propagated");
 const core=x=>{const a=x.indexOf('<section class="guide"'),z=x.indexOf("</section>",a);return a<0||z<0?"":x.slice(a,z+10)};
 ok(core(f.a).length>7000&&core(f.a)===core(f.b),"A/B identical buyer decision copy");
 for(const [label,s] of [["A",f.a],["B",f.b]]){
  ok(s.includes('<html lang="en">')&&s.includes('name="viewport"'),"HTML semantics "+label);
  ok(s.includes('name="robots" content="noindex,nofollow"'),"noindex "+label);
  ok((s.match(/<button\b[^>]*\bdisabled\b[^>]*>/gi)||[]).length===1,"disabled merchant CTA "+label);
  ok(/id="affiliate-disclosure"[\s\S]{0,410}<button\b[^>]*aria-describedby="affiliate-disclosure"/i.test(s),"adjacent disclosure "+label);
  ok(s.includes("commission at no additional cost to you"),"commission wording "+label);
  ok(s.includes("merchant’s newsletter")&&s.includes("merchant signup must never be counted as a confirmed Final Vestige lead"),"seller list distinct "+label);
  ok(s.includes("https://finalvestige.com/focus/"),"existing Focus "+label);
  ok(s.includes("prefers-reduced-motion:reduce")&&s.includes(":focus-visible"),"accessibility indicators "+label);
  ok(!/<\s*(?:script|form|iframe|video|audio|object|embed|base)\b/i.test(s),"no active code/media/forms "+label);
  ok(!/\bon[a-z]+\s*=|\b(?:href|src|action)\s*=\s*["']?\s*(?:javascript:|data:)/i.test(s),"no handler/javascript URL "+label);
  ok(!/<a\b[^>]*href\s*=\s*["']?\s*(?:https?:)?\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(s),"no merchant anchors "+label);
  ok(!/http-equiv\s*=\s*["']?refresh|\bfetch\s*\(|\bXMLHttpRequest\b|\bwindow\.location\b|\bdocument\.cookie\b|\blocalStorage\b|url\s*\(\s*["']?https?:\/\//i.test(s),"no tracking/redirect "+label);
 }
 ok(!f.a.includes('class="video-proposal"')&&f.b.includes('class="video-proposal"'),"only B storyboard");
 ok(f.b.includes("Not a video player")&&f.b.includes("complete 42-second film transcript"),"unrendered B truthful");
 const cues=[...f.captions.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
 ok(cues.length===6,"caption count");
 if(cues.length===6){ok(cues[0][1]==="00:00:00.000"&&cues[5][2]==="00:00:42.000","caption limits");for(let i=1;i<6;i++)ok(cues[i-1][2]===cues[i][1],"caption continuity "+i)}
 ok(f.plan.includes("TASK-008")&&f.plan.includes("PR #172")&&f.plan.includes("PR #49")&&f.plan.includes("Issue #150"),"owner lanes");
 ok(f.plan.includes("HARD HOLD")&&f.plan.includes("NOT COMPUTABLE"),"no commercial launch");
 return err;
}
function exercise(f){
 const base=violations(f);if(base.length)throw Error("baseline "+base.join("; "));
 let count=0,miss=[];
 const mutate=(key,fn)=>{const v={...f};fn(v);const r=violations(v);if(r.length)count++;else miss.push(key)};
 const orig=JSON.parse(f.matrix);
 for(const part of ["sources","claims","gates"]){orig[part].forEach((_,i)=>{
  mutate(part+"-identity-"+i,v=>{const j=JSON.parse(v.matrix);j[part][i][part==="sources"?"url":part==="claims"?"statement":"name"]+=" changed";v.matrix=JSON.stringify(j)});
  mutate(part+"-status-"+i,v=>{const j=JSON.parse(v.matrix);j[part][i][part==="sources"?"kind":"status"]="APPROVED";v.matrix=JSON.stringify(j)});
 })}
 const fx=[
 ["enable A",v=>v.a=v.a.replace('type="button" disabled','type="button"')],
 ["enable B",v=>v.b=v.b.replace('type="button" disabled','type="button"')],
 ["remove disclosure",v=>v.a=v.a.replace('id="affiliate-disclosure"','id="gone"')],
 ["remove merchant consent",v=>v.b=v.b.replace("merchant’s newsletter","optional note")],
 ["mislabel merchant lead",v=>v.a=v.a.replace("merchant signup must never be counted as a confirmed Final Vestige lead","merchant signup counts as a lead")],
 ["insert script",v=>v.a+='<script>alert(1)</script>'],
 ["insert form",v=>v.b+='<form><input type=email></form>'],
 ["merchant href",v=>v.a+='<a href=https://zen12.com/hnp>buy</a>'],
 ["merchant href quoted",v=>v.b+='<a href="https://inspire3.com/">buy</a>'],
 ["handler",v=>v.a=v.a.replace('<main ', '<main onclick="evil()" ')],
 ["style pixel",v=>v.a+='<style>body{background:url(https://tracker.test/p)}</style>'],
 ["meta redirect",v=>v.b+='<meta http-equiv="refresh" content="1;url=/">'],
 ["video in A",v=>v.a+='<video></video>'],
 ["A B drift",v=>v.b=v.b.replace("Before leaving Final Vestige","After leaving Final Vestige")],
 ["article reverts",v=>v.article=v.article.replace("explicitly instructed to think about the white bear","invited to think")],
 ["wrong PMC article",v=>v.r232Article=v.r232Article.replace("PMC3113981","PMC3181779")],
 ["wrong PMC registry",v=>v.r232Matrix=v.r232Matrix.replace("PMC3113981","PMC3181779")],
 ["wrong PMC guard",v=>v.r233Guard=v.r233Guard.replace("PMC3113981","PMC3181779")],
 ["caption end",v=>v.captions=v.captions.replace("00:00:42.000","00:00:43.000")],
 ["remove captions",v=>v.captions="WEBVTT"],
 ["source guide gone",v=>v.guide=v.guide.slice(0,700)],
 ["no hold",v=>v.plan=v.plan.replace(/HARD HOLD/g,"APPROVED")],
 ["live A/B claim",v=>{const j=JSON.parse(v.matrix);j.pilot.randomization="LIVE";v.matrix=JSON.stringify(j)}],
 ["invent paid sales",v=>{const j=JSON.parse(v.matrix);j.conversion_contract.net_revenue_1000="500";v.matrix=JSON.stringify(j)}],
 ["remove Film transcript",v=>v.b=v.b.replace("complete 42-second film transcript","film")],
 ["remove Focus",v=>v.a=v.a.replace("https://finalvestige.com/focus/","/bad/")]
 ];
 for(const [k,fn] of fx)mutate(k,fn);
 if(miss.length)throw Error("undetected "+miss.join(", "));
 return {baseline:base.length,rejected:count,total:count,files:Object.keys(f).length};
}
module.exports={violations,exercise};
if(typeof require==="function"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const names={"a":"../r234/zen12-A-WHITE-BEAR-TEXT-UNPUBLISHED.html","b":"../r234/zen12-B-WHITE-BEAR-OPTIONAL-VIDEO-CONCEPT-UNPUBLISHED.html","article":"../r234/THE-BEAR-YOU-CANNOT-UNTHINK-UNPUBLISHED.md","matrix":"./SELLER-CONSENT-SCIENCE-CLAIM-AND-REVENUE-GATES.json","guide":"./TWELVE-MINUTE-DECISION-ZEN12-CONSENT-AND-PROOF-UNPUBLISHED.md","plan":"./OFFER-CREATOR-ATTRIBUTION-CONSENT-RELEASE-PACKET.md","captions":"../r234/WHITE-BEAR-42S-CAPTIONS-PROPOSAL.vtt","r232Article":"../r232/TWELVE-MINUTES-IS-NOT-AN-HOUR-UNPUBLISHED.md","r232Matrix":"../r232/SELLER-CLAIM-PROOF-AND-COMMERCE-GATES.json","r233Guard":"../r233/test_r233_registry.cjs"};
 const f=Object.fromEntries(Object.entries(names).map(([k,p])=>[k,fs.readFileSync(path.join(__dirname,p),"utf8")]));
 console.log("R235 PASS",exercise(f));
}