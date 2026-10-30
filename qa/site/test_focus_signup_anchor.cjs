const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(__dirname + '/focus_signup_anchor_wp_block.html', 'utf8');
const match = html.match(/<script id="fvf-signup-anchor-v1">\s*([\s\S]*?)\s*<\/script>/);
assert.ok(match, 'versioned script must exist');
const script = match[1];

function setup({root = true, widget = true, existing = false, loading = false, hash = ''} = {}) {
  const events = {};
  let inserted = 0, scrolling = 0;
  const form = widget ? {parentNode: {insertBefore(el, before) {inserted++; assert.equal(before, form); events.created = el;}}} : null;
  const page = root ? {querySelector(sel) {assert.equal(sel, '.wp-block-jetpack-subscriptions');return form;}} : null;
  const document = {
    readyState: loading ? 'loading' : 'complete',
    querySelector(sel) {assert.equal(sel, '.fv-focus');return page;},
    getElementById(id) {assert.equal(id, 'subscribe-blog');return existing ? {id} : events.created || null;},
    createElement(tag) {assert.equal(tag, 'span');return {style:{},setAttribute(key,val){this[key]=val;},scrollIntoView(opts){scrolling++;assert.equal(opts.block, 'start');}};},
    addEventListener(name,fn,opts) {assert.equal(name,'DOMContentLoaded');assert.equal(opts.once,true);events.ready=fn;}
  };
  const window={location:{hash}};
  const context={document,window};
  return {run(){vm.runInNewContext(script,context);},fire(){events.ready?.();},get inserted(){return inserted},get scrolling(){return scrolling},get marker(){return events.created},window,form};
}

test('adds exactly one scroll target immediately before the existing Jetpack widget', () => {
  const a=setup(); a.run(); assert.equal(a.inserted,1); assert.equal(a.marker.id,'subscribe-blog');
  assert.equal(a.marker['data-fvf-signup-anchor'],'1'); assert.equal(a.marker.style.scrollMarginTop,'80px');
});
test('does not touch or replace the Jetpack widget',()=>{
  const a=setup(); a.run(); assert.ok(a.form); assert.equal(a.inserted,1);
});
test('preserves an existing native subscribe-blog anchor',()=>{
  const a=setup({existing:true});a.run();assert.equal(a.inserted,0);
});
test('does nothing if the Focus page is absent',()=>{
  const a=setup({root:false});a.run();assert.equal(a.inserted,0);
});
test('does nothing if the subscription widget is unavailable',()=>{
  const a=setup({widget:false});a.run();assert.equal(a.inserted,0);
});
test('runs after DOMContentLoaded on a still-loading document',()=>{
  const a=setup({loading:true});a.run();assert.equal(a.inserted,0);a.fire();assert.equal(a.inserted,1);
});
test('direct fragment link scrolls once to the new target',()=>{
  const a=setup({hash:'#subscribe-blog'});a.run();assert.equal(a.scrolling,1);
});
test('ordinary page loads do not scroll',()=>{
  const a=setup();a.run();assert.equal(a.scrolling,0);
});
test('idempotent on duplicate script execution',()=>{
  const a=setup();a.run();a.run();assert.equal(a.inserted,1);
});
test('no submission, network, persistence, or data collection code',()=>{
  for (const banned of ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'document.cookie', 'submit(', 'addEventListener(\'click\'']) {
    assert.equal(script.includes(banned),false,banned);
  }
});
