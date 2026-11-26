'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { imageTags, attribute, classify, audit } = require('./source_image_dependencies.cjs');
const page = content => ({ id: 1, url: 'https://finalvestige.com/story/', content });
const picture = src => '<img src="' + src + '" alt="Historical illustration">';

test('first-party absolute image', () => assert.equal(classify('https://finalvestige.com/wp-content/a.jpg'), 'first_party'));
test('first-party relative image', () => assert.equal(classify('/wp-content/a.jpg'), 'first_party'));
test('Jetpack proxy only for the first-party origin', () => {
  assert.equal(classify('https://i0.wp.com/finalvestige.com/wp-content/a.jpg?fit=500'), 'jetpack_proxy');
  assert.equal(classify('https://i0.wp.com/othersite.com/a.jpg'), 'external');
});
test('direct Wikimedia image is external', () => assert.equal(classify('https://upload.wikimedia.org/wikipedia/a.jpg'), 'external'));
test('Commons Special:Redirect image is identified', () => assert.equal(classify('https://commons.wikimedia.org/wiki/Special:Redirect/file/A.jpg?width=1280'), 'redirect_image'));
test('Google Drive thumbnail is identified', () => assert.equal(classify('https://drive.google.com/thumbnail?id=abc&amp;sz=w1600'), 'drive_thumbnail'));
test('protocol-relative third-party image is external', () => assert.equal(classify('//example.com/photo.png'), 'external'));
test('data URI is non-HTTP, not mislabeled as a broken link', () => assert.equal(classify('data:image/png;base64,abcd'), 'non_http'));
test('missing src is detected', () => assert.equal(classify(null), 'missing_src'));
test('non-HTML script and style strings are not counted as images', () => {
  assert.equal(imageTags("<script>const s='" + picture('/fake.jpg') + "';</script><style>.a{content:'" + picture('/style.jpg') + "'}</style><!-- " + picture('/comment.jpg') + " -->" + picture('/real.jpg')).length, 1);
});
test('both single and double quoted src work', () => {
  assert.equal(attribute("<img alt='x' src='/photo.png'>", 'src'), '/photo.png');
  assert.equal(attribute('<img src="/photo.png" alt="x">', 'src'), '/photo.png');
});
test('offsite threshold yields REVIEW, never a frontend failure claim', () => {
  const input = { pages: [page(Array(4).fill(picture('https://example.com/img.jpg')).join(''))] };
  const result = audit(input);
  assert.equal(result.offsite_count, 4);
  assert.equal(result.review_pages.length, 1);
  assert.equal(result.http_verified, false);
});
test('a single external illustration does not trigger volume review', () => {
  const result = audit({pages:[page(picture('https://example.com/a.jpg'))]});
  assert.equal(result.review_pages.length, 0);
});
test('bad snapshots fail closed instead of silently claiming an audit', () => {
  assert.throws(() => audit({pages:'bad'}), /Expected/);
  assert.throws(() => audit({pages:[{url:'https://finalvestige.com',content:1}]}), /Invalid/);
});
test('aggregate totals distinguish local, proxy and external images', () => {
  const html = [picture('/a.jpg'), picture('https://i1.wp.com/finalvestige.com/a.jpg'), picture('https://outside.test/b.jpg')].join('');
  const result = audit({pages:[page(html)]});
  assert.deepEqual([result.image_count,result.counts.first_party,result.counts.jetpack_proxy,result.counts.external], [3,1,1,1]);
});
