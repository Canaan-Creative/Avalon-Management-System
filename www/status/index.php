<?php
if (! isset ($_COOKIE['userId'])) {
	header('Location:/status/login.php');
	die;
}

function dec2hex($x) {
	if (abs($x - round($x)) < 0.00001 && round($x) != 0) {
		$x = round($x) - 1;
	} else {
		$x = floor($x);
	}
	return str_pad(dechex($x), 2, "0", STR_PAD_LEFT);
}

function pg_decode($pg) {
	if ($pg == 0)
		return "All";
	$str = "";
	for ($i = 1; $i < 3; $i++) {
		for ($j = 1; $j < 6; $j++) {
			$flag = $pg & 1;
			$pg = ($pg >> 1);
			if (!$flag) {
				if ($str != "")
					$str = $str . ", ";
				$str = $str . "PG" . $i . "-" . $j;
			}
		}
	}
	return $str . ".";
}

function rainbow($x, $xmin, $xmax) {
	if ($x == 0) {
		return '#ffffff';
	}
	$x = (float)($x - $xmin) / (float)($xmax - $xmin);
	if ($x < 0) {
		$r = 0;
		$g = 0;
		$b = 128;
	} elseif ($x < 0.125) {
		$r = 0;
		$g = 0;
		$b = $x / 0.125 * 128 + 128;
	} elseif ($x < 0.375) {
		$r = 0;
		$g = ($x - 0.125) / 0.25 * 256;
		$b = 256;
	} elseif ($x < 0.625) {
		$r = ($x - 0.375) / 0.25 * 256;
		$g = 256;
		$b = 256 - ($x - 0.375) / 0.25 * 256;
	} elseif($x < 0.875) {
		$r = 256;
		$g = 256 - ($x - 0.625) / 0.25 * 256;
		$b = 0;
	} else {
		$r = 256 - ($x - 0.875) / 0.25 * 256;
		$g = 0;
		$b = 0;
	}
	return '#' . dec2hex($r) . dec2hex($g) . dec2hex($b);
}

function invert_color($color) {
	$hex = '0x' . substr($color, 1);
	$invert = 0xffffff - $hex;
	return '#' . str_pad(dechex($invert), 6, '0', STR_PAD_LEFT);
}

$autorefresh = False;
if (array_key_exists('auto', $_GET) && $_GET['auto'] !== "" && $_GET['auto'] !== null) {
	$auto = $_GET['auto'];
	if (strcasecmp($auto, "true") == 0 || strcasecmp($auto, "yes") == 0 || strcasecmp($auto, "y") == 0)
		$autorefresh = True;
}
## T-map
$cfg = parse_ini_file("/path/to/ams/etc/ams.conf", true);
$dbname = $cfg['Database']['dbname'];
$user = $cfg['Database']['user'];
$passwd = $cfg['Database']['passwd'];
$dbhandle = mysql_connect("localhost", $user, $passwd)
	or die('Could not connect: ' . mysql_error());
$selected = mysql_select_db($dbname, $dbhandle)
	or die("Could not select database.");
$farmcfg = $cfg['Json']['farm'];
$farm = json_decode(file_get_contents($farmcfg), true);

$zones = $farm["zone"];

$farm_map = array();

$z = 0;

$result = mysql_query("SHOW TABLES LIKE 'Miner\_%'");
while ($row = mysql_fetch_array($result))
	$table = $row[0];
$time = explode('Miner_', $table)[1];
$tmp = explode('_', $table);
$showTime = $tmp[1] . '-' . $tmp[2] . '-' . $tmp[3] . ' ' . $tmp [4] . ':' . $tmp[5];

foreach ($zones as $zone) {
	$zone_map = array();
	$miner_per_table = $zone["layers"] * $zone["plot_split"];
	for ($i = 0; $i < ceil( count($zone["miner"]) / $miner_per_table); $i++) {
		$split_map = array();
		for ($j = 0; $j < $zone["layers"]; $j++)
			$split_map[] = array_fill(0, $zone["plot_split"], Null);
		$zone_map[] = $split_map;
	}
	for ($i=0; $i < count($zone["miner"]); $i++) {
		$miner = $zone["miner"][$i];
		$n = floor($i / $miner_per_table);
		$x = floor(($i % $miner_per_table) / $zone["layers"]);
		$y = ($i % $miner_per_table) % $zone["layers"];

		if ($miner != "skip") {
			$ip = $miner["ip"];
			$ports = array();
			$result = mysql_query("SELECT port FROM " . $table . " WHERE ip='" . $ip . "' ORDER BY port");
			while ($row = mysql_fetch_array($result))
				$ports[] = $row["port"];

			$result = mysql_query("SELECT SUM(alive) AS sum from " . $table . " WHERE ip='" . $ip . "'");
			$row = mysql_fetch_array($result);
			if ($row["sum"] > 0) {
				$alive = true;
				$result = mysql_query("SELECT SUM(summodule) AS summod, SUM(summodule0) AS summod0,
					SUM(rate15min) AS sumrate, MAX(maxtemperature) AS maxtemp FROM " . $table . " WHERE ip='" . $ip . "'");
				$row = mysql_fetch_array($result);
				$modnum = $row['summod'] . "/" . $row['summod0'];
				$maxtemp = $row['maxtemp'];
				$rate = (int)$row['sumrate'];
				if (strlen($rate) < 3)
					$rate = $rate . " MH/s";
				elseif(strlen($rate) < 6)
					$rate = sprintf("%." . (6 - strlen($rate)) . "f GH/s", (float)$rate / 1000.0);
				elseif(strlen($rate) < 9)
					$rate = sprintf("%." . (9 - strlen($rate)) . "f TH/s", (float)$rate / 1000000.0);
				else
					$rate = sprintf("%." . (12 - strlen($rate)) . "f PH/s", (float)$rate / 1000000000.0);
			} else {
				$alive = false;
				$modnum = "";
				$maxtemp ="";
				$rate = "";
			}
			if (!$ports)
				$ports = [4028];
			$backcolor = rainbow($maxtemp, 30, 70);
			$frontcolor = invert_color($backcolor);
			$zone_map[$n][$y][$x] = array(
				"skip" => false,
				"alive" => $alive,
				"ip" => $ip,
				"ports" => $ports,
				"modnum" => $modnum,
				"maxtemp" => $maxtemp,
				"rate" => $rate,
				"backcolor" => $backcolor,
				"frontcolor" => $frontcolor
			);
		} else
			$zone_map[$n][$y][$x] = array("skip" => true);
	}
	$farm_map[] = $zone_map;
	$z++;
}
# Hashrate Graph
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
		if($now - 30 * 24 * 3600 < $unix)
			$flag = TRUE;
	}
}
# Error List:
$result = mysql_query("SELECT * FROM Error_" . $time . " ORDER BY ip, port");
$errors = array();
$errorcolor = array(
	"purple",
	"red",
	"blue",
	"green",
	"orange",
	"green",
	"orange",
	"green"
);
$errormsg = array(
	"Temperature over 200. ",
	"Temperature Higher Than 62. ",
	"Temperature Lower Than 25. ",
	"Device Hardware Error Higher Than 3%. ",
	"Wrong Voltage. ",
	"Hashrate Over 20% Lower Than Average. ",
	"Mining Stopped. ",
	"Fan Stopped. "
);
while ($row = mysql_fetch_array($result)) {
	if ($row['connectionfailed'])
		$errors[] = array(
			"href" => "cgminer.php?ip=". $row['ip'],
			"id" => $row['ip'],
			"error" => array(array("color" => "red", "msg" => "Connection Failed. "))
		);
	elseif ($row['missingdevice'])
		$errors[] = array(
			"href" => "cgminer.php?ip=" . $row['ip'] . "&port=" . $row['port'],
			"id" => $row['ip'] . ":" . $row['port'],
			"error" => array(array("color" => "red", "msg" => $row['missingdevice'] . " Device(s) Missing. "))
		);
	elseif($row['missingmodule'])
		$errors[] = array(
			"href" => "cgminer.php?ip=" . $row['ip'] . "&port=" . $row['port'] . "&hl=" . $row['deviceid'],
			"id" => $row['ip'] . ":" . $row['port'] . " dev#" . $row['deviceid'],
			"error" => array(array("color" => "red", "msg" => $row['missingmodule'] . " Module(s) Missing. "))
		);
	elseif($row['apidisaster'])
		$errors[] = array(
			"href" => "cgminer.php?ip=" . $row['ip'] . "&port=" . $row['port'] . "&hl=" . $row['deviceid'],
			"id" => $row['ip'] . ":" . $row['port'] . " dev#" . $row['deviceid'],
			"error" => array(array("color" => "red", "msg" => "CGMiner API EStats Disaster! "))
		);
	else {
		$error = array(
			"href" => "cgminer.php?ip=" . $row['ip'] . "&port=" . $row['port'] . "&hl=" . $row['deviceid'] . "-" . $row['moduleid'],
			"id" => $row['ip'] . ":" . $row['port'] . " dev#" . $row['deviceid'] . " mod#" . $row['moduleid'],
			"error" => array()
		);
		if ($row['wrongpg'] != 1023)
			$error["error"][] = array("color" => "red", "msg" => "Wrong PG: " . pg_decode($row['wrongpg']));
		for ($i = 0; $i < 8; $i ++) {
			if ($i == 2)
				$j = 5;
			elseif ($i > 2 and $i < 6)
				$j = $i - 1;
			else
				$j = $i;
			if ($row[$j + 8])
				$error["error"][] = array("color" => $errorcolor[$j], "msg" => $errormsg[$j]);
		}
		$errors[] = $error;
	}
}

/**
 * Sort errorsList
 * @author Wanggh
 * 2014/09/11
 */

function makeIpToNum($ip) {
	$ip_arr = explode('.', $ip); //分隔ip段
	$ipstr = "";
	foreach ($ip_arr as $value) {
		$iphex = dechex($value); //将每段ip转换成16进制
		if(strlen($iphex) < 2) //255的16进制表示是ff，所以每段ip的16进制长度不会超过2
			$iphex = '0' . $iphex; //如果转换后的16进制数长度小于2，在其前面加一个0
			//没有长度为2，且第一位是0的16进制表示，这是为了在将数字转换成ip时，好处理
		$ipstr .= $iphex; //将四段IP的16进制数连接起来，得到一个16进制字符串，长度为8
	}
	return hexdec($ipstr); //将16进制字符串转换成10进制，得到ip的数字表示
}

$getSort = isset($_GET ['sort']) ? $_GET ['sort'] : '';
$sortName = 'ip';
$sortType = 'desc';
if ($getSort) {
	$tmpArr = explode('_', $getSort);
	$sortName = strtolower($tmpArr [0]);
	$sortType = strtolower($tmpArr [1]);
}
if (is_array($errors)) {
	$sortArr = $newArr = array();
	if ($sortName == 'ip')
		foreach ($errors as $key=>$value) {
			$t = explode(':', $value ['id']);
			$ip = array_shift($t);
			$sortArr [$key] = makeIpToNum($ip);
		}
	elseif ($sortName == 'info')
		foreach ($errors as $key=>$value)
			foreach ($value ['error'] as $v)
				$sortArr [$key] .= $v ['msg'];
	if ($sortType == 'up')
		asort($sortArr);
	elseif ($sortType == 'down')
		arsort($sortArr);
	foreach ($sortArr as $k=>$v)
		$newArr [] = $errors [$k];
}
# Alive Mod/IP Graph:
$labels_ag = ['Module', 'RPi'];
$colorlist_ag = ["red", "orange"];
$timeshift = 8 * 3600;

$series_ag = array_fill(0, 2, array());
$i = 0;
foreach ($series_ag as &$serie) {
	$serie['pointStart'] = $now * 1000 - 3600 * 1000;
	$serie['pointInterval'] = 3600 * 1000;
	$serie['data'] = array();
	$serie['color'] = $colorlist_ag[$i];
	$serie['name'] = $labels_ag[$i];
	$i += 1;
}

$result = mysql_query("SELECT * FROM Aliverate");
$flag = FALSE;
while ($row = mysql_fetch_array($result)) {
	$unix = strtotime($row['time']);
	$localtime = ($unix + $timeshift) * 1000;
	if ($flag) {
		$time_str = date('Y-m-d H:i:s', $unix);
		$date_str = explode(' ', $time_str)[0];
		$time8 = strtotime($date_str . ' 08:00:00');
		$time20 = strtotime($date_str . ' 20:00:00');
		if ((abs($unix - $time8) % (24 * 3600) < 1800) or (abs($unix - $time20) % (24 * 3600) < 1800)) {
			$series_ag[0]['data'][] = array('x' => $localtime, 'y' => $row['modrate'] * 100, 'total' => $row['totalmod'], 'alive' => $row['alivemod']);
			$series_ag[1]['data'][] = array('x' => $localtime, 'y' => $row['iprate'] * 100, 'total' => $row['totalip'], 'alive' => $row['aliveip']);
		}
	} elseif ($now - 30 * 24 * 3600 < $unix)
		$flag = TRUE;
}
# Block Found Record:
$dates = [];
$categories_b = [];
for ($i = 30; $i > -1; $i--) {
	$dates[] = date('Y.m.d', $now - $i * 86400);
	$categories_b[] = date('m.d', $now - $i * 86400);
}

$series_b = [array('name' => 'Blocks', 'data' => [])];
foreach ($dates as $date) {
	$result = mysql_query("SELECT * FROM Block WHERE time BETWEEN \"" . $date . " 00:00:00\" AND \"" . $date . " 23:59:59\"");
	$block = 0;
	$info = [];
	while ($row = mysql_fetch_array($result)) {
		$block += $row['newblock'];
		$info[] = array('block' => $row['newblock'], 'id' => $row['ip'] . ":" . $row['port']);
	}
	$series_b[0]['data'][] = array('y' => $block, 'info' => $info);
}
#
$result = mysql_query("SELECT COUNT(DISTINCT ip) FROM " . $table . "  WHERE alive=true");
$aliveIP = mysql_fetch_array($result)[0];
$result = mysql_query("SELECT COUNT(DISTINCT ip), SUM(summodule), SUM(summodule0) FROM " . $table);
$row = mysql_fetch_array($result);
$allIP = $row[0];
$aliveMod = $row[1];
$allMod = $row[2];
?>

<html>
<link rel="stylesheet" href="css/bootstrap.min.css">
<link rel="stylesheet" href="css/style.css" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<script src="js/jquery.min.js"></script>
<script src="js/bootstrap.min.js"></script>
<?php if ($autorefresh)
	echo "<script src=\"js/comm.js\"></script>";
?>
<script src="js/highcharts.js"></script>
<script>
function refresh(){
	$.ajax({
	type:"POST",
		url:"refresh.php",
		data:{},
		dataType:"json",
		success:function(data){
			alert(data.msg);
		}
});
}
</script>
<script>
$(function () {
	$('#blocksfound').highcharts({
	chart: {type: 'column'},
		credits: {enabled: false},
		tooltip: {
		shared: true,
			useHTML: true,
			formatter: function () {
				var s = "<b>" + this.x + "</b><table>";
				for(i in this.points[0].point.info){
					info = this.points[0].point.info[i];
					if(info.block > 1){
						suffix = 's';
					}else{
						suffix = '';
					}
					s += '<tr style="font-size:12px"><td style="color:red">' + info.block + '&nbsp;</td><td style="color:red">block' + suffix + '&nbsp;</td><td>@</td><td>' + info.id + '</td></tr>';
				}
				s += '</table>';
				return s;
			}
},
	title: {text:'Blocks Found Record'},
	yAxis: {title:{text:'Blocks'}},
	xAxis: {
	title:{text:'Time (UTC+8)'},
		categories: <?php echo json_encode($categories_b); ?>
			},
			series: <?php echo json_encode($series_b); ?>
});
});
</script>
<script>
$(function () {
	$('#aliverate').highcharts({
	chart: {
	zoomType: 'x'
},
credits: {enabled: false},
tooltip: {
formatter: function () {
	var s = "";
	var j = 0;
	$.each(this.points, function (i, point) {
		if (j == 0) {
			s += '<b>' + Highcharts.dateFormat('%Y-%m-%d %H:%M', new Date(this.x)) + '</b><br>';
			s += 'Mod: <b>' + point.point.alive + ' / ' + point.point.total + '</b>';
		} else {
			s += '<br>RPi:  <b>' + point.point.alive + ' / ' + point.point.total + '</b>';
		}
		j++;
	});
	return s;
},
	shared: true
},
plotOptions: {line:{lineWidth:1.5,marker:{radius:0,symbol:"circle"}}},
title: {text:'Alive Mod/RPi Rate Graph'},
yAxis: {title:{text:'%'}},
xAxis: {
title:{text:'Time (UTC+8)'},
	tickInterval: 24 * 3600 * 1000,
	type: 'datetime',
	dateTimeLabelFormats: {
	minute: '%H:%M'
	}
	},
		series: <?php echo json_encode($series_ag); ?>
});
});
</script>
<script>
$(function () {
	$('#hashrate').highcharts({
	chart: {
	zoomType: 'x'
},
credits: {enabled: false},
plotOptions: {line:{lineWidth:1.5,marker:{radius:0,symbol:"circle"}}},
title: {text:'Hash Rate Graph'},
yAxis: {title:{text:'Hash/s'}},
xAxis: {
title:{text:'Time (UTC+8)'},
	tickInterval: 24 * 3600 * 1000,
	type: 'datetime',
	dateTimeLabelFormats: {
	minute: '%H:%M'
}
},
	series: <?php echo json_encode($series); ?>
});
});
</script>
<body>
	<nav class="navbar navbar-inverse" style="margin-bottom:0px;" role="navigation">
	  <div class="container">
		<div class="navbar-header">
		  <a class="navbar-brand" href="javascript:;"></a>
		</div>

		<div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
		  <ul class="nav navbar-nav">
			<li><a href="javascript:;">RPi:		<?php echo $aliveIP . "/" . $allIP; ?></a></li>
			<li><a href="javascript:;">Avalon4-1T:     <?php echo $aliveMod . "/" . $allMod; ?></a></li>
			<li><a href="javascript:;"><?php echo $showTime ?></a></li>
		  </ul>
		</div><!-- /.navbar-collapse -->
	  </div><!-- /.container-fluid -->
	</nav>

	<div class="row">
		<!--Left Start-->
		<div class="col-md-6">
			<div class="jumbotron">
<?php
$s = 1;
foreach ($farm_map as $zone_map) {
	for ($n = 0; $n < count($zone_map); $n++) {
		echo "<table class=\"tmap\"><tbody>";
		for ($y = 0; $y < count($zone_map[$n]); $y++) {
			echo "<tr><td class=\"yaxis\"><p class=\"axis\">";
			echo count($zone_map[$n])-$y . "</p></td>";
			for ($x = 0; $x < count($zone_map[$n][$y]); $x++) {
				$atom = $zone_map[$n][$y][$x];
				if (is_Null($atom))
					continue;
				if ($atom['skip'])
					echo "<td class=\"tmap\"></td>";
				elseif ($atom["alive"])
					echo "<td title=\"" . $atom['ip'] . "\" class=\"tmap\" style=\"background:" . $atom['backcolor'] .
						"\" onclick=\"window.open('cgminer.php?ip=" . $atom["ip"] . "&port=" . join(",",$atom['ports']) . "');\">
						<p class=\"tmap\" style=\"color:" . $atom['frontcolor'] . "\">" . $atom['modnum'] . "</p>
						<p class=\"tmap\" style=\"color:" . $atom['frontcolor'] . "\">" . $atom['maxtemp'] . "&deg;C</p>
						<p class=\"tmap\" style=\"color:" . $atom['frontcolor'] . "\">" . $atom['rate'] . "</p>
						</td>";
				else
					echo "<td title=\"" . $atom['ip'] . "\" class=\"tmap\" style=\"background:white\"
						onclick=\"window.open('cgminer.php?ip=" . $atom["ip"] . "&port=" . join(",",$atom['ports']) . "');\">
						<p class=\"tmapred\">N/A</p>
						</td>";
			}
			echo "</tr>";
		}
		echo "<tr><td class=\"oaxis\"> </td>";
		for ($x = 0; $x < count($zone_map[$n][0]); $x++) {
			if (is_Null($zone_map[$n][0][$x]))
				echo "<td class=\"xaxis\"> </td>";
			else {
				echo "<td class=\"xaxis\"><p class=\"axis\">" . $s . "</td>";
				$s ++;
			}
		}
		echo "</tr>";
		echo "</tbody></table>";
	}
}
?>
			</div>
			<div class="jumbotron">
				<div id="hashrate" style="width:100%; height: 720px !important;"></div>
			</div>
			<div class="jumbotron">
				<div id="aliverate" style="width:100%; height: 720px !important;"></div>
			</div>
			<div class="jumbotron">
				<div id="blocksfound" style="width:100%; height: 720px !important;"></div>
			</div>
		</div>
		<!--Left End-->
		<!--Right Start-->
		<div class="col-md-6">
			<div class="jumbotron">
				<h3>Information List:</h3>
					<table class="table table-bordered table-striped">
						<thead>
							<tr>
								<td>
									<strong>RPi</strong>
									<?php if ($sortType == 'down' && $sortName == 'ip') {?>
										<a href='?sort=ip_up' style="float: right;font-size: 10px;cursor: pointer;">
											<img src='./img/down.jpg' width="20" height="20" />
										</a>
									<?php } else {?>
										<a href='?sort=ip_down' style="float: right;font-size: 10px;cursor: pointer;">
											<img src='./img/up.jpg' width="20" height="20" />
										</a>
									<?php }?>
								</td>
								<td>
									<strong>Information</strong>
									<?php if ($sortType == 'down' && $sortName == 'info') {?>
										<a href='?sort=info_up' style="float: right;font-size: 10px;cursor: pointer;">
											<img src='./img/down.jpg' width="20" height="20" />
										</a>
									<?php } else {?>
										<a href='?sort=info_down' style="float: right;font-size: 10px;cursor: pointer;">
											<img src='./img/up.jpg' width="20" height="20" />
										</a>
									<?php }?>
								</td>
							</tr>
						</thead>
						<tbody>
<?php
if(count($newArr) === 0)
	echo "<tr><td>None</td><td>None</td></tr>";
else {
	foreach ($newArr as $error) {
		echo "<tr><td><a href=\"" . $error["href"] . "\">" . $error["id"] . "</a></td><td>";
		foreach ($error["error"] as $err)
			echo "<span style=\"color:" . $err["color"] . "\">" . $err["msg"] . "</span><br />";
		echo "</td></tr>";
	}
}
?>
						</tbody>
					</table>
			</div>
		</div>
		<!--Right end-->
	</div>
	<div><center>Powered by Canaan Creative</center></div>
</body>
</html>
