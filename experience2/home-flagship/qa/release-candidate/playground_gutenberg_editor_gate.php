<?php
/**
 * FV EX2 Gutenberg EDITOR SAVE gate for an isolated disposable Playground.
 * NEVER upload, include, or run this file on WordPress.com or a real website.
 * Requires loopback WordPress, a synthetic-environment marker and fresh token.
 * The payload contains only 72 PUBLIC page-6 Margins texts plus mock Jetpack;
 * do not label those real public records as invented synthetic text.
 * POST-only create/login/verify/cleanup; one temporary draft, never publish.
 */
header('Content-Type: application/json; charset=utf-8');
require_once __DIR__ . '/wp-load.php';

function fv_ex2_editor_reply($status, $body) {
    http_response_code($status);
    echo wp_json_encode($body);
    exit;
}
function fv_ex2_editor_refuse($reason) {
    fv_ex2_editor_reply(422, array('result'=>'FAIL','reason'=>$reason,'release'=>'HOLD'));
}
function fv_ex2_editor_loopback_host($value) {
    $parsed = wp_parse_url('http://' . $value, PHP_URL_HOST);
    return in_array(strtolower((string)$parsed), array('127.0.0.1','localhost','::1'), true);
}

// Playground VFS /tmp is outside the HTTP-served /wordpress tree.
// Never expose the disposable authentication token or unreleased candidate as web assets.
$marker = '/tmp/fv-ex2-synthetic-only.marker';
$token_file = '/tmp/fv-ex2-editor-token';
$candidate_path = '/tmp/fv-ex2-synthetic-candidate.html';
$id_file = '/tmp/fv-ex2-editor-draft-id';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') fv_ex2_editor_refuse('POST required');
if (!fv_ex2_editor_loopback_host((string)($_SERVER['HTTP_HOST'] ?? ''))
    || !fv_ex2_editor_loopback_host((string)wp_parse_url(home_url(), PHP_URL_HOST))) {
    fv_ex2_editor_refuse('Only disposable loopback WordPress is accepted');
}
if (!is_file($marker) || trim((string)file_get_contents($marker)) !== 'SYNTHETIC_TEST_FIXTURE_ONLY') {
    fv_ex2_editor_refuse('Synthetic-only marker missing');
}
if (!is_file($token_file)) fv_ex2_editor_refuse('Session token missing');
$expected_token = trim((string)file_get_contents($token_file));
$given_token = (string)($_SERVER['HTTP_X_FV_EX2_EDITOR_TOKEN'] ?? '');
if (strlen($expected_token) !== 64 || !ctype_xdigit($expected_token)
    || !hash_equals($expected_token, $given_token)) {
    fv_ex2_editor_refuse('Invalid disposable QA token');
}
$action = (string)($_GET['action'] ?? '');

if ($action === 'create') {
    if (is_file($id_file)) fv_ex2_editor_refuse('A synthetic draft already exists');
    if (!is_file($candidate_path)) fv_ex2_editor_refuse('Synthetic candidate absent');
    $source = file_get_contents($candidate_path);
    if (!is_string($source) || strlen($source) < 1000
        || strpos($source, 'FV-EX2 PAGE6 REVIEW-ONLY') === false
        || substr_count($source, 'jetpack/subscriptions') !== 1
        || substr_count($source, 'Focus Fieldbook') < 1
        || preg_match_all('/<span class="fv-margin-strip__item" style="--i:\d+">/', $source) !== 72
        || !str_contains($source, 'fv-hf__chapter-nav')) {
        fv_ex2_editor_refuse('Synthetic candidate fails invariants');
    }
    // WordPress KSES will silently rewrite custom HTML for anonymous
    // inserts. Only after loopback/token/marker checks, bind the disposable
    // WordPress admin to this local synthetic-only request.
    $admins = get_users(array('role'=>'administrator','number'=>1,'fields'=>'all'));
    if (count($admins) !== 1 || !isset($admins[0]->ID)) {
        fv_ex2_editor_refuse('Isolated administrator unavailable');
    }
    wp_set_current_user((int)$admins[0]->ID);
    if (!current_user_can('unfiltered_html')) {
        fv_ex2_editor_refuse('Isolated editor lacks unfiltered_html capability');
    }
    $id = wp_insert_post(array(
        'post_type'=>'page',
        'post_title'=>'FV EX2 SYNTHETIC EDITOR PRE-SAVE',
        'post_status'=>'draft',
        'post_content'=>wp_slash($source)
    ), true);
    if (is_wp_error($id) || !is_int($id) || $id < 1) {
        fv_ex2_editor_refuse('Could not insert disposable draft');
    }
    // Title may change in Gutenberg. Own the draft via a private HMAC marker
    // bound to this one-time token and inserted ID, never by its editable title.
    $proof = hash_hmac('sha256', (string)$id, $expected_token);
    if (!add_post_meta($id, '_fv_ex2_editor_qa_owner', $proof, true)) {
        wp_delete_post($id, true);
        fv_ex2_editor_refuse('Could not establish draft ownership');
    }
    if (file_put_contents($id_file, (string)$id, LOCK_EX) === false) {
        wp_delete_post($id, true);
        fv_ex2_editor_refuse('Could not track disposable draft');
    }
    fv_ex2_editor_reply(200, array(
        'result'=>'CREATED','draft_id'=>$id,'release'=>'HOLD',
        'source_sha256'=>hash('sha256', $source),
        'data_class'=>'PUBLIC_PAGE6_MARGINS_WITH_SYNTHETIC_JETPACK_FIXTURE'
    ));
}
if ($action === 'login') {
    $admins = get_users(array('role'=>'administrator','number'=>1,'fields'=>'all'));
    if (count($admins) !== 1 || !isset($admins[0]->ID)) {
        fv_ex2_editor_refuse('No isolated Playground administrator');
    }
    wp_set_current_user((int)$admins[0]->ID);
    wp_set_auth_cookie((int)$admins[0]->ID, true, is_ssl());
    fv_ex2_editor_reply(200, array('result'=>'LOGIN_SET','release'=>'HOLD'));
}
if ($action === 'verify' || $action === 'cleanup') {
    if (!is_file($id_file)) fv_ex2_editor_refuse('Disposable draft identifier missing');
    $id_str = trim((string)file_get_contents($id_file));
    if (!preg_match('/^[1-9]\d*$/D', $id_str)) fv_ex2_editor_refuse('Invalid disposable draft identifier');
    $id = (int)$id_str;
    $post = get_post($id);
    $owner = get_post_meta($id, '_fv_ex2_editor_qa_owner', true);
    $proof = hash_hmac('sha256', (string)$id, $expected_token);
    if (!$post || $post->post_type !== 'page'
        || !is_string($owner) || !hash_equals($proof, $owner)) {
        fv_ex2_editor_refuse('Refusing an unowned disposable WordPress page');
    }
    // Delete only an HMAC-owned fixture even if Gutenberg accidentally
    // changed its status. Verification still fails on any non-draft status.
    if ($action === 'cleanup') {
        $deleted = wp_delete_post($id, true);
        clean_post_cache($id);
        $absent = !get_post($id);
        if (!$deleted || !$absent) fv_ex2_editor_refuse('Draft cleanup not verified');
        @unlink($id_file);
        fv_ex2_editor_reply(200, array('result'=>'DELETED','verified_absent'=>true,'release'=>'HOLD'));
    }
    if ($post->post_status !== 'draft') fv_ex2_editor_refuse('Disposable page no longer a draft');
    if (!is_file($candidate_path)) fv_ex2_editor_refuse('Candidate disappeared before verification');
    $source = file_get_contents($candidate_path);
    clean_post_cache($id);
    $stored = get_post_field('post_content', $id, 'raw');
    if (!is_string($source) || !is_string($stored)) fv_ex2_editor_refuse('Raw source unavailable');
    $checks = array(
        'editor_saved_title'=>get_post_field('post_title',$id,'raw') === 'FV EX2 SYNTHETIC EDITOR SAVED',
        'draft_not_published'=>get_post_status($id) === 'draft',
        'byte_exact_after_editor_save'=>hash_equals(hash('sha256',$source),hash('sha256',$stored)),
        'seventy_two_margins'=>preg_match_all('/<span class="fv-margin-strip__item" style="--i:\d+">/', $stored) === 72,
        'jetpack_block_comment_once'=>substr_count($stored,'jetpack/subscriptions') === 1,
        'focus_fieldbook_present'=>str_contains($stored,'Focus Fieldbook'),
        'contrast_marker_once'=>substr_count($stored,'FV-EX2 PAGE6 REVIEW-ONLY') === 1,
        'chapter_navigation_present'=>str_contains($stored,'fv-hf__chapter-nav'),
        'gutenberg_blocks_parse'=>count(parse_blocks($stored)) >= 2
    );
    $success = !in_array(false,$checks,true);
    fv_ex2_editor_reply($success ? 200 : 422, array(
        'result'=>$success?'PASS':'FAIL',
        'release'=>'HOLD',
        'test_type'=>'REAL_GUTENBERG_EDITOR_SAVE_SYNTHETIC_PLAYGROUND_ONLY',
        'data_class'=>'PUBLIC_PAGE6_MARGINS_WITH_SYNTHETIC_JETPACK_FIXTURE',
        'source_sha256'=>hash('sha256',$source),
        'stored_sha256'=>hash('sha256',$stored),
        'source_bytes'=>strlen($source),
        'stored_bytes'=>strlen($stored),
        'checks'=>$checks
    ));
}
fv_ex2_editor_refuse('Unsupported action');
