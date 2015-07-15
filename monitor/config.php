<?php
include 'include.php';
?>
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <link href="style/bootstrap.min.css" rel="stylesheet" />
    <link href="style/bootstrap-theme.min.css" rel="stylesheet" />
    <link href="style/config.css" rel="stylesheet" />
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
          <?php foreach ($cfg["miner"] as $miner) { ?>
          <tr>
            <td class="col-md-4"><?php echo $miner["ip"]; ?></td>
            <td class="col-md-2"><?php echo $miner["port"]; ?></td>
            <td class="col-md-4"><?php
            $mods = array();
            foreach ($miner["mods"] as $mod)
                $mods[] = $mod["num"];
            echo join(",", $mods); ?></td>
            <td class="col-md-2 uneditable button">
              <button type="button" class="btn btn-default btn-xs removeDevice unlock">
                Remove
              </button>
            </td>
          </tr>
          <?php } ?>
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
      <button type="button" class="btn btn-default" id="unlock">Unlock</button>
      <button type="button" class="btn btn-default unlock" id="save">Save</button>
      <button type="button" class="btn btn-default unlock" id="cancel">Cancel</button>
    </div>
    <script src="script/jquery.min.js"></script>
    <script src="script/bootstrap.min.js"></script>
    <script src="script/config.js"></script>
  </body>
</html>
