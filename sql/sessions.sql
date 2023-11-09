CREATE TABLE `sessions` (
    `id` char(36) NOT NULL,
    `user_id` char(36) NOT NULL,
    `client_id` char(36) NOT NULL,
    `platform_client_id` char(36) NOT NULL,
    `client_type` varchar(64),
    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    `expiry_at` datetime NOT NULL DEFAULT current_timestamp(),
    `session_private_key` varchar(4096) NOT NULL,
    `session_srp_server_private_key` varchar(4096) NOT NULL,
    `session_srp_client_public_key` varchar(4096) NOT NULL,
    `session_token` varchar(1024) NOT NULL,
    `session_encryption_key` varchar(128) NOT NULL,
    `activated` tinyint(1),
    PRIMARY KEY (`id`),
    INDEX `user_id_idx` (`user_id`),
    INDEX `platform_client_id_idx` (`platform_client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;