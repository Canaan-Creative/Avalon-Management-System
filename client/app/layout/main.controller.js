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
		.controller('MainController', MainController);

	MainController.$inject = ['$mdSidenav', '$mdDialog', '$mdMedia', '$location', 'ShareService'];

	function MainController($mdSidenav, $mdDialog, $mdMedia, $location, share) {
		/* jshint validthis: true */
		var vm = this;

		vm.menu = [
			{
				link: '/overview',
				name: 'Overview',
				icon: 'home',
			}, {
				link: '/detail',
				name: 'Detail',
				icon: 'view_list',
			}, {
				link: '/setting',
				name: 'Setting',
				icon: 'settings',
			}
		];
		vm.status = share.status.main;
		vm.toggleSidenav = toggleSidnav;
		vm.select = select;
		vm.chooseSnap = chooseSnap;

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
			$location.path(menuItem.link);
		}
		function chooseSnap() {
			$mdDialog.show({
				parent: angular.element(document.body),
				templateUrl: 'app/layout/snapshot.html',
				controller: 'SnapshotController',
				controllerAs: 'ctrl',
			});
		}
	}
})();
