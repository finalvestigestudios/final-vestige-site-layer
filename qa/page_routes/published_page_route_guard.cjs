#!/usr/bin/env node
'use strict';
// Offline-only inspection of saved WordPress Gutenberg page markup.
// This makes no network, CMS, or write calls. A missing registry route is
// a REVIEW, never proof of a live HTTP 404.
const fs = require('node:fs');

const RETIRED = /72-hours-without-the-tap|water-resilience-field-manual|Final_Vestige_Water|water-planner|72 Hours Without the Tap/i;
const DYNAMIC = /^\/(?:wp-content(?:\/|$)|wp-json(?:\/|$)|wp-login\.php(?:\/|$)|wp-admin(?:\/|$)|portal(?:\/|$)|feed(?:\/|$)|author(?:\/|$)|tag(?:\/|$)|category(?:\/|$))/i;

function normalizedPath(href, origin = 'https://finalvestige.com') {
  if (typeof href !== 'string' || !href.trim()) return null;
  const candidate = href.trim().replace(/&(?:amp|#0*38|#x0*26);/gi, '&');
  if (candidate.startsWith('#') || candidate.startsWith('?') || /^(?:mailto|tel|javascript|data):/i.test(candidate)) return null;
  try {
    const base = new URL(origin);
    if (!/^https?:$/.test(base.protocol)) return null;
    const target = new URL(candidate, base);
    // Treat HTTP -> HTTPS canonicalization as a source-level review if the
    // original absolute link uses plain HTTP; it is not an outage claim.
    if (target.hostname.toLowerCase() !== base.hostname.toLowerCase() || target.port !== base.port) return null;
    let path = target.pathname.replace(/\/{2,}/g, '/');
    if (!path.endsWith('/')) path += '/';
    return path;
  } catch { return null; }
}

function visibleAnchors(html) {
  // Strip inline scripts, styles, and Gutenberg comments. Their href-looking
  // strings are not reliable evidence of a rendered anchor.
  const visible = html
    .replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, '')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi, '')
    .replace(/<!--[\s\S]*?-->/g, '');
  const anchors = [];
  for (const a of visible.matchAll(/<a\b[^>]*>/gi)) {
    const m = a[0].match(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')/i);
    if (m) anchors.push(m[1] ?? m[2]);
  }
  return anchors;
}

function inspect(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' || !Array.isArray(snapshot.pages) || !Array.isArray(snapshot.posts)) {
    return { status: 'INVALID_INPUT', reason: 'Expected {pages: [...], posts: [...]}.' };
  }
  const origin = snapshot.site_origin || 'https://finalvestige.com';
  if (snapshot.pages.length === 0 || snapshot.posts.some(p => typeof p.link !== 'string') || snapshot.pages.some(p => typeof p.link !== 'string' || typeof p.content !== 'string')) {
    return { status: 'INVALID_INPUT', reason: 'Published pages must have link and saved content; posts must have links.' };
  }
  if ([...snapshot.pages, ...snapshot.posts].some(p => p.status && p.status !== 'publish')) {
    return { status: 'INVALID_INPUT', reason: 'Input must contain published items only.' };
  }
  const registry = new Set([...snapshot.pages, ...snapshot.posts].map(p => normalizedPath(p.link, origin)).filter(Boolean));
  const orphanCandidates = [], retiredReferences = [];
  let checkedLinks = 0, skippedDynamic = 0, ignoredOffsite = 0;
  for (const page of snapshot.pages) {
    if (RETIRED.test(page.content)) retiredReferences.push({ page_id: page.id, page_url: page.link });
    for (const href of visibleAnchors(page.content)) {
      const path = normalizedPath(href, origin);
      if (!path) { ignoredOffsite++; continue; }
      checkedLinks++;
      if (DYNAMIC.test(path)) { skippedDynamic++; continue; }
      if (!registry.has(path)) orphanCandidates.push({ page_id: page.id, href, normalized_path: path });
    }
  }
  return {
    status: orphanCandidates.length || retiredReferences.length ? 'REVIEW_SOURCE' : 'CLEAN_SOURCE',
    site_origin: origin, published_pages_scanned: snapshot.pages.length,
    published_posts_in_registry: snapshot.posts.length, first_party_links_inspected: checkedLinks,
    skipped_dynamic_routes: skippedDynamic, ignored_offsite_fragment_or_query: ignoredOffsite,
    orphan_route_candidates: orphanCandidates, retired_campaign_references: retiredReferences,
    browser_verified: false, http_verified: false
  };
}

if (require.main === module) {
  if (process.argv.length !== 3) {
    process.stderr.write('Usage: node published_page_route_guard.cjs /path/to/local_wp_snapshot.json\n');
    process.exitCode = 2;
  } else {
    try {
      const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
      const output = inspect(data);
      process.stdout.write(JSON.stringify(output, null, 2) + '\n');
      process.exitCode = output.status === 'CLEAN_SOURCE' ? 0 : output.status === 'REVIEW_SOURCE' ? 1 : 2;
    } catch (e) {
      process.stderr.write(`Could not inspect local snapshot: ${e.message}\n`);
      process.exitCode = 2;
    }
  }
}

module.exports = { normalizedPath, visibleAnchors, inspect };
