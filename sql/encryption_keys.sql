CREATE TABLE `encryption_keys` (
    `user_id` varchar(128) NOT NULL,
    `item_id` varchar(128) NOT NULL,
    `vault_id` varchar(128) NOT NULL,
    `encrypted_encryption_key` text NOT NULL,
    PRIMARY KEY (`user_id`, `item_id`, `vault_id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;