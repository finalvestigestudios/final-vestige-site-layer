<?php
/**
 * Apollo Experience 2.0 R362 — Research Desk source custody crosswalk.
 * Research / staging only. No WP writes, analytics, commerce, external requests or media.
 * Keeps the original 1967 Board separate from 2018 NASA retrospective.
 * This is NOT a modification of independent Research Desk PR #158.
 */
if (!defined('ABSPATH')) { exit; }
foreach (array(
    dirname(__DIR__) . '/apollo-r360/rights-audit.php',
    dirname(__DIR__) . '/apollo-r345/evidence-plate.php',
    dirname(__DIR__) . '/apollo-r355/postfire-ledger.php',
) as $file) { if (is_readable($file)) { require_once $file; } }

/** No new editorial factual copies: derive every finding from reviewed ancestor data. */
function fv_apollo_r362_rows(): array {
    if (!function_exists('fv_apollo_r345_claims') || !function_exists('fv_apollo_r355_record')) { return array(); }
    $claims = fv_apollo_r345_claims();
    $post = fv_apollo_r355_record();
    if (count($claims) !== 3 || !function_exists('fv_apollo_r350_integrity_ok')
        || !fv_apollo_r350_integrity_ok() || !function_exists('fv_apollo_r355_source_is_reviewed')
        || !fv_apollo_r355_source_is_reviewed($post)) { return array(); }
    $result = array();
    foreach ($claims as $i => $claim) {
        if (!isset($claim['question'],$claim['finding'],$claim['limit'],$claim['source'],$claim['locator'])
            || $claim['tier'] !== 'original-board'
            || $claim['source'] !== 'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html') { return array(); }
        $result[] = array(
            'kind'=>'Original 1967 Board finding', 'label'=>$claim['question'], 'finding'=>$claim['finding'],
            'boundary'=>$claim['limit'], 'url'=>$claim['source'], 'source_label'=>$claim['locator'],
            'source_key'=>'board', 'period'=>'April 1967 Board report',
        );
    }
    if (($post['source'] ?? null) !== 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/') { return array(); }
    $result[] = array(
        'kind'=>'Later NASA engineering-test retrospective',
        'label'=>$post['heading'],
        'finding'=>$post['count'] . ' on ' . $post['vehicle'] . ' (' . $post['date'] . '). ' . $post['scope'],
        'boundary'=>$post['boundary'], 'url'=>$post['source'],
        'source_label'=>'NASA 2018 — Apollo Flammability Tests', 'source_key'=>'postfire',
        'period'=>'2018 retrospective of tests after the fire',
    );
    return $result;
}
/** Permit only the exact reviewed NASA institutional record; never borrow a source URL. */
function fv_apollo_r362_link_allowed(array $row): bool {
    if (!function_exists('fv_apollo_r360_manifest') || !function_exists('fv_apollo_r360_link_allowed')) { return false; }
    foreach (fv_apollo_r360_manifest() as $original) {
        if (($original['url'] ?? '') !== ($row['url'] ?? '') ||
            ($original['class'] ?? '') !== (($row['source_key'] ?? '') === 'postfire' ? 'later-test' : 'board')) { continue; }
        return fv_apollo_r360_link_allowed($original);
    }
    return false;
}
function fv_apollo_r362_shortcode($atts = array()): string {
    static $instance = 0; ++$instance;
    $id = 'fv-apollo-r362-' . $instance;
    $e = static function($s): string { return htmlspecialchars((string)$s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); };
    $rows = fv_apollo_r362_rows();
    if (count($rows) !== 4) {
        return '<p data-fv-r362-unavailable="true">The research crosswalk is temporarily unavailable. The free <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Apollo 1 investigation</a> remains accessible.</p>';
    }
    ob_start(); ?>
<section class="fv-apollo-r362" aria-labelledby="<?php echo $e($id); ?>-title" data-fv-r362-crosswalk>
 <div class="fv-apollo-r362__inner">
  <p class="fv-apollo-r362__kicker">RESEARCH DESK / EVIDENCE-TO-CLAIM CROSSWALK</p>
  <h2 id="<?php echo $e($id); ?>-title">What was known. What was tested later.</h2>
  <p class="fv-apollo-r362__intro">Four documentary questions, two different record periods. The original Apollo 204 Review Board reached findings in 1967. NASA's later history describes deliberate flammability tests of redesigned spacecraft. These records should not be presented as one continuous body of evidence.</p>
  <ol class="fv-apollo-r362__grid">
   <?php foreach ($rows as $i=>$row): $rid=$id.'-item-'.($i+1); $allowed=fv_apollo_r362_link_allowed($row); ?>
   <li class="fv-apollo-r362__card" data-fv-r362-period="<?php echo $e($row['source_key']); ?>">
    <article aria-labelledby="<?php echo $e($rid); ?>-title">
     <p class="fv-apollo-r362__type"><?php echo $e($row['kind']); ?></p>
     <h3 id="<?php echo $e($rid); ?>-title"><?php echo $e($row['label']); ?></h3>
     <p><strong>What the record supports.</strong> <?php echo $e($row['finding']); ?></p>
     <p class="fv-apollo-r362__boundary"><strong>What it does not establish.</strong> <?php echo $e($row['boundary']); ?></p>
     <details class="fv-apollo-r362__details" data-fv-r362-details>
      <summary>Inspect source and date for <?php echo $e($row['label']); ?></summary>
      <p><strong>Document period:</strong> <?php echo $e($row['period']); ?></p>
      <p><strong>Rights:</strong> Link to the institutional source only. NASA photographs, emblems, likenesses and third-party media are NOT cleared for FV commercial reuse.</p>
      <?php if ($allowed): ?><p><a href="<?php echo $e($row['url']); ?>" rel="noopener noreferrer" data-fv-r362-reviewed-source>Open NASA source: <?php echo $e($row['source_label']); ?></a></p>
      <?php else: ?><p data-fv-source-review-required="true">NASA source link withheld because documentary custody verification failed.</p><?php endif; ?>
     </details>
     <div class="fv-apollo-r362__print-source" hidden aria-hidden="true">
      <p><strong>Document period:</strong> <?php echo $e($row['period']); ?></p>
      <p><strong>Evidence boundary:</strong> <?php echo $e($row['boundary']); ?></p>
      <p><strong>Commercial media rights:</strong> NOT CLEARED / LINK ONLY.</p>
      <?php if ($allowed): ?><p><a href="<?php echo $e($row['url']); ?>">NASA original: <?php echo $e($row['source_label']); ?></a></p><?php endif; ?>
     </div>
    </article>
   </li>
   <?php endforeach; ?>
  </ol>
  <p class="fv-apollo-r362__note">The exact initiating arc was not conclusively established. This is not a recreated fire animation, geo-map or licensed media exhibit. The primary-source trail is free to inspect and no product purchase is required.</p>
  <p class="fv-apollo-r362__next"><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/" data-fv-r362-editorial-cta>Read the free Apollo 1 investigation</a></p>
 </div>
</section>
<?php return (string)ob_get_clean();
}
function fv_apollo_r362_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post')
        || !function_exists('has_shortcode') || !function_exists('wp_enqueue_style')
        || !function_exists('plugins_url')) { return; }
    $post = get_post();
    if (!is_object($post) || !isset($post->post_content) || !is_string($post->post_content)
        || !has_shortcode($post->post_content, 'fv_apollo_research_crosswalk_r362')) { return; }
    if (is_readable(__DIR__ . '/assets/research-crosswalk.css')) {
        wp_enqueue_style('fv-apollo-r362-crosswalk', plugins_url('assets/research-crosswalk.css', __FILE__), array(), '0.0.1-research');
    }
}
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_research_crosswalk_r362','fv_apollo_r362_shortcode'); }
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_apollo_r362_enqueue',22); }
