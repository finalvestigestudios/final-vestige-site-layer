'use strict';
/** Restrict a browser photograph's CDP evidence to actual Image resource requests.
 * An XHR/Fetch/Document on the same URL is not evidence that an <img> loaded.
 * Does not perform network I/O or alter the original request records.
 */
function selectCdpImageRequests(rows){
 if(!Array.isArray(rows))return [];
 return rows.filter(r=>r&&r.type==='Image'&&typeof r.url==='string'&&/^https?:\/\//.test(r.url));
}
module.exports={selectCdpImageRequests};
