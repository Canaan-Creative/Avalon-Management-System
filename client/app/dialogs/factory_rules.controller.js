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
		.controller('FactoryRulesController', FactoryRulesController);

	FactoryRulesController.$inject = ['ShareService', 'APIService', '$mdDialog'];

	function FactoryRulesController(share, api, $mdDialog) {
		/* jshint validthis: true */
		var vm = this;
		vm.data = api.data;
		vm.loaded = false;

		vm.close = close;
		vm.reload = reload;
		vm.setRules = setRules;
		vm.addRules = addRules;
		vm.deleteRules = deleteRules;

		init();

		function init() {
			api.getRules().then(function() {
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

		function deleteRules(rule, rule_set) {
			vm.data.rules[rule_set].splice(vm.data.rules[rule_set].indexOf(rule), 1);
		}

		function addRules(rule_set) {
			switch (rule_set) {
			case "code":
				vm.data.rules.code.push({
					header: '',
					name: '',
					model: '',
				});
				break;
			case "depend":
				vm.data.rules.depend.push({
					product_header: '',
					component_header: '',
					component_count: 1,
				});
				break;
			default:
				break;
			}
		}

		function setRules() {
			api.setRules();
		}

	}
})();
