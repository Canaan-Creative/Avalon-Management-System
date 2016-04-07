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
		.controller('DetailHashrateController', DetailHashrateController);

	DetailHashrateController.$inject = ['ShareService', 'APIService'];

	function DetailHashrateController(share, api) {
		/* jshint validthis: true */
		var vm = this;
		vm.status = share.status.detail;
		vm.hashrate = share.status.hashrate;
		vm.data = api.data;

		vm.loaded = false;
		vm.status.reloadListeners.push(main);
		main();

		function main() {
			vm.loaded = false;
			share.status.main.timePromise.then(getNodeHashrate);
		}

		function getNodeHashrate() {
			api.getNodeHashrate(
				vm.status.node.ip,
				vm.status.node.port,
				share.status.main.time - 30 * 24 * 3600,
				share.status.main.time
			).then(
				function() {
					vm.loaded = true;
			});
		}
	}
})();
