<?php
include '../config.php';

$dbhandle = mysql_connect("localhost", $user, $passwd)
	or die('Could not connect: ' . mysql_error());
$selected = mysql_select_db($dbname, $dbhandle)
	or die("Could not select database.");

$result = mysql_query("DESCRIBE Hashrate");
$labels = array();
while ($row = mysql_fetch_array($result)) {
	if ($row['Field'] == 'time')
		continue;
	$labels[] = $row['Field'];
}

$colorlist = array("blue", "cyan", "green", "red", "yellow", "purple");
$timeshift = 8 * 3600;

$now = time();

$series = array_fill(0, sizeof($labels), array());
$i = 0;
foreach ($series as &$serie) {
	$serie['pointStart'] = $now * 1000 - 24 * 3600 * 1000;
	$serie['pointInterval'] = 24 * 3600 * 1000;
	$serie['data'] = array();
	$serie['color'] = $colorlist[$i];
	$serie['name'] = $labels[$i];
	$i += 1;
}


$result = mysql_query("SELECT * FROM Hashrate");
$flag = FALSE;
while ($row = mysql_fetch_array($result)) {
	$unix = strtotime($row['time']);
	$localtime = ($unix + $timeshift) * 1000;
	if($flag) {
		$i = 0;
		foreach ($labels as $label) {
			$series[$i]['data'][] = array($localtime, $row[$label] * 1000000);
			$i += 1;
		}
	} else {
		if($now - 2 * 24 * 3600 < $unix)
			$flag = TRUE;
	}
}

#
# Hashrate
#
$hashrate = round(end($series[0]['data'])[1] / 1000000000000, 1);


#
# Temp
#
$result = mysql_query("SELECT time FROM head WHERE type = 'main'");
$time = mysql_fetch_array($result)['time'];
$tmp = explode('_', $time);
$showTime = $tmp[0] . '-' . $tmp[1] . '-' . $tmp[2] . ' ' . $tmp [3] . ':' . $tmp[4];
$table = 'Module_' . $time;

$result = mysql_query("SELECT max(temp) max, avg(temp) avg FROM " . $table);
$tmp = mysql_fetch_array($result);
$temp = number_format($tmp["avg"], 1) . "/" . $tmp["max"] . "&deg;C";


#
# Alive
#
$result = mysql_query("SELECT alivemod, totalmod FROM Aliverate ORDER BY time DESC LIMIT 1");
$tmp = mysql_fetch_array($result);
$mod = $tmp["alivemod"] . "/" . $tmp["totalmod"];

echo json_encode(array("hashrate" => $hashrate, "temperature" => $temp, "aliverate" => $mod, "graph" => $series));
