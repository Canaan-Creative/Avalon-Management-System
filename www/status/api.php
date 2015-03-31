<?php
include 'config.php';

$dbhandle = mysql_connect("localhost", $user, $passwd)
	or die('Could not connect: ' . mysql_error());
$selected = mysql_select_db($dbname, $dbhandle)
	or die("Could not select database.");

$result = mysql_query("SELECT time FROM head WHERE type = 'main'");

$time = mysql_fetch_array($result)['time'];

$tmp = explode('_', $time);
$timealt = $tmp[0] . '-' . $tmp[1] . '-' . $tmp[2] . ' ' . $tmp [3] . ':' . $tmp[4];
#	$time = $tmp[0] . '-' . $tmp[1] . '-' . $tmp[2] . ' ' . $tmp [3] . ':' . $tmp[4];
#	
#	$datetime = new DateTime($time);
#	$time = $datetime->format('Y_m_d_H_i');
#	$datetime->sub(new DateInterval('PT120S'));
#	$lasttime = $datetime->format('Y_m_d_H_i');
#	
#	$table0 = 'Module_' . $lasttime;

$table = 'Module_' . $time;

$result = mysql_query("SELECT dna, ghs FROM " . $table);
$ghs = [];
while ($row = mysql_fetch_array($result))
	$ghs[$row['dna']] = $row['ghs'];
echo json_encode(array('time' => $timealt, 'ghs' => $ghs));
