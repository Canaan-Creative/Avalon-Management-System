<?php
if (! isset ($_COOKIE['userId'])) {
	header('Location:/status/login.php');
	die;
}
#
$pattern = '/Ver\[([-+0-9A-Fa-f]+)\]\sDNA\[([0-9A-Fa-f]+)\]\sElapsed\[([-0-9]+)\]\s.*LW\[([0-9]+)\]\s.*HW\[([0-9]+)\]\sDH\[([.0-9]+)%\]\sGHS5m\[([-.0-9]+)\]\sDH5m\[([-.0-9]+)%\]\s.*Temp\[([-0-9]+)\]\sFan\[([0-9]+)\]\sVol\[([.0-9]+)\]\s.*Freq\[([.0-9]+)\]\sPG\[([0-9]+)\]\sLed\[(0|1)./';
$ip   = $_GET['ip'];
$ports = explode(',', $_GET['port']);
if (array_key_exists('hl', $_GET) && $_GET['hl'] !== "" && $_GET['hl'] !== null)
	$hls = explode('-', $_GET['hl']);
else
	$hls = null;
$data = json_decode(exec("python chkstat.py " . $ip . " " . join(' ', $ports)),true);
$summary_l = $data[0];
$devs_l = $data[1];
$stats_l = $data[2];
$pools_l = $data[3];
?>

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=GBK">

<script src="http://libs.baidu.com/jquery/2.0.0/jquery.js"></script>


<script>

function restart_cgminer(ip,port){
	var _ip = ip;
	var _port = port;

	$.ajax({
		type:"POST",
		url:"restart_cgminer.php",
		data:{ip:_ip,port:_port},
		dataType:"json",
		success:function(data){
			alert(data.msg);
		}
	});
}

function switch_led(ip,port,dev,mod){
	var _ip = ip;
	var _port = port;
	var _dev = dev;
	var _mod = mod;

	$.ajax({
		type:"POST",
		url:"switch_led.php",
		data:{ip:_ip,port:_port,dev:_dev,mod:_mod},
		dataType:"json",
		success:function(data){
			alert(data.msg);
		}
	});
}

function adjust_volt(ip, port, dev, mod, volt) {
	var _ip = ip;
	var _port = port;
	var _dev = dev;
	var _mod = mod;
	var _volt = volt;

	$.ajax({
		type:"POST",
		url:"adjust_volt.php",
		data:{ip:_ip,port:_port,dev:_dev,mod:_mod,volt:_volt},
		dataType:"json",
		success:function(data){
			alert(data.msg);
		}
	});
}
</script>
<style>
.div-table{border:1px solid #c3c3c3;}
fieldset{border:1px dashed #c3c3c3;margin-bottom:15px;}
legend{ font-size:16px; font-weight:bold;}
table{ width:100%;}
th{ background:#efefef ; border:1px solid #c3c3c3;}
td{ border:1px solid #c3c3c3;}
.highlight{border:1px solid #c3c3c3; background:red}
.lowlight{border:1px solid #c3c3c3; background:yellow}
.nolight0{border:1px solid #c3c3c3}
.nolight1{border:1px solid #c3c3c3; background: #c3c3c3}
</style>

</head>
<body>
<h2>
Cgminer Status
<span>
<button onClick="restart_cgminer('<?php echo $ip . "','" . join(',',$ports);?>');">Restart All</button>
<button onClick="window.open('./debug.php?ip=<?php echo $ip; ?>');">Debug</button>
</span>
</h2>
<hr>

<?php
function second2human($seconds) {
	$d = (int)($seconds / (3600 * 24));
	$h = (int)(($seconds % (3600 * 24)) / 3600);
	$m = (int)(($seconds % 3600) / 60);
	$s = (int)($seconds % 60);
	if ($d)
		return $d . "d " . $h . "h " . $m . "m " . $s . "s";
	elseif ($h)
		return $h . "h " . $m . "m " . $s . "s";
	elseif ($m)
		return $m . "m " . $s . "s";
	else
		return $s . "s";
}

for ($i = 0; $i < count($ports); $i++) {
	$port = $ports[$i];
	$summary = $summary_l[$i]['SUMMARY'][0];
	$devs = $devs_l[$i]['DEVS'];
	$stats = $stats_l[$i]['STATS'];
	$pools = $pools_l[$i]['POOLS'];

	echo "
<hr>
<fieldset>
<legend>" . $ip . ":" . $port . "
<span>
<button onClick=\"restart_cgminer('" . $ip . "'," . $port . ");\">Restart Cgminer</button>
</span>
</legend>

<fieldset>
<legend>Summary</legend>
<div class=\"div-table\">
<table>
<tr>
  <th>Elapsed</th>
  <th>GHSav</th>
  <th>Accepted</th>
  <th>Rejected</th>
  <th>Discarded</th>
  <th>NetworkBlocks</th>
  <th>BestShare</th>
</tr>
<tr>
  <td>" . second2human($summary['Elapsed']) ."</td>
  <td>" . number_format($summary['MHS av']/1000, 2) . "</td>
  <td>" . $summary['Accepted'] . "</td>
  <td>" . $summary['Rejected'] . "</td>
  <td>" . $summary['Discarded'] . "</td>
  <td>" . $summary['Network Blocks'] . "</td>
  <td>" . $summary['Best Share'] . "</td>
</tr>
</table>
</div>
</fieldset>

<fieldset>
<legend>Pool</legend>
<div class=\"div-table\">
<table>
<tr>
  <th>Pool</th>
  <th>URL</th>
  <th>StratumActive</th>
  <th>User</th>
  <th>Status</th>
  <th>GetWorks</th>
  <th>Accepted</th>
  <th>Rejected</th>
  <th>Discarded</th>
  <th>Stale</th>
  <th>LST</th>
  <th>LSD</th>
</tr>";

	foreach ($pools as $pool_name=>$pool) {
		if ($pool_name !== 'STATUS') {
			echo "<tr>";
			echo "<td>" . $pool['POOL'] . "</td>";
			echo "<td>" . $pool['URL'] . "</td>";
			echo "<td>" . ($pool['Stratum Active'] ? "true" : "false") . "</td>";
			echo "<td>" . $pool['User'] . "</td>";
			echo "<td>" . $pool['Status'] . "</td>";
			echo "<td>" . $pool['Works'] . "</td>";
			echo "<td>" . $pool['Accepted'] . "</td>";
			echo "<td>" . $pool['Rejected'] . "</td>";
			echo "<td>" . $pool['Discarded'] . "</td>";
			echo "<td>" . $pool['Stale'] . "</td>";
			if ($pool['Last Share Time'] !== "0") {
				$dt = new DateTime();
				$dt->setTimestamp($pool['Last Share Time']);
				echo "<td>" . date_format($dt,"Y-m-d H:i:s") . "</td>";
			}
			else
				echo "<td>Never</td>";
			echo "<td>" . round($pool['Last Share Difficulty']) . "</td>";
			echo "</tr>";
		}
	}
	echo "
</table>
</div>
</fieldset>

<fieldset>
<legend>Devices</legend>
<div class=\"div-table\">
<table>
<tr>
  <th>Device</th>
  <th>MM Count</th>
  <th>Enabled</th>
  <th>Status</th>
  <th>T(C)</th>
  <th>GHSav</th>
  <th>GHS5s</th>
  <th>GHS1m</th>
  <th>GHS5m</th>
  <th>GHS15m</th>
  <th>LastValidWork</th>
</tr>";

	foreach ($devs as $dev) {
		if (($hls !== null) && ($dev['ID'] == $hls[0]))
			$td = "<td class=\"highlight\">";
		else
			$td = "<td>";
		echo "<tr>";
		echo $td . "ASC" . $dev['ASC']. "-" . $dev['Name'] . "-" . $dev['ID'] ."</td>";
		foreach ($stats as $stat)
			if (substr($stat['ID'], 3) == $dev['ID']) {
				echo $td . $stat['MM Count'] . "</td>";
				break;
			}
		echo $td . $dev['Enabled'] . "</td>";
		echo $td . $dev['Status'] . "</td>";
		echo $td . intval($dev['Temperature']) . "</td>";
		echo $td . number_format($dev['MHS av']/1000, 2) . "</td>";
		echo $td . number_format($dev['MHS 5s']/1000, 2) . "</td>";
		echo $td . number_format($dev['MHS 1m']/1000, 2) . "</td>";
		echo $td . number_format($dev['MHS 5m']/1000, 2) . "</td>";
		echo $td . number_format($dev['MHS 15m']/1000, 2) . "</td>";
		if ($dev['Last Valid Work'] !== "0") {
			$dt = new DateTime();
			$dt->setTimestamp($dev['Last Valid Work']);
			echo $td . date_format($dt,"Y-m-d H:i:s") . "</td>";
		}
		else
			echo $td . "Never</td>";
		echo "</tr>";
	}
	echo "
</table>
</div>
</fieldset>

<fieldset>
<legend>Status</legend>
<div class=\"div-table\">
<table>
<tr>
  <th>Indicator</th>
  <th>Elapsed</th>
  <th>Device</th>
  <th>MM</th>
  <th>DNA</th>
  <th>LocalWorks</th>
  <th>DH%</th>
  <th>GHS5m</th>
  <th>DH%5m</th>
  <th>T(C)</th>
  <th>Fan(RPM)</th>
  <th>ASIC V(V)</th>
  <th>ASIC F(GHS)</th>
  <th>Power Good</th>
</tr>";

	$i = 0;
	foreach ($stats as $stat) {
		$mods = array();
		foreach ($stat as $key=>$value)
			if (strpos($key,'MM ID') !== False)
				$mods[] = substr($key,5);
		if (count($mods) == 0)
			continue;
		sort($mods);
		foreach ($mods as $mod) {
			if (substr($stat['ID'],3) == $hls[0]) {
				if (count($hls) == 1)
					$td = "<td class=\"lowlight\">";
				else if ($mod == $hls[1])
					$td = "<td class=\"highlight\">";
			} else
				$td = "<td class=\"nolight" . ($i & 1) . "\">";
			$key = "MM ID" . $mod;
			$matches = array();
			if (preg_match($pattern, $stat[$key], $matches)) {
				echo "<tr>";
				echo $td . "<button onClick=\"switch_led('" . $ip . "'," . $port . "," . substr($stat['ID'], 3) . "," . $mod . ");\">";
				if ($matches[14])
					echo "Turn OFF</button></td>";
				else
					echo "Turn ON</button></td>";
				echo $td . second2human($matches[3]) . "</td>";
				echo $td . substr($stat['ID'],0,3) . "-" . substr($stat['ID'], 3) . "-" . $mod . "</td>";
				echo $td . $matches[1] . "</td>";
				echo $td . substr($matches[2], 12) . "</td>";
				echo $td . number_format($matches[4], 0, ".", ",") . "</td>";
				echo $td . $matches[6] . "</td>";
				echo $td . $matches[7] . "</td>";
				echo $td . $matches[8] . "</td>";
				echo $td . $matches[9] . "</td>";
				echo $td . $matches[10] . "</td>";
				echo $td . $matches[11] . "</td>";
				echo $td . $matches[12] . "</td>";
				echo $td . $matches[13] . "</td>";
				echo "</tr>";
			} else {
				echo "<tr>";
				echo "<td></td>";
				echo "<td></td>";
				echo $td . substr($stat['ID'],0,3) . "-" . substr($stat['ID'], 3) . "-" . $mod . "</td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "<td></td>";
				echo "</tr>";

			}
		}
		$i ++;
	}
	echo "
</table>
</div>
</fieldset></fieldset>";
}
?>
</body></html>
