// Final Vestige / Mind R74: OFF by design. No network, cookies or storage.
// Deliberately synthetic event classification for future design review ONLY.
export const ENABLED = false;
const KEYS = ["source","topic","variant","event","destination"];
const ACCEPT = Object.freeze({
  source: ["tiktok","organic_search","internal","direct_unknown"],
  topic: ["attentional_blink","zen12_guide","puysegur","focus"],
  variant: ["text","film","none"],
  event: ["guide_view","offer_button_intent","focus_link_intent"],
  destination: ["guide","focus","merchant_disabled"]
});
export function classifySynthetic(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) return null;
  const keys = Object.keys(input);
  if (keys.length !== KEYS.length || !KEYS.every(k => keys.includes(k))) return null;
  const clean = Object.create(null);
  for (const k of KEYS) {
    if (typeof input[k] !== "string" || !ACCEPT[k].includes(input[k])) return null;
    clean[k] = input[k];
  }
  return clean;
}
// Returns null until release gates explicitly authorize a different module.
export function capture() { return null; }
export function summarizeSynthetic(rows, minimum = 20) {
  if (!Array.isArray(rows) || minimum < 20 || !Number.isInteger(minimum)) return [];
  const groups = new Map();
  for (const row of rows) {
    const rec = classifySynthetic(row);
    if (!rec) continue;
    const key = KEYS.map(k=>rec[k]).join("|");
    groups.set(key, (groups.get(key) || 0) + 1);
  }
  return [...groups].filter(([,count])=>count>=minimum).map(([key,count])=>({bucket:key,count}));
}
