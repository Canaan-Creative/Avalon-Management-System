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
		.controller('DetailDevicesController', DetailDevicesController);

	DetailDevicesController.$inject = ['ShareService', 'APIService'];

	function DetailDevicesController(share, api) {
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
			value: function(data) {return data.device_id;}
		}, {
			name: 'Enabled',
			index: 1,
			value: function(data) {return data.enabled;}
		}, {
			name: 'Status',
			index: 2,
			value: function(data) {return data.status;}
		}, {
			name: 'Temp',
			index: 3,
			value: function(data) {return data.temperature;}
		}, {
			name: 'GHsav',
			index: 4,
			value: function(data) {return parseInt(data.mhs_av / 1000);}
		}, {
			name: 'GHs5s',
			index: 5,
			value: function(data) {return parseInt(data.mhs_5s / 1000);}
		}, {
			name: 'GHs1m',
			index: 6,
			value: function(data) {return parseInt(data.mhs_1m / 1000);}
		}, {
			name: 'GHs5m',
			index: 7,
			value: function(data) {return parseInt(data.mhs_5m / 1000);}
		}, {
			name: 'GHs15m',
			index: 8,
			value: function(data) {return parseInt(data.mhs_15m / 1000);}
		}, {
			name: 'LastValiddata',
			index: 9,
			value: function(data) {return data.last_valid_work;}
		}, {
			name: 'SmartSpeed',
			index: 10,
			value: function(data) {return data.smart_speed;}
		}];

		vm.getTable = getTable;

		vm.status.reloadListeners.push(main);
		main();

		function main(sortIndex, sortReverse) {
			var node = vm.status.node;
			var time = vm.status.time;
			vm.loaded = false;
			vm.sortIndex = sortIndex;
			vm.sortReverse = sortReverse || false;
			api.getStatus('device', time, node.ip, node.port).then(
				function() {
					if (node.ip === vm.status.node.ip &&
							node.port === vm.status.node.port)
						vm.loaded = true;
			});
		}

		function getTable() {
			if (vm.sortIndex === undefined)
				return;
			vm.sortReverse = (1 / vm.sortIndex > 0);
			return vm.table[Math.abs(vm.sortIndex)].value;
		}
	}
})();
