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
		.controller('OverviewController', OverviewController);

	OverviewController.$inject = ['$mdMedia', '$state', '$sce', 'ShareService', 'APIService'];

	function OverviewController($mdMedia, $state, $sce, share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.status = share.status.overview;
		vm.utils = share.utils;

		share.status.main.title = "Overview";
		share.status.main.subTitle = false;

		vm.hashrateChart = {};
		vm.hashrateChart.loaded = false;
		vm.hashrateChart.options = share.hashrateChartOptions;
		vm.aliverateChart = {};
		vm.aliverateChart.loaded = false;
		vm.aliverateChart.options = share.aliverateChartOptions;
		vm.data = api.data;

		share.status.main.timePromise = share.status.main.timePromise.then(getChart);

		function updateSubTitle() {
			var shortlog = api.data.shortlog;
			share.status.main.subTitle = [
				'Time: ' + d3.time.format('%Y.%m.%d %H:%M')(new Date(shortlog.time * 1000)),
				'Hashrate: ' + vm.utils.numberShorten(shortlog.hashrate),
				'Nodes: ' + shortlog.node_num,
				'Modules: ' + shortlog.module_num
			];
		}

		function getChart() {
			api.getShortlog().then(updateSubTitle);

			api.getFarmHashrate(
				share.status.main.time - 30 * 24 * 3600,
				share.status.main.time
			).then(
				function() {
					vm.hashrateChart.loaded = true;
			});

			api.getIssue(share.status.main.time).then(
				function() {
					vm.issueLoaded = true;
			});

			api.getAliverate(
				share.status.main.time - 30 * 24 * 3600,
				share.status.main.time
			).then(
				function() {
					vm.aliverateChart.loaded = true;
			});
		}
	}
})();
