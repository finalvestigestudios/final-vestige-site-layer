<?php
/**
 * Plugin Name: Final Vestige Apollo Evidence Review Truth (Staging Candidate)
 * Description: Isolated source-status clarification; no production permission or writes.
 * Version: 0.0.1-r444
 * Requires PHP: 7.4
 */
const FV_R444_SOURCE_SHA256 = 'a940d2e6d8c685219f3dccc0e0cc984e97d999948c81fc7379c09634f3e60004';
const FV_R444_CSS_SHA256 = '682d8985fb13779bcb0156dd28322b07cdcc3330ae8e6cb19ebf031c26a52385';
const FV_R444_JS_SHA256 = 'f6f4d52e8f0b435d196cbfd81e94da6a4e02e9b817eb6ea6efe6e8fd26374af5';
const FV_R444_INVESTIGATION = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
function fv_r444_escape($value): string {
    return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function fv_r444_fallback(): string {
    return '<p class="fv-r444-fallback">The research preview is unavailable. <a href="'.fv_r444_escape(FV_R444_INVESTIGATION).'">Read the full Apollo 1 investigation</a>.</p>';
}
function fv_r444_sources(): ?array {
    $path = __DIR__ . '/source_manifest.json';
    if (!is_readable($path) || !hash_equals(FV_R444_SOURCE_SHA256, (string)hash_file('sha256', $path))) return null;
    $data = json_decode((string)file_get_contents($path), true);
    if (!is_array($data) || ($data['schema'] ?? null) !== 'fv-apollo-review-custody-v1'
        || ($data['editorial_signoff'] ?? null) !== 'PENDING_INDEPENDENT_QD'
        || count($data['records'] ?? []) !== 5) return null;
    $ids=[];
    $board='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
    $later='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
    foreach($data['records'] as $record){
        if (!is_array($record) || !in_array($record['url'] ?? '', [$board,$later], true)
            || !in_array($record['period'] ?? '', ['original','later'],true)
            || !preg_match('/^a[1-5]$/D', (string)($record['id'] ?? ''))
            || !isset($record['title'],$record['finding'],$record['limit'],$record['source'],$record['date_label'])) return null;
        $ids[]=$record['id'];
    }
    if (count(array_unique($ids)) !== 5) return null;
    return $data;
}
/** Pure render, no environment writes. Per-instance namespace prevents duplicate ID collisions. */
function fv_r444_render(): string {
    $data=fv_r444_sources();
    if($data===null) return fv_r444_fallback();
    static $instance=0; $instance++;
    $id='fv-r444-'.$instance;
    ob_start();
    ?>
<section class="fv-r444" data-r444-root aria-labelledby="<?php echo fv_r444_escape($id); ?>-heading">
  <p class="fv-r444__eyebrow">FINAL VESTIGE STUDIOS · APOLLO 1 / EVIDENCE CUSTODY</p>
  <h2 id="<?php echo fv_r444_escape($id); ?>-heading">What the documents establish—and what remains open</h2>
  <p>These links identify NASA source documents. That is not the same as an independent approval of every historical claim, or clearance to sell NASA imagery.</p>
  <div class="fv-r444__states" aria-label="Three separate review states">
    <div class="fv-r444__state"><strong>Source identity: checked</strong><p>Official NASA source addresses reviewed November 17, 2026. A source URL check is not a historical editorial signoff.</p></div>
    <div class="fv-r444__state"><strong>Historical interpretation: review pending</strong><p>Independent editorial/QD approval has not been recorded. Claims retain explicit boundaries below.</p></div>
    <div class="fv-r444__state"><strong>Commercial image rights: not cleared</strong><p>No photographs, emblems or archival media are reproduced here. NASA is not a sponsor or endorser.</p></div>
  </div>
  <div class="fv-r444__filter" data-r444-controls hidden aria-label="Filter by historical source period">
    <button type="button" data-r444-filter="all" aria-pressed="true">All five</button>
    <button type="button" data-r444-filter="original" aria-pressed="false">1967 findings</button>
    <button type="button" data-r444-filter="later" aria-pressed="false">Later account</button>
    <span class="fv-r444__count" data-r444-count role="status" aria-live="polite"></span>
  </div>
  <div class="fv-r444__records" aria-label="Five curated documentary findings">
  <?php foreach($data['records'] as $n=>$record): ?>
    <article class="fv-r444__record" data-r444-record data-r444-period="<?php echo fv_r444_escape($record['period']); ?>" aria-labelledby="<?php echo fv_r444_escape($id.'-'.$record['id']); ?>">
      <p class="fv-r444__date"><?php echo fv_r444_escape($record['date_label']); ?></p>
      <p class="fv-r444__kind"><?php echo fv_r444_escape($record['type']); ?> · Evidence <?php echo $n+1; ?> / 5</p>
      <h3 id="<?php echo fv_r444_escape($id.'-'.$record['id']); ?>"><?php echo fv_r444_escape($record['title']); ?></h3>
      <p class="fv-r444__claim"><?php echo fv_r444_escape($record['finding']); ?></p>
      <details><summary>Source and limits</summary>
        <p class="fv-r444__boundary"><strong>What this does not prove:</strong> <?php echo fv_r444_escape($record['limit']); ?></p>
        <p><a href="<?php echo fv_r444_escape($record['url']); ?>">Read NASA source: <?php echo fv_r444_escape($record['source']); ?></a></p>
      </details>
    </article>
  <?php endforeach; ?>
  </div>
  <div class="fv-r444__next"><p><strong>Next step:</strong> Follow the evidence into the complete investigation. Reading is free.</p>
    <p><a href="<?php echo fv_r444_escape(FV_R444_INVESTIGATION); ?>">Read the full Apollo 1 investigation</a></p>
    <p class="fv-r444__disclosure">This research preview is not a NASA publication or a commercial product. No buyer checkout, subscriber collection, behavioral tracking, or geographic mapping is present.</p>
  </div>
</section>
    <?php
    return (string)ob_get_clean();
}
/** Optional isolated WordPress shortcode. Assets are enqueued only by shortcode invocation. */
if (defined('ABSPATH') && function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_review_trail', function(){
        $css=__DIR__.'/assets/review-panel.css'; $js=__DIR__.'/assets/review-panel.js';
        if (!is_readable($css) || !hash_equals(FV_R444_CSS_SHA256,(string)hash_file('sha256',$css))
            || !is_readable($js) || !hash_equals(FV_R444_JS_SHA256,(string)hash_file('sha256',$js))) return fv_r444_fallback();
        if (function_exists('wp_enqueue_style')) wp_enqueue_style('fv-r444-review',plugins_url('assets/review-panel.css',__FILE__),[], '0.0.1-r444');
        if (function_exists('wp_enqueue_script')) wp_enqueue_script('fv-r444-review',plugins_url('assets/review-panel.js',__FILE__),[], '0.0.1-r444',true);
        return fv_r444_render();
    });
}
