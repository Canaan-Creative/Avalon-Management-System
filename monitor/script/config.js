function isInterger(str) {
	var n = ~~Number(str);
	return String(n) === str;
}

function unlock() {
	$("#devices tbody tr td:not(.uneditable)").prop("contentEditable", true);

	//stable row height
	var rowHeight = parseInt($("#devices tbody tr").css("height"));
	var buttonHeight = parseInt($("#devices tbody tr td button").css("height"));
	var padding = (rowHeight - buttonHeight) / 2 + "px";
	$("#devices tbody tr td button").parent().css("padding", padding);

	$(".unlock").show();
	$("#unlock").remove();
}

function save() {
	var error = false;
	var miner = $("#devices tbody tr:not(.unlock)").map(function() {
		var cells = $(this).find("td:not(.uneditable)");

		// check validation of IP
		var ip = $(cells[0]).text();
		$(cells[0]).css("color", "");
		$(cells[0]).css("background", "");
		if (ip === "")
			$(cells[0]).css("background", "red");
		if (ip.split(".").length !== 4) {
			error = true;
			$(cells[0]).css("color", "red");
		} else for (var p of ip.split("."))
			if (!isInterger(p) || parseInt(p) > 255 && parseInt(p) < 0) {
				error = true;
				$(cells[0]).css("color", "red");
				break;
			}

		// check validation of port
		var port = $(cells[1]).text();
		$(cells[1]).css("color", "");
		$(cells[1]).css("background", "");
		if (port === "")
			$(cells[1]).css("background", "red");
		if (!isInterger(port) || parseInt(port) > 65535 && parseInt(port) < 0) {
				error = true;
				$(cells[1]).css("color", "red");
		}
		port = parseInt(port);

		// check validation of mod list
		var mods = $(cells[2]).text();
		$(cells[2]).css("color", "");
		$(cells[2]).css("background", "");
		if (mods === "")
			$(cells[2]).css("background", "red");
		if (!mods.match(/^[0-9]+(?:,[0-9]+)*$/)) {
			error = true;
			$(cells[2]).css("color", "red");
		}
		mods = mods.split(",").map(function(mod) {
			return {num: parseInt(mod)};
		});

		return {ip: ip, port: port, mods: mods};
	}).get();

	if (error)
		return false;

	$.ajax({
		type: "POST",
		url: 'updateYAML.php',
		data: {miner: miner},
		success: function() {},
	});
}

function reload() {
	location.reload();
}

function addDevice() {
	$("#devices tbody tr:last").before(`
<tr>
  <td class="col-md-4" contentEditable="true"></td>
  <td class="col-md-2" contentEditable="true"></td>
  <td class="col-md-4" contentEditable="true"></td>
  <td class="col-md-2 uneditable">
    <button type="button" class="btn btn-default btn-xs removeDevice">
      Remove
    </button>
  </td>
</tr>`
	);
}

function removeDevice() {
	$(this).parents("tr").remove();
}

$(function() {
	$("#devices tbody").on("click", "tr td .removeDevice", removeDevice);
	$("#addDevice").on("click", addDevice);
	$("#unlock").on("click", unlock);
	$("#save").on("click", save);
	$("#cancel").on("click", reload);
});
