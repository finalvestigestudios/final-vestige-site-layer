<?php
/** Apollo R345: evidence plates. Isolated staging research, NOT production. */
if (!defined('ABSPATH')) { exit; }
function fv_apollo_r345_claims(): array {
  $board = 'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html';
  return array(
    array('number'=>'01', 'question'=>'What initiated the fire?', 'finding'=>'The Board identified an electrical arc as the most probable initiator and documented evidence of several arcs.', 'limit'=>'No single ignition source was conclusively identified. An exact failed wire or component cannot be asserted.', 'source'=>$board, 'locator'=>'1967 Review Board — Finding and Determination 1', 'tier'=>'original-board'),
    array('number'=>'02', 'question'=>'Why were conditions hazardous?', 'finding'=>'The Board recorded a 16.7 psia, 100-percent-oxygen test atmosphere and combustible materials near possible ignition sources.', 'limit'=>'These environmental conditions explain fire risk; they do not establish which precise arc initiated the fire.', 'source'=>$board, 'locator'=>'1967 Review Board — Finding and Determination 2', 'tier'=>'original-board'),
    array('number'=>'03', 'question'=>'Why was emergency egress impossible?', 'finding'=>'The Board found that internal pressure prevented opening the inner hatch before cabin rupture.', 'limit'=>'This finding does not establish that the crew made no effort to follow emergency procedures.', 'source'=>$board, 'locator'=>'1967 Review Board — Finding and Determination 4', 'tier'=>'original-board'),
  );
}
function fv_apollo_r345_evidence_plate(): string {
  static $instance=0; $instance++;
  $section_id='fv-apollo-r345-heading-'.$instance;
  $e=static function($v): string { return htmlspecialchars((string)$v, ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'); };
  ob_start(); ?>
<section class="fv-apollo-r345" aria-labelledby="<?php echo $e($section_id); ?>" data-fv-apollo-claim-ledger>
  <div class="fv-apollo-r345__inner">
    <p class="fv-apollo-r345__eyebrow">RESEARCH DESK / DOCUMENTARY FINDINGS</p>
    <h2 id="<?php echo $e($section_id); ?>">What the record establishes.</h2>
    <p class="fv-apollo-r345__intro">Three questions, three Board findings. Each separates a documented determination from what the evidence cannot prove. These are editorial paraphrases of an original NASA-hosted report, not photographs, reconstructed sensor data or a claim to know the exact ignition point.</p>
    <ol class="fv-apollo-r345__grid">
      <?php foreach(fv_apollo_r345_claims() as $claim): ?>
      <li class="fv-apollo-r345__card" data-fv-apollo-tier="<?php echo $e($claim['tier']); ?>"><article>
        <p class="fv-apollo-r345__number">BOARD FINDING <?php echo $e($claim['number']); ?></p>
        <h3><?php echo $e($claim['question']); ?></h3>
        <p class="fv-apollo-r345__finding"><strong>Established:</strong> <?php echo $e($claim['finding']); ?></p>
        <p class="fv-apollo-r345__limit"><strong>Evidence limit:</strong> <?php echo $e($claim['limit']); ?></p>
        <details class="fv-apollo-r345__custody"><summary>Inspect source custody</summary><p>Document class: original 1967 NASA Apollo 204 Review Board findings, hosted by NASA. Plate text is a paraphrase, not a verbatim quotation.</p></details>
        <p class="fv-apollo-r345__source"><a href="<?php echo $e($claim['source']); ?>" rel="noopener noreferrer" data-fv-apollo-primary-source="board"><?php echo $e($claim['locator']); ?></a></p>
        <!-- A separate print-only source ledger avoids losing closed <details> in native PDF export.
             It is hidden from the screen/accessibility tree and replaces, rather than duplicates,
             the screen source link in print. All data derives from this same reviewed claim. -->
        <div class="fv-apollo-r345__print-custody" data-fv-apollo-print-custody hidden>
          <p><strong>Original Board source:</strong> <a href="<?php echo $e($claim['source']); ?>" rel="noopener noreferrer" data-fv-apollo-print-source="board"><?php echo $e($claim['locator']); ?></a></p>
          <p><strong>Record custody:</strong> NASA-hosted 1967 Apollo 204 Review Board finding; this plate is an editorial paraphrase, not a verbatim quotation or a photograph.</p>
        </div>
      </article></li>
      <?php endforeach; ?>
    </ol>
    <p class="fv-apollo-r345__footer">NASA documentary links are not a grant of commercial media rights. This source comparison embeds no NASA images, map pins, endorsements or sales solicitations.</p>
  </div>
</section>
<?php return (string)ob_get_clean();
}
