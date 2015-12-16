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
		self.getConfig = getConfig;
		self.getHashrate = getHashrate;
		self.setLED = setLED;

		function getNodes(){
			return $http.get('/api/nodes').then(
				function(response) {
					self.data.nodes = response.data.result;
				}, function(errResponse) {
					self.data.nodes = null;
					console.error('Error fetching nodes');
				});
		}

		function getStatus(name, time, ip, port) {
			return $http.get(
					'/api/status/' + name + '/' + time + '/' + ip + '/' + port
				).then(function(response) {
					self.data[name] = response.data.result;
				}, function(errResponse) {
					self.data[name] = null;
					console.error(
						'Error fetching ' + name + ' of ' +
							ip + ':' + port + ' at ' + time
					);
				});
		}

		function getHashrate() {
			return $http.get('/api/hashrate')
				.then(function(response) {
					self.data.hashrate = response.data.result;
				}, function(errResponse) {
					self.data.hashrate = null;
					console.error('Error fetching hashrate');
				});
		}

		function getConfig(ip, port) {
			return $http.get(
					'/api/config/' + ip + '/' + port
				).then(function(response) {
					self.data.config = response.data.result;
					if (self.data.config.voltage_adjust === '--avalon4-automatic-voltage')
						self.data.config.autoAdjust = true;
					else
						self.data.config.autoAdjust = false;
				}, function(errResponse) {
					self.data.config = null;
					console.error(
						'Error fetching config of ' + ip + ':' + port
					);
				});
		}

		function setLED(data) {
			return $http.post('/api/led', data);
		}
	}
})();
