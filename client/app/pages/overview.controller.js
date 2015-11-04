(function() {
	'use strict';

	angular
		.module('ams')
		.controller('OverviewController', OverviewController);

	OverviewController.$inject = ['ShareService', 'APIService'];

	function OverviewController(share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.status = share.status.overview;

		share.status.main.title = "Overview";
		share.status.main.subTitle = false;
	}
})();
