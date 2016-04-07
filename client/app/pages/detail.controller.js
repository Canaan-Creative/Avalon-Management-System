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
		.controller('DetailController', DetailController);

	DetailController.$inject = ['$filter', '$stateParams', 'ShareService', 'APIService'];

	function DetailController($filter, $stateParams, share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.auth = false;

		vm.status = share.status.detail;
		// vm.status = {
		//	tabName:   /* selected tab  */ 'summary' | 'device' | 'module' | 'config',
		//	node:      /* selected node */ {ip, port},
		// }

		vm.data = api.data;

		vm.select = select;
		vm.reload = reload;
		vm.getTab = getTab;

		share.status.main.title = "Detail";
		share.status.main.subTitle = false;

		if (share.status.main.latest)
			vm.status.time = 'latest';
		else
			vm.status.time = share.status.main.time;
		vm.status.reloadListeners = [];

		var params = $stateParams;
		if (params.ip && params.port) {
			vm.status.tabIndex = 0;
			vm.status.tabName = "summary";
			vm.status.node = {
				ip: params.ip,
				port: params.port,
			};
			if (params.dna) {
				vm.status.tabName = "module";
				vm.status.tabIndex = 2;
				vm.status.highlightDNA = params.dna;
			}
			$stateParams.ip = null;
			$stateParams.port = null;
			$stateParams.dna = null;
		}
		api.getNodes().then(previousSelect);

		vm.hashrateChart = {};
		vm.hashrateChart.loaded = false;
		vm.hashrateChart.options = share.hashrateChartOptions;

		vm.data = api.data;

		function getNodeHashrate() {
			api.getNodeHashrate(
				vm.status.node.ip,
				vm.status.node.port,
				share.status.main.time - 30 * 24 * 3600,
				share.status.main.time
			).then(
				function() {
					vm.hashrateChart.loaded = true;
			});
		}

		function previousSelect() {
			if (vm.status.node) {
				for (var i = 0; i < vm.data.nodes.length; i++) {
					var node = vm.data.nodes[i];
					if (vm.status.node.ip == node.ip &&
						vm.status.node.port == node.port) {
							select(node);
							return;
					}
				}
				vm.status.node = false;
			}
		}

		function select(node) {
			if (vm.status.node && vm.status.node !== node)
				vm.status.node.selected = false;
			node.selected = true;
			vm.status.node = node;
			share.status.main.subTitle = [node.ip + ':' + node.port];
			vm.getTab(vm.status.tabName);
		}

		function reload() {
			for (var i = 0; i < vm.status.reloadListeners.length; i++) {
				var listener = vm.status.reloadListeners[i];
				if (listener !== undefined)
					listener();
			}
		}

		function getTab(name) {
			var node = vm.status.node;
			var time = vm.status.time;
			vm.status.tabName = name;
			vm.hashrateChart.loaded = false;

			switch (name) {
			case 'summary':
				share.status.main.timePromise.then(getNodeHashrate);
				break;
			}
		}
	}
})();
