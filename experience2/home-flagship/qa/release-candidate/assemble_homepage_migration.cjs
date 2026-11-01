'use strict';
/**
 * Build a *private, review-only* WordPress Gutenberg homepage candidate.
 * This is a selective, single-block migration: replace only the live legacy
 * studio hero with the seven-chapter fragment; all other public page bytes
 * (including Margins, Focus, Jetpack, Query blocks and schema) stay verbatim.
 * Never connects to WordPress and must never contain subscribers or WP DB data.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { attest, SHA } = require('./verify_homepage_migration.cjs');
const HERO_MARKER = '<section class="fv-studios-hero" aria-labelledby="fv-studios-title">';
const HERO_TITLE = '<h1 id="fv-studios-title">Find what others miss.</h1>';
const HTML_BLOCK = /<!-- wp:html -->([\s\S]*?)<!-- \/wp:html -->/g;
const CHAPTER_IDS = ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
const CASE_IDS = ['apollo','franklin','malbone'];
function closed(message) { throw new Error('FV SELECTIVE HOMEPAGE MIGRATION HOLD: ' + message); }
function count(text, part) { return text.split(part).length - 1; }
function expect(condition, message) { if (!condition) closed(message); }
function assertFragment(fragment, expectedFragmentSha) {
  expect(typeof fragment === 'string' && fragment.startsWith('<div class="fv-hf"') && fragment.trimEnd().endsWith('</div>'), 'not the reviewed WordPress-only flagship fragment');
  expect(/^[a-f0-9]{64}$/.test(expectedFragmentSha || ''), 'expected independent exact fragment SHA-256 required');
  expect(SHA(fragment) === expectedFragmentSha, 'fragment SHA-256 mismatch');
  expect(count(fragment, 'data-fv-home-flagship') === 1, 'unexpected flagship root count');
  expect(!/<\/?(?:html|head|body|main|header|footer)\b/i.test(fragment), 'document, main, header or footer wrapper leaked');
  expect(!/<(?:script|style|iframe|object|embed|form)\b/i.test(fragment), 'executable, CSS, or foreign form tag in Gutenberg fragment');
  expect(!/<!--\s*(?:wp:|\/wp:)/i.test(fragment), 'nested Gutenberg block comments in raw HTML fragment');
  expect(!/fv-hf__studio-controls|DESIGN STUDY\s*[·•]\s*NOT LIVE/i.test(fragment), 'development controls leaked');
  expect(!/^<div class="fv-hf"[^>]*\b(?:hidden|inert)(?:\s|=|>)/i.test(fragment), 'flagship root hidden or inert');
  for (const id of CHAPTER_IDS) expect(count(fragment, 'id="' + id + '"') === 1, 'unexpected chapter anchor '+id);
  for (const id of CASE_IDS) expect(count(fragment, 'data-fv-case="' + id + '"') === 1, 'unexpected evidence case '+id);
  expect((fragment.match(/<h1\b/gi) || []).length === 1, 'fragment must own exactly one H1');
  expect(fragment.includes('https://finalvestige.com/affiliate-disclosure/'), 'editorial disclosure missing');
}
function assemble(legacy, fragment, opts={}) {
  expect(typeof legacy === 'string' && legacy.length > 0, 'public legacy Gutenberg page is required');
  expect(/^[a-f0-9]{64}$/.test(opts.expectedLegacySha || ''), 'independently reviewed page-6 source SHA-256 required');
  expect(SHA(legacy) === opts.expectedLegacySha, 'live page source changed since review');
  assertFragment(fragment, opts.expectedFragmentSha);
  const blocks=[...legacy.matchAll(HTML_BLOCK)];
  const heroes=blocks.filter(m=>m[1].includes(HERO_MARKER) || m[1].includes(HERO_TITLE));
  expect(heroes.length === 1, 'no unique, exact legacy hero block (source drift or duplicate)');
  const hero=heroes[0];
  expect(hero[1].includes(HERO_MARKER) && hero[1].includes(HERO_TITLE), 'legacy hero structure changed');
  expect(count(hero[1], HERO_MARKER) === 1 && count(hero[1], HERO_TITLE) === 1, 'ambiguous legacy hero identity');
  expect(!/fv-margin-strip__item|wp:jetpack\/subscriptions|\/focus\//i.test(hero[1]), 'protected historical/subscription content unexpectedly inside old hero');
  expect(!/<\/?main\b/i.test(hero[1]), 'legacy hero contains main landmark');
  const candidateBlock='<!-- wp:html -->\n'+fragment.trim()+'\n<!-- /wp:html -->';
  const start=hero.index, end=hero.index+hero[0].length;
  const candidate=legacy.slice(0,start)+candidateBlock+legacy.slice(end);
  // Byte-for-byte non-hero preservation is the central safety invariant.
  expect(candidate.startsWith(legacy.slice(0,start)) && candidate.endsWith(legacy.slice(end)), 'non-hero content changed');
  expect(count(candidate,HERO_MARKER)===0 && count(candidate,HERO_TITLE)===0, 'obsolete hero survived');
  const checked=attest(legacy,candidate,{expectedLegacySha:opts.expectedLegacySha,requireSourceDigest:true});
  expect(checked.h1===1 && checked.margins===72 && checked.jetpack_original_blocks===1, 'protected blocks absent');
  return {
    candidate,
    receipt:{
      status:'SELECTIVE_GUTENBERG_CANDIDATE_REVIEW_ONLY_NOT_DEPLOYED',
      legacy_sha256:SHA(legacy),fragment_sha256:SHA(fragment),
      removed_hero_sha256:SHA(hero[0]),candidate_sha256:SHA(candidate),
      removed_hero_bytes:Buffer.byteLength(hero[0]),
      candidate_bytes:Buffer.byteLength(candidate),
      preserved_byte_prefix:Buffer.byteLength(legacy.slice(0,start)),
      preserved_byte_suffix:Buffer.byteLength(legacy.slice(end)),
      preserved_margin_items:checked.margins,original_jetpack_blocks:checked.jetpack_original_blocks,
      original_focus_links:checked.original_focus_links,chapter_anchors:checked.chapter_anchors,
      evidence_cases:checked.evidence_cases,
      caveats:['The resulting file is private review-only raw Gutenberg; no WordPress write or install',
        'Requires isolated WordPress/Assembler render and a separate verified CSS/JS staging adapter',
        'Native Jetpack fulfillment, WCAG, rights, image HTTP, Lighthouse and field CWV are NOT certified']
    }
  };
}
function cli(argv) {
  const val = k=>{const i=argv.indexOf(k);return i>=0?argv[i+1]:undefined;};
  for(const k of ['--legacy','--fragment','--legacy-sha256','--fragment-sha256','--out','--receipt'])
    expect(val(k) && !String(val(k)).startsWith('--'), 'missing '+k);
  const out=path.resolve(val('--out')), receipt=path.resolve(val('--receipt'));
  expect(out!==receipt,'candidate and receipt must be separate paths');
  expect(!fs.existsSync(out) && !fs.existsSync(receipt),'refusing overwrite of existing review output');
  const {candidate,receipt:record}=assemble(fs.readFileSync(path.resolve(val('--legacy')),'utf8'),
    fs.readFileSync(path.resolve(val('--fragment')),'utf8'),
    {expectedLegacySha:val('--legacy-sha256'),expectedFragmentSha:val('--fragment-sha256')});
  fs.writeFileSync(out,candidate,{flag:'wx',mode:0o600});
  try { fs.writeFileSync(receipt,JSON.stringify(record,null,2)+'\n',{flag:'wx',mode:0o600}); }
  catch (err) { fs.rmSync(out,{force:true}); throw err; }
  process.stdout.write(JSON.stringify({status:record.status,candidate_sha256:record.candidate_sha256,margins:record.preserved_margin_items,jetpack:record.original_jetpack_blocks})+'\n');
}
if(require.main===module) cli(process.argv.slice(2));
module.exports={assemble,assertFragment};
