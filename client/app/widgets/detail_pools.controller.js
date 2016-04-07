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
		.controller('DetailPoolsController', DetailPoolsController);

	DetailPoolsController.$inject = ['$filter', 'ShareService', 'APIService'];

	function DetailPoolsController($filter, share, api) {
		/* jshint validthis: true */
		var vm = this;
		vm.status = share.status.detail;
		vm.data = api.data;

		vm.table = [{
			name: 'URL',
			value: function(data) {return data.url;}
		}, {
			name: 'User',
			value: function(data) {return data.user;}
		}, {
			name: 'Status',
			value: function(data) {
				if (data.stratum_active && data.status === 'Alive')
					return 'Active';
				else if (data.status === 'Alive')
					return 'Standby';
				else
					return 'Dead';
			}
		}, {
			name: 'W',
			tooltip: 'GetWorks',
			value: function(data) {return data.getworks;}
		}, {
			name: 'A',
			tooltip: 'Accepted',
			value: function(data) {return data.accepted;}
		}, {
			name: 'R',
			tooltip: 'Rejected',
			value: function(data) {return data.rejected;}
		}, {
			name: 'D',
			tooltip: 'Discarded',
			value: function(data) {return data.discarded;}
		}, {
			name: 'S',
			tooltip: 'Stale',
			value: function(data) {return data.stale;}
		}, {
			name: 'LST',
			value: function(data) {
				return $filter('date')(
					data.last_share_time * 1000,
					'yyyy-MM-dd HH:mm:ss'
				);
			}
		}, {
			name: 'LSD',
			value: function(data) {return data.last_share_difficulty;}
		}];

		vm.loaded = false;
		vm.status.reloadListeners.push(main);
		main();

		function main() {
			var time = vm.status.time;
			var node = vm.status.node;
			vm.loaded = false;
			api.getStatus('pool', time, node.ip, node.port).then(
				function() {
					if (node.ip === vm.status.node.ip &&
							node.port === vm.status.node.port)
						vm.loaded = true;
			});
		}
	}
})();
