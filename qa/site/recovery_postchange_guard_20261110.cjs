"use strict";

/**
 * Offline evidence gate. It makes no network requests and never treats a
 * clean scan or successful backup before a production change as post-change
 * recovery evidence. It is NOT a restore test or vulnerability assessment.
 *
 * Input is a sanitized projection of read-only Jetpack/WP snapshots:
 * {
 *   backup: { last_backup_when: "YYYY-MM-DD HH:mm:ss",
 *             last_attempt_status: "finished", last_attempt_failed: false },
 *   scan: { state: "idle", threats: [], ignored_threats: [],
 *           last_scan: { started_at: ISO_WITH_OFFSET,
 *             progress: 100, error: false } },
 *   changes: [{ group: "plugin"|"theme"|"core",
 *               action: "installed"|"activated"|"updated"|...,
 *               date: ISO_WITH_OFFSET }],
 *   restore: { has_restore_record: false }
 * }
 * The naive WPCOM last_backup_when value is interpreted as UTC, matching
 * its read-only API convention. Never supply local clock time in this field.
 */
const GROUPS = new Set(["plugin", "theme", "core"]);
const ACTIONS = new Set(["installed", "activated", "updated", "autoupdated", "deactivated", "deleted", "upgraded"]);

function utcMillis(value, allowWpNaive = false) {
  if (typeof value !== "string") return null;
  let s = value.trim();
  if (allowWpNaive && /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(s)) {
    s = s.replace(" ", "T") + "Z";
  }
  // Date.parse normalizes impossible calendar days (Feb 30 -> Mar 2).
  // Reject impossible source evidence before comparing recovery timestamps.
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$/);
  if (!m) return null;
  const year = Number(m[1]), month = Number(m[2]), day = Number(m[3]);
  const hour = Number(m[4]), minute = Number(m[5]), second = Number(m[6]);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const monthDays = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (year < 1 || month < 1 || month > 12 || day < 1 ||
      day > monthDays[month - 1] || hour > 23 || minute > 59 || second > 59) return null;
  if (m[8] !== "Z") {
    const zoneHour = Number(m[8].slice(1, 3));
    const zoneMinute = Number(m[8].slice(4, 6));
    if (zoneHour > 14 || zoneMinute > 59 || (zoneHour === 14 && zoneMinute !== 0)) return null;
  }
  const t = Date.parse(s);
  return Number.isFinite(t) ? t : null;
}

function assess(snapshot) {
  const changes = Array.isArray(snapshot && snapshot.changes)
    ? snapshot.changes.filter(x => x && GROUPS.has(x.group) && ACTIONS.has(x.action))
    : [];
  const restoration = snapshot && snapshot.restore && snapshot.restore.has_restore_record === true
    ? "RECORD_EXISTS_NOT_REHEARSED_HERE" : "NO_RESTORE_RECORD";
  if (changes.length === 0) return {
    status: "NO_CHANGE_EVIDENCE", reasons: ["No qualifying recent change supplied; cannot establish coverage."],
    restoration
  };
  const dates = changes.map(c => utcMillis(c.date));
  if (dates.some(t => t === null)) return {
    status: "HOLD", reasons: ["Production-change date missing or not timezone-qualified."], restoration
  };
  const latest = Math.max(...dates);
  const backup = (snapshot && snapshot.backup) || {};
  const scan = (snapshot && snapshot.scan) || {};
  const lastScan = scan.last_scan || {};
  const backupAt = utcMillis(backup.last_backup_when, true);
  const scanAt = utcMillis(lastScan.started_at);
  const backupOk = backup.last_attempt_status === "finished" &&
    backup.last_attempt_failed === false && backupAt !== null && backupAt > latest;
  // An error-free scan with unresolved or suppressed threats is not clean.
  // Missing threat arrays are insufficient evidence, so fail closed.
  const threatsClear = Array.isArray(scan.threats) && scan.threats.length === 0 &&
    Array.isArray(scan.ignored_threats) && scan.ignored_threats.length === 0;
  const scanOk = scan.state === "idle" && lastScan.progress === 100 &&
    lastScan.error === false && scanAt !== null && scanAt > latest && threatsClear;
  const reasons = [];
  if (!backupOk) reasons.push("No independently verified completed backup starting strictly after latest production change.");
  if (!scanOk) reasons.push("No completed post-change scan with explicit empty active and ignored threat lists was independently verified.");
  return {
    status: backupOk && scanOk ? "POST_CHANGE_EVIDENCE_PRESENT" : "HOLD",
    latest_change_utc: new Date(latest).toISOString(),
    backup_after_change: backupOk, scan_after_change: scanOk,
    restoration, reasons
  };
}

module.exports = { assess, utcMillis };
