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

	DetailController.$inject = ['$filter', '$location', 'ShareService', 'APIService'];

	function DetailController($filter, $location, share, api) {
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

		vm.poolTable = [{
			name: 'URL',
			value: function(data) {return data.url;}
		},{
			name: 'User',
			value: function(data) {return data.user;}
		},{
			name: 'Status',
			value: function(data) {
				if (data.stratum_active && data.status === 'Alive')
					return 'Active';
				else if (data.status === 'Alive')
					return 'Standby';
				else
					return 'Dead';
			}
		},{
			name: 'W',
			tooltip: 'GetWorks',
			value: function(data) {return data.getworks;}
		},{
			name: 'A',
			tooltip: 'Accepted',
			value: function(data) {return data.accepted;}
		},{
			name: 'R',
			tooltip: 'Rejected',
			value: function(data) {return data.rejected;}
		},{
			name: 'D',
			tooltip: 'Discarded',
			value: function(data) {return data.discarded;}
		},{
			name: 'S',
			tooltip: 'Stale',
			value: function(data) {return data.stale;}
		},{
			name: 'LST',
			value: function(data) {
				return $filter('date')(
					data.last_share_time * 1000,
					'yyyy-MM-dd HH:mm:ss'
				);
			}
		},{
			name: 'LSD',
			value: function(data) {return data.last_share_difficulty;}
		}];

		vm.deviceTable = [{
			name: 'ID',
			index: 0,
			value: function(data) {return data.device_id;}
		},{
			name: 'Enabled',
			index: 1,
			value: function(data) {return data.enabled;}
		},{
			name: 'Status',
			index: 2,
			value: function(data) {return data.status;}
		},{
			name: 'Temp',
			index: 3,
			value: function(data) {return data.temperature;}
		},{
			name: 'GHsav',
			index: 4,
			value: function(data) {return parseInt(data.mhs_av / 1000);}
		},{
			name: 'GHs5s',
			index: 5,
			value: function(data) {return parseInt(data.mhs_5s / 1000);}
		},{
			name: 'GHs1m',
			index: 6,
			value: function(data) {return parseInt(data.mhs_1m / 1000);}
		},{
			name: 'GHs5m',
			index: 7,
			value: function(data) {return parseInt(data.mhs_5m / 1000);}
		},{
			name: 'GHs15m',
			index: 8,
			value: function(data) {return parseInt(data.mhs_15m / 1000);}
		},{
			name: 'LastValiddata',
			index: 9,
			value: function(data) {return data.last_valid_work;}
		},{
			name: 'SmartSpeed',
			index: 10,
			value: function(data) {return data.smart_speed;}
		}];

		vm.moduleTable = [{
			name: 'ID',
			index: 0,
			value: function(data) {return data.device_id + ':' + data.module_id;},
			sortValue: function(data) {return (data.device_id << 8) + data.module_id;}
		},{
			name: 'Elapesed',
			index: 1,
			value: function(data) {return parseInt(data.elapsed);}
		},{
			name: 'Version',
			index: 2,
			value: function(data) {return data.ver;}
		},{
			name: 'LW',
			index: 3,
			value: function(data) {return data.lw;}
		},{
			name: 'GHs',
			index: 4,
			value: function(data) {return parseInt(data.ghsmm);}
		},{
			name: 'T',
			index: 5,
			value: function(data) {return data.temp + '/' + data.temp0 + '/' + data.temp1;}
		},{
			name: 'Fan',
			index: 6,
			value: function(data) {return data.fan;}
		},{
			name: 'Volt',
			index: 7,
			value: function(data) {return data.vol;}
		},{
			name: 'PG',
			index: 8,
			value: function(data) {return data.pg;}
		},{
			name: 'EC',
			index: 9,
			value: function(data) {return data.ec;}
		}];

		vm.getDeviceTable = getDeviceTable;
		vm.getModuleTable = getModuleTable;
		vm.sortIndex = undefined;
		vm.sortReverse = false;

		vm.select = select;
		vm.getTab = getTab;
		vm.setSingleLED = setSingleLED;

		share.status.main.title = "Detail";
		share.status.main.subTitle = false;

		var params = $location.search();
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
			$location
				.search('ip', null)
				.search('port', null)
				.search('dna', null);
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
			share.status.main.subTitle = node.ip + ':' + node.port;
			vm.getTab(vm.status.tabName);
		}

		function getTab(name) {
			var time;
			var node = vm.status.node;
			if (share.status.main.latest)
				time = 'latest';
			else
				time = share.status.main.time;
			vm.status.tabLoaded = false;
			vm.status.poolCardLoaded = false;
			vm.status.summaryCardLoaded = false;
			vm.status.tabName = name;
			vm.sortIndex = undefined;
			vm.sortReverse = false;
			vm.hashrateChart.loaded = false;

			switch (name) {
			case 'summary':
				api.getStatus('pool', time, node.ip, node.port).then(
					function() {
						if (node == vm.status.node)
							vm.status.poolCardLoaded = true;
				});
				api.getStatus('summary', time, node.ip, node.port).then(
					function() {
						if (node == vm.status.node)
							vm.status.summaryCardLoaded = true;
				});
				if (share.status.main.time === 0)
					share.getLastTime().then(getNodeHashrate);
				else
					getNodeHashrate();
				break;
			case 'device':
			case 'module':
				api.getStatus(name, time, node.ip, node.port).then(
					function() {
						if (node == vm.status.node) {
							if (name == 'module' && vm.data.module.length > 0) {
								var initID = vm.data.module[0].device_id;
								var theme = true;
								for (var i = 0; i < vm.data.module.length; i++) {
									var module = vm.data.module[i];
									module.highlight = (module.dna === vm.status.highlightDNA);
									if (module.device_id != initID) {
										initID = module.device_id;
										theme = !theme;
									}
									module.theme = theme;
									module.led = parseInt(module.led);
								}
							}
							vm.status.tabLoaded = true;
						}
				});
				break;
			case 'config':
				api.getConfig(node.ip, node.port).then(
					function() {
						if (node == vm.status.node)
							vm.status.tabLoaded = true;
				});
				break;
			}
		}

		function setSingleLED(module) {
			api.setLED({
				modules: [{
					ip: module.ip,
					port: module.port,
					device_id: module.device_id,
					module_id: module.module_id,
					led: module.led,
				}]
			}).then(function() {
				vm.getTab(vm.status.tabName);
			});
		}

		function getDeviceTable() {
			if (vm.sortIndex === undefined)
				return;
			vm.sortReverse = (1 / vm.sortIndex > 0);
			return vm.deviceTable[Math.abs(vm.sortIndex)].value;
		}

		function getModuleTable() {
			if (vm.sortIndex === undefined)
				return;
			vm.sortReverse = (1 / vm.sortIndex > 0);
			var item = vm.moduleTable[Math.abs(vm.sortIndex)];
			if (item.sortValue === undefined)
				return item.value;
			else
				return item.sortValue;
		}

	}
})();
