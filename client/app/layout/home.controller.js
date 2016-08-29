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
		.controller('HomeController', HomeController);

	HomeController.$inject = ['$mdSidenav', '$mdMedia', '$state', 'ShareService'];

	function HomeController($mdSidenav, $mdMedia, $state, share) {
		/* jshint validthis: true */
		var vm = this;

		vm.menu = [
			{
				link: 'home.overview',
				name: 'Overview',
				icon: 'home',
			}, {
				link: 'home.statistics',
				name: 'Statistics',
				icon: 'equalizer',
			}, {
				link: 'home.detail',
				name: 'Detail',
				icon: 'view_list',
			}, {
				link: 'home.setting',
				name: 'Setting',
				icon: 'settings',
			}, {
				link: 'home.rtac',
				name: 'RTAC',
				icon: 'build',
			}, {
				link: 'home.factory',
				name: 'factory',
				icon: 'airport_shuttle',
			}
		];
		vm.status = share.status.main;
		vm.auth = share.status.auth;
		vm.version = share.status.version;
		vm.toggleSidenav = toggleSidnav;
		vm.select = select;
		vm.chooseSnap = chooseSnap;
		vm.logout = logout;
		vm.login = login;

		function toggleSidnav() {
			$mdSidenav('left').toggle();
		}

		function select(menuItem) {
			if (vm.status.title !== menuItem.name) {
				vm.status.title = menuItem.name;
				vm.status.subTitle = false;
			}
			if (!$mdMedia('gt-lg'))
				$mdSidenav('left').toggle();
			$state.go(menuItem.link);
		}

		function chooseSnap() {
			share.utils.showDialog('snapshot');
		}

		function logout() {
			vm.auth.success = false;
			vm.auth.name = '';
			vm.auth.token = '';
		}

		function login() {
			share.utils.showDialog('login');
		}
	}
})();
