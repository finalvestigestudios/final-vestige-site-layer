'use strict';
/** Offline, read-only classifier for dispatch/focus newsletter first-click evidence.
 * No network, no subscriber actions, no sending, no settings writes. */
const FORBIDDEN = /(?:[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|\b(?:api[_-]?key|access[_-]?token|confirmation[_-]?token|subscriber[_-]?email)\b)/i;
function isBoolean(value) { return typeof value === 'boolean'; }
function inspect(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw Error('evidence object required');
  const serialized = JSON.stringify(input);
  if (FORBIDDEN.test(serialized)) throw Error('private or tokenized evidence prohibited');
  const e = input.editor || {}, v = input.view || {}, g = input.guest || null, n = input.newsletter || {};
  for (const [label,obj] of [['editor',e],['view',v],['newsletter',n]]) {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) throw Error(`${label} object required`);
  }
  const fields=['jetpack_block_present','has_email_input','has_html_form','has_self_link_to_page'];
  for (const [i,f] of fields.entries()) {
    const val=(i===0?e:v)[f];
    if (val!==undefined && val!==null && !isBoolean(val)) throw Error(`invalid ${f}`);
  }
  if (n.auto_send_new_posts !== false || n.enabled !== true) throw Error('unverified or unsafe newsletter configuration');
  if (!['full','excerpt'].includes(n.email_format)) throw Error('unverified email format');
  const editorBlock=e.jetpack_block_present===true;
  const selfLink=v.has_self_link_to_page===true;
  const noViewInput=v.has_email_input===false && v.has_html_form===false;
  const representationGap=editorBlock && noViewInput && selfLink;
  let guestPass=null;
  if(g!==null) {
    if(typeof g!=='object'||Array.isArray(g)) throw Error('guest evidence object required');
    const keys=['signed_out','actual_browser','email_input_visible','subscribe_control_operable','keyboard_path_pass','destination_not_self'];
    for(const k of keys) if (!isBoolean(g[k])) throw Error(`guest ${k} proof required`);
    guestPass=keys.every(k=>g[k]===true);
  }
  // A positive guest-form observation is *not* confirmation, consent or Fieldbook delivery.
  return Object.freeze({
    category:'FIRST_CLICK_ONLY',
    representation_gap:representationGap,
    native_guest_form_pass:guestPass,
    risk:guestPass===false ? 'P0_GUEST_PATH_FAIL' : (representationGap && guestPass!==true ? 'P0_VERIFY_DISPATCH_GUEST_FIRST_CLICK' : 'NO_GUEST_PATH_FAILURE_PROVEN'),
    confirmed_signup:null,
    actual_welcome_receipt:null,
    actual_paid_orders:null,
    send_decision:'HOLD_UNSENT',
    commercial_decision:'HOLD_MERCHANT',
    note:'Stored editor and REST view HTML are not equivalent to anonymous browser DOM. Guest form is not opt-in or confirmed signup.'
  });
}
module.exports={inspect};
