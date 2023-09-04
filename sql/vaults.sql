CREATE TABLE `vaults` (
    `id` varchar(128) NOT NULL,
    `creator_id` varchar(128) NOT NULL,
    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    `name` varchar(255) NOT NULL,
    `description` text,
    `tags` json,
    `is_default` tinyint(1),
    PRIMARY KEY (`id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;