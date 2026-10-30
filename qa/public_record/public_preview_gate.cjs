'use strict';
// Read-only, offline snapshot review; no WordPress/GitHub/network mutation.
const fs = require('node:fs');

function canonicalPath(url) {
  if (typeof url !== 'string') return null;
  try {
    const parsed = new URL(url, 'https://finalvestige.com');
    if (parsed.origin !== 'https://finalvestige.com') return null;
    return parsed.pathname.replace(/\/+$/, '') + '/';
  } catch { return null; }
}
function linkedPaths(markup) {
  const links = new Set();
  if (typeof markup !== 'string') return links;
  for (const match of markup.matchAll(/\bhref\s*=\s*["']([^"']+)["']/gi)) {
    const path = canonicalPath(match[1]);
    if (path) links.add(path);
  }
  return links;
}
function audit(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' || !Array.isArray(snapshot.documents)) {
    throw new TypeError('Expected {landing, documents[]} snapshot');
  }
  const landing = snapshot.landing || {};
  const linked = linkedPaths(landing.markup);
  const findings = [];
  if (landing.status === 'publish' && landing.noindex === false &&
      (!landing.seo_title || !landing.seo_description)) {
    findings.push({code:'REVIEW_INDEXABLE_HUB_METADATA',level:'review',id:landing.id,
      evidence:'Indexable landing page has missing saved custom SEO fields; browser output not tested.'});
  }
  let previews = 0;
  for (const doc of snapshot.documents) {
    if (!doc || typeof doc !== 'object') continue;
    const path = canonicalPath(doc.url);
    if (!path || !linked.has(path)) continue;
    if (doc.status !== 'publish') {
      findings.push({code:'HIGH_LINKED_UNPUBLISHED',level:'high',id:doc.id,path,
        evidence:'Published hub links to a nonpublished document; public HTTP status unverified.'});
      continue;
    }
    const researchDraft = /\bresearch\s+draft\b/i.test(String(doc.editorial_label || ''));
    if (!researchDraft) continue;
    previews++;
    findings.push({code:'REVIEW_PUBLIC_RESEARCH_PREVIEW',level:'review',id:doc.id,path,
      evidence:'Published and linked Research Draft. The hub labels it as a preview; check editorial approval.'});
    if (doc.noindex !== true) {
      findings.push({code:'HIGH_INDEXABLE_RESEARCH_DRAFT',level:'high',id:doc.id,path,
        evidence:'Research Draft is published and linked without saved WordPress noindex flag.'});
    }
  }
  return {checked: snapshot.documents.length, linked_paths:linked.size,
    published_research_previews:previews, findings,
    production_browser_verified:false};
}
module.exports = {canonicalPath,linkedPaths,audit};
if (require.main === module) {
  if (process.argv.length !== 3) {
    process.stderr.write('Usage: node public_preview_gate.cjs sanitized-snapshot.json\n');
    process.exitCode = 64;
  } else {
    try {
      const input = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
      const result = audit(input);
      process.stdout.write(JSON.stringify(result,null,2)+'\n');
      if (result.findings.some(f => f.level === 'high')) process.exitCode = 2;
    } catch (e) { process.stderr.write(e.message+'\n');process.exitCode = 1; }
  }
}
