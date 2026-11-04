'use strict';
/* Apollo R123 Board chronology custody tests.
 * Run: node --test experience2/apollo-creator-bridge/test_r123_board_clock.cjs
 * Source-level regression; does not substitute for Chromium / axe.
 */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'landing-preview.html'),'utf8');
const BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
function railFrom(src) {
  const m=src.match(/<section id="event-sequence"[^>]*>([\s\S]*?)<\/section>/);
  assert.ok(m,'missing event sequence');
  return m[1];
}
function rowsFrom(src) {
  return [...railFrom(src).matchAll(/<li data-fv-board-time="([^"]+)" data-fv-event-status="([^"]+)"><time datetime="([^"]+)">([^<]+)<\/time>/g)]
    .map(m=>({id:m[1],kind:m[2],iso:m[3],label:m[4]}));
}
const rows=rowsFrom(html);
test('Five canonical source-backed chronology milestones exist in stable order',()=>{
  assert.deepEqual(rows.map(r=>r.id),['power-interruption','fire-report','intense-fire','rupture','telemetry-loss']);
});
test('Clock readings are parseable, UTC, and strictly increasing',()=>{
  assert.ok(rows.every(r=>/Z$/.test(r.iso)&&!Number.isNaN(Date.parse(r.iso))));
  for(let i=1;i<rows.length;i++)assert.ok(Date.parse(rows[i].iso)>Date.parse(rows[i-1].iso));
});
test('First verbal warning to approximate rupture is about 14.3 seconds',()=>{
  const seconds=(Date.parse(rows[3].iso)-Date.parse(rows[1].iso))/1000;
  assert.ok(seconds>=13.5 && seconds<=15);
  assert.equal(seconds,14.3);
});
test('No ignition certainty is implied by the power interruption',()=>{
  const s=railFrom(html);
  assert.match(s,/not proof of when or where ignition occurred/);
  assert.match(s,/could not conclusively identify a specific ignition source/);
});
test('The first verbal report is explicitly distinct from ignition',()=>{
  assert.match(railFrom(html),/not<\/em> the proven instant of ignition/);
});
test('Rupture and intensity readings are labeled approximate, not measured exact',()=>{
  assert.equal(rows[2].kind,'approximate');
  assert.equal(rows[3].kind,'approximate');
  assert.match(rows[3].label,/about/);
});
test('Electrical interruption and first fire report retain observed designations',()=>{
  assert.equal(rows[0].kind,'observed'); assert.equal(rows[1].kind,'observed');
});
test('Transmission cutoff is a bound and never presented as death instant',()=>{
  assert.equal(rows[4].kind,'bounded');
  assert.match(railFrom(html),/Do not treat this as a certified time of death/);
});
test('Board approximately 15 seconds and rounded approximately 14 seconds remain distinct',()=>{
  const r=railFrom(html);
  assert.match(r,/roughly <strong>14 seconds<\/strong>/);
  assert.match(r,/approximately <strong>15 seconds<\/strong>/);
  assert.match(r,/neither establishes the exact ignition time or the moment of death/);
});
test('Primary NASA Board link accompanies the clock rail',()=>{
  assert.ok(railFrom(html).includes('href="'+BOARD+'"'));
});
test('No data coordinates, map pins or event-to-photo causal graph in clock markup',()=>{
  assert.doesNotMatch(railFrom(html),/data-latitude|data-longitude|data-pin=|data-geo=|data-edge=/i);
});
test('Photo dates and Board fire chronology stay distinct sections',()=>{
  assert.match(html,/<section id="source-custody"/);
  assert.match(html,/<nav class="photo-provenance"/);
  assert.doesNotMatch(railFrom(html),/data-fv-photo-record=/);
});
test('Original Grok-to-page hook and single relevant free exercise remain unchanged',()=>{
  assert.match(html,/<h1>Fourteen seconds\. More than one failure\.<\/h1>/);
  assert.equal((html.match(/data-fv-primary-cta/g)||[]).length,1);
});
test('No mandatory registration, unapproved commerce or analytics introduced',()=>{
  assert.doesNotMatch(html,/<form\b|<iframe\b|<script\b[^>]*src=|https?:\/\/[^"']*payhip|sendBeacon\s*\(/i);
});
test('Board chronology is readable without script enhancement',()=>{
  assert.match(railFrom(html),/<ol class="timeline"[^>]*data-fv-board-clock-rail>/);
  assert.doesNotMatch(railFrom(html),/<ol[^>]+hidden\b|<li[^>]+hidden\b/);
});
test('Ordinary printing retains clock rail; student-only printing remains separate',()=>{
  assert.match(html,/@media print/);
  assert.match(html,/body\.fv-worksheet-only #main>:not\(#classroom-preview\)/);
  assert.doesNotMatch(html,/@media print\s*\{[^}]*#event-sequence\s*\{display\s*:\s*none/i);
});
test('Atlas R80 parity: exactly four known-day photographic checkpoints',()=>{
  const section=html.match(/<nav class="photo-provenance"[\\s\\S]*?<\\/nav>/);
  assert.ok(section,'photo provenance rail missing');
  const days=[...section[0].matchAll(/<li data-fv-photo-day="([^"]+)">/g)].map(m=>m[1]);
  assert.deepEqual(days,['1966-10-18','1967-01-03','1967-01-28','2017-01-24']);
});
test('Same-day 2017 retrospective sources 04 and 06 share one date',()=>{
  const day=html.match(/<li data-fv-photo-day="2017-01-24">([\\s\\S]*?)<\\/li>/);
  assert.ok(day);
  assert.match(day[1],/data-fv-photo-record="04"/);
  assert.match(day[1],/data-fv-photo-record="06"/);
  assert.match(day[1],/time datetime="2017-01-24"/);
});
test('January month-only portrait is not falsely ordered by day',()=>{
  const nav=html.match(/<nav class="photo-provenance"[\\s\\S]*?<\\/nav>/)[0];
  const days=nav.match(/<ol data-fv-photo-day-sequence>([\\s\\S]*?)<\\/ol>/)[1];
  assert.doesNotMatch(days,/data-fv-photo-record="01"/);
  assert.match(nav,/data-fv-photo-month-uncertain/);
  assert.match(nav,/time datetime="1967-01"/);
  assert.match(nav,/data-fv-photo-record="01"/);
});
test('Exactly six unique NASA source-custody targets survive navigation',()=>{
  const nav=html.match(/<nav class="photo-provenance"[\\s\\S]*?<\\/nav>/)[0];
  const ids=[...nav.matchAll(/data-fv-photo-record="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(ids.length,6);
  assert.equal(new Set(ids).size,6);
  for(const id of ids)assert.ok(html.includes('id="photo-source-'+id+'"'));
});
test('No unverified geographic assertions or thumbnails leak into photo chronology',()=>{
  const nav=html.match(/<nav class="photo-provenance"[\\s\\S]*?<\\/nav>/)[0];
  assert.doesNotMatch(nav,/<img|data-latitude|data-longitude|data-geo=|data-edge=/i);
});
test('Mutation guard: timing changes that break Board interval are detectable',()=>{
  const changed=html.replace('1967-01-27T23:31:04.700Z','1967-01-27T23:31:00Z');
  const rr=rowsFrom(changed);
  assert.ok((Date.parse(rr[3].iso)-Date.parse(rr[1].iso))/1000>15);
});
