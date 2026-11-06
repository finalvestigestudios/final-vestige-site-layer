'use strict';
/**
 * Read-only WordPress Page 1579 migration PROPOSAL.
 * Patches a local export of Gutenberg edit content; never calls WP or publishes.
 * Insert the permanent hash target before the native Jetpack subscriptions block
 * so #subscribe-blog works without the optional client-side anchor installer.
 *
 * Usage: node focus_1579_nojs_anchor_proposal.cjs --input focus-edit-export.html --output proposed.html
 */
function transform(original) {
  if (typeof original !== 'string' || original.length < 12000 || original.length > 200000) {
    throw Error('UNEXPECTED_EDITOR_EXPORT');
  }
  if (!original.includes('Stop dreading it.') ||
      !original.includes('The Seven Day Focus Fieldbook') ||
      !original.includes('fvf-signup-anchor-v1')) {
    throw Error('WRONG_FOCUS_CONTENT_OR_REVISION');
  }
  const block = /<!-- wp:jetpack\/subscriptions \{[^\r\n]*\} \/-->/g;
  const markers = [...original.matchAll(block)];
  if (markers.length !== 1) {
    throw Error('EXPECTED_ONE_JETPACK_BLOCK_GOT_' + markers.length);
  }
  const refs = [...original.matchAll(/href=["']#subscribe-blog["']/g)].length;
  if (refs !== 5) {
    throw Error('UNEXPECTED_INTERNAL_CTA_COUNT_' + refs);
  }
  if (/id=["']subscribe-blog["']/.test(original)) {
    throw Error('ANCHOR_ALREADY_STATIC_OR_DUPLICATED');
  }
  // A real, parser-visible Gutenberg HTML block precedes the subscription block.
  // With JavaScript on, the existing installer detects the ID and does nothing.
  const patch = '<!-- wp:html -->\n' +
    '<span id="subscribe-blog" style="display:block;scroll-margin-top:5rem" aria-hidden="true"></span>\n' +
    '<!-- /wp:html -->\n\n';
  const index = markers[0].index;
  const modified = original.slice(0, index) + patch + original.slice(index);
  if (modified.slice(0,index) !== original.slice(0,index) ||
      modified.slice(index + patch.length) !== original.slice(index) ||
      [...modified.matchAll(block)].length !== 1 ||
      (modified.match(/id="subscribe-blog"/g) || []).length !== 1 ||
      [...modified.matchAll(/href=["']#subscribe-blog["']/g)].length !== refs ||
      !modified.includes('fvf-signup-anchor-v1')) {
    throw Error('SOURCE_CUSTODY_FAILURE');
  }
  return { content: modified, inserted: patch.length, fiveLinksResolvedInStaticMarkup: true };
}
function selfTest() {
  const base = '<div class="fv-focus">Stop dreading it. The Seven Day Focus Fieldbook ' +
    'fvf-signup-anchor-v1 ' + 'q'.repeat(12000) +
    Array(5).fill('<a href="#subscribe-blog">Get the fieldbook</a>').join('') +
    '\n<!-- wp:jetpack/subscriptions {"submitButtonText":"Send me the fieldbook"} /-->';
  const good = transform(base);
  if (good.inserted <= 90 || !good.fiveLinksResolvedInStaticMarkup) throw Error('POSITIVE_FIXTURE_FAILED');
  const bad = [
    base.replace('Stop dreading it.', 'Another page.'),
    base.replace('fvf-signup-anchor-v1', 'anchor missing'),
    base.replace('wp:jetpack/subscriptions', 'wp:jetpack/other'),
    base.replace('href="#subscribe-blog"', 'href="#elsewhere"'),
    base + '\n<!-- wp:jetpack/subscriptions {"submitButtonText":"Send me the fieldbook"} /-->',
    good.content,
  ];
  for (let i=0; i<bad.length; i++) {
    let rejected=false; try { transform(bad[i]); } catch (_) { rejected=true; }
    if (!rejected) throw Error('NEGATIVE_FIXTURE_ACCEPTED_' + i);
  }
  return { positive:1, negative:bad.length };
}
module.exports = { transform, selfTest };
if (require.main === module) {
  const fs = require('node:fs');
  const path = require('node:path');
  if (process.argv.length === 3 && process.argv[2] === '--self-test') {
    console.log(JSON.stringify(selfTest()));
  } else {
    const args = process.argv.slice(2);
    if (args.length !== 4 || args[0] !== '--input' || args[2] !== '--output') {
      throw Error('USAGE: --input <local WordPress editor export> --output <new local candidate>');
    }
    const input = path.resolve(args[1]), output = path.resolve(args[3]);
    if (input === output || /^https?:/.test(args[1]) || /^https?:/.test(args[3])) {
      throw Error('REFUSE_IN_PLACE_OR_REMOTE_MUTATION');
    }
    const proposal = transform(fs.readFileSync(input,'utf8'));
    fs.writeFileSync(output, proposal.content, {encoding:'utf8',flag:'wx'});
    console.log(JSON.stringify({status:'LOCAL_PROPOSAL_ONLY',inserted:proposal.inserted,
      static_hash_navigation:proposal.fiveLinksResolvedInStaticMarkup,production_modified:false}));
  }
}
