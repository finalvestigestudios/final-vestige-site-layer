'use strict';
// Offline snapshot audit only. It cannot run a scan or prove that code is unsafe.
const EXECUTABLE_CHANGES = new Set([
  'plugin__installed', 'plugin__activated', 'plugin__updated', 'plugin__deleted',
  'plugin__deactivated', 'theme__activated', 'theme__updated', 'theme__deleted',
  'core__updated'
]);
function parseUtc(s) {
  if (typeof s !== 'string') return null;
  if (/^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$/.test(s)) s = s.replace(' ', 'T') + 'Z';
  if (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(s)) return null;
  const ms = Date.parse(s);
  return Number.isFinite(ms) ? ms : null;
}
function assess(snapshot, {asOf} = {}) {
  if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)) throw new TypeError('Snapshot object required');
  const now = parseUtc(asOf || new Date().toISOString());
  if (now === null) throw new TypeError('Explicit timezone required for asOf');
  const findings = [];
  const add = (code, level, detail) => findings.push({code, level, detail});
  const scan = (snapshot.scan || {}).last_scan;
  let scanEnd = null;
  if (!scan || typeof scan !== 'object') add('SCAN_UNAVAILABLE', 'UNKNOWN', 'No last completed security scan record');
  else if (scan.error !== false) add('SCAN_STATUS_UNCONFIRMED', 'UNKNOWN', 'Scan error flag missing or not false');
  else {
    const start = parseUtc(scan.started_at);
    const seconds = scan.duration_seconds;
    if (start === null || !Number.isFinite(seconds) || seconds < 0 || seconds > 86400)
      add('SCAN_TIME_UNCONFIRMED', 'UNKNOWN', 'Start or duration invalid');
    else {
      scanEnd = start + seconds * 1000;
      if (scanEnd > now) add('FUTURE_SCAN', 'UNKNOWN', 'Scan completion is after asOf');
    }
  }
  if (!Array.isArray(snapshot.activities)) add('ACTIVITY_UNAVAILABLE', 'UNKNOWN', 'Activity snapshot absent');
  const later = [];
  for (const e of (Array.isArray(snapshot.activities) ? snapshot.activities : [])) {
    if (!e || !EXECUTABLE_CHANGES.has(e.name)) continue;
    const time = parseUtc(e.date);
    if (time === null || time > now) {
      add('CODE_ACTIVITY_TIME_UNCONFIRMED', 'UNKNOWN', String(e.name));
    } else if (scanEnd !== null && scanEnd <= now && time > scanEnd) {
      later.push({action: e.name, at: new Date(time).toISOString()});
    }
  }
  later.sort((a, b) => b.at.localeCompare(a.at));
  if (later.length) add('CODE_CHANGED_AFTER_SCAN', 'REVIEW', later.length + ' code changes after latest reported scan');
  const status = findings.some(f => f.level === 'UNKNOWN') ? 'UNKNOWN' : later.length ? 'REVIEW' : 'NO_ALERTS_IN_SNAPSHOT';
  return {status, scan_completed_at: scanEnd === null || scanEnd > now ? null : new Date(scanEnd).toISOString(), code_changes_after_scan: later, findings};
}
module.exports = {assess, parseUtc};
if (require.main === module) {
  const fs = require('node:fs');
  try {
    if (!process.argv[2]) throw new Error('Usage: node guard.cjs SANITIZED_SNAPSHOT.json [--as-of ISO_TIMESTAMP]');
    const i = process.argv.indexOf('--as-of');
    const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    const result = assess(data, {asOf: i < 0 ? undefined : process.argv[i + 1]});
    console.log(JSON.stringify(result, null, 2));
    if (result.status === 'UNKNOWN') process.exitCode = 2;
    else if (result.status === 'REVIEW') process.exitCode = 1;
  } catch (e) { console.error(e.message); process.exitCode = 2; }
}
