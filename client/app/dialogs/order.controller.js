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
		.controller('OrderController', OrderController);

	OrderController.$inject = ['ShareService', 'APIService', '$mdDialog'];

	function OrderController(share, api, $mdDialog) {
		/* jshint validthis: true */
		var vm = this;

		if (vm.order) {
			vm.old = true;
			api.getBOMs(vm.order.uid).then(cloneBOMs);
		} else {
			vm.old = false;
			vm.order = {
				time: new Date(),
				id: '',
				doc_id: '',
				quantity: 0,
				batch: '',
				serial: '',
				model: '',
				boms: [{
					id: 0,
					name: '',
					model: '',
					sn: '',
					time: new Date()
				}]
			};
		}

		vm.close = close;
		vm.addBOM = addBOM;
		vm.deleteBOM = deleteBOM;
		vm.print = print;

		function close() {
			$mdDialog.hide();
		}

		function cloneBOMs() {
			var boms = [];
			for (var i = 0; i < api.data.boms.length; i++) {
				boms.push({
					id: api.data.boms[i].id,
					name: api.data.boms[i].name,
					model: api.data.boms[i].model,
					sn: api.data.boms[i].sn,
					time: api.data.boms[i].time,
				});
			}
			vm.order.boms = boms;
		}

		function deleteBOM(b) {
			vm.order.boms.splice(vm.order.boms.indexOf(b), 1);
			for (var i = 0; i < vm.order.boms.length; i++)
				vm.order.boms[i].id = i + 1;
		}

		function addBOM() {
			vm.order.boms.push({
				id: vm.order.boms.length + 1,
				name: '',
				model: '',
				sn: '',
				time: new Date()
			});
		}

		function print() {
			
		}
	}
})();
