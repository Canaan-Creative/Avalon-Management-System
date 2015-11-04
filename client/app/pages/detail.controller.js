(function() {
	'use strict';

	angular
		.module('ams')
		.controller('DetailController', DetailController);

	DetailController.$inject = ['ShareService', 'APIService'];

	function DetailController(share, api) {
		/* jshint validthis: true */
		var vm = this;

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
			name: 'DH',
			value: function(data) {return data.dh.toFixed(1);}
		},{
			name: 'DH5m',
			value: function(data) {return data.dh5m.toFixed(1);}
		},{
			name: 'GHs5m',
			value: function(data) {return data.ghs5m.toFixed(0);}
		},{
			name: 'T',
			value: function(data) {return data.temp;}
		},{
			name: 'Fan',
			value: function(data) {return data.fan;}
		},{
			name: 'Volt',
			value: function(data) {return data.vol * 10000;}
		},{
			name: 'Freq',
			value: function(data) {return data.freq;}
		},{
			name: 'PG',
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

		function getConfig() {
		}

		function select(node) {
			vm.status.node = node;
			share.status.main.subTitle = node.ip + ':' + node.port;
			vm.getTab(vm.status.tabName);
		}

		function getTab(name) {
			var time;
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
				api.getStatus(
					name,
					time,
					vm.status.node.ip,
					vm.status.node.port
				).then(function() {
					vm.status.tabLoaded = true;
				});
				break;
			case 'config':
				getConfig();
				break;
			}
		}

		function setLED(module) {
		}
	}
})();
