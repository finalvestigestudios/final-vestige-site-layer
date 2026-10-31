"use strict";
/**
 * Final Vestige Studios Mind R21 source-gate audit.
 * Reproduce in repository checkout: node mind/attentional-blink-r21/qa.cjs --mutation
 * Tests SOURCE only, not WordPress staging, browsers, sound/caption synchronization, CVW or claims effectiveness.
 * Can also be imported via require('./qa.cjs').audit(files).
 */
const fs = require("fs");
const path = require("path");
const NAMES = [
  "INVESTIGATION.md","CLAIM_PROOF_MATRIX.json",
  "ZEN12_A_TEXT_GUIDE.html","ZEN12_B_OPTIONAL_FILM.html",
  "ZEN12_FILM_POSTER.svg","ZEN12_FILM_CAPTIONS_DRAFT.vtt",
  "MIND_HUB_CANDIDATE.html"
];
function wordcount(s){ return s.replace(/<[^>]+>/g," ").trim().split(/\s+/).filter(Boolean).length; }
function contrast(a,b){
  const ch=h=>[0,2,4].map(i=>parseInt(h.slice(i+1,i+3),16)/255).map(v=>v<=0.04045?v/12.92:Math.pow((v+0.055)/1.055,2.4));
  const lum=h=>ch(h).reduce((v,c,i)=>v+c*[.2126,.7152,.0722][i],0);
  const l=[lum(a),lum(b)].sort((x,y)=>y-x);return (l[0]+.05)/(l[1]+.05);
}
function audit(f){
  const t=[];const ok=(name,pass)=>t.push({name,pass:!!pass});
  const I=f["INVESTIGATION.md"]||"", M=f["CLAIM_PROOF_MATRIX.json"]||"";
  const A=f["ZEN12_A_TEXT_GUIDE.html"]||"",B=f["ZEN12_B_OPTIONAL_FILM.html"]||"";
  const H=f["MIND_HUB_CANDIDATE.html"]||"",P=f["ZEN12_FILM_POSTER.svg"]||"",V=f["ZEN12_FILM_CAPTIONS_DRAFT.vtt"]||"";
  let matrix={sources:{},claims:[],partner:{}};try{matrix=JSON.parse(M)}catch(e){}
  ok("01 substantive 2000+ word investigation",wordcount(I)>=2200);
  ok("02 unique title",I.includes("# The Second Number Vanished"));
  ok("03 1992 primary citation",I.includes("pubmed.ncbi.nlm.nih.gov/1500880"));
  ok("04 2009 theory review",I.includes("pubmed.ncbi.nlm.nih.gov/19933555"));
  ok("05 lag-one sparing nuance",/lag-one sparing/i.test(I)&&/not universal|nor is lag-one sparing universal/i.test(I));
  ok("06 2007 intensive training caveat",I.includes("three months")||I.includes("Three months"));
  ok("07 no claim that original study trialed Zen12",/not a trial of Zen12/i.test(I));
  ok("08 original field exercise properly not a clinical test",I.includes("not an attentional-blink test"));
  ok("09 published Puységur link",I.includes("finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"));
  ok("10 published Focus link",I.includes("finalvestige.com/focus/"));
  ok("11 no merchant purchasing href in investigation",!/<a\s+[^>]*href=["']https?:\/\/(?:zen12|inspire3|affiliates\.)/i.test(I));
  ok("12 FTC disclosure sources included",I.includes("ftc.gov/business-guidance/resources/ftcs-endorsement-guides"));
  ok("13 FTC health sources included",I.includes("ftc.gov/business-guidance/resources/health-products"));
  ok("14 48 matrix claims",Array.isArray(matrix.claims)&&matrix.claims.length===48);
  ok("15 12 source records",Object.keys(matrix.sources||{}).length===12);
  ok("16 unique claim IDs",new Set((matrix.claims||[]).map(x=>x.id)).size===48);
  ok("17 every claim decision",matrix.claims.every(x=>x.statement&&x.status&&x.decision));
  ok("18 source IDs resolve",matrix.claims.every(x=>(x.source_ids||[]).every(y=>matrix.sources[y])));
  ok("19 all source URLs HTTPS",Object.values(matrix.sources||{}).every(x=>/^https:\/\//.test(x.url||"")));
  ok("20 no affiliate URL",matrix.partner?.approved_affiliate_url===null);
  for(const key of ["accepted","acceptance_verified","eligible_skus_verified","tracking_terms_verified","website_rights_verified","email_rights_verified","social_rights_verified","creative_permissions_verified","activation_enabled"])ok("partner OFF "+key,matrix.partner?.[key]===false);
  ok("30 seller one-hour equivalence excluded",matrix.claims.some(x=>x.id==="C27"&&x.status.includes("unsupported")&&x.decision==="exclude"));
  ok("31 automatic brainwave excluded",matrix.claims.some(x=>x.id==="C28"&&x.decision==="exclude"));
  ok("32 commercial tests not presented as achieved",matrix.claims.some(x=>x.id==="C46"&&x.status.includes("not measured")));
  for(const [label,s] of [["A",A],["B",B]]){
    ok(label+" full guide 1200+ words",wordcount(s)>=1200);
    ok(label+" language and viewport",s.includes('<html lang="en">')&&s.includes('name="viewport"'));
    ok(label+" noindex unpublished",s.includes('name="robots" content="noindex,nofollow"'));
    ok(label+" no JS scripts",!/<script\b/i.test(s));
    ok(label+" no signup form",!/<form\b/i.test(s));
    ok(label+" no iframe/merchant analytics",!/<iframe\b/i.test(s)&&!/(?:googletagmanager|google-analytics|facebook\.com\/tr|pixel\.facebook)/i.test(s));
    ok(label+" disclosure",s.includes("Final Vestige may earn a commission at no additional cost to you"));
    ok(label+" inactive purchase control",s.includes('class="disabled-cta" role="note"')&&s.includes("Purchase link withheld"));
    ok(label+" disclosure next to control",/<p class="disclosure">[\s\S]{0,500}<span class="disabled-cta"/.test(s));
    ok(label+" no merchant anchor",!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com)/i.test(s));
    ok(label+" no active purchase button",!/<button\b|<span\b[^>]*href=/i.test(s));
    ok(label+" no autofocus/autoplay",!/(?:autoplay|autofocus)(?:\s|=|>)/i.test(s));
    ok(label+" free practice",s.includes("Minutes 0–2")&&s.includes("Minutes 10–12"));
    ok(label+" source research links",s.includes("pubmed.ncbi.nlm.nih.gov/17488185"));
    ok(label+" link to existing Focus funnel",s.includes("https://finalvestige.com/focus/"));
    ok(label+" accessible focus states",s.includes(":focus-visible"));
    ok(label+" reduced motion",s.includes("prefers-reduced-motion"));
    ok(label+" responsive grid",s.includes("@media(max-width:700px)"));
  }
  ok("A is text only",!A.includes("fv21-film")&&!A.includes("<video"));
  ok("B film section explicit",B.includes('id="fv21-film"')&&B.includes("approximately 40 seconds"));
  ok("B video hidden and src-less",/<video hidden controls preload="none" playsinline[^>]*><\/video>/.test(B));
  ok("B visible transcript",B.includes('class="transcript"')&&B.includes("[32–40s]"));
  ok("B poster text alternative",B.includes('role="img" aria-label='));
  const normalize=s=>s.replace(/Draft [AB]/g,"Draft X").replace(/<section class="panel" id="fv21-film">[\s\S]*?<\/section>/,"");
  ok("A/B substantive editorial content is identical",normalize(A)===normalize(B));
  ok("SVG has title and desc",P.includes("<title")&&P.includes("<desc")&&P.includes('viewBox="0 0 540 960"'));
  ok("SVG does not link to offsite media",!/<image|href=|<script/i.test(P));
  ok("draft VTT proper signature",V.startsWith("WEBVTT"));
  ok("draft VTT no caption overrun",V.includes("00:00:32.000 --> 00:00:40.000")&&!V.includes("00:00:41.000"));
  ok("draft VTT production disclaimer",V.includes("Not synced"));
  ok("hub future draft not live clickable",H.includes("NOT YET LIVE")&&!H.includes('href="/mind/'));
  ok("hub source-first 4 streams",["PERCEPTION &amp; ATTENTION","HISTORY OF SUGGESTION","PRACTICE &amp; REFLECTION","TOOLS UNDER REVIEW"].every(x=>H.includes(x)));
  ok("hub uses published archive and Focus links",H.includes("puysegurs-animal-magnetism-files/")&&H.includes("finalvestige.com/focus/"));
  ok("hub no form/JS/tracking",!/<form\b|<script\b|<iframe\b/i.test(H));
  ok("hub noindex and layout adaptation",H.includes('noindex,nofollow')&&H.includes("@media(max-width:720px)"));
  const cssColor=(s,key)=>{const m=s.match(new RegExp("--"+key+":(#[0-9a-fA-F]{6})"));return m?m[1]:"#000000";};
  for(const [name,fg,bg] of [["article ivory",cssColor(A,"ink"),cssColor(A,"bg")],["bronze label",cssColor(A,"bronze"),cssColor(A,"bg")],["muted body",cssColor(A,"muted"),cssColor(A,"bg")],["CTA text","#d5c5aa","#25231e"],["B headline",cssColor(B,"ink"),cssColor(B,"bg")],["hub headline",cssColor(H,"ink"),cssColor(H,"bg")]])ok("contrast >=4.5:1 "+name,contrast(fg,bg)>=4.5);
  return t;
}
function readFiles(root){return Object.fromEntries(NAMES.map(name=>[name,fs.readFileSync(path.join(root,name),"utf8")]));}
function mutants(f){
 const changes=[
 ["erase commission disclosure","ZEN12_A_TEXT_GUIDE.html",s=>s.replace("Final Vestige may earn a commission at no additional cost to you","Undisclosed compensation")],
 ["enable fake affiliate link","ZEN12_A_TEXT_GUIDE.html",s=>s.replace('class="disabled-cta" role="note"','href="https://zen12.com/getstarted" class="disabled-cta" role="note"')],
 ["insert signup form","ZEN12_A_TEXT_GUIDE.html",s=>s.replace("<main","<form action='/collect'><input name='email'></form><main")],
 ["add tracking pixel","ZEN12_B_OPTIONAL_FILM.html",s=>s.replace("</body>",'<script src="https://google-analytics.com/ga.js"></script></body>')],
 ["enable autoplay","ZEN12_B_OPTIONAL_FILM.html",s=>s.replace("<video hidden controls","<video autoplay hidden controls")],
 ["fake video src","ZEN12_B_OPTIONAL_FILM.html",s=>s.replace("controls preload","controls src='https://cdn.example.invalid/ad.mp4' preload")],
 ["erase B transcript","ZEN12_B_OPTIONAL_FILM.html",s=>s.replace('class="transcript"','class="missing"')],
 ["erase B poster alternative","ZEN12_B_OPTIONAL_FILM.html",s=>s.replace('role="img" aria-label=','role="presentation" data-label=')],
 ["change B editorial content","ZEN12_B_OPTIONAL_FILM.html",s=>s.replace("forty-eight","forty-seven")],
 ["reveal affiliate URL","CLAIM_PROOF_MATRIX.json",s=>s.replace('"approved_affiliate_url": null','"approved_affiliate_url": "fake"')],
 ["set partner authorization true","CLAIM_PROOF_MATRIX.json",s=>s.replace('"activation_enabled": false','"activation_enabled": true')],
 ["weaken unsupported claim gate","CLAIM_PROOF_MATRIX.json",s=>s.replace('"id": "C27",','"id": "C27a",')],
 ["remove 2007 study caveat","INVESTIGATION.md",s=>s.replace("not a trial of Zen12","a trial of Zen12")],
 ["remove original research citation","INVESTIGATION.md",s=>s.replace("pubmed.ncbi.nlm.nih.gov/1500880","source-not-found")],
 ["erase VTT signature","ZEN12_FILM_CAPTIONS_DRAFT.vtt",s=>s.replace("WEBVTT","CAPTIONS")],
 ["remove SVG alt description","ZEN12_FILM_POSTER.svg",s=>s.replace("<desc","<x-desc")],
 ["break hub intro link","MIND_HUB_CANDIDATE.html",s=>s.replace("finalvestige.com/focus/","invalid.invalid/focus/")],
 ["break contrast","ZEN12_A_TEXT_GUIDE.html",s=>s.replace("--ink:#f4efe6","--ink:#303030")]
 ];
 return changes.map(([name,file,change])=>{
   const g={...f,[file]:change(f[file])};
   return {name,caught:audit(g).some(x=>!x.pass)};
 });
}
if(require.main===module){
 const root=__dirname; const f=readFiles(root), checks=audit(f);
 console.log(JSON.stringify({checked:new Date().toISOString(),pass:checks.filter(x=>x.pass).length,total:checks.length,failures:checks.filter(x=>!x.pass)},null,2));
 if(process.argv.includes("--mutation")){const m=mutants(f);console.log(JSON.stringify({mutation_caught:m.filter(x=>x.caught).length,total:m.length,missed:m.filter(x=>!x.caught)},null,2));if(m.some(x=>!x.caught))process.exitCode=2;}
 if(checks.some(x=>!x.pass))process.exitCode=1;
}
module.exports={audit,mutants,NAMES};
