'use strict';
/**
 * Fail-closed HAR page scoping. HAR is user-supplied, not independent browser
 * attestation. Never attribute another tab's request to the audited article.
 * No network, CMS writes, cookie/header or image-body handling here.
 */
function articlePath(raw) {
  if (typeof raw !== 'string') return null;
  try {
    const u = new URL(raw);
    if (u.protocol !== 'https:' || u.hostname !== 'finalvestige.com' ||
        u.username || u.password) return null;
    const p = u.pathname.replace(/\/+$/, '') || '/';
    return u.origin + p;
  } catch { return null; }
}
function isArticleDocument(e, target, pageId) {
  if (!e || e.pageref !== pageId || String(e._resourceType || '').toLowerCase() !== 'document' ||
      e.request?.method !== 'GET' || articlePath(e.request?.url) !== target) return false;
  const status = e.response?.status;
  const mime = typeof e.response?.content?.mimeType === 'string' ?
    e.response.content.mimeType.split(';')[0].trim().toLowerCase() : '';
  return Number.isInteger(status) && status >= 200 && status < 300 &&
    (mime === 'text/html' || mime === 'application/xhtml+xml');
}
function scopeHarToArticle(har, articleUrl) {
  if (!har || !har.log || !Array.isArray(har.log.entries)) throw Error('Valid HAR log.entries required');
  const entries = har.log.entries, pages = har.log.pages;
  const base = {ok:false, scoped_entries:[], input_entry_count:entries.length,
    excluded_unscoped_entries:entries.length};
  const target = articlePath(articleUrl);
  if (!target) return {...base,reason:'INVALID_EXPECTED_ARTICLE_URL'};
  if (!Array.isArray(pages) || !pages.length) return {...base,reason:'MISSING_HAR_PAGE_METADATA'};
  if (pages.some(p=>!p || typeof p.id !== 'string' || !p.id.trim()) ||
      new Set(pages.map(p=>p.id)).size !== pages.length)
    return {...base,reason:'DUPLICATE_OR_INVALID_HAR_PAGE_IDS'};
  const matches = pages.filter(p=>articlePath(p.title) === target);
  if (matches.length !== 1) return {...base,reason:matches.length ? 'AMBIGUOUS_ARTICLE_PAGES' : 'ARTICLE_PAGE_NOT_IN_HAR'};
  const id = matches[0].id;
  if (!entries.some(e=>isArticleDocument(e,target,id)))
    return {...base,reason:'MATCHING_SUCCESSFUL_DOCUMENT_REQUEST_MISSING'};
  const scoped = entries.filter(e=>e && e.pageref === id);
  return {ok:true,reason:'SUPPLIED_HAR_ARTICLE_SCOPE_CONSISTENT',
    scoped_entries:scoped,input_entry_count:entries.length,
    excluded_unscoped_entries:entries.length-scoped.length};
}
module.exports = {articlePath,isArticleDocument,scopeHarToArticle};

