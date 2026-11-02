// Final Vestige Studios — exact-checkout homepage source and media custody gate.
// Source PASS is never WordPress staging / WCAG / Lighthouse / rights / release PASS.
export const auditHomepage = function auditHomepage(html,ledger,assets){
  const checks={},errors=[],record=(name,ok)=>{checks[name]=!!ok;if(!ok)errors.push(name)};
  const a=(tag,name)=>{const m=tag.match(new RegExp("(?:^|\\s)"+name+"\\s*=\\s*([\"'])(.*?)\\1","i"));return m?m[2]:null};
  const decode=s=>String(s??"").replace(/&amp;/g,"&");
  const chapter=["fv-hf-title","fv-hf-chronicle","fv-hf-evidence","fv-hf-inquiry","fv-hf-method-title","fv-hf-observer","fv-hf-mind-title"];
  const css=["flagship.css","chronicle.css","chronicle-lens.css","inquiry.css","observer-lab.css","reading-trail.css"];
  const js=["flagship.js","observer-lab.js","chronicle-lens.js","reading-trail.js"];
  const ids=[...html.matchAll(/\bid\s*=\s*["']([^"']+)["']/g)].map(m=>m[1]);
  const anchors=[...html.matchAll(/<a\b[^>]*\bhref\s*=\s*["']#([^"']+)["'][^>]*>/gi)].map(m=>m[1]);
  const links=[...html.matchAll(/<a\b[^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*>/gi)].map(m=>decode(m[1]));
  const imgTags=[...html.matchAll(/<img\b[^>]*>/gi)].map(m=>m[0]);
  const panels=[...html.matchAll(/<(?:article|section|div)\b[^>]*\bdata-fv-case\s*=\s*["'][^"']+["'][^>]*>/gi)].map(m=>m[0]);
  const frames=[...html.matchAll(/<(?:figure|section|div)\b[^>]*\bdata-fv-observer-frame\s*=\s*["'][^"']+["'][^>]*>/gi)].map(m=>m[0]);
  record("one_h1",(html.match(/<h1\b/gi)||[]).length===1);
  record("unique_ids",ids.length===new Set(ids).size);
  record("seven_chapters",chapter.every(id=>ids.includes(id)));
  record("chapter_anchor_links",chapter.every(id=>html.includes('href="#'+id+'"')));
  record("all_fragment_targets_exist",anchors.every(id=>ids.includes(id)));
  record("unpublished_guard",html.includes("DO NOT DEPLOY AS THE WORDPRESS HOME PAGE")&&html.includes("DESIGN CANDIDATE · NOT LIVE"));
  record("native_nojs_cases",panels.length===3&&frames.length===2&&[...panels,...frames].every(tag=>!/\shidden(?:\s|=|>)/i.test(tag))&&(html.match(/<details\b/gi)||[]).length>=6);
  record("editorial_no_checkout",!/<form\b/i.test(html)&&!/clickbank\.net|hop\.clickbank|inspire3\.com\/checkout|guaranteed brain reprogramming/i.test(html));
  record("focus_and_primary_sources",[
    "/focus/","/editorial-standards/","/free-resources/puysegurs-animal-magnetism-files/",
    "rmg.co.uk/collections/objects/","historymuseum.ca/blog/a-very-special-piece-of-paper",
    "nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/","digitalcollections.nypl.org/items/"
  ].every(s=>html.includes(s)));
  record("six_css_four_js_exact",css.every(n=>html.split('<link rel="stylesheet" href="./'+n+'">').length===2)&&
    js.every(n=>html.split('<script src="./'+n+'" defer></script>').length===2)&&
    (html.match(/<link\b[^>]*rel=["']stylesheet["']/gi)||[]).length===css.length&&
    (html.match(/<script\b[^>]*\bsrc=/gi)||[]).length===js.length);
  record("ten_asset_files_present",[...css,...js].every(n=>typeof assets[n]==="string"&&assets[n].length>0));
  record("no_remote_js_css",!/<(?:script|link)\b[^>]*\b(?:src|href)=["']https?:/i.test(html));
  record("two_retained_images_have_alt_dimensions",imgTags.length===2&&imgTags.every(tag=>a(tag,"alt")&&Number(a(tag,"width"))>0&&Number(a(tag,"height"))>0));
  record("image_ledger_ids",ledger.records.length===3&&["apollo","franklin","malbone"].every(id=>ledger.records.some(r=>r.id===id)));
  const srcs=imgTags.map(t=>decode(a(t,"src"))),allowed=new Set(ledger.records.map(r=>r.image_url));
  record("displayed_images_exactly_in_ledger",srcs.length===2&&new Set(srcs).size===2&&srcs.every(url=>allowed.has(url)));
  record("image_delivery_host_scoped",srcs.every(u=>u.startsWith("https://finalvestige.com/wp-content/uploads/")||u.startsWith("https://i0.wp.com/finalvestige.com/wp-content/uploads/")));
  const mapTag=imgTags.find(t=>decode(a(t,"src")).includes("5003296"));
  const sourcePlate=html.includes('class="fv-hf__source-plate"')&&html.includes("ARCHIVAL REFERENCE · IMAGE NOT REPRODUCED");
  record("retained_archive_images_responsive",imgTags.every(t=>!!a(t,"srcset")&&!!a(t,"sizes")));
  record("nypl_uncleared_capture_not_embedded",!mapTag&&sourcePlate&&
    !html.includes("edit-017-v02-nypl-5003296-original.jpg"));
  record("original_sources_linked",ledger.records.every(r=>r.source_url&&links.includes(r.source_url)));
  record("map_not_fake_crash_overlay",html.includes("1903")&&html.includes("1918")&&ledger.records.some(r=>r.id==="malbone"&&r.limitation?.includes("Do not spatially")));
  const unsigned=ledger.records.filter(r=>!r.rights_approval||r.rights_approval.outcome!=="approved"||!r.rights_approval.reviewer||!r.rights_approval.checked_at||!r.rights_approval.evidence_url).map(r=>r.id);
  return {
    source:{status:errors.length?"FAIL":"PASS",checks,errors,counts:{ids:ids.length,chapters:chapter.length,images:imgTags.length,details:(html.match(/<details\b/gi)||[]).length,styles:css.length,scripts:js.length,source_chars:html.length}},
    media:{status:unsigned.length?"HOLD":"REVIEWED",pending_signoff:unsigned,source_claims:ledger.records.map(r=>({id:r.id,media_credit:r.image_credit,source_url:r.source_url,declared_status:r.media_rights_status})),image_transfer_bytes:null,loaded_media_browser_test:null},
    release:{status:"HOLD",blockers:[
      ...(errors.length?["Source failures: "+errors.join(", ")+"."]:[]),
      ...(unsigned.length?["Source-specific signed media-rights review missing: "+unsigned.join(", ")+"."]:[]),
      "No separately authorized private WordPress/Assembler staging instance connected or verified.",
      "Actual staging Chromium cookies/CSP and first-party image loads not verified.",
      "Genuine WCAG 2.2 AA, keyboard/assistive-tech/Safari and real Lighthouse/field p75 CWV not measured.",
      "Hosted CI and independent QD on final SHA plus founder-governed release approval pending."
    ]},
    limits:["Source static audit only; not a browser, legal, image-transfer or performance certification.","Release status intentionally never auto-promotes to PASS."]
  };
};
import {readFileSync,writeFileSync} from "node:fs";
import {resolve,join} from "node:path";
import {execFileSync} from "node:child_process";
import {pathToFileURL} from "node:url";
const css=["flagship.css","chronicle.css","chronicle-lens.css","inquiry.css","observer-lab.css","reading-trail.css"];const js=["flagship.js","observer-lab.js","chronicle-lens.js","reading-trail.js"];
export function auditCheckout(root,expectedHead){
  if(!/^[a-f0-9]{40}$/.test(expectedHead||""))throw Error("Required 40-hex --expected-head");
  const home=resolve(root),repo=resolve(home,"../..");
  const actual=execFileSync("git",["rev-parse","HEAD"],{cwd:repo,encoding:"utf8"}).trim();
  if(actual!==expectedHead)throw Error("Expected SHA does not match actual checkout HEAD "+actual);
  const paths=["index.html","source-manifest.json",...css,...js].map(n=>"experience2/home-flagship/"+n);
  const changed=execFileSync("git",["status","--porcelain","--untracked-files=no","--",...paths],{cwd:repo,encoding:"utf8"}).trim();
  if(changed)throw Error("Canonical source files dirty: "+changed);
  const src=Object.fromEntries([...css,...js].map(n=>[n,readFileSync(join(home,n),"utf8")]));
  return auditHomepage(readFileSync(join(home,"index.html"),"utf8"),JSON.parse(readFileSync(join(home,"source-manifest.json"),"utf8")),src);
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 const arg=(flag)=>{let i=process.argv.indexOf(flag);return i<0?undefined:process.argv[i+1]};
 try{const report=auditCheckout(arg("--root")||"experience2/home-flagship",arg("--expected-head"));if(arg("--report"))writeFileSync(arg("--report"),JSON.stringify(report,null,2)+"\n");process.stdout.write(JSON.stringify({source:report.source,media:report.media.status,release:report.release},null,2)+"\n");if(report.source.status!=="PASS"||(process.argv.includes("--require-release")&&report.release.status!=="PASS"))process.exitCode=2}
 catch(err){process.stderr.write("FAIL CLOSED: "+err.message+"\n");process.exitCode=2}
}
