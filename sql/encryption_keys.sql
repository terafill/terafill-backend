CREATE TABLE `encryption_keys` (
    `item_id` char(36) NOT NULL,
    `user_id` char(36) NOT NULL,
    `encrypted_encryption_key` text NOT NULL,
    PRIMARY KEY (`item_id`),
    INDEX `user_id_idx` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
