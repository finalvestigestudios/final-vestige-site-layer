<?php
/**
 * Plugin Name: FV Apollo Evidence Landing — isolated Experience 2.0 prototype
 * Description: One source-led landing entry to the Apollo 1 evidence experience. Not production authorized.
 * Version: 0.0.1-research
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/** Build a single, noncommercial editorial path without JavaScript or embedded NASA media. */
function fv_apollo_r347_landing_shortcode($atts = array()): string {
    static $instance = 0;
    $instance++;
    $id = 'fv-apollo-r347-' . $instance;
    $e = static function ($s): string { return htmlspecialchars((string) $s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); };
    $chronology = dirname(__DIR__) . '/apollo-r339/chronology-rail.php';
    if (is_readable($chronology)) { require_once $chronology; }
    $file = dirname(__DIR__) . '/apollo-r340/apollo-accession-gallery.php';
    if (is_readable($file)) { require_once $file; }
    if (!function_exists('fv_apollo_r339_shortcode') || !function_exists('fv_apollo_r340_gallery_shortcode')) {
        // Fail open to the established free investigation, without an empty interactive shell.
        return '<p>NASA evidence experience unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
    }
    $plate_file = dirname(__DIR__) . '/apollo-r345/evidence-plate.php';
    if (is_readable($plate_file)) { require_once $plate_file; }
    if (!function_exists('fv_apollo_r345_evidence_plate')) {
        return '<p>NASA evidence experience unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
    }
    ob_start(); ?>
<article class="fv-apollo-r347" aria-labelledby="<?php echo $e($id); ?>-title" data-fv-apollo-r347="source-led-landing">
  <header class="fv-apollo-r347__header">
    <p class="fv-apollo-r347__kicker">FINAL VESTIGE STUDIOS / EVIDENCE EXPERIENCE</p>
    <h2 id="<?php echo $e($id); ?>-title">Apollo 1: what can the record prove?</h2>
    <p class="fv-apollo-r347__deck">A fire during a ground test claimed three astronauts on January 27, 1967. NASA's Review Board judged an electrical arc the most probable initiator, but could not establish one definitive ignition source.</p>
    <p class="fv-apollo-r347__proof"><strong>Source first:</strong> <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/" rel="noopener noreferrer" data-fv-r347-proof="1967-board">Read NASA's Apollo 204 Review Board report</a>. Later histories and archive photographs are labeled separately; an archive link is not commercial-media clearance.</p>
    <nav aria-label="Apollo 1 evidence sections" class="fv-apollo-r347__jump"><ol>
      <li><a href="#<?php echo $e($id); ?>-timeline"><span>01</span> Recorded sequence</a></li>
      <li><a href="#<?php echo $e($id); ?>-findings"><span>02</span> Findings and limits</a></li>
      <li><a href="#<?php echo $e($id); ?>-archive"><span>03</span> Contextual archive</a></li>
    </ol></nav>
    <p class="fv-apollo-r347__guide">Start with the sequence, inspect each claim's source, then continue to the free investigation. There is no reconstructed fire animation, speculative map or purchase request.</p>
  </header>
  <section id="<?php echo $e($id); ?>-timeline" aria-label="Documentary chronology" class="fv-apollo-r347__section" tabindex="-1">
    <?php echo fv_apollo_r339_shortcode(); ?>
  </section>
  <section id="<?php echo $e($id); ?>-findings" aria-label="Original Review Board findings" class="fv-apollo-r347__section" tabindex="-1">
    <?php echo fv_apollo_r345_evidence_plate(); ?>
  </section>
  <section id="<?php echo $e($id); ?>-archive" aria-label="Contextual NASA photo-accession links" class="fv-apollo-r347__section" tabindex="-1">
    <?php echo fv_apollo_r340_gallery_shortcode(); ?>
  </section>
</article>
<?php return (string) ob_get_clean();
}

/** Bounded, read-only shortcode discovery before wp_head; detects direct and core/block reuse. */
function fv_apollo_r347_in_content(string $content, array &$seen = array(), int $depth = 0): bool {
    if (strlen($content) > 500000) { return false; }
    if (function_exists('has_shortcode') ? has_shortcode($content, 'fv_apollo_evidence_landing_r347') : strpos($content, '[fv_apollo_evidence_landing_r347') !== false) { return true; }
    if ($depth >= 5 || !function_exists('parse_blocks')) { return false; }
    $walk = function (array $blocks) use (&$walk, &$seen, $depth): bool {
        foreach ($blocks as $block) {
            if (!is_array($block)) { continue; }
            if (($block['blockName'] ?? '') === 'core/block') {
                $ref = (int) ($block['attrs']['ref'] ?? 0);
                if ($ref > 0 && !isset($seen[$ref]) && count($seen) < 24 && function_exists('get_post')) {
                    $seen[$ref] = true;
                    $post = get_post($ref);
                    if (is_object($post) && ($post->post_type ?? '') === 'wp_block' && fv_apollo_r347_in_content((string) ($post->post_content ?? ''), $seen, $depth + 1)) { return true; }
                }
            }
            if (isset($block['innerBlocks']) && is_array($block['innerBlocks']) && $walk($block['innerBlocks'])) { return true; }
        }
        return false;
    };
    return $walk(parse_blocks($content));
}
function fv_apollo_r347_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post') || !function_exists('wp_enqueue_style')) { return; }
    $post = get_post();
    if (!is_object($post) || !isset($post->post_content)) { return; }
    $seen = array();
    if (!fv_apollo_r347_in_content((string) $post->post_content, $seen)) { return; }
    $assets = array(
        array('fv-apollo-r347-landing', 'assets/apollo-evidence-landing.css'),
        array('fv-apollo-r339-chronology', '../apollo-r339/assets/chronology-rail.css'),
        array('fv-apollo-r345-evidence-plate', '../apollo-r345/evidence-plate.css'),
        array('fv-apollo-r340-gallery', '../apollo-r340/assets/accession-gallery.css'),
    );
    foreach ($assets as $asset) {
        if (is_readable(__DIR__ . '/' . $asset[1])) {
            wp_enqueue_style($asset[0], plugins_url($asset[1], __FILE__), array(), '0.0.1-research');
        }
    }
}
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_evidence_landing_r347', 'fv_apollo_r347_landing_shortcode'); }
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_apollo_r347_enqueue', 20); }
