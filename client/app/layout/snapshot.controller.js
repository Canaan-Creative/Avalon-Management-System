(function() {
	'use strict';

	angular
		.module('ams')
		.controller('SnapshotController', SnapshotController);

	SnapshotController.$inject = ['ShareService', 'APIService'];

	function SnapshotController(share, api) {
		/* jshint validthis: true */
		var vm = this;
	}
})();
