CREATE TABLE `custom_item_fields` (
    `id` char(36) NOT NULL,
    `item_id` char(36) NOT NULL,
    `user_id` char(36) NOT NULL,
    `is_tag` tinyint(1) DEFAULT '0',
    `field_value` varchar(255) NOT NULL,
    `field_name` varchar(128) NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `item_id_idx` (`item_id`),
    INDEX `user_id_idx` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;