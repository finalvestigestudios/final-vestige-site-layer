/* Household Emergency Plan Builder: page behavior.
   State is a plain object held in memory. It is never written to cookies, storage, the URL or the network.
   The only ways information leaves the page are the visitor's own Print and Download buttons. */
(function () {
  var app = document.getElementById('pb-app');
  if (!app || typeof pbNormalize !== 'function') return;
  document.documentElement.setAttribute('data-pb-js', '');
  var blank = document.getElementById('pb-blank'); if (blank) blank.removeAttribute('open');

  function emptyState() {
    return { members: [{ name: '', age: 'adult', needs: [], cardNote: '' }], outOfArea: { name: '', phone1: '', phone2: '' },
      contacts: [{ name: '', relation: '', phone: '' }], meeting: { near: '', far: '', outOfArea: '' }, children: [], pets: [], petPlace: '',
      access: { checks: [], note: '' }, meds: { checks: [], pharmacyPhone: '', powerPhone: '', note: '' },
      building: { managerPhone: '', utilityPhone: '', elevator: 'unknown', exits: '', shutoffs: '' }, practice: { drill: '', kit: '', review: '' }, start: '' };
  }
  var raw = emptyState();
  var $ = function (id) { return document.getElementById(id); };
  var uid = 0;

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') n.textContent = attrs[k];
      else if (attrs[k] === true) n.setAttribute(k, '');
      else if (attrs[k] !== false && attrs[k] !== null && attrs[k] !== undefined) n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function getPath(o, p) { return p.split('.').reduce(function (a, k) { return a == null ? undefined : a[k]; }, o); }
  function setPath(o, p, v) { var ks = p.split('.'), last = ks.pop(); var t = ks.reduce(function (a, k) { return a[k]; }, o); t[last] = v; }

  /* ---------- field builders ---------- */
  function field(path, label, o) {
    o = o || {}; var id = 'pb-f-' + (++uid), errId = id + '-err', hintId = id + '-hint';
    var type = o.type || 'text', ctl;
    var val = getPath(raw, path); val = val == null ? '' : val;
    var common = { id: id, 'data-path': path, 'aria-describedby': (o.hint ? hintId + ' ' : '') + errId };
    if (type === 'select') {
      ctl = el('select', common, o.options.map(function (op) { var x = el('option', { value: op[0], text: op[1] }); if (op[0] === val) x.selected = true; return x; }));
    } else if (type === 'textarea') {
      ctl = el('textarea', Object.assign({ rows: 3, maxlength: o.max || 400 }, common)); ctl.value = val;
    } else {
      ctl = el('input', Object.assign({ type: type === 'tel' ? 'tel' : type, maxlength: o.max || 200, autocomplete: 'off', inputmode: type === 'tel' ? 'tel' : null }, common)); ctl.value = val;
      if (o.placeholder) ctl.setAttribute('placeholder', o.placeholder);
    }
    return el('div', { 'class': 'pb-field' }, [el('label', { 'for': id, text: label }), o.hint ? el('span', { id: hintId, 'class': 'pa-tool-note', text: o.hint }) : null, ctl, el('span', { id: errId, 'class': 'pb-err', 'data-err-for': path })]);
  }
  function checks(path, legend, all, labels, hint) {
    var set = el('fieldset', { 'class': 'pa-tool-set' }, [el('legend', { text: legend })]);
    if (hint) set.appendChild(el('p', { 'class': 'pa-tool-note', text: hint }));
    var cur = getPath(raw, path) || [];
    all.forEach(function (k) {
      var id = 'pb-c-' + (++uid);
      var cb = el('input', { type: 'checkbox', id: id, 'data-check': path, value: k }); cb.checked = cur.indexOf(k) !== -1;
      set.appendChild(el('label', { 'class': 'pa-tool-check', 'for': id }, [cb, ' ' + labels[k]]));
    });
    return set;
  }
  function repeater(key, title, noun, add, build, max, intro) {
    var wrap = el('fieldset', { 'class': 'pa-tool-set' }, [el('legend', { text: title })]);
    if (intro) wrap.appendChild(el('p', { 'class': 'pa-tool-note', text: intro }));
    raw[key].forEach(function (row, i) {
      var box = el('div', { 'class': 'pb-row', role: 'group', 'aria-label': noun + ' ' + (i + 1) }, [el('p', { 'class': 'pb-row-title', text: noun + ' ' + (i + 1) })]);
      build(box, i);
      box.appendChild(el('button', { type: 'button', 'class': 'pb-btn pb-btn--quiet', 'data-action': 'remove', 'data-key': key, 'data-index': String(i), text: 'Remove ' + noun.toLowerCase() + ' ' + (i + 1) }));
      wrap.appendChild(box);
    });
    if (raw[key].length < max) wrap.appendChild(el('button', { type: 'button', 'class': 'pb-btn', 'data-action': 'add', 'data-key': key, id: 'pb-add-' + key, text: add }));
    else wrap.appendChild(el('p', { 'class': 'pa-tool-note', text: 'Maximum of ' + max + ' reached.' }));
    return wrap;
  }
  function section(id, title, kids) {
    return el('section', { 'class': 'pb-sec', 'aria-labelledby': id }, [el('h3', { id: id, text: title })].concat(kids));
  }

  var AGE_OPTS = PB_AGE_LABEL ? Object.keys(PB_AGE_LABEL).map(function (k) { return [k, PB_AGE_LABEL[k]]; }) : [];

  function build() {
    app.textContent = '';
    var active = null;
    app.appendChild(section('pb-h-members', '1. Who is in your household', [
      el('p', { 'class': 'pa-tool-note', text: 'First names are enough. The checkboxes only mark what to plan for. They do not record medical details.' }),
      repeater('members', 'Household members', 'Person', 'Add a person', function (box, i) {
        var p = 'members.' + i;
        box.appendChild(field(p + '.name', 'Name', { max: 60 }));
        box.appendChild(field(p + '.age', 'Age group', { type: 'select', options: AGE_OPTS }));
        box.appendChild(checks(p + '.needs', 'Plan for (optional)', PB_NEEDS, PB_NEED_LABEL));
        box.appendChild(field(p + '.cardNote', 'Short note for this person’s wallet card (optional)', { max: 80, hint: 'Anything you write here is printed on the card. Keep it to what you would be comfortable having on a card in a wallet.' }));
      }, 12)
    ]));
    app.appendChild(section('pb-h-contacts', '2. How you reach each other', [
      el('p', { 'class': 'pa-tool-note', text: 'FEMA and the CDC suggest one contact outside your area whom everyone can report to, reachable two ways, and texting before calling.' }),
      el('fieldset', { 'class': 'pa-tool-set' }, [el('legend', { text: 'Out-of-area contact' }), el('div', { 'class': 'pa-tool-grid' }, [
        field('outOfArea.name', 'Name', { max: 60 }), field('outOfArea.phone1', 'Phone or text number', { type: 'tel', max: 30 }), field('outOfArea.phone2', 'Second way to reach them', { type: 'tel', max: 30, hint: 'A second number or another phone.' })])]),
      repeater('contacts', 'Other emergency contacts', 'Contact', 'Add a contact', function (box, i) {
        var p = 'contacts.' + i;
        box.appendChild(el('div', { 'class': 'pa-tool-grid' }, [field(p + '.name', 'Name', { max: 60 }), field(p + '.relation', 'Relationship or role', { max: 80 }), field(p + '.phone', 'Phone', { type: 'tel', max: 30 })]));
      }, 8)
    ]));
    app.appendChild(section('pb-h-meet', '3. Where you meet', [
      el('p', { 'class': 'pa-tool-note', text: 'FEMA suggests meeting places in different directions: one near home and one farther away. Choose places everyone can reach and get into.' }),
      field('meeting.near', 'Near home', { max: 200, hint: 'A place everyone knows, such as a neighbor’s porch or a corner.' }),
      field('meeting.far', 'Outside our neighborhood', { max: 200 }), field('meeting.outOfArea', 'Out of the area (optional)', { max: 200 })
    ]));
    app.appendChild(section('pb-h-school', '4. School and childcare', [
      repeater('children', 'Children and their schools', 'Child', 'Add a child', function (box, i) {
        var p = 'children.' + i;
        box.appendChild(el('div', { 'class': 'pa-tool-grid' }, [field(p + '.name', 'Name', { max: 60 }), field(p + '.school', 'School or childcare', { max: 80 }), field(p + '.phone', 'Their phone', { type: 'tel', max: 30 })]));
        box.appendChild(field(p + '.release', 'Who may pick up, and where families reunite', { type: 'textarea', max: 200, hint: 'Ask the school or provider for its emergency and reunification plan, then write what they tell you.' }));
      }, 12, 'Skip this section if it does not apply.')
    ]));
    app.appendChild(section('pb-h-pets', '5. Pets', [
      repeater('pets', 'Pets', 'Pet', 'Add a pet', function (box, i) {
        var p = 'pets.' + i;
        box.appendChild(el('div', { 'class': 'pa-tool-grid' }, [field(p + '.name', 'Name', { max: 60 }), field(p + '.kind', 'Kind of animal', { max: 80 }), field(p + '.vetPhone', 'Vet phone', { type: 'tel', max: 30 }),
          field(p + '.microchip', 'Microchipped, with up-to-date details?', { type: 'select', options: [['unsure', 'Not sure'], ['yes', 'Yes'], ['no', 'No']] }), field(p + '.kitLocation', 'Where its kit and carrier are kept', { max: 80 })]));
      }, 8, 'Most public shelters accept only service animals, so choose a pet-friendly place ahead of time.'),
      field('petPlace', 'Pet-friendly place we could go', { max: 200 })
    ]));
    app.appendChild(section('pb-h-access', '6. Access and mobility', [
      checks('access.checks', 'Check what applies', PB_ACCESS, PB_ACCESS_LABEL, 'Accessible transport may not be available in an emergency, so ask your local paratransit provider or emergency management office in advance.'),
      field('access.note', 'Notes (optional)', { type: 'textarea', max: 400 })
    ]));
    app.appendChild(section('pb-h-meds', '7. Medicines and powered equipment', [
      el('p', { 'class': 'pb-caution', text: 'This is a list of questions to ask, not advice. Whether a medicine or device can go without power or cold storage, and what to do, depends on the medicine or device. Ask your prescriber, pharmacist or equipment supplier. Do not change how you use any medicine because of this page.' }),
      checks('meds.checks', 'Questions we have asked', PB_MEDCHECKS, PB_MEDCHECK_LABEL),
      el('div', { 'class': 'pa-tool-grid' }, [field('meds.pharmacyPhone', 'Pharmacy phone (optional)', { type: 'tel', max: 30 }), field('meds.powerPhone', 'Power provider phone (optional)', { type: 'tel', max: 30 })]),
      field('meds.note', 'Notes (optional)', { type: 'textarea', max: 400, hint: 'Avoid writing diagnoses or doses here; they will print on the plan.' })
    ]));
    app.appendChild(section('pb-h-building', '8. Building and utilities', [
      el('div', { 'class': 'pa-tool-grid' }, [field('building.managerPhone', 'Building manager or landlord phone', { type: 'tel', max: 30 }), field('building.utilityPhone', 'Electric or gas utility phone', { type: 'tel', max: 30 })]),
      field('building.elevator', 'Does the elevator have backup power?', { type: 'select', options: [['unknown', 'Not sure: ask the manager'], ['yes', 'Yes'], ['no', 'No'], ['na', 'No elevator']] }),
      field('building.exits', 'Exits and stairs we have walked', { max: 200 }),
      field('building.shutoffs', 'Where the shutoffs are (use only if officials tell you to)', { max: 200, hint: 'Learn how from a professional or your utility before an emergency.' })
    ]));
    app.appendChild(section('pb-h-practice', '9. Practice and review', [
      el('p', { 'class': 'pa-tool-note', text: 'FEMA and the CDC both recommend practicing, but they differ on how often to check supplies (six months or a year). These suggested dates are ours: a drill at 3 months, a kit check at 6 and a plan review at 12.' }),
      field('start', 'Start counting from', { type: 'date' }),
      el('button', { type: 'button', 'class': 'pb-btn', 'data-action': 'suggest', text: 'Suggest dates' }),
      el('div', { 'class': 'pa-tool-grid' }, [field('practice.drill', 'Next drill', { type: 'date' }), field('practice.kit', 'Next kit check', { type: 'date' }), field('practice.review', 'Next plan review', { type: 'date' })])
    ]));
    app.appendChild(el('section', { 'class': 'pb-sec', 'aria-labelledby': 'pb-h-remind' }, [el('h3', { id: 'pb-h-remind', text: '10. Decision reminders' }), el('ul', {}, PB_REMINDERS.map(function (r) { return el('li', { text: r }); }))]));
    var bar = el('div', { 'class': 'pb-actions', role: 'group', 'aria-label': 'Print, download or clear' }, [
      el('button', { type: 'button', 'class': 'pb-btn pb-btn--main', 'data-action': 'print-plan', text: 'Print the full plan' }),
      el('button', { type: 'button', 'class': 'pb-btn pb-btn--main', 'data-action': 'print-cards', text: 'Print wallet cards' }),
      el('button', { type: 'button', 'class': 'pb-btn', 'data-action': 'download', text: 'Download as a text file' }),
      el('button', { type: 'button', 'class': 'pb-btn', 'data-action': 'print-blank', text: 'Print a blank worksheet' }),
      el('button', { type: 'button', 'class': 'pb-btn pb-btn--quiet', 'data-action': 'clear', id: 'pb-clear', text: 'Clear everything' })]);
    app.appendChild(bar);
    app.appendChild(el('div', { id: 'pb-confirm', 'class': 'pb-confirm', role: 'group', 'aria-labelledby': 'pb-confirm-t', hidden: true }, [
      el('p', { id: 'pb-confirm-t', text: 'Clear every field on this page? This cannot be undone.' }),
      el('button', { type: 'button', 'class': 'pb-btn pb-btn--main', 'data-action': 'clear-yes', id: 'pb-clear-yes', text: 'Yes, clear everything' }),
      el('button', { type: 'button', 'class': 'pb-btn', 'data-action': 'clear-no', text: 'No, keep my entries' })]));
    renderOutputs();
  }

  /* ---------- outputs ---------- */
  var timer = null;
  function renderOutputs() {
    var pv = $('pb-preview'); if (pv) pv.innerHTML = pbPlanHtml(raw);
  }
  function schedule() { if (timer) clearTimeout(timer); timer = setTimeout(renderOutputs, 120); }
  function status(msg) { var s = $('pb-status'); if (s) { s.textContent = ''; setTimeout(function () { s.textContent = msg; }, 30); } }

  function clearErrors() {
    Array.prototype.forEach.call(app.querySelectorAll('[aria-invalid]'), function (n) { n.removeAttribute('aria-invalid'); });
    Array.prototype.forEach.call(app.querySelectorAll('.pb-err'), function (n) { n.textContent = ''; });
    var box = $('pb-errors'); if (box) { box.textContent = ''; box.hidden = true; }
  }
  function showErrors(errs) {
    clearErrors();
    var box = $('pb-errors'); if (!box || !errs.length) return false;
    var ul = el('ul');
    errs.forEach(function (e) {
      var c = app.querySelector('[data-path="' + e.path + '"]'); if (!c) return;
      c.setAttribute('aria-invalid', 'true');
      var span = app.querySelector('[data-err-for="' + e.path + '"]'); if (span) span.textContent = e.message;
      var lab = c.id && app.querySelector('label[for="' + c.id + '"]');
      ul.appendChild(el('li', {}, [el('a', { href: '#' + c.id, text: (lab ? lab.textContent : e.path) + ': ' + e.message })]));
    });
    box.appendChild(el('p', { text: errs.length + (errs.length === 1 ? ' entry needs' : ' entries need') + ' fixing before you can print or download:' }));
    box.appendChild(ul); box.hidden = false; box.focus();
    return true;
  }
  function validateOrShow() { return !showErrors(pbValidate(raw)); }

  function printKind(kind) {
    if (!validateOrShow()) return;
    $('pb-print-plan').innerHTML = pbPlanHtml(raw);
    $('pb-print-cards').innerHTML = pbCardsHtml(raw);
    document.body.setAttribute('data-pb-print', kind);
    var done = function () { document.body.removeAttribute('data-pb-print'); window.removeEventListener('afterprint', done); };
    window.addEventListener('afterprint', done);
    window.print();
    done();
    status(kind === 'cards' ? 'Wallet cards sent to your printer dialog.' : 'Plan sent to your printer dialog.');
  }
  function download() {
    if (!validateOrShow()) return;
    var blob = new Blob([pbToText(raw)], { type: 'text/plain;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a'); a.href = url; a.download = 'household-emergency-plan.txt';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    status('Plan saved to your device as household-emergency-plan.txt. It was not sent anywhere.');
  }

  /* ---------- events ---------- */
  app.addEventListener('input', function (ev) {
    var t = ev.target, p = t.getAttribute && t.getAttribute('data-path');
    if (p) {
      setPath(raw, p, t.value);
      t.removeAttribute('aria-invalid'); var s = app.querySelector('[data-err-for="' + p + '"]'); if (s) s.textContent = '';
      schedule();
    }
  });
  app.addEventListener('change', function (ev) {
    var t = ev.target, c = t.getAttribute && t.getAttribute('data-check');
    if (c) {
      var arr = getPath(raw, c) || []; var i = arr.indexOf(t.value);
      if (t.checked && i === -1) arr.push(t.value); if (!t.checked && i !== -1) arr.splice(i, 1);
      setPath(raw, c, arr); schedule(); return;
    }
    var p = t.getAttribute && t.getAttribute('data-path');
    if (p && /phone|Phone|drill|kit$|review/.test(p)) {
      var bad = pbValidate(raw).filter(function (e) { return e.path === p; });
      var span = app.querySelector('[data-err-for="' + p + '"]');
      if (bad.length) { t.setAttribute('aria-invalid', 'true'); if (span) span.textContent = bad[0].message; } else { t.removeAttribute('aria-invalid'); if (span) span.textContent = ''; }
    }
  });
  app.addEventListener('click', function (ev) {
    var b = ev.target.closest && ev.target.closest('[data-action]'); if (!b) return;
    var a = b.getAttribute('data-action'), key = b.getAttribute('data-key'), idx = +b.getAttribute('data-index');
    var blanks = { members: { name: '', age: 'adult', needs: [], cardNote: '' }, contacts: { name: '', relation: '', phone: '' }, children: { name: '', school: '', phone: '', release: '' }, pets: { name: '', kind: '', vetPhone: '', microchip: 'unsure', kitLocation: '' } };
    if (a === 'add') {
      raw[key].push(JSON.parse(JSON.stringify(blanks[key]))); build();
      var rows = app.querySelectorAll('#pb-add-' + key); var group = raw[key].length; var last = app.querySelectorAll('[data-path^="' + key + '.' + (group - 1) + '."]')[0]; if (last) last.focus();
      status('Added. Now ' + group + '.');
    } else if (a === 'remove') {
      raw[key].splice(idx, 1); build();
      var add = $('pb-add-' + key); if (add) add.focus(); else var h = app.querySelector('h3'); if (h) { h.setAttribute('tabindex', '-1'); h.focus(); }
      status('Removed.');
    } else if (a === 'suggest') {
      var r = pbDate(raw.start);
      if (!r.ok || r.value === '') { var f = app.querySelector('[data-path="start"]'); showErrors([{ path: 'start', message: 'Pick a start date first.' }]); return; }
      var d = pbPracticeDates(r.value); raw.practice.drill = d.drill; raw.practice.kit = d.kit; raw.practice.review = d.review;
      ['drill', 'kit', 'review'].forEach(function (k) { app.querySelector('[data-path="practice.' + k + '"]').value = d[k]; });
      clearErrors(); schedule(); status('Suggested dates filled in. You can change them.');
    } else if (a === 'print-plan') printKind('plan');
    else if (a === 'print-cards') printKind('cards');
    else if (a === 'download') download();
    else if (a === 'print-blank') {
      var d = $('pb-blank'); if (d) d.setAttribute('open', '');
      document.body.setAttribute('data-pb-print', 'blank'); window.print(); document.body.removeAttribute('data-pb-print'); if (d) d.removeAttribute('open');
    }
    else if (a === 'clear') { $('pb-confirm').hidden = false; $('pb-clear-yes').focus(); }
    else if (a === 'clear-no') { $('pb-confirm').hidden = true; $('pb-clear').focus(); }
    else if (a === 'clear-yes') {
      raw = emptyState(); build(); clearErrors();
      $('pb-print-plan').innerHTML = ''; $('pb-print-cards').innerHTML = '';
      var top = $('pb-top'); if (top) top.focus();
      status('Everything has been cleared.');
    }
  });
  build();
})();
