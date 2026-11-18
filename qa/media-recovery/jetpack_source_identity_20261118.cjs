'use strict';
// Offline URL identity comparison. No network access, CMS writes or HTTP claims.
// A browser-selected srcset currentSrc may vary the Jetpack size transform
// without changing the underlying historical photograph.
const TRANSFORMS = new Set(['ssl', 'resize', 'w', 'h', 'fit', 'crop', 'quality', 'strip', 'zoom']);
const isProxy = host => /^i[0-3]\.wp\.com$/.test(host);
function parse(url) {
  if (typeof url !== 'string' || url.length > 8192 || /[\x00-\x1f\x7f]/.test(url)) return null;
  let u;
  try { u = new URL(url); } catch { return null; }
  if (u.protocol !== 'https:' || u.username || u.password || u.port || u.hash) return null;
  const proxy = isProxy(u.hostname);
  let host = u.hostname, pathname = u.pathname;
  if (proxy) {
    const m = /^\/([^/]+)(\/.*)$/.exec(pathname);
    if (!m || !/^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}$/i.test(m[1]) || m[1].includes('..')) return null;
    host = m[1].toLowerCase();
    pathname = m[2];
  }
  const immutable = new Map(), mutable = new Map(), seen = new Set();
  for (const [key, value] of u.searchParams) {
    if (seen.has(key)) return null;
    seen.add(key);
    if (proxy && TRANSFORMS.has(key)) {
      if (value.length > 80 || !/^[a-zA-Z0-9_,.:-]+$/.test(value)) return null;
      if (key === 'ssl' && value !== '1') return null;
      if (['resize', 'fit'].includes(key) && !/^\d{1,6},\d{1,6}$/.test(value)) return null;
      if (['w', 'h', 'zoom'].includes(key) && !/^\d{1,6}$/.test(value)) return null;
      mutable.set(key, value);
    } else immutable.set(key, value);
  }
  return { proxy, host, pathname, immutable, mutable };
}
function sourceMatches(current, authored) {
  const a = parse(authored), c = parse(current);
  if (!a || !c || a.host !== c.host || a.pathname !== c.pathname) return false;
  if (!c.proxy) return current === authored; // No transformations on publisher/direct URLs.
  // Publisher query parameters are immutable; image CDN resizing knobs are not.
  // Even if a publisher happens to use a parameter called "w", preserve its value.
  for (const [k, v] of a.immutable) {
    const actual = c.immutable.has(k) ? c.immutable.get(k) : c.mutable.get(k);
    if (actual !== v) return false;
  }
  for (const [k] of c.immutable) if (!a.immutable.has(k)) return false;
  if (!a.proxy) {
    for (const [k] of c.mutable) if (a.immutable.has(k) && c.mutable.get(k) !== a.immutable.get(k)) return false;
  }
  return true;
}
module.exports = { sourceMatches, parse };
