// Final Vestige Studios — Research Sources, read-only WordPress Gutenberg parity gate.
// Usage: node scripts/editorial/check-research-sources-draft-parity.mjs public-1338.raw.txt staging-2354.raw.txt
// Inputs are edit-context content.raw exports; never pass authentication tokens or publish.
// This protects the original 90 cards and known intended staging changes.
// PASS_SOURCE_PARITY_ONLY is NOT browser, screen-reader, newsletter, rights, or media QA.
import {readFileSync} from "node:fs";
function auditParity(publicMarkup, stagedMarkup) {
  const errors = [];
  const notes = [];
  const categories = {declassified:12,accountability:24,engineering:21,archives:25,navigation:8};
  function cards(markup) {
    return Array.from(markup.matchAll(/<article class="fv-rs-card" data-cat="([^"]+)"[^>]*>[\s\S]*?<\/article>/g), m => {
      const html = m[0];
      return {
        category:m[1],
        title:(html.match(/<h3>([\s\S]*?)<\/h3>/)||[])[1]||"",
        url:(html.match(/<a href="([^"]+)"/)||[])[1]||"",
        html,
      };
    });
  }
  function check(ok, description) { if(!ok) errors.push(description); }
  function inventory(arr,tag) {
    check(arr.length===90, `${tag}: expected exactly 90 cards`);
    check(new Set(arr.map(x=>x.title)).size===90, `${tag}: duplicate/empty titles`);
    check(new Set(arr.map(x=>x.url)).size===90, `${tag}: duplicate URLs`);
    check(arr.every(x=>x.title&&x.url.startsWith("https://")&&x.html.includes('target="_blank" rel="noopener noreferrer"')), `${tag}: unsafe/missing link attribute`);
    for(const [k,n] of Object.entries(categories)) check(arr.filter(x=>x.category===k).length===n,`${tag}: ${k} inventory not ${n}`);
  }
  const original=cards(publicMarkup), staged=cards(stagedMarkup);
  inventory(original,"published"); inventory(staged,"staged");
  const changes=[];
  const max=Math.max(original.length,staged.length);
  for(let i=0;i<max;i++) {
    const a=original[i], b=staged[i];
    if(!a||!b) continue;
    check(a.title===b.title&&a.url===b.url&&a.category===b.category, `card ${i+1}: title, URL or category changed`);
    if(a.html!==b.html) changes.push({ordinal:i+1,title:a.title,oldDescription:(a.html.match(/<h3>[\s\S]*?<\/h3><p>([\s\S]*?)<\/p>/)||[])[1]||"",newDescription:(b.html.match(/<h3>[\s\S]*?<\/h3><p>([\s\S]*?)<\/p>/)||[])[1]||""});
  }
  check(changes.length===1&&changes[0].title==="National Archives Record Group Explorer",`Only the intended NARA card may change, found ${changes.length}: ${changes.map(x=>x.title).join(", ")}`);
  const naraOld="NARA’s June 2026 baseline reports 475,127,595 scans";
  const naraNew="NARA updates these estimates monthly";
  check(publicMarkup.includes(naraOld)&&stagedMarkup.includes(naraNew)&&!stagedMarkup.includes(naraOld),"NARA evergreen correction does not match expected exact evidence");
  // Critical styles for cards, responsive breakpoints, keyboard focus and reduced motion must remain exactly equal.
  const primaryStyle = x => (x.match(/<style>([\s\S]*?)<\/style>/)||[])[1]||"";
  check(primaryStyle(publicMarkup)===primaryStyle(stagedMarkup),"Primary directory CSS changed (requires visual re-review)");
  for(const [name,source] of [["published",publicMarkup],["staged",stagedMarkup]]) {
    const base=source.split("<!-- /wp:html -->")[0];
    const supplemental=source.slice(source.indexOf('id="fv-rs-batch003"'));
    check((base.match(/class="fv-rs-card"/g)||[]).length===60,`${name}: 60 base HTML cards expected`);
    check((supplemental.match(/class="fv-rs-card"/g)||[]).length===30,`${name}: 30 supplemental HTML cards expected`);
    check((source.match(/<!-- wp:html -->/g)||[]).length===3,`${name}: expected three top-level Gutenberg HTML blocks`);
  }
  check((publicMarkup.match(/<script>/g)||[]).length===2, "Published baseline does not contain the expected two controllers");
  check((stagedMarkup.match(/<script>/g)||[]).length===1, "Stage must have exactly one script controller");
  check((stagedMarkup.match(/search\.addEventListener\(['"]input['"]/g)||[]).length===1, "Stage must register exactly one search input listener");
  check(stagedMarkup.includes('role="group"')&&stagedMarkup.includes('aria-label="Filter research sources"'),"Stage filter group semantics missing");
  check(/<noscript>[\s\S]*?<\/noscript>/.test(stagedMarkup),"Stage scriptless browsing guidance missing");
  check(/\.fv-rs-filters button span\s*\{[\s\S]*?clip-path:\s*inset\(50%\)/.test(stagedMarkup),"Stage accessible visually-hidden count treatment missing");
  check(!/\.fv-rs-filters button span\s*\{\s*display\s*:\s*none/.test(stagedMarkup),"Stage CSS hides numeric counts from assistive technology");
  check(/Search all 90 sources/.test(stagedMarkup)&&/All 90/.test(stagedMarkup),"Stage static filter/search total not updated to 90");
  check(!/Search all 60 sources|Showing all 60|All 60/.test(stagedMarkup),"Stage retains a stale 60-source label");
  check(stagedMarkup.includes("accountability:24,engineering:21,archives:25"),"Stage 24/25 live JavaScript totals absent");
  notes.push("This is authentic source-content parity, not production-theme browser or screen-reader QA.");
  notes.push("Card records and link-only rights cues are compared byte-for-byte; external rights/downloads not independently validated.");
  return {
    verdict:errors.length?"FAIL":"PASS_SOURCE_PARITY_ONLY", errors, notes,
    publishedCards:original.length, stagedCards:staged.length,
    exactCardMatches:original.filter((x,i)=>x.html===staged[i]?.html).length,
    changedCards:changes, expectedCategories:categories,
    rawLengths:{published:publicMarkup.length,staged:stagedMarkup.length},
    browserTested:false, notificationSuppressionTested:false,
  };
}
const [publishedPath, stagedPath] = process.argv.slice(2);
if(!publishedPath||!stagedPath) {
  console.error("Usage: node check-research-sources-draft-parity.mjs <public-raw> <staging-raw>");
  process.exit(2);
}
const report=auditParity(readFileSync(publishedPath,"utf8"),readFileSync(stagedPath,"utf8"));
console.log(JSON.stringify(report,null,2));
process.exit(report.errors.length?1:0);
