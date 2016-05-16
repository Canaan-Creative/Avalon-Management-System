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
		.controller('LoginController', LoginController);

	LoginController.$inject = ['ShareService', 'APIService', '$mdDialog'];

	function LoginController(share, api, $mdDialog) {
		/* jshint validthis: true */
		var vm = this;
		vm.failed = false;
		vm.username = '';
		vm.password = '';
		vm.status = share.status.auth;

		vm.login = login;
		vm.close = close;

		function login() {
			api.login(vm.username, vm.password).then(function(response) {
				if (response.data.auth === false)
					vm.failed = true;
				else {
					vm.failed = false;
					vm.status.success = true;
					vm.status.name = vm.username;
					vm.status.password = vm.password;
					vm.status.token = response.data.token;
					vm.close();
				}
			});
		}

		function close() {
			$mdDialog.hide();
		}
	}
})();
