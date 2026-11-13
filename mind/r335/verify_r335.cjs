#!/usr/bin/env node
"use strict";
const fs=require("node:fs");
const path=require("node:path");
const dir=__dirname;
const get=n=>fs.readFileSync(path.join(dir,n),"utf8");
const a=get("ZEN12_A_TEXT_REVIEW.html"),b=get("ZEN12_B_42S_FILM_REVIEW.html"),vtt=get("ZEN12_42S_CAPTIONS.vtt"),m=JSON.parse(get("CLAIMS_AND_AUTHORIZATION.json")),hub=get("MIND_HUB_WP_REVIEW.html"),art=get("THE_TWELVE_MINUTE_QUESTION.md");
let passes=0;const ok=(cond,msg)=>{if(!cond)throw Error("FAIL "+msg);passes++};
const forbidden=/(<script\b|<iframe\b|<form\b|\bautoplay\b\s*=|\bonclick\s*=|<img[^>]+(?:pixel|tracking))/i;
for(const [n,s] of [["A",a],["B",b],["hub",hub]]){ok(!forbidden.test(s),n+" forbidden active element");ok(!/https?:\/\/(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(s),n+" no direct merchant hyperlink/text URL in commercial markup");ok(/<html lang="en">/.test(s),n+" document language");ok(/meta name="viewport"/.test(s),n+" responsive")};
for(const [n,s] of [["A",a],["B",b]]){ok(/<button[^>]+disabled[^>]*>Purchase link not yet authorized<\/button>/.test(s),n+" disabled CTA");ok(/Prospective affiliate disclosure/.test(s),n+" nearby disclosure");ok(s.indexOf("Prospective affiliate disclosure")<s.indexOf("Purchase link not yet authorized"),n+" preceding disclosure");ok(s.includes("Seven Day Focus Fieldbook"),n+" existing single funnel");ok(s.includes("48 MP3s")&&s.includes("24 MP3s"),n+" correct tier");ok(s.includes("none has been validated here"),n+" price caution")};
function mainText(s){return s.replace(/<title>[^<]*<\/title>/,"").replace(/<section class="film"[\s\S]*?<\/section>/,"")};
ok(mainText(a)===mainText(b),"A/B complete substantive content parity, except film and title");
ok(b.includes("Not a playable video"),"film honestly storyboard");
ok(b.includes("<svg")&&b.includes("<desc"),"original accessible SVG");
ok(b.includes("00:35–00:42"),"film transcript complete");
ok((vtt.match(/ --> /g)||[]).length===6,"six caption cues");
ok(vtt.includes("00:00:42.000"),"caption to 42 seconds");
ok(m.claims.length>=20,">=20 classified claims");
ok(m.commercial_gates.length===18&&m.commercial_gates.every(x=>x.status==="UNCLEARED"&&x.evidence===null),"all release gates uncleared");
ok(m.verified_partner_acceptance===false&&m.issued_affiliate_url===null&&m.approved_merchant_url===null,"affiliate hold");
ok(m.net_revenue_per_1000_qualified_humans===null,"no invented KPI");
ok(art.includes("Ziegler")&&art.includes("Fincham")&&art.includes("Ingendoh")&&art.includes("Puységur"),"study + history sources");
ok(hub.includes("History of Suggestion")&&hub.includes("Tools Under Review"),"hub streams");
ok(!/href="https?:\/\/(?:zen12|hypnosislive|brainwaveshots)/i.test(a+b),"no active seller links");
const mutations=[
 ()=>a.replace(" disabled aria-disabled"," aria-disabled"),
 ()=>a.replace("Prospective affiliate disclosure","Hidden disclosure"),
 ()=>a.replace("</body>",'<form action="/collect"><input name="email"></form></body>'),
 ()=>b.replace("Not a playable video","Encoded playable video"),
 ()=>b.replace("00:35–00:42","00:35–00:41"),
 ()=>JSON.stringify({...m,verified_partner_acceptance:true}),
 ()=>JSON.stringify({...m,commercial_gates:m.commercial_gates.map((x,i)=>i===0?{...x,status:"CLEARED"}:x)}),
 ()=>vtt.replace(/00:35:00.000/g,""),
];
const safety=[s=>/<button[^>]+disabled/.test(s),s=>/Prospective affiliate disclosure/.test(s),s=>!/<form/.test(s),s=>/Not a playable video/.test(s),s=>/00:35–00:42/.test(s),s=>JSON.parse(s).verified_partner_acceptance===false,s=>JSON.parse(s).commercial_gates.every(x=>x.status==="UNCLEARED"),s=>(s.match(/ --> /g)||[]).length===6];
mutations.forEach((make,i)=>{const unsafe=make();ok(!safety[i](unsafe),"unsafe mutation rejected "+(i+1))});
process.stdout.write("R335 PASS "+passes+" source assertions; 8 synthetic unsafe mutations rejected. Native source-level only.\n");
