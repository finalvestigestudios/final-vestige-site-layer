/* Run with: node --test measurement/ga4-funnel-v1/test-funnel.cjs */
"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const api = require("./fv-conversion-events.js");
const source = fs.readFileSync(path.join(__dirname, "fv-conversion-events.js"), "utf8");

test("Mini Museum creative maps to outbound, not a purchase", () => {
  const x = api.classifyHref("https://www.awin1.com/cread.php?s=4236132&v=89949&r=3055117", "/collection/");
  assert.equal(x.event, "fv_affiliate_outbound");
  assert.equal(x.params.fv_offer, "mini_museum");
  assert.equal(JSON.stringify(x).includes("3055117"), false);
});
test("Suunto AWIN maps to Suunto, not Mini Museum", () => {
  assert.equal(api.classifyHref("https://www.awin1.com/cread.php?awinmid=125352", "/collection/").params.fv_offer, "suunto");
});
test("Unclassified AWIN never infers a merchant", () => {
  assert.equal(api.classifyHref("https://www.awin1.com/cread.php?s=999", "/collection/").params.fv_offer, "other_awin");
});
test("Payhip outbound is a handoff, never a purchase", () => {
  assert.equal(api.classifyHref("https://payhip.com/b/ABCDE", "/collection/").event, "fv_checkout_handoff");
});
test("Focus entrance is tracked only off-page", () => {
  assert.equal(api.classifyHref("/focus/?utm_source=tiktok", "/collection/").event, "fv_focus_entry");
  assert.equal(api.classifyHref("/focus/", "/focus/"), null);
});
test("Article-to-Focus is separately classified", () => {
  assert.equal(api.classifyHref("/focus/", "/2026/11/02/piri-reis-map/").event, "fv_article_to_resource");
});
test("PDF click is not a confirmed email signup", () => {
  const x = api.classifyHref("https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf", "/focus/");
  assert.equal(x.event, "fv_fieldbook_pdf_click");
});
test("Excludes arbitrary external and unsafe schemes", () => {
  assert.equal(api.classifyHref("https://example.com/path?email=private", "/"), null);
  assert.equal(api.classifyHref("javascript:alert(1)", "/"), null);
});
test("No URL, emails, UTMs or tracking query strings emitted", () => {
  const x = api.classifyHref("https://www.awin1.com/cread.php?s=4236132&email=secret%40example.com&utm_source=secret", "/collection/");
  assert.deepEqual(Object.keys(x.params).sort(), ["fv_offer", "fv_page_group"]);
  assert.equal(JSON.stringify(x).includes("secret"), false);
});
test("Known page grouping uses a fixed vocabulary", () => {
  assert.equal(api.pageGroup("/free-resources/"), "library");
  assert.equal(api.pageGroup("/"), "home");
  assert.equal(api.pageGroup("/unknown-route/?email=foo"), "other");
});

function createContext(pathname, withTag = true) {
  const handlers = {};
  const calls = [];
  const doc = { addEventListener(name, listener) { (handlers[name] ||= []).push(listener); } };
  const root = { location: { pathname } };
  if (withTag) root.gtag = (...args) => calls.push(args);
  const context = { window: root, document: doc, URL, module: { exports: {} } };
  vm.runInNewContext(source, context);
  return { root, doc, handlers, calls, context };
}
function anchorClick(href) { return { target: { closest(selector) {
  assert.equal(selector, "a[href]");
  return { href };
} } }; }
test("One click sends exactly one event; no navigation interference", () => {
  const c = createContext("/collection/");
  vm.runInNewContext(source, c.context); // accidental double inclusion
  assert.equal(c.handlers.click.length, 1);
  c.handlers.click[0](anchorClick("https://www.awin1.com/cread.php?s=4236132"));
  assert.equal(c.calls.length, 1);
  assert.equal(c.calls[0][1], "fv_affiliate_outbound");
});
test("No gtag means no event and no alternate network transport", () => {
  const c = createContext("/collection/", false);
  c.handlers.click[0](anchorClick("https://www.awin1.com/cread.php?s=4236132"));
  assert.equal(c.calls.length, 0);
});
test("Only Jetpack Focus form submit attempts are sent", () => {
  const c = createContext("/focus/");
  c.handlers.submit[0]({ target: { closest: () => ({}) } });
  assert.equal(c.calls[0][1], "fv_subscribe_submit_attempt");
  const d = createContext("/collection/");
  d.handlers.submit[0]({ target: { closest: () => ({}) } });
  assert.equal(d.calls.length, 0);
});
test("Click nested inside image uses containing anchor, not link contents", () => {
  const c = createContext("/mini-museum-history-collectibles/");
  c.handlers.click[0](anchorClick("https://www.awin1.com/cread.php?s=4236132"));
  assert.equal(c.calls[0][2].fv_offer, "mini_museum");
});
