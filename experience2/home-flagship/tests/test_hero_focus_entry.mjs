/** EX2 homepage entry-path contract. Exact source checkout, offline Node --test.
 * No WordPress operations, no analytics writes, no merchant assertions. */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const home = dirname(dirname(fileURLToPath(import.meta.url)));
const html = readFileSync(join(home, "index.html"), "utf8");
const css = readFileSync(join(home, "flagship.css"), "utf8");
const chapters = [
  "fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence", "fv-hf-inquiry",
  "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title"
];
const HERO_START = '<div class="fv-hf__opening-actions">';
function heroActions(source) {
  assert.equal(source.split(HERO_START).length - 1, 1, "one hero action group");
  return source.split(HERO_START)[1].split("</div>")[0];
}
function links(source) {
  return [...heroActions(source).matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)]
    .map(m => ({ href: m[1], label: m[2].replace(/<[^>]+>/g,"").trim() }));
}
function verifyHero(source) {
  const found = links(source);
  assert.equal(found.length, 2, "no extra competing hero CTAs");
  assert.equal(found[0].href, "#fv-hf-evidence", "evidence remains primary");
  assert.equal(found[1].href, "https://finalvestige.com/focus/", "free resource contextual secondary");
  assert.match(found[1].label, /free 52-page Focus Fieldbook/i, "specific verified offer");
  assert.match(heroActions(source), /fv-hf__text-link--focus/, "touch-target class attached");
}
function verifyChapters(source) {
  for(const id of chapters) assert.ok(source.includes('href="#'+id+'"'), "lost chapter "+id);
}
function verifyCss(source) {
  const rule = source.match(/\.fv-hf \.fv-hf__text-link--focus\s*\{([^}]+)\}/)?.[1] ?? "";
  assert.match(rule, /min-height:\s*44px\s*;/, "44px touch target missing");
  assert.match(rule, /max-width:\s*100%\s*;/, "mobile width cap missing");
  assert.match(rule, /overflow-wrap:\s*anywhere\s*;/, "200%-zoom wrap protection missing");
  assert.match(source, /@media\s*\(max-width:\s*600px\)[\s\S]*?\.fv-hf \.fv-hf__text-link--focus\s*\{\s*width:\s*100%\s*;/);
}
test("hero keeps evidence-primary and adds one precise free reader action", () => verifyHero(html));
test("exact seven chapter rail destinations preserved", () => verifyChapters(html));
test("authentic Royal Museums Greenwich source link preserved", () =>
  assert.ok(html.includes("https://www.rmg.co.uk/collections/objects/rmgc-object-504898")));
test("editorial navigation remains available outside the hero", () =>
  assert.ok(html.includes('href="https://finalvestige.com/blog/"')));
test("the Focus offer stays a normal href with no popup or JS requirement", () => {
  assert.match(heroActions(html), /href="https:\/\/finalvestige\.com\/focus\/"/);
  assert.doesNotMatch(heroActions(html), /onclick=|target="_blank"|data-affiliate=/i);
});
test("44px Focus tap target, width containment and reduced-motion source retained", () => {
  verifyCss(css);
  assert.match(css, /prefers-reduced-motion/);
});
test("negative control: merchant/unverified offer cannot replace free Focus", () =>
  assert.throws(() => verifyHero(html.replace('href="https://finalvestige.com/focus/">Explore the free 52-page', 'href="https://example.com/paid/">Explore the free 52-page'))));
test("negative control: missing explicit 52-page resource label fails", () =>
  assert.throws(() => verifyHero(html.replace("Explore the free 52-page Focus Fieldbook", "Learn More"))));
test("negative control: primary evidence action cannot be removed", () =>
  assert.throws(() => verifyHero(html.replace('href="#fv-hf-evidence">Enter the evidence room','href="#irrelevant">Enter the evidence room'))));
test("negative control: missing chapter destination fails", () =>
  assert.throws(() => verifyChapters(html.replace('href="#fv-hf-mind-title"','href="#not-chapter"'))));
test("negative control: undersized touch target fails", () =>
  assert.throws(() => verifyCss(css.replace(/(\.fv-hf \.fv-hf__text-link--focus\s*\{[^}]*?)min-height: 44px;/, "$1min-height: 20px;"))));
test("negative control: a non-wrapping zoom-clipped CTA fails", () =>
  assert.throws(() => verifyCss(css.replace("overflow-wrap: anywhere;", "overflow-wrap: normal;"))));
