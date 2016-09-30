<?php
include 'config.php';
$dbhandle = mysql_connect("localhost", $user, $passwd)
	or die('Could not connect: ' . mysql_error());
$selected = mysql_select_db($dbname, $dbhandle)
	or die("Could not select database.");

function switch_led($table, $clause) {
	$list = array();
	$result = mysql_query("SELECT ip, port, deviceid, moduleid from " .
		$table . " " . $clause);

	while ($row = mysql_fetch_array($result))
		$list[] = $row['ip'] . ',' . $row['port'] . ',' .
			$row['deviceid'] . ',' . $row['moduleid'];
	system("python led.py " . join(' ' , $list) . " 2>&1 >> /tmp/led.log");
}

$result = mysql_query("SELECT time, command FROM head WHERE type = 'led'");
$row = mysql_fetch_array($result);

if ($row == False)
	$clause = Null;
else
	switch ($row['command']) {
	case 'temp':
		$clause = 'WHERE temp>45';
		break;
	case 'dh':
		$clause = 'WHERE dh>10';
		break;
	default:
		$clause = Null;
		break;
	}

if (!is_null($clause)) {
	$table = 'Module_' . $row['time'];
	switch_led($table, $clause);
}


switch ($_POST['command']) {
case 'temp':
	$result = mysql_query("SELECT time FROM head WHERE type = 'main'");
	$row = mysql_fetch_array($result);
	$table = 'Module_' . $row['time'];
	$clause = "WHERE temp>45";
	switch_led($table, $clause);
	mysql_query("INSERT INTO head (time, command, type) VALUES ('" .
		$row['time'] . "', 'temp', 'led') ON DUPLICATE KEY UPDATE " .
		"time = '" . $row['time'] . "', command = 'temp'");
	echo json_encode(array('status'=>'1','msg'=>'Done.'));
	break;

case 'dh':
	$result = mysql_query("SELECT time FROM head WHERE type = 'main'");
	$row = mysql_fetch_array($result);
	$table = 'Module_' . $row['time'];
	$clause = 'WHERE dh>10';
	switch_led($table, $clause);
	mysql_query("INSERT INTO head (time, command, type) VALUES ('" .
		$row['time'] . "', 'dh', 'led') ON DUPLICATE KEY UPDATE " .
		"time = '" . $row['time'] . "', command = 'dh'");
	echo json_encode(array('status'=>'1','msg'=>'Done.'));
	break;

case 'clear':
	mysql_query("INSERT INTO head (command, type) VALUES (NULL, 'led')" .
		"ON DUPLICATE KEY UPDATE command = NULL");
	echo json_encode(array('status'=>'1','msg'=>'Done.'));
	break;

default:
	exit;
}
exit;
