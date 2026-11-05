/** Node --test: public-Page6-format synthetic fixtures only. Never uses live WP credentials. */
import test from "node:test";
import assert from "node:assert/strict";
import { inspectPage6, patchPage6, OLD_REDUCED_RULE, EXPECTED_CHAPTERS } from "./margins_page6_native_patch.mjs";

function fixture() {
  const notes = Array.from({length: 72}, (_, i) =>
    '<span class="fv-margin-strip__item" style="--i:' + i + '">Historic QA fixture ' + i + '</span>').join("");
  const chapterLinks = EXPECTED_CHAPTERS.map(id => '<a href="#' + id + '">Chapter</a>').join("");
  return '<!-- wp:html -->\n<div class="fv-margin-strip fv-margin-strip--rotator">' +
    '<div class="fv-margin-strip__inner"><div class="fv-margin-strip__label">Hidden in the Margins</div>' +
    '<div class="fv-margin-strip__window" tabindex="0" aria-live="off" aria-label="Rotating source and accountability notes">' +
    notes + '</div></div></div><style>' + OLD_REDUCED_RULE + '</style>\n' +
    '<!-- /wp:html --><!-- wp:html -->' + chapterLinks +
    '<a href="/focus/">Focus</a>'.repeat(4) +
    '<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->' +
    '<!-- /wp:html --><!-- wp:paragraph --><p>Unrelated editorial block.</p><!-- /wp:paragraph -->';
}
const expectHold = (change, re = /REVIEW HOLD/) =>
  assert.throws(() => patchPage6(change(fixture())), re);

test("native Page6-format example admits exactly 72 nonempty ordered records", () => {
  const a = inspectPage6(fixture());
  assert.equal(a.records.length, 72);
  assert.equal(a.focusLinks, 4);
});
test("patch retains 72 exact historical texts and all unrelated Gutenberg bytes", () => {
  const source = fixture(), result = patchPage6(source);
  const end = "<!-- /wp:html -->";
  assert.equal(result.html.slice(result.html.indexOf(end)), source.slice(source.indexOf(end)));
  assert.deepEqual([...result.html.matchAll(/style="--i:(\d+)">([^<]+)<\/span>/g)].map(x => x[2]), inspectPage6(source).records);
  assert.equal(result.receipt.record_count, 72);
});
test("patch restores reduced-motion fragment visibility with bounded x-scroll and no animation", () => {
  const text = patchPage6(fixture()).html;
  assert.match(text, /@media\(prefers-reduced-motion:reduce\)\{/);
  assert.match(text, /overflow-x:auto;overflow-y:hidden/);
  assert.match(text, /display:block;position:relative;flex:0 0 clamp/);
  assert.match(text, /animation:none/);
  assert.doesNotMatch(text, /nth-child\(1\)\{display:block\}/);
  assert.doesNotMatch(text, /transition:[^;]+/);
});
test("visible user instruction and neutral accessible label survive, no scripts added", () => {
  const s = patchPage6(fixture()).html;
  assert.match(s, /Scroll or swipe to browse all 72 notes/);
  assert.match(s, /aria-label="72 Hidden in the Margins historical notes"/);
  assert.doesNotMatch(s, /<script/);
});
test("repeat application fails closed instead of duplicating CSS", () => {
  assert.throws(() => patchPage6(patchPage6(fixture()).html), /REVIEW HOLD/);
});
test("first Gutenberg block must contain the exact legacy rule", () =>
  expectHold(s => s.replace(OLD_REDUCED_RULE, "@media(prefers-reduced-motion:reduce){}")));
test("missing first 72-source fragment fails", () =>
  expectHold(s => s.replace(/<span class="fv-margin-strip__item" style="--i:0">[^<]*<\/span>/, "")));
test("unexpected 73rd fragment fails", () =>
  expectHold(s => s.replace('style="--i:71">', 'style="--i:72">').replace('style="--i:70">','style="--i:71">')));
test("duplicate fragment index fails", () =>
  expectHold(s => s.replace('style="--i:37">','style="--i:36">')));
test("empty historical note fails", () =>
  expectHold(s => s.replace("Historic QA fixture 19", "   ")));
test("fragment markup mutation fails", () =>
  expectHold(s => s.replace('class="fv-margin-strip__item" style="--i:9"', 'style="--i:9" class="fv-margin-strip__item"')));
test("unexpected first Gutenberg wrapper fails", () =>
  expectHold(s => s.replace('<!-- wp:html -->\n', '<!-- wp:paragraph -->\n')));
test("source aria-label mutation fails", () =>
  expectHold(s => s.replace('aria-label="Rotating source and accountability notes"', 'aria-label="Different"')));
test("source visual label mutation fails", () =>
  expectHold(s => s.replace(">Hidden in the Margins</div>", ">Unexpected</div>")));
test("missing Jetpack subscription form fails", () =>
  expectHold(s => s.replace('wp:jetpack/subscriptions', 'wp:jetpack/other')));
test("duplicated Jetpack subscription markup fails", () =>
  expectHold(s => s.replace('<!-- wp:jetpack/subscriptions', '<!-- wp:jetpack/subscriptions') + '<!-- wp:jetpack/subscriptions />'));
test("missing key flagship chapter destination fails", () =>
  expectHold(s => s.replace('href="#fv-hf-mind-title"','href="#removed-observer"')));
test("third-party Focus link substitution fails", () =>
  expectHold(s => s.replace('href="/focus/"','href="https://example.org/focus/"')));
test("future content after first block is byte-identical under transformation", () => {
  const source = fixture() + '<!-- wp:html --><a href="/terms/">New source material</a><!-- /wp:html -->';
  const result = patchPage6(source);
  assert.ok(result.html.endsWith('<!-- wp:html --><a href="/terms/">New source material</a><!-- /wp:html -->'));
});
test("other Gutenberg tail text untouched when containing confusing CSS", () => {
  const source = fixture() + "<!-- wp:paragraph --><p>" + OLD_REDUCED_RULE + "</p><!-- /wp:paragraph -->";
  const result = patchPage6(source);
  assert.ok(result.html.endsWith("<p>" + OLD_REDUCED_RULE + "</p><!-- /wp:paragraph -->"));
});
