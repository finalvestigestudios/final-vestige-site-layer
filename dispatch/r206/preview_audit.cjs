'use strict';
// Offline audit: previews are NOT send-ready, and this code never contacts subscribers.
function audit(manifest,records){
  const issues=manifest.issues||[],failures=[],warnings=[],checks={};
  if(issues.length!==6)failures.push('MIX_SIX');
  if(issues.filter(x=>x.kind==='editorial').length!==4)failures.push('MIX_EDITORIAL');
  if(issues.filter(x=>x.kind.includes('commercial')).length!==2)failures.push('MIX_COMMERCIAL');
  for(const issue of issues){
    const key=String(issue.number).padStart(2,'0')+'-'+issue.slug;
    const r=records[key]||{},html=r.html||'',txt=r.txt||'',source=r.source||'';
    const rules={
      subject:source.includes('**Subject:** '+issue.subject)&&html.includes(issue.subject)&&txt.includes('Subject: '+issue.subject),
      preheader:source.includes('**Preheader:** '+issue.preheader)&&html.includes(issue.preheader)&&txt.includes('Preheader: '+issue.preheader),
      original_source_hold:source.includes('STATUS: UNSENT DRAFT'),
      offline_hold:html.includes('UNSENT')&&txt.includes('UNSENT')&&html.includes('HOLD'),
      postal_stop:html.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')&&txt.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]'),
      unsubscribe_stop:html.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')&&txt.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'),
      accessible_structure:html.includes('<html lang="en">')&&html.includes('<h1 ')&&html.includes('role="presentation"'),
      no_active_content:!/<script\b|<iframe\b|<img\b|<form\b/i.test(html),
      no_merchant_click:!/<a\s[^>]*href="https?:\/\/(?:www\.)?(?:zen12|hypnosislive|affiliates\.inspire3)/i.test(html),
      no_placeholder_click:!/<a[^>]*href="\[\[/i.test(html),
      no_unapproved_price:!/\$\s*(?:17\.95|24\.44|87\.99)/.test(html),
      no_external_analytics:!/(google-analytics|gtag|fbq|pixel\.facebook|analytics\.ahrefs)/i.test(html)
    };
    if(issue.kind.includes('commercial')){
      rules.commercial_disclosure=html.includes('Commercial disclosure:')&&txt.includes('Commercial disclosure:');
      rules.unpublished_guide=html.includes('WARMUP_GUIDE_URL_REQUIRED')&&txt.includes('WARMUP_GUIDE_URL_REQUIRED');
      rules.permission_hold=html.includes('EMAIL')&&html.includes('unverified');
    }
    for(const [rule,passed] of Object.entries(rules)){checks[key+':'+rule]=passed;if(!passed)failures.push(key+':'+rule);}
    if(issue.number===6&&issue.editorial_cta?.endsWith('/focus/'))warnings.push('06: redundant signup destination for existing subscribers; optional R205 alternate NOT approved');
    if(issue.number===1||issue.number===2)warnings.push(key+': overlapping Puységur destination; verify intent and editorial sequence');
  }
  return {ok:failures.length===0,failures,warnings,tests:Object.keys(checks).length,passed:Object.values(checks).filter(Boolean).length,release:'HOLD_UNSENT',commercial_release:'HOLD_MERCHANT',metrics:'NOT_COMPUTABLE'};
}
module.exports={audit};