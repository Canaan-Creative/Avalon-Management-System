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

		vm.hashrateChart = {};
		vm.hashrateChart.loaded = false;
		vm.hashrateChart.options = share.hashrateChartOptions;
		vm.data = api.data;

		if (share.status.main.time === 0)
			share.getLastTime().then(getFarmHashrate);
		else
			getFarmHashrate();

		function getFarmHashrate() {
			api.getFarmHashrate(
				share.status.main.time - 30 * 24 * 3600,
				share.status.main.time
			).then(
				function() {
					vm.hashrateChart.loaded = true;
			});
		}

	}
})();
