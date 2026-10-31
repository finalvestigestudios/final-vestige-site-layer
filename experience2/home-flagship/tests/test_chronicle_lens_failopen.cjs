/* Node built-in DOM-contract tests for the real chronology lens JS, no dependencies.
 * Browser contract is separately measured with test_chronicle_browser.py. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '..', 'chronicle-lens.js'), 'utf8');

function element(view = null) {
  const attrs = {};
  const handlers = {};
  const obj = {
    attrs, handlers, hidden: false, dataset: view ? { fvChronicleView: view } : {},
    setAttribute(k, v) { attrs[k] = String(v); },
    removeAttribute(k) { delete attrs[k]; },
    getAttribute(k) { return attrs[k] ?? null; },
    addEventListener(k, fn) { (handlers[k] ||= []).push(fn); },
    dispatch(k, event = {}) { (handlers[k] || []).forEach(fn => fn(event)); },
    focus() { this.focused = true; }
  };
  return obj;
}
function fixture({ duplicate = false, missing = false } = {}) {
  const buttons = ['original', duplicate ? 'original' : 'addition', 'both'].map(element);
  const tools = element(); tools.hidden = true;
  tools.querySelectorAll = (selector) => selector === '[data-fv-chronicle-view]' ? buttons : [];
  const original = element(); const addition = element(); const note = element();
  note.textContent = 'Both entries';
  const lookup = {
    '[data-fv-chronicle-lens]': tools,
    '.fv-hf__chronicle-entry--first': original,
    '.fv-hf__chronicle-entry--second': addition,
    '[data-fv-chronicle-lens-status]': missing ? null : note
  };
  const section = element(); section.querySelector = key => lookup[key] || null;
  const document = { querySelector: key => key === '.fv-hf__chronicle' ? section : null };
  vm.runInNewContext(source, {document}, {timeout: 1000});
  const select = view => buttons.find(b => b.dataset.fvChronicleView === view).dispatch('click');
  const key = (from, eventKey) => {
    let prevented = false;
    buttons[from].dispatch('keydown', {key:eventKey, preventDefault() { prevented = true; }});
    return prevented;
  };
  return {buttons, tools, original, addition, note, section, select, key};
}
const tests = [
  ['normal selection', () => {
    const s = fixture();
    assert.equal(s.tools.hidden, false);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'), 'both');
    s.select('original');
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'), 'original');
    s.select('addition');
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'), 'addition');
    s.select('both');
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'), 'both');
  }],
  ['keyboard arrow/home/end', () => {
    const s=fixture();
    assert.equal(s.key(0,'ArrowRight'), true);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),'addition');
    assert.equal(s.buttons[1].focused,true);
    assert.equal(s.key(1,'End'),true);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),'both');
    assert.equal(s.key(2,'Home'),true);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),'original');
    assert.equal(s.key(0,'Escape'),false);
  }],
  ['duplicate choices do not enhance', () => {
    const s=fixture({duplicate:true});
    assert.equal(s.tools.hidden,true);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),null);
    assert.equal(s.original.hidden,false);
    assert.equal(s.addition.hidden,false);
  }],
  ['missing status keeps source readable', () => {
    const s=fixture({missing:true});
    assert.equal(s.tools.hidden,true);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),null);
  }],
  ['runtime status failure restores both sources', () => {
    const s=fixture();
    Object.defineProperty(s.note,'textContent',{configurable:true,set() { throw Error('Injected'); }});
    s.select('original');
    assert.equal(s.tools.hidden,true);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),null);
    assert.equal(s.original.hidden,false);assert.equal(s.addition.hidden,false);
    assert.deepEqual(s.buttons.map(b => b.attrs['aria-pressed']), ['false','false','false']);
  }],
  ['runtime button failure restores both sources', () => {
    const s=fixture();
    s.buttons[1].setAttribute = () => { throw Error('Injected'); };
    s.select('original');
    assert.equal(s.tools.hidden,true);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),null);
    assert.equal(s.original.hidden,false);assert.equal(s.addition.hidden,false);
  }],
  ['keyboard focus failure restores both sources', () => {
    const s=fixture();
    s.buttons[1].focus = () => { throw Error('Injected'); };
    assert.equal(s.key(0,'ArrowRight'),true);
    assert.equal(s.tools.hidden,true);
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),null);
  }],
  ['post-failure controls remain inert', () => {
    const s=fixture();
    Object.defineProperty(s.note,'textContent',{configurable:true,set() { throw Error('Injected'); }});
    s.select('original');
    s.select('addition');
    assert.equal(s.section.getAttribute('data-fv-chronicle-mode'),null);
    assert.equal(s.key(0,'ArrowRight'),false);
  }]
];
for (const [name, fn] of tests) {
  fn(); console.log('PASS '+name);
}
console.log('PASS '+tests.length+'/'+tests.length+' chronology lens contract tests');
