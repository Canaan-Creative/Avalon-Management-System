(function() {
	'use strict';

	angular
		.module('ams')
		.controller('MainController', MainController);

	MainController.$inject = ['$mdSidenav', '$mdDialog', '$location', 'ShareService'];

	function MainController($mdSidenav, $mdDialog, $location, share) {
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

		var smallDevice = false;


		function toggleSidnav() {
			$mdSidenav('left').toggle();
			smallDevice = true;
		}
		function select(menuItem) {
			vm.status.title = menuItem.name;
			vm.status.subTitle = false;
			if (smallDevice)
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
