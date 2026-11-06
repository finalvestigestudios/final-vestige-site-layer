#!/usr/bin/env node
/**
 * Final Vestige EX2 / Focus destination no-JavaScript continuity QA.
 * READ-ONLY, NON-PRODUCTION. Takes a locally saved, public rendered content fragment.
 * This is a source audit, not a full-page browser or a verified Jetpack signup.
 * Use: node verify_focus_nojs_funnel.cjs path/to/focus-rendered.html
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');

function decodeEntities(value) {
  return value.replace(/&#0*38;|&#x0*26;|&amp;/gi, '&');
}
function attrs(tag) {
  const o = Object.create(null);
  for (const match of tag.matchAll(/([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g)) {
    o[match[1].toLowerCase()] = decodeEntities(match[2] ?? match[3] ?? '');
  }
  return o;
}
function anchorTags(markup) {
  return [...markup.matchAll(/<a\b[^>]*>/gi)].map(match => ({...attrs(match[0]), raw:match[0]}));
}
function elementById(markup,id) {
  return [...markup.matchAll(/<([a-z][a-z0-9-]*)\b[^>]*>/gi)]
    .find(m => attrs(m[0]).id === id)?.[0] || null;
}
function hasVisibleFallback(markup) {
  // Walk ancestor tags so a <noscript> PDF nested in an inert/hidden container
  // does not create a false accessibility PASS. This is an HTML fragment check,
  // not a replacement for browser computed styles or the theme DOM.
  const stack = [];
  const voidTags = new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);
  for (const m of markup.matchAll(/<\/?[a-z][^>]*>/gi)) {
    const token=m[0], closing=/^<\//.test(token);
    const name=token.match(/^<\/?([a-z][\w:-]*)/i)?.[1]?.toLowerCase();
    if (!name) continue;
    if (closing) {
      for(let j=stack.length-1;j>=0;j--){if(stack[j].name===name){stack.splice(j);break;}}
      continue;
    }
    const at=attrs(token);
    const hidden=Object.prototype.hasOwnProperty.call(at,'hidden') ||
      /\bhidden(?:\s|=|>)/i.test(token) ||
      at['aria-hidden']==='true' ||
      /(?:display\s*:\s*none|visibility\s*:\s*hidden)/i.test(at.style||'');
    if (name==='a' && /\.pdf(?:[?#]|$)/i.test(at.href||'') &&
        stack.some(n=>n.name==='noscript') &&
        !stack.some(n=>n.hidden)) return true;
    if(!voidTags.has(name) && !/\/>$/.test(token)) stack.push({name,hidden});
  }
  return false;
}

function inspect(markup) {
  const flags=[];
  const hasJetpackBlock=/class=["'][^"']*wp-block-jetpack-subscriptions/.test(markup);
  if (!hasJetpackBlock) flags.push('NO_JETPACK_SUBSCRIPTION_BLOCK_IN_RENDERED_CONTENT');
  if (!elementById(markup,'subscribe-blog')) flags.push('NO_SIGNUP_HEADING_ANCHOR');
  const buttons=anchorTags(markup).filter(a => /(?:post_type=page|#subscribe-blog)/.test(a.href||''));
  const selfLinks=buttons.filter(a => {
    try { const u=new URL(a.href,'https://finalvestige.com/focus/');
      return u.hostname==='finalvestige.com' &&
        (u.pathname==='/focus/' || (u.searchParams.get('post_type')==='page' && u.searchParams.get('p')==='1579'));
    } catch {return false;}
  });
  const formCount=(markup.match(/<form\b/gi)||[]).length;
  const noJsPdfFallback=hasVisibleFallback(markup);
  // A control which merely navigates to the exact same page does not, by itself,
  // demonstrate a functioning no-JS subscription workflow.
  if (selfLinks.length && formCount===0 && !noJsPdfFallback) flags.push('SELF_LINKING_SUBSCRIBE_CONTROL_HAS_NO_NOJS_FALLBACK_IN_CONTENT');
  if (!formCount && !noJsPdfFallback) flags.push('NO_NATIVE_FORM_OR_ACCESSIBLE_NOJS_PDF_FALLBACK_IN_CONTENT');
  if (!/52.page/i.test(markup.replace(/<[^>]*>/g,' '))) flags.push('FIELDBOOK_52_PAGE_PROMISE_NOT_FOUND');
  const result={kind:'fv-focus-rendered-content-nojs-audit',scope:'WordPress page-content fragment only',
    qualified_for_release:false, may_prove_live_signup:false, form_count:formCount,
    jetpack_block:hasJetpackBlock, self_link_subscription_controls:selfLinks.length,
    no_js_pdf_fallback:noJsPdfFallback, flags, conclusion:flags.length?'REQUIRES_FULL_BROWSER_TEST_AND_NOJS_REMEDIATION_REVIEW':'SOURCE_ONLY_PASS_BROWSER_STILL_REQUIRED'};
  return result;
}
if (require.main===module) {
  const file=process.argv[2];
  if (!file || process.argv.length!==3 || !fs.existsSync(file)) { console.error('Usage: node verify_focus_nojs_funnel.cjs public-focus-rendered.html');process.exit(64); }
  const input=fs.readFileSync(path.resolve(file),'utf8');
  if (input.length<100) { console.error('HOLD: rendered content too short');process.exit(2); }
  const report=inspect(input);console.log(JSON.stringify(report,null,2));
  if (report.flags.length) process.exit(2);
}
module.exports={inspect,attrs,decodeEntities};
