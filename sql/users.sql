CREATE TABLE `users` (
    `id` char(36) NOT NULL,
    `status` enum(
        'need_sign_up',
        'unconfirmed',
        'confirmed',
        'deactivated'
    ),
    `email` char(255) NOT NULL,
    `secondary_email` char(255),
    `email_verified` tinyint(1),
    `email_verification_code` int(6),
    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    PRIMARY KEY (`id`),
    UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;