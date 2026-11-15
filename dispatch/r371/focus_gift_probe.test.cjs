// No external packages, no network, no email, no signup and no WP write.
// Execute: node --test dispatch/r371/focus_gift_probe.test.cjs
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const raw = require("./focus_gift_live_fixture.cjs");
function simulate(query = "", className = "", options = {}) {
  let observer;
  const gift = { hidden: true };
  const container = { className };
  const context = {
    URLSearchParams,
    window: {
      location: { search: query },
      MutationObserver: options.observer === false ? undefined : class {
        constructor(cb) { observer = cb; }
        observe() {}
      }
    },
    document: {
      getElementById(id) { return id === "fvf-gift" && options.gift !== false ? gift : null; },
      querySelector(selector) { return selector === ".wp-block-jetpack-subscriptions__container" && options.container !== false ? container : null; }
    }
  };
  vm.runInNewContext(raw, context, { timeout: 1000 });
  return { visible: !gift.hidden, setClass(s) { container.className = s; if (observer) observer(); return !gift.hidden; } };
}
test("no query, no subscriber class: gift remains hidden", () => assert.equal(simulate().visible, false));
test("unknown nonempty subscribe value exposes gift", () => assert.equal(simulate("?subscribe=arbitrary").visible, true));
test("explicit unconfirmed value also exposes gift; this is not confirmation", () => assert.equal(simulate("?subscribe=unconfirmed").visible, true));
test("failed is not one of the excluded strings", () => assert.equal(simulate("?subscribe=failed").visible, true));
test("empty subscribe value does not expose gift", () => assert.equal(simulate("?subscribe=").visible, false));
for (const state of ["invalid_email", "error", "blocked_email", "opted_out", "blocked"]) {
  test("excluded status "+state+" stays hidden", () => assert.equal(simulate("?subscribe="+state).visible, false));
}
test("failure matching is case-sensitive", () => assert.equal(simulate("?subscribe=ERROR").visible, true));
test("is-subscriber CSS class exposes gift", () => assert.equal(simulate("", "wp-block is-subscriber").visible, true));
test("a similar non-subscriber class does not expose gift", () => assert.equal(simulate("", "is-not-subscriber").visible, false));
test("late subscriber-class mutation exposes gift", () => {
  const x=simulate("", "initial"); assert.equal(x.visible,false);
  assert.equal(x.setClass("is-subscriber"),true);
});
test("no observer prevents late reveal in the isolated harness", () => {
  const x=simulate("", "initial", { observer:false });
  assert.equal(x.setClass("is-subscriber"),false);
});
test("missing gift node does not throw", () => assert.equal(simulate("?subscribe=arbitrary","", {gift:false}).visible, false));
test("missing subscription container does not throw", () => assert.equal(simulate("?subscribe=arbitrary","",{container:false}).visible,true));
test("fixture has no recipient, email-sending, pixel or logging facility", () => {
  assert.equal(/fetch\\(|XMLHttpRequest|sendBeacon|mailto:|new Image\\(/i.test(raw),false);
});
