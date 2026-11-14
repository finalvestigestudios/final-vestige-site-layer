<?php
/**
 * Apollo R360 — staging-only source/rights acceptance annex, NOT a license grant.
 * Read-only, no media, geospatial data, analytics, external requests or paid CTAs.
 * Use only in nonproduction editorial acceptance; main experience remains unchanged.
 */
if (!defined('ABSPATH')) { exit; }
$fv_r360_upstream = dirname(__DIR__) . '/apollo-r359/resolved-block-template-prehead.php';
if (is_readable($fv_r360_upstream)) { require_once $fv_r360_upstream; }
$fv_r360_integrity = dirname(__DIR__) . '/apollo-r350/integrity.php';
if (is_readable($fv_r360_integrity)) { require_once $fv_r360_integrity; }

/** Complete documentary classification is a separate gate from rights clearance. */
function fv_apollo_r360_manifest(): array {
    $records = array(
        array('board', '1967 Board findings', 'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html', 'Determination identifies probable electrical arc but does not establish a single ignition source.'),
        array('board', '1967 Board investigation', 'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html', 'Post-fire inspection is not a recording of the ignition moment.'),
        array('board', '1967 Board chronology', 'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/chro.html', 'Measured signals and inferred event times must remain distinct.'),
        array('later-history', 'NASA retrospective: aftermath', 'https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/', 'Written decades afterward; not a 1967 Board finding.'),
        array('photo', 'Photo S67-15717', 'https://www.nasa.gov/image-detail/amf-s67-15717/', 'Preincident context cannot show where the fire began.'),
        array('photo', 'Photo S66-58038', 'https://www.nasa.gov/image-detail/amf-s66-58038/', 'Training image is not a fire telemetry record.'),
        array('photo', 'Photo S67-21294', 'https://www.nasa.gov/image-detail/amf-s67-21294/', 'An archive accession does not identify a conclusive ignition point.'),
        array('photo', 'Photo KSC-20170124-PH_KLS01_0090', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/', 'A 2017 tribute is not contemporaneous accident evidence.'),
        array('later-test', '2018 NASA flammability retrospective', 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/', 'The 102 deliberate ignitions were post-fire 1967–1968 tests, not 1967 Board findings.'),
    );
    return array_map(static function($r): array {
        return array('class'=>$r[0], 'label'=>$r[1], 'url'=>$r[2], 'boundary'=>$r[3],
            'link_review'=>'official-page-checked-2026-11-14',
            'commercial_media_rights'=>'NOT_CLEARED_LINK_ONLY');
    }, $records);
}
/** Exact native policy for 8 1967/source-photo rows; separately pinned 2018 record. */
function fv_apollo_r360_link_allowed(array $row): bool {
    // Do not let a caller borrow an approved NASA URL for an unreviewed claim.
    $exact = false;
    foreach (fv_apollo_r360_manifest() as $reviewed) { if ($row === $reviewed) { $exact = true; break; } }
    if (!$exact) { return false; }
    $url = $row['url'] ?? null;
    if (!is_string($url) || strpos($url, 'https://www.nasa.gov/') !== 0) { return false; }
    $integrity = function_exists('fv_apollo_r350_integrity_ok') && fv_apollo_r350_integrity_ok();
    if (!$integrity) { return false; }
    if (($row['class'] ?? '') === 'later-test') {
        return function_exists('fv_apollo_r355_record') && function_exists('fv_apollo_r355_source_is_reviewed')
            && fv_apollo_r355_source_is_reviewed(fv_apollo_r355_record())
            && $url === fv_apollo_r355_record()['source'];
    }
    return function_exists('fv_apollo_r349_is_source_approved') && fv_apollo_r349_is_source_approved($url);
}
function fv_apollo_r360_rights_audit_shortcode($atts=array()): string {
    static $instances = 0; ++$instances;
    $prefix = 'fv-apollo-r360-' . $instances;
    $esc = static function($value): string { return htmlspecialchars((string)$value, ENT_QUOTES|ENT_SUBSTITUTE, 'UTF-8'); };
    $rows = fv_apollo_r360_manifest();
    ob_start(); ?>
<section class="fv-apollo-r360" data-fv-rights-annex aria-labelledby="<?php echo $esc($prefix); ?>-title">
 <h2 id="<?php echo $esc($prefix); ?>-title">Apollo 1 · documentary and rights acceptance</h2>
 <p><strong>Editorial audit only.</strong> Nine NASA-hosted record pages were individually checked on November 14, 2026. Source accessibility does not clear any photograph, logo, likeness or third-party material for a commercial product. This annex contains links only; no NASA photographs are embedded.</p>
 <ol>
 <?php foreach($rows as $i => $row): ?>
  <li data-fv-rights-class="<?php echo $esc($row['class']); ?>" data-fv-commercial-clearance="not-cleared">
   <h3><?php echo $esc($row['label']); ?></h3>
   <p><strong>Document class:</strong> <?php echo $esc($row['class']); ?> · <strong>Commercial media reuse:</strong> NOT CLEARED / LINK ONLY.</p>
   <p><strong>Evidence boundary:</strong> <?php echo $esc($row['boundary']); ?></p>
   <?php if (fv_apollo_r360_link_allowed($row)): ?>
   <p><a href="<?php echo $esc($row['url']); ?>" rel="noopener noreferrer" data-fv-rights-reviewed-link>Open NASA record — <?php echo $esc($row['label']); ?></a></p>
   <?php else: ?>
   <p data-fv-source-review-required="true">NASA record link withheld: reviewed claim/source pairing requires reverification.</p>
   <?php endif; ?>
  </li>
 <?php endforeach; ?>
 </ol>
 <p>No images are licensed or bundled. Do not convert these citations into commercial reuse, checkout, endorsement or archival map coordinates. The original free investigation remains available independently.</p>
</section>
<?php return (string)ob_get_clean();
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_rights_audit_r360', 'fv_apollo_r360_rights_audit_shortcode');
}
/** Load only when explicitly placed in singular post content; no global style injection. */
function fv_apollo_r360_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post')
        || !function_exists('has_shortcode') || !function_exists('wp_enqueue_style')
        || !function_exists('plugins_url')) { return; }
    $post=get_post();
    if (!is_object($post) || !isset($post->post_content)
        || !has_shortcode((string)$post->post_content, 'fv_apollo_rights_audit_r360')) { return; }
    $asset=__DIR__.'/assets/rights-audit.css';
    if (is_readable($asset)) {
        wp_enqueue_style('fv-apollo-r360-rights',plugins_url('assets/rights-audit.css',__FILE__),array(),'0.0.1-research');
    }
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_apollo_r360_enqueue',16); }
