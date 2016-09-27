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
		vm.auto = false;
		vm.data = api.data;
		vm.product = {};
		vm.loaded = false;
		vm.eid = undefined;

		vm.parseDate = parseDate;
		vm.close = close;
		vm.reload = reload;
		vm.updateOrder = updateOrder;
		vm.addComponent = addComponent;
		vm.deleteComponent = deleteComponent;
		vm.buildDep = buildDep;
		vm.switchMode = switchMode;

		var buffer = "";
		var missed_id = 1;

		init();

		function init() {
			api.getOrder().then(api.getRules).then(function() {
				vm.buildDep();
				vm.loaded = true;
			});
		}

		function reload() {
			vm.loaded = false;
			init();
		}

		function close() {
			if (vm.eid !== undefined)
				share.event.keydown.removeListener(vm.eid);
			$mdDialog.hide();
		}

		function parseDate(dateString) {
			var d = new Date(dateString);
			var result = d.toTimeString().slice(0, 8);
			return result;
		}

		function deleteComponent(component) {
			vm.data.order.components.splice(vm.data.order.components.indexOf(component), 1);
		}

		function addComponent() {
			vm.data.order.components.push({
				cid: vm.data.order.components.length + 1,
				name: '',
				model: '',
				note: '',
				component_sn: '',
				time: vm.product.time || new Date(),
			});
		}

		function freeze() {
			vm.reload();
		}

		function updateOrder() {
			vm.loaded = false;
			vm.product.order_id = vm.data.order.order_id;
			vm.product.batch = vm.data.order.batch;
			vm.product.note = vm.data.order.note;
			Array.prototype.push.apply(
				vm.product.components, vm.data.order.components
			);
			for (var i = 0; i < vm.product.components.length; i++)
				vm.product.components[i].product_sn =
					vm.product.product_sn;
			api.setOrder().then(function() {
				api.addProduct(vm.product).then(freeze);
			});
		}

		function buildDep() {
			var time = new Date();
			for (var j = 0; j < vm.data.rules.code.length; j++)
				if (vm.data.order.product_header ===
						vm.data.rules.code[j].header) {
					vm.product = {
						header: vm.data.rules.code[j].header,
						name: vm.data.rules.code[j].name,
						model: vm.data.rules.code[j].model,
						product_sn: null,
						time: time,
						components: [],
					};
					missed_id = 1;
				}
			for (var i = 0; i < vm.data.rules.depend.length; i++)
				if (vm.data.rules.depend[i].product_header ===
						vm.data.order.product_header)
					for (j = 0; j < vm.data.rules.code.length; j++)
						if (vm.data.rules.depend[i].component_header ===
								vm.data.rules.code[j].header)
							for (var k = 0; k < vm.data.rules.depend[i].component_count; k++) {
								vm.product.components.push({
									component_id: k,
									header: vm.data.rules.code[j].header,
									name: vm.data.rules.code[j].name,
									model: vm.data.rules.code[j].model,
									note: '',
									component_sn: null,
									time: time,
								});
								missed_id++;
							}
		}

		function switchMode() {
			if (vm.auto) {
				vm.freeze = true;
				vm.eid = share.event.keydown.addListener(readBarcode);
			} else {
				vm.freeze = false;
				share.event.keydown.removeListener(vm.eid);
			}
		}

		function readBarcode(e) {
			var key = e.key;
			console.log(e);
			switch (key) {
				case 'Enter':
				case 'Tab':
				case 'Alt':
					var code = buffer;
					buffer = "";
					checkBarcode(code);
					break;
				case 'Shift':
					break;
				default:
					buffer += key;
					break;
			}
		}

		function checkBarcode(code) {
			console.log(code);
			if (code.indexOf(vm.product.header) === 0) {
				if (vm.product.product_sn === null)
					missed_id--;
				vm.product.product_sn = code;
			} else
				for (var i = 0; i < vm.product.components.length; i++) {
					var component = vm.product.components[i];
					if (component.component_sn === code)
						return;
					if (component.component_sn === null && code.indexOf(component.header) === 0) {
						missed_id--;
						component.component_sn = code;
						break;
					}
				}
			if (missed_id === 0)
				vm.updateOrder();
		}
	}
})();
