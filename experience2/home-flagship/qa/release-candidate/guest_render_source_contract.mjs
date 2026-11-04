/** Non-production guest admission policy. No site writes, analytics or customer data. */
import assert from 'node:assert/strict';

export const GUEST_VIEWPORTS=Object.freeze([
  Object.freeze({width:320,height:844,kind:'narrow-mobile'}),
  Object.freeze({width:360,height:844,kind:'mobile'}),
  Object.freeze({width:390,height:844,kind:'mobile'}),
  Object.freeze({width:720,height:450,kind:'200-percent-css-viewport-proxy-not-physical-zoom'}),
  Object.freeze({width:768,height:900,kind:'tablet'}),
  Object.freeze({width:1440,height:900,kind:'desktop'}),
  Object.freeze({width:1920,height:900,kind:'wide-desktop'})
]);

/** Compare each PUBLIC page-6 fragment, not just 72 elements or a label. */
export function assertPublishedMarginParity(actual,expected) {
  assert.ok(Array.isArray(expected)&&expected.length===72,
    'Published Margins fixture must contain exactly 72 source strings');
  assert.ok(Array.isArray(actual)&&actual.length===72,
    'Guest DOM must contain exactly 72 Margins elements');
  for(let i=0;i<72;i++) {
    assert.equal(typeof expected[i],'string');
    assert.equal(typeof actual[i],'string');
    assert.equal(actual[i].trim(),expected[i].trim(),
      'Published Margins guest text drift at index '+i);
  }
  return true;
}

/** An anonymous no-JS source link is not usable if CSS hides its context. */
export function assertAnonymousNoJSState(s) {
  assert.equal(s?.admin_bar,false,'Anonymous no-JS must not show admin toolbar');
  assert.equal(s?.logged_in,false,'Anonymous no-JS must not inherit login');
  assert.equal(s?.details,true,'Observer disclosure is missing');
  assert.equal(s?.summary_visible,true,'Observer summary must be visible without JS');
  assert.ok(s?.evidence>=2,'Both original research links must remain');
  assert.equal(s?.focus,true,'Contextual Focus link missing without JS');
  assert.equal(s?.focus_visible,true,'Contextual Focus link hidden without JS');
  assert.equal(s?.margins,72,'Published Margins missing without JS');
  assert.equal(s?.margin_position,'static','Margins must remain in document flow');
  assert.equal(s?.margin_opacity,'1','Margins must be readable without JS');
  assert.equal(s?.window_overflow,'auto','Margins region must allow scrolling');
  assert.ok(Array.isArray(s?.margin_readability)&&s.margin_readability.length===72,
    'All 72 Margins must have individual rendered-state evidence');
  for(let i=0;i<72;i++) {
    const row=s.margin_readability[i];
    assert.ok(row&&typeof row==='object','Margins readability record missing at '+i);
    assert.notEqual(row.display,'none','Margins item display:none at '+i);
    assert.equal(row.visibility,'visible','Margins item visibility hidden at '+i);
    assert.equal(row.position,'static','Margins item removed from normal flow at '+i);
    assert.ok(Number(row.opacity)>=0.5,'Margins item opacity too low at '+i);
    assert.ok(Number(row.width)>0&&Number(row.height)>0,
      'Margins item has no rendered box at '+i);
    assert.equal(row.ancestor_hidden,false,
      'Margins item hidden by ancestor, aria-hidden or inert at '+i);
  }
  assert.equal(s?.horizontal_overflow,false,'No-JS mobile horizontal overflow');
  return true;
}
