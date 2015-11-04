(function() {
	'use strict';

	angular
		.module('ams')
		.service('APIService', APIService);

	APIService.$inject = ['$http'];

	function APIService($http) {
		/* jshint validthis: true */
		var self = this;

		self.data = {};
		self.getNodes = getNodes;
		self.getStatus = getStatus;

		function getNodes(){
			return $http.get('/api/nodes').then(
				function(response) {
					self.data.nodes = response.data.result;
				}, function(errResponse) {
					console.error('Error fetching nodes');
				});
		}

		function getStatus(name, time, ip, port) {
			return $http.get(
					'/api/status/' + name + '/' + time + '/' + ip + '/' + port
				).then(function(response) {
					self.data[name] = response.data.result;
				}, function(errResponse) {
					console.error(
						'Error fetching ' + name + ' of ' +
							ip + ':' + port + ' at ' + time
					);
				});
		}
	}
})();
