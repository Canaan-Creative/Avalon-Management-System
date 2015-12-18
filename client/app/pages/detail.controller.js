(function() {
	'use strict';

	angular
		.module('ams')
		.controller('DetailController', DetailController);

	DetailController.$inject = ['ShareService', 'APIService'];

	function DetailController(share, api) {
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
			value: function(data) {return data.last_share_time;}
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
		}];

		vm.moduleTable = [{
			name: 'ID',
			index: 0,
			value: function(data) {return data.device_id + ':' + data.module_id;}
		},{
			name: 'Elapesed',
			index: 1,
			value: function(data) {return data.elapsed;}
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
		api.getNodes().then(previousSelect);


		function previousSelect() {
			if (vm.status.node) {
				for (var node of vm.data.nodes)
					if (vm.status.node.ip == node.ip &&
						vm.status.node.port == node.port) {
							select(node);
							return;
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
			vm.status.tabName = name;
			vm.sortIndex = undefined;
			vm.sortReverse = false;

			switch (name) {
			case 'summary':
				api.getStatus('pool', time, node.ip, node.port).then(
					function() {
						if (node == vm.status.node)
							vm.status.poolCardLoaded = true;
				});
				break;
			case 'device':
			case 'module':
				api.getStatus(name, time, node.ip, node.port).then(
					function() {
						if (node == vm.status.node) {
							if (name == 'module' && vm.data.module.length > 0) {
								var initID = vm.data.module[0].device_id;
								var theme = true;
								for (var module of vm.data.module) {
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
			return vm.moduleTable[Math.abs(vm.sortIndex)].value;
		}

	}
})();
