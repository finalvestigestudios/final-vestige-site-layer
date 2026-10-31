'use strict';
/*
 * The Dispatch R28: independent cross-surface release-integrity validator.
 * Pure, deterministic, read-only; no network, WordPress API, email, PII, file I/O
 * or affiliate link activation. Inputs are untrusted copies of source files.
 * Returns findings, never an authorization to publish or send.
 */
function words(s) {
  return String(s).normalize('NFKC')
    .replace(/&(?:amp|#38);/gi, '&').replace(/&(?:quot|#34);/gi,'"')
    .replace(/&(?:apos|#39|#x27);/gi,"'").replace(/&(?:nbsp|#160);/gi,' ')
    .replace(/&(?:lt|#60);/gi,'<').replace(/&(?:gt|#62);/gi,'>')
    .replace(/[\u2018\u2019]/g,"'").replace(/[\u201C\u201D]/g,'"')
    .replace(/https?:\/\/[^\s<>)]*/g,' ').replace(/[^\p{L}\p{N}]+/gu,' ')
    .toLowerCase().trim().replace(/\s+/g,' ');
}
function markupText(s) {
  return words(String(s).replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ')
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ')
    .replace(/<!--[^]*?-->/g,' ').replace(/<[^>]*>/g,' '));
}
function markdownText(s) {
  return words(String(s).replace(/\[([^\]\n]+)\]\(https:\/\/[^\s)]+\)/g,'$1')
    .replace(/[*_`#>|]/g,' '));
}
function normalizedSnippets(body) {
  const paragraphs=String(body).split(/\n\s*\n/)
    .filter(s=>s.trim() && !s.trim().startsWith('- ') && !s.includes('[['))
    .map(markdownText).filter(s=>s.split(' ').length>=18);
  if(paragraphs.length<3)return [];
  const indexes=[0,Math.floor(paragraphs.length/2),paragraphs.length-1];
  return indexes.map(i=>paragraphs[i].split(' ').slice(0,11).join(' '));
}
function auditCampaign(data) {
  const failures=[],checks=[],warnings=[];
  function ok(id,pass,why) { checks.push({id,pass:!!pass});if(!pass)failures.push({id,why}); }
  function warn(id,why){warnings.push({id,why});}
  const m=data.manifest;
  ok('campaign-manifest',!!m&&m.status==='DRAFT_UNSENT_NO_SCHEDULING'&&
    m.mix?.editorial===4&&m.mix?.commercial_review_pending===2&&m.issues?.length===6,
    'Require existing six-issue 4 editorial/2 commercial unsent manifest.');
  if(!m||!Array.isArray(m.issues)||m.issues.length!==6)
    return {status:'INVALID_HOLD',passed:checks.filter(x=>x.pass).length,checked:checks.length,failures,warnings,editions:[]};
  const ledger=data.ledger?.editions??data.ledger?.candidates??[];
  ok('six-ledger-rows',ledger.length===6,'Six release attestations required.');
  const board=String(data.board??'');
  ok('review-board-is-unsent',/NOT.*(WORDPRESS|SEND|EMAIL)|HOLD.*UNSENT/i.test(board)
     &&!/READY TO SEND/i.test(board), 'Review board must warn it is NOT a delivered email.');
  const editions=[];
  for(let i=0;i<6;i++){
    const issue=m.issues[i], n=i+1, tag='I'+String(n).padStart(2,'0');
    const source=String(data.issues?.[i]??''),html=String(data.previews_html?.[i]??''),
      plain=String(data.previews_txt?.[i]??''),blocks=String(data.gutenberg?.[i]??'');
    const commercial=n===3||n===5;
    const matches=source.split(/\n---\n/);
    const body=matches.length>=3?matches[1]:'';
    const sourceText=markdownText(body);
    const sourceLink=issue.editorial_cta;
    const sourceUrls=[...body.matchAll(/https:\/\/[^\s)]+/g)].map(x=>x[0]);
    const proposedTitle=String(issue.subject??'');
    const proposedPreview=String(issue.preheader??'');
    ok(tag+'-sequence',issue.number===n&&issue.publish_state==='hold'&&issue.merchant_affiliate_url==null,
      'Issue numbering/status may not change.');
    ok(tag+'-classification',(issue.kind==='commercial-review-pending')===commercial,
      'Only 03 and 05 may have commercial placements.');
    ok(tag+'-metadata',source.includes('**Subject:** '+proposedTitle)&&
      source.includes('**Preheader:** '+proposedPreview)&&
      html.includes(proposedTitle)&&html.includes(proposedPreview)&&
      plain.includes('Subject: '+proposedTitle)&&plain.includes('Preheader: '+proposedPreview),
      'Email subject/preheader drifted across source and offline previews.');
    ok(tag+'-body-boundaries',body.length>500&&
      source.includes('UNSENT DRAFT')&&/Pre-send compliance block/.test(source),
      'Editor boundaries/draft safeguards are required.');
    ok(tag+'-review-assertion',board.includes(proposedTitle)&&
      blocks.includes('DO NOT PUBLISH OR EMAIL')&&plain.includes('DO NOT SEND')&&
      /NOT A SENT EMAIL/i.test(html),
      'Offline reviewer signals or Gutenberg hard hold are missing.');
    ok(tag+'-legal-hold',source.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')&&
      source.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')&&
      plain.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')&&
      plain.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'),
      'Unverified commercial legal/footer state must stay explicit.');
    const snippets=normalizedSnippets(body);
    const observed=[markupText(html),words(plain),markupText(blocks)];
    ok(tag+'-opening-middle-closing',snippets.length===3&&
      snippets.every(t=>observed.every(out=>out.includes(t))),
      'Material body paragraphs must survive HTML/plaintext/Gutenberg conversion.');
    ok(tag+'-source-links',sourceUrls.every(url=>html.includes(url)&&plain.includes(url)&&blocks.includes(url)),
      'All cited primary/public links must survive each conversion.');
    ok(tag+'-no-live-affiliate',![source,html,plain,blocks].some(v=>
      /(?:hop\.clickbank\.net|clickbank\.net\/|affiliates\.inspire3\.com|subid=|aff_id=)/i.test(v)),
      'No earning/tracking URL can enter any review asset.');
    if(commercial){
      ok(tag+'-disabled-guide',/^\[\[APPROVED_[A-Z0-9_]+_URL_REQUIRED\]\]$/.test(sourceLink)&&
        source.includes(sourceLink)&&plain.includes(sourceLink)&&
        /GUIDE NOT LIVE[^<\n]*/.test(blocks)&&
        html.includes('UNVERIFIED:')&&!html.includes('href="'+sourceLink+'"'),
        'Commercial warm-up CTA must be visibly disabled in all surfaces.');
      ok(tag+'-near-cta-disclosure',/Commercial disclosure:/.test(body)&&
        /may (earn|receive) a commission/i.test(body)&&
        /Commercial disclosure:/.test(plain)&&/Commercial disclosure:/.test(html)&&/Commercial disclosure:/.test(blocks),
        'Relevant commission disclosure must survive conversion.');
      ok(tag+'-claim-boundaries',/seller claims?|seller.*advertis|vendor claims?|zen12 also claims|hypnosis live.*claims?/i.test(body)&&
        /not independently|not verified|not establish/i.test(body),
        'Seller product assertions must not become independent effectiveness claims.');
    } else {
      ok(tag+'-live-editorial-cta',/^https:\/\/finalvestige\.com\//.test(sourceLink)&&
        source.includes(sourceLink)&&html.includes(sourceLink)&&plain.includes(sourceLink)&&
        blocks.includes('href="'+sourceLink+'"'),
        'Editorial CTA must be one published, approved Final Vestige route.');
    }
    const att=ledger.find(x=>x.issue===n);
    ok(tag+'-release-ledger',!!att&&(att.release_ready===false||att.ready_to_send===false)&&
      att.send_to_subscribers===false&&
      (att.primary_cta??att.editorial_cta)===sourceLink,
      'Preexisting release ledger must preserve false send permissions and CTAs.');
    if(proposedTitle.length>65)warn(tag+'-subject-length', 'Mobile display may clip this subject ('+proposedTitle.length+' characters).');
    if(proposedPreview.length>100)warn(tag+'-preheader-length','Preheader may clip in mobile inboxes.');
    editions.push({issue:n,kind:issue.kind,subject:proposedTitle,subject_characters:proposedTitle.length,
      preheader:proposedPreview,primary_cta:commercial?'DISABLED_PENDING_GUIDE':sourceLink,
      source_links:sourceUrls.length,delivery_mode:'LIVE_GLOBAL_EXCERPT',
      preheader_native_jetpack:'NOT_VERIFIED',native_email:'NOT_RECEIVED',
      postal:'NOT_VERIFIED',unsubscribe:'NOT_VERIFIED',affiliate_permission:commercial?'NOT_VERIFIED':'N/A',
      status:commercial?'HOLD_UNSENT_AND_MERCHANT':'HOLD_UNSENT'});
  }
  return {status:failures.length?'INVALID_HOLD':'SOURCE_SURFACES_PASS_RELEASE_HOLD',
    passed:checks.filter(x=>x.pass).length,checked:checks.length,
    failures,warnings,editions,
    note:'These tests establish only source/offline content parity, NOT Jetpack received email, live links, merchant approval, legality, delivery or permission to send.'};
}
module.exports={auditCampaign,words,markupText,markdownText,normalizedSnippets};