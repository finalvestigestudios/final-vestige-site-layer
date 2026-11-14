<?php
/**
 * Apollo R363: strict evidence-to-source custody, additive STAGING ONLY.
 * Unlike R362's URL/class-only gate, the COMPLETE reviewed claim must match.
 * Read-only shortcode; no publishing, remote requests, tracking, or commerce.
 */
if (!defined('ABSPATH')) { exit; }
foreach (array(
    dirname(__DIR__) . '/apollo-r360/rights-audit.php',
    dirname(__DIR__) . '/apollo-r345/evidence-plate.php',
    dirname(__DIR__) . '/apollo-r355/postfire-ledger.php',
) as $file) { if (is_readable($file)) { require_once $file; } }

/** Rebuild from already reviewed originals; never trust submitted row contents. */
function fv_apollo_r363_reviewed_rows(): array {
    if (!function_exists('fv_apollo_r350_integrity_ok') || !fv_apollo_r350_integrity_ok()
        || !function_exists('fv_apollo_r345_claims') || !function_exists('fv_apollo_r355_record')
        || !function_exists('fv_apollo_r355_source_is_reviewed')) { return array(); }
    $claims = fv_apollo_r345_claims();
    $post = fv_apollo_r355_record();
    $board = 'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html';
    $later = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
    if (count($claims) !== 3 || !fv_apollo_r355_source_is_reviewed($post)
        || ($post['source'] ?? null) !== $later || ($post['count'] ?? null) !== '102 deliberate ignitions') { return array(); }
    $rows = array();
    foreach ($claims as $claim) {
        if (!isset($claim['question'],$claim['finding'],$claim['limit'],$claim['source'],$claim['locator'],$claim['tier'])
            || $claim['tier'] !== 'original-board' || $claim['source'] !== $board) { return array(); }
        $rows[] = array('period'=>'Original 1967 Review Board', 'question'=>$claim['question'],
            'finding'=>$claim['finding'], 'limit'=>$claim['limit'], 'source'=>$board,
            'locator'=>$claim['locator'], 'class'=>'board');
    }
    $rows[] = array('period'=>'Later 2018 NASA retrospective', 'question'=>$post['heading'],
        'finding'=>$post['count'] . ' on ' . $post['vehicle'] . ' (' . $post['date'] . '). ' . $post['scope'],
        'limit'=>$post['boundary'], 'source'=>$later,
        'locator'=>'NASA, Apollo Flammability Tests (February 14, 2018)', 'class'=>'later-test');
    return $rows;
}
/** Full-array strict equality (including period, question, finding, evidence limit, locator).
 * A matching URL and source class alone NEVER authorize a source or the claim. */
function fv_apollo_r363_exact_review(array $candidate): bool {
    foreach (fv_apollo_r363_reviewed_rows() as $reviewed) {
        if ($candidate === $reviewed) { return true; }
    }
    return false;
}
function fv_apollo_r363_source_allowed(array $candidate): bool {
    if (!fv_apollo_r363_exact_review($candidate) || !function_exists('fv_apollo_r360_manifest')
        || !function_exists('fv_apollo_r360_link_allowed')) { return false; }
    foreach (fv_apollo_r360_manifest() as $record) {
        if (($record['url'] ?? null) === $candidate['source'] && ($record['class'] ?? null) === $candidate['class']) {
            return fv_apollo_r360_link_allowed($record);
        }
    }
    return false;
}
/** Rows arg is an explicit adversarial test seam, not a public shortcode attribute. */
function fv_apollo_r363_render_rows(array $rows): string {
    static $instance = 0; ++$instance;
    $id = 'fv-apollo-r363-' . $instance;
    $e = static fn($s): string => htmlspecialchars((string)$s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    ob_start(); ?>
<section class="fv-apollo-r362" data-fv-r363-custody aria-labelledby="<?php echo $e($id); ?>-title">
 <div class="fv-apollo-r362__inner">
  <p class="fv-apollo-r362__kicker">RESEARCH DESK · DOCUMENTARY CUSTODY</p>
  <h2 id="<?php echo $e($id); ?>-title">Original findings. Later engineering tests.</h2>
  <p class="fv-apollo-r362__intro">The 1967 Apollo 204 Review Board findings and the later NASA account of post-fire tests are distinct source periods. Inspect each claim, its limitation and its original record.</p>
  <ol class="fv-apollo-r362__grid">
  <?php foreach ($rows as $i => $row): ?>
   <li class="fv-apollo-r362__card" data-fv-r363-record>
   <?php if (!is_array($row) || !fv_apollo_r363_exact_review($row)): ?>
    <p data-fv-r363-withheld><strong>Evidence withheld:</strong> claim/source pairing no longer matches the reviewed record. Consult NASA originals and the free investigation independently.</p>
   <?php else: $rid=$id.'-row-'.($i+1); $linked=fv_apollo_r363_source_allowed($row); ?>
    <article aria-labelledby="<?php echo $e($rid); ?>-title">
     <p class="fv-apollo-r362__type"><?php echo $e($row['period']); ?></p>
     <h3 id="<?php echo $e($rid); ?>-title"><?php echo $e($row['question']); ?></h3>
     <p><strong>Supported:</strong> <?php echo $e($row['finding']); ?></p>
     <p class="fv-apollo-r362__boundary"><strong>Not established:</strong> <?php echo $e($row['limit']); ?></p>
     <details class="fv-apollo-r362__details" data-fv-r363-details>
      <summary>Inspect NASA source for <?php echo $e($row['question']); ?></summary>
      <p><strong>Source period:</strong> <?php echo $e($row['period']); ?></p>
      <p><strong>Media rights:</strong> Link only; photographs, third-party materials, emblems and likenesses not cleared for commercial reuse.</p>
      <?php if ($linked): ?><p><a data-fv-r363-source href="<?php echo $e($row['source']); ?>" rel="noopener noreferrer">Open NASA source for <?php echo $e($row['question']); ?></a></p>
      <?php else: ?><p data-fv-r363-source-unavailable>Source link withheld pending re-verification.</p><?php endif; ?>
     </details>
     <div class="fv-apollo-r362__print-source" hidden aria-hidden="true">
      <p><strong>Reviewed period:</strong> <?php echo $e($row['period']); ?></p>
      <p><strong>Commercial-media rights:</strong> NOT CLEARED — LINK ONLY.</p>
      <?php if ($linked): ?><p><a href="<?php echo $e($row['source']); ?>">NASA record: <?php echo $e($row['question']); ?></a></p><?php endif; ?>
     </div>
    </article>
   <?php endif; ?>
   </li>
  <?php endforeach; ?>
  </ol>
  <p class="fv-apollo-r362__note">The Board did not conclusively identify one exact ignition source. Later test counts are not original Board observations. No NASA photographs are embedded or licensed by this component.</p>
  <p class="fv-apollo-r362__next"><a data-fv-r363-editorial-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a></p>
 </div>
</section>
<?php return (string)ob_get_clean();
}
function fv_apollo_r363_shortcode($atts=array()): string {
    $rows = fv_apollo_r363_reviewed_rows();
    return count($rows) === 4 ? fv_apollo_r363_render_rows($rows)
        : fv_apollo_r363_render_rows(array(array('unverified'=>true)));
}
function fv_apollo_r363_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post')
        || !function_exists('has_shortcode') || !function_exists('wp_enqueue_style')
        || !function_exists('plugins_url')) { return; }
    $post = get_post();
    if (!is_object($post) || !isset($post->post_content) || !is_string($post->post_content)
        || !has_shortcode($post->post_content, 'fv_apollo_custody_guard_r363')) { return; }
    $file = dirname(__DIR__) . '/apollo-r362/assets/research-crosswalk.css';
    if (is_readable($file)) { wp_enqueue_style('fv-apollo-r362-crosswalk',
        plugins_url('../apollo-r362/assets/research-crosswalk.css', __FILE__), array(), '0.0.1-research'); }
}
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_custody_guard_r363','fv_apollo_r363_shortcode'); }
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_apollo_r363_enqueue',23); }
