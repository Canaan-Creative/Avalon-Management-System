/*
 Copyright (C) 2015-2016  DING Changchang (of Canaan Creative)

 This file is part of Avalon Management System (AMS).

 AMS is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 AMS is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with AMS. If not, see <http://www.gnu.org/licenses/>.
*/
(function() {
	'use strict';

	angular
		.module('ams')
		.controller('SettingController', SettingController);

	SettingController.$inject = ['ShareService', 'APIService'];

	function SettingController(share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.auth = share.status.auth;
		vm.status = share.status.setting;
		vm.data = api.data;
		vm.nodeChanged = false;
		vm.tempNodes = false;
		vm.deletedNodes = [];

		vm.showDialog = share.utils.showDialog;

		vm.deleteNode = deleteNode;
		vm.addNode = addNode;
		vm.cancelNode = cancelNode;
		vm.saveNode = saveNode;

		share.status.main.title = "Setting";
		share.status.main.subTitle = false;

		api.getNodes().then(cloneNodes);

		function cloneNodes() {
			var temp = [];
			for (var i = 0; i < vm.data.nodes.length; i++)
				temp.push({
					ip: vm.data.nodes[i].ip,
					port: vm.data.nodes[i].port,
					mods: vm.data.nodes[i].mods,
				});
			vm.tempNodes = temp;
		}

		function saveNode() {
			api.updateNodes(vm.tempNodes, vm.auth.token);
		}

		function cancelNode() {
			vm.tempNodes = false;
			api.getNodes().then(cloneNodes);
		}

		function deleteNode(node) {
			vm.nodeChanged = true;
			vm.tempNodes.splice(vm.tempNodes.indexOf(node), 1);
		}

		function addNode() {
			vm.nodeChanged = true;
			vm.tempNodes.push({
				ip: null, port: 4028, mods: 0
			});
		}
	}
})();
