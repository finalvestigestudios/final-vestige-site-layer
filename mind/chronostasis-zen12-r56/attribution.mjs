/** Privacy-first synthetic attribution specification — NO live collection.
 * Never call this from WordPress production or use identity, IP, cookies,
 * identifiers, timestamps, full referrers, page paths, UTM strings or emails.
 * Reports only preapproved categories, with counts <20 suppressed.
 */
export const ATTRIBUTION_ENABLED = false;
export const MIN_GROUP_SIZE = 20;
const allow = Object.freeze({
  source: ["organic","tiktok","direct","dispatch","internal","other"],
  variant: ["A","B"],
  topic: ["zen12-guide","chronostasis","mind-hub","focus-fieldbook"],
  event: ["guide_view","qualified_outbound_click"]
});
export function validateSyntheticEvent(candidate) {
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) throw new TypeError("Expected plain object");
  const keys = Object.keys(candidate);
  if (keys.length !== 4 || keys.some(k => !Object.hasOwn(allow,k))) throw new TypeError("Unexpected or personal field rejected");
  for (const key of Object.keys(allow)) {
    if (typeof candidate[key] !== "string" || !allow[key].includes(candidate[key])) throw new TypeError("Unapproved category: "+key);
  }
  return Object.freeze({source:candidate.source,variant:candidate.variant,topic:candidate.topic,event:candidate.event});
}
export function recordVisitorEvent(_candidate) {
  // Deliberate fail-closed no-op; activation requires authorization, privacy review,
  // first-party implementation and a separately approved release.
  return null;
}
export function aggregateSyntheticTest(events) {
  if (!Array.isArray(events)) throw new TypeError("Expected synthetic test records");
  const counts = new Map();
  for (const input of events) {
    const e = validateSyntheticEvent(input);
    const key = [e.source,e.variant,e.topic,e.event].join("|");
    counts.set(key,(counts.get(key)||0)+1);
  }
  return Array.from(counts).filter(([,n])=>n>=MIN_GROUP_SIZE).map(([key,n])=>{
    const [source,variant,topic,event] = key.split("|");
    return Object.freeze({source,variant,topic,event,count:n});
  });
}
