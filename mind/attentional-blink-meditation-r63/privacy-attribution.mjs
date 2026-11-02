/**
 * FV Mind R63 — privacy-safe hypothetical attribution contract.
 *
 * HARD DISABLED: no browser listener, storage, cookie, remote endpoint,
 * tracking pixels, third-party analytics, data capture or invocation.
 * Pure functions for offline synthetic QA only.
 * This is not an implementation approval for production measurement.
 */
export const ACTIVE = false;
export const MIN_AGGREGATE_COUNT = 20;
const VARIANT = new Set(["text", "video"]);
const TOPIC = new Set(["attentional-blink", "zen12-guide"]);
const EVENT = new Set(["guide-view", "focus-intent", "outbound-intent"]);
const SOURCE = new Set(["organic", "tiktok", "direct", "other"]);
const KEYS = ["variant", "topic", "event", "source"];

export function acceptSynthetic(row) {
  if (!row || typeof row !== "object" || Array.isArray(row)) return false;
  const given = Object.keys(row);
  if (given.length !== KEYS.length) return false;
  if (!KEYS.every(k => Object.prototype.hasOwnProperty.call(row, k))) return false;
  if (given.some(k => !KEYS.includes(k))) return false;
  if (!VARIANT.has(row.variant) || !TOPIC.has(row.topic)) return false;
  if (!EVENT.has(row.event) || !SOURCE.has(row.source)) return false;
  return true;
}
export function aggregateSynthetic(rows) {
  if (!Array.isArray(rows)) return [];
  const groups = new Map();
  for (const row of rows) {
    if (!acceptSynthetic(row)) continue;
    const key = KEYS.map(k => row[k]).join("|");
    groups.set(key, (groups.get(key) || 0) + 1);
  }
  return [...groups]
    .filter(([_key,count]) => count >= MIN_AGGREGATE_COUNT)
    .sort((a,b) => a[0].localeCompare(b[0]))
    .map(([key,count]) => {
      const [variant,topic,event,source] = key.split("|");
      return {variant,topic,event,source,count};
    });
}
export function emitLiveEvent(_row) { return false; } // must remain inert
