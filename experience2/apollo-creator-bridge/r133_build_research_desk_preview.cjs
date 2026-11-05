'use strict';
/**
 * Offline, deterministic Research Desk editorial preview builder.
 * STAGING ONLY; does not install a WordPress plugin, contact NASA, or publish anything.
 * Combines the already-reviewed R132 six-card HTML with the actual Research Desk CSS/JS.
 * Use this to inspect source-role changes without modifying PR #158 or the homepage.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const os = require('node:os');
const {audit, gitBlob} = require('./r132_research_desk_source_role_gate.cjs');
const ROOT = path.resolve(__dirname, '../..');
const SOURCES = Object.freeze({
  html: 'experience2/apollo-creator-bridge/r132_research_desk_source_role_review.html',
  css: 'experience2/research-desk/assets/source-ledger.css',
  js: 'experience2/research-desk/assets/source-ledger.js'
});
const SHA256 = s => crypto.createHash('sha256').update(s).digest('hex');
const CSPHASH = s => crypto.createHash('sha256').update(s).digest('base64');
const STATE = Object.freeze({release:'STAGING_HOLD',rights:'0_OF_6_CLEARED',browser_acceptance:'NOT_ESTABLISHED',paid_offer:'NOT_VERIFIED'});
function assetPolicy(css, js) {
  const reasons = [];
  if (!css.includes('.fv-ex2-ledger') || !js.includes('[data-fvx-ledger]')) reasons.push('COMPONENT_ASSET_MISMATCH');
  if (/<\s*\/\s*(?:style|script)\b/i.test(css+'\n'+js)) reasons.push('UNSAFE_EMBED_TERMINATOR');
  if (/@import\b|url\s*\(\s*['"]?https?:|@font-face\b/i.test(css)) reasons.push('EXTERNAL_STYLE_DEPENDENCY');
  if (/\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|localStorage|sessionStorage|indexedDB|serviceWorker)\b/i.test(js)) reasons.push('NETWORK_OR_STORAGE_DEPENDENCY');
  if (/\b(?:eval|new\s+Function)\s*\(/i.test(js)) reasons.push('DYNAMIC_EVALUATION');
  return reasons;
}
// R132 editorial fragment omitted the clear control required by the existing
// Research Desk progressive-search script. Repair only the isolated preview,
// then rerun the historical-source gate on the modified HTML.
function repairSearch(html) {
  if (html.includes('data-fvx-clear')) return html;
  const needle='<span class="fv-ex2-ledger__status" role="status" aria-live="polite" data-fvx-status></span>';
  const count=html.split(needle).length-1;
  if (count!==1) throw Error('REFUSED_SEARCH_REPAIR_AMBIGUOUS: '+count);
  return html.replace(needle,needle+'<button type="button" class="fv-ex2-ledger__clear" data-fvx-clear hidden>Clear search</button>');
}
function renderDocument(html, css, js) {
  const policy = assetPolicy(css,js);
  if (policy.length) throw Error('REFUSED_UNSAFE_ASSET: '+policy.join(','));
  // The banner/background are included in the hashed stylesheet; no unsafe-inline exception.
  const layoutCss = '\nbody.fv-r133-preview-body{margin:0;background:#090a0a}\n#fv-r133-preview-status{color:#fff;background:#472d09;font:600 14px/1.5 system-ui;padding:12px 20px;margin:0}';
  const bundledCss = css + layoutCss;
  const csp = ["default-src 'none'",`style-src 'sha256-${CSPHASH(bundledCss)}'`,`script-src 'sha256-${CSPHASH(js)}'`,"img-src 'none'","connect-src 'none'","font-src 'none'","frame-src 'none'","form-action 'none'","base-uri 'none'","object-src 'none'"].join('; ');
  // No remote images, embeds, analytics, or fonts. The NASA source links open a new tab.
  return ['<!doctype html>','<html lang="en"><head>','<meta charset="utf-8">','<meta name="viewport" content="width=device-width,initial-scale=1">','<meta name="robots" content="noindex,nofollow,noarchive">',
  '<meta http-equiv="Content-Security-Policy" content="'+csp+'">',
  '<meta name="color-scheme" content="dark">',
  '<title>Editorial Preview · Apollo 1 Research Desk · NOT LIVE</title>',
  '<style>'+bundledCss+'</style>','</head><body class="fv-r133-preview-body">',
  '<p id="fv-r133-preview-status" role="note">EDITORIAL STAGING ONLY · NOT LIVE · No image redistribution or commercial-use clearance. NASA photographs are source links, not technical instruments.</p>',
  html,'<script>'+js+'</script>','</body></html>'].join('\n')+'\n';
}
function build({root=ROOT,outDir=path.join(os.tmpdir(),'fv-apollo-r133-preview')}={}) {
  const contents = {};
  for (const [key,rel] of Object.entries(SOURCES)) contents[key] = fs.readFileSync(path.join(root,rel),'utf8');
  const result = audit(contents.html);
  if (result.status !== 'PASS' || result.release !== 'STAGING_HOLD' || result.rights !== '0_OF_6_CLEARED' || result.reviewed_records!==6) throw Error('REFUSED_R132_SOURCE_GATE: '+JSON.stringify(result.errors));
  const policy = assetPolicy(contents.css,contents.js);
  if(policy.length) throw Error('REFUSED_ASSET_POLICY: '+policy.join(','));
  const enhancedHtml = repairSearch(contents.html);
  const postRepair = audit(enhancedHtml);
  if (postRepair.status !== 'PASS' || !enhancedHtml.includes('data-fvx-clear hidden')) throw Error('REFUSED_POST_REPAIR_AUDIT: '+JSON.stringify(postRepair.errors));
  const document = renderDocument(enhancedHtml,contents.css,contents.js);
  const manifest = {
    schema:'fv.ex2.apollo.r133.offline-preview.v1',artifact:'apollo-r133-research-desk-editorial-preview.html',
    inputs:Object.fromEntries(Object.entries(SOURCES).map(([key,rel])=>[key,{path:rel,sha256:SHA256(contents[key]),git_blob:gitBlob(contents[key])}])),
    artifact_sha256:SHA256(document),count_verified_nasa_link_targets:6, ...STATE,
    attribution:'Source link ≠ redistribution/publicity authorization; no commercial endorsement inferred.',
    measurement:'No sessions, leads, checkout starts or revenue measured by this builder.'
  };
  fs.mkdirSync(outDir,{recursive:true});
  const output=path.join(outDir,manifest.artifact);
  fs.writeFileSync(output,document,'utf8');
  fs.writeFileSync(path.join(outDir,'apollo-r133-preview-manifest.json'),JSON.stringify(manifest,null,2)+'\n','utf8');
  return {output,manifest};
}
if (require.main === module) {
  const index=process.argv.indexOf('--out');
  if (index!==-1 && !process.argv[index+1]) throw Error('--out requires a directory');
  const outDir=index!==-1?path.resolve(process.argv[index+1]):undefined;
  try { const {output,manifest}=build({outDir});process.stdout.write(JSON.stringify({output,manifest},null,2)+'\n'); }
  catch(err){ process.stderr.write(err.message+'\n');process.exitCode=2; }
}
module.exports={assetPolicy,repairSearch,renderDocument,build,SOURCES,STATE};
