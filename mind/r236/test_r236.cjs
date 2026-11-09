"use strict";
// R236 static-source guard. Native run: node mind/r236/test_r236.cjs
// NEVER interpret this as WordPress/browser/checkout/revenue evidence.
const frozen={sources:"cebc7a2f",claims:"e19b193f",gates:"d610e433",tracking:"fd336855",experiment:"8b990394"};
function digest(x){let s=JSON.stringify(x),h=2166136261;for(let i=0;i<s.length;i++)h=Math.imul(h^s.charCodeAt(i),16777619)>>>0;return h.toString(16).padStart(8,"0")}
function tagAttrs(s,tag){const re=new RegExp("<"+tag+"\\b([^>]*)>","gi");return Array.from(s.matchAll(re),m=>m[1])}
function issues(f){
 const errors=[],check=(v,s)=>{if(!v)errors.push(s)};
 let m;try{m=JSON.parse(f.matrix)}catch(e){return ["invalid JSON matrix"]}
 check(m.version==="R236"&&m.state==="SOURCE_DRAFT_NO_CMS_NO_AFFILIATE_RELEASE","R236 draft identity");
 for(const k in frozen)check(digest(m[k])===frozen[k],"immutable "+k);
 check(m.sources?.length===19&&m.claims?.length===24&&m.gates?.length===16,"expected registry counts");
 check(m.gates.every(x=>x.status==="HARD_HOLD"&&x.proof==="NOT_AUTHENTICATED"),"all gates held");
 check(m.tracking.net_revenue_per_1000==="NOT_COMPUTABLE"&&m.experiment.state==="DRAFT_NOT_LIVE","no invented result");
 check(f.article.split(/\s+/).length>2400&&f.article.includes("336 milliseconds")&&f.article.includes("672 milliseconds")&&f.article.includes("Seventeen participants"),"primary-method article");
 check(f.article.includes("https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.0050138")&&f.article.includes("https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0286023"),"research bibliography");
 check(f.article.includes("no merchant CTA")&&f.article.includes("no affiliate URL"),"article commerce separation");
 const p=f.preview;
 check(/<html lang="en"/.test(p)&&/name="viewport"/.test(p)&&/noindex,nofollow/.test(p),"html semantics/index hold");
 check(/href="#content"/.test(p)&&/id="content"/.test(p),"skip link");
 check(/:focus-visible/.test(p)&&/prefers-reduced-motion:reduce/.test(p)&&/forced-colors:active/.test(p),"a11y source markers");
 check(/role="img"/.test(p)&&/aria-labelledby=/.test(p),"original SVG accessibility");
 const buttons=tagAttrs(p,"button");
 check(buttons.length===1&&/(?:^|\s)disabled(?:\s|=|$)/i.test(buttons[0]),"genuinely disabled native button");
 check(buttons.length===1&&/aria-describedby="affiliate-disclosure"/.test(buttons[0]),"button disclosure association");
 const pos=p.indexOf('id="affiliate-disclosure"'),pos2=p.indexOf("<button",pos);
 check(pos>=0&&pos2>pos&&pos2-pos<600&&p.includes("commission at no additional cost to you"),"adjacent FTC disclosure");
 check(/merchant.{0,24}newsletter/i.test(p)&&p.includes("not Final Vestige"),"merchant-owned newsletter distinction");
 check(p.includes('href="https://finalvestige.com/focus/"'),"existing Focus route");
 for(const [name,s] of [["preview",p],["A",f.a],["B",f.b]]){
  check(!/<\s*(script|form|iframe|video|audio|object|embed|base)\b/i.test(s),"no scripts/forms/external media "+name);
  check(!/\bon[a-z]+\s*=|javascript\s*:|data\s*:/i.test(s),"no handlers/unsafe urls "+name);
  check(!/http-equiv\s*=\s*["']?refresh|window\.location|document\.cookie|localStorage|XMLHttpRequest|fetch\s*\(|url\s*\(\s*["']?https?:\/\//i.test(s),"no covert redirects/pixels "+name);
  const links=Array.from(s.matchAll(/<a\b[^>]*href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/gi),x=>(x[1]||x[2]||x[3]).toLowerCase());
  check(!links.some(u=>/^(https?:)?\/\/(www\.)?(zen12|inspire3|hypnosislive|brainwaveshots)\./.test(u)),"no merchant anchor "+name);
 }
 for(const [name,s] of [["A",f.a],["B",f.b]]){
  const b=tagAttrs(s,"button");
  check(b.length===1&&/(?:^|\s)disabled(?:\s|=|$)/i.test(b[0]),"inherited button native-disabled "+name);
 }
 const core=s=>{const i=s.indexOf('<section class="guide"'),j=s.indexOf("</section>",i);return i<0||j<0?"":s.slice(i,j+10)};
 check(core(f.a).length>7000&&core(f.a)===core(f.b),"inherited pilot buyer copy identical");
 check(f.plan.includes("TASK-008")&&f.plan.includes("PR #172")&&f.plan.includes("Issue #150")&&f.plan.includes("NOT COMPUTABLE"),"owner/revenue contract");
 return errors;
}
function test(f){
 const baseline=issues(f);if(baseline.length)throw Error("baseline: "+baseline.join(", "));
 let detected=0,undetected=[];
 function mutate(id,fn){const o={...f};fn(o);if(issues(o).length)detected++;else undetected.push(id)}
 let m=JSON.parse(f.matrix);
 for(const field of ["sources","claims","gates"]){for(let i=0;i<m[field].length;i++){
  mutate(field+i+"identity",o=>{let x=JSON.parse(o.matrix);x[field][i][field==="sources"?"url":field==="claims"?"claim":"id"]+="X";o.matrix=JSON.stringify(x)});
  mutate(field+i+"approval",o=>{let x=JSON.parse(o.matrix);x[field][i][field==="sources"?"type":field==="claims"?"classification":"status"]="APPROVED";o.matrix=JSON.stringify(x)});
 }}
 const probes=[
 ["enable preview",o=>o.preview=o.preview.replace('type="button" disabled','type="button"')],
 ["fake-disabled preview",o=>o.preview=o.preview.replace('type="button" disabled','type="button" data-disabled')],
 ["disclosure removal",o=>o.preview=o.preview.replace('id="affiliate-disclosure"','id="no-disclosure"')],
 ["quoted merchant",o=>o.preview+='<a href="https://zen12.com/hnp">buy</a>'],
 ["bare merchant",o=>o.preview+='<a href=https://inspire3.com/>buy</a>'],
 ["extra form",o=>o.preview+='<form><input type=email></form>'],
 ["external script",o=>o.preview+='<script src="https://bad.invalid/x"></script>'],
 ["handler",o=>o.preview=o.preview.replace('<main ', '<main onclick="bad()" ')],
 ["tracking pixel",o=>o.preview+='<style>body{background:url(https://bad.invalid/px)}</style>'],
 ["redirect",o=>o.preview+='<meta http-equiv="refresh" content="0">'],
 ["inherited A enabled",o=>o.a=o.a.replace('type="button" disabled','type="button"')],
 ["inherited B enabled",o=>o.b=o.b.replace('type="button" disabled','type="button"')],
 ["pilot buyer drift",o=>o.b=o.b.replace("Before leaving Final Vestige","After leaving Final Vestige")],
 ["article stripped",o=>o.article=o.article.slice(0,900)],
 ["article primary swapped",o=>o.article=o.article.replace("336 milliseconds","100 milliseconds")],
 ["revenue fabricated",o=>{let x=JSON.parse(o.matrix);x.tracking.net_revenue_per_1000=100;o.matrix=JSON.stringify(x)}],
 ["experiment live false",o=>{let x=JSON.parse(o.matrix);x.experiment.state="LIVE";o.matrix=JSON.stringify(x)}],
 ["Focus replaced",o=>o.preview=o.preview.replace('href="https://finalvestige.com/focus/"','href="/new-form/"')],
 ["index enabled",o=>o.preview=o.preview.replace("noindex,nofollow","index,follow")],
 ["owner swapped",o=>o.plan=o.plan.replace("Issue #150","Issue #999")]
 ];probes.forEach(([id,fn])=>mutate(id,fn));
 if(undetected.length)throw Error("undetected: "+undetected.join(", "));
 return {baseline_violations:baseline.length,unsafe_mutations_detected:detected,missed:undetected.length,mode:"source-only",files:Object.keys(f).length};
}
module.exports={issues,test};
if(typeof require==="function"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const map={matrix:"./EVIDENCE-COMMERCE-GATE-REVENUE-MATRIX.json",preview:"./zen12-attention-buyer-CONVERSION-SOURCE-PREVIEW-UNPUBLISHED.html",article:"./THE-SECOND-NUMBER-VANISHED-ATTENTIONAL-BLINK-UNPUBLISHED.md",plan:"./OFFER-FIT-EXPERIMENT-MEASUREMENT-QA-RELEASE.md",a:"../r234/zen12-A-WHITE-BEAR-TEXT-UNPUBLISHED.html",b:"../r234/zen12-B-WHITE-BEAR-OPTIONAL-VIDEO-CONCEPT-UNPUBLISHED.html"};
 const f=Object.fromEntries(Object.entries(map).map(([k,p])=>[k,fs.readFileSync(path.join(__dirname,p),"utf8")]));
 console.log("R236 RESULT",test(f));
}