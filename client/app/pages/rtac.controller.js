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

		vm.auth = share.status.auth;
		vm.status = share.status.rtac;
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

		vm.showDialog = share.utils.showDialog;

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

		function polling(session_id) {
			var session = vm.status[session_id];
			var promise = session.promise;
			promise.then(function(response) {
				if (response && response.data && response.data.auth === false)
					return;
				promise = api.rtaclog(session_id, vm.auth.token).then(
					function(response) {
						if (response.data.result !== 'timeout') {
							var ip = response.data.node.ip;
							var port = response.data.node.port;
							session.logs[ip + ":" + port] = response.data;
							session.len++;
						}
						if (session.len < session.targets.length) {
							session.promise = promise;
							polling(session_id);
						}
					});
			});
		}

		function commit(targets, commands) {
			var session_id = Date.now();
			var promise = api.rtac(targets, commands, session_id, vm.auth.token);
			vm.status[session_id] = {
				promise: promise,
				logs: {},
				commands: commands,
				targets: targets,
				len: 0,
			};
			polling(session_id);
			share.utils.showDialog('rtaclog', {session_id: session_id});
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
						commands.push({
							lib: 'uci',
							method: 'set',
							params: [
								'cgminer',
								'default',
								'pool' + (i + 1) + 'url',
								vm.actions.pool[i].address,
							],
						});
						commands.push({
							lib: 'uci',
							method: 'set',
							params: [
								'cgminer',
								'default',
								'pool' + (i + 1) + 'user',
								vm.actions.pool[i].worker,
							],
						});
						commands.push({
							lib: 'uci',
							method: 'set',
							params: [
								'cgminer',
								'default',
								'pool' + (i + 1) + 'pw',
								vm.actions.pool[i].password,
							],
						});
					}
					commands.push({lib: 'uci', method: 'commit', params: ['cgminer']});
				}
				if (vm.actions.apiSwitch) {
					commands.push({
						lib: 'uci',
						method: 'set',
						params: [
							'cgminer',
							'default',
							'api_allow',
							vm.actions.api,
						],
					});
					commands.push({lib: 'uci', method: 'commit', params: ['cgminer']});
				}
				if (vm.actions.ntpSwitch) {
					commands.push({
						lib: 'uci',
						method: 'set',
						params: [
							'cgminer',
							'default',
							'ntp_enable',
							vm.actions.ntp,
						],
					});
					commands.push({lib: 'uci', method: 'commit', params: ['cgminer']});
				}
				if (vm.actions.restartMiner)
					commands.push({
						lib: 'sys',
						method: 'exec',
						params: ['/etc/init.d/cgminer restart'],
					});
				break;
			case 'Basic':
				var raw = vm.actions.custom.split('\n');
				for (i = 0; i < raw.length; i++) {
					commands.push({lib: 'sys', method: 'exec', params: [raw[i]]});
				}
				break;
			}

			if (targets.length !== 0 && commands.length !== 0) {
				api.login(vm.auth.name, vm.auth.password).then(function(response) {
					if (response.data.auth === false)
						vm.auth.failed = true;
					else {
						vm.auth.failed = false;
						vm.auth.token = response.data.token;
						commit(targets, commands);
					}
				});
			}

			vm.targetLock = false;
		}
	}
})();
