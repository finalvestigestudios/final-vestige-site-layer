#!/usr/bin/env node
/** Final Vestige: read-only public-content source parity, never anonymous-browser certification.
 * Usage: node audit_assembler_focus_source_parity.mjs /private/page6.json /private/assembler-header-list.json /private/focus1579.json
 * Input files are local only. No requests, CMS writes, personal data, script installation, or merchant navigation.
 */
import {readFile} from "node:fs/promises";
import {pathToFileURL} from "node:url";
function unwrapPage(resp, id) {
  const x=resp?.structuredContent?.data??resp?.data??resp;
  if(x?.id!==id||x?.status!=="publish"||typeof x?.content!=="string")throw new Error("Published WP page "+id+" required");
  return x;
}
function inspectPage6(resp) {
  const p=unwrapPage(resp,6), h=p.content;
  if(!h.includes("data-fv-home-flagship"))throw new Error("Published flagship markup not found");
  const nav=h.match(/<nav\b[^>]*\bfv-hf__chapter-nav\b[^>]*>[\s\S]*?<\/nav>/i)?.[0]??"";
  const chapterIds=[...nav.matchAll(/<a\b[^>]*href=["']#([^"']+)["']/gi)].map(m=>m[1]);
  const allIds=new Set([...h.matchAll(/\bid=["']([^"']+)["']/gi)].map(m=>m[1]));
  const indexes=[...h.matchAll(/<span\b[^>]*\bfv-margin-strip__item\b[^>]*style=["'][^"']*--i:\s*(\d+)/gi)].map(m=>Number(m[1]));
  const focusTags=[...h.matchAll(/<a\b[^>]*href=["']((?:https:\/\/finalvestige\.com)?\/focus\/?)["'][^>]*>/gi)].map(m=>({at:m.index,href:m[1]}));
  const observerAt=h.indexOf('id="fv-hf-mind-title"');
  const firstFocusAt=focusTags[0]?.at??-1;
  return {id:p.id,modified:p.modified??null,chapter_count:chapterIds.length,seven_chapters_resolve:chapterIds.length===7&&chapterIds.every(id=>allIds.has(id)),margins_count:indexes.length,margins_0_to_71:indexes.length===72&&indexes.every((n,i)=>n===i),focus_links:focusTags.length,focus_within_first_six_chapters:firstFocusAt!==-1&&observerAt!==-1&&firstFocusAt<observerAt,folio_present:h.includes("fv-hf__folio-arrival"),jetpack_block_present:h.includes("jetpack/subscriptions"),dedicated_masthead_focus:h.includes('class="fv-hf__mast-cta"')};
}
function inspectHeader(headerList) {
  const all=Array.isArray(headerList)?headerList:headerList?.data??headerList?.structuredContent?.data;
  if(!Array.isArray(all))throw new Error("Assembler template part list required");
  const header=all.find(x=>x.id==="assembler//header");
  if(!header||typeof header?.content?.raw!=="string")throw new Error("Actual Assembler header template part not found");
  const raw=header.content.raw;
  const navBlocks=[...raw.matchAll(/<!--\s*wp:navigation-link\s+(\{[^\r\n]*\})\s*\/-->/g)].map(m=>{
    try{return JSON.parse(m[1]);}catch{return null}
  }).filter(Boolean);
  const isFocus=(x)=>/^((https:\/\/finalvestige\.com)?\/focus\/?)$/i.test(x||"");
  const focusNav=navBlocks.filter(x=>isFocus(x.url));
  const htmlLinks=[...raw.matchAll(/<a\b[^>]*href=["']([^"']+)["'][^>]*>/gi)].map(x=>x[1]);
  const bannerCount=htmlLinks.filter(isFocus).length;
  return {template_part:header.id,source:header.source??null,nav_focus_count:focusNav.length,nav_focus_label:focusNav[0]?.label??null,html_focus_count:bannerCount,plain_anchor_exists:bannerCount>0,link_destination_canonical:focusNav.length>0&&bannerCount>0};
}
function inspectFocusPage(resp){
  const p=unwrapPage(resp,1579),s=p.content;
  const pdf=[...s.matchAll(/href=["'](https:\/\/finalvestige\.com\/wp-content\/uploads\/[^"']+\.pdf)["']/gi)].map(m=>m[1]);
  return {id:p.id,status:p.status,modified:p.modified??null,jetpack_block_present:s.includes("jetpack/subscriptions"),pdf_link_present:pdf.some(x=>x.includes("Seven_Day_Focus_Fieldbook")),number_of_pdf_links:pdf.length};
}
function reconcile(current,header,focus){
  const sourceChecks={seven_chapters:current.seven_chapters_resolve,margins_72:current.margins_0_to_71,franklin_evidence:current.folio_present,header_focus_nav:header.nav_focus_count>0,header_focus_strip:header.html_focus_count>0,focus_page_published:focus.status==="publish",focus_jetpack_block:focus.jetpack_block_present,focus_pdf_link:focus.pdf_link_present};
  return {release:"HOLD",qualification:"CMS_EDITOR_AND_ASSEMBLER_TEMPLATE_SOURCE_ONLY",source_checks:sourceChecks,source_checks_pass:Object.values(sourceChecks).every(Boolean),page6_modified:current.modified,focus_page_modified:focus.modified,published_page6_focus_links:current.focus_links,page6_focus_before_mind_chapter:current.focus_within_first_six_chapters,assembler_nav_focus_label:header.nav_focus_label,source_parity_finding:"Assembler custom header has both an explicit Focus navigation link and a separate static ebook-strip anchor; absence of candidate-specific mast CTA from Page 6 editor markup is not a proved visitor CTA defect.",required_next:"Anonymous live-header mobile hit-test, overlay/keyboard/no-JS, network images, whole-doc axe, measured Lighthouse; no production changes."};
}
export {inspectPage6,inspectHeader,inspectFocusPage,reconcile};
async function main(){
 const files=process.argv.slice(2);if(files.length!==3)throw new Error("Expected three read-only local JSON paths: Page6, header list, Focus1579");
 const [page,header,focus]=await Promise.all(files.map(async f=>JSON.parse(await readFile(f,"utf8"))));
 const result=reconcile(inspectPage6(page),inspectHeader(header),inspectFocusPage(focus));
 console.log(JSON.stringify(result,null,2));if(!result.source_checks_pass)process.exitCode=1;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(e=>{console.error("HOLD: "+e.message);process.exitCode=1});
