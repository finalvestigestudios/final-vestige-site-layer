// Final Vestige Studios — Library only. Read-only local audit of a Gutenberg content export.
// Usage: node scripts/editorial/check-research-sources-runtime-surface.mjs <raw-content.txt> --expect=published|staging
// Never connects to WordPress or publishes. This is NOT a browser/accessibility verdict.
import {readFileSync} from "node:fs";

function audit(raw,expect){
  const itemRx=/<article class="fv-rs-card" data-cat="([^"]+)"[^>]*>[\s\S]*?<h3>([\s\S]*?)<\/h3>[\s\S]*?<a href="([^"]+)"([^>]*)>/g;
  const cards=Array.from(raw.matchAll(itemRx),m=>({category:m[1],title:m[2].replace(/<[^>]+>/g,"").trim(),url:m[3],anchorAttrs:m[4]}));
  const first=raw.split("<!-- /wp:html -->")[0]||"";
  const second=raw.slice(raw.indexOf('id="fv-rs-batch003"'));
  const categories=Object.fromEntries(["declassified","accountability","engineering","archives","navigation"].map(cat=>[cat,cards.filter(c=>c.category===cat).length]));
  const filters=Object.fromEntries(Array.from(first.matchAll(/<button[^>]+data-filter="([^"]+)"[^>]*>[\s\S]*?<span>(\d+)<\/span><\/button>/g),m=>[m[1],Number(m[2])]));
  const scripts=Array.from(raw.matchAll(/<script>([\s\S]*?)<\/script>/g),m=>m[1]);
  const countLabel=Number((first.match(/Search all (\d+) sources/)||[])[1]||0);
  const stat=Number((first.match(/<div class="fv-rs-stats"[\s\S]*?<b>(\d+)<\/b>/)||[])[1]||0);
  const hard=[];
  if(cards.length!==90)hard.push("90 card count mismatch");
  if(new Set(cards.map(c=>c.title)).size!==90)hard.push("duplicate or absent titles");
  if(new Set(cards.map(c=>c.url)).size!==90)hard.push("duplicate or absent destinations");
  if(JSON.stringify(categories)!==JSON.stringify({declassified:12,accountability:24,engineering:21,archives:25,navigation:8}))hard.push("actual category inventory changed");
  if((first.match(/class="fv-rs-card"/g)||[]).length!==60||(second.match(/class="fv-rs-card"/g)||[]).length!==30)hard.push("60+30 independent fallback blocks changed");
  if(countLabel!==expect||stat!==expect||filters.all!==expect)hard.push("static 60/90 label mismatch for selected mode");
  if(cards.some(c=>!/^https:\/\//.test(c.url)||!/target="_blank"/.test(c.anchorAttrs)||!/noopener/.test(c.anchorAttrs)||!/noreferrer/.test(c.anchorAttrs)))hard.push("source URL scheme or outbound rel protection missing");
  const warnings=[];
  if(!/<noscript\b/i.test(raw))warnings.push("No noscript guidance; search/filter controls stay visible but inert without JavaScript");
  if(scripts.filter(s=>s.includes("search.addEventListener('input'")).length>1)warnings.push("Two independent input listeners operate on the same search control (60 and 90-card passes)");
  if(raw.includes(".fv-rs-filters button span{display:none}"))warnings.push("CSS hides all numeric filter spans, including corrected category totals");
  if(/<div class="fv-rs-filters" aria-label=/.test(raw)&&!/<div class="fv-rs-filters"[^>]*role="group"/.test(raw))warnings.push("Filter div carries aria-label without explicit grouping role");
  if(expect===90 && Object.entries({...categories,all:90}).some(([k,v])=>filters[k]!==v))hard.push("static filter totals contradict 90-card inventory");
  return {mode:expect===90?"staging":"published",cards:cards.length,uniqueTitles:new Set(cards.map(c=>c.title)).size,uniqueUrls:new Set(cards.map(c=>c.url)).size,firstBlockCards:(first.match(/class="fv-rs-card"/g)||[]).length,fallbackCards:(second.match(/class="fv-rs-card"/g)||[]).length,categories,filters,searchLabelCount:countLabel,summaryStatCount:stat,scriptCount:scripts.length,hardFailures:hard,warnings,verdict:hard.length?"FAIL":"PASS_STATIC_STRUCTURE_ONLY",browserTested:false,sourceRightsVerifiedByThisTool:false};
}

const args=process.argv.slice(2);
const path=args.find(a=>!a.startsWith("--"));
const mode=args.find(a=>a.startsWith("--expect="))?.split("=")[1];
if(!path||!["published","staging"].includes(mode)){
  process.stderr.write("Usage: node check-research-sources-runtime-surface.mjs <raw-content.txt> --expect=published|staging\\n");
  process.exit(2);
}
const result=audit(readFileSync(path,"utf8"),mode==="published"?60:90);
process.stdout.write(JSON.stringify(result,null,2)+"\\n");
process.exit(result.hardFailures.length?1:0);
