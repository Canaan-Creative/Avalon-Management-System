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
(function (){
	'use strict';

	angular
		.module('ams')
		.config(config);

	config.$inject = ['$stateProvider', '$urlRouterProvider'];

	function config($stateProvider, $urlRouterProvider) {
		$urlRouterProvider.otherwise('/home/overview');
		$stateProvider
			.state('home', {
				url: '/home',
				templateUrl: 'app/layout/home.html',
				controller: 'HomeController',
				controllerAs: 'vm',
			})
			.state('home.overview', {
				url: '/overview',
				views: {
					'@home': {
						templateUrl: 'app/pages/overview.html',
						controller: 'OverviewController',
						controllerAs: 'vm',
					},
					'farmmap@home.overview': {
						templateUrl: 'app/widgets/farmmap.html',
						controller: 'FarmMapController',
						controllerAs: 'vm',
					},
					'issues@home.overview': {
						templateUrl: 'app/widgets/issues.html',
						controller: 'IssuesController',
						controllerAs: 'vm',
					},
					'hashrate@home.overview': {
						templateUrl: 'app/widgets/hashrate.html',
						controller: 'HashrateController',
						controllerAs: 'vm',
					},
					'aliverate@home.overview': {
						templateUrl: 'app/widgets/aliverate.html',
						controller: 'AliverateController',
						controllerAs: 'vm',
					},
				}
			})
			.state('home.detail', {
				url: '/detail',
				params: {
					ip: null,
					port: null,
					dna: null,
				},
				views: {
					'@home': {
						templateUrl: 'app/pages/detail.html',
						controller: 'DetailController',
						controllerAs: 'vm',
					},
					'summary@home.detail': {
						templateUrl: 'app/widgets/detail_summary.html',
						controller: 'DetailSummaryController',
						controllerAs: 'vm',
					},
					'hashrate@home.detail': {
						templateUrl: 'app/widgets/detail_hashrate.html',
						controller: 'DetailHashrateController',
						controllerAs: 'vm',
					},
					'pools@home.detail': {
						templateUrl: 'app/widgets/detail_pools.html',
						controller: 'DetailPoolsController',
						controllerAs: 'vm',
					},
					'devices@home.detail': {
						templateUrl: 'app/widgets/detail_devices.html',
						controller: 'DetailDevicesController',
						controllerAs: 'vm',
					},
					'modules@home.detail': {
						templateUrl: 'app/widgets/detail_modules.html',
						controller: 'DetailModulesController',
						controllerAs: 'vm',
					},
					'config@home.detail': {
						templateUrl: 'app/widgets/detail_config.html',
						controller: 'DetailConfigController',
						controllerAs: 'vm',
					},
				}
			})
			.state('home.setting', {
				url: '/setting',
				templateUrl: 'app/pages/setting.html',
				controller: 'SettingController',
				controllerAs: 'vm',
			})
			.state('farmmap', {
				url: '/farmmap',
				templateUrl: 'app/widgets/farmmap.html',
				controller: 'FarmMapController',
				controllerAs: 'vm',
			})
			.state('issues', {
				url: '/issues',
				templateUrl: 'app/widgets/issues.html',
				controller: 'IssuesController',
				controllerAs: 'vm',
			});
	}
})();
