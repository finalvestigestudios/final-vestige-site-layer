// Research-only synthetic aggregation prototype. NO active visitor collection.
// This file is not included in any published WordPress content.
export const ACTIVE = false;
export const ALLOWLIST = Object.freeze({
  source: Object.freeze(["organic","tiktok","direct","unknown"]),
  topic: Object.freeze(["gorilla-second-look","zen12-guide","mind-hub"]),
  variant: Object.freeze(["text","film"])
});
export const MIN_GROUP_SIZE = 20;

export function validateSyntheticInput(input) {
  if (input === null || typeof input !== "object" || Array.isArray(input)) throw new TypeError("Expected plain synthetic object");
  const allowed = ["source","topic","variant","clicked"];
  if (Object.keys(input).some(k => !allowed.includes(k))) throw new Error("Unexpected field blocked (including URLs, UTM strings or PII)");
  for (const k of ["source","topic","variant"]) {
    if (!ALLOWLIST[k].includes(input[k])) throw new Error("Unapproved value blocked: "+k);
  }
  if (typeof input.clicked !== "boolean") throw new Error("Synthetic clicked flag required");
  return Object.freeze({ source: input.source, topic: input.topic, variant: input.variant, clicked: input.clicked });
}
export function collectOutboundEvent() {
  // Do not bypass by setting ACTIVE without an approved separate implementation.
  throw new Error("Outbound attribution is not activated; verified account permission and privacy review required");
}
export function summarizeSynthetic(rows) {
  if (!Array.isArray(rows)) throw new TypeError("Expected synthetic rows");
  const groups = new Map();
  for (const row of rows) {
    const r = validateSyntheticInput(row);
    const key = [r.source,r.topic,r.variant].join("|");
    const count = groups.get(key) || { source:r.source, topic:r.topic, variant:r.variant, impressions:0, clicked:0 };
    count.impressions += 1;
    if (r.clicked) count.clicked += 1;
    groups.set(key,count);
  }
  return [...groups.values()].filter(g=>g.impressions>=MIN_GROUP_SIZE).map(g=>Object.freeze({...g,click_rate:g.clicked/g.impressions}));
}
// Actual affiliate conversions cannot be inferred from click counts.
// No cookie/localStorage, IP, device, referrer URL, UTM string, email,
// visitor ID, tracking pixel, network request or external dependency.
