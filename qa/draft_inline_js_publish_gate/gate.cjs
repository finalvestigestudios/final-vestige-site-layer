#!/usr/bin/env node
'use strict';
/* Read-only, offline pre-publication syntax gate for sanitized WordPress snapshots.
   Input may contain private draft page text: never log/commit the input file. */
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const MAX_INPUT = 12 * 1024 * 1024;
const MAX_HTML = 2 * 1024 * 1024;
const MAX_PAGES = 250;
const MAX_SCRIPTS = 100;
const SCRIPT_RE = /<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi;

function inspect(html) {
  if (typeof html !== 'string' || Buffer.byteLength(html) > MAX_HTML) throw new Error('invalid_or_oversized_html');
  const scripts = [];
  for (const match of html.matchAll(SCRIPT_RE)) {
    if (scripts.length >= MAX_SCRIPTS) throw new Error('too_many_scripts');
    const attrs = match[1];
    const src = /(?:^|\s)src\s*=/i.test(attrs);
    const type = (attrs.match(/(?:^|\s)type\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i) || []).slice(1).find(Boolean) || '';
    const isJSON = /^(?:application\/ld\+json|application\/json)$/i.test(type);
    const js = !type || /^(?:text|application)\/javascript$/i.test(type);
    let result = 'not_executable';
    if (src) result = 'external_unverified';
    else if (isJSON) {
      try { JSON.parse(match[2]); result = 'valid_json'; } catch { result = 'invalid_json'; }
    } else if (js) {
      try { new vm.Script(match[2], { filename: 'private-inline-script.js' }); result = 'valid_js'; }
      catch { result = 'invalid_js'; }
    } else if (type === 'module') result = 'module_unverified';
    scripts.push({ result, type: type.toLowerCase() });
  }
  // A malformed/nonclosed script tag cannot simply disappear from the audit.
  const starts = (html.match(/<script\b/gi) || []).length;
  if (starts !== scripts.length) throw new Error('unclosed_script_tag');
  return scripts;
}

function evaluate(snapshot) {
  if (!snapshot || !Array.isArray(snapshot.pages) || !snapshot.pages.length || snapshot.pages.length > MAX_PAGES) {
    throw new Error('invalid_page_set');
  }
  const failures = [];
  let checkedScripts = 0;
  let draftCount = 0;
  for (const p of snapshot.pages) {
    if (!Number.isInteger(p.id) || p.id <= 0 || !['draft', 'pending', 'future', 'private'].includes(p.status)) {
      throw new Error('invalid_draft_metadata');
    }
    draftCount++;
    const saved = inspect(p.saved_html);
    const rendered = inspect(p.rendered_html);
    checkedScripts += Math.max(saved.length, rendered.length);
    if (saved.length !== rendered.length) {
      failures.push({ page_id: p.id, kind: 'script_count_changed', saved: saved.length, rendered: rendered.length });
      continue;
    }
    for (let i = 0; i < saved.length; i++) {
      const a = saved[i], b = rendered[i];
      if (a.type !== b.type) failures.push({ page_id: p.id, script_index: i, kind: 'script_type_changed' });
      else if (a.result === 'invalid_js' || a.result === 'invalid_json') failures.push({ page_id: p.id, script_index: i, kind: 'saved_syntax_invalid' });
      else if (b.result === 'invalid_js' || b.result === 'invalid_json') failures.push({ page_id: p.id, script_index: i, kind: 'rendered_syntax_invalid' });
      else if (a.result === 'module_unverified' || b.result === 'module_unverified') failures.push({ page_id: p.id, script_index: i, kind: 'module_unverified' });
      else if (a.result !== b.result) failures.push({ page_id: p.id, script_index: i, kind: 'script_classification_changed' });
    }
  }
  return { status: failures.length ? 'HOLD' : 'PASS', scope: 'source_syntax_only_not_browser', draft_pages: draftCount, inline_scripts_checked: checkedScripts, failures };
}

function main(argv) {
  if (argv.length !== 1) throw new Error('usage: node gate.cjs private-snapshot.json');
  const file = path.resolve(argv[0]);
  if (!fs.statSync(file).isFile() || fs.statSync(file).size > MAX_INPUT) throw new Error('invalid_or_oversized_input');
  const receipt = evaluate(JSON.parse(fs.readFileSync(file, 'utf8')));
  process.stdout.write(JSON.stringify(receipt) + '\n');
  return receipt.status === 'PASS' ? 0 : 1;
}
if (require.main === module) {
  try { process.exitCode = main(process.argv.slice(2)); }
  catch (err) {
    process.stderr.write(JSON.stringify({ status: 'HOLD', scope: 'source_syntax_only_not_browser', error: 'input_rejected' }) + '\n');
    process.exitCode = 2;
  }
}
module.exports = { inspect, evaluate };
