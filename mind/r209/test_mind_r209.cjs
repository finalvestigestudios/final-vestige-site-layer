/** R209 source regression. Run from any cwd: node mind/r209/test_mind_r209.cjs.
 * No network, external packages, login, browser or merchant requests.
 * This runs static source-level checks ONLY; browser/WCAG/Lighthouse/payment remain untested.
 */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=path.resolve(__dirname,"../..");
function read(rel){return fs.readFileSync(path.join(root,rel),"utf8");}
const P={
 A:"mind/r209/zen12-proof-A-TEXT-UNPUBLISHED.html",
 B:"mind/r209/zen12-proof-B-OPTIONAL-42S-UNRENDERED.html",
 M:"mind/r209/claim-source-commercial-gates.json",
 guide:"mind/r209/zen12-the-evidence-not-the-promise-BUYERS-FIELD-GUIDE-UNPUBLISHED.md",
 plan:"mind/r209/CANONICAL-ATTENTION-PAID-CONVERSION-ACCEPTANCE.md",
 R208:"mind/r208/the-second-thing-you-didnt-see-ATTENTIONAL-BLINK-UNPUBLISHED.md",
 R208M:"mind/r208/ATTENTIONAL-BLINK-ZEN12-SOURCE-CLAIM-COMMERCE-GATES.json",
 R207B:"mind/r207/zen12-B-OPTIONAL-42S-UNPUBLISHED.html",
 R207V:"mind/r207/zen12-optional-film-UNRENDERED.vtt"
};
function check(test,message){assert.ok(test,message);}
function filmRemoved(s){return s.replace(/<section class="band" id="optional-film"[\s\S]*?<\/section>/,"").replace(/<title>[\s\S]*?<\/title>/,"<title>normalized</title>");}
function validatePage(s,kind){
 check(s.startsWith("<!doctype html>"),"doctyped HTML");
 check(/<html lang="en">/.test(s),"English declared");
 check(/<meta name="viewport"/.test(s),"mobile viewport");
 check(/<meta name="robots" content="noindex,nofollow"/.test(s),"unpublished noindex");
 check((s.match(/<main\b/g)||[]).length===1,"one main");
 check(/<nav[^>]+aria-label="On this page"/.test(s),"semantic navigation");
 check(/:focus-visible/.test(s),"focus visible");
 check(/prefers-reduced-motion/.test(s),"reduced-motion");
 check(!/<script\b|<iframe\b|<form\b|<video\b|<audio\b|autoplay|<link\b|@import|<img\b/i.test(s),"no JS forms players or remote assets");
 check(!/href=["'][^"']*(?:ref=|affiliate_id|clickbank|hop=|awin1|utm_source=)/i.test(s),"no disguised earning links");
 check((s.match(/<button[^>]*\bdisabled\b/g)||[]).length===1,"one genuinely native-disabled CTA");
 check(/Final Vestige may earn a commission at no additional cost to you/.test(s),"near CTA affiliate language");
 let offer=s.match(/<section class="band" id="decision">([\s\S]*?)<\/section>/);
 check(offer&&offer[1].indexOf("commission")<offer[1].indexOf("<button"),"disclosure placed before purchase control");
 check(/partner approval not verified/.test(s),"CTA withheld for authorization");
 check(/zen12\.com\/hnp/.test(s),"exact official seller is sourced");
 check(/Ingendoh/.test(s)&&/Slagter/.test(s),"independent science");
 check(/finalvestige\.com\/focus/.test(s),"original Focus pathway");
 check(/subscribe before/.test(s)===false,"no subscription pressure");
 if(kind==="B"){check(/optional-film/.test(s),"B adds optional film");check(/Read the complete 42-second script/.test(s),"B transcript");check(/<svg/.test(s)&&/role="img"/.test(s),"B original accessible vector poster");check(/not a playable or rendered video/.test(s),"B clearly unrendered");}
 else{check(!/optional-film/.test(s),"A no film");}
}
function validateMatrix(raw){
 const m=JSON.parse(raw);check(m.claims.length>=19,"substantive claim ledger");check(m.release_gates.length>=9,"release gates");
 const ids=Object.keys(m.source_ids);check(new Set(ids).size===ids.length,"unique source ids");
 check(m.claims.every(c=>c.sources.length&&c.sources.every(id=>id in m.source_ids)),"all claims cite sources");
 check(new Set(m.claims.map(c=>c.id)).size===m.claims.length,"unique claims");
 check(m.release_gates.every(g=>g.status==="OPEN"),"every release gate remains OPEN");
 check(m.merchant_account_status==="NO_AUTHENTICATED_FV_PUBLISHER_APPROVAL","no invented partner acceptance");
 check(m.experiment.status==="DESIGN_ONLY_NOT_RANDOMIZED_NOT_LIVE","experiment not misreported live");
 check(m.experiment.commercial_cta==="NATIVE_DISABLED; NO_EARNING_URL","commerce not active");
 check(m.claims.find(c=>c.id==="10")?.limit.includes("10/12"),"accurate EEG denominator");
 check(m.claims.find(c=>c.id==="03")?.status==="INCONSISTENT_DATED_SELLER_EXTRACTION","price caveat");
}
function validateScience(s,m){
 check(/NONRANDOMIZED, self-selected 17/.test(m),"nonrandom comparison not RCT");
 check(/pooled both groups/.test(m),"pooled P3b association");
 check(/10 practitioners and 12 novices/.test(s),"main EEG sample");
 check(/14 and 20 respectively/.test(s),"expanded sample");
 check(/Across the analyzed practitioners and novices/.test(s),"P3b pooled across groups");
 check(!/Within the trained group, people showing larger reductions/.test(s),"old inaccurate association corrected");
 check(/supplementary research/.test(s)||/SUPPLEMENT TO CANONICAL R196/.test(s),"duplicate canonical warning");
}
function validateFilm(s,v){
 const line="Across 65 studies, the clearest pooled cost concerned reading comprehension; other outcomes were less certain.";
 check(s.includes(line)&&v.includes(line),"same corrected B narration and captions");
 check(!s.includes("Sixty-five reading studies found small average costs")&&!v.includes("Sixty-five reading studies found small average costs"),"old imprecise meta statement removed");
 check(v.startsWith("WEBVTT"),"valid VTT header");
 check((v.match(/\d\d:\d\d:\d\d\.\d{3} -->/g)||[]).length===5,"five timed captions");
}
function validateGuide(s){
 check(/UNPUBLISHED/.test(s),"guide unpublished");
 check(/five reported results consistent/.test(s),"EEG nuance");
 check(/nonrandomized/i.test(s),"retreat design caveat");
 check(/We have not bought, listened to, or medically tested/.test(s),"no firsthand claims");
 check(/no active affiliate earning link/i.test(s),"no affiliate active");
 check(/FTC/.test(s),"FTC source trail");
 check(/source-based purchasing analysis/.test(s),"independent positioning");
 check(/What Twelve Minutes of Meditation Audio Actually Buys/.test(s),"guide title");
 check(/buyer who/.test(s)||/buyer/.test(s),"purchaser intent");
 check(s.trim().split(/\s+/).length>=2200,"deep original product guide");
}
function run(files){
 validatePage(files[P.A],"A");validatePage(files[P.B],"B");
 check(filmRemoved(files[P.A])===filmRemoved(files[P.B]),"identical factual/commerce copy A vs B");
 validateMatrix(files[P.M]);validateScience(files[P.R208],files[P.R208M]);
 validateFilm(files[P.R207B],files[P.R207V]);validateGuide(files[P.guide]);
 check(files[P.plan].includes("NOT COMPUTABLE"),"never turn absent income into zero");
 check(files[P.plan].includes("asset_id"),"creator-asset routing contract");
 check(files[P.plan].includes("canonical"),"duplicate suppression is tracked");
 check(files[P.plan].includes("No changes to protected"),"release governance");
 return "R209 source validation PASS";
}
const data=Object.fromEntries(Object.values(P).map(p=>[p,read(p)]));
let asserts=0;const orig=check; // Test failures must be from the SAME validators as unmodified inputs.
const mutators=[
 [P.A,s=>s.replace(" disabled aria-describedby"," aria-describedby")],
 [P.B,s=>s.replace(" disabled aria-describedby"," aria-describedby")],
 [P.A,s=>s.replace("Final Vestige may earn a commission at no additional cost to you","(disclosure deleted)")],
 [P.B,s=>s.replace("no playable or rendered video","now a live playable video")],
 [P.A,s=>s.replace('<meta name="robots" content="noindex,nofollow">',"")],
 [P.M,s=>s.replace('"NO_AUTHENTICATED_FV_PUBLISHER_APPROVAL"','"APPROVED"')],
 [P.M,s=>s.replace('"status": "OPEN"','"status": "CLOSED"')],
 [P.R208M,s=>s.replace("NONRANDOMIZED, self-selected 17","fully randomized sample 17")],
 [P.R208,s=>s.replace("Across the analyzed practitioners and novices","Within the trained group")],
 [P.R207V,s=>s.replace("Across 65 studies, the clearest pooled cost concerned reading comprehension; other outcomes were less certain.","Sixty-five reading studies found small average costs from sound, especially intelligible words and lyrics.")],
 [P.R207B,s=>s.replace("Across 65 studies, the clearest pooled cost concerned reading comprehension; other outcomes were less certain.","Sixty-five reading studies found small average costs from sound, especially intelligible words and lyrics.")],
 [P.guide,s=>s.replace("We have not bought, listened to, or medically tested","We have bought, listened to, and medically tested")],
 [P.plan,s=>s.replaceAll("NOT COMPUTABLE","$0")]
];
try{
 run(data);
 let caught=0;
 for(const [file,mutate] of mutators){
  let copy={...data,[file]:mutate(data[file])};
  assert.notEqual(copy[file],data[file],"mutation must really change source");
  try{run(copy);}catch(e){caught++;continue;}
  throw new Error("unsafe mutation escaped validation: "+file);
 }
 process.stdout.write("PASS: R209 source checks; "+caught+"/"+mutators.length+" genuine mutated artifacts rejected.\n");
}catch(e){process.stderr.write(e.stack+"\n");process.exitCode=1;}
