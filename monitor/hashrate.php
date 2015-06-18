<?php
include 'include.php';

$dbhandle = mysql_connect('localhost', $user, $password)
	or die('Cannot connect: ' . mysql_error());
$selected = mysql_select_db($database, $dbhandle)
	or die('Cannot select database.');

$query = <<<EOT
SELECT a.*, b.mhs
  FROM hashrate a
  JOIN (
        SELECT time, SUM(mhs) AS mhs
          FROM miner
         GROUP BY time
       ) b
    ON a.time = b.time
EOT;
$result = mysql_query($query);

var_dump($result);
