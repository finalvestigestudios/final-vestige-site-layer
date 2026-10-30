'use strict';
/**
 * Pure, offline WordPress metadata consistency check.
 * Only compares editor source with editor SEO metadata; NEVER verifies Google snippets or public HTML.
 */
function pageCounts(value) {
  if (typeof value !== 'string') return [];
  const found = new Set();
  const re = /\b(\d{1,3})(?:\s*[-–]\s*|\s+)pages?\b/gi;
  let m;
  while ((m = re.exec(value))) found.add(Number(m[1]));
  return Array.from(found).sort((a, b) => a - b);
}
function checkFocusMetadata(snapshot) {
  const p = snapshot && typeof snapshot === 'object' && snapshot.page ? snapshot.page : snapshot;
  if (!p || typeof p !== 'object' || Number(p.id) !== 1579 || p.slug !== 'focus') {
    return {status: 'INCONCLUSIVE', code: 'UNEXPECTED_PAGE', source_only: true};
  }
  if (p.status !== 'publish') return {status: 'INCONCLUSIVE', code: 'NOT_PUBLISHED', source_only: true};
  const body = typeof p.content === 'string' ? p.content : (p.content && p.content.raw) || '';
  const description = p.meta && p.meta.advanced_seo_description;
  const bodyPages = pageCounts(body);
  const descriptionPages = pageCounts(description);
  const common = {source_only: true, page_id: 1579, body_pages: bodyPages, seo_description_pages: descriptionPages};
  if (bodyPages.length !== 1) return {...common, status: 'INCONCLUSIVE', code: 'BODY_EDITION_AMBIGUOUS'};
  if (descriptionPages.length !== 1) return {...common, status: 'REVIEW', code: 'SEO_PAGE_COUNT_MISSING_OR_AMBIGUOUS'};
  if (bodyPages[0] !== descriptionPages[0]) return {...common, status: 'MISMATCH_CMS', code: 'FOCUS_EDITION_PAGE_COUNT_MISMATCH'};
  return {...common, status: 'PASS_CMS', code: 'FOCUS_EDITION_COUNTS_MATCH'};
}
module.exports = {pageCounts, checkFocusMetadata};
if (require.main === module) {
  const fs = require('node:fs');
  const path = process.argv[2];
  if (!path) {
    process.stderr.write('Usage: node focus_metadata_guard.cjs SANITIZED_WORDPRESS_SNAPSHOT.json\n');
    process.exitCode = 2;
  } else {
    try {
      const result = checkFocusMetadata(JSON.parse(fs.readFileSync(path, 'utf8')));
      process.stdout.write(JSON.stringify(result, null, 2) + '\n');
      process.exitCode = result.status === 'PASS_CMS' ? 0 : result.status === 'MISMATCH_CMS' ? 1 : 2;
    } catch (_) {
      process.stderr.write('Unable to parse sanitized snapshot\n');
      process.exitCode = 2;
    }
  }
}
