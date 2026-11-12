/*
 * Final Vestige #2151 — read-only, editor-local preview inspector.
 * Run only on an authenticated FRONTEND PREVIEW of WordPress draft #2151.
 * Paste into DevTools Console at responsive widths 390px, then 1440px.
 * Save sanitized console output plus manual screenshots. Does not read cookies,
 * preview URLs, credentials, localStorage or tokens, or write/fetch/upload data.
 * Current article revision (2026-11-11 20:42 Pacific): 81 blocks, 42 sources,
 * SHA-1 b52d0225d81c99239c4e2336789999ceebfea858 (must be independently checked).
 * A console PASS is NOT a Gutenberg SHA check, visual review or publication gate.
 */
(async () => {
  'use strict';
  const EXPECTED = { title: 'The Levee They Blew on Purpose', photos: 4,
    bibliography: 42, headings: 11, tableRows: 10, chronologyCards: 5,
    chronologyLinks: 4 };
  const MEDIA = {
    '2148': ['NOAA'], '2255': ['Library of Congress', 'LOC'],
    '2202': ['Library of Congress', 'LOC'],
    '2149': ['Library of Congress', 'LOC', 'National Photo Company']
  };
  const scrollBefore = window.scrollY;
  const article = document.querySelector('article');
  const h1 = document.querySelector('h1');
  if (!article || !h1 || !h1.textContent.includes(EXPECTED.title)) {
    console.error('FV QA: STOP — not the expected article frontend preview.');
    return;
  }
  const imgs = [...article.querySelectorAll('figure.wp-block-image img')];
  const imageReports = [];
  for (const img of imgs) {
    img.scrollIntoView({block: 'center', behavior: 'instant'});
    try { await img.decode(); } catch (_e) { /* unloaded image is a FAIL */ }
    const fig = img.closest('figure');
    const id = (img.className.match(/wp-image-(\d+)/) || [])[1] || null;
    const src = img.currentSrc || img.src || '';
    let local = false;
    try {
      const u = new URL(src);
      const domain = u.hostname.toLowerCase();
      local = u.protocol === 'https:' && (
        ((domain === 'finalvestige.com' || domain === 'www.finalvestige.com') &&
          u.pathname.startsWith('/wp-content/uploads/')) ||
        (/^i[012]\.wp\.com$/.test(domain) &&
          /^\/(www\.)?finalvestige\.com\/wp-content\/uploads\//.test(u.pathname))
      );
    } catch (_e) { /* malformed URL is a FAIL */ }
    const caption = fig?.querySelector('figcaption')?.textContent || '';
    const rect = img.getBoundingClientRect();
    const expectedCredits = MEDIA[id] || [];
    imageReports.push({ mediaId: id, altPresent: !!img.getAttribute('alt')?.trim(),
      loaded: img.complete && img.naturalWidth > 0, localSource: local,
      captionPresent: !!caption.trim(),
      creditPresent: expectedCredits.some(c => caption.toLowerCase().includes(c.toLowerCase())),
      onScreenSize: rect.width > 40 && rect.height > 20 });
  }
  window.scrollTo({top: scrollBefore, behavior: 'instant'});
  const sourceHeading = article.querySelector('h2#sources');
  let sourceList = sourceHeading?.nextElementSibling || null;
  while (sourceList && sourceList.tagName !== 'UL') sourceList = sourceList.nextElementSibling;
  const sources = sourceList ? sourceList.querySelectorAll(':scope > li').length : 0;
  const timeline = article.querySelector('figure.fv-caernarvon-timeline');
  const timelineCards = timeline ? [...timeline.querySelectorAll('ol > li')] : [];
  const tlRect = timeline?.getBoundingClientRect();
  const tlText = timeline?.textContent || '';
  const tlDescriptionFonts = timelineCards.map(el => el.querySelector('span:last-child'))
    .filter(Boolean).map(el => parseFloat(getComputedStyle(el).fontSize));
  const timelineReport = {
    cards: timelineCards.length,
    sourceLinks: timeline?.querySelectorAll('figcaption a[href]').length || 0,
    accessibleName: !!timeline?.getAttribute('aria-label') && timeline?.getAttribute('role') === 'group',
    distinguishesMeasurements: tlText.includes('Neither number is a direct measurement') &&
      tlText.includes('Different methods and reference conditions'),
    fitViewport: !tlRect || (tlRect.left >= -2 && tlRect.right <= innerWidth + 2),
    clippedCards: timelineCards.some(el => el.scrollWidth > el.clientWidth + 2),
    minimumDescriptionFontPx: tlDescriptionFonts.length ? Math.min(...tlDescriptionFonts) : 0,
    captionFontPx: timeline?.querySelector('figcaption') ?
      parseFloat(getComputedStyle(timeline.querySelector('figcaption')).fontSize) : 0
  };
  const table = article.querySelector('figure table');
  const tableFig = table?.closest('figure');
  const tableStyles = tableFig ? getComputedStyle(tableFig) : null;
  const tableReport = {
    rows: table?.rows.length || 0,
    focusable: !!tableFig?.hasAttribute('tabindex'),
    labelled: !!tableFig?.getAttribute('aria-label'),
    overflowX: tableStyles?.overflowX || '',
    innerScrollWidth: tableFig?.scrollWidth || 0,
    innerClientWidth: tableFig?.clientWidth || 0
  };
  const bodyText = article.textContent || '';
  const sentinels = ['2:17 p.m.', '$1,096,796.53', 'Bohemia Spillway',
    'Acosta v.', '1991', 'May 9, 1927', '$3,387,000', 'Graham v. Jones'];
  const missingSentinels = sentinels.filter(t => !bodyText.includes(t));
  const brokenAnchors = [...article.querySelectorAll('a[href^="#"]')].filter(a => {
    const target = a.getAttribute('href')?.slice(1);
    if (!target) return false;
    try { return !document.getElementById(decodeURIComponent(target)); }
    catch (_e) { return true; }
  }).length;
  const width = document.documentElement.clientWidth;
  const photoIds = imageReports.map(p => p.mediaId).sort();
  const imageExpected = Object.keys(MEDIA).sort().join(',') === photoIds.join(',');
  const allImagesOk = imageExpected && imageReports.length === EXPECTED.photos &&
    imageReports.every(p => p.altPresent && p.loaded && p.localSource &&
      p.creditPresent && p.onScreenSize);
  const checks = {
    expected_title: true,
    correct_four_locally_hosted_credited_images: allImagesOk,
    exactly_42_bibliography_entries: sources === EXPECTED.bibliography,
    eleven_h2_sections: article.querySelectorAll('h2').length === EXPECTED.headings,
    evidence_table_ten_rows: tableReport.rows === EXPECTED.tableRows,
    internal_anchors_resolve: brokenAnchors === 0,
    no_page_wide_overflow: document.documentElement.scrollWidth <= width + 2,
    responsive_table_accessible: !!(tableReport.focusable && tableReport.labelled &&
      (width > 500 || (['auto','scroll'].includes(tableReport.overflowX) &&
      tableReport.innerScrollWidth > tableReport.innerClientWidth))),
    chronology_complete: !!(timeline && timelineReport.cards === EXPECTED.chronologyCards &&
      timelineReport.sourceLinks === EXPECTED.chronologyLinks && timelineReport.accessibleName),
    chronology_cautions_present: timelineReport.distinguishesMeasurements,
    chronology_readable: !!(timeline && timelineReport.fitViewport &&
      !timelineReport.clippedCards && timelineReport.minimumDescriptionFontPx >= 14 &&
      timelineReport.captionFontPx >= 14),
    revision_sentinels_present: missingSentinels.length === 0,
    header_and_footer_present: !!document.querySelector('header') && !!document.querySelector('footer')
  };
  const result = {
    inspector: 'FV #2151 console QA v1 (read-only)',
    dateUtc: new Date().toISOString(), viewportPx: width, outerViewportPx: innerWidth,
    allAutomatedChecksPassed: Object.values(checks).every(Boolean),
    checks, evidence: { imageReports, sourceCount: sources, timelineReport,
      tableReport, brokenAnchors, missingSentinels,
      pageOverflowPx: document.documentElement.scrollWidth - width },
    manualGatesRemain: [
      'Verify this is WP #2151 in editor; separately compare fresh Gutenberg SHA.',
      'Inspect screenshots of actual 390px and 1440px production-theme PREVIEW.',
      'Inspect main navigation, signup overlay, byline, images, chart and footer by eye.',
      'Open both USACE brochures and both USGS reports as anonymous reader.',
      'Do not publish from this script alone; publication belongs to Investigations.'
    ]
  };
  console.log('FV QA (no credentials/URLs included in report):');
  console.log(JSON.stringify(result, null, 2));
  return result;
})();