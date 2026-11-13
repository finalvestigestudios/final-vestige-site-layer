// Mind R340 source-level acceptance guard. Run: node mind/r340/verify_r340.mjs
// Also run: node --test mind/r340/conversion_metrics.test.mjs
// It is NOT a replacement for browser, WordPress, affiliate, media or settlement testing.
import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";
import {fileURLToPath} from "node:url";
import {computeNetRevenue, validateEvent} from "./conversion_metrics.mjs";
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=n=>fs.readFileSync(path.join(dir,n),"utf8");
const fn=["THE_SECOND_THING_YOU_NEVER_SAW.md","ZEN12_A_TEXT_REVIEW.html","ZEN12_B_FILM_REVIEW.html","ZEN12_42S_POSTER.svg","ZEN12_42S_CAPTIONS.vtt","ZEN12_VIDEO_PRODUCTION.md","MIND_HUB_WORDPRESS_REVIEW_ONLY.html","CLAIM_SOURCE_AUTHORIZATION_MATRIX.json","conversion_metrics.mjs","conversion_metrics.test.mjs","CONVERSION_ATTRIBUTION_AND_RELEASE.md","verify_r340.mjs"];
let assertions=0, rejected=0;
const check=(name, predicate)=>{assert.ok(predicate,name);assertions++};
for (const f of fn)check("file must be source-controlled: "+f,fs.existsSync(path.join(dir,f)));
const article=read(fn[0]),a=read(fn[1]),b=read(fn[2]),poster=read(fn[3]),captions=read(fn[4]),notes=read(fn[5]),hub=read(fn[6]),matrix=JSON.parse(read(fn[7])),dossier=read(fn[10]);
check("original article substantial",article.trim().split(/\s+/).length>=2300);
check("foundational 1992",article.includes("https://pubmed.ncbi.nlm.nih.gov/1500880/"));
check("three-month study",article.includes("three months of intensive mental training"));
check("source-bounded merchant benefit",article.includes("seller representations"));
check("historical source",article.includes("puysegurs-animal-magnetism-files"));
check("FTC source",article.includes("ftc.gov/business-guidance"));
check("Fieldbook retained",article.includes("https://finalvestige.com/focus/"));
check("A/B product tier parity",a.includes("48 MP3s")&&b.includes("48 MP3s")&&a.includes("24 MP3s")&&b.includes("24 MP3s"));
check("A/B evidence disclosure",a.replace(/<[^>]*>/g,"").includes("not a controlled attentional-blink experiment")&&b.replace(/<[^>]*>/g,"").includes("not a controlled attentional-blink experiment"));
check("A/B source link to article",a.includes("THE_SECOND_THING_YOU_NEVER_SAW.md")&&b.includes("THE_SECOND_THING_YOU_NEVER_SAW.md"));
const blockedCommercial=s=>!/<a\b[^>]*href=["'][^"']*(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com|payhip\.com)/i.test(s);
const noActiveCommerce=s=>blockedCommercial(s)&&/<button[^>]*disabled[^>]*>Zen12 merchant offer — not yet verified<\/button>/i.test(s);
check("A withholds all merchant links",noActiveCommerce(a));
check("B withholds all merchant links",noActiveCommerce(b));
const disclose=s=>s.indexOf('Affiliate disclosure for any future merchant recommendation')>0&&s.indexOf('Affiliate disclosure for any future merchant recommendation')<s.indexOf('<button type="button" class="cta"');
check("A disclosure adjacent before disabled CTA",disclose(a));
check("B disclosure adjacent before disabled CTA",disclose(b));
const noRuntime=s=>!/<script\b|<form\b|<iframe\b|<video[^>]*autoplay|<input\b|<img[^>]*src=["']https?:\/\//i.test(s);
check("A no scripts forms embeds autoplay remote image",noRuntime(a));
check("B no scripts forms embeds autoplay remote image",noRuntime(b));
check("A accessible structure",a.includes('lang="en"')&&a.includes('name="viewport"')&&a.includes('scope="col"')&&a.includes(':focus-visible'));
check("B accessible structure",b.includes('lang="en"')&&b.includes('name="viewport"')&&b.includes('scope="row"')&&b.includes(':focus-visible'));
check("B optional film concept",b.includes('class="film"')&&b.includes('<details>')&&b.includes('ZEN12_42S_CAPTIONS.vtt'));
check("A has no film",!a.includes('class="film"'));
const norm=s=>s.replace(/<section class="film"[\s\S]*?<\/section>/,"").replace(/Variant [AB]/g,"Variant X");
check("substantive buyer text identical",norm(a)===norm(b));
check("poster original self-contained",poster.startsWith("<svg")&&!/https?:\/\//.test(poster.replace('http://www.w3.org/2000/svg','')));
check("caption end exactly 42s",captions.includes("00:00:42.000"));
check("caption cues exactly six",(captions.match(/-->/g)||[]).length===6);
check("production does not fake playable video",notes.includes("NOT ENCODED IN GITHUB"));
check("hub four streams",["Perception &amp; Attention","History of Suggestion","Practice &amp; Reflection","Tools Under Review"].every(x=>hub.includes(x)));
check("hub not live page claim",hub.includes("not a WordPress-saved or published page"));
check("hub no new mail signup",noRuntime(hub));
check("matrix 18 primary verified source records",matrix.sources.length>=18);
check("matrix >=30 classified claims",matrix.claims.length>=30);
check("matrix 19 held gates",matrix.release_gates.length===19&&matrix.release_gates.every(g=>g.passed===false));
check("claim includes seller newsletter",matrix.claims.some(c=>c.id==="C11"&&c.status==="seller_page_explicit"));
check("partner acceptance unverified",matrix.claims.some(c=>c.id==="C17"&&c.status==="not_verified"));
check("merchant authorization not verified",matrix.claims.some(c=>c.id==="C18"&&c.status==="not_verified"));
check("money claims not count as revenue",dossier.includes("NOT COMPUTABLE")&&dossier.includes("affiliate_click"));
check("creator IDs honestly absent",dossier.includes("PENDING")&&dossier.includes("Grok"));
check("metric does not convert click to money",!validateEvent({type:"affiliate_click",date:"2026-11-13",asset_id:"fixture_asset",revenue:99}));
check("synthetic unknown financials returns hold",computeNetRevenue({qualifiedHumanSessions:0,grossPaid:0,refunds:0,fees:0,commissions:0}).status==="NOT_COMPUTABLE");
const mutations=[
 ["merchant link",a.replace("Zen12 merchant offer — not yet verified",'<a href="https://zen12.com/checkout">Buy Zen12</a>')],
 ["remove disclosure",a.replace("Affiliate disclosure for any future merchant recommendation","")],
 ["enable commerce",a.replace('class="cta" disabled','class="cta"')],
 ["extra signup",a.replace("</main>",'<form action="/new-list"><input name="email"></form></main>')],
 ["remote pixel",a.replace("</main>",'<img src="https://tracker.example/pixel"></main>')],
 ["arbitrary script",a.replace("</main>",'<script src="https://tracker.example/x.js"></script></main>')]
];
const secure=s=>noActiveCommerce(s)&&disclose(s)&&noRuntime(s);
for(const [label,c] of mutations){assert.equal(secure(c),false,"unsafe mutation should be caught: "+label);rejected++}
console.log(JSON.stringify({result:"PASS",assertions,rejected_mutations:rejected,scope:"Git source-level plus synthetic data",not_done:["browser","WordPress sanitizer","hosted CI","video playback","merchant checkout","affiliate approval","settled revenue"]},null,2));
