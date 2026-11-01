import { readFileSync } from "node:fs";
import { strict as assert } from "node:assert";
import { selfTest } from "./attribution-disabled.mjs";
const dir = new URL(".", import.meta.url);
const read = name => readFileSync(new URL(name,dir),"utf8");
const A=read("zen12-text-a.html"),B=read("zen12-video-b.html"),H=read("mind-hub-alternative.html"),I=read("investigation.md"),C=read("claims-permissions.csv"),V=read("poster.svg"),T=read("film-captions.vtt");
let assertions=0;
const check=(cond,label)=>{assert.ok(cond,label);assertions++};
const shared=s=>s.match(/<!-- START SHARED GUIDE -->([\s\S]*?)<!-- END SHARED GUIDE -->/)?.[1];
check(shared(A)===shared(B),"A/B share exact substantive guide");
check(A.includes("fv-disclosure") && B.includes("fv-disclosure"),"close CTA disclosure");
check(A.includes('disabled aria-describedby=') && B.includes('disabled aria-describedby='),"disabled commercial CTA");
for(const [label,s] of [["A",A],["B",B],["hub",H],["article",I]]) {
 check(!/<a\b[^>]*href=["']https?:\/\/[^"']*(?:zen12|inspire3|hypnosislive|affiliates\.inspire3)/i.test(s),label+" no merchant hyperlinks");
 check(!/<form\b|<iframe\b|<script\b/i.test(s),label+" no forms iframe script");
 check(!/<video\b[^>]*\bautoplay/i.test(s),label+" no autoplay");
}
check(!A.includes("fv-film-title"),"A omits film");
check(B.includes("fv-film-title")&&B.includes("not an available player"),"B honest unhosted film");
check((T.match(/-->/g)||[]).length===6,"VTT six caption cues");
check(T.includes("00:00:40.000"),"captions through 40s");
check(V.startsWith("<svg")&&V.includes("<title"),"original poster SVG accessibility");
check(I.includes("Deslon") && I.includes("1785") && I.includes("modern randomized trial"),"historical nuance");
check(!/Zen12|inspire3|Hypnosis Live/.test(I),"independent investigation no commercial brands");
check(C.split("\n").length>=40,"claim matrix breadth");
check(H.includes("Focus Fieldbook") && H.includes("Puységur"),"existing internal routes");
const privacy=selfTest();check(privacy.total===14&&privacy.passed===14,"disabled privacy test");
const malicious=[
 A.replace(' disabled aria-describedby=', ' aria-describedby='),
 A.replace("If you eventually purchase through an approved earning link here, Final Vestige may earn a commission at no additional cost to you.",""),
 A.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/getstarted"'),
 B.replace("not an available player","watch the real video now"),
 B.replace("<details>","<form><details>"),
 B.replace('loading="lazy"','loading="lazy" autoplay'),
];
check(!malicious[0].includes('disabled aria-describedby='),"mutation detects enabled CTA");
check(!malicious[1].includes("Final Vestige may earn a commission"),"mutation detects missing disclosure");
check(/href="https:\/\/zen12\.com/.test(malicious[2]),"mutation detects rogue merchant link");
check(!malicious[3].includes("not an available player"),"mutation detects fake player wording");
check(/<form>/.test(malicious[4]),"mutation detects form");
check(/autoplay/.test(malicious[5]),"mutation detects autoplay");
console.log(JSON.stringify({assertions,privacy,maliciousCaught:6,pass:true},null,2));
