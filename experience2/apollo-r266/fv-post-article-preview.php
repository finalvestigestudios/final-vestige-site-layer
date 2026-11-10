<?php
/**
 * Apollo R266 — UNPUBLISHED CLI-ONLY AFTER-ARTICLE REVIEW FIXTURE.
 * Not a WordPress plugin, no hooks, no shortcode, no automatic inclusion.
 * Does not output unless explicitly invoked in CLI with every approval flag.
 */
declare(strict_types=1);

function fv_apollo_r266_preview(array $gate): string {
    // A preview can never be activated by HTTP or by a partial / truthy string status.
    if (PHP_SAPI !== 'cli') return '';
    $required = [
        'staging_review' => true,
        'article_location_accepted' => true,
        'rights_review_recorded' => true,
        'offer_merchant_reviewed' => true,
        'founder_preview_permission' => true,
    ];
    foreach ($required as $key => $value) {
        if (!array_key_exists($key, $gate) || $gate[$key] !== $value) return '';
    }
    $guide = 'https://finalvestige.com/mini-museum-history-collectibles/';
    $title = 'A different kind of evidence';
    return '<aside class="fv-apollo-postscript" aria-labelledby="fv-apollo-postscript-title" data-release="REVIEW-ONLY">'
      . '<div class="fv-apollo-postscript__label">After the investigation · Optional collector’s guide</div>'
      . '<h2 id="fv-apollo-postscript-title">' . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . '</h2>'
      . '<p>The Apollo 1 record stands on its own. For readers interested in physical evidence, our separate Mini Museum buying guide explains what to check in a specimen’s documentation, size and seller policies. These items are not Apollo 1 artifacts.</p>'
      . '<p class="fv-apollo-postscript__disclosure"><strong>Affiliate disclosure:</strong> If you buy through an eligible retailer link in the guide, Final Vestige may receive a commission. The investigation and NASA’s source records are free. NASA does not endorse Final Vestige or the recommended retailer.</p>'
      . '<p><a class="fv-apollo-postscript__action" href="' . htmlspecialchars($guide, ENT_QUOTES, 'UTF-8') . '">Read the Mini Museum buying guide <span aria-hidden="true">↗</span></a></p>'
      . '<p class="fv-apollo-postscript__fineprint">Optional next reading · Merchant eligibility and paid conversion reporting remain unverified · Review fixture only, not published</p>'
      . '</aside>';
}
