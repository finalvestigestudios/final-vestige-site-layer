'use strict';
/*
 * Final Vestige — source-pinned, non-publishing homepage release-review builder.
 * Generates a standalone full-page browser review and a WordPress-compatible
 * BLOCK CONTENT FRAGMENT without altering the original three-direction study.
 * No WordPress API requests, deploy hooks, subscriber data or production writes.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const SOURCE_GIT_BLOB = '70ebe0d8e122048343c99a3c6adc6f7ac498ed7f';
const CHAPTERS = [
  'fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
  'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title'
];
const CASES = ['apollo', 'franklin', 'malbone'];
const ASSETS = [
  'flagship.css', 'chronicle.css', 'chronicle-lens.css', 'inquiry.css',
  'observer-lab.css', 'reading-trail.css', 'flagship.js', 'observer-lab.js',
  'chronicle-lens.js', 'reading-trail.js'
];

function count(text, needle) { return text.split(needle).length - 1; }
function check(condition, message) { if (!condition) throw new Error('RELEASE REVIEW CLOSED: ' + message); }
function blobSha(text) {
  const bytes = Buffer.from(text, 'utf8');
  return crypto.createHash('sha1').update('blob ' + bytes.length + '\0').update(bytes).digest('hex');
}
function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }

function render(html) {
  check(typeof html === 'string' && html.startsWith('<!doctype html>'), 'unexpected standalone document');
  check(count(html, '<main>') === 1 && count(html, '</main>') === 1, 'source must contain exactly one main landmark');
  check(count(html, '<div class="fv-hf"') === 1, 'source has unexpected flagship root count');
  CHAPTERS.forEach(id => check(count(html, 'id="' + id + '"') === 1, 'missing/duplicate chapter anchor: ' + id));
  CASES.forEach(id => {
    check(count(html, 'data-fv-case="' + id + '"') === 1, 'missing/duplicate evidence case: ' + id);
    check(count(html, 'data-fv-case-button="' + id + '"') === 1, 'missing/duplicate evidence control: ' + id);
  });
  check(count(html, 'data-fv-case-buttons') === 1, 'case control wrapper drift');
  check(count(html, 'data-fv-direction-choice="') === 3, 'three study directions missing');
  check(count(html, 'https://finalvestige.com/focus/') >= 2, 'Focus Fieldbook routes missing');
  check(html.includes('data-fv-home-flagship'), 'flagship enhancement target missing');

  const originalStudyComment = '<!-- ISOLATED DESIGN STUDY:';
  const commentStart = html.indexOf(originalStudyComment);
  const commentEnd = html.indexOf('-->', commentStart);
  check(commentStart >= 0 && commentEnd > commentStart, 'source review-only marker missing');
  let documentHtml = html.slice(0, commentStart) + html.slice(commentEnd + 3);

  const studioStart = documentHtml.indexOf('  <div class="fv-hf__studio"');
  const canvasStart = documentHtml.indexOf('  <div class="fv-hf__canvas">', studioStart);
  check(studioStart >= 0 && canvasStart > studioStart, 'development toolbar bounds changed');
  const removed = documentHtml.slice(studioStart, canvasStart);
  check(count(removed, 'data-fv-direction-choice="') === 3 &&
        removed.includes('DESIGN STUDY · NOT LIVE') &&
        count(removed, 'class="fv-hf__studio-controls"') === 1,
        'refusing to remove ambiguous content from source');
  documentHtml = documentHtml.slice(0, studioStart) + documentHtml.slice(canvasStart);

  const originalTitle = '<title>Find what others miss. — Final Vestige Studios / Homepage Art Direction Study</title>';
  check(count(documentHtml, originalTitle) === 1, 'source title drift');
  documentHtml = documentHtml.replace(originalTitle, '<title>Find what others miss. — Final Vestige Studios</title>');

  const draftCopy = 'A future /mind/ hub is in draft review. No affiliate offers or unverified commercial claims are included in this study.';
  check(count(documentHtml, draftCopy) === 1, 'unreviewed Mind portal draft note changed');
  documentHtml = documentHtml.replace(draftCopy, 'Our Mind &amp; Perception coverage distinguishes historical sources, independent evidence and seller claims.');

  const rootStart = documentHtml.indexOf('<div class="fv-hf"');
  const bodyEnd = documentHtml.lastIndexOf('\n</body>');
  check(rootStart >= 0 && bodyEnd > rootStart, 'source body/root boundaries changed');
  let wordpressFragment = documentHtml.slice(rootStart, bodyEnd).trim();
  check(count(wordpressFragment, '<main>') === 1 && count(wordpressFragment, '</main>') === 1, 'fragment main mismatch');
  wordpressFragment = wordpressFragment.replace('<main>', '<div class="fv-hf__story">').replace('</main>', '</div>');
  check(!wordpressFragment.includes('<main>') && !wordpressFragment.includes('</main>'), 'nested WordPress main landmark');
  check(!wordpressFragment.includes('<html') && !wordpressFragment.includes('<script '), 'fragment includes document/script tag');
  check(!documentHtml.includes('DESIGN STUDY · NOT LIVE') && !wordpressFragment.includes('data-fv-direction-choice'), 'preview controls leaked');
  CHAPTERS.forEach(id => check(count(wordpressFragment, 'id="' + id + '"') === 1, 'fragment chapter drift: ' + id));
  CASES.forEach(id => check(count(wordpressFragment, 'data-fv-case="' + id + '"') === 1, 'fragment case drift: ' + id));
  check(count(wordpressFragment, 'https://finalvestige.com/focus/') >= 2, 'fragment lost Focus links');
  return { documentHtml, wordpressFragment };
}

function makeBundle(home, outDir) {
  const source = path.join(home, 'index.html');
  const html = fs.readFileSync(source, 'utf8');
  check(blobSha(html) === SOURCE_GIT_BLOB, 'index.html Git blob is not independently reviewed exact source');
  const {documentHtml, wordpressFragment} = render(html);
  const referenced = [...html.matchAll(/(?:href|src)="\.\/([a-z-]+\.(?:css|js))"/g)].map(x => x[1]);
  check(referenced.length === ASSETS.length &&
    referenced.every((name, i) => name === ASSETS[i]), 'source references changed or extra local assets added');

  check(path.resolve(outDir) !== path.resolve(home), 'output directory must be isolated from source');
  fs.mkdirSync(outDir, {recursive: true});
  const files = Object.create(null);
  function add(name, data) {
    const bytes = Buffer.isBuffer(data) ? data : Buffer.from(data, 'utf8');
    fs.writeFileSync(path.join(outDir, name), bytes);
    files[name] = {bytes: bytes.length, sha256: sha256(bytes)};
  }
  add('index.release-review.html', documentHtml);
  add('wordpress-page-fragment.review-only.html', wordpressFragment);
  for (const name of ASSETS) add(name, fs.readFileSync(path.join(home, name)));
  const manifest = {
    kind: 'FV Experience 2.0 OFFLINE REVIEW — NOT PRODUCTION',
    sourceGitBlob: SOURCE_GIT_BLOB,
    sourceSha256: sha256(Buffer.from(html, 'utf8')),
    chapters: CHAPTERS, cases: CASES, standaloneHasMain: true,
    wordpressFragmentHasMain: false,
    environment: 'isolated static-browser artifact; WordPress/Jetpack/Assembler not certified',
    files
  };
  fs.writeFileSync(path.join(outDir, 'SOURCE_MANIFEST.json'), JSON.stringify(manifest, null, 2) + '\n');
  return manifest;
}
module.exports = {render, makeBundle, SOURCE_GIT_BLOB, CHAPTERS, CASES, ASSETS, blobSha};

if (require.main === module) {
  const outFlag = process.argv.indexOf('--out-dir');
  if (outFlag < 0 || !process.argv[outFlag + 1]) {
    process.stderr.write('Usage: node build_release_review.cjs --out-dir /private/isolated/output\n');
    process.exitCode = 2;
  } else {
    const home = path.resolve(__dirname, '..', '..');
    try {
      const manifest = makeBundle(home, path.resolve(process.argv[outFlag + 1]));
      process.stdout.write(JSON.stringify({status:'REVIEW_ONLY', source:manifest.sourceGitBlob, files:Object.keys(manifest.files).length}) + '\n');
    } catch (err) {
      process.stderr.write(String(err) + '\n');
      process.exitCode = 1;
    }
  }
}
