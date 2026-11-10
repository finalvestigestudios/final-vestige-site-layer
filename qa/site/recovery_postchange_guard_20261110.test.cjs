"use strict";
const assert = require("node:assert/strict");
const { assess, utcMillis } = require("./recovery_postchange_guard_20261110.cjs");
const baseline = () => ({
  backup: { last_backup_when: "2026-11-10 03:06:04", last_attempt_status: "finished", last_attempt_failed: false },
  scan: { state: "idle", threats: [], ignored_threats: [], last_scan: { started_at: "2026-11-10T03:08:36+00:00", progress: 100, error: false } },
  changes: [{ group: "plugin", action: "activated", date: "2026-11-10T10:47:49Z" }],
  restore: { has_restore_record: false }
});
let n = 0;
function run(name, fn) { fn(); n++; }
run("new plugin after backup and scan => HOLD", () => {
  const x = assess(baseline()); assert.equal(x.status, "HOLD"); assert.equal(x.backup_after_change, false); assert.equal(x.scan_after_change, false);
});
run("both after latest change => covered but no restore proof", () => {
  const x = baseline(); x.backup.last_backup_when = "2026-11-10 11:00:00"; x.scan.last_scan.started_at = "2026-11-10T11:01:00Z";
  assert.equal(assess(x).status, "POST_CHANGE_EVIDENCE_PRESENT"); assert.equal(assess(x).restoration, "NO_RESTORE_RECORD");
});
run("backup after, scan before => HOLD", () => {
  const x=baseline(); x.backup.last_backup_when="2026-11-10 11:00:00"; assert.equal(assess(x).scan_after_change,false);
});
run("scan after, backup before => HOLD", () => {
  const x=baseline(); x.scan.last_scan.started_at="2026-11-10T11:00:00Z"; assert.equal(assess(x).backup_after_change,false);
});
run("finished is required", () => {
  const x=baseline(); x.backup.last_backup_when="2026-11-10 11:00:00"; x.scan.last_scan.started_at="2026-11-10T11:01:00Z";
  x.backup.last_attempt_status="running"; assert.equal(assess(x).status,"HOLD");
});
run("clean completed scan required", () => {
  const x=baseline(); x.backup.last_backup_when="2026-11-10 11:00:00"; x.scan.last_scan.started_at="2026-11-10T11:01:00Z";
  x.scan.last_scan.progress=70; assert.equal(assess(x).status,"HOLD");
});
run("missing timezone change => HOLD", () => {
  const x=baseline(); x.changes[0].date="2026-11-10 10:47:49"; assert.equal(assess(x).status,"HOLD");
});
run("change at equal timestamp is not proven covered", () => {
  const x=baseline(); x.changes[0].date="2026-11-10T03:06:04Z"; x.scan.last_scan.started_at="2026-11-10T11:00:00Z";
  assert.equal(assess(x).status,"HOLD");
});
run("newer change supersedes earlier passing one", () => {
  const x=baseline(); x.backup.last_backup_when="2026-11-10 11:00:00"; x.scan.last_scan.started_at="2026-11-10T11:01:00Z";
  x.changes.push({group:"plugin",action:"updated",date:"2026-11-10T11:02:00Z"}); assert.equal(assess(x).status,"HOLD");
});
run("no change evidence never PASS", () => {
  const x=baseline(); x.changes=[]; assert.equal(assess(x).status,"NO_CHANGE_EVIDENCE");
});
run("unqualified ISO date rejected", () => {
  assert.equal(utcMillis("2026-11-10T12:00:00"),null);
});
run("nonqualifying editorial change excluded", () => {
  const x=baseline(); x.changes=[{group:"post",action:"updated",date:"2026-11-10T10:47:49Z"}]; assert.equal(assess(x).status,"NO_CHANGE_EVIDENCE");
});
run("active threat after otherwise adequate post-change scan => HOLD", () => {
  const x=baseline(); x.backup.last_backup_when="2026-11-10 11:00:00"; x.scan.last_scan.started_at="2026-11-10T11:01:00Z";
  x.scan.threats=[{id:777,signature:"malware"}];
  assert.equal(assess(x).status,"HOLD"); assert.equal(assess(x).scan_after_change,false);
});
run("ignored unresolved threat => HOLD", () => {
  const x=baseline(); x.backup.last_backup_when="2026-11-10 11:00:00"; x.scan.last_scan.started_at="2026-11-10T11:01:00Z";
  x.scan.ignored_threats=[{id:778}];
  assert.equal(assess(x).status,"HOLD");
});
run("missing threats inventory => HOLD", () => {
  const x=baseline(); x.backup.last_backup_when="2026-11-10 11:00:00"; x.scan.last_scan.started_at="2026-11-10T11:01:00Z";
  delete x.scan.threats;
  assert.equal(assess(x).status,"HOLD");
});
run("malformed ignored threats inventory => HOLD", () => {
  const x=baseline(); x.backup.last_backup_when="2026-11-10 11:00:00"; x.scan.last_scan.started_at="2026-11-10T11:01:00Z";
  x.scan.ignored_threats={};
  assert.equal(assess(x).status,"HOLD");
});

run("impossible Feb 30 change cannot produce false green", () => {
  const x=baseline(); x.changes[0].date="2026-02-30T01:00:00Z";
  x.backup.last_backup_when="2026-03-03 02:00:00"; x.scan.last_scan.started_at="2026-03-03T03:00:00Z";
  assert.equal(assess(x).status,"HOLD");
});
run("impossible November 31 rejected", () => {
  assert.equal(utcMillis("2026-11-31T12:00:00Z"),null);
});
run("invalid post-change backup cannot pass", () => {
  const x=baseline(); x.changes[0].date="2026-02-28T01:00:00Z";
  x.backup.last_backup_when="2026-02-30 02:00:00"; x.scan.last_scan.started_at="2026-03-03T03:00:00Z";
  assert.equal(assess(x).status,"HOLD"); assert.equal(assess(x).backup_after_change,false);
});
run("invalid post-change scan cannot pass", () => {
  const x=baseline(); x.changes[0].date="2026-02-28T01:00:00Z";
  x.backup.last_backup_when="2026-03-03 02:00:00"; x.scan.last_scan.started_at="2026-02-30T03:00:00Z";
  assert.equal(assess(x).status,"HOLD"); assert.equal(assess(x).scan_after_change,false);
});
run("nonleap February 29 rejected", () => {
  assert.equal(utcMillis("2027-02-29T00:00:00Z"),null);
});
run("valid leap day and valid timezone offset accepted", () => {
  assert.equal(utcMillis("2028-02-29T23:00:00+01:00"),Date.parse("2028-02-29T23:00:00+01:00"));
});
run("impossible UTC offset rejected", () => {
  assert.equal(utcMillis("2026-11-10T12:00:00+14:30"),null);
});
console.log(n + "/23 offline tests passed");
