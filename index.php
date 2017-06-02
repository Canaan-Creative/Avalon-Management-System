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
	} elseif ($x < 0.875) {
		$r = 256;
		$g = 256 - ($x - 0.625) / 0.25 * 256;
		$b = 0;
	} elseif ($x <= 1) {
		$r = 256 - ($x - 0.875) / 0.25 * 256;
		$g = 0;
		$b = 0;
	} else {
		$r = 128;
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
if (array_key_exists('auto', $_GET))
	$url_suffix = '&auto=' . $_GET['auto'];
else
	$url_suffix = '';
if (array_key_exists('auto', $_GET) && $_GET['auto'] !== "" && $_GET['auto'] !== null) {
	$auto = $_GET['auto'];
	if (strcasecmp($auto, "true") == 0 || strcasecmp($auto, "yes") == 0 || strcasecmp($auto, "y") == 0)
		$autorefresh = True;
}
## T-map

include 'config.php';

$dbhandle = mysql_connect("localhost", $user, $passwd)
	or die('Could not connect: ' . mysql_error());
$selected = mysql_select_db($dbname, $dbhandle)
	or die("Could not select database.");
$farmcfg = $cfg['Json']['farm'];
$farm = json_decode(file_get_contents($farmcfg), true);

$zones = $farm["zone"];

$farm_map = array();

$z = 0;

$result = mysql_query("SELECT time FROM head WHERE type = 'main'");
$time = mysql_fetch_array($result)['time'];
$tmp = explode('_', $time);
$showTime = $tmp[0] . '-' . $tmp[1] . '-' . $tmp[2] . ' ' . $tmp [3] . ':' . $tmp[4];
$table = 'Miner_' . $time;

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
					SUM(rate15min) AS sumrate, MAX(maxtemperature) AS maxtemp,
					AVG(avgtemperature) AS avgtemp FROM " . $table . " WHERE ip='" . $ip . "'");
				$row = mysql_fetch_array($result);
				$modnum = $row['summod'] . "/" . $row['summod0'];
				$maxtemp = $row['maxtemp'];
				$avgtemp = (int)$row['avgtemp'];
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
				$avgtemp ="";
				$rate = "";
			}
			if (!$ports)
				$ports = [4028];
			$backcolor = rainbow($maxtemp, 40, 50);
			$frontcolor = invert_color($backcolor);
			$zone_map[$n][$y][$x] = array(
				"skip" => false,
				"alive" => $alive,
				"ip" => $ip,
				"ports" => $ports,
				"modnum" => $modnum,
				"maxtemp" => $maxtemp,
				"avgtemp" => $avgtemp,
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

include 'info.php';
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
<head>
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
function led(command) {
	var _command = command;
	$.ajax({
		type: "POST",
		url: "led.php",
		data: {command: _command},
		dataType: "json",
		success: function(data) {
				alert(data.msg);
			}
	});
}
</script>
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
</head>
<body>
	<nav class="navbar navbar-inverse" style="margin-bottom:0px;" role="navigation">
	  <div class="container">
		<div class="navbar-header">
		  <a class="navbar-brand" href="javascript:;"></a>
		</div>

		<div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
		  <ul class="nav navbar-nav">
			<li><a href="javascript:;">RPi:		<?php echo $aliveIP . "/" . $allIP; ?></a></li>
			<li><a href="javascript:;">Avalon7-6T:     <?php echo $aliveMod . "/" . $allMod; ?></a></li>
			<li><a href="javascript:;"><?php echo $showTime ?></a></li>
		  </ul>
		</div><!-- /.navbar-collapse -->
	  </div><!-- /.container-fluid -->
	</nav>

	<div class="row">
		<!--Left Start-->
		<div class="col-md-6">
			<div class="jumbotron">
				<button onClick="led('temp');">LED: Temp &gt; 45&deg;C</button>
				<button onClick="led('dh');">LED: DH &gt; 10%</button>
				<button onClick="led('clear');">LED: Clear</button>
			</div>
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
						<p class=\"tmap\" style=\"color:" . $atom['frontcolor'] . "\">" . $atom['avgtemp'] . "/" . $atom['maxtemp'] . "&deg;C</p>
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
			<div>
				<ul class="nav nav-tabs" role="tablist">
					<li role="presentation" class="active"><a href="#all" role="tab" data-toggle="tab">All</a></li>

					<li role="presentation" class="dropdown">
						<a class="dropdown-toggle" data-toggle="dropdown" href="#">
							Critical<span class="caret"></span>
						</a>
						<ul class="dropdown-menu" role="menu">
							<li><a href="#wrongmw" data-toggle="tab" role="tab">MW异常</a></li>
							<li><a href="#wrongcrc" data-toggle="tab" role="tab">CRC异常</a></li>
							<li><a href="#missing" data-toggle="tab" role="tab">设备缺失</a></li>
							<li><a href="#hightemp" data-toggle="tab" role="tab">温度过高</a></li>
							<li><a href="#wrongpg" data-toggle="tab" role="tab">电源模块错误</a></li>
							<li><a href="#apimess" data-toggle="tab" role="tab">API Mess</a></li>
						</ul>
					</li>

					<li role="presentation" class="dropdown">
						<a class="dropdown-toggle" data-toggle="dropdown" href="#">
							Warning<span class="caret"></span>
						</a>
						<ul class="dropdown-menu" role="menu">
							<li><a href="#highdh" data-toggle="tab" role="tab">错误率过高</a></li>
							<li><a href="#fanstopped" data-toggle="tab" role="tab">风扇停转</a></li>
							<li><a href="#miningstopped" data-toggle="tab" role="tab">挖矿停止</a></li>
							<li><a href="#lowhashrate" data-toggle="tab" role="tab">算力过低</a></li>
							<li><a href="#lowtemp" data-toggle="tab" role="tab">温度过低</a></li>
							<li><a href="#wrongvolt" data-toggle="tab" role="tab">电压错误</a></li>
						</ul>
					</li>

				</ul>
				<div class="tab-content">

				<div role="tabpanel" class="tab-pane active" id="all">
				<table class="table table-bordered table-striped">
					<thead>
						<tr>
							<td><strong>RPi</strong></td>
							<td><strong>Information</strong></td>
						</tr>
					</thead>
					<tbody>
<?php
if(count($errors) === 0)
	echo "<tr><td>None</td><td>None</td></tr>";
else {
	foreach ($errors as $error) {
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

<?php
foreach ($errorc as $key => $value) {
	echo "
				<div role=\"tabpanel\" class=\"tab-pane\" id=\"" . $key . "\">
				<table class=\"table table-bordered table-striped\">
					<thead>
						<tr>
							<td><strong>RPi</strong></td>
							<td><strong>Information</strong></td>
						</tr>
					</thead>
					<tbody>";
	if(count($value) === 0)
		echo "<tr><td>None</td><td>None</td></tr>";
	else {
		foreach ($value as $error) {
			echo "<tr><td><a href=\"" . $error["href"] . "\">" . $error["id"] . "</a></td><td>";
			foreach ($error["error"] as $err)
				echo "<span style=\"color:" . $err["color"] . "\">" . $err["msg"] . "</span><br />";
			echo "</td></tr>";
		}
	}
	echo "
					</tbody>
				</table>
				</div>";
}
?>


				</div>
			</div>
			</div>
		</div>
		<!--Right end-->
	</div>
	<div><center>Powered by Canaan Creative</center></div>
</body>
</html>
