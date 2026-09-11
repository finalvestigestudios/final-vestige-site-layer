<?php
$scenario = $argv[1] ?? '';
$store = $argv[2] ?? sys_get_temp_dir() . '/fvdb-options.json';
$root = getenv('FVDB_TEST_ROOT') ?: (sys_get_temp_dir() . '/fvdb-runtime-' . getmypid());
@mkdir($root . '/wp/wp-admin/includes', 0777, true);
@mkdir($root . '/content/plugins', 0777, true);
file_put_contents($root . '/wp/wp-admin/includes/file.php', "<?php\n");
file_put_contents($root . '/wp/wp-admin/includes/plugin.php', "<?php\n");
define('ABSPATH', $root . '/wp/');
define('WP_CONTENT_DIR', $root . '/content');
define('WP_PLUGIN_DIR', $root . '/content/plugins');
define('FVDB_VERSION', '0.3.1');
define('FVDB_EXPECTED_REPOSITORY', 'finalvestigestudios/final-vestige-site-layer');
define('FVDB_EXPECTED_BRANCH', 'production');
define('FVDB_TARGET_SLUG', 'final-vestige-site-layer');
define('FVDB_TARGET_MAIN', 'final-vestige-site-layer.php');
define('FVDB_REST_NAMESPACE', 'fv-deploy/v1');
if (in_array($scenario, ['target_swap_rollback', 'post_swap_rollback'], true)) {
    define('FVDB_TEST_FAILPOINT', $scenario === 'target_swap_rollback' ? 'target_swap' : 'post_swap_verify');
}

final class WP_Error {
    public function __construct(private string $code, private string $message) {}
    public function get_error_code(): string { return $this->code; }
    public function get_error_message(): string { return $this->message; }
}
function is_wp_error($v): bool { return $v instanceof WP_Error; }
final class WP_REST_Request {
    public function __construct(private array $headers = [], private string $body = '') {}
    public function get_header($name): string { return (string)($this->headers[strtolower($name)] ?? ''); }
    public function get_body(): string { return $this->body; }
}
final class WP_REST_Response {
    public function __construct(public array $data, public int $status = 200) {}
}
function trailingslashit($p): string { return rtrim((string)$p, '/\\') . '/'; }
function wp_tempnam($name) { return tempnam(sys_get_temp_dir(), 'fvdb_'); }
function wp_mkdir_p($dir): bool { return is_dir($dir) || @mkdir($dir, 0777, true); }
function wp_generate_password($len = 12): string { return substr(hash('sha256', uniqid('', true)), 0, $len); }
function get_filesystem_method(): string { return 'direct'; }
function wp_json_encode($v, $flags = 0): string { return json_encode($v, $flags); }
function register_activation_hook(...$a): void {}
function add_action(...$a): void {}
function register_rest_route(...$a): void {}
function __return_true(): bool { return true; }
function is_plugin_active($plugin): bool { return false; }
function wp_cache_delete($key, $group = ''): bool { return true; }
function maybe_serialize($value) {
    if (is_array($value) || is_object($value)) return serialize($value);
    return (string)$value;
}
function maybe_unserialize($value) {
    if (!is_string($value)) return $value;
    $trim = trim($value);
    if ($trim === 'N;' || preg_match('/^[aObisdC]:/', $trim)) {
        $decoded = @unserialize($value);
        if ($decoded !== false || $value === 'b:0;') return $decoded;
    }
    return $value;
}

function store_tx(callable $fn) {
    global $store;
    $fh = fopen($store, 'c+');
    if (!$fh) { throw new RuntimeException('store open failed'); }
    flock($fh, LOCK_EX);
    rewind($fh);
    $raw = stream_get_contents($fh);
    $data = $raw ? json_decode($raw, true) : [];
    if (!is_array($data)) { $data = []; }
    [$data, $result] = $fn($data);
    rewind($fh); ftruncate($fh, 0); fwrite($fh, json_encode($data)); fflush($fh); flock($fh, LOCK_UN); fclose($fh);
    return $result;
}
function get_option($key, $default = false) {
    return store_tx(function($d) use ($key, $default) { return [$d, array_key_exists($key, $d) ? $d[$key] : $default]; });
}
function update_option($key, $value, $autoload = null): bool {
    return store_tx(function($d) use ($key, $value) { $d[$key] = $value; return [$d, true]; });
}
function add_option($key, $value = '', $deprecated = '', $autoload = 'yes'): bool {
    return store_tx(function($d) use ($key, $value) { if (array_key_exists($key, $d)) return [$d, false]; $d[$key] = $value; return [$d, true]; });
}
function delete_option($key): bool {
    return store_tx(function($d) use ($key) { $had = array_key_exists($key, $d); unset($d[$key]); return [$d, $had]; });
}
function fvdb_test_barrier_after_raw_read(string $key): void {
    $dir = getenv('FVDB_TEST_BARRIER_DIR') ?: '';
    $prefix = getenv('FVDB_TEST_BARRIER_KEY_PREFIX') ?: '';
    $count = (int)(getenv('FVDB_TEST_BARRIER_COUNT') ?: 0);
    if ($dir === '' || $prefix === '' || $count < 2 || !str_starts_with($key, $prefix)) return;
    if (!is_dir($dir)) @mkdir($dir, 0777, true);
    file_put_contents($dir . '/' . getmypid(), $key);
    $deadline = microtime(true) + 8.0;
    while (count(glob($dir . '/*') ?: []) < $count) {
        if (microtime(true) > $deadline) throw new RuntimeException('barrier timeout for ' . $key);
        usleep(10000);
    }
}
function fvdb_decode_prepared(string $prepared): array {
    if (!str_starts_with($prepared, 'FVDB_PREP:')) throw new RuntimeException('unexpected SQL in test');
    $decoded = json_decode((string)base64_decode(substr($prepared, 10), true), true);
    if (!is_array($decoded) || !isset($decoded['args']) || !is_array($decoded['args'])) throw new RuntimeException('bad prepared SQL');
    return $decoded;
}
final class FVDB_Test_WPDB {
    public string $options = 'wp_options';
    public function prepare(string $query, ...$args): string {
        return 'FVDB_PREP:' . base64_encode(json_encode(['query'=>$query, 'args'=>$args], JSON_UNESCAPED_SLASHES));
    }
    public function get_var(string $prepared) {
        $decoded = fvdb_decode_prepared($prepared);
        $key = (string)($decoded['args'][0] ?? '');
        $raw = store_tx(function($d) use ($key) {
            $value = array_key_exists($key, $d) ? maybe_serialize($d[$key]) : null;
            return [$d, $value];
        });
        fvdb_test_barrier_after_raw_read($key);
        return $raw;
    }
    public function query(string $prepared): int {
        $decoded = fvdb_decode_prepared($prepared);
        $key = (string)($decoded['args'][0] ?? '');
        $expected = (string)($decoded['args'][1] ?? '');
        return store_tx(function($d) use ($key, $expected) {
            if (!array_key_exists($key, $d) || maybe_serialize($d[$key]) !== $expected) return [$d, 0];
            unset($d[$key]);
            return [$d, 1];
        });
    }
}
$wpdb = new FVDB_Test_WPDB();

function test_critical_enter(): void {
    store_tx(function($d) {
        $active = (int)($d['__critical_active'] ?? 0) + 1;
        $d['__critical_active'] = $active;
        $d['__critical_max'] = max((int)($d['__critical_max'] ?? 0), $active);
        return [$d, null];
    });
}
function test_critical_leave(): void {
    store_tx(function($d) {
        $d['__critical_active'] = max(0, (int)($d['__critical_active'] ?? 0) - 1);
        return [$d, null];
    });
}

if (!class_exists('ZipArchive')) {
    final class ZipArchive {
        public const RDONLY = 16;
        public int $numFiles = 0;
        private array $entries = [];
        public function open($path, $flags = 0) {
            $decoded = json_decode((string)@file_get_contents($path), true);
            if (!is_array($decoded) || !isset($decoded['entries']) || !is_array($decoded['entries'])) return false;
            $this->entries = array_values($decoded['entries']);
            $this->numFiles = count($this->entries);
            return true;
        }
        public function statIndex($i) {
            if (!isset($this->entries[$i])) return false;
            $e = $this->entries[$i];
            $content = (string)($e['content'] ?? '');
            return [
                'name' => (string)($e['name'] ?? ''),
                'size' => isset($e['size']) ? (int)$e['size'] : strlen($content),
                'encryption_method' => (int)($e['encryption_method'] ?? 0),
            ];
        }
        public function getStream($name) {
            foreach ($this->entries as $e) {
                if (($e['name'] ?? '') === $name) {
                    $s = fopen('php://temp', 'w+b'); fwrite($s, (string)($e['content'] ?? '')); rewind($s); return $s;
                }
            }
            return false;
        }
        public function close(): bool { return true; }
    }
}

$base = dirname(__DIR__) . '/final-vestige-deployment-bridge/includes';
require_once $base . '/class-fvdb-state.php';
require_once $base . '/class-fvdb-auth.php';
require_once $base . '/class-fvdb-lock.php';
require_once $base . '/class-fvdb-package.php';
require_once $base . '/class-fvdb-core.php';

function valid_spec(string $commit, array $extra = [], ?string $manifest_commit = null): string {
    $main = "<?php\n// site layer test\n";
    $manifest = json_encode([
        'repository' => FVDB_EXPECTED_REPOSITORY,
        'branch' => FVDB_EXPECTED_BRANCH,
        'commit' => $manifest_commit ?? $commit,
        'files' => [['path' => FVDB_TARGET_MAIN, 'sha256' => hash('sha256', $main)]],
    ], JSON_UNESCAPED_SLASHES);
    $entries = [
        ['name' => FVDB_TARGET_SLUG . '/' . FVDB_TARGET_MAIN, 'content' => $main],
        ['name' => FVDB_TARGET_SLUG . '/release-manifest.json', 'content' => $manifest],
    ];
    foreach ($extra as $e) $entries[] = $e;
    return json_encode(['entries' => $entries], JSON_UNESCAPED_SLASHES);
}
function call_package(string $bytes, string $commit) {
    return FVDB_Package::install_from_base64(base64_encode($bytes), hash('sha256', $bytes), $commit);
}
function code_of($v): string { return is_wp_error($v) ? $v->get_error_code() : 'OK'; }
function assert_true($cond, string $message): void { if (!$cond) { fwrite(STDERR, "ASSERT FAIL: $message\n"); exit(2); } }

if ($scenario === 'replay_worker') {
    $secret = $argv[3]; $ts = $argv[4]; $nonce = $argv[5]; $commit = $argv[6]; $bodySha = $argv[7]; $sig = $argv[8];
    update_option('fvdb_secret_v1', $secret, false);
    $r = FVDB_Auth::authenticate_deploy(['timestamp'=>$ts,'nonce'=>$nonce,'repository'=>FVDB_EXPECTED_REPOSITORY,'branch'=>FVDB_EXPECTED_BRANCH,'commit'=>$commit,'signature'=>$sig], $bodySha);
    echo is_wp_error($r) ? $r->get_error_code() : 'OK';
    exit;
}
if ($scenario === 'lock_worker' || $scenario === 'stale_lock_worker') {
    $token = FVDB_Lock::acquire($scenario === 'lock_worker' ? 'same-idempotency-key' : 'stale-takeover-idempotency-key');
    if (is_wp_error($token)) { echo $token->get_error_code(); exit; }
    test_critical_enter();
    echo 'ACQUIRED'; fflush(STDOUT);
    usleep($scenario === 'stale_lock_worker' ? 800000 : 350000);
    test_critical_leave();
    FVDB_Lock::release($token);
    exit;
}

$commit = str_repeat('a', 40);
if ($scenario === 'package_valid') {
    $r = call_package(valid_spec($commit), $commit);
    assert_true(code_of($r) === 'OK', 'valid package should deploy');
    assert_true(FVDB_Package::installed_matches($commit) === true, 'installed release must verify');
    echo 'PASS'; exit;
}
if ($scenario === 'unsafe_path') {
    $bytes = valid_spec($commit, [['name'=>FVDB_TARGET_SLUG . '/../evil.php','content'=>'x']]);
    assert_true(code_of(call_package($bytes, $commit)) === 'unsafe_zip_path', 'path traversal rejected'); echo 'PASS'; exit;
}
if ($scenario === 'duplicate_entry') {
    $main = "<?php\n";
    $manifest = json_encode(['repository'=>FVDB_EXPECTED_REPOSITORY,'branch'=>FVDB_EXPECTED_BRANCH,'commit'=>$commit,'files'=>[['path'=>FVDB_TARGET_MAIN,'sha256'=>hash('sha256',$main)]]]);
    $bytes = json_encode(['entries'=>[
        ['name'=>FVDB_TARGET_SLUG . '/' . FVDB_TARGET_MAIN,'content'=>$main],
        ['name'=>FVDB_TARGET_SLUG . '/' . FVDB_TARGET_MAIN,'content'=>$main],
        ['name'=>FVDB_TARGET_SLUG . '/release-manifest.json','content'=>$manifest],
    ]]);
    assert_true(code_of(call_package($bytes, $commit)) === 'duplicate_zip_entry', 'duplicate rejected'); echo 'PASS'; exit;
}
if ($scenario === 'encrypted_entry') {
    $bytes = valid_spec($commit, [['name'=>FVDB_TARGET_SLUG . '/secret.bin','content'=>'x','encryption_method'=>99]]);
    assert_true(code_of(call_package($bytes, $commit)) === 'encrypted_zip_rejected', 'encrypted entry rejected'); echo 'PASS'; exit;
}
if ($scenario === 'malformed_zip') {
    $bytes = 'not-a-zip'; assert_true(code_of(call_package($bytes, $commit)) === 'zip_open_failed', 'malformed archive rejected'); echo 'PASS'; exit;
}
if ($scenario === 'oversized_zip') {
    $bytes = str_repeat('A', 5242881); assert_true(code_of(call_package($bytes, $commit)) === 'package_too_large', 'compressed size limit'); echo 'PASS'; exit;
}
if ($scenario === 'expanded_zip') {
    $bytes = valid_spec($commit, [['name'=>FVDB_TARGET_SLUG . '/huge.bin','content'=>'x','size'=>20971521]]);
    assert_true(code_of(call_package($bytes, $commit)) === 'zip_limits_exceeded', 'expanded size limit'); echo 'PASS'; exit;
}
if ($scenario === 'manifest_mismatch') {
    $bytes = valid_spec($commit, [], str_repeat('b', 40));
    assert_true(code_of(call_package($bytes, $commit)) === 'manifest_commit_mismatch', 'manifest commit mismatch rejected'); echo 'PASS'; exit;
}
if ($scenario === 'target_swap_rollback' || $scenario === 'post_swap_rollback') {
    $target = WP_PLUGIN_DIR . '/' . FVDB_TARGET_SLUG; @mkdir($target, 0777, true); file_put_contents($target . '/old-marker.txt', 'old');
    $r = call_package(valid_spec($commit), $commit);
    $expected = $scenario === 'target_swap_rollback' ? 'target_swap_failed' : 'post_swap_verification_failed';
    assert_true(code_of($r) === $expected, 'expected failpoint error');
    assert_true(is_file($target . '/old-marker.txt') && file_get_contents($target . '/old-marker.txt') === 'old', 'old target restored');
    echo 'PASS'; exit;
}
if ($scenario === 'auth_stale_bad') {
    $secret = str_repeat('a', 64); update_option('fvdb_secret_v1', $secret, false); $nonce='nonce_abcdefghijklmnop'; $bodySha=hash('sha256','{}');
    $stale = time()-1000; $canonical = implode("\n", [(string)$stale,$nonce,FVDB_EXPECTED_REPOSITORY,FVDB_EXPECTED_BRANCH,$commit,$bodySha]);
    $sig='sha256='.hash_hmac('sha256',$canonical,$secret);
    $r=FVDB_Auth::authenticate_deploy(['timestamp'=>(string)$stale,'nonce'=>$nonce,'repository'=>FVDB_EXPECTED_REPOSITORY,'branch'=>FVDB_EXPECTED_BRANCH,'commit'=>$commit,'signature'=>$sig],$bodySha);
    assert_true(code_of($r)==='stale_request','stale request rejected');
    $ts=time(); $r=FVDB_Auth::authenticate_deploy(['timestamp'=>(string)$ts,'nonce'=>$nonce.'x','repository'=>FVDB_EXPECTED_REPOSITORY,'branch'=>FVDB_EXPECTED_BRANCH,'commit'=>$commit,'signature'=>'sha256='.str_repeat('0',64)],$bodySha);
    assert_true(code_of($r)==='signature_mismatch','bad signature rejected'); echo 'PASS'; exit;
}
if ($scenario === 'status_surface') {
    $secret = str_repeat('a', 64); update_option('fvdb_secret_v1', $secret, false); $nonce='statusnonce_abcdefgh'; $ts=time();
    $canonical=implode("\n",[(string)$ts,$nonce,FVDB_EXPECTED_REPOSITORY,FVDB_EXPECTED_BRANCH,'status']); $sig='sha256='.hash_hmac('sha256',$canonical,$secret);
    $req=new WP_REST_Request(['x-fv-timestamp'=>(string)$ts,'x-fv-nonce'=>$nonce,'x-fv-repository'=>FVDB_EXPECTED_REPOSITORY,'x-fv-branch'=>FVDB_EXPECTED_BRANCH,'x-fv-signature'=>$sig]);
    $resp=FVDB_Core::status($req); assert_true($resp->status===200,'signed status succeeds');
    $keys=array_keys($resp->data); sort($keys); assert_true($keys===['bridge_version','host_capability','ok'],'status surface minimal');
    $bad=new WP_REST_Request([]); $badResp=FVDB_Core::status($bad); assert_true($badResp->status===401 && ($badResp->data['error']??'')==='authentication_failed','unsigned status rejected');
    echo 'PASS'; exit;
}

fwrite(STDERR, "Unknown scenario\n"); exit(3);