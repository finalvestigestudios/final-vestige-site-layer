// Unit tests for the Start Here tools' pure logic.  Run: node preparedness/tests/test_start_tools.js
const assert = require("assert");
const pb = require("../tools/plan_builder.js");
const kb = require("../tools/kit_planner.js");

// ---- text hygiene and escaping ----
assert.strictEqual(pb.pbText("  a\u0000b\n\tc  ", 10), "a b c");
assert.strictEqual(pb.pbText("x".repeat(500), 50).length, 50);
assert.strictEqual(pb.pbText(null, 10), ""); assert.strictEqual(pb.pbText(undefined, 10), "");
assert.strictEqual(pb.pbEsc(`<img src=x onerror="alert(1)">&'\``), "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;&amp;&#39;&#96;");

// ---- phone validation ----
assert.strictEqual(pb.pbPhone("").ok, true);
assert.strictEqual(pb.pbPhone("(555) 123-4567").ok, true);
assert.strictEqual(pb.pbPhone("+44 20 7946 0958").ok, true);
assert.strictEqual(pb.pbPhone("911").ok, true);
assert.strictEqual(pb.pbPhone("call mom").ok, false);
assert.strictEqual(pb.pbPhone("<script>").ok, false);
assert.strictEqual(pb.pbPhone("12").ok, false);
assert.strictEqual(pb.pbPhone("1".repeat(25)).ok, false);

// ---- date validation ----
assert.strictEqual(pb.pbDate("2026-11-01").ok, true);
assert.strictEqual(pb.pbDate("").ok, true);
assert.strictEqual(pb.pbDate("2026-02-30").ok, false);
assert.strictEqual(pb.pbDate("11/01/2026").ok, false);
assert.strictEqual(pb.pbDate("2026-13-01").ok, false);

// ---- practice dates: month arithmetic clamps the day, crosses year ends ----
assert.deepStrictEqual(pb.pbPracticeDates("2026-11-30"), { drill: "2027-02-28", kit: "2027-05-30", review: "2027-11-30" });
assert.strictEqual(pb.pbAddMonths("2024-08-31", 6), "2025-02-28");
assert.strictEqual(pb.pbAddMonths("2024-08-31", 18), "2026-02-28");
assert.strictEqual(pb.pbAddMonths("nonsense", 3), "");

// ---- normalization: caps, enums, junk ----
let n = pb.pbNormalize({ members: Array.from({ length: 40 }, (_, i) => ({ name: "P" + i, age: "alien", needs: ["mobility", "hax", "mobility"] })), pets: "no", contacts: [null, 5, { phone: "bad" }] });
assert.strictEqual(n.members.length, pb.PB_LIMITS.members);
assert.strictEqual(n.members[0].age, "adult");
assert.deepStrictEqual(n.members[0].needs, ["mobility"]);
assert.deepStrictEqual(n.pets, []);
assert.strictEqual(n.contacts.length, 3);
assert.strictEqual(n.building.elevator, "unknown");
assert.deepStrictEqual(pb.pbNormalize(null).members, []);
assert.deepStrictEqual(pb.pbNormalize("junk").contacts, []);
assert.strictEqual(pb.pbNormalize({ practice: { drill: "2026-02-31" } }).practice.drill, "");

// ---- validation points at the right fields ----
let errs = pb.pbValidate({ outOfArea: { phone1: "abc" }, contacts: [{ phone: "555-1111" }, { phone: "x!" }], practice: { review: "soon" } });
assert.deepStrictEqual(errs.map(e => e.path).sort(), ["contacts.1.phone", "outOfArea.phone1", "practice.review"]);
assert.deepStrictEqual(pb.pbValidate({}), []);

// ---- outputs never contain unescaped HTML from user input ----
const hostile = { members: [{ name: "<b>Eve</b>", age: "child", needs: ["mobility"], cardNote: "<script>alert(1)</script>" }], outOfArea: { name: "\"><img src=x onerror=alert(1)>", phone1: "555-123-4567" },
  contacts: [{ name: "<i>x</i>", relation: "'; DROP TABLE", phone: "555-0000" }], meeting: { near: "<svg onload=alert(1)>" }, pets: [{ name: "<u>Rex</u>", kind: "dog", microchip: "yes" }], meds: { note: "<iframe src=//evil>" } };
const html = pb.pbPlanHtml(hostile) + pb.pbCardsHtml(hostile);
assert.ok(!/<(script|img|svg|iframe|b|i|u)\b/i.test(html.replace(/<(h2|h3|ul|li|p|em|small|br|div|span|\/[a-z0-9]+)[^>]*>/gi, "")), "hostile markup must come out escaped");
assert.ok(html.includes("&lt;script&gt;"));
// plain text export keeps user text literal and never contains HTML tags we generated
const txt = pb.pbToText(hostile);
assert.ok(txt.includes("<b>Eve</b>") && !/<h2|<ul|<li/.test(txt));

// ---- required content: privacy line, reminders, medicine items are questions not instructions ----
assert.ok(txt.includes("Kept on this device only"));
assert.ok(pb.PB_REMINDERS.some(r => /911/.test(r)) && pb.PB_REMINDERS.some(r => /local officials/i.test(r)));
const list = pb.pbToText({});
assert.ok(/THINGS TO ASK \(this is a to-do list, not advice\)/.test(list));
assert.ok(!/b(discard|throw away|stop taking|ration|rationing)b/i.test(list), "plan text must not give medicine instructions");

// ---- wallet cards: one per member, never include needs or notes beyond the optional card note ----
let cards = pb.pbWalletCards({ members: [{ name: "A", needs: ["medication"], cardNote: "Speaks Spanish" }, { name: "B" }], outOfArea: { name: "Sam", phone1: "555-123-4567" }, meeting: { near: "Oak St", far: "Library" } });
assert.strictEqual(cards.length, 2);
assert.ok(!JSON.stringify(cards).includes("medication"));
assert.strictEqual(cards[0].note, "Speaks Spanish");
assert.strictEqual(pb.pbWalletCards({}).length, 1, "a blank plan still yields one blank card");

// ---- kit planner ----
const groups = [{ id: "core", scenario: "" }, { id: "children", scenario: "children" }, { id: "pets", scenario: "pets" }];
assert.deepStrictEqual(kb.kbVisibleGroups(groups, ["adults"]).map(g => g.visible), [true, false, false]);
assert.deepStrictEqual(kb.kbVisibleGroups(groups, ["children", "pets"]).map(g => g.visible), [true, true, true]);
assert.deepStrictEqual(kb.kbVisibleGroups(groups, null).map(g => g.visible), [true, false, false]);
assert.deepStrictEqual(kb.kbVisibleGroups(null, []), []);
const items = [{ visible: true, checked: true }, { visible: true, checked: false }, { visible: false, checked: true }, null, { checked: true }];
assert.deepStrictEqual(kb.kbSummarize(items), { total: 3, packed: 2, remaining: 1 });
assert.ok(/None ticked/.test(kb.kbSummaryText({ total: 5, packed: 0, remaining: 5 })));
assert.ok(/All 5 items ticked/.test(kb.kbSummaryText({ total: 5, packed: 5, remaining: 0 })));
assert.strictEqual(kb.kbSummaryText({ total: 0, packed: 0, remaining: 0 }), "No items to show.");
const out = kb.kbToText({ scenarios: ["Adults", "Pets"], items: [{ visible: true, checked: true, groupTitle: "Everyone", label: "Water" }, { visible: true, checked: false, groupTitle: "Everyone", label: "Radio" }, { visible: false, checked: true, groupTitle: "Children", label: "Hidden item" }] });
assert.ok(out.includes("[x] Water") && out.includes("[ ] Radio") && !out.includes("Hidden item"));
assert.ok(/does not mean you are ready/.test(out));
console.log("test_start_tools.js: all assertions passed");
