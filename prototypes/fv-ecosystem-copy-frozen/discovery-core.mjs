// Pure functions for a future Daily Discovery integration. No UI strings, tracking,
 // network calls, storage, approved content, or WordPress hooks.
export function eligibleRecords(records) {
 if (!Array.isArray(records)) return [];
 const seen = new Set();
 return records.filter(r => {
  if (!r || typeof r.id !== 'string' || !r.id.trim() || seen.has(r.id) ||
      r.reviewStatus !== 'approved' || r.copyApproved !== true ||
      r.rightsApproved !== true || !Array.isArray(r.sources) ||
      !r.sources.length || !r.sources.every(s => typeof s === 'string' && /^https:\/\//i.test(s))) return false;
  seen.add(r.id); return true;
 }).sort((a,b)=>a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
}
export function dailyRecord(records, date = new Date()) {
 const available = eligibleRecords(records);
 if (!(date instanceof Date) || !Number.isFinite(date.valueOf()) || !available.length) return null;
 const day = Math.floor(date.valueOf()/86400000);
 return available[((day % available.length)+available.length)%available.length];
}
export function recordById(records,id) {
 return eligibleRecords(records).find(r=>r.id===id) ?? null;
}
