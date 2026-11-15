<?php
/**
 * Apollo Experience 2.0 R372 — evidence provenance route, STAGING/DRAFT ONLY.
 * No API, image, map, tracking, network, form or merchant integration.
 * Reuses existing reviewed R365 chronology and R371 NASA gallery records.
 */
if (!defined('ABSPATH')) { exit; }

/** Explicit documentary identity joins; never inferred from title or geography. */
function fv_apollo_r372_join(): array {
    return array('fire'=>'review-board', 'findings'=>'review-board',
        'tests'=>'flammability', 'decision'=>'atmosphere');
}

function fv_apollo_r372_approved($events, $documents): bool {
    if (!function_exists('fv_apollo_r367_is_sealed') ||
        !function_exists('fv_apollo_r371_is_sealed') ||
        !fv_apollo_r367_is_sealed($events) || !fv_apollo_r371_is_sealed($documents)) { return false; }
    $join = fv_apollo_r372_join();
    if (array_keys($join) !== array('fire','findings','tests','decision')) { return false; }
    $sources = array();
    foreach ($documents as $doc) {
        if (!is_array($doc) || !isset($doc['key'], $doc['url']) || isset($sources[$doc['key']])) { return false; }
        $sources[$doc['key']] = $doc;
    }
    if (array_keys($sources) !== array('review-board','flammability','atmosphere','context')) { return false; }
    foreach ($events as $event) {
        $key = $join[$event['id']] ?? null;
        if (!is_string($key) || !isset($sources[$key]) ||
            !hash_equals($event['source'], $sources[$key]['url'])) { return false; }
    }
    // A 2022 retrospective is contextual reading, not a new 1967 event or an event-to-geo edge.
    return $sources['context']['url'] === 'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/';
}

function fv_apollo_r372_fallback(): string {
    return '<section class="fv-apollo-r372__fallback" aria-label="Apollo source custody unavailable">'
        . '<h2>Evidence route currently unavailable</h2>'
        . '<p>The reviewed chronology or its documentary source relationships did not pass verification. Historical claims and citations have been withheld.</p>'
        . '<p><a data-fv-free-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the existing free Apollo 1 investigation</a></p></section>';
}

/** Pure server-side render. Native details and document links work without JavaScript. */
function fv_apollo_r372_render($events, $documents): string {
    if (!fv_apollo_r372_approved($events, $documents)) { return fv_apollo_r372_fallback(); }
    static $instance = 0; ++$instance;
    $prefix = 'fv-apollo-r372-' . $instance;
    $esc = static fn($v): string => htmlspecialchars((string)$v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    $docs = array_column($documents, null, 'key');
    $join = fv_apollo_r372_join();
    ob_start(); ?>
<section class="fv-apollo-r372" data-fv-apollo-path aria-labelledby="<?php echo $esc($prefix); ?>-title">
 <div class="fv-apollo-r372__wrap">
  <p class="fv-apollo-r372__eyebrow">APOLLO 1 · RESEARCH DESK → EVIDENCE ATLAS</p>
  <h2 id="<?php echo $esc($prefix); ?>-title">Trace the claim. Check the document.</h2>
  <p class="fv-apollo-r372__intro">Four moments, three contemporaneous-or-later documentary sources and one optional historical retrospective. The original investigation, later tests and later decisions are not interchangeable. Follow each source yourself before drawing a conclusion.</p>
  <nav class="fv-apollo-r372__jump" aria-label="Jump to reviewed evidence stage"><ol>
  <?php foreach ($events as $i=>$event): ?>
   <li><a href="#<?php echo $esc($prefix.'-'.$event['id']); ?>"><?php echo $esc(sprintf('%02d', $i+1)); ?> · <?php echo $esc($event['when']); ?></a></li>
  <?php endforeach; ?>
  </ol></nav>
  <ol class="fv-apollo-r372__stages">
  <?php foreach ($events as $i=>$event): $doc = $docs[$join[$event['id']]]; $ref_id = $prefix.'-'.$event['id']; ?>
   <li class="fv-apollo-r372__stage" id="<?php echo $esc($ref_id); ?>" data-fv-evidence-stage>
    <article aria-labelledby="<?php echo $esc($ref_id.'-heading'); ?>">
     <header class="fv-apollo-r372__stagehead">
      <span class="fv-apollo-r372__index"><?php echo $esc(sprintf('%02d', $i+1)); ?></span>
      <div><p class="fv-apollo-r372__when"><?php echo $esc($event['when']); ?> · <?php echo $esc(str_replace('-', ' ', $event['class'])); ?></p>
       <h3 id="<?php echo $esc($ref_id.'-heading'); ?>"><?php echo $esc($event['heading']); ?></h3></div>
     </header>
     <p class="fv-apollo-r372__claim"><strong>Supported by the record:</strong> <?php echo $esc($event['supported']); ?></p>
     <p class="fv-apollo-r372__limit"><strong>Not established:</strong> <?php echo $esc($event['limit']); ?></p>
     <details class="fv-apollo-r372__drawer" data-fv-source-drawer>
      <summary>Inspect document, date and rights for stage <?php echo $esc($i+1); ?></summary>
      <div class="fv-apollo-r372__source">
       <p><strong>Reviewed source:</strong> <?php echo $esc($doc['title']); ?> · <?php echo $esc($doc['kind']); ?></p>
       <p><strong>Document date / context:</strong> <?php echo $esc($doc['when']); ?></p>
       <p><strong>Custodian:</strong> <?php echo $esc($doc['publisher']); ?></p>
       <p><strong>Source limitation:</strong> <?php echo $esc($doc['boundary']); ?></p>
       <p><strong>Rights:</strong> <?php echo $esc($doc['rights']); ?> No NASA endorsement claimed.</p>
       <p><a data-fv-nasa-source href="<?php echo $esc($doc['url']); ?>" rel="noopener noreferrer">Read NASA source for stage <?php echo $esc($i+1); ?>: <?php echo $esc($doc['title']); ?></a></p>
      </div>
     </details>
     <p class="fv-apollo-r372__print"><strong>Document:</strong> <a data-fv-print-source href="<?php echo $esc($doc['url']); ?>"><?php echo $esc($doc['publisher']); ?> — <?php echo $esc($doc['title']); ?></a></p>
    </article>
   </li>
  <?php endforeach; ?>
  </ol>
  <aside class="fv-apollo-r372__context" aria-label="Later contextual reading">
   <details data-fv-context><summary>What about NASA’s 2022 retrospective?</summary>
    <p>It recounts the 1967 ground test and crew. It is a later historical account, not a fifth event on the 1967–1968 chronology and not a substitute for the original Review Board.</p>
    <p><strong>Source:</strong> <?php echo $esc($docs['context']['publisher']); ?> · <?php echo $esc($docs['context']['when']); ?></p>
    <p><strong>Boundary:</strong> <?php echo $esc($docs['context']['boundary']); ?></p>
    <p><a data-fv-nasa-context href="<?php echo $esc($docs['context']['url']); ?>" rel="noopener noreferrer">Read NASA’s 2022 historical account</a></p>
   </details>
   <p class="fv-apollo-r372__print"><strong>Additional retrospective:</strong> <a data-fv-print-source href="<?php echo $esc($docs['context']['url']); ?>">NASA 2022 retrospective</a></p>
  </aside>
  <p class="fv-apollo-r372__method">Document relationships here are reviewed source identities, not geographic connections. No coordinates, speculative map edges, archival photographs or agency emblems are used. Historical access remains free.</p>
  <p class="fv-apollo-r372__cta"><a data-fv-free-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the full free Apollo 1 investigation</a></p>
  <p class="fv-apollo-r372__note">An Apollo educator dossier is only a proposed future offer; it is not a verified purchasable product or endorsed by NASA. No sale or conversion is claimed.</p>
 </div>
</section>
<?php return (string)ob_get_clean();
}

function fv_apollo_r372_shortcode($atts = array()): string {
    return fv_apollo_r372_render(
        function_exists('fv_apollo_r365_rows') ? fv_apollo_r365_rows() : null,
        function_exists('fv_apollo_r371_catalog') ? fv_apollo_r371_catalog() : null
    );
}
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_source_path_r372', 'fv_apollo_r372_shortcode'); }
