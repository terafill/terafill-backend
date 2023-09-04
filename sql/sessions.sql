CREATE TABLE `sessions` (
    `id` varchar(128) NOT NULL,
    `user_id` varchar(128) NOT NULL,
    `client_id` varchar(128) NOT NULL,
    `client_type` varchar(128),
    `platform_client_id` varchar(128) NOT NULL,
    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    `expiry_at` datetime NOT NULL DEFAULT current_timestamp(),
    `session_private_key` text NOT NULL,
    `session_srp_server_private_key` text NOT NULL,
    `session_srp_client_public_key` text NOT NULL,
    `session_token` text NOT NULL,
    `session_encryption_key` text NOT NULL,
    `activated` tinyint(1),
    PRIMARY KEY (`id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;