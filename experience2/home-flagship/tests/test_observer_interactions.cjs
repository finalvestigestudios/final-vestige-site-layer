'use strict';
// Dependency-free executable DOM-contract regression for the real, committed
// Observer Lab JavaScript. This is not a browser or WordPress acceptance test.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const script = fs.readFileSync(path.join(__dirname, '..', 'observer-lab.js'), 'utf8');

function element(key, attr) {
  return {
    hidden: false, listeners: {}, attributes: { [attr]: key }, focused: false,
    getAttribute(name) { return this.attributes[name] ?? null; },
    setAttribute(name, value) { this.attributes[name] = String(value); },
    addEventListener(type, cb) { this.listeners[type] = cb; },
    focus() { this.focused = true; },
    emit(type, event = {}) { this.listeners[type]?.(event); }
  };
}
function fixture(options = {}) {
  const frames = [element('a', 'data-fv-observer-frame'), element('b', 'data-fv-observer-frame')];
  const buttons = [element('a', 'data-fv-observer-switch'), element('b', 'data-fv-observer-switch')];
  const controls = { hidden: true };
  const status = { textContent: 'Frame A displayed.' };
  if (options.dropButton) buttons.pop();
  const root = {
    dataset: {},
    querySelectorAll(sel) {
      if (sel === '[data-fv-observer-frame]') return frames;
      if (sel === '[data-fv-observer-switch]') return buttons;
      throw new Error('Unexpected selector '+sel);
    },
    querySelector(sel) {
      if (sel === '[data-fv-observer-controls]') return controls;
      if (sel === '[data-fv-observer-status]') return status;
      throw new Error('Unexpected selector '+sel);
    }
  };
  const document = { querySelectorAll(sel) { assert.equal(sel, '[data-fv-observer]'); return [root]; } };
  return { frames, buttons, controls, status, root, document };
}
function execute(f) { vm.runInNewContext(script, { document: f.document }, { timeout: 1000 }); return f; }
const noSpoiler = (message) => {
  assert.match(message, /^Frame [AB] displayed\.$/);
  assert.doesNotMatch(message, /lower[- ]right|corner|seal|absent|missing/i);
};

test('loads only Frame A, announces neutral state and reveals buttons after wiring', () => {
  const f = execute(fixture());
  assert.deepEqual(f.frames.map(x => x.hidden), [false, true]);
  assert.equal(f.controls.hidden, false);
  assert.deepEqual(f.buttons.map(x => x.getAttribute('aria-pressed')), ['true', 'false']);
  noSpoiler(f.status.textContent);
});

test('clicking Frame B/A preserves source meaning without an answer hint', () => {
  const f = execute(fixture());
  f.buttons[1].emit('click');
  assert.deepEqual(f.frames.map(x => x.hidden), [true, false]);
  assert.deepEqual(f.buttons.map(x => x.getAttribute('aria-pressed')), ['false', 'true']);
  noSpoiler(f.status.textContent);
  f.buttons[0].emit('click');
  assert.deepEqual(f.frames.map(x => x.hidden), [false, true]);
  noSpoiler(f.status.textContent);
});

test('ArrowLeft/ArrowRight/Home/End work and move real button focus', () => {
  const f = execute(fixture());
  for (const [current, key, selected] of [[0,'ArrowRight',1],[1,'ArrowLeft',0],[0,'End',1],[1,'Home',0]]) {
    let prevented = false;
    f.buttons[current].emit('keydown', {key, preventDefault() { prevented = true; }});
    assert.equal(prevented, true);
    assert.equal(f.buttons[selected].focused, true);
    assert.equal(f.buttons[selected].getAttribute('aria-pressed'), 'true');
    noSpoiler(f.status.textContent);
  }
});

test('unhandled keys remain native and do not trap keyboard', () => {
  const f = execute(fixture());
  for (const key of ['Tab','Enter',' ','Escape']) {
    f.buttons[0].emit('keydown', { key, preventDefault() { throw new Error('preventDefault called for '+key); } });
  }
  assert.equal(f.buttons[0].getAttribute('aria-pressed'), 'true');
});

test('malformed enhancement markup does not hide the original two frames', () => {
  const f = execute(fixture({ dropButton: true }));
  assert.deepEqual(f.frames.map(x => x.hidden), [false, false]);
  assert.equal(f.controls.hidden, true);
});

test('switch failure restores both source illustrations and hides disabled controls', () => {
  const f = execute(fixture());
  f.frames[1].getAttribute = () => {throw new Error('synthetic DOM corruption');};
  f.buttons[1].emit('click');
  assert.deepEqual(f.frames.map(x => x.hidden), [false, false]);
  assert.equal(f.controls.hidden, true);
  assert.equal(f.root.dataset.fvObserverEnhanced, undefined);
});

test('no-script DOM state remains readable by default', () => {
  const f = fixture(); // Intentionally do not call execute().
  assert.deepEqual(f.frames.map(x => x.hidden), [false, false]);
  assert.equal(f.controls.hidden, true);
});
