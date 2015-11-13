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

		vm.deviceTable = [{
			name: 'ID',
			value: function(data) {return data.device_id;}
		},{
			name: 'Enabled',
			value: function(data) {return data.enabled;}
		},{
			name: 'Status',
			value: function(data) {return data.status;}
		},{
			name: 'Temp',
			value: function(data) {return data.temperature;}
		},{
			name: 'GHsav',
			value: function(data) {return (data.mhs_av / 1000).toFixed(0);}
		},{
			name: 'GHs5s',
			value: function(data) {return (data.mhs_5s / 1000).toFixed(0);}
		},{
			name: 'GHs1m',
			value: function(data) {return (data.mhs_1m / 1000).toFixed(0);}
		},{
			name: 'GHs5m',
			value: function(data) {return (data.mhs_5m / 1000).toFixed(0);}
		},{
			name: 'GHs15m',
			value: function(data) {return (data.mhs_15m / 1000).toFixed(0);}
		},{
			name: 'LastValiddata',
			value: function(data) {return data.last_valid_work;}
		}];

		vm.moduleTable = [{
			name: 'ID',
			value: function(data) {return data.device_id + ':' + data.module_id;}
		},{
			name: 'Elapesed',
			value: function(data) {return data.elapsed;}
		},{
			name: 'Version',
			value: function(data) {return data.ver;}
		},{
			name: 'LW',
			value: function(data) {return data.lw;}
		},{
			name: 'GHs',
			value: function(data) {return data.ghsmm.toFixed(0);}
		},{
			name: 'T',
			value: function(data) {return data.temp + '/' + data.temp0 + '/' + data.temp1;}
		},{
			name: 'Fan',
			value: function(data) {return data.fan;}
		},{
			name: 'Volt',
			value: function(data) {return data.vol;}
		},{
			name: 'PG',
			value: function(data) {return data.pg;}
		},{
			name: 'EC',
			value: function(data) {return data.pg;}
		}];

		vm.select = select;
		vm.getTab = getTab;
		vm.setLED = setLED;

		share.status.main.title = "Detail";
		share.status.main.subTitle = false;
		api.getNodes();


		function getSummary() {
		}

		function select(node) {
			if (vm.status.node)
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
			vm.status.tabName = name;

			switch (name) {
			case 'summary':
				getSummary();
				break;
			case 'device':
			case 'module':
				api.getStatus(name, time, node.ip, node.port).then(
					function() {
						if (node == vm.status.node) {
							var initID = vm.data.module[0].device_id;
							var theme = true;
							for (var module of vm.data.module) {
								if (module.device_id != initID) {
									initID = module.device_id;
									theme = !theme;
								}
								module.theme = theme;
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

		function setLED(module) {
		}
	}
})();
