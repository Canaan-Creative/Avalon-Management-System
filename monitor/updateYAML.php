<?php
include 'include.php';

if ($_POST) {
	foreach ($_POST as $key => $value)
		$cfg[$key] = $value;
	yaml_emit_file($file, $cfg);
}
