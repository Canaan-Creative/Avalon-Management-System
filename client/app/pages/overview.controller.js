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

		share.status.main.title = "Overview";
		share.status.main.subTitle = false;

		vm.$sce = $sce;
		vm.hashrateChart = {};
		vm.hashrateChart.loaded = false;
		vm.hashrateChart.options = share.hashrateChartOptions;
		vm.aliverateChart = {};
		vm.aliverateChart.loaded = false;
		vm.aliverateChart.options = share.aliverateChartOptions;
		vm.summaryLoaded = false;
		vm.farmMap = {
			loaded: false,
			switch: 0, // 00 max intake, 01 max board, 10 average intake, 11 average board
			tempSwitch: 'Intake',
			mathSwitch: 'Max',
			viewSwitch: 'Node',
			maxDevice: 0,
			maxModule: 0,
			modWidth: 0,
			modHeight: 0,
			info: $sce.trustAsHtml("&nbsp;"),
		};
		vm.rearrangedMap = [];
		vm.issueLoaded = false;
		vm.data = api.data;

		vm.switchMap = switchMap;
		vm.gotoDetail = gotoDetail;
		vm.ecDecode = ecDecode;
		vm.numberShorten = numberShorten;

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

		function rainbow(x, xmin, xmax) {
			var r, g, b;
			if (!x) {
				return {
					color: 'red',
					"background-color": "#eeeeee",
				};
			}
			x = (x - xmin) / (xmax - xmin);
			if (x < 0) {
				r = 0;
				g = 0;
				b = 128;
			}else if (x < 0.125) {
				r = 0;
				g = 0;
				b = x / 0.125 * 128 + 128;
			}else if (x < 0.375) {
				r = 0;
				g = Math.floor((x - 0.125) / 0.25 * 256);
				b = 256;
			} else if (x < 0.625) {
				r = Math.floor((x - 0.375) / 0.25 * 256);
				g = 256;
				b = Math.floor(256 - (x - 0.375) / 0.25 * 256);
			} else if (x < 0.875) {
				r = 256;
				g = Math.floor(256 - (x - 0.625) / 0.25 * 256);
				b = 0;
			} else if (x <= 1) {
				r = Math.floor(256 - (x - 0.875) / 0.25 * 256);
				g = 0;
				b = 0;
			} else {
				r = 128;
				g = 0;
				b = 0;
			}
			if (r == 256) r = 255;
			if (g == 256) g = 255;
			if (b == 256) b = 255;
			return {
				color: '#' + (
					("0" + (255 - r).toString(16)).substr(-2) +
					("0" + (255 - g).toString(16)).substr(-2) +
					("0" + (255 - b).toString(16)).substr(-2)
				),
				"background-color": '#' + (
					("0" + r.toString(16)).substr(-2) +
					("0" + g.toString(16)).substr(-2) +
					("0" + b.toString(16)).substr(-2)
				),
			};
		}

		function updateSubTitle() {

			var shortlog = api.data.shortlog;
			share.status.main.subTitle = [
				'Time: ' + d3.time.format('%Y.%m.%d %H:%M')(new Date(shortlog.time * 1000)),
				'Hashrate: ' + vm.numberShorten(shortlog.hashrate),
				'Nodes: ' + shortlog.node_num,
				'Modules: ' + shortlog.module_num
			];
		}

		function splitFarmMap(size) {
			var farmMap = vm.data.farmMap;
			var splitted = [];
			var j = 0;
			for (var i = 0; i < farmMap.length; i++, j++) {
				j %= size;
				if (j === 0)
					splitted.push([]);
				var node = farmMap[i];
				var style = [
					rainbow(node.max_tempI, 25, 45), rainbow(node.max_tempB, 65, 75),
					rainbow(node.avg_tempI, 25, 45), rainbow(node.avg_tempB, 65, 75),
				];
				var modules = [];
				var deviceNum = 0;
				for (var k = 0; k < node.modules.length; k++) {
					var did;
					var mod = node.modules[k];
					mod.style = [
						rainbow(mod.temp, 25, 45),
						rainbow(Math.max(mod.temp0, mod.temp1), 65, 75),
						rainbow(mod.temp, 25, 45),
						rainbow((mod.temp0 + mod.temp1) / 2, 65, 75),
					];
					did = mod.id.split(':')[0];
					if (modules[did] === undefined) {
						deviceNum++;
						modules[did] = [];
					}
					modules[did].push(mod);
				}
				if (deviceNum > vm.farmMap.maxDevice)
					vm.farmMap.maxDevice = deviceNum;
				for (k = 0; k < modules.length; k++)
					if (modules[k] !== undefined)
						if (modules[k].length > vm.farmMap.maxModule)
							vm.farmMap.maxModule = modules[k].length;
				splitted[parseInt(i / size)].push({
					node: node,
					modules: modules,
					style: style,
					index: i,
				});
			}
			vm.farmMap.modWidth = Math.floor(72 / vm.farmMap.maxModule);
			vm.farmMap.modHeight = Math.floor(72 / vm.farmMap.maxDevice);
			return splitted;
		}

		function switchMap(bit) {
			vm.farmMap.switch ^= (1 << bit);
		}

		function getChart() {
			api.getShortlog().then(updateSubTitle);

			api.getFarmMap(share.status.main.time).then(
				function() {
					if ($mdMedia('gt-lg'))
						vm.rearrangedMap = splitFarmMap(10);
					else
						vm.rearrangedMap = splitFarmMap(8);
					vm.farmMap.loaded = true;
			});

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
				$state.go('home.detail', {
					ip: ip,
					port: port,
					dna: dna,
				});
			else
				$state.go('home.detail', {
					ip: ip,
					port: port,
				});
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

		function numberShorten(num) {
			var prefix = [
				{prefix: 'EHs', base: 1000000000000},
				{prefix: 'PHs', base: 1000000000},
				{prefix: 'THs', base: 1000000},
				{prefix: 'GHs', base: 1000},
				{prefix: 'MHs', base: 1}
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
	}
})();
