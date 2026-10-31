/* Mind R22 source-content auditor. No dependencies. Run:
   node mind/suggestion-memory-r22/qa.cjs
   node mind/suggestion-memory-r22/qa.cjs --mutation
   Can also be imported and run against authenticated GitHub byte readbacks. */
"use strict";
function contrast(fg,bg){
  const v=x=>{const n=parseInt(x,16)/255;return n<=0.04045?n/12.92:((n+0.055)/1.055)**2.4;};
  const lum=h=>{const a=[h.slice(1,3),h.slice(3,5),h.slice(5,7)].map(v);return .2126*a[0]+.7152*a[1]+.0722*a[2];};
  const a=lum(fg),b=lum(bg);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
}
function getCsvRows(s){return s.trim().split(/\r?\n/).slice(1).filter(Boolean);}
function removeVideo(s){return s.replace(/<section class="video-concept"[\s\S]*?<\/section>/,"\n");}
function audit(d){
 const out=[]; const check=(name,ok)=>out.push({name,pass:!!ok});
 const A=d.A||"",B=d.B||"",article=d.article||"",hub=d.hub||"",matrix=d.matrix||"",vtt=d.vtt||"",measurement=d.measurement||"",readiness=d.readiness||"",totalFocus=d.totalFocus||"";
 const pos=(s,x)=>s.indexOf(x);
 const buttons=(s)=>(s.match(/<button\b[^>]*>/g)||[]);
 const near=(s)=>{const i=pos(s,'class="disclosure"'),j=pos(s,'class="pending"');return i>0&&j>i&&(j-i)<1000;};
 const rows=getCsvRows(matrix);
 check("A independent full guide",A.length>14000&&A.includes("The pause you can actually keep."));
 check("B independent full guide",B.length>16500&&B.includes("The pause you can actually keep."));
 check("A/B editorial identical except film",A===removeVideo(B));
 check("A disclosure near disabled control",near(A));
 check("B disclosure near disabled control",near(B));
 check("Both exactly one disabled purchase control",[A,B].every(s=>buttons(s).length===1&&buttons(s)[0].includes("disabled")));
 check("No active merchant purchasing anchors",[A,B].every(s=>!/<a[^>]+(href="https:\/\/zen12.com\/getstarted")[^>]*>\s*(buy|purchase|unlock|visit|view offer)/i.test(s)));
 check("No affiliate parameters or redirected shopping URL",[A,B].every(s=>!/([?&](ref|aff|aid|tag|subid|utm_campaign|hop)=|bit\.ly|tinyurl\.com)/i.test(s)));
 check("No new collection form",[A,B,hub].every(s=>!/<form\b/i.test(s)));
 check("No active third-party embed or script",[A,B,hub].every(s=>!/<script\b|<iframe\b/i.test(s)));
 check("No JS event handler attributes",[A,B,hub].every(s=>!/<[a-z][^>]*\s(onclick|onload|onerror|onmouseenter)\s*=/i.test(s)));
 check("No autoplay media",[A,B].every(s=>!/<(video|audio)[^>]+\bautoplay\b/i.test(s)));
 check("No fake video controls",!/<video\b/i.test(B)&&!/<video\b/i.test(A));
 check("B poster and fully visible transcript",B.includes('<svg viewBox="0 0 600 330"')&&B.includes('<details open>')&&B.includes("0–40")===false&&B.includes("34–40s."));
 check("A excludes video concept",!A.includes('class="video-concept"'));
 check("B has optional film concept",B.includes('class="video-concept"'));
 check("Both are WordPress HTML fragments",[A,B,hub].every(s=>s.startsWith("<!-- wp:html -->")&&s.trimEnd().endsWith("<!-- /wp:html -->")));
 check("Both seller exact About + checkout + Inspire3",[A,B].every(s=>s.includes("https://zen12.com/about")&&s.includes("https://zen12.com/getstarted")&&s.includes("https://inspire3.com/")));
 check("Both cite FTC and NCCIH",[A,B].every(s=>s.includes("www.ftc.gov/business-guidance/resources/health-products-compliance-guidance")&&s.includes("www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety")));
 check("Both preserve existing Focus route",[A,B,article,hub,totalFocus].every(s=>s.includes("https://finalvestige.com/focus/")));
 check("No invented unique results/commissions",[A,B].every(s=>!/(my experience using Zen12|we tested the MP3|guaranteed results)/i.test(s)));
 check("Investigation is substantial",article.split(/\s+/).length>1800);
 check("Investigation cites experiments + 1843 primary",article.includes("Loftus")&&article.includes("Braid")&&article.includes("Wellcome")&&article.includes("Scoboria"));
 check("Investigation no commercial product CTA",!/<a[^>]+href="https:\/\/(zen12\.com|hypnosislive\.com)/i.test(article));
 check("Hub no live false guide links",!hub.includes('href="/mind/the-memory')&&!hub.includes('href="/mind/tools/'));
 check("Hub preserves published Puy route",hub.includes("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"));
 check("Total Focus independent long guide",totalFocus.split(/\s+/).length>1100&&totalFocus.includes("33-minute")&&totalFocus.includes("47-MB"));
 check("Total Focus no active earning link",totalFocus.includes("NOT ACTIVE")&&totalFocus.includes("no affiliate purchase link"));
 check("Claim matrix source/decision column",matrix.startsWith("id,claim,status,evidence_type,editorial_decision,source_url"));
 check("Claim matrix >=50 item rows",rows.length>=50);
 check("Matrix records merchant approval missing",matrix.includes("Authorized Final Vestige merchant account")&&matrix.includes("missing_permission"));
 check("Matrix records FTC guidance",matrix.includes("FTC Q&A")&&matrix.includes("FTC health guidance"));
 check("Matrix does not assert universal EEG proof",matrix.includes("Binaural entrainment EEG evidence mixed"));
 check("Video VTT bounded to 40s",vtt.startsWith("WEBVTT")&&vtt.includes("00:00:40.000")&&vtt.includes("DRAFT"));
 check("Video readiness explicitly no hosted player",readiness.includes("not an activated video")&&readiness.includes("separate founder signoff"));
 let m={};try{m=JSON.parse(measurement);}catch{}
 check("Analytics default OFF",m.enabled===false&&m.deploy===false);
 check("Analytics no user identifiers",Array.isArray(m.forbidden_fields)&&m.forbidden_fields.includes("user_id")&&m.forbidden_fields.includes("IP"));
 check("Analytics no active tracking destination",!measurement.includes("https://analytics.")&&!measurement.includes("api_key"));
 check("Anonymous denominator clear",measurement.includes("NOT unique visitors")&&measurement.includes("page-render"));
 check("Contextual affiliate disclosure appears before CTA",[A,B].every(s=>pos(s,"If an authorized earning link")>=0&&pos(s,"If an authorized earning link")<pos(s,'class="pending"')));
 check("No relative hidden assets / media src",[A,B].every(s=>!/<video[^>]*src=|<track[^>]*src=/i.test(s)));
 check("No unexplained live merchant price or commission",[A,B].every(s=>!/(\$[0-9]+|[0-9]+% commission|60%\+)/.test(s)));
 check("Text/background WCAG AA contrast",contrast("#dad3c7","#090a0a")>=4.5);
 check("Muted/background WCAG AA contrast",contrast("#ada79c","#090a0a")>=4.5);
 check("Golden links/background WCAG AA contrast",contrast("#edcc96","#090a0a")>=4.5);
 check("Gold tag/panel contrast",contrast("#c7a66c","#111312")>=4.5);
 return {pass:out.filter(x=>x.pass).length,total:out.length,failed:out.filter(x=>!x.pass),checks:out};
}
function mutants(d){
 const bad=[
 ["remove A disclosure",{...d,A:d.A.replace(/<p class="disclosure">[\s\S]*?<\/p>/,"")}],
 ["enable B purchase button",{...d,B:d.B.replace("type=\"button\" disabled aria-disabled=\"true\"","type=\"button\"")}],
 ["inject tracking script",{...d,A:d.A.replace("</section>\n<!-- /wp:html -->","<script src=\"https://tracker.example/a.js\"></script></section>\n<!-- /wp:html -->")}],
 ["duplicate signup form",{...d,hub:d.hub.replace("</section>\n<!-- /wp:html -->","<form><input type=\"email\"></form></section>\n<!-- /wp:html -->")}],
 ["autoplay video",{...d,B:d.B.replace("<!-- Activation gated.","<video autoplay controls src=\"track.mp4\"></video><!-- Activation gated.")}],
 ["remove video transcript",{...d,B:d.B.replace(/<details open>[\s\S]*?<\/details>/,"")}],
 ["activate measurement",{...d,measurement:d.measurement.replace('"enabled": false','"enabled": true')}],
 ["remove evidence rows",{...d,matrix:d.matrix.split("\n").slice(0,20).join("\n")}],
 ["insert guessed affiliate URL",{...d,A:d.A.replace("Zen12 product link — awaiting approval","<a href=\"https://zen12.com/getstarted?aff=guessed\">Buy now</a>")}]
 ];
 return bad.map(([name,x])=>({name,caught:audit(x).failed.length>0}));
}
module.exports={audit,mutants,contrast};
if(typeof require!=="undefined"&&require.main===module){
 const fs=require("node:fs"),path=require("node:path");
 const base=__dirname;
 const read=f=>fs.readFileSync(path.join(base,f),"utf8");
 const d={A:read("zen12-guide-A.wp.html"),B:read("zen12-guide-B.wp.html"),article:read("investigation.md"),totalFocus:read("hypnosis-live-total-focus-guide.md"),hub:read("mind-hub-candidate.wp.html"),matrix:read("claim_matrix.csv"),vtt:read("zen12-40s-DRAFT.vtt"),readiness:read("video-readiness.md"),measurement:read("measurement-OFF.json")};
 const r=audit(d);console.log("Mind R22 audit",r.pass+"/"+r.total,r.failed);let bad=[];if(process.argv.includes("--mutation")){bad=mutants(d);console.log("Mutations caught",bad.filter(x=>x.caught).length+"/"+bad.length,bad);}if(r.failed.length||bad.some(x=>!x.caught))process.exitCode=1;
}
