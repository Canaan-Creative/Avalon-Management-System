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
		vm.hashrateChart.options = {
			chart: {
				type: 'lineChart',
				height: 400,
				margin : {
					top: 20,
					right: 20,
					bottom: 40,
					left: 54
				},
				x: function(d) {return d.x;},
				y: function(d) {return d.y;},
				useInteractiveGuideline: true,
				dispatch: {
					stateChange: function(e) {},
					changeState: function(e) {},
					tooltipShow: function(e) {},
					tooltipHide: function(e) {},
				},
				xAxis: {
					axisLabel: 'Time',
					showMaxMin: false,
					tickFormat: function(d) {
						return d3.time.format('%m.%d %H:%M')(new Date(d * 1000));
					},
				},
				yAxis: {
					axisLabel: 'Hashrate (Hash/s)',
					showMaxMin: false,
					tickFormat: numberShorten,
					axisLabelDistance: -10,
				},
				callback: function(chart) {},
				forceY: [0],
				xScale: d3.time.scale().nice(),
			},
			title: {
				enable: true,
				text: 'Hashrate'
			},
		};

		vm.data = api.data;

		api.getHashrate().then(
			function() {
				vm.hashrateChart.loaded = true;
		});

		function numberShorten(num) {
			var prefix = [
				{prefix: 'E', base: 100000000000000000},
				{prefix: 'P', base: 100000000000000},
				{prefix: 'T', base: 100000000000},
				{prefix: 'G', base: 100000000},
				{prefix: 'M', base: 100000},
				{prefix: 'k', base: 100},
			];
			for (var i = 0; i < prefix.length; i++) {
				var p = prefix[i];
				if (num >= p.base) {
					if (num >= p.base * 10) {
						return (num / p.base / 10).toFixed(0) + ' ' + p.prefix;
					}
					else {
						return (num / p.base / 10).toFixed(1) + ' ' + p.prefix;
					}
				}
			}
			return num;
		}
	}
})();
