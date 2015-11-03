<?php
if (! isset ($_COOKIE['userId'])) {
	header('Location:/status/login.php');
	die;
}

function pg_decode($pg) {
	if ($pg == 0)
		return "All";
	$str = "";
	for ($i = 1; $i < 3; $i++) {
		$flag = $pg & 1;
		$pg = ($pg >> 1);
		if (!$flag) {
			if ($str != "")
				$str = $str . ", ";
			$str = $str . "PG" . $i;
		}
	}
	return $str . ".";
}

include 'config.php';

$dbhandle = mysql_connect("localhost", $user, $passwd)
	or die('Could not connect: ' . mysql_error());
$selected = mysql_select_db($dbname, $dbhandle)
	or die("Could not select database.");

$result = mysql_query("SELECT * FROM Error_" . $time . " ORDER BY INET_ATON(ip), port, deviceid, moduleid");
$errors = array();
$errorc = array(
	"missing" => array(),
	"hightemp" => array(),
	"highdh" => array(),
	"wrongpg" => array(),
	"fanstopped" => array(),
	"miningstopped" => array(),
	"lowhashrate" => array(),
	"lowtemp" => array(),
	"wrongvolt" => array(),
	"apimess" => array()
);
$errorcolor = array(
	"purple",
	"red",
	"blue",
	"green",
	"orange",
	"green",
	"orange",
	"green",
	"orange"
);
$errormsg = array(
	"Temperature over 200. ",
	"Temperature Higher Than 50. ",
	"Temperature Lower Than 25. ",
	"Device Hardware Error Higher Than 3%. ",
	"Wrong Voltage. ",
	"Hashrate Over 20% Lower Than Average. ",
	"Mining Stopped. ",
	"Fan Stopped. ",
	"Hashrate lower than 600GHs. "
);
while ($row = mysql_fetch_array($result)) {
	if ($row['connectionfailed']) {
		$e = array(
			"href" => "cgminer.php?ip=". $row['ip'],
			"id" => $row['ip'],
			"error" => array(array("color" => "red", "msg" => "Connection Failed. "))
		);
		$errors[] = $e;
		$errorc['missing'][] = $e;
	} elseif ($row['missingdevice']) {
		$e = array(
			"href" => "cgminer.php?ip=" . $row['ip'] . "&port=" . $row['port'],
			"id" => $row['ip'] . ":" . $row['port'],
			"error" => array(array("color" => "red", "msg" => $row['missingdevice'] . " Device(s) Missing. "))
		);
		$errors[] = $e;
		$errorc['missing'][] = $e;
	} elseif($row['missingmodule']) {
		$e = array(
			"href" => "cgminer.php?ip=" . $row['ip'] . "&port=" . $row['port'] . "&hl=" . $row['deviceid'],
			"id" => $row['ip'] . ":" . $row['port'] . " dev#" . $row['deviceid'],
			"error" => array(array("color" => "red", "msg" => $row['missingmodule'] . " Module(s) Missing. "))
		);
		$errors[] = $e;
		$errorc['missing'][] = $e;
	} elseif($row['apidisaster']) {
		$e = array(
			"href" => "cgminer.php?ip=" . $row['ip'] . "&port=" . $row['port'] . "&hl=" . $row['deviceid'],
			"id" => $row['ip'] . ":" . $row['port'] . " dev#" . $row['deviceid'],
			"error" => array(array("color" => "red", "msg" => "CGMiner API EStats Disaster! "))
		);
		$errors[] = $e;
		$errorc['apimess'][] = $e;
	} else {
		$e = array(
			"href" => "cgminer.php?ip=" . $row['ip'] . "&port=" . $row['port'] . "&hl=" . $row['deviceid'] . "-" . $row['moduleid'],
			"id" => $row['ip'] . ":" . $row['port'] . " dev#" . $row['deviceid'] . " mod#" . $row['moduleid'],
			"error" => array()
		);
		$c_index = array();
		if ($row['wrongpg'] != 1023) {
			$e["error"][] = array("color" => "red", "msg" => "Wrong PG: " . pg_decode($row['wrongpg']));
			$c_index[] = "wrongpg";
		}
		for ($i = 0; $i < 9; $i ++) {
			if ($i == 2)
				$j = 5;
			elseif ($i > 2 and $i < 6)
				$j = $i - 1;
			else
				$j = $i;
			if ($row[$j + 8]) {
				$e["error"][] = array("color" => $errorcolor[$j], "msg" => $errormsg[$j]);
				switch ($errormsg[$j]) {
				case "Temperature over 200. ":
				case "Temperature Higher Than 50. ":
					$c_index[] = "hightemp";
					break;
				case "Temperature Lower Than 25. ":
					$c_index[] = "lowtemp";
					break;
				case "Device Hardware Error Higher Than 3%. ":
					$c_index[] = "highdh";
					break;
				case "Wrong Voltage. ":
					$c_index[] = "wrongvolt";
					break;
				case "Mining Stopped. ":
					$c_index[] = "miningstopped";
					break;
				case "Fan Stopped. ":
					$c_index[] = "fanstopped";
					break;
				case "Hashrate Over 20% Lower Than Average. ":
				case "Hashrate lower than 600GHs. ":
					$c_index[] = "lowhashrate";
					break;
				default:
					break;
				}
			}
		}
		$errors[] = $e;
		foreach (array_unique($c_index) as $c)
			$errorc[$c][] = $e;
	}
}
