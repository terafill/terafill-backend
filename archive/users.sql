CREATE TABLE `users` (
    `id` varchar(128) NOT NULL,
    `status` enum(
        'need_sign_up',
        'unconfirmed',
        'confirmed',
        'deactivated'
    ),
    `email` varchar(255) NOT NULL,
    `secondary_email` varchar(255),
    -- `phone_no` varchar(20),
    -- `first_name` varchar(50) NOT NULL,
    -- `last_name` varchar(50) NOT NULL,
    -- `birthday` date,
    `email_verified` tinyint(1),
    `email_verification_code` int(6),
    -- `gender` enum(
    --     'male',
    --     'female',
    --     'non-binary',
    --     'transgender',
    --     'genderqueer',
    --     'two-spirit',
    --     'bigender',
    --     'pangender',
    --     'agender',
    --     'demigender',
    --     'third gender',
    --     'androgynous',
    --     'intersex',
    --     'questioning',
    --     'other'
    -- ),
    `created_at` datetime NOT NULL DEFAULT current_timestamp(),
    -- `profile_image` longblob,
    PRIMARY KEY (`id`),
    UNIQUE KEY `email` (`email`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;