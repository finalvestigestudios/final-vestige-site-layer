<?php
/**
 * FV Apollo R365 chronology source-custody rail, isolated DRAFT staging component.
 * No remote media, map coordinates, tracking, form, cart, or CMS writes.
 * Reviewed rows are deliberately sealed; tests may pass candidates to render_rows.
 */
if (!defined('ABSPATH')) { exit; }
function fv_apollo_r365_rows(): array {
    $board = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
    $tests = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
    $atmo = 'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/';
    return array(
      array('id'=>'fire','when'=>'January 27, 1967','era'=>'1967 event · reviewed in the original Board report',
        'heading'=>'A ground test became a fatal cabin fire',
        'supported'=>'The Apollo 204 crew was performing a ground test in a pressurized, pure-oxygen cabin. The Board identified combustible material and inadequate emergency egress among the hazards.',
        'limit'=>'The original Board did not conclusively establish one exact ignition source.',
        'source'=>$board,'source_title'=>'Apollo 204 Review Board · original report','published'=>'1967 Review Board report','class'=>'primary-investigation'),
      array('id'=>'findings','when'=>'1967 · Review Board','era'=>'Original investigation · not a later test',
        'heading'=>'The probable initiator was not a proven wire',
        'supported'=>'The Board determined that an electrical arc was the most probable initiator while identifying unsafe cabin conditions and hatch limitations.',
        'limit'=>'A probable class of initiator does not prove which particular cable or arc started the fire.',
        'source'=>$board,'source_title'=>'Apollo 204 Review Board · findings and determinations','published'=>'1967 Review Board report','class'=>'primary-investigation'),
      array('id'=>'tests','when'=>'December 1967 – February 1968','era'=>'Engineering tests · documented retrospectively in 2018',
        'heading'=>'102 deliberate Command Module ignitions',
        'supported'=>'NASA reports three series of 102 deliberate ignitions in Command Module Boilerplate 1224, testing different cabin atmospheres and pressures after the Apollo 1 fire.',
        'limit'=>'These later engineering experiments were not 102 observed ignition events in Apollo 1 and were not findings made in the original 1967 Board report.',
        'source'=>$tests,'source_title'=>'NASA · 50 Years Ago: Apollo Flammability Tests','published'=>'NASA retrospective, February 14, 2018','class'=>'later-engineering'),
      array('id'=>'decision','when'=>'March 14, 1968','era'=>'Redesign decision · described in a 2018 NASA retrospective',
        'heading'=>'Ground operations moved to a mixed atmosphere',
        'supported'=>'NASA announced that Apollo 7 would use 60 percent oxygen and 40 percent nitrogen at approximately 16 psi during launch-pad operations.',
        'limit'=>'This was a ground-operations decision; it does not mean Apollo abandoned low-pressure pure oxygen during orbital flight.',
        'source'=>$atmo,'source_title'=>'NASA · Mixed-gas atmosphere anniversary','published'=>'NASA retrospective, March 9, 2018','class'=>'later-decision'),
    );
}
function fv_apollo_r365_reviewed(array $candidate): bool {
    foreach (fv_apollo_r365_rows() as $row) { if ($candidate === $row) { return true; } }
    return false;
}
function fv_apollo_r365_render_rows(array $rows): string {
    static $instance = 0; $instance++;
    $base = 'fv-apollo-r365-' . $instance;
    $esc = static fn($value): string => htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    ob_start(); ?>
<section class="fv-apollo-r365" data-fv-chronology aria-labelledby="<?php echo $esc($base); ?>-title">
 <div class="fv-apollo-r365__inner">
  <p class="fv-apollo-r365__eyebrow">APOLLO 1 · A CHRONOLOGY OF THE RECORD</p>
  <h2 id="<?php echo $esc($base); ?>-title">What happened. What investigators found. What changed.</h2>
  <p class="fv-apollo-r365__deck">The fire, the Board's findings and the later engineering tests belong to different moments. Each record below names its source, publication period and limit. This is a chronology, not a geographic reconstruction.</p>
  <nav aria-label="Jump to Apollo evidence stages"><ol class="fv-apollo-r365__quick">
  <?php foreach ($rows as $i=>$row): if (is_array($row) && fv_apollo_r365_reviewed($row)): ?>
   <li><a href="#<?php echo $esc($base.'-'.$row['id']); ?>"><?php echo $esc($row['when']); ?></a></li>
  <?php endif; endforeach; ?>
  </ol></nav>
  <ol class="fv-apollo-r365__rail">
  <?php foreach ($rows as $i=>$row): ?>
   <li class="fv-apollo-r365__event" <?php if (is_array($row) && fv_apollo_r365_reviewed($row)): ?>id="<?php echo $esc($base.'-'.$row['id']); ?>"<?php endif; ?>>
   <?php if (!is_array($row) || !fv_apollo_r365_reviewed($row)): ?>
    <p class="fv-apollo-r365__withheld" data-fv-withheld><strong>Record withheld.</strong> A claim or source differs from the reviewed chronology; no citation is authorized.</p>
   <?php else: ?>
    <div class="fv-apollo-r365__date"><strong><?php echo $esc($row['when']); ?></strong><span><?php echo $esc($row['era']); ?></span></div>
    <article class="fv-apollo-r365__plate" aria-labelledby="<?php echo $esc($base.'-'.$row['id'].'-heading'); ?>">
     <p class="fv-apollo-r365__class"><?php echo $esc(str_replace('-', ' ', $row['class'])); ?></p>
     <h3 id="<?php echo $esc($base.'-'.$row['id'].'-heading'); ?>"><?php echo $esc($row['heading']); ?></h3>
     <p><?php echo $esc($row['supported']); ?></p>
     <p class="fv-apollo-r365__limit"><strong>Evidence boundary:</strong> <?php echo $esc($row['limit']); ?></p>
     <details data-fv-source-drawer><summary>Inspect source and rights for <?php echo $esc($row['heading']); ?></summary>
      <div class="fv-apollo-r365__source"><p><strong>Source:</strong> <?php echo $esc($row['source_title']); ?></p>
       <p><strong>Publication:</strong> <?php echo $esc($row['published']); ?></p>
       <p><strong>Media rights:</strong> Link only. No NASA photographs, third-party images, marks or likenesses are cleared for commercial reuse by this prototype.</p>
       <p><a data-fv-nasa-source href="<?php echo $esc($row['source']); ?>" rel="noopener noreferrer">Read the NASA source for <?php echo $esc($row['heading']); ?></a></p>
      </div>
     </details>
    </article>
   <?php endif; ?>
   </li>
  <?php endforeach; ?></ol>
  <p class="fv-apollo-r365__method">Archival sources and retrospective accounts are labeled separately. No mapped pins or inferred geographic connections are presented. NASA does not endorse this prototype or Final Vestige's products.</p>
  <p class="fv-apollo-r365__continue"><a data-fv-free-cta href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the complete free Apollo 1 investigation</a></p>
  <p class="fv-apollo-r365__commerce">An educational product is only a future proposal; no purchasable Apollo kit or checkout is claimed here.</p>
 </div>
</section>
<?php return (string)ob_get_clean();
}
function fv_apollo_r365_shortcode($atts=array()): string {
    return fv_apollo_r365_render_rows(fv_apollo_r365_rows());
}
function fv_apollo_r365_enqueue(): void {
    if (!function_exists('wp_enqueue_style') || !function_exists('plugins_url')) { return; }
    // Staging plugin must be loaded only on the isolated QA surface. The normal
    // WordPress template lifecycle and conditional-asset loading remain release gates.
    wp_enqueue_style('fv-apollo-r365-chronology', plugins_url('assets/chrono-rail.css', __FILE__), array(), '0.0.1-staging');
}
if (function_exists('add_shortcode')) { add_shortcode('fv_apollo_chronology_r365', 'fv_apollo_r365_shortcode'); }
if (function_exists('add_action')) { add_action('wp_enqueue_scripts', 'fv_apollo_r365_enqueue', 20); }
