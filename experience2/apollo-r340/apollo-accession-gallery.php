<?php
/**
 * Plugin Name: FV Apollo 1 Source Gallery Bridge — Research Only
 * Description: Isolated no-JS source-custody gallery and R339 chronology integration. NOT authorized for installation.
 * Version: 0.0.1-research
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
$fv_apollo_r349_policy = dirname(__DIR__) . '/apollo-r349/source-policy.php';
if (is_readable($fv_apollo_r349_policy)) { require_once $fv_apollo_r349_policy; }


/** NASA source pages only. Accessions are context, never proof of ignition or blanket commercial permission. */
function fv_apollo_r340_accessions(): array {
    return array(
        array('id' => 'S67-15717', 'title' => 'Spacecraft 012 preparation', 'context' => 'NASA archive record of command-module preparation before the fire.', 'limit' => 'A pre-incident image cannot establish where the fire began.', 'url' => 'https://www.nasa.gov/image-detail/amf-s67-15717/'),
        array('id' => 'S66-58038', 'title' => 'Altitude test context', 'context' => 'NASA image record of Apollo/Saturn 204 astronaut training and testing.', 'limit' => 'This testing photograph is not a sensor record of the January 27 emergency.', 'url' => 'https://www.nasa.gov/image-detail/amf-s66-58038/'),
        array('id' => 'S67-21294', 'title' => 'Fire investigation context', 'context' => 'NASA accession for a photograph of Command Module 012 associated with the fire.', 'limit' => 'An image record alone cannot conclusively identify an electrical initiator.', 'url' => 'https://www.nasa.gov/image-detail/amf-s67-21294/'),
        array('id' => 'KSC-20170124-PH_KLS01_0090', 'title' => 'Later Apollo 1 tribute', 'context' => 'NASA archival page for a later Apollo 1 tribute photograph.', 'limit' => 'Commemorative imagery is not contemporaneous evidence of spacecraft conditions.', 'url' => 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/'),
    );
}

function fv_apollo_r340_gallery_shortcode($atts = array()): string {
    static $instance = 0;
    $instance++;
    $heading_id = 'fv-apollo-r340-gallery-' . $instance;
    $escape = function ($text): string { return htmlspecialchars((string) $text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); };
    ob_start();
    ?>
<section class="fv-apollo-r340" aria-labelledby="<?php echo $escape($heading_id); ?>" data-fv-r340-gallery>
  <div class="fv-apollo-r340__inner">
    <p class="fv-apollo-r340__kicker">APOLLO 1 / NASA ARCHIVE ACCESSIONS</p>
    <h2 id="<?php echo $escape($heading_id); ?>">Four records. Four boundaries.</h2>
    <p class="fv-apollo-r340__intro">A link-only research gallery: open original NASA archive pages to inspect photographs and their descriptions. The images are not embedded, cropped, downloaded or licensed for Final Vestige merchandise. An image accession is not a Review Board conclusion.</p>
    <ol class="fv-apollo-r340__grid">
    <?php foreach (fv_apollo_r340_accessions() as $record): ?>
      <li class="fv-apollo-r340__card" data-fv-r340-rights="review-required" data-fv-r340-role="contextual-photo-only">
        <p class="fv-apollo-r340__id">NASA / <?php echo $escape($record['id']); ?></p>
        <h3><?php echo $escape($record['title']); ?></h3>
        <p><?php echo $escape($record['context']); ?></p>
        <details><summary>Provenance and limits for <?php echo $escape($record['title']); ?></summary><p><?php echo $escape($record['limit']); ?></p><p>Source classification: contextual NASA photograph. Copyright, branding, likeness and commercial-context restrictions require individual review.</p></details>
        <p class="fv-apollo-r340__print-limit" data-fv-r340-print-limit hidden><strong>Photograph evidence limitation:</strong> <?php echo $escape($record['limit']); ?> <strong>Rights review required:</strong> A NASA accession link is not commercial image/likeness/branding clearance.</p>
        <?php echo function_exists('fv_apollo_r349_source_link') ? fv_apollo_r349_source_link($record['url'], 'Inspect NASA accession ' . $record['id'], array('data-fv-r340-source'=>'contextual-photo')) : '<span data-fv-source-review-required="true">Source link withheld pending verification</span>'; ?>
      </li>
    <?php endforeach; ?>
    </ol>
    <p class="fv-apollo-r340__rights">These links remain on NASA's website. No photograph is used as proof of the exact ignition point. The archive's public accessibility does not itself authorize endorsement, trademark use, identifiable-person merchandising or third-party rights.</p>
  </div>
</section>
    <?php
    return (string) ob_get_clean();
}

/** The chronology supplies the only editorial continuation CTA; gallery supplies none. */
function fv_apollo_r340_experience_shortcode($atts = array()): string {
    $chronology = dirname(__DIR__) . '/apollo-r339/chronology-rail.php';
    if (is_readable($chronology)) {
        require_once $chronology;
    }
    if (!function_exists('fv_apollo_r339_shortcode')) {
        return '<p>Research experience unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
    }
    $plate_file = dirname(__DIR__) . '/apollo-r345/evidence-plate.php';
    if (is_readable($plate_file)) { require_once $plate_file; }
    $plate = function_exists('fv_apollo_r345_evidence_plate') ? fv_apollo_r345_evidence_plate() : '';
    return fv_apollo_r339_shortcode() . $plate . fv_apollo_r340_gallery_shortcode();
}

/**
 * Resolve a bounded set of core/block reusable patterns before wp_head.
 * Do not render blocks or change WP content. Missing/malformed references fail closed
 * for optional styling; the shortcode itself still emits complete semantic HTML.
 * Explicitly does not claim detection in arbitrary dynamic/template-part renderers.
 * @return array{0: bool, 1: bool} composite / gallery-only shortcode flags
 */
function fv_apollo_r340_shortcode_flags(string $content, array &$seen = array(), int $depth = 0): array {
    $contains = function (string $tag) use ($content): bool {
        return function_exists('has_shortcode') ? has_shortcode($content, $tag) : strpos($content, '[' . $tag) !== false;
    };
    $flags = array($contains('fv_apollo_experience_r340'), $contains('fv_apollo_gallery_r340'));
    if (($flags[0] && $flags[1]) || $depth >= 5 || strlen($content) > 500000 || !function_exists('parse_blocks')) {
        return $flags;
    }
    $visit = function (array $blocks) use (&$visit, &$flags, &$seen, $depth): void {
        foreach ($blocks as $block) {
            if (!is_array($block)) { continue; }
            if (($block['blockName'] ?? '') === 'core/block') {
                $ref = (int) ($block['attrs']['ref'] ?? 0);
                if ($ref > 0 && !isset($seen[$ref]) && count($seen) < 24 && function_exists('get_post')) {
                    $seen[$ref] = true;
                    $referenced = get_post($ref);
                    if (is_object($referenced) && ($referenced->post_type ?? '') === 'wp_block') {
                        $nested = fv_apollo_r340_shortcode_flags((string) ($referenced->post_content ?? ''), $seen, $depth + 1);
                        $flags[0] = $flags[0] || $nested[0];
                        $flags[1] = $flags[1] || $nested[1];
                    }
                }
            }
            if (isset($block['innerBlocks']) && is_array($block['innerBlocks'])) {
                $visit($block['innerBlocks']);
            }
            if ($flags[0] && $flags[1]) { return; }
        }
    };
    $visit(parse_blocks($content));
    return $flags;
}

/** Enqueue scoped styles for direct and safely resolvable reusable-block references. */
function fv_apollo_r340_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post') || !function_exists('wp_enqueue_style')) { return; }
    $post = get_post();
    if (!$post || !isset($post->post_content)) { return; }
    $seen = array();
    $flags = fv_apollo_r340_shortcode_flags((string) $post->post_content, $seen);
    $combined = $flags[0];
    if (!$combined && !$flags[1]) { return; }
    if ($combined && is_readable(dirname(__DIR__) . '/apollo-r339/assets/chronology-rail.css')) {
        wp_enqueue_style('fv-apollo-r339-chronology', plugins_url('../apollo-r339/assets/chronology-rail.css', __FILE__), array(), '0.0.1-research');
    }
    if ($combined && is_readable(dirname(__DIR__) . '/apollo-r345/evidence-plate.css')) {
        wp_enqueue_style('fv-apollo-r345-evidence-plate', plugins_url('../apollo-r345/evidence-plate.css', __FILE__), array(), '0.0.1-research');
    }
    wp_enqueue_style('fv-apollo-r340-gallery', plugins_url('assets/accession-gallery.css', __FILE__), array(), '0.0.1-research');
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_gallery_r340', 'fv_apollo_r340_gallery_shortcode');
    add_shortcode('fv_apollo_experience_r340', 'fv_apollo_r340_experience_shortcode');
}
if (function_exists('add_action')) {
    add_action('wp_enqueue_scripts', 'fv_apollo_r340_enqueue', 20);
}
