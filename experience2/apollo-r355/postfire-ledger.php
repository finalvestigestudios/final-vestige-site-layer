<?php
/**
 * Apollo R355 / post-Board source custody — independent RESEARCH-ONLY shortcode.
 * No WP content writes, network calls, checkout, tracking or media embedding.
 */
if (!defined('ABSPATH')) { exit; }

function fv_apollo_r355_record(): array {
    return array(
        'heading' => 'The tests that came after the investigation',
        'date' => 'December 1967–February 1968',
        'count' => '102 deliberate ignitions',
        'vehicle' => 'Command Module Boilerplate 1224',
        'scope' => 'Three series of command-module flammability tests examined redesigned hardware and differing cabin atmospheres.',
        'boundary' => 'These tests happened after the January 1967 fire and after the original Review Board inquiry. They are not measurements from the accident, evidence of an exact ignition wire or proof that the redesign eliminated all risks.',
        'document_class' => 'Later NASA institutional retrospective, published February 14, 2018; not a 1967 Review Board document',
        'source' => 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
    );
}

/** Pinned editorial row identity, not a hash of an upstream NASA file or rights clearance. */
function fv_apollo_r355_source_is_reviewed(array $record): bool {
    $json = json_encode($record, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    return is_string($json) && hash_equals('0b1c83bad191ca57754f182945593a5caeebcc448025d1b438151ea4f80425bb', hash('sha256', $json));
}
function fv_apollo_r355_postfire_shortcode($atts = array()): string {
    static $instance = 0; ++$instance;
    $record = fv_apollo_r355_record();
    $approved = fv_apollo_r355_source_is_reviewed($record);
    $id = 'fv-apollo-r355-' . $instance;
    $e = static function($v): string { return htmlspecialchars((string)$v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); };
    ob_start(); ?>
<section class="fv-apollo-r355" aria-labelledby="<?php echo $e($id); ?>-heading" data-fv-apollo-postfire>
  <div class="fv-apollo-r355__inner">
    <p class="fv-apollo-r355__eyebrow">APOLLO 1 / POST-BOARD SOURCE CUSTODY</p>
    <h2 id="<?php echo $e($id); ?>-heading"><?php echo $e($record['heading']); ?></h2>
    <p class="fv-apollo-r355__lead">The original 1967 Review Board examined the fatal fire. A separate NASA program subsequently tested how redesigned spacecraft would behave when fire was deliberately introduced.</p>
    <div class="fv-apollo-r355__facts">
      <p><span>Test period</span><strong><?php echo $e($record['date']); ?></strong></p>
      <p><span>Documented scale</span><strong><?php echo $e($record['count']); ?></strong></p>
      <p><span>Test article</span><strong><?php echo $e($record['vehicle']); ?></strong></p>
    </div>
    <p><?php echo $e($record['scope']); ?></p>
    <p class="fv-apollo-r355__boundary"><strong>Evidence boundary.</strong> <?php echo $e($record['boundary']); ?></p>
    <details class="fv-apollo-r355__source">
      <summary>Inspect the later NASA source and its limits</summary>
      <p><strong>Document class:</strong> <?php echo $e($record['document_class']); ?></p>
      <?php if ($approved): ?>
      <p><a href="<?php echo $e($record['source']); ?>" rel="noopener noreferrer" data-fv-r355-reviewed-source>Read NASA's 2018 flammability-test history</a></p>
      <?php else: ?>
      <p data-fv-source-review-required="true">Link withheld: editorial source identity requires independent review.</p>
      <?php endif; ?>
      <p>The 2018 NASA account describes the test program; it is not a surviving 1967 test recording and does not authorize commercial reuse of NASA imagery, marks or portraits.</p>
    </details>
    <div class="fv-apollo-r355__print" hidden aria-hidden="true">
      <p><strong>Document class:</strong> <?php echo $e($record['document_class']); ?></p>
      <p><strong>Evidence boundary:</strong> <?php echo $e($record['boundary']); ?></p>
      <?php if ($approved): ?><p><strong>NASA source:</strong> <a href="<?php echo $e($record['source']); ?>">2018 flammability-test history</a></p><?php endif; ?>
    </div>
    <p class="fv-apollo-r355__note">No NASA photograph is embedded. No historical coordinates or causal connection to an exact ignition point is inferred. Research remains free.</p>
  </div>
</section>
<?php return (string)ob_get_clean();
}
/** The composite preserves exactly one existing free investigation CTA. */
function fv_apollo_r355_experience_shortcode($atts = array()): string {
    $parent = dirname(__DIR__) . '/apollo-r348/source-custody.php';
    if (is_readable($parent)) { require_once $parent; }
    if (!function_exists('fv_apollo_r348_experience_shortcode')) {
        return '<p>The source experience is unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
    }
    return fv_apollo_r348_experience_shortcode() . fv_apollo_r355_postfire_shortcode();
}
/** Read-only, bounded shortcode discovery; no recursive WP content changes. */
function fv_apollo_r355_in_content(string $content, array &$seen = array(), int $depth = 0): bool {
    $present = function_exists('has_shortcode')
        ? has_shortcode($content, 'fv_apollo_experience_r355') || has_shortcode($content, 'fv_apollo_postfire_r355')
        : strpos($content, '[fv_apollo_experience_r355') !== false || strpos($content, '[fv_apollo_postfire_r355') !== false;
    if ($present || $depth >= 5 || strlen($content) > 500000 || !function_exists('parse_blocks')) { return (bool)$present; }
    $walk = static function(array $blocks) use (&$walk, &$seen, $depth): bool {
        foreach ($blocks as $block) {
            if (!is_array($block)) { continue; }
            if (($block['blockName'] ?? '') === 'core/block' && function_exists('get_post')) {
                $ref = (int)($block['attrs']['ref'] ?? 0);
                if ($ref > 0 && !isset($seen[$ref]) && count($seen) < 24) {
                    $seen[$ref] = true; $post = get_post($ref);
                    if (is_object($post) && ($post->post_type ?? '') === 'wp_block' && fv_apollo_r355_in_content((string)($post->post_content ?? ''), $seen, $depth + 1)) { return true; }
                }
            }
            if (isset($block['innerBlocks']) && is_array($block['innerBlocks']) && $walk($block['innerBlocks'])) { return true; }
        }
        return false;
    };
    return $walk(parse_blocks($content));
}
function fv_apollo_r355_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post') || !function_exists('wp_enqueue_style')) { return; }
    $post = get_post(); if (!is_object($post) || !isset($post->post_content)) { return; }
    $seen = array(); if (!fv_apollo_r355_in_content((string)$post->post_content, $seen)) { return; }
    // Dependencies are enqueued conservatively for reusable-block compositions.
    $assets = array(
        array('fv-apollo-r339-chronology', '../apollo-r339/assets/chronology-rail.css'),
        array('fv-apollo-r340-gallery', '../apollo-r340/assets/accession-gallery.css'),
        array('fv-apollo-r345-evidence-plate', '../apollo-r345/evidence-plate.css'),
        array('fv-apollo-r347-index', '../apollo-r347/assets/source-index.css'),
        array('fv-apollo-r348-custody', '../apollo-r348/assets/source-custody.css'),
        array('fv-apollo-r355-postfire', 'postfire-ledger.css'),
    );
    foreach ($assets as $asset) {
        if (is_readable(__DIR__.'/'.$asset[1])) { wp_enqueue_style($asset[0], plugins_url($asset[1], __FILE__), array(), '0.0.1-research'); }
    }
    if (function_exists('wp_enqueue_script') && is_readable(dirname(__DIR__).'/apollo-r347/assets/source-index.js')) {
        wp_enqueue_script('fv-apollo-r347-index', plugins_url('../apollo-r347/assets/source-index.js',__FILE__),array(),'0.0.1-research',true);
    }
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_postfire_r355', 'fv_apollo_r355_postfire_shortcode');
    add_shortcode('fv_apollo_experience_r355', 'fv_apollo_r355_experience_shortcode');
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_apollo_r355_enqueue',17); }
