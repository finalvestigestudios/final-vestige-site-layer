'use strict';
// Run: node --test experience2/home-flagship/tests/test_reading_trail_progress.cjs
// Executes the committed Reading Trail JavaScript in a deterministic DOM simulation;
// this is NOT a Chromium/WordPress/browser-layout acceptance claim.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const script = fs.readFileSync(path.join(__dirname, '..', 'reading-trail.js'), 'utf8');
const IDS = ['fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
  'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title'];
const TOPS = [0, 1400, 2900, 4000, 5100, 6600, 8000];
const LAST_SECTION_BOTTOM = 9800;
const VIEWPORT = 900;

function mount(scroll, options = {}) {
  const attrs = (initial = {}) => {
    const a = {...initial};
    return {
      getAttribute: key => a[key] ?? null,
      hasAttribute: key => Object.hasOwn(a, key),
      setAttribute: (key, value) => { a[key] = String(value); },
      removeAttribute: key => { delete a[key]; }
    };
  };
  let focused = null;
  let restored = false;
  const section = {
    getBoundingClientRect: () => ({top: 8000 - scroll, bottom: LAST_SECTION_BOTTOM - scroll})
  };
  const targets = IDS.map((id, index) => ({
    ...attrs({id}),
    getBoundingClientRect: () => ({top: TOPS[index] - scroll, bottom: TOPS[index] + 50 - scroll}),
    closest: (selector) => selector === 'section' && index === IDS.length - 1 ? section : null,
    focus: () => { focused = id; }
  }));
  if (options.noClosest) delete targets[targets.length - 1].closest;
  const links = IDS.map((id) => {
    const callbacks = {};
    return {
      ...attrs({href: '#' + id}),
      addEventListener: (type, callback) => { callbacks[type] = callback; },
      dispatchClick: (detail) => { if (callbacks.click) callbacks.click({detail}); }
    };
  });
  const props = {};
  const handlers = {};
  const navAttrsStore = attrs();
  const navScroll = options.navScroll || {scrollWidth: 100, clientWidth: 100, scrollLeft: 0};
  const nav = {
    ...navAttrsStore,
    querySelectorAll: () => links,
    style: {
      setProperty: (key, value) => { props[key] = value; },
      removeProperty: key => { delete props[key]; }
    },
    getBoundingClientRect: () => ({height: 55}),
    removeAttribute: key => {
      if (key === 'data-fv-trail-enhanced') restored = true;
      navAttrsStore.removeAttribute(key);
    },
    addEventListener: () => {},
    removeEventListener: () => {},
    scrollWidth: navScroll.scrollWidth, clientWidth: navScroll.clientWidth, scrollLeft: navScroll.scrollLeft
  };
  const root = {
    querySelector: selector => {
      if (selector === '.fv-hf__chapter-nav') return nav;
      const match = /^\[id="([^"]+)"\]$/.exec(selector);
      return match ? targets[IDS.indexOf(match[1])] || null : null;
    }
  };
  const document = {querySelector: selector => selector === '[data-fv-home-flagship]' ? root : null};
  const window = {
    scrollY: scroll, pageYOffset: scroll, innerHeight: VIEWPORT,
    requestAnimationFrame: fn => fn(),
    addEventListener: (name, fn) => { handlers[name] = fn; },
    removeEventListener: name => { delete handlers[name]; },
    setTimeout: fn => fn()
  };
  vm.runInNewContext(script, {window, document}, {timeout: 1000});
  const navAttr = key => navAttrsStore.hasAttribute(key) ? navAttrsStore.getAttribute(key) : undefined;
  return {
    progress: Number(props['--fv-trail-progress']),
    active: links.findIndex(link => link.getAttribute('aria-current') === 'location'),
    links, restored,
    get focused() { return focused; },
    handlers,
    navAttrs: {
      'data-fv-trail-overflow-left': navAttr('data-fv-trail-overflow-left'),
      'data-fv-trail-overflow-right': navAttr('data-fv-trail-overflow-right')
    }
  };
}

test('Reading Trail remains incomplete before final chapter starts', () => {
  const h = mount(7200);
  assert.equal(h.restored, false);
  assert.equal(h.active, 5); // Chapter 06 (Observer)
  assert.ok(h.progress > 0.78 && h.progress < 0.85,
    'The final chapter must still count toward progress; got ' + h.progress);
});

test('Progress continues through the final chapter instead of freezing at 100%', () => {
  const before = mount(8000).progress;
  const within = mount(8750).progress;
  assert.ok(before > 0.88 && before < 0.92, 'Unexpected final-chapter start: ' + before);
  assert.ok(within > 0.97 && within < 1, 'The chapter is not yet finished: ' + within);
  assert.ok(within > before);
});

test('Progress reaches 100% only at the actual final-chapter boundary', () => {
  assert.equal(mount(LAST_SECTION_BOTTOM - VIEWPORT).progress, 1);
  assert.equal(mount(0).progress, 0);
});

test('Anchor links and keyboard focus remain native and correct', () => {
  const h = mount(7000);
  assert.equal(h.links.length, 7);
  assert.equal(h.focused, null);
  h.links[3].dispatchClick(1);
  assert.equal(h.focused, null, 'Pointer click must not force focus');
  h.links[3].dispatchClick(0);
  assert.equal(h.focused, 'fv-hf-inquiry', 'Keyboard activation focuses the real source anchor');
});

test('Unsupported closest() fails gracefully without breaking navigation', () => {
  const h = mount(7200, {noClosest: true});
  assert.equal(h.restored, false);
  assert.equal(h.links.length, 7);
  assert.ok(h.progress >= 0 && h.progress <= 1);
});

test('mobile chapter-nav overflow sets fade-edge attributes from real scroll position, not a guess', () => {
  // scrollWidth/clientWidth/scrollLeft simulate the seven labels not fitting the
  // narrow viewport -- the actual bug report ("03 Inspect the evid...") -- and confirm
  // the JS correctly identifies which edge(s) still have hidden chapters, without ever
  // hiding any label's full text (that's handled by scrollable markup alone, no JS
  // needed for it to work at all).
  const h = mount(0, {navScroll: {scrollWidth: 900, clientWidth: 390, scrollLeft: 0}});
  assert.equal(h.navAttrs['data-fv-trail-overflow-left'], undefined, 'at the start, nothing is scrolled past to the left');
  assert.equal(h.navAttrs['data-fv-trail-overflow-right'], '', 'seven labels wider than the viewport must signal more content to the right');

  const mid = mount(0, {navScroll: {scrollWidth: 900, clientWidth: 390, scrollLeft: 255}});
  assert.equal(mid.navAttrs['data-fv-trail-overflow-left'], '', 'scrolled off the start, the left edge must fade too');
  assert.equal(mid.navAttrs['data-fv-trail-overflow-right'], '', 'still short of the end, the right edge must keep fading');

  const end = mount(0, {navScroll: {scrollWidth: 900, clientWidth: 390, scrollLeft: 510}});
  assert.equal(end.navAttrs['data-fv-trail-overflow-left'], '', 'at the end, the left edge still has hidden chapters behind it');
  assert.equal(end.navAttrs['data-fv-trail-overflow-right'], undefined, 'fully scrolled to the end, there is nothing further right to signal');

  const fits = mount(0, {navScroll: {scrollWidth: 390, clientWidth: 390, scrollLeft: 0}});
  assert.equal(fits.navAttrs['data-fv-trail-overflow-left'], undefined, 'when all seven labels fit, neither edge should ever fade');
  assert.equal(fits.navAttrs['data-fv-trail-overflow-right'], undefined);
});
