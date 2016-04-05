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
		.controller('IssuesController', IssuesController);

	IssuesController.$inject = ['ShareService', 'APIService'];

	function IssuesController(share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.status = share.status.issues;
		// vm.status.loaded: *Bool*

		vm.utils = share.utils;
		// vm.utils.gotoDetail(ip, port, dna)
		// vm.utils.ecDecode(ec)

		vm.data = api.data;
		// vm.data.issues

		share.status.main.timePromise = share.status.main.timePromise.then(main);

		function main() {
			if (!vm.status.loaded)
				api.getIssue(share.status.main.time).then(
					function() {
						vm.status.loaded = true;
				});
		}
	}
})();
