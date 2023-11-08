CREATE TABLE `key_wrapping_keys` (
	`user_id` char(36) NOT NULL,
	`public_key` varchar(4096),
	`encrypted_private_key` varchar(4096) NOT NULL,
	PRIMARY KEY (`user_id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;