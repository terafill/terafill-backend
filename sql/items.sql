CREATE TABLE `items` (
    `id` varchar(128) NOT NULL,
    `vault_id` varchar(128) NOT NULL,
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
    `title` varchar(255) NOT NULL,
    `description` text,
    `username` varchar(255),
    `password` varchar(255),
    `website` varchar(255),
    `notes` text,
    `tags` json,
    `is_favorite` tinyint(1) DEFAULT '0',
    `creator_id` varchar(128) NOT NULL,
    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (`id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;