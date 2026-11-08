'use strict';
// Offline, fail-closed WordPress Gutenberg text-only patch evaluator.
// NEVER calls the WordPress API or sends any email. Founder approval required before deployment.
function count(text, needle) { return text.split(needle).length - 1; }
function patch(page, spec) {
  if (!page || page.id !== spec.id || page.slug !== spec.slug || page.modified !== spec.modified)
    throw new Error('SOURCE_VERSION_OR_PAGE_MISMATCH');
  if (typeof page.content !== 'string' || count(page.content,spec.before)!==1)
    throw new Error('SOURCE_ANCHOR_NOT_UNIQUE');
  if (page.content.includes(spec.after)) throw new Error('ALREADY_PATCHED');
  const next=page.content.replace(spec.before,spec.after);
  if (next.replace(spec.after,spec.before)!==page.content) throw new Error('UNRELATED_CONTENT_CHANGED');
  for(const marker of ['<!-- wp:jetpack/subscriptions','href=','<script','<!-- wp:html','data-fv-event']) {
    if(count(next,marker)!==count(page.content,marker)) throw new Error('SITE_STRUCTURE_CHANGED_'+marker);
  }
  if(spec.slug==='dispatch') {
    const pos=next.indexOf(spec.after),form=next.indexOf('<!-- wp:jetpack/subscriptions');
    if(pos<0||form<0||pos>form||form-pos>850||!next.includes('may earn Final Vestige Studios a commission'))
      throw new Error('DISCLOSURE_NOT_NEAR_SIGNUP');
  }
  if(spec.slug==='focus') {
    if(!next.includes('You do not need to sign up again.')||next.includes(spec.before))
      throw new Error('REPEAT_SIGNUP_NOT_CORRECTED');
  }
  return next;
}
module.exports={patch,count};
