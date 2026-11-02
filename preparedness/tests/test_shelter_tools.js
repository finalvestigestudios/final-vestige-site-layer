// Run with: node preparedness/tests/test_shelter_tools.js   (also invoked from the Python suite)
const assert = require("assert");
Object.assign(global, require("../tools/shelter_common.js"));
const fw = require("../tools/fire_worksheet.js");
const og = require("../tools/outage_items.js");
const rc = require("../tools/reunion_card.js");

// ---------- common helpers ----------
assert.strictEqual(paCleanText("  a\u0000b ‮ c\n\td ", 50), "ab c d");
assert.strictEqual(paCleanText("x".repeat(500), 10).length, 10);
assert.strictEqual(paCleanText(null, 10), "");
assert.strictEqual(paAddMonths("2026-08-31", 6), "2027-02-28");
assert.strictEqual(paAddMonths("2027-08-31", 6), "2028-02-29");
assert.strictEqual(paAddMonths("2026-12-15", 6), "2027-06-15");
assert.strictEqual(paAddMonths("2026-02-30", 6), null);      // impossible date
assert.strictEqual(paAddMonths("garbage", 6), null);
assert.strictEqual(paAddMonths("2026-01-01", 1e9), null);
assert.strictEqual(paAddYears("2016-03-15", 10), "2026-03-15");
assert.strictEqual(paAddYears("2016-02-29", 10), "2026-02-28");

// ---------- fire worksheet ----------
assert.strictEqual(fw.fwNextPractice("2026-11-01"), "2027-05-01");          // twice a year
assert.strictEqual(fw.fwSmokeAlarmReplaceBy("2020-06-10"), "2030-06-10");   // 10 years after manufacture
const messages = (d, today) => fw.fwCheckPlan(d, today).map(x => x.text).join("\n");
assert.match(messages({}, "2026-11-01"), /No rooms listed/);
assert.match(messages({}, "2026-11-01"), /No outside meeting place/);
assert.match(messages({ rooms: [{ room: "Bedroom", out1: "door" }] }, "2026-11-01"), /"Bedroom": fewer than two ways out/);
assert.match(messages({ rooms: [{ room: "Bedroom", out1: "Window", out2: "window" }] }, "2026-11-01"), /both ways out are the same/);
assert.doesNotMatch(messages({ rooms: [{ room: "Bedroom", out1: "Door", out2: "Window" }], meeting: { primary: "mailbox" } }, "2026-11-01"), /Bedroom/);
assert.match(messages({ people: [{ name: "Grandma", need: "walker" }] }, "2026-11-01"), /Grandma: no helper assigned/);
assert.match(messages({ people: [{ name: "Grandma", need: "walker", helper: "Sam" }] }, "2026-11-01"), /no backup helper/);
assert.doesNotMatch(messages({ people: [{ name: "Grandma", need: "walker", helper: "Sam", backup: "Lee" }] }, "2026-11-01"), /Grandma/);
assert.match(messages({ practice: [{ date: "2026-01-10" }] }, "2026-11-01"), /another is due/);
assert.doesNotMatch(messages({ practice: [{ date: "2026-09-10" }] }, "2026-11-01"), /another is due/);
assert.match(messages({ alarms: { mfgDate: "2015-01-01" } }, "2026-11-01"), /10 years old or more/);
assert.doesNotMatch(messages({ alarms: { mfgDate: "2024-01-01" } }, "2026-11-01"), /10 years old/);
assert.match(messages({ inApartment: true, people: [{ name: "Ana", need: "wheelchair user", helper: "x", backup: "y" }] }, "2026-11-01"), /building plan for them is blank/);
assert.doesNotMatch(messages({ inApartment: false, people: [{ name: "Ana", need: "wheelchair user", helper: "x", backup: "y" }] }, "2026-11-01"), /building plan/);
// text export is sanitised and bounded; hostile markup stays inert text
const hostile = { fireDept: "<img src=x onerror=alert(1)>", rooms: [{ room: "<script>alert(1)</script>", out1: "a", out2: "b" }], meeting: { primary: "x".repeat(5000) } };
const cleaned = fw.fwClean(hostile);
assert.ok(cleaned.fireDept.length <= 60 && cleaned.meeting.primary.length <= 120);
assert.ok(fw.fwText(hostile, "2026-11-01").length < 3000);
assert.ok(fw.fwText({}, "2026-11-01").includes("not a substitute for your building's official plan"));
// junk shapes do not throw
fw.fwClean(null); fw.fwClean({ rooms: "nope", people: 7, practice: { a: 1 } }); fw.fwCheckPlan(undefined, "bad");
assert.strictEqual(fw.fwClean({ rooms: new Array(500).fill({ room: "r" }) }).rooms.length, 40);

// ---------- outage planner ----------
const ids = og.OUTAGE_ITEMS.map(i => i.id);
assert.strictEqual(new Set(ids).size, ids.length, "item ids must be unique");
og.OUTAGE_ITEMS.forEach(i => {
  assert.ok(og.OUTAGE_SRC[i.src], i.id + " has an unknown source key");
  assert.ok(og.OUTAGE_GROUPS.some(g => g.id === i.g), i.id + " has an unknown group");
  (i.when || []).forEach(k => assert.ok(og.OUTAGE_QUESTIONS.some(q => q.key === k), i.id + " depends on unknown answer " + k));
});
const flat = a => og.buildOutageChecklist(a).groups.flatMap(g => g.items.map(i => i.id));
const baseline = flat({});
["L1", "C5", "F1", "S1", "G0", "W9"].forEach(x => assert.ok(baseline.includes(x), "baseline should include " + x));
["M3", "M4", "G1", "W1", "W5", "K1", "A1"].forEach(x => assert.ok(!baseline.includes(x), "baseline must not include " + x));
assert.ok(flat({ medDevice: true }).includes("M4") && flat({ medDevice: true }).includes("M5") && flat({ medDevice: true }).includes("M9"));
assert.ok(flat({ coldMeds: true }).includes("M3") && !flat({ coldMeds: true }).includes("M4"));
assert.ok(flat({ generator: true }).includes("G1") && flat({ generator: true }).includes("G3") && flat({ generator: true }).includes("G4"));
assert.ok(flat({ heat: true }).includes("W1") && !flat({ heat: true }).includes("W5"));
assert.ok(flat({ cold: true }).includes("W5") && flat({ cold: true }).includes("G5"));
assert.ok(flat({ baby: true }).includes("K1") && flat({ pets: true }).includes("K4"));
assert.ok(flat({ apartment: true }).includes("A4"));
assert.ok(flat({ mobility: true }).includes("M8") && flat({ mobility: true }).includes("A1"));
assert.deepStrictEqual(flat({ medDevice: "yes" }), baseline, "only boolean true selects an item");
assert.strictEqual(flat(null).length, baseline.length);
// every question changes the list
og.OUTAGE_QUESTIONS.forEach(q => { const a = {}; a[q.key] = true; assert.ok(flat(a).length > baseline.length || q.key === "x", q.key + " should add items"); });
// safety constraints on wording: no sizing, no fuel quantities, no wiring procedure, no blanket medication discard/stop
const everything = og.OUTAGE_ITEMS.filter(i => !i.disclaimer);
everything.forEach(i => {
  assert.doesNotMatch(i.text, /\b(watts?|kw|kilowatts?|amps?|btu|gallons?|liters?|litres?|sizing|transfer switch|interlock|backfeed)\b/i, i.id + " must not give sizing, fuel or wiring detail");
});
og.OUTAGE_ITEMS.filter(i => i.g === "meds").forEach(i => {
  assert.doesNotMatch(i.text, /\b(throw (it )?(away|out)|discard|stop taking|skip a dose|skip doses)\b/i, i.id + " must not tell people to discard or stop medicine");
});
assert.match(og.OUTAGE_ITEMS.find(i => i.id === "M3").text, /call your pharmacist or doctor/i);
assert.match(og.OUTAGE_ITEMS.find(i => i.id === "M3").text, /Do not stop or change a medicine on your own/);
assert.match(og.OUTAGE_ITEMS.find(i => i.id === "G1").text, /minimum, not a guarantee/);
assert.match(og.OUTAGE_ITEMS.find(i => i.id === "G3").text, /Never connect a generator to your home's electrical system/);
og.OUTAGE_ITEMS.filter(i => i.src === "editor").forEach(i => assert.ok(!/\d+\s*(feet|hours|minutes)/.test(i.text), "editor items carry no numbers: " + i.id));
// contacts adapt; text export marks checked items and cleans contact values
const cl = og.buildOutageChecklist({ medDevice: true, apartment: true });
assert.ok(cl.contacts.some(c => c.key === "supplier") && cl.contacts.some(c => c.key === "building"));
assert.ok(!og.buildOutageChecklist({}).contacts.some(c => c.key === "supplier"));
const txt = og.outageText({ generator: true }, ["L1"], { utility: "555-0100\u0000<b>", outside: "x".repeat(1000) });
assert.ok(txt.includes("[x] Keep a flashlight") && txt.includes("[ ] "));
assert.ok(txt.includes("Not medical advice"));
assert.ok(!txt.includes("\u0000") && txt.length < 20000);

// ---------- reunification card ----------
assert.ok(!/[<>a-df-wyz]/i.test(rc.rcClean({ hhPhone: "(555) 010-0100 ext 4 <script>" }).hhPhone));
assert.ok(/^[0-9+()\-. x#*]*$/i.test(rc.rcClean({ hhPhone: "(555) 010-0100 <b>ext</b>" }).hhPhone));
assert.ok(rc.rcLooksLikeStreetAddress("123 Maple Street"));
assert.ok(rc.rcLooksLikeStreetAddress("4500 N. Oak Ave"));
assert.ok(!rc.rcLooksLikeStreetAddress("Library on Main"));
assert.ok(rc.rcLooksLikeGovId("123-45-6789") && rc.rcLooksLikeGovId("my passport 12345"));
const full = { hhName: "The Rivera family", hhPhone: "555-0100", outName: "Aunt Rosa", outPhone: "555-0199", meet1: "Mailbox out front", meet2: "Library", school: "Lincoln Elementary", schoolPlan: "Follow school notice", pickup: "Only people on the school list", careName: "Mr. Lee", carePhone: "555-0150", access: "Uses text, not calls", reviewed: "2026-11-01" };
const full1 = rc.rcModel(full, false), min1 = rc.rcModel(full, true);
assert.ok(full1.back.some(r => r.v === "Lincoln Elementary") && full1.back.some(r => r.v === "Mr. Lee") && full1.back.some(r => r.v === "Uses text, not calls"));
const minText = JSON.stringify(min1);
["Lincoln", "Mr. Lee", "555-0150", "Uses text", "Library", "school list"].forEach(s => assert.ok(!minText.includes(s), "minimal card must omit " + s));
assert.ok(minText.includes("Aunt Rosa") && minText.includes("Mailbox out front"));
assert.strictEqual(rc.rcModel({}, false).front.length, 0);
assert.ok(rc.rcWarnings({ hhName: "x", meet1: "123 Maple Street" }, "2026-11-01").some(w => /street address/.test(w)));
assert.ok(rc.rcWarnings({ pickup: "SSN 123-45-6789" }, "2026-11-01").some(w => /ID number/.test(w)));
assert.ok(rc.rcWarnings({ hhPhone: "123" }, "2026-11-01").some(w => /complete phone number/.test(w)));
assert.ok(rc.rcWarnings({ reviewed: "2025-01-01" }, "2026-11-01").some(w => /more than a year/.test(w)));
assert.ok(rc.rcWarnings({}, "2026-11-01").some(w => /out-of-area/.test(w)));
Object.values(rc.rcClean({ hhName: "x".repeat(900), meet1: "y".repeat(900), pickup: "z".repeat(900) })).forEach(v => assert.ok(String(v).length <= 64));
rc.rcClean(null); rc.rcModel(undefined, true); rc.rcWarnings(null, null);

console.log("shelter tools: all assertions passed");
