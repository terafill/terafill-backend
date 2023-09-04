CREATE TABLE `srp_data` (
	`user_id` varchar(128) NOT NULL,
	`verifier` text,
	`salt` text,
	PRIMARY KEY (`user_id`)
) ENGINE InnoDB,
CHARSET utf8mb4,
COLLATE utf8mb4_0900_ai_ci;