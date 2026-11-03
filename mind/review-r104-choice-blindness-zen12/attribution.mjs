/**
 * FV Mind R104 OFFLINE-ONLY synthetic attribution contract.
 * No import side effects. No browser code. No network. No storage, identifiers,
 * referrer URL, timestamps, clicks, purchases or real users.
 * Merchant tracking/partner acceptance is NOT enabled by this module.
 */
const FIELDS = Object.freeze(["variant", "source", "topic", "action"]);
const ALLOWED = Object.freeze({
  variant: ["A", "B"],
  source: ["tiktok", "organic_search", "site_navigation", "direct", "unknown"],
  topic: ["zen12", "choice_blindness"],
  action: ["guide_view", "evidence_open", "fieldbook_link", "merchant_intent_simulated"]
});
const MIN_CELL_SIZE = 20;
function isPlainRecord(value) {
  return value !== null && typeof value === "object" &&
    !Array.isArray(value) && Object.getPrototypeOf(value) === Object.prototype;
}
export function validateSyntheticRecord(value) {
  if (!isPlainRecord(value)) throw new TypeError("Plain synthetic record required");
  const keys = Object.keys(value).sort();
  if (keys.length !== FIELDS.length || keys.join("|") !== [...FIELDS].sort().join("|")) {
    throw new TypeError("Unexpected or missing fields; identifying fields are forbidden");
  }
  for (const key of FIELDS) {
    if (typeof value[key] !== "string" || !ALLOWED[key].includes(value[key])) {
      throw new TypeError("Invalid categorical value for " + key);
    }
  }
  return Object.freeze({variant:value.variant,source:value.source,topic:value.topic,action:value.action});
}
export function aggregateSyntheticRecords(records) {
  if (!Array.isArray(records)) throw new TypeError("Synthetic array required");
  const bins = new Map();
  for (const entry of records) {
    const x = validateSyntheticRecord(entry);
    const k = [x.variant,x.source,x.topic,x.action].join("|");
    bins.set(k, (bins.get(k) ?? 0) + 1);
  }
  const visible = [];
  for (const [key, count] of bins) {
    if (count < MIN_CELL_SIZE) continue;
    const [variant,source,topic,action] = key.split("|");
    visible.push(Object.freeze({variant,source,topic,action,syntheticCount:count}));
  }
  return Object.freeze(visible.sort((a,b)=>[a.variant,a.source,a.topic,a.action].join("|").localeCompare([b.variant,b.source,b.topic,b.action].join("|"))));
}
export function recordLiveEvent() {
  throw new Error("HARD HOLD: no live visitor instrumentation or partner conversion measurement approved");
}
export const SYNTHETIC_POLICY = Object.freeze({kind:"OFFLINE_SYNTHETIC_ONLY",minCellSize:MIN_CELL_SIZE,realSalesMeasured:false,liveOutboundEnabled:false});
