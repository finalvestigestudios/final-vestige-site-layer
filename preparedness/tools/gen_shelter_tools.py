#!/usr/bin/env python3
"""Generates the three Shelter, Power and Family Communication tool pages.

Why a generator: each tool has a static, printable form that must keep working with JavaScript off. The markup for repeated
rows and for the no-JavaScript checklist is produced from one source so the static fallback and the scripted version cannot
drift apart. Run:  python -I preparedness/tools/gen_shelter_tools.py   (add --check to verify the committed files are current)
The generated files are content/tools/<slug>.body.html and .meta.json; the tests call --check.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
OUT = ROOT / "content" / "tools"
UPDATED = "2026-11-01"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def node_json(expr: str) -> object:
    node = shutil.which("node")
    if not node:
        raise SystemExit("node is required to generate the outage planner's static checklist")
    code = ("Object.assign(global, require('./shelter_common.js'));"
            "const og=require('./outage_items.js');console.log(JSON.stringify(" + expr + "))")
    r = subprocess.run([node, "-e", code], capture_output=True, text=True, cwd=str(TOOLS), timeout=60)
    if r.returncode:
        raise SystemExit(r.stderr)
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------------------------------- shared CSS
CSS = r"""
<style>
.pa-sheet { margin: 0 0 24px; padding: 20px; background: var(--pa-surface); border: 1px solid var(--pa-line); }
.pa-sheet fieldset { margin: 0 0 18px; padding: 14px 16px; border: 1px solid var(--pa-line); min-width: 0; }
.pa-sheet legend { padding: 0 6px; font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: var(--pa-gold); font-weight: 600; }
.pa-sheet label { display: block; font-size: 14px; font-weight: 600; margin: 0 0 4px; color: var(--pa-text); }
.pa-sheet input[type="text"], .pa-sheet input[type="tel"], .pa-sheet input[type="date"], .pa-sheet select, .pa-sheet textarea { width: 100%; box-sizing: border-box; min-height: 44px; padding: 8px 12px; font: inherit; font-size: 16px; color: var(--pa-text); background: var(--pa-bg); border: 1px solid #5B5C54; border-radius: 0; color-scheme: dark; }
.pa-sheet textarea { min-height: 88px; resize: vertical; }
.pa-sheet :focus-visible, .pa-btn:focus-visible { outline: 3px solid var(--pa-gold); outline-offset: 2px; }
.pa-row { display: grid; gap: 10px; margin: 0 0 14px; padding: 0 0 12px; border-bottom: 1px dashed var(--pa-line); }
.pa-row-title { margin: 0; font-size: 13px; color: var(--pa-muted); grid-column: 1 / -1; }
@container (min-width: 560px) { .pa-row--2 { grid-template-columns: repeat(2, 1fr); } .pa-row--3 { grid-template-columns: repeat(3, 1fr); } .pa-row--4 { grid-template-columns: repeat(4, 1fr); } .pa-grid2 { grid-template-columns: repeat(2, 1fr); } }
.pa-grid2 { display: grid; gap: 14px; margin: 0 0 12px; }
.pa-check { display: flex; gap: 12px; align-items: flex-start; font-weight: 400 !important; min-height: 44px; padding: 6px 0; }
.pa-check input { width: 24px; height: 24px; flex: none; margin: 0; accent-color: var(--pa-gold); }
.pa-check span { font-size: 15px; line-height: 24px; }
.pa-hint { display: block; font-size: 14px; color: var(--pa-muted); margin: 4px 0 0; font-weight: 400; }
.pa-out { margin: 0 0 12px; padding: 12px 16px; border: 1px solid var(--pa-line); background: var(--pa-surface-2); }
.pa-out ul { margin: 0; padding-left: 20px; }
.pa-out li { margin: 0 0 6px; }
.pa-out .pa-gap { color: var(--pa-warn); }
.pa-list { list-style: none; margin: 0 0 18px; padding: 0; }
.pa-list li { margin: 0; padding: 0; border-bottom: 1px solid var(--pa-line); }
.pa-src { display: block; font-size: 13px; color: var(--pa-muted); margin: -2px 0 8px 36px; }
.pa-gridsvg { display: block; width: 100%; height: auto; max-height: 360px; border: 1px solid var(--pa-line); background: var(--pa-bg); }
.pa-vh { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.pa-printonly { display: none; }
.pa-sheet [hidden], .pa-printbar [hidden], .pa-sheet button[hidden] { display: none !important; }
@media (max-width: 420px) { .pa-sheet { padding: 14px 12px; } .pa-sheet fieldset { padding: 12px 10px; } }
@media print {
  @page { margin: 0.5in; }
  .pa-article:has(.pa-printsheet) > *:not(.pa-shell) { display: none !important; }
  .pa-article:has(.pa-printsheet) .pa-shell > *:not(.pa-body) { display: none !important; }
  .pa-article:has(.pa-printsheet) .pa-body > *:not(.pa-printsheet):not(:has(.pa-printsheet)) { display: none !important; }
  .pa-row--2 { grid-template-columns: repeat(2, 1fr); } .pa-row--3 { grid-template-columns: repeat(3, 1fr); } .pa-row--4 { grid-template-columns: repeat(4, 1fr); } .pa-grid2 { grid-template-columns: repeat(2, 1fr); }
  .pa-sheet { border: 0 !important; padding: 0 !important; }
  .pa-noprint, .pa-printbar { display: none !important; }
  .pa-sheet fieldset { border: 1px solid #000 !important; break-inside: auto; margin: 0 0 8pt; padding: 6pt 8pt; }
  .pa-hint { font-size: 8pt; margin: 0 0 3pt; }
  .pa-sheet p { margin: 0 0 4pt; font-size: 9.5pt; }
  .pa-sheet legend { font-size: 9pt; color: #000 !important; }
  .pa-sheet label { font-size: 9pt; color: #000 !important; }
  .pa-sheet input[type="text"], .pa-sheet input[type="tel"], .pa-sheet input[type="date"], .pa-sheet select, .pa-sheet textarea { border: 0 !important; border-bottom: 1px solid #000 !important; min-height: 0; padding: 2px 0; font-size: 10.5pt; color: #000 !important; }
  .pa-sheet textarea { resize: none; min-height: 40pt; }
  .pa-row { break-inside: avoid; border-bottom: 0; gap: 6pt; }
  .pa-check { min-height: 0; padding: 2pt 0; }
  .pa-check input { width: 11pt; height: 11pt; }
  .pa-check span { font-size: 10pt; line-height: 1.3; }
  .pa-src { margin-left: 0; font-size: 8pt; }
  .pa-gridsvg { max-height: 3.4in; border: 1px solid #000; }
  .pa-out { border: 1px solid #000; }
}
</style>
"""

NOSCRIPT_NOTE = ('<noscript><div class="pa-alert pa-alert--note"><p class="pa-alert-title">JavaScript is off</p>'
                 '<p>%s The form below still works and prints. Only the automatic reminders and the text download need JavaScript.</p></div></noscript>')


def field(fid: str, label: str, kind: str = "text", maxlen: int = 60, attrs: str = "", hint: str = "") -> str:
    h = f'<span id="{fid}-h" class="pa-hint">{esc(hint)}</span>' if hint else ""
    d = f' aria-describedby="{fid}-h"' if hint else ""
    if kind == "textarea":
        return f'<div><label for="{fid}">{esc(label)}</label><textarea id="{fid}" maxlength="{maxlen}" rows="3"{d} {attrs}></textarea>{h}</div>'
    if kind == "date":
        return f'<div><label for="{fid}">{esc(label)}</label><input id="{fid}" type="date"{d} {attrs}>{h}</div>'
    typ = "tel" if kind == "tel" else "text"
    ac = ' autocomplete="off"'
    return f'<div><label for="{fid}">{esc(label)}</label><input id="{fid}" type="{typ}" maxlength="{maxlen}"{ac}{d} {attrs}>{h}</div>'


def check(fid: str, label: str, attrs: str = "") -> str:
    return f'<label class="pa-check" for="{fid}"><input id="{fid}" type="checkbox" {attrs}><span>{esc(label)}</span></label>'


def list_rows(prefix: str, group: str, count: int, cols: list[tuple[str, str, int, str]], title: str, cls: str) -> str:
    out = []
    for i in range(count):
        cells = "".join(field(f"{prefix}-{group}-{i}-{k}", lab, "text", n, f'data-g="{group}" data-i="{i}" data-f="{k}"') for k, lab, n, _ in cols)
        out.append(f'<div class="pa-row {cls}" role="group" aria-label="{esc(title)} {i + 1}" data-list="{group}" data-i="{i}"><p class="pa-row-title">{esc(title)} {i + 1}</p>{cells}</div>')
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------------- tool 1
FW_SCRIPT = r"""
<script>
{{inline-js:shelter_common.js}}
{{inline-js:fire_worksheet.js}}
(function () {
  var form = document.getElementById('fw'); if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  function today() { var d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  var CAP = { rooms: 40, people: 30, practice: 12 };
  function collect() {
    var data = { rooms: [], people: [], practice: [], meeting: {}, roles: {}, alarms: {}, building: {} };
    form.querySelectorAll('[data-g]').forEach(function (el) {
      var g = el.getAttribute('data-g'), f = el.getAttribute('data-f'), i = el.getAttribute('data-i');
      var v = el.type === 'checkbox' ? el.checked : el.value;
      if (i !== null) { var n = Number(i); data[g][n] = data[g][n] || {}; data[g][n][f] = v; }
      else if (g === 'top') { data[f] = v; }
      else { data[g][f] = v; }
    });
    ['rooms', 'people', 'practice'].forEach(function (g) { data[g] = data[g].filter(Boolean); });
    return data;
  }
  function setList(id, lines, cls) {
    var box = $(id); while (box.firstChild) box.removeChild(box.firstChild);
    if (!lines.length) return;
    var ul = document.createElement('ul');
    lines.forEach(function (l) { var li = document.createElement('li'); if (cls && l.level === 'gap') li.className = cls; li.textContent = l.text; ul.appendChild(li); });
    box.appendChild(ul);
  }
  function render() {
    var data = collect(), t = today();
    var checks = fwCheckPlan(data, t);
    var out = $('fw-check'); while (out.firstChild) out.removeChild(out.firstChild);
    var h = document.createElement('p'); h.className = 'pa-hint'; h.textContent = checks.length ? 'Blanks and reminders (a prompt to fill things in, not a safety rating):' : 'Nothing left blank that this check looks for. That does not mean the plan is safe; practice it.';
    out.appendChild(h);
    if (checks.length) { var ul = document.createElement('ul'); checks.forEach(function (c) { var li = document.createElement('li'); li.className = c.level === 'gap' ? 'pa-gap' : ''; li.textContent = c.text; ul.appendChild(li); }); out.appendChild(ul); }
    var by = fwSmokeAlarmReplaceBy(data.alarms.mfgDate);
    $('fw-replace').textContent = by ? 'Replace this smoke alarm by ' + by + ' (10 years after manufacture).' : '';
    var last = data.practice.map(function (p) { return p.date; }).filter(Boolean).sort().pop();
    var nxt = last ? fwNextPractice(last) : null;
    $('fw-next').textContent = nxt ? 'Next practice due about ' + nxt + ' (twice a year).' : '';
  }
  function addRow(group) {
    var rows = form.querySelectorAll('[data-list="' + group + '"]');
    if (rows.length >= CAP[group]) return;
    var last = rows[rows.length - 1], n = rows.length, clone = last.cloneNode(true);
    clone.setAttribute('data-i', n); clone.classList.add('pa-extra');
    var title = (last.getAttribute('aria-label') || '').replace(/\s*\d+$/, '') + ' ' + (n + 1);
    clone.setAttribute('aria-label', title); clone.querySelector('.pa-row-title').textContent = title;
    clone.querySelectorAll('[data-g]').forEach(function (el) {
      var oldId = el.id; el.setAttribute('data-i', n);
      el.id = oldId.replace(/-\d+-([a-z0-9]+)$/i, '-' + n + '-$1');
      if (el.type === 'checkbox') el.checked = false; else el.value = '';
      var lab = clone.querySelector('label[for="' + oldId + '"]'); if (lab) lab.setAttribute('for', el.id);
    });
    last.parentNode.insertBefore(clone, last.nextSibling);
    var first = clone.querySelector('input'); if (first) first.focus();
    render();
  }
  form.addEventListener('input', render); form.addEventListener('change', render);
  [['fw-add-room', 'rooms'], ['fw-add-person', 'people'], ['fw-add-practice', 'practice']].forEach(function (p) {
    var b = $(p[0]); if (!b) return; b.hidden = false; b.addEventListener('click', function () { addRow(p[1]); });
  });
  $('fw-print').hidden = false; $('fw-print').addEventListener('click', function () { window.print(); });
  $('fw-download').hidden = false; $('fw-download').addEventListener('click', function () { paDownloadText('home-fire-escape-plan.txt', fwText(collect(), today())); });
  $('fw-reset').hidden = false; $('fw-reset').addEventListener('click', function () {
    form.reset(); form.querySelectorAll('.pa-extra').forEach(function (r) { r.parentNode.removeChild(r); }); render();
  });
  render();
})();
</script>
"""


def fire_body() -> str:
    P = "fw"
    rooms = list_rows(P, "rooms", 8, [("room", "Room", 60, ""), ("out1", "First way out", 60, ""), ("out2", "Second way out", 60, ""), ("notes", "Notes (stuck window, ladder, who helps)", 120, "")], "Room", "pa-row--4")
    people = list_rows(P, "people", 5, [("name", "Who", 60, ""), ("need", "Needs help with", 60, ""), ("helper", "Helper", 60, ""), ("backup", "Backup helper", 60, ""), ("notes", "Notes", 120, "")], "Person", "pa-row--3")
    practice = list_rows(P, "practice", 4, [("date", "Date", 10, ""), ("who", "Who took part", 120, ""), ("when", "Day or night", 60, ""), ("learned", "What we learned or fixed", 120, "")], "Practice", "pa-row--4")
    practice = practice.replace('type="text" maxlength="10" autocomplete="off"', 'type="date"')
    svg = ('<svg class="pa-gridsvg" role="img" aria-label="Blank square grid for drawing your floor plan by hand. The Rooms table above is the text version of the same plan." viewBox="0 0 400 220" preserveAspectRatio="none">'
           '<defs><pattern id="fw-pat" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#8a8a80" stroke-width="0.6"/></pattern></defs>'
           '<rect width="400" height="220" fill="url(#fw-pat)" stroke="#8a8a80"/></svg>')
    return f"""<section class="pa-act" aria-labelledby="act-h">
<h2 id="act-h">What to do now</h2>
<ol>
<li><strong>Fill in what you know.</strong> Blanks are fine. The point is to talk it through with everyone who lives in the home.</li>
<li><strong>Mark two ways out of every room,</strong> choose one meeting place outside in front of the home, and write down who helps whom, with a backup.{{{{cite:usfa-fire-escape}}}}{{{{cite:shelter-nfpa-escape}}}}</li>
<li><strong>Print it or save it as a PDF,</strong> draw your floor plan by hand on the grid, and put the page where everyone can see it.</li>
<li><strong>Practice with everyone at least twice a year,</strong> as a simulation only.{{{{cite:shelter-nfpa-escape}}}}</li>
</ol>
<p class="pa-act-note"><strong>If there is a fire right now,</strong> get out, stay out and call 911 from outside. <strong>Private by design:</strong> what you type stays on this page. It is not sent anywhere and is not saved. Closing the tab clears it, so print or save a PDF to keep a copy. This worksheet does not replace your building's official evacuation plan or advice from your fire department.</p>
</section>
{CSS}
{NOSCRIPT_NOTE % 'This worksheet is a printable form.'}
<h2 id="worksheet">Your home fire escape plan</h2>
<form class="pa-sheet pa-printsheet" id="fw" onsubmit="return false" aria-describedby="fw-help">
<p id="fw-help">Every field is optional. Short answers are best. Nothing here asks for an address.</p>

<fieldset><legend>Basics</legend>
<div class="pa-grid2">
{field("fw-fireDept", "Fire department emergency number", "tel", 60, 'data-g="top" data-f="fireDept"', "Write it down so anyone can call from outside. NFPA says everyone should know it.")}
{field("fw-planDate", "Date you made this plan", "date", 10, 'data-g="top" data-f="planDate"')}
</div>
{check("fw-inApartment", "We live in an apartment, condominium or high-rise (adds a building section below)", 'data-g="top" data-f="inApartment"')}
</fieldset>

<fieldset><legend>Two ways out of every room</legend>
<p class="pa-hint">Include bedrooms first. Check that both ways out can be used by everyone who sleeps there.</p>
{rooms}
<div class="pa-noprint"><button type="button" class="pa-btn pa-btn--ghost" id="fw-add-room" hidden>Add another room</button></div>
</fieldset>

<fieldset><legend>Outside meeting place</legend>
<div class="pa-grid2">
{field("fw-meeting-primary", "Meet here first (in front of the home, a safe distance away)", "text", 120, 'data-g="meeting" data-f="primary"', "For example a neighbor's house, a light post, a mailbox or a stop sign.")}
{field("fw-meeting-alternate", "If that is not possible, meet here", "text", 120, 'data-g="meeting" data-f="alternate"')}
</div>
</fieldset>

<fieldset><legend>People who need help getting out</legend>
<p class="pa-hint">Infants, older adults, and anyone with a disability or mobility limitation. NFPA says to assign a helper and a backup.</p>
{people}
<div class="pa-noprint"><button type="button" class="pa-btn pa-btn--ghost" id="fw-add-person" hidden>Add another person</button></div>
</fieldset>

<fieldset><legend>Who does what</legend>
<div class="pa-grid2">
{field("fw-roles-wake", "Who wakes the children or others who may not wake", "text", 120, 'data-g="roles" data-f="wake"')}
{field("fw-roles-pets", "Who looks after pets (tell firefighters if one is trapped)", "text", 120, 'data-g="roles" data-f="pets"')}
{field("fw-roles-call", "Who calls 911 from outside", "text", 120, 'data-g="roles" data-f="call"')}
{field("fw-roles-other", "Childcare, caregiver or other responsibilities", "text", 120, 'data-g="roles" data-f="other"')}
</div>
</fieldset>

<fieldset><legend>Smoke and carbon monoxide alarms</legend>
<div class="pa-grid2">
{field("fw-alarms-locations", "Where the alarms are", "textarea", 300, 'data-g="alarms" data-f="locations"', "NFPA: inside and outside every sleeping area and on every level.")}
{field("fw-alarms-coNote", "Carbon monoxide alarm notes", "text", 120, 'data-g="alarms" data-f="coNote"', "Follow the maker's replacement instructions.")}
{field("fw-alarms-lastTest", "Date you last tested the alarms", "date", 10, 'data-g="alarms" data-f="lastTest"', "NFPA: test every alarm once a month.")}
{field("fw-alarms-mfgDate", "Manufacture date printed on a smoke alarm", "date", 10, 'data-g="alarms" data-f="mfgDate"', "NFPA: replace the whole unit 10 years after manufacture.")}
</div>
<p id="fw-replace" class="pa-hint" role="status"></p>
</fieldset>

<fieldset><legend>Practice log (at least twice a year)</legend>
<p class="pa-hint">Use the alarm's test button to start a drill, then everyone goes to the meeting place. Never use real smoke, flame or heat, and never switch off power or any safety or medical equipment.</p>
{practice}
<p id="fw-next" class="pa-hint" role="status"></p>
<div class="pa-noprint"><button type="button" class="pa-btn pa-btn--ghost" id="fw-add-practice" hidden>Add another practice</button></div>
</fieldset>

<fieldset><legend>If you live in an apartment, condominium or high-rise</legend>
<div class="pa-grid2">
{field("fw-building-manager", "Building manager or landlord contact", "text", 120, 'data-g="building" data-f="manager"')}
{field("fw-building-stairs", "Where the exit stairs are on your floor", "text", 120, 'data-g="building" data-f="stairs"')}
{field("fw-building-alarmProcedure", "What the building does when the alarm sounds (announcements, who to follow)", "textarea", 300, 'data-g="building" data-f="alarmProcedure"')}
{field("fw-building-nonStairPlan", "The plan for anyone who cannot use the stairs, agreed with your manager and the fire department", "textarea", 300, 'data-g="building" data-f="nonStairPlan"')}
</div>
</fieldset>

<fieldset><legend>Floor plan</legend>
<p class="pa-hint">Draw your home on the grid after you print it: all doors and windows, two ways out of every room, and the meeting place. The table of rooms above is the text version of the same plan.</p>
{svg}
</fieldset>

<div class="pa-printbar pa-noprint">
<button type="button" class="pa-btn" id="fw-print" hidden>Print or save as PDF</button>
<button type="button" class="pa-btn pa-btn--ghost" id="fw-download" hidden>Download as text</button>
<button type="button" class="pa-btn pa-btn--ghost" id="fw-reset" hidden>Clear everything</button>
</div>
</form>
<div id="fw-check" class="pa-out pa-noprint" role="status" aria-live="polite" aria-label="Blanks and reminders"></div>

<h2 id="how">How it works, and what it will not do</h2>
<p>The page is a form with a few small helpers. It does not score your plan or judge whether it is safe. It points out blanks against what the agencies ask for: two ways out of every room, a meeting place in front of the home, a helper and a backup for anyone who needs help, practice at least twice a year, and a smoke alarm tested monthly and replaced 10 years after its manufacture date.{{{{cite:usfa-fire-escape}}}}{{{{cite:shelter-nfpa-escape}}}}{{{{cite:shelter-nfpa-smoke-alarms}}}} Its fields follow USFA's printable escape grid, which asks for the fire department's number, a map showing all doors and windows, two ways out of each room, a drawn meeting place, and practice twice a year.{{{{cite:shelter-usfa-escape-grid}}}}</p>
<p>The floor plan is a printed grid you draw on by hand, with the rooms table as the text alternative. We chose that over a drawing canvas because a hand drawing needs no software, works with a pencil, a screen reader user can complete the table, and nothing about your home layout has to be stored or sent anywhere.</p>
<div class="pa-alert pa-alert--stop"><p class="pa-alert-title">Practice as a simulation only</p>
<p>The sources ask you to practice twice a year, to practice finding your way out in the dark, and to find out whether children and others wake to the alarm.{{{{cite:shelter-nfpa-escape}}}}{{{{cite:shelter-ready-home-fires}}}} None of them asks for real smoke, flame or heat, and this page does not either. Do not switch off power, gas or any medical or safety equipment as part of a drill, do not block or lock any exit to test it, and clear tripping hazards before a dark or eyes-closed run.</p></div>
<p><span class="pa-tag pa-tag--ed">Editor's note</span> If someone in your home uses stairs differently, or lives on an upper floor of a tall building, the plan above is only the start. The building's own plan and your fire department's advice come first. In a high-rise, USFA and NFPA make leaving by the stairs the default, with sealing yourself in reserved for people who cannot get out.{{{{cite:shelter-nfpa-high-rise}}}}{{{{cite:shelter-usfa-high-rise-handout}}}} For the full reasoning, read {{{{link:home-fire-escape-plan|Two ways out: home fire planning}}}}. For the next steps after a fire plan, see {{{{link:shelter-or-evacuate|shelter in place or evacuate}}}} and {{{{link:family-communication-plan|the family communication plan}}}}.</p>
<h2 id="privacy">Privacy and printing</h2>
<p>Nothing you type is sent, stored in cookies or browser storage, or kept after you close the page. Printing is the only way to keep a copy. Choose "Save as PDF" in your browser's print dialog if you want a file. A worksheet that lists who needs help getting out is personal; keep the printed copy at home, and think before posting a photo of it.</p>
<p>A human safety review is required before this tool is public, and the box at the bottom of the page shows where that stands.</p>
{FW_SCRIPT}
"""


# ---------------------------------------------------------------------------------------------------- tool 2
OP_SCRIPT = r"""
<script>
{{inline-js:shelter_common.js}}
{{inline-js:outage_items.js}}
(function () {
  var form = document.getElementById('op'); if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  var out = $('op-out'), summary = $('op-summary');
  var checked = {}, contacts = {};
  function answers() { var a = {}; OUTAGE_QUESTIONS.forEach(function (q) { var el = $('op-q-' + q.key); a[q.key] = !!(el && el.checked); }); return a; }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function render() {
    var a = answers(), list = buildOutageChecklist(a);
    while (out.firstChild) out.removeChild(out.firstChild);
    var chosen = OUTAGE_QUESTIONS.filter(function (q) { return a[q.key]; }).map(function (q) { return q.label; });
    summary.textContent = chosen.length ? 'Planned for: ' + chosen.join('; ') + '.' : 'No household details selected: showing the basic checklist.';
    list.groups.forEach(function (g, gi) {
      var h = el('h3', null, g.title); h.id = 'op-g-' + g.id; out.appendChild(h);
      var ul = el('ul', 'pa-list'); ul.setAttribute('aria-labelledby', h.id);
      g.items.forEach(function (it) {
        var li = el('li'), lab = el('label', 'pa-check'), box = el('input'), span = el('span', null, it.text);
        box.type = 'checkbox'; box.id = 'op-i-' + it.id; box.checked = !!checked[it.id];
        box.addEventListener('change', function () { checked[it.id] = box.checked; });
        lab.setAttribute('for', box.id); lab.appendChild(box); lab.appendChild(span); li.appendChild(lab);
        li.appendChild(el('span', 'pa-src', 'Source: ' + it.src + (it.editor ? '' : '')));
        ul.appendChild(li);
      });
      out.appendChild(ul);
    });
    var h2 = el('h3', null, 'Contacts to fill in'); h2.id = 'op-g-contacts'; out.appendChild(h2);
    var grid = el('div', 'pa-grid2');
    list.contacts.forEach(function (c) {
      var d = el('div'), lab = el('label', null, c.label), inp = el('input');
      inp.type = 'text'; inp.maxLength = 120; inp.autocomplete = 'off'; inp.id = 'op-c-' + c.key; inp.value = contacts[c.key] || '';
      inp.addEventListener('input', function () { contacts[c.key] = inp.value; });
      lab.setAttribute('for', inp.id); d.appendChild(lab); d.appendChild(inp); grid.appendChild(d);
    });
    out.appendChild(grid);
  }
  form.addEventListener('change', function (e) { if (e.target && /^op-q-/.test(e.target.id)) render(); });
  $('op-static').hidden = true; $('op-live').hidden = false;
  $('op-print').hidden = false; $('op-print').addEventListener('click', function () { window.print(); });
  $('op-download').hidden = false; $('op-download').addEventListener('click', function () {
    var done = Object.keys(checked).filter(function (k) { return checked[k]; });
    paDownloadText('power-outage-checklist.txt', outageText(answers(), done, contacts));
  });
  $('op-reset').hidden = false; $('op-reset').addEventListener('click', function () { form.reset(); checked = {}; contacts = {}; render(); });
  render();
})();
</script>
"""


def outage_body() -> str:
    qs = node_json("og.OUTAGE_QUESTIONS")
    groups = node_json("og.OUTAGE_GROUPS")
    items = node_json("og.OUTAGE_ITEMS")
    src = node_json("og.OUTAGE_SRC")
    contacts = node_json("og.OUTAGE_CONTACTS")
    qlab = {q["key"]: q["label"] for q in qs}
    boxes = "\n".join(check(f"op-q-{q['key']}", q["label"], "") for q in qs)
    static = []
    for g in groups:
        rows = []
        for it in items:
            if it["g"] != g["id"]:
                continue
            cond = ""
            if it["when"]:
                cond = "If: " + "; or ".join(qlab[k][0].lower() + qlab[k][1:] for k in it["when"]) + ". "
            rows.append(f'<li><label class="pa-check" for="ops-{it["id"]}"><input id="ops-{it["id"]}" type="checkbox"><span>{esc(cond + it["text"])}</span></label><span class="pa-src">Source: {esc(src[it["src"]])}</span></li>')
        static.append(f'<h3 id="ops-g-{g["id"]}">{esc(g["title"])}</h3><ul class="pa-list" aria-labelledby="ops-g-{g["id"]}">' + "".join(rows) + "</ul>")
    crow = "".join(f'<div><label for="ops-c-{c["key"]}">{esc(c["label"])}</label><input id="ops-c-{c["key"]}" type="text" maxlength="120" autocomplete="off"></div>' for c in contacts)
    static_html = "".join(static) + f'<h3 id="ops-g-contacts">Contacts to fill in</h3><div class="pa-grid2">{crow}</div>'
    return f"""<section class="pa-act" aria-labelledby="act-h">
<h2 id="act-h">What to do now</h2>
<ol>
<li><strong>Tell the planner about your household.</strong> Tick what applies. Nothing is required.</li>
<li><strong>Work down the checklist it builds,</strong> and tick items as you finish them. Every item says which agency page it comes from.</li>
<li><strong>Fill in the contacts,</strong> then print or save the page as a PDF, or download it as a text file.</li>
<li><strong>If someone relies on electric medical equipment or refrigerated medicine,</strong> make an individual plan with their provider, the device supplier and your electric utility. This page cannot do that for you.{{{{cite:shelter-fema-power-outage-sheet}}}}{{{{cite:shelter-ready-disabilities}}}}</li>
</ol>
<p class="pa-act-note"><strong>In an emergency,</strong> call 911. Carbon monoxide symptoms (headache, dizziness, weakness, nausea, confusion) mean get outside to fresh air first, then call 911.{{{{cite:shelter-cpsc-co}}}} <strong>Private by design:</strong> your answers stay on this page and are not sent or saved. Closing the tab clears them.</p>
</section>
{CSS}
{NOSCRIPT_NOTE % 'The complete checklist is shown below with a note on who each item is for.'}
<h2 id="planner">Your household</h2>
<form class="pa-sheet" id="op" onsubmit="return false" aria-describedby="op-help">
<p id="op-help">Tick everything that applies. The checklist below changes as you tick.</p>
<fieldset><legend>About your household</legend>
<div class="pa-grid2">
{boxes}
</div>
</fieldset>
<div class="pa-printbar pa-noprint">
<button type="button" class="pa-btn" id="op-print" hidden>Print or save as PDF</button>
<button type="button" class="pa-btn pa-btn--ghost" id="op-download" hidden>Download as text</button>
<button type="button" class="pa-btn pa-btn--ghost" id="op-reset" hidden>Clear everything</button>
</div>
</form>
<div class="pa-printsheet">
<h2 id="checklist">Your checklist</h2>
<p id="op-summary" class="pa-hint" role="status" aria-live="polite"></p>
<div id="op-live" hidden><div id="op-out" class="pa-sheet"></div></div>
<div id="op-static" class="pa-sheet">
{static_html}
</div>
</div>

<h2 id="medical">If someone depends on medical equipment or refrigerated medicine</h2>
<p>This is the part of outage planning that most needs a plan made for one household, with the people who know the equipment. FEMA's December 2023 sheet says to talk to your doctor to make a plan for how you will use medical devices that need electricity and how you will store your medications.{{{{cite:shelter-fema-power-outage-sheet}}}} Ready.gov's disability page suggests asking your power provider about priority restoration, knowing more than one treatment facility if you rely on dialysis, and planning how to keep equipment running or replace it.{{{{cite:shelter-ready-disabilities}}}} Ready.gov's outage page asks you to find out how long medication can be stored at higher temperatures.{{{{cite:shelter-ready-power-outages}}}}</p>
<p>For a long outage, the agencies use different words. FEMA's sheet says to replace refrigerated medications if the power is out for a day or more unless the label says otherwise, to call your doctor or pharmacist if you depend on a refrigerated medication that has been at room temperature, and to use the medicine only until you have a new supply.{{{{cite:shelter-fema-power-outage-sheet}}}} <strong>Do not stop, skip or throw out a medicine you depend on without asking your pharmacist or prescriber.</strong> The CDC also says not to stop or change your medicines until you talk to your doctor.{{{{cite:shelter-cdc-heat}}}}</p>
<div class="pa-alert pa-alert--stop"><p class="pa-alert-title">What this tool will not tell you</p>
<p>It will not say how large a generator or battery you need, how to wire one, how much fuel to store, how long equipment will run, or how to operate or ventilate any fuel-burning device. None of the agency pages we verified gives those details, and getting them wrong can kill. The planner repeats the agencies' rules for generators and carbon monoxide only: outdoors, at least 20 feet from windows, doors and vents, exhaust away from the home, never connected to the home's wiring, and a working battery carbon monoxide alarm indoors.{{{{cite:shelter-cpsc-co}}}}{{{{cite:shelter-ready-evacuation}}}}{{{{cite:shelter-fema-power-outage-sheet}}}} For the reasoning and the places where the agencies disagree, read {{{{link:outage-heat-cold-generators|heat, cold and generator safety in an outage}}}}.</p></div>

<h2 id="sources">Where the checklist comes from</h2>
<p>Each item names its source. The pages behind the list are the CDC's power-outage, winter-storm, heat and carbon monoxide pages,{{{{cite:shelter-cdc-power-outage}}}}{{{{cite:shelter-cdc-winter-storm}}}}{{{{cite:shelter-cdc-heat}}}}{{{{cite:shelter-cdc-co-basics}}}} Ready.gov's power-outage, heat, winter-weather, shelter, tech and building pages,{{{{cite:shelter-ready-power-outages}}}}{{{{cite:shelter-ready-heat}}}}{{{{cite:shelter-ready-winter-weather}}}}{{{{cite:shelter-ready-shelter}}}}{{{{cite:shelter-ready-tech}}}}{{{{cite:shelter-ready-plan-locations}}}} FEMA's December 2023 sheet,{{{{cite:shelter-fema-power-outage-sheet}}}} NOAA Weather Radio,{{{{cite:shelter-nws-nwr}}}} the CPSC's carbon monoxide pages,{{{{cite:shelter-cpsc-co}}}} and USDA's food-safety guidance for emergencies.{{{{cite:shelter-usda-fsis-emergencies}}}}{{{{cite:fsis-power-failure}}}} Two items are marked as the editor's suggestion because no source says them. Food items follow USDA; where Ready.gov words a time limit differently (food at 40 F or higher for two hours), the item says so instead of silently picking one.</p>
<p><span class="pa-tag pa-tag--ed">Editor's note</span> The checklist is deliberately conservative. A missing item is not a statement that something is unsafe or unnecessary; it means we could not trace it to a verified source. A human safety review is required before this tool is public, and the box at the bottom of the page shows where that stands.</p>
{OP_SCRIPT}
"""


# ---------------------------------------------------------------------------------------------------- tool 3
RC_CSS = r"""
<style>
.pa-cardpv { margin: 0 0 12px; display: grid; gap: 12px; }
@container (min-width: 700px) { .pa-cardpv { grid-template-columns: 1fr 1fr; } }
.pa-face { box-sizing: border-box; padding: 12px 14px; border: 1px dashed #8a8a80; background: var(--pa-surface-2); font-size: 14px; line-height: 1.35; overflow-wrap: anywhere; }
.pa-face .pa-face-title { margin: 0 0 6px; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--pa-gold); font-weight: 700; }
.pa-face p { margin: 0 0 3px; }
.pa-face b { font-weight: 700; }
.pa-foldcard { display: grid; gap: 8px; margin: 0 0 12px; }
@container (min-width: 700px) { .pa-foldcard { grid-template-columns: 1fr 1fr; } }
@media print {
  .pa-cardpv { display: none !important; }
  .pa-printonly { display: block !important; }
  .pa-foldcard { display: grid !important; grid-template-columns: 1fr 1fr; width: 7in; height: 2.125in; margin: 0 0 .12in; border: 1px solid #000; box-sizing: border-box; break-inside: avoid; position: relative; }
  .pa-foldcard .pa-face { border: 0; border-right: 1px dashed #000; padding: .07in .1in; font-size: 7.5pt; line-height: 1.14; overflow: hidden; height: 2.125in; }
  .pa-foldcard .pa-face:last-child { border-right: 0; }
  .pa-foldcard .pa-face .pa-face-title { font-size: 7.5pt; margin: 0 0 2pt; letter-spacing: .06em; }
  .pa-foldcard .pa-face p { margin: 0 0 1pt; }
  .pa-printpage-note { display: block; font-size: 8pt; margin: 0 0 6pt; }
  .pa-card-mainhide { display: none !important; }
}
</style>
"""

RC_SCRIPT = r"""
<script>
{{inline-js:shelter_common.js}}
{{inline-js:reunion_card.js}}
(function () {
  var form = document.getElementById('rc'); if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  function today() { var d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  var KEYS = ['hhName', 'hhPhone', 'outName', 'outPhone', 'meet1', 'meet2', 'school', 'schoolPlan', 'pickup', 'careName', 'carePhone', 'access', 'reviewed'];
  function fields() { var f = {}; KEYS.forEach(function (k) { f[k] = $('rc-' + k).value; }); return f; }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function face(title, rows) {
    var d = el('div', 'pa-face'); d.appendChild(el('p', 'pa-face-title', title));
    if (!rows.length) d.appendChild(el('p', null, '(blank)'));
    rows.forEach(function (r) { var p = el('p'); p.appendChild(el('b', null, r.k + ': ')); p.appendChild(document.createTextNode(r.v)); d.appendChild(p); });
    return d;
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
  function render() {
    var minimal = $('rc-minimal').checked, m = rcModel(fields(), minimal);
    var pv = $('rc-preview'); clear(pv);
    pv.appendChild(face('Front: ' + (minimal ? 'minimal' : 'contacts'), m.front));
    pv.appendChild(face('Back: ' + (minimal ? 'minimal' : 'school and care'), m.back));
    var copies = Math.max(1, Math.min(4, Number($('rc-copies').value) || 1));
    var pr = $('rc-sheet'); clear(pr);
    pr.appendChild(el('p', 'pa-printpage-note', 'Cut out each card and fold it on the dotted line to wallet size. Keep the card with you. Review it each year.'));
    for (var i = 0; i < copies; i++) {
      var c = el('div', 'pa-foldcard'); c.appendChild(face('Emergency contacts', m.front)); c.appendChild(face(minimal ? 'Reviewed' : 'School and care', m.back)); pr.appendChild(c);
    }
    var w = rcWarnings(fields(), today()), box = $('rc-warn'); clear(box);
    if (w.length) { var ul = el('ul'); w.forEach(function (x) { ul.appendChild(el('li', null, x)); }); box.appendChild(ul); }
  }
  form.addEventListener('input', render); form.addEventListener('change', render);
  $('rc-live').hidden = false;
  $('rc-print').hidden = false; $('rc-print').addEventListener('click', function () { window.print(); });
  $('rc-reset').hidden = false; $('rc-reset').addEventListener('click', function () { form.reset(); render(); });
  render();
})();
</script>
"""


def card_fold(label: str) -> str:
    lines = lambda names: "".join(f"<p><b>{esc(n)}:</b> ________________________</p>" for n in names)
    return (f'<div class="pa-foldcard"><div class="pa-face"><p class="pa-face-title">Emergency contacts</p>'
            + lines(["Household", "Phone", "Out-of-area contact", "Out-of-area phone", "Meet first at", "If not, meet at"])
            + '</div><div class="pa-face"><p class="pa-face-title">School and care</p>'
            + lines(["School or childcare", "Reunification plan", "Pick-up reminder", "Caregiver", "Caregiver phone", "Communication needs", "Reviewed"])
            + "</div></div>")


def card_body() -> str:
    fl = lambda k, lab, kind, n, hint="": field(f"rc-{k}", lab, kind, n, "", hint)
    return f"""<section class="pa-act" aria-labelledby="act-h">
<h2 id="act-h">What to do now</h2>
<ol>
<li><strong>Choose an out-of-area contact</strong> and ask them first. Put their name and number on the card.{{{{cite:shelter-fcc-comms}}}}{{{{cite:shelter-ready-evacuation}}}}</li>
<li><strong>Pick a meeting place</strong> and an alternate, then fill in only what you are comfortable carrying.</li>
<li><strong>Use the minimal version if you are unsure.</strong> It prints only the out-of-area contact, a phone and the first meeting place.</li>
<li><strong>Print, cut and fold the card,</strong> keep it with you, and review it every year.{{{{cite:shelter-cdc-reunification}}}}</li>
</ol>
<p class="pa-act-note"><strong>In an emergency,</strong> call 911 for anything life-threatening, and use text messages rather than calls for everything else when networks are busy.{{{{cite:shelter-ready-tech}}}} <strong>Private by design:</strong> what you type stays on this page. It is not sent or saved. Closing the tab clears it.</p>
</section>
{CSS}{RC_CSS}
<div class="pa-alert pa-alert--stop pa-card-mainhide"><p class="pa-alert-title">A printed card can be lost</p>
<p>Anyone who finds it can read it. Do not put a child's full name, a home address, a government ID number, a medical diagnosis or a password on it. First names or nicknames and phone numbers are usually enough. If you are unsure, tick the minimal version, which leaves out the school, caregiver and communication details and refers to your written plan at home.</p></div>
{NOSCRIPT_NOTE % 'A blank fold-over card is shown below. Print it and fill it in by hand.'}
<h2 id="card">Your card</h2>
<form class="pa-sheet pa-card-mainhide" id="rc" onsubmit="return false" aria-describedby="rc-help">
<p id="rc-help">Every field is optional. Fields stop at a length that fits on the card.</p>
<fieldset><legend>Version</legend>
{check("rc-minimal", "Minimal version: only the out-of-area contact, a phone number, the first meeting place and the review date")}
<div><label for="rc-copies">Cards to print</label><select id="rc-copies"><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option></select><span class="pa-hint">Up to 4 fold-over cards fit on one letter page.</span></div>
</fieldset>
<fieldset><legend>Contacts and meeting places</legend>
<div class="pa-grid2">
{fl("hhName", "Household (first names or a family nickname)", "text", 24)}
{fl("hhPhone", "Household emergency phone", "tel", 24)}
{fl("outName", "Out-of-area contact", "text", 24)}
{fl("outPhone", "Out-of-area contact phone", "tel", 24)}
{fl("meet1", "Meet first at", "text", 32, "A place, not an address.")}
{fl("meet2", "If not possible, meet at", "text", 32)}
</div>
</fieldset>
<fieldset><legend>School, childcare and care (left off the minimal version)</legend>
<div class="pa-grid2">
{fl("school", "School or childcare (name only)", "text", 32)}
{fl("schoolPlan", "Reunification process (for example: wait for the school's notice)", "text", 44, "Ask your school how it works; Colorado's version is not everyone's.")}
{fl("pickup", "Authorized pick-up reminder", "text", 44, "For example: only people on the school's list; update the list each year.")}
{fl("careName", "Caregiver", "text", 24)}
{fl("carePhone", "Caregiver phone", "tel", 24)}
{fl("access", "Communication or access considerations", "text", 44, "For example: uses text, not calls.")}
</div>
</fieldset>
<fieldset><legend>Review</legend>
{fl("reviewed", "Date last reviewed", "date", 10)}
</fieldset>
<div class="pa-printbar pa-noprint">
<button type="button" class="pa-btn" id="rc-print" hidden>Print or save as PDF</button>
<button type="button" class="pa-btn pa-btn--ghost" id="rc-reset" hidden>Clear everything</button>
</div>
</form>
<div id="rc-warn" class="pa-out pa-noprint pa-card-mainhide" role="status" aria-live="polite" aria-label="Things to check"></div>
<div id="rc-live" hidden>
<h2 id="preview" class="pa-card-mainhide">Preview</h2>
<div id="rc-preview" class="pa-cardpv pa-card-mainhide" role="group" aria-label="Card preview"></div>
<div id="rc-sheet" class="pa-printonly pa-printsheet"></div>
</div>
<noscript><div class="pa-printsheet">{card_fold("blank")}</div></noscript>
<noscript><style>#rc, #rc-warn {{ display: none; }}</style></noscript>

<h2 id="how">How to use it well</h2>
<p>A communication card supports a household plan; it does not replace one. Ready.gov's planning page asks households to decide how they will contact each other and reconnect, to choose a meeting place that is familiar and easy to find, and to write the plan down and practice it.{{{{cite:shelter-ready-plan}}}} Its fillable communication plan collects family contacts, school and childcare pick-up plans, emergency contacts, meeting places and medical information, and says the information entered is not saved, stored or shared by any government agency.{{{{cite:shelter-ready-plan-form}}}} This card is the small part you carry.</p>
<p>The out-of-area contact comes first because networks jam. Ready.gov says text messages require less bandwidth and can be transmitted more reliably when many people are using their phones, and the FCC's older guide advises designating someone out of the area as a central contact.{{{{cite:shelter-ready-tech}}}}{{{{cite:shelter-fcc-comms}}}} The CDC suggests choosing a meeting spot, giving children emergency contact cards for their school bags, and helping older children memorize important names and numbers.{{{{cite:shelter-cdc-reunification}}}} If you and your children are separated in a chemical emergency, the CDC says not to go to them unless police, fire or other local officials say it is safe, because they may be sheltered where they are.{{{{cite:shelter-cdc-chemical-evac}}}}</p>
<h2 id="school">School and childcare reunification</h2>
<p>Schools and childcare centers have their own plans, and the card cannot know them. The CDC says to learn school safety procedures from the principal.{{{{cite:shelter-cdc-reunification}}}} Colorado's Office of School Safety, as one state's example, tells parents to wait for the school's notification, to bring photo ID, and not to rush to the school; other states and districts differ. California's Department of Education, for example, recommends that schools establish reunification locations and procedures and make sure parents are aware of them, in languages they understand.{{{{cite:shelter-co-oss-reunification}}}}{{{{cite:shelter-ca-cde-safety-plans}}}} The "reunification process" field is a reminder to ask, not an instruction.</p>
<p>If a child is missing after a disaster, the CDC lists NCMEC's 24-hour hotline, 1-800-THE-LOST, and NCMEC's own site shows the same number as 1-800-843-5678.{{{{cite:shelter-cdc-reunification}}}}{{{{cite:shelter-ncmec-hotline}}}} FEMA's fact sheet describes national reunification support, which is activated only in some Presidentially declared disasters, and FEMA marks it as archived content, so do not rely on it being available.{{{{cite:shelter-fema-reunification}}}}</p>
<p><span class="pa-tag pa-tag--ed">Editor's note</span> Custody arrangements, informal caregivers and who may collect a child are decided by your school's own rules and by law, neither of which the sources we read describe. List every adult your school has on file, keep the school's list current, and ask the school. We make no legal claims. A human safety review is required before this tool is public, and the box at the bottom of the page shows where that stands.</p>
<h2 id="print">Printing the card</h2>
<p>Choose "Save as PDF" or print on letter paper at 100 percent scale, with margins set to default or none. Each fold-over card is 7 by 2.125 inches, so it folds to 3.5 by 2.125 inches, a little larger than a credit card, and text is set at 7.5 points. Check the print preview to confirm nothing is cut off. Related guides: {{{{link:family-communication-plan|the family communication plan}}}} and {{{{link:shelter-or-evacuate|shelter in place or evacuate}}}}.</p>
{RC_SCRIPT}
"""


# ---------------------------------------------------------------------------------------------------- meta
def metas() -> dict[str, dict]:
    base = {"kind": "tool", "section": "field-tools", "track": "modern", "updated": UPDATED, "last_checked": UPDATED,
            "status": {"editorial": "drafted", "publish": "draft"}, "safety_review": {"state": "pending", "reviewer": None, "date": None}}
    fw = dict(base, n=102, slug="home-fire-escape-worksheet", title="Home fire escape plan worksheet", h1="Home fire escape plan worksheet",
              dek="A free, printable worksheet for two ways out of every room, a meeting place, who helps whom, alarm dates and practice. It runs in your browser, keeps nothing, and works without JavaScript.",
              description="A free printable home fire escape worksheet based on USFA and NFPA: two exits per room, meeting place, helpers, alarm and practice dates. Private; nothing is saved.",
              tags=["Worksheet", "Printable", "Runs locally"], recheck="If USFA or NFPA revise their escape-planning pages, or at the next quarterly source sweep.",
              related=["home-fire-escape-plan", "shelter-or-evacuate", "family-communication-plan"],
              source_use={
                  "usfa-fire-escape": "Two ways out of every room; map with all doors and windows; outside meeting place in front; practice with everyone.",
                  "shelter-nfpa-escape": "Helper and backup assignments; practice twice a year; escape-planning rules reflected in the worksheet's checks.",
                  "shelter-nfpa-smoke-alarms": "Monthly alarm test; replace the unit 10 years after manufacture.",
                  "shelter-usfa-escape-grid": "Fields of USFA's printable escape grid that the worksheet follows.",
                  "shelter-ready-home-fires": "Practice in the dark; wake-up checks; simulation guidance context.",
                  "shelter-nfpa-high-rise": "High-rise default: stairs; sealing in only when you cannot get out.",
                  "shelter-usfa-high-rise-handout": "High-rise default: leave by the stairs; cannot-get-out steps."})
    op = dict(base, n=103, slug="power-outage-planner", title="Power-outage readiness planner", h1="Power-outage readiness planner",
              dek="A checklist that adapts to your household and cites the agency page behind every item. It never sizes a generator, prescribes medical care or gives wiring or fuel advice. Free, private, works offline.",
              description="A free outage checklist that adapts to your household, drawn from CDC, FEMA, CPSC and Ready.gov. No generator sizing or medical advice. Private; nothing is saved.",
              tags=["Checklist", "Printable", "Runs locally"], recheck="If the CDC, FEMA, CPSC or Ready.gov revise their outage pages, or at the next quarterly source sweep.",
              related=["outage-heat-cold-generators", "shelter-or-evacuate", "family-communication-plan"],
              source_use={
                  "shelter-fema-power-outage-sheet": "Medical-device and medication planning with your doctor; replace refrigerated medicines wording; paper communication plan; supplies for several days; food, water advisory, and vehicle items.",
                  "shelter-ready-disabilities": "Priority restoration, treatment facilities, equipment backups and communication cards.",
                  "shelter-cpsc-co": "Generator placement and carbon monoxide symptom first response.",
                  "shelter-ready-evacuation": "Never connect a generator to the home's electrical system.",
                  "shelter-cdc-heat": "Fans below 90 F; air conditioning options; do not stop or change medicines without asking.",
                  "shelter-cdc-power-outage": "Flashlights instead of candles; food timings; stay with others if the home is damaged; no gas oven for heat.",
                  "shelter-cdc-winter-storm": "Cold-weather items; infants; pipes; heaters.",
                  "shelter-cdc-co-basics": "Carbon monoxide alarm placement wording.",
                  "shelter-ready-power-outages": "Flashlights, power bank, home phone, community location, medication storage question.",
                  "shelter-ready-heat": "Heat-illness signs and cooling items; pets.",
                  "shelter-ready-winter-weather": "Extra batteries for radios and flashlights; winter items.",
                  "shelter-ready-shelter": "Shelter text line; pets and shelters.",
                  "shelter-ready-tech": "Text rather than call; charging; low-power mode.",
                  "shelter-ready-plan-locations": "School plans; neighbors and shared buildings.",
                  "shelter-nws-nwr": "NOAA Weather Radio description and receiver requirement.",
                  "shelter-usda-fsis-emergencies": "Thermometer temperatures, grouping, full freezer, cooler and gel packs, up to 4 hours, never taste food, which perishables to discard after more than 4 hours without power.",
                  "fsis-power-failure": "Refrigerator about 4 hours unopened; full freezer about 48 hours (24 if half full)."})
    rc = dict(base, n=104, slug="reunification-plan", title="Family communication and reunification card", h1="Family communication and reunification card",
              dek="A compact fold-over wallet card for your out-of-area contact, meeting places and school pick-up reminders, with a minimal version for privacy. Free, local-only, prints at true size.",
              description="Make a free wallet-size family communication and reunification card with an out-of-area contact and meeting places. Minimal privacy version. Nothing is stored.",
              tags=["Wallet card", "Printable", "Runs locally"], recheck="If Ready.gov, the CDC or FEMA revise their reunification pages, and before each school year.",
              related=["family-communication-plan", "shelter-or-evacuate", "home-fire-escape-plan"],
              source_use={
                  "shelter-fcc-comms": "Designate an out-of-area person as a central contact (older, undated guide).",
                  "shelter-ready-evacuation": "Out-of-state contact in the family communications plan; update the meeting place.",
                  "shelter-cdc-reunification": "Meeting spot, children's contact cards, memorize numbers, learn school procedures, NCMEC hotline.",
                  "shelter-ready-tech": "Text messages use less bandwidth and are transmitted more reliably.",
                  "shelter-ready-plan": "Reconnect plan; familiar easy-to-find meeting place; document and practice.",
                  "shelter-ready-plan-form": "Fields of Ready.gov's fillable plan; not saved by any government agency.",
                  "shelter-co-oss-reunification": "One state's example of parent guidance; not universal.",
                  "shelter-ncmec-hotline": "NCMEC's own listing of its 24-hour hotline number.",
                  "shelter-fema-reunification": "National reunification support; archived content; Presidential declaration trigger.",
                  "shelter-cdc-chemical-evac": "Do not go to your children unless officials say it is safe; they may be sheltered where they are.",
                  "shelter-ca-cde-safety-plans": "California recommendation that schools set reunification locations and procedures and tell parents in languages they understand."})
    return {"home-fire-escape-worksheet": fw, "power-outage-planner": op, "reunification-plan": rc}


def render_all() -> dict[str, str]:
    files: dict[str, str] = {}
    bodies = {"home-fire-escape-worksheet": fire_body(), "power-outage-planner": outage_body(), "reunification-plan": card_body()}
    for slug, body in bodies.items():
        files[f"{slug}.body.html"] = body.replace("{{{{", "{{").replace("}}}}", "}}")
    for slug, meta in metas().items():
        files[f"{slug}.meta.json"] = json.dumps(meta, indent=2, ensure_ascii=False) + "\n"
    return files


def main() -> int:
    files = render_all()
    if "--check" in sys.argv:
        stale = [n for n, text in files.items() if not (OUT / n).exists() or (OUT / n).read_text(encoding="utf-8").replace("\r\n", "\n") != text]
        print("stale: " + ", ".join(stale) if stale else "generated tool pages are current")
        return 1 if stale else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for n, text in files.items():
        (OUT / n).write_text(text, encoding="utf-8", newline="\n")
    print("wrote", len(files), "files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
