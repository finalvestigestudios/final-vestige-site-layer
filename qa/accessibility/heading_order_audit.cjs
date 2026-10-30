'use strict';
/** Read-only semantic heading audit for sanitized WordPress Gutenberg snapshots. */
const fs = require('node:fs');

function headingsFromMarkup(markup) {
  if (typeof markup !== 'string') throw new TypeError('content must be a string');
  const text = markup
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<(?:script|style|template)\b[^>]*>[\s\S]*?<\/(?:script|style|template)\s*>/gi, '');
  return [...text.matchAll(/<h([1-6])\b[^>]*>([\s\S]*?)<\/h\1\s*>/gi)]
    .map(match => ({
      level: Number(match[1]),
      text: match[2].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim().slice(0, 120)
    }));
}

function auditPages(pages) {
  if (!Array.isArray(pages)) throw new TypeError('input must be an array of page snapshots');
  return pages.filter(page => page && page.status === 'publish').map(page => {
    if (!Number.isInteger(page.id) || typeof page.url !== 'string')
      throw new TypeError('each published page requires numeric id and url');
    const headings = headingsFromMarkup(page.content);
    const firstH1 = headings.findIndex(h => h.level === 1);
    const preceding = headings.slice(0, firstH1 < 0 ? undefined : firstH1);
    const before = preceding.filter(h => h.level > 1);
    const reviewReasons = [];
    if (firstH1 === -1) reviewReasons.push('NO_CONTENT_H1');
    if (before.length) reviewReasons.push('HEADING_BEFORE_CONTENT_H1');
    if (headings.filter(h => h.level === 1).length > 1) reviewReasons.push('MULTIPLE_CONTENT_H1');
    return {
      id: page.id, url: page.url,
      status: reviewReasons.length ? 'REVIEW_SOURCE_ONLY' : 'PASS_SOURCE_ONLY',
      reviewReasons, headingCount: headings.length,
      firstHeadings: headings.slice(0, 4),
      beforeH1Count: before.length
    };
  });
}

if (require.main === module) {
  try {
    if (process.argv.length !== 3) throw new Error('Usage: node heading_order_audit.cjs sanitized-pages.json');
    const results = auditPages(JSON.parse(fs.readFileSync(process.argv[2], 'utf8')));
    const report = {
      examined: results.length,
      pass: results.filter(r => r.status === 'PASS_SOURCE_ONLY').length,
      review: results.filter(r => r.status === 'REVIEW_SOURCE_ONLY').length,
      results: results.filter(r => r.status !== 'PASS_SOURCE_ONLY'),
      scope: 'Gutenberg/editor markup only; not public DOM, not WCAG certification'
    };
    process.stdout.write(JSON.stringify(report, null, 2) + '\n');
  } catch (error) {
    process.stderr.write(String(error.message) + '\n');
    process.exitCode = 2;
  }
}
module.exports = { headingsFromMarkup, auditPages };
