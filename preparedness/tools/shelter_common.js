/* Shared helpers for the Shelter, Power and Family Communication tools.
   Pure functions plus one local file download. No storage, no network, no innerHTML. */
function paCleanText(value, max) {
  var s = String(value == null ? "" : value);
  s = s.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F​-‏‪-‮⁦-⁩]/g, "");
  s = s.replace(/[ \t\r\n]+/g, " ").trim();
  var limit = Math.max(0, Math.floor(Number(max)) || 200);
  return s.length > limit ? s.slice(0, limit) : s;
}

function paIsoOrNull(iso) {
  var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ""));
  if (!m) return null;
  var y = Number(m[1]), mo = Number(m[2]), d = Number(m[3]);
  var dt = new Date(Date.UTC(y, mo - 1, d));
  if (dt.getUTCFullYear() !== y || dt.getUTCMonth() !== mo - 1 || dt.getUTCDate() !== d) return null;
  return { y: y, m: mo - 1, d: d };
}

/* Add whole calendar months to an ISO date (YYYY-MM-DD). Clamps to the end of a shorter month. Returns ISO or null. */
function paAddMonths(iso, months) {
  var p = paIsoOrNull(iso);
  var n = Math.floor(Number(months));
  if (!p || !isFinite(n) || Math.abs(n) > 1200) return null;
  var target = new Date(Date.UTC(p.y, p.m + n, 1));
  var last = new Date(Date.UTC(target.getUTCFullYear(), target.getUTCMonth() + 1, 0)).getUTCDate();
  target.setUTCDate(Math.min(p.d, last));
  return target.toISOString().slice(0, 10);
}

function paAddYears(iso, years) {
  return paAddMonths(iso, Math.floor(Number(years)) * 12);
}

/* Write a plain-text file to the user's device with a Blob. Nothing is sent anywhere. */
function paDownloadText(filename, text) {
  var safe = String(filename || "plan.txt").replace(/[^A-Za-z0-9._-]/g, "-").slice(0, 80);
  var blob = new Blob([String(text)], { type: "text/plain;charset=utf-8" });
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = safe;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { paCleanText: paCleanText, paIsoOrNull: paIsoOrNull, paAddMonths: paAddMonths, paAddYears: paAddYears };
}
