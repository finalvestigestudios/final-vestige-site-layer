// Run with: node preparedness/tests/test_water_planner.js   (also invoked from the Python suite)
const assert = require("assert");
const { computeWaterPlan, nextReplacementDate } = require("../tools/water_planner.js");

// CDC/Ready.gov baseline: 1 gallon per person per day
let r = computeWaterPlan({ people: 4, days: 3 });
assert.strictEqual(r.baselineGallons, 12); assert.strictEqual(r.totalGallons, 12); assert.strictEqual(r.shortfallGallons, 12);
r = computeWaterPlan({ people: 4, days: 14 });
assert.strictEqual(r.totalGallons, 56);
// matches the table in the water-math guide
[[1,3,3],[1,14,14],[2,3,6],[2,14,28],[3,3,9],[3,14,42],[5,3,15],[5,14,70],[6,3,18],[6,14,84]].forEach(([p,d,g]) => assert.strictEqual(computeWaterPlan({people:p,days:d}).totalGallons, g));
// very hot doubles people only (Ready.gov), not user allowances
r = computeWaterPlan({ people: 4, days: 3, veryHot: true });
assert.strictEqual(r.totalGallons, 24);
r = computeWaterPlan({ people: 4, days: 3, veryHot: true, petCount: 1, petGalPerDay: 0.5, extraGalPerDay: 1 });
assert.strictEqual(r.peopleGallons, 24); assert.strictEqual(r.petGallons, 1.5); assert.strictEqual(r.extraGallons, 3); assert.strictEqual(r.totalGallons, 28.5);
// pets contribute nothing unless the user supplies a figure
assert.strictEqual(computeWaterPlan({ people: 2, days: 3, petCount: 3 }).petGallons, 0);
// shortfall never negative; stored subtracts
r = computeWaterPlan({ people: 2, days: 3, storedGallons: 10 });
assert.strictEqual(r.shortfallGallons, 0); assert.strictEqual(r.oneGallonJugs, 0);
r = computeWaterPlan({ people: 2, days: 14, storedGallons: 10 });
assert.strictEqual(r.shortfallGallons, 18); assert.strictEqual(r.fiveGallonContainers, 4); assert.strictEqual(r.oneGallonJugs, 18);
// hostile / junk input is clamped, never NaN or negative
r = computeWaterPlan({ people: -5, days: "abc", veryHot: "yes", petCount: NaN, storedGallons: -3 });
assert.strictEqual(r.totalGallons, 0); assert.strictEqual(r.veryHot, false);
r = computeWaterPlan({ people: 1e9, days: 1e9 });
assert.ok(isFinite(r.totalGallons) && r.totalGallons <= 100 * 365);
// weight
assert.strictEqual(computeWaterPlan({ people: 4, days: 14 }).approxWeightLb, Math.round(56 * 8.34));
// six-month replacement date
assert.strictEqual(nextReplacementDate("2026-10-29"), "2027-04-29");
assert.strictEqual(nextReplacementDate("2026-08-31"), "2027-02-28");   // end-of-month clamp
assert.strictEqual(nextReplacementDate("2027-08-31"), "2028-02-29");   // leap year
assert.strictEqual(nextReplacementDate("2026-12-15"), "2027-06-15");   // year rollover
assert.strictEqual(nextReplacementDate(""), null); assert.strictEqual(nextReplacementDate("not-a-date"), null);
console.log("water planner: all assertions passed");
