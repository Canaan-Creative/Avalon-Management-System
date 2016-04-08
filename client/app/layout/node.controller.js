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
		.controller('NodeController', NodeController);

	NodeController.$inject = ['$stateParams', 'ShareService'];

	function NodeController($stateParams, share) {
		/* jshint validthis: true */
		var vm = this;

		console.log("node");
		vm.status = share.status.detail;

		if (share.status.main.latest)
			vm.status.time = 'latest';
		else
			vm.status.time = share.status.main.time;

		var params = $stateParams;
		if (params.ip && params.port) {
			vm.status.node = {
				ip: params.ip,
				port: params.port,
			};
			if (params.dna)
				vm.status.highlightDNA = params.dna;
		}

	}
})();
