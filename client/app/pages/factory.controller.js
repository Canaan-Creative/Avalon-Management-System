/*
 Copyright (C) 2016  DING Changchang (of Canaan Creative)

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
		.controller('FactoryController', FactoryController);

	FactoryController.$inject = ['$filter', 'ShareService', 'APIService'];

	function FactoryController($filter, share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.search = "";
		vm.searchDone = true;
		vm.auth = share.status.auth;
		vm.status = share.status.factory;
		vm.data = api.data;

		vm.table = [{
			name: 'Time',
			value: function(data) {
				return $filter('date')(data.time, 'yyyy-MM-dd HH:mm');}
		}, {
			name: 'Order ID',
			value: function(data) {return data.id;}
		}, {
			name: 'SN',
			value: function(data) {
				return data.model + ("0000000" + data.uid.toString(16)).substr(-8);}
		}];

		share.status.main.title = "Factory";
		share.status.main.subTitle = false;

		vm.showDialog = share.utils.showDialog;

		vm.newOrder = newOrder;
		vm.openOrder = openOrder;
		vm.searchOrder = searchOrder;
		vm.setting = setting;

		api.getOrder().then(function () {
			vm.loaded = true;
		});

		function newOrder() {
			vm.showDialog('order');
		}

		function openOrder(order) {
			vm.showDialog('order', {order: order});
		}

		function searchOrder(sn) {
			if (sn === "")
				return;
			vm.searchDone = false;
			api.searchOrder(sn).then(function () {
				vm.search = "";
				vm.searchDone = true;
			});
		}

		function setting() {
			vm.showDialog('factory_rules');
		}
	}
})();
