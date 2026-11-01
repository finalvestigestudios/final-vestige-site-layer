/* Family communication and reunification card: pure logic. No DOM, no storage, no network.
   Everything is optional. A minimal version leaves out school, caregiver and accessibility details so that a lost card
   reveals as little as possible. The card never asks for a child's full name, a home address, or any government ID number. */
var RC_LIMITS = { name: 24, phone: 24, place: 32, text: 44 };

function rcPhone(v) {
  return paCleanText(v, 60).replace(/[^0-9+()\-. x#*]/gi, "").slice(0, RC_LIMITS.phone);
}

function rcLooksLikeStreetAddress(v) {
  return /\b\d{1,6}\s+(?:[A-Za-z0-9.']+\s+){1,4}(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct|boulevard|blvd|way|place|pl|circle|cir|highway|hwy)\b\.?/i.test(String(v || ""));
}

function rcLooksLikeGovId(v) {
  return /\b\d{3}-\d{2}-\d{4}\b/.test(String(v || "")) || /\b(ssn|social security|passport|driver'?s? licen[cs]e)\b/i.test(String(v || ""));
}

function rcClean(f) {
  var d = f || {};
  var t = function (v, n) { return paCleanText(v, n); };
  return {
    hhName: t(d.hhName, RC_LIMITS.name), hhPhone: rcPhone(d.hhPhone),
    outName: t(d.outName, RC_LIMITS.name), outPhone: rcPhone(d.outPhone),
    meet1: t(d.meet1, RC_LIMITS.place), meet2: t(d.meet2, RC_LIMITS.place),
    school: t(d.school, RC_LIMITS.place), schoolPlan: t(d.schoolPlan, RC_LIMITS.text),
    pickup: t(d.pickup, RC_LIMITS.text),
    careName: t(d.careName, RC_LIMITS.name), carePhone: rcPhone(d.carePhone),
    access: t(d.access, RC_LIMITS.text),
    reviewed: paIsoOrNull(d.reviewed) ? d.reviewed : ""
  };
}

/* Returns the lines to print. minimal=true drops every field that identifies a school, a caregiver or a disability. */
function rcModel(fields, minimal) {
  var c = rcClean(fields);
  var row = function (k, v) { return v ? { k: k, v: v } : null; };
  var keep = function (a) { return a.filter(function (x) { return x; }); };
  var front = keep([
    row("Household", c.hhName), row("Phone", c.hhPhone),
    row("Out-of-area contact", c.outName), row("Out-of-area phone", c.outPhone),
    row("Meet first at", c.meet1), minimal ? null : row("If not, meet at", c.meet2)
  ]);
  var back = minimal
    ? keep([row("Reviewed", c.reviewed), { k: "Details", v: "Kept in our written plan at home." }])
    : keep([
      row("School or childcare", c.school), row("Reunification plan", c.schoolPlan), row("Pick-up reminder", c.pickup),
      row("Caregiver", c.careName), row("Caregiver phone", c.carePhone), row("Communication needs", c.access), row("Reviewed", c.reviewed)
    ]);
  return { front: front, back: back, minimal: !!minimal };
}

function rcWarnings(fields, today) {
  var c = rcClean(fields);
  var w = [];
  var all = Object.keys(c).map(function (k) { return c[k]; }).join(" | ");
  if (rcLooksLikeStreetAddress(all)) w.push("One entry looks like a street address. A found card could lead a stranger to your home. Leave addresses off unless you are sure.");
  if (rcLooksLikeGovId(all)) w.push("One entry looks like a government ID number. Do not put ID numbers, Social Security numbers or similar on a card.");
  [["Household phone", c.hhPhone], ["Out-of-area phone", c.outPhone], ["Caregiver phone", c.carePhone]].forEach(function (p) {
    var digits = p[1].replace(/\D/g, "");
    if (p[1] && (digits.length < 7 || digits.length > 15)) w.push(p[0] + " does not look like a complete phone number.");
  });
  if (!c.outName || !c.outPhone) w.push("No complete out-of-area contact yet. The FCC and Ready.gov both recommend one.");
  if (!c.meet1) w.push("No meeting place yet.");
  if (c.reviewed && paIsoOrNull(today)) {
    var due = paAddMonths(c.reviewed, 12);
    if (due && due <= today) w.push("This card was last reviewed more than a year ago. Check that every number is still right.");
  }
  return w;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { rcClean: rcClean, rcModel: rcModel, rcWarnings: rcWarnings, rcLooksLikeStreetAddress: rcLooksLikeStreetAddress, rcLooksLikeGovId: rcLooksLikeGovId, RC_LIMITS: RC_LIMITS };
}
