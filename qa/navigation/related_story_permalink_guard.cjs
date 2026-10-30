#!/usr/bin/env node
'use strict';
/**
 * Offline, read-only canonical internal-link REVIEW. No network, WordPress writes,
 * redirects, browser emulation, or claim that an alias returns HTTP 404.
 */
const fs = require('node:fs');

function pathOnly(value, origin) {
  if (typeof value !== 'string' || !value.trim()) return null;
  try {
    const base = new URL(origin);
    const url = new URL(value.trim(), base);
    if (!['http:', 'https:'].includes(url.protocol) || url.hostname.toLowerCase() !== base.hostname.toLowerCase()) return null;
    return url.pathname.replace(/\/{2,}/g, '/').replace(/\/$/, '') || '/';
  } catch { return null; }
}

function linksFromMarkup(markup) {
  if (typeof markup !== 'string') return [];
  return [...markup.matchAll(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')/gi)].map(m => m[1] ?? m[2]);
}

function inspect(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' || !Array.isArray(snapshot.posts) ||
      !Array.isArray(snapshot.articles) || !Array.isArray(snapshot.published_page_paths) ||
      typeof snapshot.site_origin !== 'string') throw new TypeError('Invalid read-only WordPress snapshot');
  const origin = new URL(snapshot.site_origin).origin;
  const pages = new Set(snapshot.published_page_paths.map(p => pathOnly(p, origin)).filter(Boolean));
  const canonicalBySlug = new Map();
  for (const post of snapshot.posts) {
    if (post?.status !== 'publish' || typeof post.slug !== 'string') continue;
    const canonical = pathOnly(post.url, origin);
    if (canonical) canonicalBySlug.set(post.slug, { id: post.id, canonical });
  }
  const findings = [];
  let checked = 0;
  for (const article of snapshot.articles) {
    const hrefs = Array.isArray(article.links) ? article.links : linksFromMarkup(article.markup);
    for (const href of hrefs) {
      const sourcePath = pathOnly(href, origin);
      if (!sourcePath) continue;
      checked++;
      const match = /^\/([^/]+)$/.exec(sourcePath);
      if (!match || pages.has(sourcePath)) continue;
      const dest = canonicalBySlug.get(match[1]);
      if (!dest || dest.canonical === sourcePath) continue;
      findings.push({
        severity: 'REVIEW', code: 'NONCANONICAL_PUBLISHED_POST_LINK',
        source_id: article.id, source_title: article.title,
        href, target_id: dest.id, canonical_path: dest.canonical,
        reason: 'Source uses a bare post slug although WordPress records a dated canonical permalink; an automatic redirect may exist.'
      });
    }
  }
  return {
    status: findings.length ? 'REVIEW' : 'NO_MISMATCHES_IN_SNAPSHOT',
    checked_first_party_links: checked, reviewed_articles: snapshot.articles.length,
    findings, note: 'WordPress source/canonical metadata comparison only. This is not a browser HTTP-status test or proof of a broken visitor link.'
  };
}

if (require.main === module) {
  try {
    if (process.argv.length !== 3) throw new Error('Usage: node related_story_permalink_guard.cjs snapshot.json');
    const snapshot = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    console.log(JSON.stringify(inspect(snapshot), null, 2));
  } catch (error) { console.error(String(error)); process.exitCode = 1; }
}

module.exports = { inspect, pathOnly, linksFromMarkup };
