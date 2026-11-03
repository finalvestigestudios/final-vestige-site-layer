#!/usr/bin/env node
/**
 * EX2: synthetic Gutenberg-source persistence using real WordPress Playground.
 * NO WordPress.com API, production export, secret, subscriber data, or public write.
 * Does not claim Gutenberg browser-editor save or Assembler-host parity.
 */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import { runCLI } from '@wp-playground/cli';

const here = dirname(fileURLToPath(import.meta.url));
const flag = process.argv.indexOf('--candidate');
const mflag = process.argv.indexOf('--manifest');
if (flag < 0 || mflag < 0 || !process.argv[flag + 1] || !process.argv[mflag + 1]) {
  throw new Error('Expected --candidate FILE --manifest FILE (synthetic ONLY)');
}
const candidatePath = resolve(process.argv[flag + 1]);
const manifestPath = resolve(process.argv[mflag + 1]);
assert.notEqual(candidatePath, manifestPath, 'Manifest and candidate paths overlap');
const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
assert.equal(manifest.data_classification, 'SYNTHETIC_TEST_FIXTURE_ONLY');
assert.equal(manifest.page6_live_content_included, false);
assert.equal(manifest.release, 'HOLD');
const candidate = await readFile(candidatePath);
const digest = createHash('sha256').update(candidate).digest('hex');
assert.equal(manifest.candidate_sha256, digest, 'Fixture digest does not match manifest');
assert.equal(manifest.candidate_bytes, candidate.byteLength);
assert.equal(manifest.margin_items, 72);
assert.ok(manifest.gutenberg_custom_html_blocks >= 2);
assert.equal(manifest.jetpack_block_comments, 1);
assert.equal(manifest.nypl_record_links, 2);
const phpProbe = await readFile(join(here, 'playground_core_save_readback.php'), 'utf8');

let server;
try {
  server = await runCLI({
    command: 'server',
    wp: '6.8',
    php: '8.3',
    port: 9472,
    login: false,
  });
  const url = new URL(server.serverUrl);
  assert.ok(['127.0.0.1', 'localhost', '::1'].includes(url.hostname), 'Server must be loopback-only');
  await server.playground.writeFile('/wordpress/wp-content/fv-ex2-synthetic-only.marker', 'SYNTHETIC_TEST_FIXTURE_ONLY\n');
  await server.playground.writeFile('/wordpress/wp-content/fv-ex2-synthetic-candidate.html', candidate);
  await server.playground.writeFile('/wordpress/fv_ex2_qa_once.php', phpProbe);
  const resultUrl = new URL('/fv_ex2_qa_once.php', url);
  // A redirect is not a successful probe. Allow only a single canonical
  // loopback host alias correction to the SAME PHP file and port; never a
  // login page, off-origin URL or changed query. Do not log any secret URL.
  let response = await fetch(resultUrl, { signal: AbortSignal.timeout(90000), redirect: 'manual' });
  if ([301,302,303,307,308].includes(response.status)) {
    const location = response.headers.get('location') || '';
    let target;
    try { target = new URL(location, resultUrl); } catch {
      throw new Error('Playground redirected to an invalid target, HTTP ' + response.status);
    }
    const local = target.protocol === 'http:' &&
      ['127.0.0.1','localhost','[::1]'].includes(target.hostname);
    if (!local || target.port !== resultUrl.port ||
        target.pathname !== resultUrl.pathname || target.search || target.username || target.password) {
      throw new Error('Playground PHP route redirect denied: HTTP ' + response.status +
        ', destination PATH=' + target.pathname + ' (no query or credentials logged)');
    }
    response = await fetch(target, { signal: AbortSignal.timeout(90000), redirect: 'error' });
  }
  const responseText = await response.text();
  let result;
  try {
    result = JSON.parse(responseText);
  } catch {
    throw new Error('WordPress core probe did not return JSON; HTTP ' + response.status);
  }
  assert.equal(response.status, 200, 'WordPress core probe HTTP failure: ' + JSON.stringify(result));
  assert.equal(result.result, 'PASS', JSON.stringify(result));
  assert.equal(result.data_class, 'SYNTHETIC_TEST_FIXTURE_ONLY');
  assert.equal(result.source_sha256, digest);
  assert.equal(result.stored_sha256, digest);
  assert.equal(result.test_type, 'WORDPRESS_CORE_DRAFT_SAVE_READBACK_NOT_GUTENBERG_EDITOR');
  assert.equal(result.release, 'HOLD');
  for (const [key, value] of Object.entries(result.checks)) {
    assert.equal(value, true, 'WordPress core preservation failure: ' + key);
  }
  // Only small synthetic-safe metadata is emitted. No page content or WordPress DB.
  console.log(JSON.stringify(result, null, 2));
} finally {
  if (server) {
    await server[Symbol.asyncDispose]();
  }
}
