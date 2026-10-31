#!/usr/bin/env node
/**
 * Offline syntax preflight for inline classic JavaScript in WordPress REST
 * content.rendered HTML. Parsing does not execute page scripts or make HTTP calls.
 * This is NOT an actual browser or WordPress frontend acceptance test.
 */
import { readFileSync } from 'node:fs';
import { Script } from 'node:vm';
import { pathToFileURL } from 'node:url';

function getAttribute(attrs, name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = attrs.match(new RegExp(`(?:^|\\s)${escaped}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i'));
  return match?.[1] ?? match?.[2] ?? match?.[3] ?? null;
}

export function inspectRenderedHtml(html) {
  if (typeof html !== 'string') throw new TypeError('HTML input must be a string');
  const scripts = [];
  const rx = /<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi;
  let match;
  while ((match = rx.exec(html)) !== null) {
    const index = scripts.length + 1;
    const attrs = match[1];
    const body = match[2];
    const type = (getAttribute(attrs, 'type') ?? 'text/javascript').trim().toLowerCase();
    const source = getAttribute(attrs, 'src');
    const base = { index, type, length: body.length, status: 'PASS', entityAmpersands: (body.match(/&(?:amp|#0?38);/gi) ?? []).length };
    if (source !== null) {
      scripts.push({ ...base, status: 'SKIP_EXTERNAL' });
      continue;
    }
    if (type === 'module') {
      scripts.push({ ...base, status: 'SKIP_MODULE_BROWSER_REQUIRED' });
      continue;
    }
    if (!['text/javascript', 'application/javascript', 'text/ecmascript', 'application/ecmascript'].includes(type)) {
      scripts.push({ ...base, status: 'SKIP_NON_JS' });
      continue;
    }
    try {
      new Script(body, { filename: `inline-script-${index}.js`, displayErrors: false });
      scripts.push(base);
    } catch (error) {
      scripts.push({ ...base, status: 'SYNTAX_ERROR', error: String(error.message).slice(0, 240) });
    }
  }
  return {
    status: scripts.some(x => x.status === 'SYNTAX_ERROR') ? 'FAIL' : 'PASS',
    scripts,
    checked: scripts.filter(x => x.status === 'PASS' || x.status === 'SYNTAX_ERROR').length,
    errors: scripts.filter(x => x.status === 'SYNTAX_ERROR').length,
    skipped: scripts.filter(x => x.status.startsWith('SKIP')).length,
  };
}

export function extractRestRendered(jsonText) {
  const parsed = JSON.parse(jsonText);
  const content = parsed?.data?.content ?? parsed?.content ?? parsed?.result?.data?.content;
  if (typeof content?.rendered !== 'string') {
    throw new TypeError('REST response must include content.rendered string; raw saved source is not equivalent');
  }
  return content.rendered;
}

function cli(args) {
  if (args.length !== 2 || !['--html', '--rest'].includes(args[0])) {
    console.error('Usage: node check.mjs --html <saved-rendered-page.html> | --rest <wp-rest-response.json>');
    return 2;
  }
  let html;
  try {
    const text = readFileSync(args[1], 'utf8');
    html = args[0] === '--rest' ? extractRestRendered(text) : text;
  } catch (err) {
    console.error(`INPUT_ERROR: ${err.message}`);
    return 2;
  }
  const report = inspectRenderedHtml(html);
  console.log(JSON.stringify(report, null, 2));
  return report.errors > 0 ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exitCode = cli(process.argv.slice(2));
}
