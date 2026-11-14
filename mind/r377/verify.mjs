// Offline source-only checks for FV Mind R377.
// Run: node mind/r377/verify.mjs
// No network, no merchant links, no CMS actions, no analytics, no paid dependencies.
import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";
import {fileURLToPath} from "node:url";
const dir=path.dirname(fileURLToPath(import.meta.url));
const get=name=>fs.readFileSync(path.join(dir,name),"utf8");
const article=get("THE_GORILLA_IN_THE_SCAN.md");
const a=get("ZEN12_A_TEXT_GUIDE.html");
const b=get("ZEN12_B_OPTIONAL_FILM_GUIDE.html");
const hub=get("MIND_HUB_WORDPRESS_SOURCE_ONLY.html");
const poster=get("ORIGINAL_42S_POSTER.svg");
const vtt=get("ORIGINAL_42S_CAPTIONS.vtt");
const memo=get("CONVERSION_ACCEPTANCE_AND_HANDOFF.md");
const claims=JSON.parse(get("CLAIM_SOURCE_RIGHTS_MATRIX.json"));
const figure=/<figure id="optional-film"[^>]*>[\s\S]*?<\/figure>/;
const offer=html=>html.match(/<section class="offer" id="offer">[\s\S]*?<\/section>/)?.[0]||"";
const merchantHref=/<a\b[^>]*href\s*=\s*["']\s*https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)(?:[\/"'?\s]|$)/i;
const nativeButton=/<button\b(?=[^>]*\btype="button")[^>]*\sdisabled(?:\s|>|=)/i;
function safeBuyer(html){
 const block=offer(html);
 return html.startsWith("<!doctype html>") &&
  /<html lang="en">/.test(html) &&
  /name="robots" content="noindex,nofollow,noarchive"/.test(html) &&
  /name="viewport"/.test(html) &&
  /name="referrer" content="no-referrer"/.test(html) &&
  /Content-Security-Policy/.test(html) &&
  !/<(?:script|iframe|form|input|audio|video)\b/i.test(html) &&
  !merchantHref.test(html) &&
  !/\b(?:autoplay|onerror|onclick|onload)\b\s*=/i.test(html) &&
  !/<(?:link|meta)\b[^>]*(?:pixel|preconnect|preload)/i.test(html) &&
  nativeButton.test(block) &&
  block.indexOf('class="disclosure"')>0 &&
  block.indexOf('class="disclosure"')<block.indexOf('<button') &&
  block.includes("may earn a commission at no additional cost to you") &&
  block.includes("publisher acceptance") &&
  html.includes("https://finalvestige.com/focus/");
}
let passed=0;
const check=(label,yes)=>{assert.ok(yes,label);passed++;};
check("original article at least 2000 words",article.trim().split(/\s+/).length>=2000);
for(const fragment of ["Twenty of the twenty-four","https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/","https://doi.org/10.1068/p281059","puysegurs-animal-magnetism-files","https://finalvestige.com/focus/","not proof that an MP3"])check("article required "+fragment,article.toLowerCase().includes(fragment.toLowerCase()));
check("A independent inactive buyer guide",safeBuyer(a));
check("B independent inactive buyer guide",safeBuyer(b));
check("A/B meaningful source parity after optional film",b.replace(figure,"")===a);
check("B optional film inserted once",(b.match(figure)||[]).length===1);
check("B poster referenced",b.includes('src="ORIGINAL_42S_POSTER.svg"'));
check("B full narrated transcript",b.includes("What you search for can shape what you notice."));
check("B clearly not playable",b.includes("not playable media"));
check("B contains no active video tag",!/<video\b/i.test(b));
check("original poster SVG",poster.startsWith("<svg")&&poster.includes("Original abstract")&&poster.includes('viewBox="0 0 960 540"'));
check("VTT header",vtt.startsWith("WEBVTT\n"));
check("VTT six cues",(vtt.match(/-->/g)||[]).length===6);
check("VTT exact duration",vtt.includes("00:00:42.000"));
check("VTT clean text",!/<(?:script|img|iframe)\b/i.test(vtt));
check("hub accessible markup",hub.startsWith("<!doctype html>")&&hub.includes("lang=\"en\"")&&hub.includes('name="viewport"'));
check("hub noindex",hub.includes("noindex,nofollow,noarchive"));
check("hub no merchant/link/script/form",!merchantHref.test(hub)&&!/<(?:script|form|iframe|video)\b/i.test(hub));
for(const stream of ["Perception &amp; Attention","History of Suggestion","Practice &amp; Reflection","Tools Under Review"])check("hub stream "+stream,hub.includes(stream));
for(const route of ["https://finalvestige.com/2026/11/02/change-blindness/","https://finalvestige.com/2026/11/02/mesmerism/","https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/","https://finalvestige.com/focus/"])check("hub existing route "+route,hub.includes(route));
check("matrix schema",claims.schema==="fv-mind-r377-claims/1.0");
check("matrix 28 claims",claims.claims.length===28);
check("matrix 14 sources",Object.keys(claims.sources).length===14);
check("matrix 32 commercial gates",claims.commercial_gates.length===32);
check("matrix all closed and null evidence",claims.commercial_gates.every(x=>x.status==="HOLD"&&x.evidence===null));
check("no active merchant links in matrix",claims.audits.active_affiliate_urls===0&&claims.audits.activated_links===0);
check("seller efficacy unsupported",claims.claims.find(x=>x.id==="P15")?.status==="unsupported for product");
check("publisher authorization not verified",claims.claims.find(x=>x.id==="A20")?.status==="not verified");
check("owned product not verified",claims.claims.find(x=>x.id==="A21")?.status==="not verified");
check("memo 7/30 day cohorts",memo.includes("7/30-day"));
check("memo exact media ID gate",memo.includes("immutable platform media identifier"));
check("memo distinction from sales",memo.includes("NOT")&&memo.includes("merchant_confirmed_paid_order"));
check("memo no CMS changes",memo.includes("no CMS write"));
const attacks=[
["enabled button",a.replace('type="button" disabled','type="button"')],
["aria disabled only",a.replace('type="button" disabled','type="button" aria-disabled="true"')],
["removed disclosure",a.replace('<p class="disclosure">','<p class="disclosure-removed">')],
["live seller link",a.replace('The exact public seller page','<a href="https://zen12.com/">BUY</a> The exact public seller page')],
["active affiliate link",a.replace('What Zen12 Premium','<a href="https://affiliates.inspire3.com/abc">buy</a> What Zen12 Premium')],
["script",a.replace('</body>','<script>console.log(1)</script></body>')],
["iframe",a.replace('</main>','<iframe src="https://example.test/x"></iframe></main>')],
["new form",a.replace('</main>','<form><input name="email"></form></main>')],
["indexable",a.replace("noindex,nofollow,noarchive","index,follow")],
["autoplay",a.replace("</main>",'<video autoplay></video></main>')],
["handler",a.replace('</main>','<div onclick="go()">X</div></main>')]
];
for(const [name,bad] of attacks)check("unsafe mutation rejected: "+name,!safeBuyer(bad));
check("A/B differential guard",b.replace(figure,"")===a && b.replace(/<figure[\s\S]*?<\/figure>/,"")===a);
console.log("R377 source-only verifier PASS: "+passed+"/"+passed+" checks; "+attacks.length+" unsafe buyer mutations rejected; no merchant/production operations.");
