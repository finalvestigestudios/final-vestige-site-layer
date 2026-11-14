<?php
/**
 * Plugin Name: FV Apollo Source Index R347 — Research Only
 * Description: Provenance-first curated evidence index; independent staging shortcode, not approved for installation.
 * Version: 0.0.1-research
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }
$fv_apollo_r349_policy = dirname(__DIR__) . '/apollo-r349/source-policy.php';
if (is_readable($fv_apollo_r349_policy)) { require_once $fv_apollo_r349_policy; }


/** Derive labels, limits, and URLs from the already-reviewed records, never maintain competing factual copies. */
function fv_apollo_r347_records(): array {
    foreach (array(
        dirname(__DIR__) . '/apollo-r339/chronology-rail.php',
        dirname(__DIR__) . '/apollo-r345/evidence-plate.php',
        dirname(__DIR__) . '/apollo-r340/apollo-accession-gallery.php',
    ) as $file) { if (is_readable($file)) { require_once $file; } }
    if (!function_exists('fv_apollo_r339_chronology') || !function_exists('fv_apollo_r345_claims') || !function_exists('fv_apollo_r340_accessions')) { return array(); }
    $result = array();
    foreach (fv_apollo_r345_claims() as $row) {
        $result[] = array('group'=>'findings', 'type'=>'Original 1967 Board finding', 'label'=>$row['question'], 'limit'=>$row['limit'], 'url'=>$row['source'], 'locator'=>$row['locator']);
    }
    foreach (fv_apollo_r339_chronology() as $row) {
        $later = $row['tier'] === 'later-history';
        $result[] = array('group'=>$later?'later':'chronology', 'type'=>$later?'Later NASA institutional history':'Original 1967 Board analysis', 'label'=>$row['event'], 'limit'=>$row['boundary'], 'url'=>$row['source'], 'locator'=>$row['source_label']);
    }
    foreach (fv_apollo_r340_accessions() as $row) {
        $result[] = array('group'=>'photos', 'type'=>'Contextual NASA photograph', 'label'=>$row['id'].' — '.$row['title'], 'limit'=>$row['limit'], 'url'=>$row['url'], 'locator'=>'NASA accession '.$row['id']);
    }
    return $result;
}

function fv_apollo_r347_index_shortcode($atts = array()): string {
    static $instance = 0; ++$instance;
    $id = 'fv-apollo-r347-' . $instance;
    $records = fv_apollo_r347_records();
    $esc = static function ($t): string { return htmlspecialchars((string)$t, ENT_QUOTES|ENT_SUBSTITUTE, 'UTF-8'); };
    $groups = array(
        'findings' => array('heading'=>'Board findings', 'description'=>'Three original 1967 findings and their limits. These are independent questions, not three independent NASA reports.'),
        'chronology' => array('heading'=>'Recorded chronology', 'description'=>'Five markers traced to the original Review Board’s analysis; approximate markers remain approximate.'),
        'later' => array('heading'=>'Later NASA history', 'description'=>'One post-accident design-history record. Do not read this as a contemporary emergency recording.'),
        'photos' => array('heading'=>'Contextual photographs', 'description'=>'Four NASA accession pages. Photographs are context, not evidence identifying the precise ignition source or permission for commercial reuse.'),
    );
    ob_start(); ?>
<section class="fv-apollo-r347" data-fv-apollo-source-index aria-labelledby="<?php echo $esc($id); ?>-heading">
  <div class="fv-apollo-r347__inner">
    <p class="fv-apollo-r347__kicker">APOLLO 1 / EVIDENCE ATLAS</p>
    <h2 id="<?php echo $esc($id); ?>-heading">Find the original record.</h2>
    <p class="fv-apollo-r347__intro">A curated index of <strong><?php echo count($records); ?> evidence entries</strong> derived from the chronology, findings and NASA accession gallery above. Entries can share the same source page. Each link opens its institutional record; access does not establish image or commercial rights.</p>
    <?php if (!$records): ?>
      <p class="fv-apollo-r347__unavailable">The source index is unavailable. The complete <a href="https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html">NASA Apollo 204 Review Board findings</a> remain accessible directly.</p>
    <?php else: ?>
      <div class="fv-apollo-r347__filters" data-fv-apollo-filters hidden aria-label="Filter evidence types"></div>
      <p class="fv-apollo-r347__status" data-fv-apollo-status aria-live="polite" hidden></p>
      <div class="fv-apollo-r347__groups">
      <?php foreach($groups as $key=>$group): ?>
        <section class="fv-apollo-r347__group" data-fv-apollo-group="<?php echo $esc($key); ?>" aria-labelledby="<?php echo $esc($id.'-'.$key); ?>">
          <h3 id="<?php echo $esc($id.'-'.$key); ?>"><?php echo $esc($group['heading']); ?></h3>
          <p class="fv-apollo-r347__description"><?php echo $esc($group['description']); ?></p>
          <ol class="fv-apollo-r347__records">
            <?php foreach ($records as $record): if ($record['group'] !== $key) { continue; } ?>
              <li data-fv-apollo-entry="<?php echo $esc($key); ?>">
                <p class="fv-apollo-r347__type"><?php echo $esc($record['type']); ?></p>
                <h4><?php echo $esc($record['label']); ?></h4>
                <p><strong>Evidence boundary:</strong> <?php echo $esc($record['limit']); ?></p>
                <?php echo function_exists('fv_apollo_r349_source_link') ? fv_apollo_r349_source_link($record['url'], $record['locator'], array('data-fv-apollo-source-link'=>$key)) : '<span data-fv-source-review-required="true">Source link withheld pending verification</span>'; ?>
              </li>
            <?php endforeach; ?>
          </ol>
        </section>
      <?php endforeach; ?>
      </div>
      <p class="fv-apollo-r347__footer">Not a map of inferred locations or a recreation of missing data. Source types and uncertainty remain visible without JavaScript or filters. Photo rights, agency marks, identifiable likenesses and third-party rights require case-specific review before commercial reuse.</p>
    <?php endif; ?>
  </div>
</section>
<?php return (string) ob_get_clean();
}

/** Optional combined staging shortcode preserves the sole original editorial continuation action. */
function fv_apollo_r347_experience_shortcode($atts = array()): string {
    $file = dirname(__DIR__) . '/apollo-r340/apollo-accession-gallery.php';
    if (is_readable($file)) { require_once $file; }
    if (!function_exists('fv_apollo_r340_experience_shortcode')) {
        return '<p>Source experience unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a>.</p>';
    }
    return fv_apollo_r340_experience_shortcode() . fv_apollo_r347_index_shortcode();
}

/** Bounded, read-only shortcode resolver for direct posts and reusable core/block references. */
function fv_apollo_r347_in_content(string $content, array &$seen = array(), int $depth = 0): array {
    if (strlen($content) > 500000) { return array(false,false); }
    $has = static function(string $tag) use ($content): bool {
        return function_exists('has_shortcode') ? has_shortcode($content,$tag) : strpos($content,'['.$tag) !== false;
    };
    $flags = array($has('fv_apollo_experience_r347'), $has('fv_apollo_source_index_r347'));
    if ($depth >= 5 || !function_exists('parse_blocks')) { return $flags; }
    $walk = function(array $blocks) use (&$walk,&$flags,&$seen,$depth): void {
        foreach($blocks as $block) {
            if (!is_array($block)) { continue; }
            if (($block['blockName']??'') === 'core/block' && function_exists('get_post')) {
                $ref = (int)($block['attrs']['ref']??0);
                if ($ref > 0 && !isset($seen[$ref]) && count($seen) < 24) {
                    $seen[$ref] = true;
                    $post = get_post($ref);
                    if (is_object($post) && ($post->post_type??'')==='wp_block') {
                        $nested = fv_apollo_r347_in_content((string)($post->post_content??''),$seen,$depth+1);
                        $flags[0] = $flags[0] || $nested[0]; $flags[1] = $flags[1] || $nested[1];
                    }
                }
            }
            if (isset($block['innerBlocks']) && is_array($block['innerBlocks'])) { $walk($block['innerBlocks']); }
        }
    };
    $walk(parse_blocks($content));
    return $flags;
}

/** Enqueue dependencies BEFORE wp_head for the R347 wrapper; prior R340 detector does not know this shortcode. */
function fv_apollo_r347_enqueue(): void {
    if (!function_exists('is_singular') || !is_singular() || !function_exists('get_post') || !function_exists('wp_enqueue_style')) { return; }
    $post = get_post(); if (!is_object($post) || !isset($post->post_content)) { return; }
    $seen=array(); $flags=fv_apollo_r347_in_content((string)$post->post_content,$seen);
    if (!$flags[0] && !$flags[1]) { return; }
    $items = array(
        array('fv-apollo-r339-chronology','../apollo-r339/assets/chronology-rail.css'),
        array('fv-apollo-r345-evidence-plate','../apollo-r345/evidence-plate.css'),
        array('fv-apollo-r340-gallery','../apollo-r340/assets/accession-gallery.css'),
        array('fv-apollo-r347-index','assets/source-index.css'),
    );
    foreach ($items as $item) {
        if (!$flags[0] && $item[0] !== 'fv-apollo-r347-index') { continue; }
        $path = dirname(__FILE__).'/'.$item[1];
        if (is_readable($path)) { wp_enqueue_style($item[0],plugins_url($item[1],__FILE__),array(),'0.0.1-research'); }
    }
    if (function_exists('wp_enqueue_script') && is_readable(__DIR__.'/assets/source-index.js')) {
        wp_enqueue_script('fv-apollo-r347-index', plugins_url('assets/source-index.js',__FILE__),array(),'0.0.1-research',true);
    }
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_source_index_r347','fv_apollo_r347_index_shortcode');
    add_shortcode('fv_apollo_experience_r347','fv_apollo_r347_experience_shortcode');
}
if (function_exists('add_action')) { add_action('wp_enqueue_scripts','fv_apollo_r347_enqueue',19); }
