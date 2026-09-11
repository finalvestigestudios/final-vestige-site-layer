<?php
defined('ABSPATH') || exit;

final class FVDB_Auth {
    private const OPTION_SECRET = 'fvdb_secret_v1';
    private const NONCE_PREFIX = 'fvdb_nonce_v2_';
    private const MAX_SKEW = 300;
    private const NONCE_TTL = 600;

    public static function ensure_secret(): void {
        if (!get_option(self::OPTION_SECRET)) {
            self::store_secret(self::new_secret());
        }
    }

    public static function current_secret(): string {
        return (string) get_option(self::OPTION_SECRET, '');
    }

    public static function regenerate_secret(): void {
        self::store_secret(self::new_secret());
    }

    public static function headers(WP_REST_Request $request): array {
        return [
            'timestamp' => trim((string) $request->get_header('x-fv-timestamp')),
            'nonce' => trim((string) $request->get_header('x-fv-nonce')),
            'repository' => trim((string) $request->get_header('x-fv-repository')),
            'branch' => trim((string) $request->get_header('x-fv-branch')),
            'commit' => trim((string) $request->get_header('x-fv-commit')),
            'signature' => trim((string) $request->get_header('x-fv-signature')),
        ];
    }

    public static function authenticate_deploy(array $h, string $body_sha) {
        $common = self::validate_common($h);
        if (is_wp_error($common)) {
            return $common;
        }
        $commit = strtolower((string) ($h['commit'] ?? ''));
        if (!preg_match('/^[a-f0-9]{40}$/', $commit)) {
            return new WP_Error('invalid_commit', 'Commit SHA is invalid.');
        }
        $canonical = implode("\n", [
            (string) $common['timestamp'],
            $common['nonce'],
            FVDB_EXPECTED_REPOSITORY,
            FVDB_EXPECTED_BRANCH,
            $commit,
            $body_sha,
        ]);
        $verified = self::verify_signature($canonical, (string) ($h['signature'] ?? ''));
        if (is_wp_error($verified)) {
            return $verified;
        }
        return self::claim_nonce($common['nonce'], 'deploy');
    }

    public static function authenticate_status(array $h) {
        $common = self::validate_common($h);
        if (is_wp_error($common)) {
            return $common;
        }
        $canonical = implode("\n", [
            (string) $common['timestamp'],
            $common['nonce'],
            FVDB_EXPECTED_REPOSITORY,
            FVDB_EXPECTED_BRANCH,
            'status',
        ]);
        $verified = self::verify_signature($canonical, (string) ($h['signature'] ?? ''));
        if (is_wp_error($verified)) {
            return $verified;
        }
        return self::claim_nonce($common['nonce'], 'status');
    }

    private static function validate_common(array $h) {
        $secret = self::current_secret();
        if (strlen($secret) !== 64 || !ctype_xdigit($secret)) {
            return new WP_Error('bridge_unconfigured', 'Deployment bridge has no valid secret.');
        }
        if (!ctype_digit((string) ($h['timestamp'] ?? ''))) {
            return new WP_Error('invalid_timestamp', 'Missing or invalid timestamp.');
        }
        $ts = (int) $h['timestamp'];
        if (abs(time() - $ts) > self::MAX_SKEW) {
            return new WP_Error('stale_request', 'Deployment request timestamp is outside the allowed window.');
        }
        $nonce = (string) ($h['nonce'] ?? '');
        if (!preg_match('/^[A-Za-z0-9_-]{16,96}$/', $nonce)) {
            return new WP_Error('invalid_nonce', 'Missing or invalid deployment nonce.');
        }
        if (($h['repository'] ?? '') !== FVDB_EXPECTED_REPOSITORY) {
            return new WP_Error('repository_rejected', 'Repository is not allowlisted.');
        }
        if (($h['branch'] ?? '') !== FVDB_EXPECTED_BRANCH) {
            return new WP_Error('branch_rejected', 'Branch is not allowlisted.');
        }
        return ['timestamp' => $ts, 'nonce' => $nonce];
    }

    private static function verify_signature(string $canonical, string $signature) {
        $signature = strtolower($signature);
        if (!preg_match('/^sha256=[a-f0-9]{64}$/', $signature)) {
            return new WP_Error('invalid_signature', 'Signature header is invalid.');
        }
        $expected = 'sha256=' . hash_hmac('sha256', $canonical, self::current_secret());
        if (!hash_equals($expected, $signature)) {
            return new WP_Error('signature_mismatch', 'Request signature did not verify.');
        }
        return true;
    }

    private static function claim_nonce(string $nonce, string $purpose) {
        $key = self::NONCE_PREFIX . hash('sha256', $purpose . "\n" . $nonce);
        $expires = time() + self::NONCE_TTL;

        // add_option is a single INSERT guarded by the unique option_name index, making
        // the first claim atomic across concurrent PHP workers. No get-then-set window.
        if (add_option($key, $expires, '', false)) {
            return true;
        }

        $existing = (int) get_option($key, 0);
        if ($existing > 0 && $existing < time()) {
            delete_option($key);
            if (add_option($key, $expires, '', false)) {
                return true;
            }
        }
        return new WP_Error('replay_rejected', 'Deployment nonce has already been used.');
    }

    private static function new_secret(): string {
        return bin2hex(random_bytes(32));
    }

    private static function store_secret(string $secret): void {
        update_option(self::OPTION_SECRET, $secret, false);
    }
}
