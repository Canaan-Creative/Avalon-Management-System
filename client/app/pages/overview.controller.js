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

	OverviewController.$inject = ['$location', 'ShareService', 'APIService'];

	function OverviewController($location, share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.status = share.status.overview;

		share.status.main.title = "Overview";
		share.status.main.subTitle = false;

		vm.hashrateChart = {};
		vm.hashrateChart.loaded = false;
		vm.hashrateChart.options = share.hashrateChartOptions;
		vm.aliverateChart = {};
		vm.aliverateChart.loaded = false;
		vm.aliverateChart.options = share.aliverateChartOptions;
		vm.summaryLoaded = false;
		vm.issueLoaded = false;
		vm.data = api.data;
		vm.gotoDetail = gotoDetail;
		vm.ecDecode = ecDecode;

		vm.summaryTable = [{
			name: 'Node',
			value: function(data) {return data.ip + ':' + data.port;},
		}, {
			name: 'Modules',
			value: function(data) {return data.module;},
		}, {
			name: 'Temperature',
			value: function(data) {
				return parseFloat(data.temp).toFixed(1) +
					' / ' + parseFloat(data.temp0).toFixed(1) +
					' / ' + parseFloat(data.temp1).toFixed(1);
			},
		}];

		if (share.status.main.time === 0)
			share.getLastTime().then(getChart);
		else
			getChart();

		function updateSubTitle() {
			function numberShorten(num) {
				var prefix = [
					{prefix: 'EHs', base: 1000000000000000000},
					{prefix: 'PHs', base: 1000000000000000},
					{prefix: 'THs', base: 1000000000000},
					{prefix: 'GHs', base: 1000000000},
					{prefix: 'MHs', base: 1000000},
					{prefix: 'kHs', base: 1000},
				];
				for (var i = 0; i < prefix.length; i++) {
					var p = prefix[i];
					if (num >= p.base) {
						if (num >= p.base * 100)
							return (num / p.base).toFixed(1) + ' ' + p.prefix;
						else if (num >= p.base * 10)
							return (num / p.base).toFixed(2) + ' ' + p.prefix;
						else
							return (num / p.base).toFixed(3) + ' ' + p.prefix;
					}
				}
				return num;
			}

			var shortlog = api.data.shortlog;
			share.status.main.subTitle = [
				'Time: ' + d3.time.format('%Y.%m.%d %H:%M')(new Date(shortlog.time * 1000)),
				'Hashrate: ' + numberShorten(shortlog.hashrate),
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

			api.getSummary(share.status.main.time).then(
				function() {
					vm.summaryLoaded = true;
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

		function gotoDetail(ip, port, dna) {
			if (dna)
				$location.path('/detail')
					.search('ip', ip)
					.search('port', port)
					.search('dna', dna);
			else
				$location.path('/detail')
					.search('ip', ip)
					.search('port', port);
		}

		function ecDecode(ec) {
			var errcode = [
				null, 'TOOHOT', 'LOOP0FAILED', 'LOOP1FAILED',
				'INVALIDMCU', null, null, null,
				null, 'NOFAN', 'PG0FAILED', 'PG1FAILED',
				'CORETESTFAILED', 'ADC0_ERR', 'ADC1_ERR', 'VOLTAGE_ERR'
			];
			var msg = '';
			for (var i = 0; i < errcode.length; i++)
				if (((ec >> i) & 1) && (errcode[i]))
					msg += errcode[i] + ' ';
			return msg;
		}
	}
})();
