<?php
include 'config.php';
$dbhandle = mysql_connect("localhost", $user, $passwd)
	or die('Could not connect: ' . mysql_error());
$selected = mysql_select_db($dbname, $dbhandle)
	or die("Could not select database.");

function switch_led($table, $clause) {
	$list = array();
	$result = mysql_query("SELECT ip, port, device, module from " .
		$table . " " . $clause);
	while ($row = mysql_fetch_array($result))
		$list[] = $row['ip'] . ',' . $row['port'] . ',' .
				$row['device'] . ',' . $row['module']; 
	system("python led.py " . join(' ' , $list));
}

$result = mysql_query("SELECT time, command FROM head WHERE type = 'led'");
$row = mysql_fetch_array($result)[0];

switch ($row['command']) {
case 'temp':
	$clause = 'WHERE temp>45';
	break;
case 'dh':
	$clause = 'WHERE dh>10';
	break;
default:
	$clause = Null;
	exit;
}

if (!is_null($clause)) {
	$table = 'Module_' . $row['time'];
	switch_led($table, $clause);
}


switch ($_POST['command']) {
case 'temp':
	$result = mysql_query("SELECT time FROM head WHERE type = 'main'");
	$row = mysql_fetch_array($result)[0];
	$table = 'Module_' . $row['time'];
	$clause = 'WHERE temp>45';
	switch_led($table, $clause);
	mysql_query("UPDATE head SET time = '" . $row['time'] .
		"' WHERE type = 'led'");
	break;

case 'dh':
	$result = mysql_query("SELECT time FROM head WHERE type = 'main'");
	$row = mysql_fetch_array($result)[0];
	$table = 'Module_' . $row['time'];
	$clause = 'WHERE dh>10';
	switch_led($table, $clause);
	mysql_query("UPDATE head SET time = '" . $row['time'] .
		"' WHERE type = 'led'");
	break;

case 'clear':
	mysql_query("UPDATE head SET command = NULL WHERE type = 'led'");
	break;

default:
	exit;
}
exit;
