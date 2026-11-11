<?php
/**
 * FV Apollo R273 editorial source-review custody component — staging-only preview.
 * No WordPress registration, tracking, merchant links or writes.
 * Public source research may be accurate while a separate editorial review is pending.
 */
function fv_ex2_r273_review_panel(array $records): string {
    // Reentrant when a reusable block renders more than one panel.
    // Preserve the first ID for backwards-compatible single-instance previews.
    static $panel_index = 0;
    ++$panel_index;
    $title_id = $panel_index === 1 ? 'fv-r273-title' : 'fv-r273-title-' . $panel_index;
    $allowed = [
        'board' => ['label' => 'Apollo 204 Review Board report', 'url' => 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'],
        'chronology' => ['label' => 'Four recorded chronology markers', 'url' => 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'],
    ];
    $pending = [];
    $rows = [];
    foreach ($allowed as $id => $item) {
        $entry = $records[$id] ?? null;
        // Never turn a self-asserted string into a verified editorial approval.
        // Real review authority is checked outside this staging component.
        $ready = is_array($entry) && ($entry['state'] ?? '') === 'review-recorded'
            && isset($entry['receipt_sha256']) && is_string($entry['receipt_sha256'])
            && preg_match('/^[a-f0-9]{64}$/D', $entry['receipt_sha256']) === 1
            && isset($entry['reviewer'], $entry['review_date'])
            && is_string($entry['reviewer']) && trim($entry['reviewer']) !== ''
            && is_string($entry['review_date']) && preg_match('/^\d{4}-\d{2}-\d{2}$/D', $entry['review_date']) === 1
            && (($date = date_parse_from_format('!Y-m-d', $entry['review_date'])) !== false)
            && ($date['error_count'] === 0) && ($date['warning_count'] === 0)
            && $entry['review_date'] <= gmdate('Y-m-d');
        $status = $ready ? 'Review receipt supplied (self-reported, unverified) — independent acceptance required' : 'Editorial review pending';
        if (!$ready) $pending[] = $id;
        $rows[] = '<li class="fv-r273__record"><span class="fv-r273__record-title">' . htmlspecialchars($item['label'], ENT_QUOTES, 'UTF-8') . '</span>'
            . '<strong class="fv-r273__status">' . $status . '</strong>'
            . '<a href="' . htmlspecialchars($item['url'], ENT_QUOTES, 'UTF-8') . '" target="_blank" rel="noopener noreferrer">Read NASA primary source: ' . htmlspecialchars($item['label'], ENT_QUOTES, 'UTF-8') . ' <span class="fv-r273__external">(opens in new tab)</span></a></li>';
    }
    $headline = count($pending) ? 'Editorial review remains open' : 'Unverified review metadata present';
    $detail = count($pending)
        ? 'Some Atlas review statuses remain pending. The linked NASA documents are available to inspect; a source link is not the same as completed editorial review.'
        : 'Both records contain self-reported receipt identifiers, but no independent reviewer, evidence artifact, rights clearance or release authorization has been authenticated.';
    return '<aside class="fv-r273" aria-labelledby="' . $title_id . '" data-fv-review-ready="false">'
        . '<p class="fv-r273__eyebrow">Apollo 1 · source custody</p>'
        . '<h2 id="' . $title_id . '">' . $headline . '</h2>'
        . '<p class="fv-r273__summary">' . $detail . '</p>'
        . '<details class="fv-r273__disclosure"><summary>Inspect review status and primary sources</summary>'
        . '<p class="fv-r273__shared-source">Both record views cite the same NASA Apollo 204 Review Board report. These are two editorial record categories, not two independent source confirmations.</p>'
        . '<ul class="fv-r273__records">' . implode('', $rows) . '</ul></details>'
        . '<p class="fv-r273__boundary">NASA has not endorsed Final Vestige or any commercial offer. This review note is not a correction to the Review Board findings.</p>'
        . '<p class="fv-r273__next"><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read the free Apollo 1 investigation</a></p>'
        . '</aside>';
}
