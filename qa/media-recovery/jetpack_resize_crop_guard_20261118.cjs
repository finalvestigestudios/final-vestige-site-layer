'use strict';
// Offline parity safety: WordPress says Jetpack ?resize=W,H resizes AND CROPS.
// Therefore responsive replacement dimensions may vary proportionally but must
// not change aspect ratio (or add/remove the crop transform) without review.
// Unlike ?resize, ?fit maintains source aspect ratio and may change freely.
function resizeBox(raw) {
  let u;
  try { u = new URL(raw); } catch { return { invalid: true }; }
  if (!/^i[0-3]\.wp\.com$/i.test(u.hostname)) return null;
  const values = u.searchParams.getAll('resize');
  if (!values.length) return null;
  if (values.length !== 1 || !/^\d{1,6},\d{1,6}$/.test(values[0])) return { invalid: true };
  const parts = values[0].split(',').map(Number);
  if (parts[0] <= 0 || parts[1] <= 0) return { invalid: true };
  return parts;
}
function resizeCropPreserved(beforeUrl, afterUrl) {
  const a = resizeBox(beforeUrl), b = resizeBox(afterUrl);
  if (a === null && b === null) return true;
  if (!Array.isArray(a) || !Array.isArray(b)) return false;
  return BigInt(a[0]) * BigInt(b[1]) === BigInt(b[0]) * BigInt(a[1]);
}
module.exports = { resizeCropPreserved };
