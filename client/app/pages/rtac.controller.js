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
		.controller('RTACController', RTACController);

	RTACController.$inject = ['ShareService', 'APIService'];

	function RTACController(share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.status = share.status.setting;
		vm.data = api.data;

		share.status.main.title = "RTAC";
		share.status.main.subTitle = false;

		vm.level = 'Advance';
		vm.actions = {
			poolSwitch: false,
			pool: [
				{address: '', worker: '', password: ''},
				{address: '', worker: '', password: ''},
				{address: '', worker: '', password: ''},
			],
			apiSwitch: false,
			api: '',
			custom: '',
			ntpSwitch: false,
			ntp: '',
			restartMiner: false,
		};
		vm.targetLock = false;

		vm.selectAll = selectAll;
		vm.selectInvert = selectInvert;
		vm.switchLevel = switchLevel;
		vm.run = run;

		api.getNodes();


		function selectAll() {
			for (var i = 0; i < vm.data.nodes.length; i++)
				vm.data.nodes[i].selected = true;
		}

		function selectInvert() {
			for (var i = 0; i < vm.data.nodes.length; i++)
				vm.data.nodes[i].selected = ! vm.data.nodes[i].selected;
		}

		function switchLevel() {
			if (vm.level === 'Advance')
				vm.level = 'Basic';
			else
				vm.level = 'Advance';
		}

		function run() {
			vm.targetLock = true;

			var i;
			var targets = [];
			for (i = 0; i < vm.data.nodes.length; i++)
				if (vm.data.nodes[i].selected)
					targets.push(vm.data.nodes[i]);

			var commands = [];
			switch (vm.level) {
			case 'Advance':
				if (vm.actions.poolSwitch) {
					for (i = 0; i < 3; i++) {
						commands.push('uci set cgminer.default.pool' + (i + 1) + 'url=' + vm.actions.pool[i].address);
						commands.push('uci set cgminer.default.pool' + (i + 1) + 'user=' + vm.actions.pool[i].worker);
						commands.push('uci set cgminer.default.pool' + (i + 1) + 'pw=' + vm.actions.pool[i].password);
					}
					commands.push('uci commit');
				}
				if (vm.actions.apiSwitch) {
					commands.push('uci set cgminer.default.api_allow=' + vm.actions.api);
					commands.push('uci commit');
				}
				if (vm.actions.ntpSwitch) {
					commands.push('uci set cgminer.default.ntp=' + vm.actions.ntp);
					commands.push('uci commit');
				}
				if (vm.actions.restartMiner)
					commands.push('/etc/init.d/cgminer restart');
				break;
			case 'Basic':
				commands = vm.actions.custom.split('\n');
				break;
			}

			if (targets.length !== 0 && commands.length !== 0)
				api.rtac(targets, commands);

			vm.targetLock = false;
		}
	}
})();
