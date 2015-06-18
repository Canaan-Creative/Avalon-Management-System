<?php
foreach ([
	'/etc/ams.yaml',
	'/etc/ams/ams.yaml',
	'/home/ams/ams.yaml',
	'/home/archang/canaan-creative/ams/config/ams.yaml',
] as $file)
	if (file_exists($file)) {
		$cfg = yaml_parse_file($file);
		$yaml = $file;
	}
$dbname = $cfg['database']['database'];
$user = $cfg['database']['user'];
$password = $cfg['database']['password'];
