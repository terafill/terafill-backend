CREATE TABLE `vaults` (
    `id` char(36) NOT NULL,
    `user_id` char(36) NOT NULL,
    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    `name` varchar(255) NOT NULL,
    `description` varchar(255),
    `tags` json,
    `is_default` tinyint(1),
    PRIMARY KEY (`id`),
    INDEX `user_id_idx` (`user_id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;