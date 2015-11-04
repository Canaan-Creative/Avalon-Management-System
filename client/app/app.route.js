(function (){
	'use strict';

	angular
		.module('ams')
		.config(config);

	config.$inject = ['$routeProvider'];

	function config($routeProvider) {
		$routeProvider
			.when('/overview', {
				templateUrl: "app/pages/overview.html",
				controller: 'OverviewController',
				controllerAs: 'vm',
			})
			.when('/detail', {
				templateUrl: "app/pages/detail.html",
				controller: 'DetailController',
				controllerAs: 'vm',
			})
			.when('/setting', {
				templateUrl: "app/pages/setting.html",
				controller: 'SettingController',
				controllerAs: 'vm',
			})
			.otherwise({redirectTo: '/overview'});
	}
})();
