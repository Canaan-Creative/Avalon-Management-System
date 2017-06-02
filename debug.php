<?php
if (! isset ($_COOKIE['userId'])){
        header('Location:/status/login.php');
        die;
}

$ip = empty($_GET['ip']) ? 0 : $_GET['ip'];
$port = empty($_GET['port']) ? 4028 : $_GET['port'];

if (!$ip)
	exit;
if (preg_match('/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/', $ip) && is_numeric($port)) {
    $output = array();
    exec("python debug.py " . $ip . " " . $port . "| jq '.' | sed 's/\]/\]\\n/g'", $output);
    foreach ($output as $o)
		echo $o . "<br />";
}
