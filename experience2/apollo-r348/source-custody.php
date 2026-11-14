<?php
/**
 * Plugin Name: FV Apollo R348 Source Custody Drawer — RESEARCH ONLY
 * Description: Read-only, source-page-deduplicated NASA custody view; no production authorization.
 * Version: 0.0.1-research
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/**
 * Immutable editorial source-page allowlist. A NASA domain alone is NOT sufficient:
 * new links and record interpretations must undergo explicit source/rights review.
 * URL and record text are derived from R347; these labels are page identifiers.
 */
function fv_apollo_r348_approved_pages(): array {
    $policy = dirname(__DIR__) . '/apollo-r349/source-policy.php';
    if (is_readable($policy)) { require_once $policy; }
    // Absent policy module: quarantine all source links instead of trusting URLs.
    return function_exists('fv_apollo_r349_approved_sources') ? fv_apollo_r349_approved_sources() : array();
}
/** No heuristics or speculative relationships: a shared URL is the ONLY grouping edge. */
function fv_apollo_r348_custody(?array $input = null): array {
    if ($input === null) {
        $parent = dirname(__DIR__) . '/apollo-r347/source-index.php';
        if (is_readable($parent)) { require_once $parent; }
        if (!function_exists('fv_apollo_r347_records')) { return array(); }
        $input = fv_apollo_r347_records();
    }
    $approved = fv_apollo_r348_approved_pages();
    $groups = array();
    foreach ($input as $record) {
        $url = isset($record['url']) ? (string)$record['url'] : '';
        // Omit an unreviewed OUTBOUND LINK, not the record/limitation; fail visibly.
        $ok = array_key_exists($url, $approved);
        $key = $ok ? $url : 'unreviewed:' . hash('sha256', $url);
        if (!isset($groups[$key])) {
            $groups[$key] = array(
                'label' => $ok ? $approved[$url] : 'Source identity awaiting editorial review',
                'url' => $ok ? $url : '',
                'approved' => $ok,
                'items' => array(),
            );
        }
        $groups[$key]['items'][] = $record;
    }
    return array_values($groups);
}
function fv_apollo_r348_drawer_shortcode($atts=array()): string {
    static $instance=0; $instance++;
    $id='fv-apollo-r348-'.$instance;
    $esc=static function($v): string { return htmlspecialchars((string)$v, ENT_QUOTES|ENT_SUBSTITUTE, 'UTF-8'); };
    $pages=fv_apollo_r348_custody(); $references=0; $approved=0;
    foreach ($pages as $page) { $references+=count($page['items']); if ($page['approved']) $approved++; }
    ob_start(); ?>
<section class="fv-apollo-r348" data-fv-apollo-custody aria-labelledby="<?php echo $esc($id); ?>-heading">
  <div class="fv-apollo-r348__inner">
    <p class="fv-apollo-r348__kicker">APOLLO 1 / SOURCE CUSTODY</p>
    <h2 id="<?php echo $esc($id); ?>-heading">Trace each claim to its source.</h2>
    <p class="fv-apollo-r348__intro">This is a source-page crosswalk, not an additional set of independent reports. <?php echo $esc((string)$references); ?> evidence references resolve to <?php echo $esc((string)count($pages)); ?> distinct source identities; <?php echo $esc((string)$approved); ?> of those page addresses are explicitly approved for link display. Entries are grouped <strong>only when their exact NASA source-page URL matches</strong>. A citation does not grant media reuse rights.</p>
    <?php if (!$pages): ?>
      <p class="fv-apollo-r348__fallback">The custody crosswalk is temporarily unavailable. Read the <a href="https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html">original NASA Review Board findings</a>.</p>
    <?php else: ?>
      <ol class="fv-apollo-r348__pages">
      <?php foreach($pages as $n=>$page): ?>
        <li class="fv-apollo-r348__page" data-fv-custody-approval="<?php echo $page['approved']?'approved':'review-required'; ?>">
          <article aria-labelledby="<?php echo $esc($id.'-source-'.$n); ?>">
            <h3 id="<?php echo $esc($id.'-source-'.$n); ?>"><?php echo $esc($page['label']); ?></h3>
            <p class="fv-apollo-r348__count"><?php echo count($page['items']); ?> referenced <?php echo count($page['items'])===1?'entry':'entries'; ?> · <?php echo $page['approved']?'NASA source-page link':'source link withheld pending review'; ?></p>
            <?php if ($page['approved']): ?><p><a href="<?php echo $esc($page['url']); ?>" rel="noopener noreferrer" data-fv-custody-source>Open institutional source record</a></p><?php else: ?><p class="fv-apollo-r348__warning">Unreviewed URL withheld. This evidence must not be presented as source-verified or used for a commercial claim.</p><?php endif; ?>
            <details class="fv-apollo-r348__detail">
              <summary>Inspect <?php echo count($page['items']); ?> record <?php echo count($page['items'])===1?'boundary':'boundaries'; ?></summary>
              <ol>
                <?php foreach($page['items'] as $item): ?>
                  <li><p class="fv-apollo-r348__role"><?php echo $esc($item['type']); ?></p><h4><?php echo $esc($item['label']); ?></h4><p><strong>Evidence boundary:</strong> <?php echo $esc($item['limit']); ?></p></li>
                <?php endforeach; ?>
              </ol>
            </details>
            <!-- Native print/PDF commonly suppresses closed <details>. Deliberate print
                 twin is absent from screen and accessibility tree, but always prints. -->
            <div class="fv-apollo-r348__print" data-fv-custody-print hidden>
              <p><strong>Source status:</strong> <?php echo $page['approved']?'Reviewed NASA source-page address':'Not approved; link withheld'; ?></p>
              <?php if ($page['approved']): ?><p><strong>Source:</strong> <a href="<?php echo $esc($page['url']); ?>"><?php echo $esc($page['label']); ?></a></p><?php endif; ?>
              <ol>
              <?php foreach($page['items'] as $item): ?>
                <li><strong><?php echo $esc($item['type'].' — '.$item['label']); ?></strong>. Evidence boundary: <?php echo $esc($item['limit']); ?></li>
              <?php endforeach; ?>
              </ol>
            </div>
          </article>
        </li>
      <?php endforeach; ?>
      </ol>
      <p class="fv-apollo-r348__rights"><strong>Evidence is not license clearance.</strong> NASA photograph accessions here are contextual links, not proof of an ignition location. Commercial use of images, identifiable people, marks and third-party material requires separate case-specific review. No speculative map pins or connections are presented.</p>
    <?php endif; ?>
  </div>
</section>
<?php return (string)ob_get_clean();
}
function fv_apollo_r348_experience_shortcode($atts=array()): string {
    $parent=dirname(__DIR__).'/apollo-r347/source-index.php';
    if (is_readable($parent)) require_once $parent;
    if (!function_exists('fv_apollo_r347_experience_shortcode')) {
        return '<p>The source experience is unavailable. <a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo investigation</a>.</p>';
    }
    return fv_apollo_r347_experience_shortcode().fv_apollo_r348_drawer_shortcode();
}
/**
 * Read-only, bounded detection for direct and core/block shortcode placements.
 * No content/settings mutations, rendering side effects, or network access.
 */
function fv_apollo_r348_flags(string $content,array &$seen=array(),int $depth=0): array {
    $has=static function(string $tag)use($content):bool {
        return function_exists('has_shortcode')?has_shortcode($content,$tag):strpos($content,'['.$tag)!==false;
    };
    $flags=array($has('fv_apollo_experience_r348'),$has('fv_apollo_source_drawer_r348'));
    if ($depth>=5||strlen($content)>500000||!function_exists('parse_blocks'))return $flags;
    $walk=function(array $blocks)use(&$walk,&$flags,&$seen,$depth):void {
        foreach($blocks as $block) {
            if(!is_array($block))continue;
            if(($block['blockName']??'')==='core/block'&&function_exists('get_post')) {
                $ref=(int)($block['attrs']['ref']??0);
                if($ref>0&&!isset($seen[$ref])&&count($seen)<24) {
                    $seen[$ref]=true; $p=get_post($ref);
                    if(is_object($p)&&($p->post_type??'')==='wp_block') {
                        $nested=fv_apollo_r348_flags((string)($p->post_content??''),$seen,$depth+1);
                        $flags[0]=$flags[0]||$nested[0];$flags[1]=$flags[1]||$nested[1];
                    }
                }
            }
            if(isset($block['innerBlocks'])&&is_array($block['innerBlocks']))$walk($block['innerBlocks']);
        }
    };
    $walk(parse_blocks($content));return $flags;
}
function fv_apollo_r348_enqueue():void {
    if(!function_exists('is_singular')||!is_singular()||!function_exists('get_post')||!function_exists('wp_enqueue_style'))return;
    $p=get_post(); if(!is_object($p)||!isset($p->post_content))return;
    $seen=array();$flags=fv_apollo_r348_flags((string)$p->post_content,$seen);
    if(!$flags[0]&&!$flags[1])return;
    $styles=array(
       array('fv-apollo-r339-chronology','../apollo-r339/assets/chronology-rail.css'),
       array('fv-apollo-r345-evidence-plate','../apollo-r345/evidence-plate.css'),
       array('fv-apollo-r340-gallery','../apollo-r340/assets/accession-gallery.css'),
       array('fv-apollo-r347-index','../apollo-r347/assets/source-index.css'),
       array('fv-apollo-r348-custody','assets/source-custody.css'),
    );
    foreach($styles as $item){
        if(!$flags[0]&&$item[0]!=='fv-apollo-r348-custody')continue;
        if(is_readable(__DIR__.'/'.$item[1]))wp_enqueue_style($item[0],plugins_url($item[1],__FILE__),array(),'0.0.1-research');
    }
    if($flags[0]&&function_exists('wp_enqueue_script')&&is_readable(dirname(__DIR__).'/apollo-r347/assets/source-index.js'))
        wp_enqueue_script('fv-apollo-r347-index',plugins_url('../apollo-r347/assets/source-index.js',__FILE__),array(),'0.0.1-research',true);
}
if(function_exists('add_shortcode')){
    add_shortcode('fv_apollo_source_drawer_r348','fv_apollo_r348_drawer_shortcode');
    add_shortcode('fv_apollo_experience_r348','fv_apollo_r348_experience_shortcode');
}
if(function_exists('add_action'))add_action('wp_enqueue_scripts','fv_apollo_r348_enqueue',18);
