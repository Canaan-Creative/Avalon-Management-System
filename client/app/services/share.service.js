(function() {
	'use strict';

	angular
		.module('ams')
		.service('ShareService', ShareService);

	ShareService.$inject = ['$http'];

	function ShareService($http) {
		/* jshint validthis: true */
		var self = this;

		self.status = {
			main: {
				title: "Overview",
				subTitle: false,
				time: 0,
				latest: true,
			},
			detail: {
				node: false,
				tabLoaded: false,
				poolCardLoaded: false,
				tabName: "summary",
			},
		};
		self.getLastTime = getLastTime;
		self.aliverateChartOptions = {
			chart: {
				type: 'multiChart',
				height: 350,
				margin : {
					top: 20,
					right: 54,
					bottom: 40,
					left: 54
				},
				line1: {
					x: function(d) {return d.x * 1000;},
					y: function(d) {return d.y;},
				},
				line2: {
					x: function(d) {return d.x * 1000;},
					y: function(d) {return d.y;},
				},
				useInteractiveGuideline: true,
				interactiveLayer: {
					tooltip: {
						headerFormatter: function(d) {
							return d3.time.format('%Y.%m.%d %H:%M')(new Date(d * 1000));
						},
					},
				},
				dispatch: {
					stateChange: function(e) {},
					changeState: function(e) {},
					tooltipShow: function(e) {},
					tooltipHide: function(e) {},
				},
				xAxis: {
					axisLabel: 'Time',
					showMaxMin: false,
					ticks: function(start, stop) {
						return d3.time.days(start, stop, 7);
					},
					tickFormat: function(d) {
						return d3.time.format('%m.%d')(new Date(d * 1000));
					},
				},
				yAxis1: {
					axisLabel: 'Nodes',
					showMaxMin: false,
					axisLabelDistance: -10,
				},
				yAxis2: {
					axisLabel: 'Modules',
					showMaxMin: false,
					axisLabelDistance: -10,
				},
				callback: function(chart) {},
				forceY: [0],
				xScale: d3.time.scale(),
			},
			title: {
				enable: false,
			},
		};

		self.hashrateChartOptions = {
			chart: {
				type: 'lineChart',
				height: 350,
				margin : {
					top: 20,
					right: 20,
					bottom: 40,
					left: 54
				},
				x: function(d) {return d.x * 1000;},
				y: function(d) {return d.y;},
				useInteractiveGuideline: true,
				interactiveLayer: {
					tooltip: {
						valueFormatter: function(d) {
							return numberShorten(d, 4);
						},
						headerFormatter: function(d) {
							return d3.time.format('%Y.%m.%d %H:%M')(new Date(d));
						},
					},
				},
				dispatch: {
					stateChange: function(e) {},
					changeState: function(e) {},
					tooltipShow: function(e) {},
					tooltipHide: function(e) {},
				},
				xAxis: {
					axisLabel: 'Time',
					showMaxMin: false,
					ticks: function(start, stop) {
						return d3.time.days(start, stop, 7);
					},
					tickFormat: function(d) {
						return d3.time.format('%m.%d')(new Date(d));
					},
				},
				yAxis: {
					axisLabel: 'Hashrate (Hash/s)',
					showMaxMin: false,
					tickFormat: function(d) {
						return numberShorten(d, 2);
					},
					axisLabelDistance: -10,
				},
				callback: function(chart) {},
				forceY: [0],
				xScale: d3.time.scale(),
			},
			title: {
				enable: false,
			},
		};


		getLastTime();

		function getLastTime() {
			return $http.get('/api/lasttime')
				.then(function(response) {
					self.status.main.time = response.data.result;
				}, function(errResponse) {
					'Error fetching LastTime';
				});
		}

		function numberShorten(num, precise) {
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
					if (num >= p.base * 100)
						return (num / p.base / 10).toFixed(precise - 2) + ' ' + p.prefix;
					else if (num >= p.base * 10)
						return (num / p.base / 10).toFixed(precise - 1) + ' ' + p.prefix;
					else
						return (num / p.base / 10).toFixed(precise) + ' ' + p.prefix;
				}
			}
			return num;
		}

	}
})();
