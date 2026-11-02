/* Household Emergency Plan Builder: pure logic.
   No DOM, no storage, no network. Everything a visitor types lives in memory on the page and is lost when the tab closes
   unless the visitor chooses to print or to download a copy. Nothing here gives medical, legal or safety instructions;
   it only organizes what the visitor decides. */
var PB_LIMITS = { name: 60, short: 80, text: 200, long: 400, phone: 30, members: 12, contacts: 8, children: 12, pets: 8 };
var PB_AGE = ['adult', 'older', 'teen', 'child', 'infant'];
var PB_AGE_LABEL = { adult: 'Adult', older: 'Older adult', teen: 'Teen', child: 'Child', infant: 'Infant' };
var PB_NEEDS = ['mobility', 'hearing', 'vision', 'communication', 'cognitive', 'medical-device', 'refrigerated-medicine', 'medication', 'dietary', 'language'];
var PB_NEED_LABEL = {
  mobility: 'Needs help moving or leaving a building', hearing: 'Deaf or hard of hearing', vision: 'Blind or low vision',
  communication: 'Communication support', cognitive: 'Needs support in unfamiliar or stressful places', 'medical-device': 'Uses powered medical equipment',
  'refrigerated-medicine': 'Has a medicine that must be kept cold', medication: 'Takes daily medication', dietary: 'Special diet', language: 'Needs information in another language'
};
var PB_ACCESS = ['transport', 'stairs', 'support-network', 'registry', 'service-animal', 'communication-card'];
var PB_ACCESS_LABEL = {
  transport: 'We need accessible transport if we must leave', stairs: 'Someone may not be able to use stairs',
  'support-network': 'We have named people who will check on us', registry: 'We looked into a local registry for people who need help',
  'service-animal': 'A service animal travels with us', 'communication-card': 'We carry a card that explains how to communicate with us'
};
var PB_MEDCHECKS = ['asked-prescriber', 'asked-supply', 'asked-cold', 'asked-power-provider', 'device-backup', 'clinic-plan'];
var PB_MEDCHECK_LABEL = {
  'asked-prescriber': 'We asked the prescriber or pharmacist what to do if medicines are disrupted',
  'asked-supply': 'We asked how large an emergency supply of each medicine can be',
  'asked-cold': 'We asked how long each cold-storage medicine can stay warm, and what the replacement plan is',
  'asked-power-provider': 'We asked our power provider about priority restoration',
  'device-backup': 'We have a written plan for powered equipment with its clinician or supplier',
  'clinic-plan': 'We asked our clinic or treatment center about its emergency plan and back-up provider'
};

function pbText(v, max) {
  var s = (v === null || v === undefined) ? '' : String(v);
  s = s.replace(/[\u0000-\u001F\u007F\u2028\u2029]+/g, ' ').replace(/\s+/g, ' ').trim();
  return s.length > max ? s.slice(0, max) : s;
}
function pbEsc(s) {
  return String(s).replace(/[&<>"'`]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '`': '&#96;' }[c]; });
}
function pbPhone(v) {
  var raw = (v === null || v === undefined) ? '' : String(v);
  var value = pbText(raw, PB_LIMITS.phone);
  if (value === '') return { value: '', ok: true, message: '' };
  if (!/^[0-9+().\-xX#*\s]+$/.test(value)) return { value: value, ok: false, message: 'Use only digits, spaces and + - ( ) . x' };
  var digits = value.replace(/[^0-9]/g, '').length;
  if (digits < 3 || digits > 20) return { value: value, ok: false, message: 'That number has ' + digits + ' digits. Check it.' };
  return { value: value, ok: true, message: '' };
}
function pbDate(v) {
  var s = pbText(v, 10);
  if (s === '') return { value: '', ok: true, message: '' };
  var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  if (!m) return { value: s, ok: false, message: 'Use the date picker or the form YYYY-MM-DD.' };
  var d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
  if (d.getUTCFullYear() !== +m[1] || d.getUTCMonth() !== +m[2] - 1 || d.getUTCDate() !== +m[3]) return { value: s, ok: false, message: 'That date does not exist.' };
  return { value: s, ok: true, message: '' };
}
function pbPhoneV(v) { var r = pbPhone(v); return r.ok ? r.value : ''; }
function pbDateV(v) { var r = pbDate(v); return r.ok ? r.value : ''; }
function pbPick(list, allowed) {
  var out = [];
  (Array.isArray(list) ? list : []).forEach(function (x) { if (allowed.indexOf(x) !== -1 && out.indexOf(x) === -1) out.push(x); });
  return out;
}
function pbRows(arr, max, fn) {
  return (Array.isArray(arr) ? arr : []).slice(0, max).map(function (x) { return fn(x && typeof x === 'object' ? x : {}); });
}
function pbEnum(v, allowed, fallback) { return allowed.indexOf(v) !== -1 ? v : fallback; }

function pbNormalize(raw) {
  raw = raw && typeof raw === 'object' ? raw : {};
  var T = pbText, L = PB_LIMITS;
  var oa = raw.outOfArea || {}, mt = raw.meeting || {}, bd = raw.building || {}, pr = raw.practice || {}, ac = raw.access || {}, md = raw.meds || {};
  return {
    members: pbRows(raw.members, L.members, function (m) {
      return { name: T(m.name, L.name), age: pbEnum(m.age, PB_AGE, 'adult'), needs: pbPick(m.needs, PB_NEEDS), cardNote: T(m.cardNote, L.short) };
    }),
    outOfArea: { name: T(oa.name, L.name), phone1: pbPhoneV(oa.phone1), phone2: pbPhoneV(oa.phone2) },
    contacts: pbRows(raw.contacts, L.contacts, function (c) { return { name: T(c.name, L.name), relation: T(c.relation, L.short), phone: pbPhoneV(c.phone) }; }),
    meeting: { near: T(mt.near, L.text), far: T(mt.far, L.text), outOfArea: T(mt.outOfArea, L.text) },
    children: pbRows(raw.children, L.children, function (c) {
      return { name: T(c.name, L.name), school: T(c.school, L.short), phone: pbPhoneV(c.phone), release: T(c.release, L.text) };
    }),
    pets: pbRows(raw.pets, L.pets, function (p) {
      return { name: T(p.name, L.name), kind: T(p.kind, L.short), vetPhone: pbPhoneV(p.vetPhone), microchip: pbEnum(p.microchip, ['yes', 'no', 'unsure'], 'unsure'), kitLocation: T(p.kitLocation, L.short) };
    }),
    petPlace: T(raw.petPlace, L.text),
    access: { checks: pbPick(ac.checks, PB_ACCESS), note: T(ac.note, L.long) },
    meds: { checks: pbPick(md.checks, PB_MEDCHECKS), pharmacyPhone: pbPhoneV(md.pharmacyPhone), powerPhone: pbPhoneV(md.powerPhone), note: T(md.note, L.long) },
    building: { managerPhone: pbPhoneV(bd.managerPhone), utilityPhone: pbPhoneV(bd.utilityPhone), elevator: pbEnum(bd.elevator, ['yes', 'no', 'unknown', 'na'], 'unknown'), exits: T(bd.exits, L.text), shutoffs: T(bd.shutoffs, L.text) },
    practice: { drill: pbDateV(pr.drill), kit: pbDateV(pr.kit), review: pbDateV(pr.review) }
  };
}

/* Validation works on RAW form values so it can point at what the visitor typed. Returns [{path, message}]. */
function pbValidate(raw) {
  var errs = [];
  raw = raw && typeof raw === 'object' ? raw : {};
  function ph(path, v) { var r = pbPhone(v); if (!r.ok) errs.push({ path: path, message: r.message }); }
  function dt(path, v) { var r = pbDate(v); if (!r.ok) errs.push({ path: path, message: r.message }); }
  var oa = raw.outOfArea || {};
  ph('outOfArea.phone1', oa.phone1); ph('outOfArea.phone2', oa.phone2);
  (raw.contacts || []).slice(0, PB_LIMITS.contacts).forEach(function (c, i) { ph('contacts.' + i + '.phone', c && c.phone); });
  (raw.children || []).slice(0, PB_LIMITS.children).forEach(function (c, i) { ph('children.' + i + '.phone', c && c.phone); });
  (raw.pets || []).slice(0, PB_LIMITS.pets).forEach(function (p, i) { ph('pets.' + i + '.vetPhone', p && p.vetPhone); });
  var md = raw.meds || {}; ph('meds.pharmacyPhone', md.pharmacyPhone); ph('meds.powerPhone', md.powerPhone);
  var bd = raw.building || {}; ph('building.managerPhone', bd.managerPhone); ph('building.utilityPhone', bd.utilityPhone);
  var pr = raw.practice || {}; dt('practice.drill', pr.drill); dt('practice.kit', pr.kit); dt('practice.review', pr.review);
  return errs;
}

/* Suggested review dates. These intervals are editorial: FEMA and the CDC differ (6 months vs 1 year), so we
   suggest a drill at 3 months, a kit check at 6 months and a plan review at 12 months. Month arithmetic clamps the day. */
function pbAddMonths(iso, months) {
  var r = pbDate(iso);
  if (!r.ok || r.value === '') return '';
  var p = r.value.split('-').map(Number);
  var total = p[0] * 12 + (p[1] - 1) + months;
  var y = Math.floor(total / 12), mo = total % 12;
  var last = new Date(Date.UTC(y, mo + 1, 0)).getUTCDate();
  var d = Math.min(p[2], last);
  return y + '-' + String(mo + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');
}
function pbPracticeDates(fromIso) { return { drill: pbAddMonths(fromIso, 3), kit: pbAddMonths(fromIso, 6), review: pbAddMonths(fromIso, 12) }; }

var PB_REMINDERS = [
  'If anyone is in danger, call 911 or your local emergency number first.',
  'Follow the instructions of local officials. A mandatory evacuation order is theirs to give; this plan cannot override it.',
  'Decide stay or go from the hazard, not from habit: the right choice for a fire, a flood, a storm and a power outage can differ.',
  'Actions such as sheltering in place, sealing a room or shutting off utilities depend on the hazard and the building. Do them only as local officials or your fire department direct.',
  'Never use a generator, grill or camp stove indoors, in a garage, or near windows and doors.',
  'This page is not medical or legal advice. Ask your prescriber, pharmacist, clinic or landlord about anything that affects health or housing.'
];

function pbNeedsText(m) { return m.needs.map(function (n) { return PB_NEED_LABEL[n]; }).join('; '); }
function pbLine(label, v) { return v ? label + ': ' + v : ''; }

function pbToText(rawOrPlan) {
  var p = pbNormalize(rawOrPlan), L = [];
  L.push('HOUSEHOLD EMERGENCY PLAN', 'Prepared with the Final Vestige Preparedness Archive plan builder. Kept on this device only.', '');
  L.push('HOUSEHOLD MEMBERS');
  if (!p.members.length) L.push('  (none entered)');
  p.members.forEach(function (m) { L.push('  - ' + (m.name || '(unnamed)') + ' (' + PB_AGE_LABEL[m.age] + ')' + (m.needs.length ? ': ' + pbNeedsText(m) : '')); });
  L.push('', 'OUT-OF-AREA CONTACT', '  ' + (p.outOfArea.name || '(not set)'), '  ' + [p.outOfArea.phone1, p.outOfArea.phone2].filter(Boolean).join('  /  '));
  L.push('', 'OTHER EMERGENCY CONTACTS');
  if (!p.contacts.length) L.push('  (none entered)');
  p.contacts.forEach(function (c) { L.push('  - ' + [c.name, c.relation, c.phone].filter(Boolean).join(', ')); });
  L.push('', 'WHERE WE MEET', '  ' + pbLine('Near home', p.meeting.near), '  ' + pbLine('Outside our neighborhood', p.meeting.far), '  ' + pbLine('Out of the area', p.meeting.outOfArea));
  if (p.children.length) {
    L.push('', 'SCHOOL AND CHILDCARE');
    p.children.forEach(function (c) { L.push('  - ' + [c.name, c.school, c.phone].filter(Boolean).join(', ') + (c.release ? ' | Reunification: ' + c.release : '')); });
  }
  if (p.pets.length || p.petPlace) {
    L.push('', 'PETS');
    p.pets.forEach(function (x) { L.push('  - ' + [x.name, x.kind].filter(Boolean).join(', ') + ' | microchip: ' + x.microchip + (x.vetPhone ? ' | vet: ' + x.vetPhone : '') + (x.kitLocation ? ' | kit: ' + x.kitLocation : '')); });
    if (p.petPlace) L.push('  Pet-friendly place: ' + p.petPlace);
  }
  if (p.access.checks.length || p.access.note) {
    L.push('', 'ACCESS AND MOBILITY');
    p.access.checks.forEach(function (k) { L.push('  [x] ' + PB_ACCESS_LABEL[k]); });
    if (p.access.note) L.push('  Notes: ' + p.access.note);
  }
  L.push('', 'MEDICINES AND POWERED EQUIPMENT: THINGS TO ASK (this is a to-do list, not advice)');
  PB_MEDCHECKS.forEach(function (k) { L.push('  [' + (p.meds.checks.indexOf(k) !== -1 ? 'x' : ' ') + '] ' + PB_MEDCHECK_LABEL[k]); });
  if (p.meds.pharmacyPhone) L.push('  Pharmacy: ' + p.meds.pharmacyPhone);
  if (p.meds.powerPhone) L.push('  Power provider: ' + p.meds.powerPhone);
  if (p.meds.note) L.push('  Notes: ' + p.meds.note);
  L.push('', 'BUILDING AND UTILITIES');
  L.push('  ' + pbLine('Building manager', p.building.managerPhone), '  ' + pbLine('Utility', p.building.utilityPhone), '  Elevator has backup power: ' + p.building.elevator);
  if (p.building.exits) L.push('  Exits and stairs: ' + p.building.exits);
  if (p.building.shutoffs) L.push('  Shutoff locations (only if officials tell us to): ' + p.building.shutoffs);
  L.push('', 'PRACTICE AND REVIEW', '  ' + pbLine('Next drill', p.practice.drill), '  ' + pbLine('Next kit check', p.practice.kit), '  ' + pbLine('Next plan review', p.practice.review));
  L.push('', 'REMINDERS');
  PB_REMINDERS.forEach(function (r) { L.push('  * ' + r); });
  return L.join('\n');
}

function pbWalletCards(rawOrPlan) {
  var p = pbNormalize(rawOrPlan);
  var people = p.members.length ? p.members : [{ name: '', age: 'adult', needs: [], cardNote: '' }];
  return people.map(function (m) {
    return {
      name: m.name, note: m.cardNote,
      outOfArea: [p.outOfArea.name, p.outOfArea.phone1, p.outOfArea.phone2].filter(Boolean),
      meetNear: p.meeting.near, meetFar: p.meeting.far,
      contact: p.contacts.length ? [p.contacts[0].name, p.contacts[0].phone].filter(Boolean).join(' ') : ''
    };
  });
}
function pbCardsHtml(rawOrPlan) {
  return pbWalletCards(rawOrPlan).map(function (c) {
    function row(k, v) { return v ? '<div><span>' + pbEsc(k) + '</span> ' + pbEsc(v) + '</div>' : '<div><span>' + pbEsc(k) + '</span> ____________________</div>'; }
    return '<div class="pb-card"><p class="pb-card-title">Emergency contact card</p>' + row('Name', c.name) +
      row('Call first (out of area)', c.outOfArea.join('  ')) + row('Meet near home', c.meetNear) + row('If not, meet at', c.meetFar) + row('Also call', c.contact) +
      (c.note ? '<div><span>Note</span> ' + pbEsc(c.note) + '</div>' : '') + '<p class="pb-card-foot">Text first: messages often get through when calls do not.</p></div>';
  }).join('');
}
function pbPlanHtml(rawOrPlan) {
  var p = pbNormalize(rawOrPlan), e = pbEsc;
  function ul(items) { return items.length ? '<ul>' + items.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>' : '<p class="pb-empty">Nothing entered.</p>'; }
  var h = '<h2>Household emergency plan</h2>';
  h += '<h3>Household members</h3>' + ul(p.members.map(function (m) { return e(m.name || '(unnamed)') + ' <em>(' + e(PB_AGE_LABEL[m.age]) + ')</em>' + (m.needs.length ? '<br><small>' + e(pbNeedsText(m)) + '</small>' : ''); }));
  h += '<h3>Out-of-area contact</h3><p>' + (p.outOfArea.name || p.outOfArea.phone1 ? e([p.outOfArea.name, p.outOfArea.phone1, p.outOfArea.phone2].filter(Boolean).join(' · ')) : '<span class="pb-empty">Not set.</span>') + '</p>';
  h += '<h3>Other emergency contacts</h3>' + ul(p.contacts.map(function (c) { return e([c.name, c.relation, c.phone].filter(Boolean).join(', ')); }));
  h += '<h3>Where we meet</h3>' + ul([p.meeting.near && 'Near home: ' + e(p.meeting.near), p.meeting.far && 'Outside our neighborhood: ' + e(p.meeting.far), p.meeting.outOfArea && 'Out of the area: ' + e(p.meeting.outOfArea)].filter(Boolean));
  if (p.children.length) h += '<h3>School and childcare</h3>' + ul(p.children.map(function (c) { return e([c.name, c.school, c.phone].filter(Boolean).join(', ')) + (c.release ? '<br><small>Reunification: ' + e(c.release) + '</small>' : ''); }));
  if (p.pets.length || p.petPlace) h += '<h3>Pets</h3>' + ul(p.pets.map(function (x) { return e([x.name, x.kind].filter(Boolean).join(', ')) + '<br><small>Microchip: ' + e(x.microchip) + (x.vetPhone ? ' · Vet: ' + e(x.vetPhone) : '') + (x.kitLocation ? ' · Kit: ' + e(x.kitLocation) : '') + '</small>'; }).concat(p.petPlace ? ['Pet-friendly place: ' + e(p.petPlace)] : []));
  if (p.access.checks.length || p.access.note) h += '<h3>Access and mobility</h3>' + ul(p.access.checks.map(function (k) { return e(PB_ACCESS_LABEL[k]); }).concat(p.access.note ? ['Notes: ' + e(p.access.note)] : []));
  h += '<h3>Medicines and powered equipment: things to ask</h3><p><small>A to-do list, not advice. Ask your prescriber or pharmacist.</small></p>' +
    '<ul class="pb-checks">' + PB_MEDCHECKS.map(function (k) { return '<li>' + (p.meds.checks.indexOf(k) !== -1 ? '&#9745; ' : '&#9744; ') + e(PB_MEDCHECK_LABEL[k]) + '</li>'; }).join('') + '</ul>' +
    (p.meds.pharmacyPhone || p.meds.powerPhone ? '<p>' + e([p.meds.pharmacyPhone && 'Pharmacy: ' + p.meds.pharmacyPhone, p.meds.powerPhone && 'Power provider: ' + p.meds.powerPhone].filter(Boolean).join(' · ')) + '</p>' : '') +
    (p.meds.note ? '<p>Notes: ' + e(p.meds.note) + '</p>' : '');
  h += '<h3>Building and utilities</h3>' + ul([p.building.managerPhone && 'Building manager: ' + e(p.building.managerPhone), p.building.utilityPhone && 'Utility: ' + e(p.building.utilityPhone), 'Elevator has backup power: ' + e(p.building.elevator), p.building.exits && 'Exits and stairs: ' + e(p.building.exits), p.building.shutoffs && 'Shutoff locations (only if officials tell us to): ' + e(p.building.shutoffs)].filter(Boolean));
  h += '<h3>Practice and review</h3>' + ul([p.practice.drill && 'Next drill: ' + e(p.practice.drill), p.practice.kit && 'Next kit check: ' + e(p.practice.kit), p.practice.review && 'Next plan review: ' + e(p.practice.review)].filter(Boolean));
  h += '<h3>Reminders</h3><ul>' + PB_REMINDERS.map(function (r) { return '<li>' + e(r) + '</li>'; }).join('') + '</ul>';
  return h;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { pbText: pbText, pbEsc: pbEsc, pbPhone: pbPhone, pbDate: pbDate, pbNormalize: pbNormalize, pbValidate: pbValidate, pbAddMonths: pbAddMonths, pbPracticeDates: pbPracticeDates, pbToText: pbToText, pbWalletCards: pbWalletCards, pbCardsHtml: pbCardsHtml, pbPlanHtml: pbPlanHtml, PB_LIMITS: PB_LIMITS, PB_REMINDERS: PB_REMINDERS, PB_NEEDS: PB_NEEDS, PB_ACCESS: PB_ACCESS, PB_MEDCHECKS: PB_MEDCHECKS };
}
