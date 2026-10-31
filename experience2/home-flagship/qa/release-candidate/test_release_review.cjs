'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const {
  render, makeBundle, blobSha, SOURCE_GIT_BLOB, CHAPTERS, CASES, ASSETS, ASSET_GIT_BLOBS
} = require('./build_release_review.cjs');

const home = path.resolve(__dirname, '..', '..');
const input = fs.readFileSync(path.join(home, 'index.html'), 'utf8');
function count(s, text) { return s.split(text).length - 1; }
function rejected(source, reason) {
  assert.throws(() => render(source), /RELEASE REVIEW CLOSED/, reason);
}

test('actual source is the pinned Git blob, not a moving latest branch', () => {
  assert.equal(blobSha(input), SOURCE_GIT_BLOB);
});

test('standalone review is a complete HTML document and contains no developer bar', () => {
  const {documentHtml} = render(input);
  assert.match(documentHtml, /^<!doctype html>/);
  assert.equal(count(documentHtml, '<main>'), 1);
  assert.equal(count(documentHtml, '</main>'), 1);
  assert.doesNotMatch(documentHtml, /DESIGN STUDY · NOT LIVE|data-fv-direction-choice=/);
  assert.match(documentHtml, /<title>Find what others miss\. — Final Vestige Studios<\/title>/);
});

test('WordPress fragment avoids a nested main and includes no script/document element', () => {
  const {wordpressFragment} = render(input);
  assert.match(wordpressFragment, /^<div class="fv-hf"/);
  assert.doesNotMatch(wordpressFragment, /<main>|<\/main>|<html|<script /);
  assert.match(wordpressFragment, /class="fv-hf__story"/);
  assert.match(wordpressFragment, /fv-hf__footer/);
});

test('all seven chapters, evidence cases and native fallback exist in WordPress fragment', () => {
  const {wordpressFragment: frag} = render(input);
  for (const id of CHAPTERS) assert.equal(count(frag, 'id="' + id + '"'), 1, id);
  for (const id of CASES) {
    assert.equal(count(frag, 'data-fv-case="' + id + '"'), 1, id);
    assert.equal(count(frag, 'data-fv-case-button="' + id + '"'), 1, id);
  }
  assert.match(frag, /data-fv-case-buttons hidden/);
  assert.ok(count(frag, 'https://finalvestige.com/focus/') >= 2);
  assert.match(frag, /https:\/\/finalvestige\.com\/affiliate-disclosure\//);
  assert.doesNotMatch(frag, /affiliate_id=|inspire3\.com\/checkout/i);
});

test('source remains a three-direction review even when the release view hides controls', () => {
  assert.equal(count(input, 'data-fv-direction-choice="'), 3);
  assert.equal(count(render(input).documentHtml, 'data-fv-direction-choice="'), 0);
  assert.equal(count(render(input).documentHtml, 'data-fv-direction="dossier"'), 1);
});

test('reject missing chapter', () => {
  rejected(input.replace('id="fv-hf-mind-title"', 'id="missing"'));
});
test('reject duplicate chapter identifier', () => {
  rejected(input.replace('id="fv-hf-title"', 'id="fv-hf-title" id="fv-hf-title"'));
});
test('reject missing evidence panel', () => {
  rejected(input.replace('data-fv-case="malbone"', 'data-fv-case="not-malbone"'));
});
test('reject missing evidence button', () => {
  rejected(input.replace('data-fv-case-button="apollo"', 'data-fv-case-button="not-apollo"'));
});
test('reject changed developer-bar boundaries', () => {
  rejected(input.replace('class="fv-hf__studio"', 'class="drift"'));
});
test('reject changed Mind bridge editorial note', () => {
  rejected(input.replace('A future /mind/ hub is in draft review.', 'Unsupported new claim.'));
});
test('reject Focus path loss', () => {
  rejected(input.replaceAll('https://finalvestige.com/focus/', 'https://example.invalid/focus/'));
});

test('real local bundle copies only referenced first-party JS/CSS with SHA-256 checksums', () => {
  const parentDir = fs.mkdtempSync(path.join(os.tmpdir(), 'fv-ex2-local-review-'));
  const outDir = path.join(parentDir, 'private-bundle');
  try {
    const manifest = makeBundle(home, outDir);
    assert.equal(manifest.sourceGitBlob, SOURCE_GIT_BLOB);
    assert.deepEqual(manifest.assetGitBlobs, ASSET_GIT_BLOBS);
    assert.equal(Object.keys(manifest.files).length, ASSETS.length + 2);
    assert.equal(manifest.wordpressFragmentHasMain, false);
    assert.equal(manifest.standaloneHasMain, true);
    for (const [name, entry] of Object.entries(manifest.files)) {
      const bytes = fs.readFileSync(path.join(outDir, name));
      assert.equal(entry.bytes, bytes.length, name);
      assert.equal(entry.sha256, crypto.createHash('sha256').update(bytes).digest('hex'), name);
    }
    assert.deepEqual(
      JSON.parse(fs.readFileSync(path.join(outDir, 'SOURCE_MANIFEST.json'), 'utf8')),
      manifest
    );
  } finally {
    fs.rmSync(parentDir, {recursive: true, force: true});
  }
});

test('refuse writing a review bundle into the source directory', () => {
  assert.throws(() => makeBundle(home, home), /RELEASE REVIEW CLOSED/);
});

test('corrupted first-party JS blocks release without leaving partial output', () => {
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'fv-ex2-bad-asset-'));
  const output = path.join(scratch, 'output');
  try {
    fs.copyFileSync(path.join(home, 'index.html'), path.join(scratch, 'index.html'));
    for (const asset of ASSETS) fs.copyFileSync(path.join(home, asset), path.join(scratch, asset));
    fs.appendFileSync(path.join(scratch, 'flagship.js'), '\n// unreviewed mutation\n');
    assert.throws(() => makeBundle(scratch, output), /asset Git blob drift: flagship.js/);
    assert.equal(fs.existsSync(output), false, 'half-written release output not allowed');
  } finally {
    fs.rmSync(scratch, {recursive: true, force: true});
  }
});

test('refuse overwriting an existing preview tree', () => {
  const existing = fs.mkdtempSync(path.join(os.tmpdir(), 'fv-ex2-existing-'));
  try {
    assert.throws(() => makeBundle(home, existing), /already exists/);
  } finally {
    fs.rmSync(existing, {recursive:true, force:true});
  }
});
