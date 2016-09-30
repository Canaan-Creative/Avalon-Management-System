<?php
if (! isset ($_COOKIE['userId'])) {
	header('Location:/status/login.php');
	die;
}
include 'config.php';
$farmcfg = $cfg['Json']['farm'];
$farm = json_decode(file_get_contents($farmcfg), true);
$zones = $farm["zone"];
?>
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <link href="css/bootstrap.min.css" rel="stylesheet">
    <link href="css/config.css" rel="stylesheet">
    <title>AMS - Configuration</title>
  </head>
  <body>
    <div class="panel panel-default">
      <div class="panel-heading">Devices</div>
      <table class="table table-hover" id="devices">
        <thead>
          <tr>
            <th class="col-md-4">IP</th>
            <th class="col-md-2">Port</th>
            <th class="col-md-4">Device List</th>
            <th class="col-md-2"></th>
          </tr>
        </thead>
        <tbody>
        <?php
foreach ($zones as $zone) {
	foreach ($zone["miner"] as $miner) {?>
          <tr>
            <td class="col-md-4"><?php echo $miner["ip"]; ?></td>
            <td class="col-md-2"><?php echo $miner["cgminer"][0]["port"]; ?></td>
            <td class="col-md-4"><?php echo join(",", $miner["cgminer"][0]["mod"]); ?></td>
            <td class="col-md-2 uneditable button">
              <button type="button" class="btn btn-default btn-xs removeDevice unlock">
                Remove
              </button>
            </td>
          </tr>
          <?php
	}
} ?>
          <tr class="unlock">
            <td class="col-md-4 uneditable"></td>
            <td class="col-md-2 uneditable"></td>
            <td class="col-md-4 uneditable"></td>
            <td class="col-md-2 uneditable button">
              <button type="button" class="btn btn-default btn-xs unlock" id="addDevice">
                Add
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div>
    </div>
    <div>
      <button type"button" class="btn btn-default" id="unlock">Unlock</button>
      <button type="button" class="btn btn-default unlock" id="save">Save</button>
      <button type="button" class="btn btn-default unlock" id="cancel">Cancel</button>
    </div>
    <script src="js/jquery.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/config.js"></script>
  </body>
</html>
