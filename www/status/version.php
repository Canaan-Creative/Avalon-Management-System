<?php
if (! isset ($_COOKIE['userId'])){
        header('Location:/status/login.php');
        die;
}

$ip = empty($_POST['ip']) ? 0 : $_POST['ip'];
if (preg_match('/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/', $ip)) {
	$output = array();
	exec("python version.py " . $ip, $output);
	$version = $output[0];

	echo json_encode(array('version' => $version));
}
