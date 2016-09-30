<?php
$cfg = parse_ini_file("/home/archang/ams/etc/ams.conf", true);
$dbname = $cfg['Database']['dbname'];
$user = $cfg['Database']['user'];
$passwd = $cfg['Database']['passwd'];
