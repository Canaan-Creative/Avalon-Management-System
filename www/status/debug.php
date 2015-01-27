<?php
if (! isset ($_COOKIE['userId'])){
        header('Location:/status/login.php');
        die;
}

$ip = empty($_GET['ip']) ? 0 : $_GET['ip'];

if (!$ip)
	exit;

$output = array();
exec("python debug.py " . $ip, $output);
foreach ($output as $o)
	echo $o . "<br />";
