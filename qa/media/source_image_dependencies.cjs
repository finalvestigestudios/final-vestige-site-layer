'use strict';
// Offline WordPress Gutenberg source audit. Never fetches or modifies websites/assets.
const fs = require('node:fs');
const { URL } = require('node:url');
const BASE = 'https://finalvestige.com';
const KINDS = ['first_party', 'jetpack_proxy', 'external', 'redirect_image', 'drive_thumbnail', 'non_http', 'missing_src'];

function imageTags(content) {
  const html = String(content || '').replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, '')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi, '');
  return html.match(/<img\b[^>]*>/gi) || [];
}
function attribute(tag, name) {
  const re = new RegExp('\\b' + name + '\\s*=\\s*(["\\\'])([\\s\\S]*?)\\1', 'i');
  return tag.match(re)?.[2] ?? null;
}
function classify(src) {
  if (src === null || !String(src).trim()) return 'missing_src';
  let u;
  try { u = new URL(String(src).trim().replace(/&amp;/gi, '&'), BASE); }
  catch { return 'non_http'; }
  if (u.protocol !== 'http:' && u.protocol !== 'https:') return 'non_http';
  const h = u.hostname.toLowerCase().replace(/^www\./, '');
  if (h === 'finalvestige.com') return 'first_party';
  if (/^i[012]\.wp\.com$/.test(h) && /^\/finalvestige\.com(?:\/|$)/i.test(u.pathname)) return 'jetpack_proxy';
  if (h === 'drive.google.com' && u.pathname === '/thumbnail') return 'drive_thumbnail';
  if (h === 'commons.wikimedia.org' && u.pathname.startsWith('/wiki/Special:Redirect/')) return 'redirect_image';
  return 'external';
}
function audit(input) {
  if (!input || !Array.isArray(input.pages) || input.pages.length > 500) throw Error('Expected {pages: [...]} (maximum 500)');
  const counts = Object.fromEntries(KINDS.map(k => [k, 0]));
  const rows = []; let total = 0;
  for (const page of input.pages) {
    if (!page || typeof page.content !== 'string' || page.content.length > 300000 || typeof page.url !== 'string') throw Error('Invalid page record');
    const tags = imageTags(page.content); total += tags.length;
    if (total > 5000) throw Error('Too many images');
    const item = Object.fromEntries(KINDS.map(k => [k, 0]));
    for (const tag of tags) { const k = classify(attribute(tag, 'src')); counts[k]++; item[k]++; }
    const offsite = item.external + item.redirect_image + item.drive_thumbnail;
    const ratio = tags.length ? offsite / tags.length : 0;
    rows.push({ id: page.id ?? null, url: page.url, images: tags.length, offsite, offsite_ratio: +ratio.toFixed(3), review: tags.length >= 4 && ratio >= 0.75 });
  }
  return { method: 'WordPress stored markup only (not rendered/browser HTTP)', http_verified: false,
    image_count: total, counts, offsite_count: counts.external + counts.redirect_image + counts.drive_thumbnail,
    pages_scanned: rows.length, review_pages: rows.filter(p => p.review), rows };
}
if (require.main === module) {
  try {
    if (process.argv.length !== 3) throw Error('Usage: node source_image_dependencies.cjs snapshot.json');
    const file = process.argv[2];
    if (fs.statSync(file).size > 8 * 1024 * 1024) throw Error('Input exceeds 8 MiB');
    console.log(JSON.stringify(audit(JSON.parse(fs.readFileSync(file, 'utf8'))), null, 2));
  } catch (error) { console.error('IMAGE_QA_INPUT_ERROR: ' + error.message); process.exitCode = 2; }
}
module.exports = { imageTags, attribute, classify, audit };
