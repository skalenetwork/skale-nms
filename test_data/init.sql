USE test;
CREATE TABLE `report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `my_id` int(11) unsigned NOT NULL,
  `node_id` int(11) unsigned NOT NULL,
  `is_alive` tinyint(4) unsigned NOT NULL,
  `latency` int(11) unsigned NOT NULL,
  `stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25158 DEFAULT CHARSET=utf8;

CREATE TABLE `bounty` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tx_dt` DATETIME NOT NULL DEFAULT '2000-01-01 00:00:00',
  `my_id` int(11) unsigned NOT NULL,
  `bounty` DECIMAL(65,0) unsigned NOT NULL,
  `latency` int(11) unsigned NOT NULL,
  `downtime` int(11) unsigned NOT NULL,
  `gas` int(11) unsigned NOT NULL,
  `stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4196 DEFAULT CHARSET=utf8;
