/* Household emergency-water planner: pure calculation. No DOM, no storage, no network.
   Sourced inputs only: 1 gallon per person per day (CDC, Ready.gov) and the very-hot-weather doubling (Ready.gov).
   Pet and medical allowances are supplied by the user, because no verified official figure exists. */
function computeWaterPlan(input) {
  var clamp = function (v, lo, hi) {
    var n = Number(v);
    if (!isFinite(n)) n = 0;
    return Math.min(hi, Math.max(lo, n));
  };
  var people = Math.round(clamp(input.people, 0, 100));
  var days = Math.round(clamp(input.days, 0, 365));
  var veryHot = input.veryHot === true;
  var pets = Math.round(clamp(input.petCount, 0, 100));
  var petPerDay = clamp(input.petGalPerDay, 0, 100);
  var extraPerDay = clamp(input.extraGalPerDay, 0, 100);
  var stored = clamp(input.storedGallons, 0, 100000);

  var baseline = people * days * 1;
  var climateFactor = veryHot ? 2 : 1;
  var peopleWater = baseline * climateFactor;
  var petWater = pets * petPerDay * days;
  var extraWater = extraPerDay * days;
  var total = peopleWater + petWater + extraWater;
  var shortfall = Math.max(0, total - stored);
  var round1 = function (x) { return Math.round(x * 10) / 10; };

  return {
    people: people, days: days, veryHot: veryHot,
    baselineGallons: round1(baseline),
    peopleGallons: round1(peopleWater),
    petGallons: round1(petWater),
    extraGallons: round1(extraWater),
    totalGallons: round1(total),
    storedGallons: round1(stored),
    shortfallGallons: round1(shortfall),
    approxWeightLb: Math.round(total * 8.34),
    oneGallonJugs: Math.ceil(shortfall),
    fiveGallonContainers: Math.ceil(shortfall / 5)
  };
}

/* Six calendar months after a fill date (the CDC and Ready.gov replacement interval). Returns YYYY-MM-DD or null. */
function nextReplacementDate(isoDate) {
  var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoDate || "");
  if (!m) return null;
  var y = Number(m[1]), mo = Number(m[2]) - 1, d = Number(m[3]);
  var target = new Date(Date.UTC(y, mo + 6, 1));
  var last = new Date(Date.UTC(target.getUTCFullYear(), target.getUTCMonth() + 1, 0)).getUTCDate();
  target.setUTCDate(Math.min(d, last));
  if (isNaN(target.getTime())) return null;
  return target.toISOString().slice(0, 10);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { computeWaterPlan: computeWaterPlan, nextReplacementDate: nextReplacementDate };
}
