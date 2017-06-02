<?php
if (! isset ($_COOKIE['userId'])){
	header('Location:/status/login.php');
	die;
}
//error_reporting(E_ALL);

$ip = empty($_POST['ip']) ? 0 : $_POST['ip'];
$port = empty($_POST['port']) ? 0 : $_POST['port'];
$dev = empty($_POST['dev']) ? 0 : $_POST['dev'];
$mod = empty($_POST['mod']) ? 0 : $_POST['mod'];

if((!$ip) || (!$port)){
	echo json_encode(array('status'=>'0','msg'=>'ip or port is null'));exit;
}

system("python ./cgminer_api.py 'ascset|" . $dev . ",reboot," . $mod . "' " . $ip . " ". $port);

echo json_encode(array('status'=>'1','msg'=>'成功，页面将刷新'));
exit;
