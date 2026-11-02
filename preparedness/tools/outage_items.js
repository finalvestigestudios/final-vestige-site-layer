/* Power-outage readiness planner: checklist data and pure logic. No DOM, no storage, no network.
   Every item cites the agency page it comes from, or says it is the editor's suggestion. The tool never gives generator
   sizes, wiring, fuel quantities, run times, heater ventilation or medical advice, because the verified sources do not. */
var OUTAGE_SRC = {
  rgOutage: "Ready.gov, Power Outages",
  rgWinter: "Ready.gov, Winter Weather",
  rgHeat: "Ready.gov, Extreme Heat",
  rgDis: "Ready.gov, People with Disabilities",
  rgShelter: "Ready.gov, Shelter",
  rgEvac: "Ready.gov, Evacuation",
  rgTech: "Ready.gov, Get Tech Ready",
  rgLoc: "Ready.gov, Plan for Locations",
  fema: "FEMA, Be Prepared for a Power Outage (Dec 2023)",
  cdcOut: "CDC, Protect Yourself During a Power Outage",
  cdcPsa: "CDC, Avoiding Carbon Monoxide Poisoning",
  cdcWin: "CDC, Winter Storm Safety",
  cdcHeat: "CDC, About Heat and Your Health",
  cdcCo: "CDC, Carbon Monoxide Basics",
  cpsc: "CPSC, Carbon Monoxide",
  nws: "NWS, NOAA Weather Radio",
  editor: "Editor's suggestion (not an agency statement)"
};

/* Questions asked of the household. Each key is a boolean answer. */
var OUTAGE_QUESTIONS = [
  { key: "medDevice", label: "Someone depends on electrically powered medical equipment" },
  { key: "coldMeds", label: "Someone takes a medicine that needs refrigeration" },
  { key: "baby", label: "There is an infant or a small child" },
  { key: "school", label: "There are school-aged children" },
  { key: "older", label: "There is an adult aged 65 or older" },
  { key: "pets", label: "We have pets" },
  { key: "mobility", label: "Someone has a mobility disability" },
  { key: "deaf", label: "Someone is deaf or hard of hearing" },
  { key: "blind", label: "Someone is blind or has low vision" },
  { key: "commDis", label: "Someone has a speech or communication disability" },
  { key: "caregiver", label: "Someone relies on a caregiver or support network" },
  { key: "apartment", label: "We live in an apartment, condominium or other shared building" },
  { key: "heat", label: "Extreme heat is a realistic risk where we live" },
  { key: "cold", label: "Extreme cold or winter storms are a realistic risk where we live" },
  { key: "generator", label: "We own or are thinking about a portable generator" },
  { key: "altHeat", label: "We might use a fireplace, wood stove or portable heater when the power is out" }
];

var OUTAGE_GROUPS = [
  { id: "lighting", title: "Lighting" },
  { id: "comms", title: "Communications and alerts" },
  { id: "food", title: "Refrigeration, food and water" },
  { id: "weather", title: "Heat and cold" },
  { id: "meds", title: "Medicines and medical devices" },
  { id: "family", title: "Children, older adults and pets" },
  { id: "access", title: "Mobility, hearing, vision and support networks" },
  { id: "shelter", title: "A safe place to go" },
  { id: "co", title: "Carbon monoxide, generators and alternative heat" }
];

/* when: [] means always. Otherwise the item shows if ANY listed answer is true. */
var OUTAGE_ITEMS = [
  { id: "L1", g: "lighting", when: [], src: "rgOutage", text: "Keep a flashlight for every household member." },
  { id: "L2", g: "lighting", when: [], src: "cdcOut", text: "Use battery-powered flashlights and lanterns instead of candles. If you do use candles, keep them away from anything that can catch fire and never leave them unattended." },
  { id: "L3", g: "lighting", when: [], src: "rgWinter", text: "Keep extra batteries for flashlights and radios." },
  { id: "L4", g: "lighting", when: ["deaf"], src: "rgDis", text: "Keep a battery-operated lantern so people who sign or lip-read can communicate when the electricity is out and it is dark." },
  { id: "C1", g: "comms", when: [], src: "rgOutage", text: "List the things you rely on electricity for, and plan how you would manage without each one." },
  { id: "C2", g: "comms", when: [], src: "rgTech", text: "Have a way to keep phones charged, such as a portable charger or power bank, and use low-power mode to save battery." },
  { id: "C3", g: "comms", when: [], src: "rgOutage", text: "Find out whether your home phone will work in an outage and how long any battery backup will last." },
  { id: "C4", g: "comms", when: [], src: "rgTech", text: "Plan to use text messages rather than calls when networks are busy, and save calls for emergencies." },
  { id: "C5", g: "comms", when: [], src: "fema", text: "Make a family communication plan and keep a paper copy." },
  { id: "C6", g: "comms", when: [], src: "nws", text: "Have an alert source that does not depend on home power, such as NOAA Weather Radio (it needs a special receiver) or local alerts on a charged phone." },
  { id: "C7", g: "comms", when: ["deaf"], src: "rgDis", text: "Consider a weather radio with a text display and flashing alert, extra hearing-aid batteries, and pen and paper." },
  { id: "C8", g: "comms", when: ["commDis"], src: "rgDis", text: "Carry printed cards or store information on a device that tells first responders and others how to communicate with you, and plan how you will communicate if an assistive device stops working." },
  { id: "F1", g: "food", when: [], src: "cdcOut", text: "Keep refrigerator and freezer doors closed as much as possible." },
  { id: "F2", g: "food", when: [], src: "cdcOut", text: "Know the agencies' timings: a refrigerator keeps food cold for about 4 hours, and a full freezer for about 48 hours (24 hours if half full), if the doors stay closed." },
  { id: "F3", g: "food", when: [], src: "fema", text: "Keep a thermometer in the refrigerator and freezer, and be ready to keep them cold with ice." },
  { id: "F4", g: "food", when: [], src: "rgOutage", text: "When in doubt, throw it out. The agencies' time limits differ (Ready.gov says food exposed to 40°F or higher for two hours or more; FEMA and the CDC say about four hours), so check current USDA food-safety guidance for specific foods." },
  { id: "F5", g: "food", when: [], src: "fema", text: "Gather food and water to last several days, and check your supplies regularly." },
  { id: "F6", g: "food", when: [], src: "fema", text: "Do not store food outside or in the snow in cold weather." },
  { id: "F7", g: "food", when: [], src: "fema", text: "Pay attention to water advisories. Use bottled water, or boil water, if advised." },
  { id: "W1", g: "weather", when: ["heat"], src: "cdcHeat", text: "Find places with air conditioning you could go to: call 2-1-1, check cooling-center listings, or ask your health department or emergency management agency." },
  { id: "W2", g: "weather", when: ["heat"], src: "cdcHeat", text: "Do not rely on a fan alone. The CDC says to use fans only when the indoor temperature is below 90°F." },
  { id: "W3", g: "weather", when: ["heat"], src: "rgHeat", text: "Learn the signs of heat illness. For suspected heat stroke (confusion, no sweating, hot dry skin, unconsciousness), call 911." },
  { id: "W4", g: "weather", when: ["heat"], src: "rgHeat", text: "Plan for fluids, cool showers or baths, light-colored lightweight clothing, and avoiding strenuous activity in midday heat." },
  { id: "W5", g: "weather", when: ["cold"], src: "cdcWin", text: "Have extra blankets, sleeping bags and warm coats. Close off rooms you do not need, stuff towels under doors, and cover windows at night." },
  { id: "W6", g: "weather", when: ["cold"], src: "cdcWin", text: "Learn the signs of hypothermia and frostbite. A body temperature below 95°F is an emergency: get medical attention." },
  { id: "W7", g: "weather", when: ["cold"], src: "cdcWin", text: "Know how to protect pipes in freezing weather: leave taps slightly open so they drip, and open cabinet doors under sinks." },
  { id: "W8", g: "weather", when: ["heat", "cold"], src: "rgOutage", text: "Plan to go to a community location with power if heat or cold becomes extreme." },
  { id: "W9", g: "weather", when: [], src: "fema", text: "Plan to check on family members and neighbors if it is safe to do so." },
  { id: "M1", g: "meds", when: ["coldMeds"], src: "rgOutage", text: "Ask your doctor or pharmacist, before an outage, how long each of your medicines can be stored at higher temperatures." },
  { id: "M2", g: "meds", when: ["coldMeds"], src: "rgDis", text: "Keep a cooler and chemical ice packs available for medicines that need to be kept cold." },
  { id: "M3", g: "meds", when: ["coldMeds"], src: "fema", text: "If the power is out for a day or more, call your pharmacist or doctor about any refrigerated medicine. FEMA says to replace refrigerated medications unless the label says otherwise, and to use a medicine that has been at room temperature only until you have a new supply. Do not stop or change a medicine on your own." },
  { id: "M4", g: "meds", when: ["medDevice"], src: "fema", text: "Talk to your doctor or health care provider now about a plan for each device that needs electricity: what to do in an outage." },
  { id: "M5", g: "meds", when: ["medDevice"], src: "rgDis", text: "Ask your power provider whether it keeps a priority-restoration list and how to be put on it. Ready.gov says you can ask." },
  { id: "M6", g: "meds", when: ["medDevice"], src: "rgDis", text: "Know where you would go if the equipment cannot run, and how you would get there. If you rely on dialysis or other life-sustaining treatment, know the location and availability of more than one facility." },
  { id: "M7", g: "meds", when: ["medDevice"], src: "rgDis", text: "Keep a list of your devices with style, serial number and special operating instructions, and where each came from." },
  { id: "M8", g: "meds", when: ["medDevice", "mobility"], src: "rgDis", text: "Keep extra batteries charged for battery-operated medical or assistive devices and mobility equipment." },
  { id: "M9", g: "meds", when: ["medDevice"], src: "editor", disclaimer: true, text: "This page does not size backup power or tell you how to run medical equipment on a generator or battery. Make that plan with your provider, the device supplier and your utility." },
  { id: "K1", g: "family", when: ["baby"], src: "cdcWin", text: "Infants under one year should never sleep in a cold room. The CDC advises warm sleepwear or a sleep sack and no pillows or soft bedding, and says to arrange to stay elsewhere if you cannot keep the home warm." },
  { id: "K2", g: "family", when: ["school"], src: "rgLoc", text: "Find out your child's school or childcare emergency plan and how families are notified, and make back-up plans for your children in case you cannot get home." },
  { id: "K3", g: "family", when: ["older"], src: "cdcWin", text: "Older adults often make less body heat. People over 65 should check the home temperature often in extreme cold." },
  { id: "K4", g: "family", when: ["pets"], src: "rgHeat", text: "Make sure pets have cool water and access to shade in heat." },
  { id: "K5", g: "family", when: ["pets"], src: "rgShelter", text: "Many public shelters and hotels do not allow pets, though all shelters accept service animals. Know a safe place for pets to go before an emergency." },
  { id: "A1", g: "access", when: ["mobility"], src: "rgDis", text: "Plan accessible transportation to a warming or cooling place in advance, checking with local transit providers and your emergency management agency." },
  { id: "A2", g: "access", when: ["mobility"], src: "rgDis", text: "Tell neighbors who could help if you must leave the building, and keep a backup mobility device if you can." },
  { id: "A3", g: "access", when: ["blind"], src: "rgDis", text: "Mark emergency supplies with Braille or large print, and keep a list of supplies on a flash drive or as an audio file." },
  { id: "A4", g: "access", when: ["apartment"], src: "rgLoc", text: "Talk to neighbors about working together. Find out who has equipment such as a generator or expertise such as medical knowledge, and decide who will check on elderly or disabled neighbors." },
  { id: "A5", g: "access", when: ["caregiver"], src: "rgDis", text: "Tell your support network where your supplies are, keep their contact list in a watertight container or on your devices, and consider giving a trusted person a key." },
  { id: "S1", g: "shelter", when: [], src: "rgOutage", text: "Choose two places you could go if heat or cold becomes dangerous, such as a friend's or relative's home and a community location with power. Check with local officials about heating and cooling locations open near you." },
  { id: "S2", g: "shelter", when: [], src: "editor", text: "Decide in advance what would make you leave (for example, a medical need that cannot be met, or indoor conditions you cannot make safe) and how you would get there." },
  { id: "S3", g: "shelter", when: [], src: "rgShelter", text: "During an active disaster you can search for open shelters by texting SHELTER and your ZIP code to 43362 (standard rates apply)." },
  { id: "S4", g: "shelter", when: [], src: "cdcPsa", text: "If your home is damaged, stay with friends or family or in a shelter." },
  { id: "G0", g: "co", when: [], src: "cdcCo", text: "Have working battery or battery-backup carbon monoxide alarms before the outage. The agencies word placement differently (near every sleeping area; on every level; or both), so follow the alarm's instructions and cover both." },
  { id: "G1", g: "co", when: ["generator"], src: "cpsc", text: "Run a generator only outdoors, at least 20 feet from windows, doors, vents and attached garages, with the exhaust facing away. Never run it in a garage, basement or other enclosed structure, even with doors and windows open. Twenty feet is a minimum, not a guarantee." },
  { id: "G2", g: "co", when: ["generator"], src: "rgOutage", text: "Keep a generator dry, connect appliances with heavy-duty outdoor-rated cords, let it cool before refueling, store fuel safely, and follow the manufacturer's instructions." },
  { id: "G3", g: "co", when: ["generator"], src: "rgEvac", text: "Never connect a generator to your home's electrical system." },
  { id: "G4", g: "co", when: ["generator"], src: "editor", disclaimer: true, text: "This page gives no generator size, fuel quantity, run time or wiring advice, because the sources we verified do not. Use the manufacturer's instructions." },
  { id: "G5", g: "co", when: ["altHeat", "cold"], src: "cdcOut", text: "Never use a gas oven or stovetop to heat a home, and never use a charcoal grill, camp stove or lantern indoors." },
  { id: "G6", g: "co", when: ["altHeat"], src: "cdcWin", text: "Use a fireplace, wood stove or portable heater only if it is properly vented to the outside and in good order, follow the manufacturer's instructions, and keep heaters at least 3 feet from anything that can burn." },
  { id: "G7", g: "co", when: ["altHeat", "generator"], src: "cpsc", text: "Know the symptoms of carbon monoxide poisoning: headache, dizziness, weakness, nausea, vomiting, sleepiness and confusion. If you suspect it, get outside to fresh air immediately, then call 911." },
  { id: "G8", g: "co", when: ["generator", "cold"], src: "fema", text: "Never leave a vehicle running inside a garage, even with the garage door open." }
];

var OUTAGE_CONTACTS = [
  { key: "utility", label: "Electric utility phone", when: [] },
  { key: "oem", label: "Local emergency management or information line", when: [] },
  { key: "outside", label: "Out-of-area contact", when: [] },
  { key: "doctor", label: "Doctor or pharmacist", when: ["coldMeds", "medDevice"] },
  { key: "supplier", label: "Medical equipment supplier", when: ["medDevice"] },
  { key: "building", label: "Building manager", when: ["apartment"] },
  { key: "neighbor", label: "Neighbor who can check on us", when: [] }
];

function outageActive(when, answers) {
  if (!when || !when.length) return true;
  return when.some(function (k) { return !!answers && answers[k] === true; });
}

function buildOutageChecklist(answers) {
  var a = answers || {};
  var groups = OUTAGE_GROUPS.map(function (g) {
    return {
      id: g.id, title: g.title,
      items: OUTAGE_ITEMS.filter(function (it) { return it.g === g.id && outageActive(it.when, a); })
        .map(function (it) { return { id: it.id, text: it.text, src: OUTAGE_SRC[it.src], editor: it.src === "editor", disclaimer: it.disclaimer === true }; })
    };
  }).filter(function (g) { return g.items.length > 0; });
  var contacts = OUTAGE_CONTACTS.filter(function (c) { return outageActive(c.when, a); });
  return { groups: groups, contacts: contacts };
}

function outageText(answers, doneIds, contactValues) {
  var list = buildOutageChecklist(answers);
  var done = {};
  (Array.isArray(doneIds) ? doneIds : []).forEach(function (id) { done[String(id)] = true; });
  var vals = contactValues || {};
  var L = ["POWER OUTAGE READINESS CHECKLIST (Final Vestige Preparedness Archive). Not medical advice. Not a substitute for guidance from your doctor, device supplier, utility or local officials.", ""];
  list.groups.forEach(function (g) {
    L.push(g.title.toUpperCase());
    g.items.forEach(function (it) { L.push((done[it.id] ? "[x] " : "[ ] ") + it.text + " (" + it.src + ")"); });
    L.push("");
  });
  L.push("CONTACTS");
  list.contacts.forEach(function (c) { L.push(c.label + ": " + paCleanText(vals[c.key], 120)); });
  return L.join("\n");
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OUTAGE_SRC: OUTAGE_SRC, OUTAGE_QUESTIONS: OUTAGE_QUESTIONS, OUTAGE_GROUPS: OUTAGE_GROUPS, OUTAGE_ITEMS: OUTAGE_ITEMS, OUTAGE_CONTACTS: OUTAGE_CONTACTS, buildOutageChecklist: buildOutageChecklist, outageText: outageText };
}
