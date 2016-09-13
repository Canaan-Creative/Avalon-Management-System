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
		vm.auto = "OFF";
		vm.data = api.data;
		vm.product = {};
		vm.loaded = false;

		vm.close = close;
		vm.reload = reload;
		vm.setOrder = setOrder;
		vm.addComponent = addComponent;
		vm.deleteComponent = deleteComponent;
		vm.buildDep = buildDep;

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
			$mdDialog.hide();
		}

		function deleteComponent(component) {
			vm.data.order.components.splice(vm.data.order.components.indexOf(component), 1);
		}

		function addComponent() {
			vm.data.order.components.push({
				name: '',
				model: '',
				component_id: '',
				time: vm.product.time || new Date(),
			});
		}

		function setOrder() {
			product.order_id = vm.data.order.order_id;
			Array.prototype.push.apply(
				vm.product.components, vm.data.order.components
			);
			for (var i = 0; i < vm.product.components.length; i++)
				vm.product.components[i].product_id =
				vm.product.product_id;
			api.setOrder.then(function() {
				api.addProduct(vm.product);
			});
		}

		function buildDep() {
			var time = new Date();
			for (var j = 0; j < vm.data.rules.code.length; j++)
				if (vm.data.order.product_header ===
						vm.data.rules.code[j].header)
					vm.product = {
						header: vm.data.rules.code[j].header,
						name: vm.data.rules.code[j].name,
						model: vm.data.rules.code[j].model,
						product_id: '',
						time: time,
						components: [],
					};
			for (var i = 0; i < vm.data.rules.depend.length; i++)
				if (vm.data.rules.depend[i].product_header ===
						vm.data.order.product_header)
					for (j = 0; j < vm.data.rules.code.length; j++)
						if (vm.data.rules.depend[i].component_header ===
							vm.data.rules.code[j].header)
						vm.product.components.push({
							header: vm.data.rules.code[j].header,
							name: vm.data.rules.code[j].name,
							model: vm.data.rules.code[j].model,
							component_id: '',
							time: time,
						});
		}
	}
})();
