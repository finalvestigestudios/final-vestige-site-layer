<?php
defined('ABSPATH') || exit;

final class FVDB_State {
    private const OPTION_STATE = 'fvdb_state_v1';

    public static function ensure(): void {
        if (get_option(self::OPTION_STATE) === false) {
            update_option(self::OPTION_STATE, [
                'bridge_version' => FVDB_VERSION,
                'last_status' => 'never_deployed',
                'last_commit' => '',
                'last_package_sha256' => '',
                'last_idempotency_key' => '',
                'last_deployed_at' => '',
                'last_error' => '',
            ], false);
        }
    }

    public static function get(): array {
        $state = get_option(self::OPTION_STATE, []);
        return is_array($state) ? $state : [];
    }

    public static function write(array $patch): void {
        $state = array_merge(self::get(), ['bridge_version' => FVDB_VERSION], $patch);
        update_option(self::OPTION_STATE, $state, false);
    }

    public static function record_authenticated_error(string $code, string $message): void {
        self::write([
            'last_status' => 'rejected_or_failed',
            'last_error' => $code . ': ' . $message,
        ]);
    }
}
