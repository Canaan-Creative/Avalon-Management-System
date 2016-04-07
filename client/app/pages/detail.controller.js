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

		// vm.status = {
		//	tabLoaded: /* loading...    */ bool,
		//	tabName:   /* selected tab  */ 'summary' | 'device' | 'module' | 'config',
		//	node:      /* selected node */ {ip, port},
		// }
		vm.status = share.status.detail;

		vm.data = api.data;

		vm.summaryTable = [{
			name: 'Elapsed',
			value: function(data) {return data && data.elapsed;}
		},{
			name: 'GHs 15m',
			value: function(data) {return data && parseInt(data.mhs_15m / 1000);}
		},{
			name: 'GHs 1m',
			value: function(data) {return data && parseInt(data.mhs_1m / 1000);}
		},{
			name: 'GHs 5m',
			value: function(data) {return data && parseInt(data.mhs_5m / 1000);}
		},{
			name: 'GHs 5s',
			value: function(data) {return data && parseInt(data.mhs_5s / 1000);}
		},{
			name: 'GHs av',
			value: function(data) {return data && parseInt(data.mhs_av / 1000);}
		},{
			name: 'Found Blocks',
			value: function(data) {return data && data.found_blocks;}
		},{
			name: 'Getworks',
			value: function(data) {return data && data.getworks;}
		},{
			name: 'Accepted',
			value: function(data) {return data && data.accepted;}
		},{
			name: 'Rejected',
			value: function(data) {return data && data.rejected;}
		},{
			name: 'Hardware Errors',
			value: function(data) {return data && data.hardware_errors;}
		},{
			name: 'Utility',
			value: function(data) {return data && data.utility;}
		},{
			name: 'Discarded',
			value: function(data) {return data && data.discarded;}
		},{
			name: 'Stale',
			value: function(data) {return data && data.stale;}
		},{
			name: 'Get Failures',
			value: function(data) {return data && data.get_failures;}
		},{
			name: 'Local Work',
			value: function(data) {return data && data.local_work;}
		},{
			name: 'Remote Failures',
			value: function(data) {return data && data.remote_failures;}
		},{
			name: 'Network Blocks',
			value: function(data) {return data && data.network_blocks;}
		},{
			name: 'Total MHash',
			value: function(data) {return data && data.total_mh;}
		},{
			name: 'Work Utility',
			value: function(data) {return data && data.work_utility;}
		},{
			name: 'Diff Accepted',
			value: function(data) {return data && data.difficulty_accepted;}
		},{
			name: 'Diff Rejected',
			value: function(data) {return data && data.difficulty_rejected;}
		},{
			name: 'Diff Stale',
			value: function(data) {return data && data.difficulty_stale;}
		},{
			name: 'Best Share',
			value: function(data) {return data && data.best_share;}
		},{
			name: 'Device Hardware Error',
			value: function(data) {return data && (data.device_hardware + '%');}
		},{
			name: 'Device Rejected',
			value: function(data) {return data && (data.device_rejected + '%');}
		},{
			name: 'Pool Rejected',
			value: function(data) {return data && (data.pool_rejected + '%');}
		},{
			name: 'Pool Stale',
			value: function(data) {return data && (data.pool_stale + '%');}
		},{
			name: 'Last Getwork',
			value: function(data) {
				return data && $filter('date')(
					data.last_getwork * 1000,
					'yyyy-MM-dd HH:mm:ss'
				);
			}
		}];

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
			vm.status.tabLoaded = false;
			vm.status.poolCardLoaded = false;
			vm.status.summaryCardLoaded = false;
			vm.status.tabName = name;
			vm.sortIndex = undefined;
			vm.sortReverse = false;
			vm.hashrateChart.loaded = false;

			switch (name) {
			case 'summary':
				api.getStatus('summary', time, node.ip, node.port).then(
					function() {
						if (node == vm.status.node)
							vm.status.summaryCardLoaded = true;
				});
				share.status.main.timePromise.then(getNodeHashrate);
				break;
			}
		}
	}
})();
