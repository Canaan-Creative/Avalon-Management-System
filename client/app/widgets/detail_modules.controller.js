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
		.controller('DetailModulesController', DetailModulesController);

	DetailModulesController.$inject = ['ShareService', 'APIService'];

	function DetailModulesController(share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.status = share.status.detail;
		vm.data = api.data;

		vm.loaded = false;
		vm.sortIndex = undefined;
		vm.sortReverse = false;
		vm.table = [{
			name: 'ID',
			index: 0,
			value: function(data) {return data.device_id + ':' + data.module_id;},
			sortValue: function(data) {return (data.device_id << 8) + data.module_id;}
		}, {
			name: 'Elapesed',
			index: 1,
			value: function(data) {return parseInt(data.elapsed);}
		}, {
			name: 'Version',
			index: 2,
			value: function(data) {return data.ver;}
		}, {
			name: 'LW',
			index: 3,
			value: function(data) {return data.lw;}
		}, {
			name: 'DH',
			index: 4,
			value: function(data) {return data.dh + '%';}
		}, {
			name: 'WU',
			index: 5,
			value: function(data) {return data.wu;}
		}, {
			name: 'GHs',
			index: 6,
			value: function(data) {return parseInt(data.ghsmm);}
		}, {
			name: 'T',
			index: 7,
			value: function(data) {return data.temp + '/' + data.tmax;}
		}, {
			name: 'Fan',
			index: 8,
			value: function(data) {return data.fan + '/' + data.fanr + '%';}
		}, {
			name: 'PG',
			index: 9,
			value: function(data) {return data.pg;}
		}, {
			name: 'ECHU',
			index: 10,
			value: function(data) {return data.echu.join(' ');}
		}, {
			name: 'ECMM',
			index: 11,
			value: function(data) {return data.ecmm;}
		}, {
			name: 'CRC',
			index: 12,
			value: function(data) {return data.crc.join(' ');}
		}];

		vm.getTable = getTable;
		vm.setLED = setLED;

		vm.status.reloadListeners.push(main);
		main();

		function main(sortIndex, sortReverse) {
			var node = vm.status.node;
			var time = vm.status.time;
			vm.loaded = false;
			vm.sortIndex = sortIndex;
			vm.sortReverse = sortReverse || false;
			api.getStatus('module', time, node.ip, node.port).then(
				function() {
					if (node.ip === vm.status.node.ip &&
							node.port === vm.status.node.port) {
						if (vm.data.module && vm.data.module.length > 0) {
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
						vm.loaded = true;
					}
			});
		}

		function setLED(module) {
			api.setLED({
				modules: [{
					ip: module.ip,
					port: module.port,
					device_id: module.device_id,
					module_id: module.module_id,
					led: module.led,
				}]
			}).then(function() {
				main(vm.sortIndex, vm.sortReverse);
			});
		}

		function getTable() {
			if (vm.sortIndex === undefined)
				return;
			vm.sortReverse = (1 / vm.sortIndex > 0);
			var item = vm.table[Math.abs(vm.sortIndex)];
			if (item.sortValue === undefined)
				return item.value;
			else
				return item.sortValue;
		}
	}
})();
