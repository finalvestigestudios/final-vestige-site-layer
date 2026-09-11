<?php
defined('ABSPATH') || exit;

final class FVDB_Lock {
    private const OPTION_LOCK = 'fvdb_deployment_mutex_v1';
    private const TTL = 900;

    public static function acquire(string $idempotency_key) {
        $token = bin2hex(random_bytes(16));
        $value = [
            'token' => $token,
            'idempotency_key' => $idempotency_key,
            'expires' => time() + self::TTL,
        ];

        if (add_option(self::OPTION_LOCK, $value, '', false)) {
            return $token;
        }

        $existing = get_option(self::OPTION_LOCK, []);
        $expires = is_array($existing) ? (int) ($existing['expires'] ?? 0) : 0;
        if ($expires > 0 && $expires < time()) {
            delete_option(self::OPTION_LOCK);
            if (add_option(self::OPTION_LOCK, $value, '', false)) {
                return $token;
            }
        }
        return new WP_Error('deployment_busy', 'Another authenticated deployment currently owns the deployment mutex.');
    }

    public static function release(string $token): void {
        $existing = get_option(self::OPTION_LOCK, []);
        if (is_array($existing) && hash_equals((string) ($existing['token'] ?? ''), $token)) {
            delete_option(self::OPTION_LOCK);
        }
    }
}
