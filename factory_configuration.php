<?php
if (! isset ($_COOKIE['userId'])){
	header('Location:/status/login.php');
	die;
}

$ip = empty($_POST['ip']) ? 0 : $_POST['ip'];
$port = empty($_POST['port']) ? 0 : $_POST['port'];
$value = empty($_POST['value']) ? 0 : $_POST['value'];

if((!$ip) || (!$port)){
	echo json_encode(array('status'=>'1','msg'=>'ip or port is null'));exit;
}

function write_config($ip, $port, $value) {
	$config_info = $ip . ',' . $port . ',' . $value;

	system("python factory_configuration.py " . $config_info . " 2>&1 >> /tmp/factory_configuration.log");
	echo json_encode(array('status'=>'0','msg'=>'Done.'));
}

write_config($ip, $port, $value);
exit;
