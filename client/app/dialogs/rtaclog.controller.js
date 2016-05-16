/*
 Copyright (C) 2016  DING Changchang (of Canaan Creative)

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
		.controller('RTACLogController', RTACLogController);

	RTACLogController.$inject = ['ShareService', 'APIService', '$mdDialog', '$sce'];

	function RTACLogController(share, api, $mdDialog, $sce) {
		/* jshint validthis: true */
		var vm = this;

		vm.data = share.status.rtac[vm.session_id];
		vm.show = null;

		vm.focus = focus;
		vm.close = close;
		vm.convert = convert;

		function focus(node) {
			vm.show = node;
		}

		function convert(text) {
			if (text === undefined)
				text = '';
			return $sce.trustAsHtml(String(text).replace("\n", "<br />"));
		}

		function close() {
			$mdDialog.hide();
		}

	}
})();
