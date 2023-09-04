CREATE TABLE `key_wrapping_keys` (
	`user_id` varchar(128) NOT NULL,
	`public_key` text,
	`encrypted_private_key` text NOT NULL,
	PRIMARY KEY (`user_id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;