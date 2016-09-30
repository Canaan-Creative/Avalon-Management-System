<?php
if (! isset ($_COOKIE['userId'])) {
	header('Location:/status/login.php');
	die;
}
if ($_POST) {
	include 'config.php';
	$farmcfg = $cfg['Json']['farm'];
	$fp = fopen($farmcfg, 'w');
	fwrite($fp, $_POST["cfg"]);
	fclose($fp);
}
