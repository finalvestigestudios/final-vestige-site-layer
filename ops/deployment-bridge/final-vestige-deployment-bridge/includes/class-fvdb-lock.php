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

        // Read the exact stored bytes and only reclaim an expired lease if those
        // same bytes are still present at deletion time. This closes the stale
        // reader race where worker B could otherwise delete worker A's fresh lock.
        $raw = self::read_raw_option(self::OPTION_LOCK);
        if ($raw !== null) {
            $existing = maybe_unserialize($raw);
            $expires = is_array($existing) ? (int) ($existing['expires'] ?? 0) : 0;
            if ($expires > 0 && $expires < time() && self::compare_delete_option(self::OPTION_LOCK, $raw)) {
                if (add_option(self::OPTION_LOCK, $value, '', false)) {
                    return $token;
                }
            }
        }
        return new WP_Error('deployment_busy', 'Another authenticated deployment currently owns the deployment mutex.');
    }

    public static function release(string $token): void {
        // Release is also compare-delete safe: an expired owner's late release
        // can never delete a successor lease acquired after it read the old row.
        $raw = self::read_raw_option(self::OPTION_LOCK);
        if ($raw === null) {
            return;
        }
        $existing = maybe_unserialize($raw);
        if (is_array($existing) && hash_equals((string) ($existing['token'] ?? ''), $token)) {
            self::compare_delete_option(self::OPTION_LOCK, $raw);
        }
    }

    private static function read_raw_option(string $key): ?string {
        global $wpdb;
        $raw = $wpdb->get_var(
            $wpdb->prepare(
                "SELECT option_value FROM {$wpdb->options} WHERE option_name = %s LIMIT 1",
                $key
            )
        );
        return $raw === null ? null : (string) $raw;
    }

    private static function compare_delete_option(string $key, string $expected_raw): bool {
        global $wpdb;
        $deleted = $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM {$wpdb->options} WHERE option_name = %s AND BINARY option_value = BINARY %s",
                $key,
                $expected_raw
            )
        );
        if ($deleted === 1) {
            wp_cache_delete($key, 'options');
            return true;
        }
        return false;
    }
}
