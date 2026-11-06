'use strict';
/* EX2 source gate: full 72-item archival record parity + opt-in CSS-only motion.
 * This is a source admission check, NOT browser/WCAG/WordPress certification.
 * Usage: node experience2/home-flagship/playground/verify_opt_in_margins_motion.cjs
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const blueprintPath = path.join(__dirname, 'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json');
const raw = fs.readFileSync(blueprintPath, 'utf8');
const blueprint = JSON.parse(raw);
const plugin = blueprint.steps.find(s => s.step === 'writeFile' && s.path.endsWith('/fv-ex2-playground-review.php'));
if (!plugin) throw Error('Missing exact MU-plugin review source');

function audit(text) {
  const out = [];
  const sourceItems = [...text.matchAll(/<span class="fv-margin-strip__item" style="--i:(\d+)">([^<]*)<\/span>/g)];
  const css = text.slice(text.indexOf('/* EX2 REVIEW ONLY — Issues #150/#820'), text.indexOf('FVPG_CSS_END'));
  const markup = text.slice(text.indexOf('<div class="fv-margin-strip fv-margin-strip--rotator"'), text.indexOf('<div class="fv-hf" data-fv-home-flagship>'));
  const check = (cond, name) => { if (!cond) out.push(name); };
  check(sourceItems.length === 72, 'all 72 records');
  check(sourceItems.every((m, n) => Number(m[1]) === n && m[2].trim()), 'records sequential and nonempty');
  check(markup.includes('class="fv-margin-strip__motion-check" type="checkbox"'), 'native motion choice');
  check(markup.includes('Animate fragments (optional)'), 'user-facing choice');
  check(markup.includes('scroll horizontally'), 'accessible scroll instruction');
  check(css.includes('animation:none;') && css.includes('overflow-x:auto'), 'static scroll by default');
  check(css.includes('scroll-snap-type:x proximity'), 'touch browsing');
  check(css.includes('selector(.fv-margin-strip:has('), 'opt-in CSS feature detection');
  check(css.includes('prefers-reduced-motion: no-preference'), 'motion only with user preference');
  check(css.includes(':has(.fv-margin-strip__motion-check:checked) .fv-margin-strip__item'), 'opt-in animation selector');
  check(css.includes('prefers-reduced-motion: reduce'), 'reduced-motion safeguard');
  check(css.indexOf('animation:none;') < css.indexOf('animation:fvMarginReveal'), 'static-first cascade');
  check(text.includes('FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1'), 'isolated WordPress marker');
  check(!/wp:jetpack\/subscriptions/.test(markup), 'no cloned subscriber form');
  check(text.includes('href="https://finalvestige.com/focus/"'), 'existing Focus destination');
  for (const id of ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'])
    check(text.includes('id="'+id+'"'), 'chapter '+id);
  return out;
}
const source = plugin.data;
assert.deepEqual(audit(source), [], 'exact candidate source must qualify');
const mutations = [
  ['remove last record', s => s.replace(/<span class="fv-margin-strip__item" style="--i:71">[^<]*<\/span>/, '')],
  ['change index', s => s.replace('style="--i:20"', 'style="--i:21"')],
  ['erase motion checkbox', s => s.replace('class="fv-margin-strip__motion-check" type="checkbox"', '')],
  ['erase scroll cue', s => s.replace('scroll horizontally', '')],
  ['erase no-preference', s => s.replace('prefers-reduced-motion: no-preference', 'prefers-reduced-motion: reduce')],
  ['erase static animation guard', s => s.replace('animation:none; will-change:auto;', 'animation:fvMarginReveal 360s linear infinite; will-change:auto;')],
  ['erase native review marker', s => s.replaceAll('FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1', 'UNSAFE-PRODUCTION-COPY')],
  ['erase Focus link', s => s.replaceAll('href="https://finalvestige.com/focus/"', 'href="#"')]
];
for (const [label, fn] of mutations) assert.notDeepEqual(audit(fn(source)), [], label+' should be rejected');
console.log('EX2_ARCHIVAL_MOTION_SOURCE_PASS 1 exact source + '+mutations.length+' rejected mutants');
