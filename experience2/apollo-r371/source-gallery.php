<?php
/**
 * Final Vestige Apollo R371 — source-custody documentary gallery, DRAFT STAGING ONLY.
 * Optional shortcode [fv_apollo_source_gallery_r371]. No API, JS, tracking, geo, image,
 * product or checkout calls; requires the existing R367 full chronology seal.
 * Readonly documentary gallery, source links only. Do not install without founder/QD review.
 */
if (!defined('ABSPATH')) { exit; }

function fv_apollo_r371_catalog(): array {
    return array(
      array(
        'key'=>'review-board', 'when'=>'1967', 'kind'=>'Original investigation',
        'title'=>'The Board’s findings',
        'finding'=>'The Board identified an electrical arc as the most probable initiator and did not conclusively identify a single ignition source.',
        'boundary'=>'The findings do not identify one proven cable, exact spark or individual wire.',
        'url'=>'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
        'publisher'=>'NASA · Apollo 204 Review Board', 'rights'=>'Link only; no source photographs or seals incorporated.'
      ),
      array(
        'key'=>'flammability', 'when'=>'December 1967–February 1968; article February 14, 2018',
        'kind'=>'Later engineering · retrospective', 'title'=>'102 deliberate test ignitions',
        'finding'=>'NASA documents three series totaling 102 deliberate Command Module Boilerplate 1224 ignitions after the Apollo 1 fire.',
        'boundary'=>'These were later tests, not 102 ignition events observed during Apollo 1.',
        'url'=>'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
        'publisher'=>'NASA Johnson Space Center · John Uri', 'rights'=>'Link only; associated photographs are not reused.'
      ),
      array(
        'key'=>'atmosphere', 'when'=>'March 14, 1968; article March 9, 2018',
        'kind'=>'Later decision · retrospective', 'title'=>'A change at the launch pad',
        'finding'=>'NASA announced a 60-percent oxygen, 40-percent nitrogen mix for Apollo 7 launch-pad operations.',
        'boundary'=>'This did not eliminate the lower-pressure, pure-oxygen atmosphere used in orbit.',
        'url'=>'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/',
        'publisher'=>'NASA Johnson Space Center · John Uri', 'rights'=>'Link only; no commercial reuse of NASA media is implied.'
      ),
      array(
        'key'=>'context', 'when'=>'January 27, 2022', 'kind'=>'Later historical account',
        'title'=>'The crew and the ground test',
        'finding'=>'NASA’s later history recounts the January 27, 1967 plugs-out test involving Grissom, White and Chaffee.',
        'boundary'=>'This retrospective helps orient readers; the 1967 Review Board remains the original investigative record.',
        'url'=>'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/',
        'publisher'=>'NASA Johnson Space Center · John Uri', 'rights'=>'Link only; images of identifiable people are not cleared for commercial use here.'
      ),
    );
}

/** The whole gallery must match the frozen, reviewed list including order. */
function fv_apollo_r371_is_sealed($records): bool {
    return is_array($records) && $records === fv_apollo_r371_catalog();
}

function fv_apollo_r371_fallback(): string {
    return '<section class="fv-apollo-r371__fallback" aria-label="Apollo sources unavailable">'
        . '<h2>Source gallery unavailable</h2><p>Unreviewed source material has been withheld.</p>'
        . '<p><a data-fv-free-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the original free Apollo 1 investigation</a></p></section>';
}

/** No seller promise, no independent sale claim; exactly one free editorial next action. */
function fv_apollo_r371_render($records, $chronology = null): string {
    if (!fv_apollo_r371_is_sealed($records) ||
        !function_exists('fv_apollo_r367_is_sealed') ||
        !fv_apollo_r367_is_sealed($chronology)) { return fv_apollo_r371_fallback(); }
    static $instance = 0; $instance++;
    $prefix = 'fv-apollo-r371-' . $instance;
    $esc = static function ($value): string { return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); };
    ob_start(); ?>
<section class="fv-apollo-r371" aria-labelledby="<?php echo $esc($prefix); ?>-title" data-fv-source-gallery>
 <div class="fv-apollo-r371__inner">
  <p class="fv-apollo-r371__eyebrow">APOLLO 1 · EVIDENCE ATLAS · DOCUMENTARY GALLERY</p>
  <h2 id="<?php echo $esc($prefix); ?>-title">Four documents. Four distinct kinds of evidence.</h2>
  <p class="fv-apollo-r371__intro">The original 1967 investigation is not interchangeable with later engineering tests or a retrospective. Explore each record, its limitation and its NASA source. No historical locations, routes or inferred map connections are plotted.</p>
  <nav class="fv-apollo-r371__jump" aria-label="Jump to documentary source"><ol>
   <?php foreach ($records as $row): ?><li><a href="#<?php echo $esc($prefix.'-'.$row['key']); ?>"><?php echo $esc($row['title']); ?></a></li><?php endforeach; ?>
  </ol></nav>
  <ol class="fv-apollo-r371__gallery">
   <?php foreach ($records as $row): $id = $prefix.'-'.$row['key']; ?>
   <li id="<?php echo $esc($id); ?>" class="fv-apollo-r371__card">
    <div class="fv-apollo-r371__meta"><span><?php echo $esc($row['kind']); ?></span><time><?php echo $esc($row['when']); ?></time></div>
    <h3><?php echo $esc($row['title']); ?></h3>
    <p><?php echo $esc($row['finding']); ?></p>
    <p class="fv-apollo-r371__boundary"><strong>What this cannot prove:</strong> <?php echo $esc($row['boundary']); ?></p>
    <details class="fv-apollo-r371__drawer" data-fv-source-drawer><summary>Inspect provenance and rights for <?php echo $esc($row['title']); ?></summary>
     <div class="fv-apollo-r371__drawer-body">
      <p><strong>Source custody:</strong> <?php echo $esc($row['publisher']); ?></p>
      <p><strong>Media policy:</strong> <?php echo $esc($row['rights']); ?> NASA does not endorse this resource or any product.</p>
      <p><a data-fv-nasa-source href="<?php echo $esc($row['url']); ?>" rel="noopener noreferrer">Read NASA’s record: <?php echo $esc($row['title']); ?></a></p>
     </div>
    </details>
    <p class="fv-apollo-r371__print-source"><strong>Primary reading link:</strong> <a data-fv-print-source href="<?php echo $esc($row['url']); ?>" rel="noopener noreferrer"><?php echo $esc($row['publisher']); ?> — <?php echo $esc($row['title']); ?></a></p>
   </li>
   <?php endforeach; ?>
  </ol>
  <p class="fv-apollo-r371__method"><strong>Research method:</strong> All four reviewed records are linked, not reproduced as images. NASA’s brand guidance permits ordinary links without implying endorsement. Commercial photography/likeness permissions have not been established; the gallery includes no NASA image or trademark asset.</p>
  <p class="fv-apollo-r371__cta"><a data-fv-free-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the original free Apollo 1 investigation</a></p>
  <p class="fv-apollo-r371__commerce">An Apollo educator kit is a proposal, not a verified purchasable product. No price, checkout, lead capture or purchase tracking is presented.</p>
 </div>
</section>
<?php return (string)ob_get_clean();
}

function fv_apollo_r371_shortcode($atts = array()): string {
    return fv_apollo_r371_render(fv_apollo_r371_catalog(), function_exists('fv_apollo_r365_rows') ? fv_apollo_r365_rows() : null);
}
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_source_gallery_r371', 'fv_apollo_r371_shortcode'); }
