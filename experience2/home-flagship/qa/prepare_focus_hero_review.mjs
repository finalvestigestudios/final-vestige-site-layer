#!/usr/bin/env node
/**
 * WordPress Page 6 OFFLINE review-only hero CTA change. No HTTP/CMS write code.
 * Input: JSON exported from WordPress pages-get(context=edit) or its data object.
 * Usage: node prepare_focus_hero_review.mjs --input page-6-edit-export.json [--out candidate.html]
 * An export with changed content/status/timestamp MUST be independently re-reviewed.
 */
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';

export const BASELINE = Object.freeze({
  site: 256784396, id: 6, modified: '2026-11-05T12:07:24',
  characters: 150710, fnv32: '70740831', margins: 72,
});
export const CHAPTER_IDS = Object.freeze([
  'fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
  'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title',
]);
export const BEFORE = '<a class="fv-hf__text-link" href="https://finalvestige.com/blog/">Read the investigations <span aria-hidden="true">↗</span></a>';
export const AFTER = '<a class="fv-hf__text-link" href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook <span aria-hidden="true">↗</span></a>';

const count = (source, needle) => source.split(needle).length - 1;
const sha256 = s => createHash('sha256').update(s).digest('hex');
export function fnv32Utf16(s) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619) >>> 0;
  return h.toString(16).padStart(8, '0');
}
function requireInvariant(ok, message) { if (!ok) throw new Error('RELEASE HOLD: ' + message); }

export function prepareReview(input, { enforceSnapshot = true } = {}) {
  const page = input?.structuredContent?.data ?? input?.data ?? input;
  const raw = typeof page?.content === 'string' ? page.content : page?.content?.raw;
  requireInvariant(page?.id === BASELINE.id && page?.status === 'publish', 'must be published WordPress Page 6 edit-context export');
  requireInvariant(typeof raw === 'string' && raw.includes('<!-- wp:html -->'), 'raw Gutenberg editor source required, not WordPress rendered/view source');
  requireInvariant(page?.modified === BASELINE.modified || !enforceSnapshot, 'WordPress page changed since approved audit baseline');
  if (enforceSnapshot) requireInvariant(raw.length === BASELINE.characters && fnv32Utf16(raw) === BASELINE.fnv32, 'editor content drift; refresh exact source audit before proposing anything');
  requireInvariant(count(raw, BEFORE) === 1, 'expected original hero secondary CTA must occur exactly once');
  requireInvariant(count(raw, AFTER) === 0, 'review CTA was already applied or duplicated');
  requireInvariant(count(raw, '<span class="fv-margin-strip__item"') === BASELINE.margins, '72 historical Margins records must remain present');
  requireInvariant(count(raw, '<!-- wp:jetpack/subscriptions') === 1, 'native Jetpack signup must be intact');
  requireInvariant(CHAPTER_IDS.every(id => count(raw, 'id="' + id + '"') === 1), 'all seven unique chapter destination IDs required');
  requireInvariant(raw.includes('edit-017-v02-nypl-5003296-original.jpg'), 'NYPL image under rights review must not be silently altered');
  const primary = '<a class="fv-hf__button fv-hf__button--gold" href="#fv-hf-evidence">Enter the evidence room';
  requireInvariant(count(raw, primary) === 1, 'primary evidence-first hero action must remain');
  const replacement = raw.replace(BEFORE, AFTER);
  const pos = raw.indexOf(BEFORE);
  requireInvariant(replacement === raw.slice(0, pos) + AFTER + raw.slice(pos + BEFORE.length), 'only the one reviewed anchor may change');
  requireInvariant(count(replacement, BEFORE) === 0 && count(replacement, AFTER) === 1, 'replacement anchor must be unique');
  const sourceSha = sha256(raw), candidateSha = sha256(replacement);
  return {
    html: replacement,
    report: {
      decision: 'REVIEW ONLY / RELEASE HOLD',
      page_id: BASELINE.id, modified: page.modified,
      source_characters: raw.length, candidate_characters: replacement.length,
      source_sha256: sourceSha, candidate_sha256: candidateSha,
      changed_anchor_count: 1, diff: { before: BEFORE, after: AFTER },
      unchanged_contract: 'Seven chapters, 72 Margins, Jetpack block, primary evidence CTA, all other source bytes unchanged',
      actual_visitor_tests: 'NOT RUN; no claim of browser, Jetpack delivery, WCAG, Lighthouse or commercial conversion',
      rights: 'The existing NYPL image remains unchanged; exact-capture reuse rights UNVERIFIED',
      production_writes: false,
    },
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const inputIndex = process.argv.indexOf('--input');
    const outputIndex = process.argv.indexOf('--out');
    if (inputIndex < 0 || !process.argv[inputIndex + 1]) throw new Error('Use --input <local WordPress edit-context JSON>');
    const input = JSON.parse(fs.readFileSync(process.argv[inputIndex + 1], 'utf8'));
    const result = prepareReview(input);
    if (outputIndex >= 0) {
      if (!process.argv[outputIndex + 1]) throw new Error('Use --out <local review HTML file>');
      fs.writeFileSync(process.argv[outputIndex + 1], result.html, { flag: 'wx', mode: 0o600 });
    }
    process.stdout.write(JSON.stringify(result.report, null, 2) + '\n');
  } catch (err) {
    process.stderr.write('HOLD: ' + err.message + '\n');
    process.exitCode = 1;
  }
}
