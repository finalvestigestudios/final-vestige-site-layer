<?php
/**
 * Plugin Name: FV Apollo Chronology Rail — isolated Research Prototype
 * Description: Text-first evidence chronology from NASA Apollo 204 records. No deployment permission.
 * Version: 0.0.1-research
 * Requires PHP: 7.4
 */
if (!defined('ABSPATH')) { exit; }

/** Dates/times are NASA report markers, not interpolated events or a fire-origin model. */
function fv_apollo_r339_chronology(): array {
    $board = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
    $aftermath = 'https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/';
    return array(
        array('time' => '23:31:04.7', 'datetime' => '1967-01-27T23:31:04.7Z', 'event' => 'First reported emergency', 'class' => 'Voice record', 'certainty' => 'Recorded transmission onset', 'description' => 'The first transmission indicating an emergency began. The initial words and the speaker cannot be identified with certainty.', 'boundary' => 'This is the first recorded fire report, not a proven time of ignition.', 'source' => $board, 'source_label' => 'Apollo 204 Review Board — voice record'),
        array('time' => 'About 23:31:12', 'datetime' => '', 'event' => 'Rapid fire development', 'class' => 'Board reconstruction', 'certainty' => 'Approximate finding', 'description' => 'The Board assessed that the fire had spread beyond its point of origin by about this time.', 'boundary' => 'An approximate investigative reconstruction, not a separately measured flame-front position.', 'source' => $board, 'source_label' => 'Apollo 204 Review Board — stages of the fire'),
        array('time' => '23:31:16.8', 'datetime' => '1967-01-27T23:31:16.8Z', 'event' => 'Final voice transmission begins', 'class' => 'Voice record', 'certainty' => 'Recorded transmission onset', 'description' => 'The final crew transmission began. NASA cautioned that no definitive transcription of its garbled content was possible.', 'boundary' => 'Do not present any popular rendition of the crew’s last words as a verbatim verified quotation.', 'source' => $board, 'source_label' => 'Apollo 204 Review Board — voice analysis'),
        array('time' => 'About 23:31:19', 'datetime' => '', 'event' => 'Pressure vessel rupture', 'class' => 'Instrument/Board finding', 'certainty' => 'Approximate event time', 'description' => 'The command module cabin ruptured at an estimated internal pressure of at least 29 psia.', 'boundary' => 'The rupture time and pressure are estimates based on the surviving instrument record.', 'source' => $board, 'source_label' => 'Apollo 204 Review Board — cabin pressure'),
        array('time' => '23:31:22.4', 'datetime' => '1967-01-27T23:31:22.4Z', 'event' => 'Telemetry ends', 'class' => 'Recorded signal boundary', 'certainty' => 'Recorded end of signal', 'description' => 'Transmission of voice and spacecraft data had ceased. The Board warned that precise timing of later events was not possible.', 'boundary' => 'Do not extrapolate a precise sensor-based animation beyond the loss of telemetry.', 'source' => $board, 'source_label' => 'Apollo 204 Review Board — recorded sequence'),
        array('time' => 'Following the 1967 fire', 'datetime' => '', 'event' => 'Safety redesign', 'class' => 'Later institutional history', 'certainty' => 'Post-incident period, not an exact event clock', 'description' => 'NASA replaced the difficult three-part hatch with a unified outward-opening hatch and changed spacecraft materials and wiring protections.', 'boundary' => 'This is a subsequent engineering response, not evidence that an exact fire initiator was identified.', 'source' => $aftermath, 'source_label' => 'NASA — The Apollo 1 Fire and its Aftermath'),
    );
}

function fv_apollo_r339_shortcode($atts = array()): string {
    static $instance = 0;
    $instance++;
    $prefix = 'fv-apollo-r339-' . $instance;
    $events = fv_apollo_r339_chronology();
    $free = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/';
    $e = function ($value): string { return htmlspecialchars((string) $value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); };
    ob_start();
    ?>
<section class="fv-apollo-r339" aria-labelledby="<?php echo $e($prefix); ?>-heading" data-fv-r339>
  <div class="fv-apollo-r339__inner">
    <p class="fv-apollo-r339__eyebrow">FINAL VESTIGE STUDIOS / APOLLO 1 / SOURCE CHRONOLOGY</p>
    <h2 id="<?php echo $e($prefix); ?>-heading">The seconds we can document.</h2>
    <p class="fv-apollo-r339__intro">January 27, 1967. These are selected markers from NASA’s Apollo 204 Review Board and a later NASA history, not a continuous fire simulation. Exact recordings, approximate findings, and later interpretations are identified separately.</p>
    <nav aria-label="Jump to a documented Apollo 1 event" class="fv-apollo-r339__nav"><ol>
      <?php foreach ($events as $i => $item): ?>
      <li><a href="#<?php echo $e($prefix . '-event-' . ($i + 1)); ?>"><span><?php echo $e($item['time']); ?><?php if ($i !== 5): ?> GMT<?php endif; ?></span><small><?php echo $e($item['event']); ?></small></a></li>
      <?php endforeach; ?>
    </ol></nav>
    <ol class="fv-apollo-r339__events">
      <?php foreach ($events as $i => $item): ?>
      <li class="fv-apollo-r339__event" id="<?php echo $e($prefix . '-event-' . ($i + 1)); ?>">
        <div class="fv-apollo-r339__time"><?php if ($item['datetime'] !== ''): ?><time datetime="<?php echo $e($item['datetime']); ?>"><?php echo $e($item['time']); ?> GMT</time><?php else: ?><?php echo $e($item['time']); ?><?php if ($i !== 5): ?> GMT<?php endif; ?><?php endif; ?></div>
        <div class="fv-apollo-r339__record"><p class="fv-apollo-r339__type"><?php echo $e($item['class']); ?> · <?php echo $e($item['certainty']); ?></p>
        <h3><?php echo $e($item['event']); ?></h3><p><?php echo $e($item['description']); ?></p>
        <details class="fv-apollo-r339__source"><summary>Source and evidence limits</summary><p><?php echo $e($item['boundary']); ?></p><p><a href="<?php echo $e($item['source']); ?>" rel="noopener noreferrer" data-fv-r339-source="<?php echo $i === 5 ? 'later-nasa-history' : 'original-board'; ?>"><?php echo $e($item['source_label']); ?></a></p></details>
        </div>
      </li>
      <?php endforeach; ?>
    </ol>
    <p class="fv-apollo-r339__caution">The Board identified an electrical arc as the most probable initiator, but did not conclusively identify any single ignition source. Linked NASA material is evidence, not automatic authorization for commercial imagery, marks, likenesses or endorsement. No NASA images or geo-coordinates are embedded here.</p>
    <p class="fv-apollo-r339__continuation"><a href="<?php echo $e($free); ?>" data-fv-r339-cta="editorial">Read the complete Apollo 1 investigation</a></p>
  </div>
</section>
    <?php
    return (string) ob_get_clean();
}
if (function_exists('add_shortcode')) {
    add_shortcode('fv_apollo_chronology_r339', 'fv_apollo_r339_shortcode');
}
