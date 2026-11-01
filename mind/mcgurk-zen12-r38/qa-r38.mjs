/**
 * R38 deterministic offline source QA.
 * Native: node mind/mcgurk-zen12-r38/qa-r38.mjs
 * No browser, network, CMS, affiliate links or visitor state accessed.
 * Can be invoked in an isolated V8 using checkWithFiles(map).
 */
export const NEED = [
 "the-syllable-that-wasnt-spoken.md","mcgurk-investigation.wp.html",
 "zen12-evidence-guide.md","zen12-a-text.wp.html","zen12-b-optional-film.wp.html",
 "mind-hub-alternative.wp.html","source-register.tsv","claim-permission-matrix.tsv",
 "mcgurk-film-poster.svg","mcgurk-film-captions.vtt","mcgurk-film-storyboard.md",
 "render-mcgurk.py","attribution-privacy.mjs","navigation-attribution-plan.md","README.md"
];
export function checkWithFiles(files) {
 let pass=0; const failures=[];
 function test(name,ok){if(ok)pass++;else failures.push(name);}
 for(const name of NEED)test("File present: "+name,typeof files[name]==="string"&&files[name].length>80);
 if(failures.length) return {passed:pass,failed:failures};
 const article=files["the-syllable-that-wasnt-spoken.md"];
 const articleHtml=files["mcgurk-investigation.wp.html"];
 const guide=files["zen12-evidence-guide.md"];
 const A=files["zen12-a-text.wp.html"],B=files["zen12-b-optional-film.wp.html"];
 const hub=files["mind-hub-alternative.wp.html"],matrix=files["claim-permission-matrix.tsv"];
 const vtt=files["mcgurk-film-captions.vtt"];
 const attr=files["attribution-privacy.mjs"];
 const source=files["source-register.tsv"];
 const plan=files["navigation-attribution-plan.md"];
 const left="<!-- guide-core-start -->",right="<!-- guide-core-end -->";
 function core(html){if(!html.includes(left)||!html.includes(right))return null;return html.split(left)[1].split(right)[0];}
 const requiredSourceUrls=[
 "https://doi.org/10.1038/264746a0",
 "https://pubmed.ncbi.nlm.nih.gov/25802068/",
 "https://doi.org/10.1371/journal.pone.0207160",
 "https://doi.org/10.3758/s13414-021-02265-6",
 "https://doi.org/10.1371/journal.pone.0286023",
 "https://zen12.com/hnp",
 "https://inspire3.com/",
 "https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance"
 ];
 for(const u of requiredSourceUrls)test("Source in register: "+u,source.includes(u));
 test("article substantial >=1900 words",article.split(/\s+/).length>=1900);
 test("guide substantial >=1800 words",guide.split(/\s+/).length>=1800);
 test("WP article same primary study",articleHtml.includes("10.1038/264746a0"));
 test("investigation retains opposing research",articleHtml.includes("2021")&&articleHtml.includes("2023")&&articleHtml.includes("2018"));
 test("investigation no vendor",!/Zen12|Inspire3|zen12\.com|affiliat(e|ion)/i.test(articleHtml));
 test("investigation no merchant clickable URL",!/href="https:\/\/(?:zen12|inspire3|affiliates\.inspire3)/i.test(articleHtml));
 test("A/B guide core exact same HTML bytes",!!core(A)&&core(A)===core(B));
 test("A video absent",!A.includes("class=\"fv38-film\""));
 test("B poster present",B.includes("mcgurk-film-poster.svg")&&B.includes("<figure"));
 test("B no fake video button",!/<video\b|<iframe\b|autoplay|data-play/i.test(B));
 test("B accessible transcript",B.includes("<details>")&&B.includes("<summary>")&&B.includes("00:34–00:40"));
 for(const [variant,html] of [["A",A],["B",B]]){
  test(variant+" direct disclosure",html.includes("Affiliate disclosure:")&&html.includes("may earn a commission"));
  test(variant+" disclosure directly before disabled action",/Affiliate disclosure:[\s\S]{0,550}<button type="button" disabled aria-disabled="true"/.test(html));
  test(variant+" no active merchant CTA",!/<a[^>]+(?:href="https:\/\/zen12\.com\/(?:getstarted|order|checkout)|data-affiliate|aff_id|hop=|refid=)/i.test(html));
  test(variant+" inert button",html.includes('Merchant link withheld — approval pending</button>'));
  test(variant+" labelled merchant sources",html.includes('aria-label="Seller source; leaves Final Vestige and may lead to checkout"'));
  test(variant+" no new opt in",!/wp-block-jetpack-subscriptions|<form\b|<input\b/i.test(html));
  test(variant+" no autoplay/scripts/iframes",!/<script\b|<iframe\b|autoplay/i.test(html));
  test(variant+" focus-visible and responsive",html.includes(":focus-visible")&&html.includes("@media(max-width:620px)"));
  test(variant+" reduced motion",html.includes("prefers-reduced-motion:reduce"));
  test(variant+" opener safe",!/target="_blank"(?![^>]*rel="noopener noreferrer")/.test(html));
  test(variant+" no seller clinical promises as FV claims",html.includes("does not justify")&&html.includes("did not"));
 }
 test("hub contains four distinct streams",["id=\"perception\"","id=\"suggestion\"","id=\"practice\"","id=\"tools\""].every(s=>hub.includes(s)));
 test("hub published references correct",hub.includes("/2026/08/20/the-hatch-opened-inward-apollo-1/")&&hub.includes("/free-resources/puysegurs-animal-magnetism-files/"));
 test("hub candidate not linked",!hub.includes('href="/mind/the-syllable')&&!hub.includes('href="/mind/zen12'));
 test("hub preserves first-party focus",hub.includes('href="/focus/"')&&!hub.includes("<form"));
 test("matrix at least 40 claims",matrix.trim().split("\n").length>=41);
 test("matrix has evidence and permission gates",matrix.includes("Z26")&&matrix.includes("Z29")&&matrix.includes("Z33")&&matrix.includes("Z43"));
 test("matrix unsubstantiated outcome identified",matrix.includes("one-hour")||matrix.includes("One hour"));
 test("privacy hard off",attr.includes("ENABLED = false")&&attr.includes("emitted:false"));
 test("privacy no network or client storage",!/\bfetch\(|XMLHttpRequest|sendBeacon|localStorage|sessionStorage|document\.cookie/.test(attr));
 test("privacy precise allowlist",attr.includes("Object.keys(candidate).length!==EXACT.length"));
 test("privacy excludes PII fields",attr.includes('const poison=["email","ip","phone"'));
 test("privacy small cohort threshold",attr.includes("n>=minGroup")&&attr.includes("minGroup<10"));
 test("privacy actual synthetic-only API",attr.includes("aggregateSynthetic")&&attr.includes("selfTest"));
 test("source register >=17 entries",source.trim().split("\n").length>=18);
 test("VTT six cues",vtt.split("-->").length-1===6);
 test("VTT final end 40 seconds",vtt.includes("00:00:40.000"));
 test("VTT first start 0",vtt.includes("00:00:00.000 --> 00:00:06.000"));
 test("poster SVG original labelled schematic",files["mcgurk-film-poster.svg"].includes("<svg")&&files["mcgurk-film-poster.svg"].includes("not a real audiovisual experiment"));
 test("render source exactly 40s",files["render-mcgurk.py"].includes("SECONDS=540")===false&&files["render-mcgurk.py"].includes("W,H,FPS,SECONDS=540,960,12,40"));
 test("renderer original only",!files["render-mcgurk.py"].includes("http")&&files["render-mcgurk.py"].includes("SCHEMATIC"));
 test("plan reminds Dispatch no send",plan.includes("HOLD_UNSENT")&&plan.includes("PR #49"));
 // Mutations deliberately simulate plausible unsafe regressions; expected detectors fail.
 const mutations=[
  ["active CTA",A.replace('button type="button" disabled','button type="button" onclick="location.href=\'https://zen12.com/getstarted\'"')],
  ["missing disclosure",A.replace("Affiliate disclosure:","NOTDISCLOSED:")],
  ["autoplay",B.replace("review-only poster","autoplay review-only poster")],
  ["lost captions",B.replace("<details>","<div>")],
  ["lost alt",B.replace('alt="Original illustrative poster','aria-hidden="true" data-note="Original illustrative poster')],
  ["new signup",A.replace("<article","<form><input type=email></form><article")],
  ["new script",A.replace("<article","<script>sendBeacon()</script><article")],
  ["broken core",B.replace("What Zen12 actually includes","What Zen12 excludes")],
  ["missing no-purchase",A.replace("Merchant link withheld — approval pending","Purchase Zen12 now")],
  ["bad disclosure placement",A.replace('<p class="fv38-disclosure">','<p class="fv38-disclosure" hidden>')],
 ];
 const detected=[];
 for(const [name,mutant] of mutations){
  let fail;
  if(name==="active CTA")fail=!mutant.includes('<button type="button" disabled aria-disabled="true"');
  else if(name==="missing disclosure")fail=!mutant.includes("Affiliate disclosure:");
  else if(name==="autoplay")fail=mutant.includes("autoplay");
  else if(name==="lost captions")fail=!mutant.includes("<details>");
  else if(name==="lost alt")fail=!mutant.includes('alt="Original illustrative poster');
  else if(name==="new signup")fail=/<form\b|<input\b/.test(mutant);
  else if(name==="new script")fail=/<script\b/.test(mutant);
  else if(name==="broken core")fail=core(mutant)!==core(A);
  else if(name==="missing no-purchase")fail=!mutant.includes("Merchant link withheld — approval pending");
  else if(name==="bad disclosure placement")fail=!mutant.includes('<p class="fv38-disclosure">');
  detected.push({name,detected:!!fail});
 }
 test("all ten dangerous mutations detected",detected.every(x=>x.detected));
 return {passed:pass,failed:failures,mutations:detected,sourceEntries:source.trim().split("\n").length-1,claimEntries:matrix.trim().split("\n").length-1,guideCoreBytes:core(A)?.length||0};
}
if (typeof process!=="undefined" && process.argv?.[1]?.endsWith("qa-r38.mjs")){
 const fs=await import("node:fs");
 const path=await import("node:path");
 const root=path.dirname(new URL(import.meta.url).pathname);
 const files=Object.fromEntries(NEED.map(f=>[f,fs.readFileSync(path.join(root,f),"utf8")]));
 const result=checkWithFiles(files);
 console.log(JSON.stringify(result,null,2));
 if(result.failed.length)process.exitCode=1;
}
