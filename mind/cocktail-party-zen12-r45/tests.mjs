// Native Node >=18: node mind/cocktail-party-zen12-r45/tests.mjs
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {validateSyntheticObservation,aggregateSyntheticObservations,recordRealVisitorEvent,LIVE_COLLECTION_ENABLED,MIN_GROUP} from "./privacy-synthetic.mjs";
const root=new URL("./",import.meta.url);
const rd=name=>readFileSync(new URL(name,root),"utf8");
const article=rd("investigation.html"), articleMd=rd("investigation.md");
const a=rd("zen12-text.html"),b=rd("zen12-optional-film.html");
const guide=rd("zen12-guide.md"),hub=rd("mind-hub-review.html");
const matrix=rd("claims-permissions.csv"),poster=rd("poster.svg");
const vtt=rd("film.vtt"),sources=rd("editor-source-register.md");
const privacy=rd("privacy-synthetic.mjs");
let n=0;const ok=(cond,label)=>{assert.ok(cond,label);n++};
const normalized=b.replace(/<aside class="film"[\s\S]*?<\/aside>/,"");
ok(a===normalized,"A/B exact substantive byte identity excluding optional aside");
for (const [name,html] of [["article",article],["A",a],["B",b],["hub",hub]]) {
  ok((html.match(/<h1\b/g)||[]).length===1,name+" unique H1");
  ok(!/<(?:form|iframe|script)\b/i.test(html),name+" no forms/iframes/scripts");
  ok(!/href=["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com)/i.test(html),name+" no merchant href");
  ok(!/<(?:audio|video)[^>]*autoplay| on(?:load|click|error)=/i.test(html),name+" no autoplay attribute or inline handler");
  ok(/:focus-visible/.test(html),name+" focus styling");
  ok(/prefers-reduced-motion/.test(html),name+" reduced-motion");
}
ok(/<button[^>]*disabled[^>]*>/.test(a),"A disabled CTA");
ok(/<button[^>]*disabled[^>]*>/.test(b),"B disabled CTA");
ok(/may receive a commission at no additional cost to you/.test(a),"A adjacent commission language");
ok(/may receive a commission at no additional cost to you/.test(b),"B adjacent commission language");
ok(a.indexOf("may receive a commission")<a.indexOf("offer unavailable"),"disclosure precedes CTA");
ok(b.indexOf("may receive a commission")<b.indexOf("offer unavailable"),"B disclosure precedes CTA");
ok(!/<video\b/.test(b),"B not pretending to host film");
ok(/<aside class="film"/.test(b),"B has original optional film aside");
ok(!/<aside class="film"/.test(a),"A is text-only");
ok(/complete readable transcript/i.test(b),"B transcript");
ok(/src="poster\.svg"/.test(b),"B static poster");
ok(articleMd.split(/\s+/).length>=1700,"long original investigation");
ok(guide.split(/\s+/).length>=1400,"deep guide");
ok(!/Zen12/.test(articleMd),"research content insulated from named seller");
ok(/Wood and Cowan/.test(articleMd)&&/Röer/.test(articleMd),"replication caveat");
ok(/29 percent/.test(articleMd)&&/34\.6%/.test(articleMd),"scoped numbers");
ok(/https:\/\/finalvestige\.com\/focus\//.test(a),"one existing Focus link");
ok(/Puységur/.test(hub),"published archive connected");
ok(/PR #172 remains authoritative/.test(hub),"canonical hub protected");
ok(/72/.test(String(matrix.trim().split("\n").length-1)),"72 permission/evidence rows");
ok(/S12/.test(matrix)&&/S16/.test(matrix),"checkout and health rules");
ok(/https:\/\/zen12\.com\/hnp/.test(sources),"exact merchant page editor-only");
ok(/https:\/\/zen12\.com\/getstarted/.test(sources),"public checkout editor-only");
ok(/^WEBVTT/.test(vtt)&&((vtt.match(/-->/g)||[]).length===6),"timed cue count");
ok(/00:00:40\.000/.test(vtt),"40 second end");
ok(/<svg/.test(poster)&&/viewBox="0 0 540 960"/.test(poster),"original poster SVG");
ok(!LIVE_COLLECTION_ENABLED,"hard off");
ok(MIN_GROUP===20,"small-cell suppression threshold");
ok(!/fetch\(|sendBeacon|localStorage|document\.cookie|XMLHttpRequest/.test(privacy),"no collection or storage");
assert.throws(()=>recordRealVisitorEvent());n++;
const sample={variant:"A",source:"organic",topic:"attention",event:"guide_view"};
ok(validateSyntheticObservation(sample).variant==="A","synthetic valid input");
for (const extra of [{...sample,email:"x@y.org"},{...sample,ip:"127.0.0.1"},{...sample,referrer:"https://x/?secret=x"},{...sample,event:"confirmed_sale"}, {...sample,source:"utm_email"}]) {assert.throws(()=>validateSyntheticObservation(extra));n++}
ok(aggregateSyntheticObservations(Array.from({length:19},()=>sample)).length===0,"suppress n<20");
ok(aggregateSyntheticObservations(Array.from({length:20},()=>sample))[0].count===20,"include n=20");
const dangerous=[
 a.replace(/disabled aria-disabled="true"/,""),
 a.replace(/may receive a commission at no additional cost to you/g,""),
 a.replace("Zen12 offer unavailable — approval pending",'<a href="https://zen12.com/getstarted">BUY</a>'),
 b.replace(/<aside class="film"[\s\S]*?<\/aside>/,"<script>navigator.sendBeacon('/collect')</script>"),
 privacy.replace("LIVE_COLLECTION_ENABLED = false","LIVE_COLLECTION_ENABLED = true")
];
ok(!/<button[^>]*disabled[^>]*>/.test(dangerous[0]),"mutation disabled flag detected");
ok(!/may receive a commission at no additional cost to you/.test(dangerous[1]),"mutation disclosure detected");
ok(/href="https:\/\/zen12\.com/.test(dangerous[2]),"mutation vendor URL detected");
ok(/<script>/.test(dangerous[3]),"mutation script detected");
ok(/LIVE_COLLECTION_ENABLED = true/.test(dangerous[4]),"mutation tracking detected");
console.log("R45 native source/privacy assertions PASS:",n,"; mutation traps: 5/5; buyer merchant hrefs 0; real collection HARD OFF");
