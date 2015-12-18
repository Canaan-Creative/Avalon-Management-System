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

		getLastTime();

		function getLastTime() {
			return $http.get('/api/lasttime')
				.then(function(response) {
					self.status.main.time = response.data.result;
				}, function(errResponse) {
					'Error fetching LastTime';
				});
		}
	}
})();
