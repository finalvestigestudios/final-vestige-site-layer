/**
 * Final Vestige Library / Research Sources — guarded staging repair.
 * DRY-RUN TOOL ONLY. This script neither authenticates to WordPress nor publishes.
 *
 * Input JSON: {page_id:1338,page_modified:"...",page_content:"...",
 *              library_id:77,library_modified:"...",library_content:"..."}
 * Usage: node scripts/editorial/reconcile-research-sources-90.mjs export.json staged.json
 */
import {readFileSync, writeFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';

const EXPECTED = Object.freeze({
  page: {id:1338,modified:'2026-11-03T22:12:43'},
  library: {id:77,modified:'2026-11-07T19:39:01'},
  counts: {declassified:12,accountability:24,engineering:21,archives:25,navigation:8}
});
const PAGE_REPLACEMENTS = [
  ['Sixty free collections, reports','Ninety free collections, reports'],
  ['<b>60</b><span>curated sources','<b>90</b><span>curated sources'],
  ['Search all 60 sources','Search all 90 sources'],
  ['All <span>60</span>','All <span>90</span>'],
  ['Declassified &amp; decisions <span>9</span>','Declassified &amp; decisions <span>12</span>'],
  ['Accountability &amp; public records <span>18</span>','Accountability &amp; public records <span>24</span>'],
  ['Engineering, disaster &amp; safety <span>16</span>','Engineering, disaster &amp; safety <span>21</span>'],
  ['Archives, maps &amp; research <span>12</span>','Archives, maps &amp; research <span>25</span>'],
  ['Navigation &amp; preservation <span>5</span>','Navigation &amp; preservation <span>8</span>'],
  ['Showing all 60 sources.','Showing all 90 sources.'],
  ["A record-group discovery tool that makes digitization gaps visible: NARA’s June 2026 baseline reports 475,127,595 scans, about 3.87% of estimated textual holdings represented there.",
   "Explore record-group scan coverage against estimated textual pages. NARA updates these estimates monthly; they do not measure how many records survive or whether a specific file is accessible."],
  ["' of 60 source'","' of 90 source'"],
  ['const totals={all:90,declassified:12,accountability:23,engineering:21,archives:26,navigation:8};',
   'const totals={all:90,declassified:12,accountability:24,engineering:21,archives:25,navigation:8};']
];
const LIBRARY_REPLACEMENTS = [
  ['Sixty free, first-party or institutionally maintained sources',
   'Ninety free, first-party or institutionally maintained sources'],
  ['60 curated sources · 8 research families · Link-out access',
   '90 curated sources · 5 research paths · Link-out access']
];
export function replaceOnce(source, before, after) {
  const hits = source.split(before).length - 1;
  if (hits !== 1) throw new Error('guard failed: expected one occurrence, found '+hits+' of '+JSON.stringify(before));
  return source.replace(before, after);
}
export function cards(source) {
  return [...source.matchAll(/<article class="fv-rs-card" data-cat="([^"]+)">([\s\S]*?)<\/article>/g)].map(m=>({
    category:m[1],
    title:(m[2].match(/<h3>([^<]*)<\/h3>/)||[])[1]||'',
    href:(m[2].match(/<a href="([^"]+)"/)||[])[1]||''
  }));
}
export function stage(input) {
  if (input.page_id!==EXPECTED.page.id || input.library_id!==EXPECTED.library.id) throw new Error('guard failed: unexpected WordPress IDs');
  if (input.page_modified!==EXPECTED.page.modified || input.library_modified!==EXPECTED.library.modified) throw new Error('guard failed: WordPress revision changed; re-audit the live source before staging');
  const page = input.page_content, lib = input.library_content;
  if(typeof page !== 'string' || typeof lib !== 'string')throw new Error('missing WordPress raw markup');
  const before=cards(page);
  if(before.length!==90)throw new Error('guard failed: expected 90 actual source cards');
  const uniqueTitle = new Set(before.map(x=>x.title));
  const uniqueHref = new Set(before.map(x=>x.href));
  if (uniqueTitle.size!==90 || uniqueHref.size!==90)throw new Error('guard failed: duplicate or missing title/URL');
  for (const [cat,n] of Object.entries(EXPECTED.counts)){
    if(before.filter(x=>x.category===cat).length!==n)throw new Error('guard failed: category '+cat+' count changed');
  }
  let patchedPage=page,patchedLibrary=lib;
  for (const [a,b] of PAGE_REPLACEMENTS)patchedPage=replaceOnce(patchedPage,a,b);
  for (const [a,b] of LIBRARY_REPLACEMENTS)patchedLibrary=replaceOnce(patchedLibrary,a,b);
  if(JSON.stringify(cards(patchedPage))!==JSON.stringify(before)) throw new Error('guard failed: source titles, categories or URLs altered');
  for (const source of [page,lib]) {
    if (!source.includes('<!-- wp:'))throw new Error('guard failed: not Gutenberg content');
  }
  for(const [a,b] of [[page,patchedPage],[lib,patchedLibrary]]){
    if((a.match(/<!-- wp:/g)||[]).length !== (b.match(/<!-- wp:/g)||[]).length)throw new Error('guard failed: block count changed');
  }
  return {status:'STAGING_ONLY_DO_NOT_PUBLISH',
    validation:{actual_sources:90, unique_titles:90, unique_urls:90, category_counts:EXPECTED.counts,
      substitutions:PAGE_REPLACEMENTS.length+LIBRARY_REPLACEMENTS.length, source_cards_preserved:true,
      wordpress_blocks_preserved:true, production_theme_verified:false},
    page_id:input.page_id,page_modified:input.page_modified,page_content:patchedPage,
    library_id:input.library_id,library_modified:input.library_modified,library_content:patchedLibrary};
}
if(process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href){
  if(process.argv.length!==4){console.error('Usage: node reconcile-research-sources-90.mjs WP-export.json staged-output.json');process.exit(2);}
  try {
    const input=JSON.parse(readFileSync(process.argv[2],'utf8'));
    const out=stage(input);
    writeFileSync(process.argv[3],JSON.stringify(out,null,2)+'\n',{flag:'wx'});
    console.log('PASS: wrote offline staging payload only. No WordPress changes made.');
  } catch(e){console.error('HOLD:',e.message);process.exit(1);}
}
