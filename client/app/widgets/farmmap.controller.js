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
		.controller('FarmMapController', FarmMapController);

	FarmMapController.$inject = ['$mdMedia', '$sce', 'ShareService', 'APIService'];

	function FarmMapController($mdMedia, $sce, share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.status = share.status.farmMap;
		// vm.status.loaded: *Bool*
		// vm.status.switch: 0, 1, 2, 3
		// vm.status.tempSwitch: 'Intake' / 'Board'
		// vm.status.mathSwitch: 'Max' / 'Avg'
		// vm.status.viewSwitch: 'Node' / 'Mod'
		// vm.status.data: formatted farm map data
		// vm.status.maxDevice
		// vm.status.maxModule
		// vm.status.modWidth
		// vm.status.modHeight
		vm.main = share.status.main;
		// vm.overview.footer

		vm.utils = share.utils;
		// vm.utils.gotoDetail(ip, port, dna)
		// vm.utils.numberShorten(number)

		vm.data = api.data;
		// vm.data.farmMap

		vm.$sce = $sce;

		vm.switchMap = switchMap;


		share.status.main.timePromise.then(main);

		function main() {
			if (!vm.status.loaded)
				api.getFarmMap(share.status.main.time).then(
					function() {
						if ($mdMedia('gt-lg'))
							vm.status.data = formatMap(10);
						else
							vm.status.data = formatMap(8);
						vm.status.loaded = true;
				});
		}

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

		function formatMap(size) {
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
				if (deviceNum > vm.status.maxDevice)
					vm.status.maxDevice = deviceNum;
				for (k = 0; k < modules.length; k++)
					if (modules[k] !== undefined)
						if (modules[k].length > vm.status.maxModule)
							vm.status.maxModule = modules[k].length;
				splitted[parseInt(i / size)].push({
					node: node,
					modules: modules,
					style: style,
					index: i,
				});
			}
			vm.status.modWidth = Math.floor(72 / vm.status.maxModule);
			vm.status.modHeight = Math.floor(72 / vm.status.maxDevice);
			return splitted;
		}

		function switchMap(bit) {
			vm.status.switch ^= (1 << bit);
		}
	}
})();
