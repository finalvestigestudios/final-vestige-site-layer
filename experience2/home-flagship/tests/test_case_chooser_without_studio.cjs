'use strict';
// Execute the real flagship.js. No jsdom, network, or invented browser pass.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const base = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(base, 'flagship.js'), 'utf8');
const page = fs.readFileSync(path.join(base, 'index.html'), 'utf8');

function exercise({ brokenCases = false } = {}) {
  const handlers = Object.create(null);
  const caseIds = ['apollo', 'franklin', 'malbone'];
  const caseButtons = (brokenCases ? caseIds.slice(0, 2) : caseIds).map(id => ({
    dataset: { fvCaseButton: id }, attrs: {},
    setAttribute(name, value) { this.attrs[name] = value; },
    focus() { handlers.focusedCase = id; }
  }));
  const panels = caseIds.map(id => ({
    dataset: { fvCase: id }, hidden: false,
    querySelector() { return { textContent: id.toUpperCase() }; }
  }));
  const caseGroup = { hidden: true, contains(button) { return caseButtons.includes(button); } };
  const status = { textContent: '' };
  const root = {
    classList: { add() {}, remove() {} },
    querySelector(sel) {
      return ({
        '[data-fv-case-buttons]': caseGroup,
        '[data-fv-case-status]': status
      })[sel] || null;
    },
    querySelectorAll(sel) {
      return ({
        '[data-fv-archive-img]': [],
        '[data-fv-case-button]': caseButtons,
        '[data-fv-case]': panels
      })[sel] || [];
    },
    addEventListener(type, fn) { handlers[type] = fn; }
  };
  class Element {}
  Element.prototype.closest = function () {};
  vm.runInNewContext(source, {
    document: { querySelectorAll: () => [root], createElement: () => ({ hidden: false }) },
    window: { location: { search: '' } },
    Element,
    URLSearchParams
  }, { timeout: 1000 });
  return { root, caseGroup, caseButtons, panels, status, handlers };
}
const visible = state => state.panels.filter(p => !p.hidden).map(p => p.dataset.fvCase);

test('publication-style markup without developer controls still enhances cases', () => {
  const state = exercise();
  assert.equal(state.caseGroup.hidden, false);
  assert.deepEqual(visible(state), ['apollo']);
});

test('the retired studio direction-picker leaves no trace in the shipped script', () => {
  assert.doesNotMatch(source, /DIRECTIONS/);
  assert.doesNotMatch(source, /fvDirectionChoice/);
  assert.doesNotMatch(source, /directionGroup/);
});

test('mouse/touch click targets select a real investigation without studio controls', () => {
  const state = exercise();
  state.handlers.click({ target: { closest(sel) {
    return sel === '[data-fv-case-button]' ? state.caseButtons[1] : null;
  } } });
  assert.deepEqual(visible(state), ['franklin']);
  assert.match(state.status.textContent, /FRANKLIN/);
});

test('keyboard arrows continue to move to a case without developer controls', () => {
  const state = exercise();
  const event = {
    key: 'ArrowRight', target: { closest(sel) {
      return sel === '[data-fv-case-button]' ? state.caseButtons[0] : null;
    } },
    preventDefault() { event.prevented = true; }
  };
  state.handlers.keydown(event);
  assert.equal(event.prevented, true);
  assert.deepEqual(visible(state), ['franklin']);
  assert.equal(state.handlers.focusedCase, 'franklin');
});

test('malformed case inventory remains readable rather than partially hidden', () => {
  const state = exercise({ brokenCases: true });
  assert.equal(state.caseGroup.hidden, true);
  assert.deepEqual(visible(state), ['apollo', 'franklin', 'malbone']);
});

test('source HTML retains seven native chapter anchors and all case panels', () => {
  for (const id of ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence',
    'fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']) {
    assert.ok(page.includes('id="' + id + '"'), 'missing ' + id);
  }
  for (const id of ['apollo','franklin','malbone']) {
    assert.match(page, new RegExp('data-fv-case="' + id + '"'));
  }
});
