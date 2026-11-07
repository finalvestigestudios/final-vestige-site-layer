<?php
/**
 * Plugin Name: FV EX2 Isolated Browser Evidence Receipt
 * Description: Review-only local WordPress Playground viewport/evidence report; NOT a release or accessibility certification.
 * Version: 0.2.0
 * License: Internal non-production review only.
 */
if (!defined('ABSPATH')) { exit; }
if (get_option('fv_ex2_playground_review_only', '') !== 'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1') { return; }
add_action('wp_footer', static function () {
    if (!is_page('fv-ex2-review')) { return; }
    ?>
    <aside id="fv-ex2-receipt" aria-label="Isolated WordPress review evidence" style="margin:2rem auto;max-width:65rem;padding:1.5rem;background:#142323;color:#f0e5d2;border:2px solid #c2a371;overflow-wrap:anywhere;font:16px/1.5 system-ui,sans-serif">
      <h2 style="color:#e7c88a;font:normal 1.6rem Georgia,serif">Isolated Playground · browser evidence</h2>
      <p><strong>Private review only.</strong> This produces a local machine-readable receipt of visible WordPress page structure and image decoding. It does not send information anywhere, create subscribers, measure actual sales, or approve release. Disable JavaScript separately to assess no-JS content. Lighthouse, axe, real image bytes and WordPress.com-hosted behavior require independent testing.</p>
      <p style="display:flex;flex-wrap:wrap;gap:.75rem"><button type="button" id="fv-ex2-run" style="padding:.9rem 1rem;min-height:44px;background:#d4ad73;color:#111;border:1px solid #d4ad73;font:700 1rem system-ui;cursor:pointer">Capture this viewport</button> <button type="button" id="fv-ex2-download" disabled style="padding:.9rem 1rem;min-height:44px;background:#d4ad73;color:#111;border:1px solid #d4ad73;font:700 1rem system-ui;cursor:pointer">Download JSON receipt</button></p>
      <p role="status" aria-live="polite" id="fv-ex2-receipt-status">Not run — no qualification asserted.</p>
      <pre id="fv-ex2-receipt-output" tabindex="0" style="overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;max-height:20rem;font-size:12px"></pre>
    </aside>
    <script id="fv-ex2-receipt-local-script">
    (() => {
      'use strict';
      const holder = document.getElementById('fv-ex2-receipt');
      if (!holder || !document.querySelector('[data-fv-home-flagship]')) return;
      const runButton = document.getElementById('fv-ex2-run');
      const downloadButton = document.getElementById('fv-ex2-download');
      const status = document.getElementById('fv-ex2-receipt-status');
      const output = document.getElementById('fv-ex2-receipt-output');
      let current = null;
      const chapterIds = ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
      const safeImage = img => {
        const raw = img.currentSrc || ''; // Browser selection, NEVER substitute declared src
        let origin = '', path = '';
        try { const parsed = new URL(raw, document.baseURI); origin = parsed.origin; path = parsed.pathname; }
        catch (_) { origin = 'INVALID'; }
        const entries = performance.getEntriesByName(raw, 'resource');
        const perf = entries.length ? entries[entries.length - 1] : null;
        return {browser_selected_origin:origin, browser_selected_path:path, selected_url_resolved: Boolean(raw), declared_src:img.getAttribute('src'), loaded: Boolean(img.complete && img.naturalWidth > 0),
          width: img.naturalWidth || 0, height: img.naturalHeight || 0,
          resource_timing_entry: Boolean(perf), transfer_bytes: 'UNVERIFIED_CROSS_ORIGIN',
          declared_alt_present: Boolean((img.getAttribute('alt') || '').trim())};
      };
      // Capture first-screen CTA geometry from scroll position 0, independent of
      // the reviewer's location at the bottom of this very long page. A brief
      // local scroll is restored; this code never follows or clicks an offer.
      const inspectFirstScreenFocus = focus => {
        const previousScrollY = window.scrollY;
        const previousScrollX = window.scrollX;
        const previousBehavior = document.documentElement.style.scrollBehavior;
        const observations = [];
        try {
          document.documentElement.style.scrollBehavior = 'auto';
          window.scrollTo(0, 0);
          for (const a of focus) {
            const r = a.getBoundingClientRect();
            const style = getComputedStyle(a);
            const visible = r.width >= 24 && r.height >= 24 &&
              r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth &&
              style.display !== 'none' && style.visibility !== 'hidden' &&
              Number(style.opacity) > 0 && style.pointerEvents !== 'none';
            // Inset the hit-testing coordinates so narrow decorative borders
            // cannot create false negatives. A child of the anchor is a hit.
            const x = Math.min(innerWidth - 1, Math.max(0, r.left + r.width / 2));
            const y = Math.min(innerHeight - 1, Math.max(0, r.top + Math.min(r.height / 2, 22)));
            const hit = visible ? document.elementFromPoint(x, y) : null;
            const clickable = Boolean(visible && hit && (a === hit || a.contains(hit)));
            observations.push({visible_in_first_screen: Boolean(visible), pointer_hit_test_pass: clickable,
              rect_css_px:{x:Math.round(r.left),y:Math.round(r.top),width:Math.round(r.width),height:Math.round(r.height)},
              visible_label:(a.textContent || '').trim().slice(0,90)});
          }
        } finally {
          window.scrollTo(previousScrollX, previousScrollY);
          document.documentElement.style.scrollBehavior = previousBehavior;
        }
        return observations;
      };
      const capture = () => {
        const root = document.querySelector('[data-fv-home-flagship]');
        const wpShell = Boolean(document.querySelector('.wp-site-blocks'));
        const focus = [...root.querySelectorAll('a')].filter(a => {
          try { const u = new URL(a.href, document.baseURI); return u.hostname === 'finalvestige.com' && u.pathname === '/focus/'; }
          catch (_) { return false; }
        });
        const chapters = chapterIds.map(id => ({id, present: Boolean(document.getElementById(id))}));
        const images = [...root.querySelectorAll('img[data-fv-archive-img]')].map(safeImage);
        const margins = root.querySelectorAll('.fv-margin-strip__item').length;
        const documentOverflow = Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth);
        const focusBounds = focus.map(a => {const r = a.getBoundingClientRect(); return {height_css_px:Math.round(r.height*100)/100, width_css_px:Math.round(r.width*100)/100};});
        const firstScreenFocus = inspectFirstScreenFocus(focus);
        const blockers = [];
        if (!wpShell) blockers.push('NOT_WORDPRESS_SHELL');
        if (chapters.some(x=>!x.present)) blockers.push('MISSING_CHAPTER');
        if (margins !== 72) blockers.push('MARGINS_NOT_72');
        if (focus.length !== 5) blockers.push('FOCUS_LINKS_NOT_5');
        if (images.length !== 2) blockers.push('ARCHIVAL_IMAGES_NOT_2');
        if (images.some(x => !['https://finalvestige.com','https://i0.wp.com'].includes(x.browser_selected_origin) || !x.declared_alt_present)) blockers.push('ARCHIVAL_PROVENANCE_OR_ALT');
        if (images.some(x => !x.selected_url_resolved)) blockers.push('ARCHIVAL_SELECTED_URL_UNRESOLVED');
        if (images.some(x => !x.loaded)) blockers.push('ARCHIVAL_IMAGE_NOT_DECODED_MAY_BE_LAZY');
        if (documentOverflow > 1) blockers.push('HORIZONTAL_OVERFLOW');
        if (focusBounds.some(x => x.height_css_px < 24 || x.width_css_px < 24)) blockers.push('FOCUS_TARGET_UNDERSIZED');
        if (!firstScreenFocus.some(x => x.pointer_hit_test_pass && x.rect_css_px.height >= 44)) blockers.push('NO_USABLE_FIRST_SCREEN_FOCUS_ACTION');
        if (firstScreenFocus.some(x => x.visible_in_first_screen && !x.pointer_hit_test_pass)) blockers.push('FOCUS_FIRST_SCREEN_POINTER_OCCLUDED');
        const data = {kind:'FV_EX2_LOCAL_BROWSER_RECEIPT_V1', release_authorized:false,
          assessment:blockers.length ? 'LOCAL_VIEWPORT_BLOCKED' : 'LOCAL_VIEWPORT_STRUCTURAL_PASS_ONLY',
          environment:'ISOLATED_WORDPRESS_PLAYGROUND_EXPECTED_NOT_WPCOM_PRODUCTION',
          generated_utc:new Date().toISOString(),
          viewport_css_px:{width:innerWidth,height:innerHeight},pixel_ratio:devicePixelRatio,
          prefers_reduced_motion:matchMedia('(prefers-reduced-motion: reduce)').matches,
          wp_shell_observed:wpShell,chapters,margins_count:margins,focus_destinations:focus.length,
          focus_button_dimensions:focusBounds,first_screen_focus_hit_tests:firstScreenFocus,
          image_observations:images,horizontal_overflow_css_px:documentOverflow,
          blockers,not_qualified:['actual_response_bytes','axe_WCAG_2_2_AA','Lighthouse_CWV','keyboard_and_touch_parity','no_JS','Jetpack_signup','paid_orders','verified_net_revenue','WordPress_com_host_parity'],
          privacy:'NO_NETWORK_TRANSMISSION_OR_PERSISTENT_STORAGE_BY_RECEIPT_CODE',
          first_screen_test_scope:'DOM hit-test only; not an actual conversion or mobile-user usability study'};
        return data;
      };
      runButton.addEventListener('click',() => {
        try {current=capture();output.textContent=JSON.stringify(current,null,2);status.textContent=current.assessment+' — this is NOT release approval.';downloadButton.disabled=false;}
        catch(e){current=null;downloadButton.disabled=true;status.textContent='BLOCKED: local receipt failed; no review approval.';output.textContent=String(e);}
      });
      downloadButton.addEventListener('click',() => {
        if (!current) return;
        const blob = new Blob([JSON.stringify(current,null,2)+'\n'],{type:'application/json'});
        const url=URL.createObjectURL(blob);
        const a=document.createElement('a');a.href=url;a.download='fv-ex2-isolated-browser-receipt.json';document.body.appendChild(a);a.click();a.remove();
        setTimeout(()=>URL.revokeObjectURL(url),1000);
      });
    })();
    </script>
    <?php
}, 1000);
