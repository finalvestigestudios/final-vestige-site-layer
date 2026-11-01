/* Home fire escape plan worksheet: pure logic. No DOM, no storage, no network.
   Sourced rules only: two ways out of every room (USFA, NFPA, Ready.gov); assign a helper and a backup for people who need
   assistance (NFPA); practice at least twice a year (NFPA, USFA, Ready.gov); replace a smoke alarm 10 years after its
   manufacturing date (NFPA). The checks below only point out blanks. They do not judge whether a plan is safe. */
var FW_LIMITS = { short: 60, medium: 120, long: 300 };

function fwNextPractice(lastIso) {
  return paAddMonths(lastIso, 6);
}

function fwSmokeAlarmReplaceBy(mfgIso) {
  return paAddYears(mfgIso, 10);
}

function fwClean(data) {
  var t = function (v, n) { return paCleanText(v, n); };
  var d = data || {};
  var list = function (a, max, fn) {
    var out = [];
    (Array.isArray(a) ? a : []).slice(0, max).forEach(function (x) { out.push(fn(x || {})); });
    return out;
  };
  return {
    fireDept: t(d.fireDept, FW_LIMITS.short),
    planDate: paIsoOrNull(d.planDate) ? d.planDate : "",
    inApartment: d.inApartment === true,
    rooms: list(d.rooms, 40, function (r) {
      return { room: t(r.room, FW_LIMITS.short), out1: t(r.out1, FW_LIMITS.short), out2: t(r.out2, FW_LIMITS.short), notes: t(r.notes, FW_LIMITS.medium) };
    }),
    meeting: { primary: t((d.meeting || {}).primary, FW_LIMITS.medium), alternate: t((d.meeting || {}).alternate, FW_LIMITS.medium) },
    people: list(d.people, 30, function (p) {
      return { name: t(p.name, FW_LIMITS.short), need: t(p.need, FW_LIMITS.short), helper: t(p.helper, FW_LIMITS.short), backup: t(p.backup, FW_LIMITS.short), notes: t(p.notes, FW_LIMITS.medium) };
    }),
    roles: { wake: t((d.roles || {}).wake, FW_LIMITS.medium), pets: t((d.roles || {}).pets, FW_LIMITS.medium), call: t((d.roles || {}).call, FW_LIMITS.medium), other: t((d.roles || {}).other, FW_LIMITS.medium) },
    alarms: {
      locations: t((d.alarms || {}).locations, FW_LIMITS.long),
      lastTest: paIsoOrNull((d.alarms || {}).lastTest) ? d.alarms.lastTest : "",
      mfgDate: paIsoOrNull((d.alarms || {}).mfgDate) ? d.alarms.mfgDate : "",
      coNote: t((d.alarms || {}).coNote, FW_LIMITS.medium)
    },
    practice: list(d.practice, 12, function (p) {
      return { date: paIsoOrNull(p.date) ? p.date : "", who: t(p.who, FW_LIMITS.medium), when: t(p.when, FW_LIMITS.short), learned: t(p.learned, FW_LIMITS.medium) };
    }),
    building: {
      manager: t((d.building || {}).manager, FW_LIMITS.medium), stairs: t((d.building || {}).stairs, FW_LIMITS.medium),
      alarmProcedure: t((d.building || {}).alarmProcedure, FW_LIMITS.long), nonStairPlan: t((d.building || {}).nonStairPlan, FW_LIMITS.long)
    }
  };
}

/* Returns [{level: "gap"|"note", text}]. today is an ISO date used only to judge how long ago the last practice was. */
function fwCheckPlan(data, today) {
  var d = fwClean(data);
  var out = [];
  var gap = function (s) { out.push({ level: "gap", text: s }); };
  var note = function (s) { out.push({ level: "note", text: s }); };
  var named = d.rooms.filter(function (r) { return r.room; });
  if (!named.length) note("No rooms listed yet. USFA and NFPA ask for two ways out of every room.");
  named.forEach(function (r) {
    if (!r.out1 || !r.out2) gap("\"" + r.room + "\": fewer than two ways out are written down.");
    else if (r.out1.toLowerCase() === r.out2.toLowerCase()) gap("\"" + r.room + "\": both ways out are the same. A second way should not depend on the first.");
  });
  if (!d.meeting.primary) gap("No outside meeting place yet. USFA and NFPA say to choose one in front of the home.");
  if (!d.fireDept) note("No fire department emergency number written down. NFPA says everyone should know it so anyone can call from outside.");
  var needHelp = d.people.filter(function (p) { return p.name || p.need; });
  needHelp.forEach(function (p) {
    var who = p.name || "A household member";
    if (!p.helper) gap(who + ": no helper assigned. NFPA says to assign someone to assist, and a backup.");
    else if (!p.backup) note(who + ": no backup helper. NFPA says to assign a backup in case the helper is not home.");
  });
  var last = d.practice.map(function (p) { return p.date; }).filter(Boolean).sort().pop();
  if (!last) note("No practice date recorded. NFPA, USFA and Ready.gov say to practice at least twice a year.");
  else if (paIsoOrNull(today)) {
    var due = fwNextPractice(last);
    if (due && due <= today) note("Your last recorded practice was " + last + ". Twice a year means another is due.");
  }
  if (!d.alarms.lastTest) note("No smoke alarm test date recorded. NFPA says to test every alarm once a month.");
  if (d.alarms.mfgDate) {
    var by = fwSmokeAlarmReplaceBy(d.alarms.mfgDate);
    if (by && paIsoOrNull(today) && by <= today) gap("A smoke alarm made on " + d.alarms.mfgDate + " is 10 years old or more. NFPA says to replace the whole unit 10 years after its manufacturing date.");
  }
  if (d.inApartment) {
    var mobility = d.people.some(function (p) { return /mobil|wheel|walker|stairs|cane|crutch/i.test(p.need + " " + p.notes); });
    if (mobility && !d.building.nonStairPlan) gap("Someone may not be able to use the stairs, and the building plan for them is blank. Ask your building manager and the fire department what the plan is.");
    if (!d.building.manager) note("No building manager contact. NFPA suggests meeting your landlord or manager to learn the building's alarms, sprinklers and evacuation plans.");
  }
  return out;
}

function fwText(data, today) {
  var d = fwClean(data);
  var L = [];
  var line = function (k, v) { L.push(k + ": " + (v || "")); };
  L.push("HOME FIRE ESCAPE PLAN (worksheet from the Final Vestige Preparedness Archive; not a substitute for your building's official plan or a fire department's advice)");
  line("Plan date", d.planDate); line("Fire department emergency number", d.fireDept); line("Apartment or condominium", d.inApartment ? "yes" : "no");
  L.push("", "TWO WAYS OUT OF EVERY ROOM");
  d.rooms.filter(function (r) { return r.room || r.out1 || r.out2; }).forEach(function (r) {
    L.push("- " + r.room + ": 1) " + r.out1 + " 2) " + r.out2 + (r.notes ? " (" + r.notes + ")" : ""));
  });
  L.push("", "OUTSIDE MEETING PLACE"); line("Primary", d.meeting.primary); line("Alternate", d.meeting.alternate);
  L.push("", "PEOPLE WHO NEED HELP, HELPER AND BACKUP");
  d.people.filter(function (p) { return p.name || p.need || p.helper; }).forEach(function (p) {
    L.push("- " + p.name + " (" + p.need + "): helper " + p.helper + ", backup " + p.backup + (p.notes ? " (" + p.notes + ")" : ""));
  });
  L.push("", "RESPONSIBILITIES"); line("Wakes children or others", d.roles.wake); line("Pets", d.roles.pets); line("Calls 911 from outside", d.roles.call); line("Other", d.roles.other);
  L.push("", "SMOKE ALARMS"); line("Locations", d.alarms.locations); line("Last tested", d.alarms.lastTest);
  line("Manufacture date", d.alarms.mfgDate); line("Replace by (10 years after manufacture)", fwSmokeAlarmReplaceBy(d.alarms.mfgDate) || ""); line("CO alarm note", d.alarms.coNote);
  L.push("", "PRACTICE LOG (at least twice a year)");
  d.practice.filter(function (p) { return p.date || p.who; }).forEach(function (p) { L.push("- " + p.date + " " + p.when + ": " + p.who + (p.learned ? " | learned: " + p.learned : "")); });
  var last = d.practice.map(function (p) { return p.date; }).filter(Boolean).sort().pop();
  if (last) line("Next practice due about", fwNextPractice(last) || "");
  if (d.inApartment) {
    L.push("", "BUILDING-SPECIFIC"); line("Building manager", d.building.manager); line("Exit stairs", d.building.stairs);
    line("Alarm and announcement procedure", d.building.alarmProcedure); line("Plan for anyone who cannot use the stairs", d.building.nonStairPlan);
  }
  var checks = fwCheckPlan(d, today);
  if (checks.length) { L.push("", "BLANKS TO FILL"); checks.forEach(function (c) { L.push("- " + c.text); }); }
  return L.join("\n");
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { fwNextPractice: fwNextPractice, fwSmokeAlarmReplaceBy: fwSmokeAlarmReplaceBy, fwClean: fwClean, fwCheckPlan: fwCheckPlan, fwText: fwText };
}
