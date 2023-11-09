CREATE TABLE `srp_data` (
	`user_id` char(36),
	`verifier` varchar(512),
	`salt` varchar(256),
	PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;