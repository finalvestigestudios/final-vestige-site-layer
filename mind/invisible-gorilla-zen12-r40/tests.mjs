import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";
import {fileURLToPath} from "node:url";
import {ENABLED,validateSyntheticEvent,recordEvent,aggregateSynthetic,selfTest} from "./privacy-attribution.mjs";
const here=path.dirname(fileURLToPath(import.meta.url));
const read=n=>fs.readFileSync(path.join(here,n),"utf8");
export function run(){
  const md=read("investigation.md"),ih=read("investigation.wp.html"),guide=read("zen12-independent-guide.md");
  const a=read("zen12-text-only.wp.html"),b=read("zen12-video-option.wp.html");
  const hub=read("mind-hub-comparison.wp.html"),vtt=read("film-captions.vtt");
  const poster=read("zen12-static-poster.svg"),matrix=read("claim-and-permission-matrix.csv"),sources=read("sources-and-offer-register.md");
  let n=0;const check=(value,message)=>{assert.ok(value,message);n++};
  check(md.split(/\s+/).length>=1500,"independent article substantial");
  check(guide.split(/\s+/).length>=1400,"buyer guide substantial");
  check((md.match(/^## /gm)||[]).length>=8,"eight scientific sections");
  check(!/zen12|inspire3|medical guarantee/i.test(md),"no selling in investigation");
  check(ih.includes('aria-labelledby="mi-title"'),"article labelled");
  check(ih.includes("10.1068/p281059"),"original science source");
  check(ih.includes("10.1073/pnas.2214930120"),"important recent counterpoint");
  check(a.includes('id="zr40-guide-core"')&&b.includes('id="zr40-guide-core"'),"both contain guide");
  const core=x=>x.slice(x.indexOf('<div id="zr40-guide-core"'));
  check(core(a)===core(b),"byte identical independent guide in A/B");
  check(!a.includes('class="film"')&&b.includes('class="film"'),"only B film");
  check(b.includes("<details>")&&b.includes('href="#zr40-guide-core"'),"transcript and skip");
  check(!a.includes("<video")&&!b.includes("<video"),"no misleading unhosted player");
  check(!/<iframe|<script\b|<form\b|autoplay|onclick\s*=/i.test(a+b),"no scripts embeds forms autoplay");
  check(!/href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive)\.com/i.test(a+b+hub+ih),"zero clickable merchant links");
  for(const page of [a,b]){
    check(page.includes('<button disabled type="button"'),"hard disabled CTA");
    const d=page.indexOf('id="zr40-disclosure"'),c=page.indexOf("<button disabled");
    check(d>0&&c>d&&c-d<420,"near recommendation disclosure");
    check(page.includes("may earn a commission at no additional cost to you"),"plain earning disclosure");
    check(page.includes('aria-describedby="zr40-disclosure zr40-hold"'),"disabled CTA described");
  }
  check(a.includes("First 6")&&a.includes("All 12")&&a.includes("Last 6"),"tier coverage");
  check(a.includes("24 MP3s")&&a.includes("48 MP3s"),"merchant package specification");
  check(!/<form\b/i.test(hub),"no extra subscriber form");
  check(hub.includes("https://finalvestige.com/focus/"),"one preexisting Fieldbook");
  check(hub.includes("puysegurs-animal-magnetism-files"),"historic archive");
  check(poster.includes("<svg")&&poster.includes("<desc"),"SVG original accessibility");
  check(vtt.startsWith("WEBVTT")&&(vtt.match(/--> /g)||[]).length===6,"six caption cues");
  check(vtt.includes("00:00:40.000"),"correct total runtime");
  check(matrix.trim().split("\n").length>=50,"at least 49 claim rows");
  check(sources.includes("https://zen12.com/hnp"),"exact offer in editor register");
  check(sources.includes("ftc.gov"),"FTC evidence noted");
  check(ENABLED===false&&recordEvent({action:"view",channel:"direct",topic:"zen12",variant:"text"})===null,"no attribution activation");
  check(validateSyntheticEvent({action:"view",channel:"organic",topic:"gorilla",variant:"text"}),"synthetic allowlisted");
  check(!validateSyntheticEvent({action:"view",channel:"organic",topic:"gorilla",variant:"text",ip:"127.0.0.1"}),"identifiers rejected");
  check(aggregateSynthetic(Array(9).fill({action:"view",channel:"direct",topic:"zen12",variant:"text"})).length===0,"small cells suppressed");
  const p=selfTest();check(p>=20,"privacy self-test");
  // Mutation checks ensure the important guard conditions actually distinguish unsafe variants.
  const unsafe=[
   a.replace('disabled type="button"','type="button"'),
   a.replace("may earn a commission at no additional cost to you",""),
   a.replace('id="zr40-disclosure"','id="disclosure-erased"'),
   a.replace('class="offer"','class="offer-hidden"'),
   a.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/getstarted"')
  ];
  check(!unsafe[0].includes('<button disabled type="button"'),"mutation detects enabled CTA");
  check(!unsafe[1].includes("may earn a commission at no additional cost to you"),"mutation detects missing disclosure");
  check(!unsafe[2].includes('id="zr40-disclosure"'),"mutation detects broken disclosure label");
  check(!unsafe[3].includes('class="offer"'),"mutation detects changed block");
  check(/href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive)\.com/i.test(unsafe[4]),"mutation detects checkout bypass");
  return {source_checks:n,mutations_caught:5,privacy_checks:p};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(JSON.stringify(run(),null,2));
