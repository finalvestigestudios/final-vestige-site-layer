#!/usr/bin/env node
'use strict';

/**
 * Offline-only WordPress/Gutenberg source census for the Research Sources catalog.
 * It never fetches URLs, renders a browser, or changes WordPress.
 * Give it a UTF-8 snapshot of the page's saved `content.raw`.
 */
const fs = require('node:fs');

function attribute(tag, name) {
  const safe = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp('(?:\\s|^)' + safe + '\\s*=\\s*(["\\x27])([\\s\\S]*?)\\1', 'i');
  const m = tag.match(re);
  return m ? m[2] : null;
}

function auditResearchSources(raw) {
  if (typeof raw !== 'string') throw new TypeError('A UTF-8 string is required');
  const observed = { all: 0 };
  for (const match of raw.matchAll(/<article\b[^>]*>/gi)) {
    const tag = match[0];
    if (!(attribute(tag, 'class') || '').split(/\s+/).includes('fv-rs-card')) continue;
    observed.all += 1;
    const category = attribute(tag, 'data-cat') || '(missing data-cat)';
    observed_category] = (observed[category] || 0) + 1;
  }
  const match = [...raw.matchAll(/\bconst\s+totals\s*=\s*\{([^{}]+)\}/g)].at(-1);
  const declared = {};
  if (match) {
    for (const pair of match[1].matchAll(/(?:^|,)\s*([a-z][a-z0-9_-]*)\s*:\s*(\d+)\s*(?=,|$)/gi)) {
      declared[pair[1]] = Number(pair[2]);
    }
  }
  if (observed.all === 0 || !Object.prototype.hasOwnProperty.call(declared, 'all')) {
    return { status: 'INSUFFICIENT_DATA', observed, declared, mismatches: [] };
  }
  const keys = [...new Set([...Object.keys(observed), ...Object.keys(declared)])].sort();
  const mismatches = keys.filter(key => observed[key] !== declared[key]).map(key => ({
    category: key,
    observed: observed[key] ?? null,
    declared: declared[key] ?? null,
  }));
  return {
    status: mismatches.length ? 'MISMATCH_SOURCE' : 'PASS',
    observed, declared, mismatches,
    browser_verified: false,
    production_changed: false,
  };
}

if (require.main === module) {
  const file = process.argv[2];
  if (!file || process.argv.length !== 3) {
    process.stderr.write('Usage: node research_sources_count_guard.cjs <wordpress-content-raw.txt>\n');
    process.exitCode = 2;
  } else {
    try {
      const report = auditResearchSources(fs.readFileSync(file, 'utf8'));
      process.stdout.write(JSON.stringify(report, null, 2) + '\n');
      process.exitCode = report.status === 'PASS' ? 0 : report.status == 'MISMATCH_SOURCE' ? 1 : 2;
    } catch (error) {
      process.stderr.write(`${error.message}\n`);
      process.exitCode = 2;
    }
  }
}

module.exports = { auditResearchSources };
