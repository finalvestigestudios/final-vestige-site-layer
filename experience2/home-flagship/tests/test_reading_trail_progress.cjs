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
  const nav = {
    ...attrs(),
    querySelectorAll: () => links,
    style: {
      setProperty: (key, value) => { props[key] = value; },
      removeProperty: key => { delete props[key]; }
    },
    getBoundingClientRect: () => ({height: 55}),
    removeAttribute: key => { if (key === 'data-fv-trail-enhanced') restored = true; }
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
  return {
    progress: Number(props['--fv-trail-progress']),
    active: links.findIndex(link => link.getAttribute('aria-current') === 'location'),
    links, restored,
    get focused() { return focused; },
    handlers
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
