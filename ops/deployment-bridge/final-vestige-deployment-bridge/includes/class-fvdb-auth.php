<?php
defined('ABSPATH') || exit;

final class FVDB_Auth {
    private const OPTION_SECRET = 'fvdb_secret_v1';
    private const MAX_SKEW = 300;

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

    public static function authenticate(array $h, string $body_sha) {
        $secret = self::current_secret();
        if (strlen($secret) !== 64 || !ctype_xdigit($secret)) {
            return new WP_Error('bridge_unconfigured', 'Deployment bridge has no valid secret.');
        }
        if (!ctype_digit($h['timestamp'] ?? '')) {
            return new WP_Error('invalid_timestamp', 'Missing or invalid timestamp.');
        }
        $ts = (int) $h['timestamp'];
        if (abs(time() - $ts) > self::MAX_SKEW) {
            return new WP_Error('stale_request', 'Deployment request timestamp is outside the allowed window.');
        }
        $nonce = $h['nonce'] ?? '';
        if (!preg_match('/^[A-Za-z0-9_-]{16,96}$/', $nonce)) {
            return new WP_Error('invalid_nonce', 'Missing or invalid deployment nonce.');
        }
        $nonce_key = 'fvdb_nonce_' . hash('sha256', $nonce);
        if (get_transient($nonce_key)) {
            return new WP_Error('replay_rejected', 'Deployment nonce has already been used.');
        }
        if (($h['repository'] ?? '') !== FVDB_EXPECTED_REPOSITORY) {
            return new WP_Error('repository_rejected', 'Repository is not allowlisted.');
        }
        if (($h['branch'] ?? '') !== FVDB_EXPECTED_BRANCH) {
            return new WP_Error('branch_rejected', 'Branch is not allowlisted.');
        }
        $commit = strtolower((string) ($h['commit'] ?? ''));
        if (!preg_match('/^[a-f0-9]{40}$/', $commit)) {
            return new WP_Error('invalid_commit', 'Commit SHA is invalid.');
        }
        $signature = strtolower((string) ($h['signature'] ?? ''));
        if (!preg_match('/^sha256=[a-f0-9]{64}$/', $signature)) {
            return new WP_Error('invalid_signature', 'Signature header is invalid.');
        }
        $canonical = implode("\n", [
            (string) $ts,
            $nonce,
            FVDB_EXPECTED_REPOSITORY,
            FVDB_EXPECTED_BRANCH,
            $commit,
            $body_sha,
        ]);
        $expected = 'sha256=' . hash_hmac('sha256', $canonical, $secret);
        if (!hash_equals($expected, $signature)) {
            return new WP_Error('signature_mismatch', 'Request signature did not verify.');
        }

        // Burn a valid nonce before any package processing. A signed malformed request may
        // fail, but it cannot be replayed within the acceptance window.
        set_transient($nonce_key, '1', 10 * MINUTE_IN_SECONDS);
        return true;
    }

    private static function new_secret(): string {
        return bin2hex(random_bytes(32));
    }

    private static function store_secret(string $secret): void {
        update_option(self::OPTION_SECRET, $secret, false);
    }
}
