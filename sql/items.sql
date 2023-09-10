CREATE TABLE `items` (
    `id` char(36),
    `vault_id` char(36) NOT NULL,
    `user_id` char(36) NOT NULL,
    `type` enum(
        'PASSWORD',
        'NOTE',
        'CREDIT_CARD',
        'CRYPTO_WALLET',
        'SSH_KEY',
        'SOFTWARE_LICENSE',
        'WIFI_PASSWORD',
        'DATABASE_CREDENTIAL',
        'DOCUMENT'
    ) NOT NULL,
    `title` varchar(64) NOT NULL,
    `description` varchar(255),
    `username` varchar(128),
    `password` varchar(128),
    `website` varchar(255),
    `tags` json,
    `is_favorite` tinyint(1) DEFAULT '0',
    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (`id`) INDEX `user_id_idx` (`user_id`) INDEX `vault_id_idx` (`vault_id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;