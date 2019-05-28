USE db_skale;
CREATE TABLE `report` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `my_id` int unsigned NOT NULL,
  `node_id` int unsigned NOT NULL,
  `is_alive` tinyint(1)  unsigned NOT NULL,
  `latency` int unsigned NOT NULL,
  `stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25158 DEFAULT CHARSET=utf8;

CREATE TABLE `bounty` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `my_id` int unsigned NOT NULL,
  `tx_dt` DATETIME NOT NULL DEFAULT '2000-01-01 00:00:00',
  `tx_hash` CHAR(66) NOT NULL DEFAULT '0x',
  `bounty` VARCHAR(28) unsigned NOT NULL,
  `latency` int unsigned NOT NULL,
  `downtime` int unsigned NOT NULL,
  `gas` int unsigned NOT NULL,
  `stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4196 DEFAULT CHARSET=utf8;

CREATE TABLE `bounty_rcp` (
  `tx_hash` CHAR(66) NOT NULL,
  `eth_balance_before` VARCHAR(28) NULL,
  `skl_balance_before` VARCHAR(28) NULL,
  `eth_balance` VARCHAR(28) NULL,
  `skl_balance` VARCHAR(28) NULL,
  `gas_used` DECIMAL(65) NULL,
  PRIMARY KEY (`tx_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

