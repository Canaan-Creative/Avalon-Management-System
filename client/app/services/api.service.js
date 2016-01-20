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
		self.getSummary = getSummary;
		self.getIssue = getIssue;
		self.getConfig = getConfig;
		self.getAliverate = getAliverate;
		self.getFarmHashrate = getFarmHashrate;
		self.getNodeHashrate = getNodeHashrate;
		self.setLED = setLED;

		var getStatusLock = {
			number: 0,
			id: 0
		};
		var getConfigLock = {
			number: 0,
			id: 0
		};

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
			var id = getStatusLock.id++;
			getStatusLock.number++;
			return $http.get(
					'/api/status/' + name + '/' + time + '/' + ip + '/' + port
				).then(function(response) {
					if (id === getStatusLock.id - 1)
						self.data[name] = response.data.result;
					if (--getStatusLock.number === 0)
						getStatusLock.id = 0;
				}, function(errResponse) {
					console.error(
						'Error fetching ' + name + ' of ' +
							ip + ':' + port + ' at ' + time
					);
					if (id === getStatusLock.id - 1)
						self.data[name] = null;
					if (--getStatusLock.number === 0)
						getStatusLock.id = 0;
				});
		}

		function getSummary(time) {
			return $http.get('/api/summary/' + time).then(
				function(response) {
					self.data.summary = response.data.result;
				}, function(errResponse) {
					self.data.summary = null;
					console.error('Error fetching summary');
				});
		}

		function getIssue(time) {
			return $http.get('/api/issue/' + time).then(
				function(response) {
					self.data.issue = response.data.result;
				}, function(errResponse) {
					self.data.issue = null;
					console.error('Error fetching issue');
				});
		}

		function getAliverate(start, end) {
			return $http.post('/api/aliverate', {
					start: start,
					end: end,
				}).then(function(response) {
					self.data.aliverate = response.data.result;
					self.data.aliverate[0].type = 'line';
					self.data.aliverate[0].yAxis = 1;
					self.data.aliverate[1].type = 'line';
					self.data.aliverate[1].yAxis = 2;
				}, function(errResponse) {
					self.data.aliverate = null;
					console.error('Error fetching hashrate');
				});
		}

		function getFarmHashrate(start, end) {
			return $http.post('/api/hashrate', {
					scope: 'farm',
					start: start,
					end: end,
				}).then(function(response) {
					self.data.farmHashrate = response.data.result;
				}, function(errResponse) {
					self.data.farmHashrate = null;
					console.error('Error fetching aliverate');
				});
		}

		function getNodeHashrate(ip, port, start, end) {
			return $http.post('/api/hashrate', {
					scope: 'node',
					ip: ip,
					port: port,
					start: start,
					end: end,
				}).then(function(response) {
					self.data.nodeHashrate = response.data.result;
				}, function(errResponse) {
					self.data.nodeHashrate = null;
					console.error('Error fetching hashrate');
				});
		}

		function getConfig(ip, port) {
			var id = getConfigLock.id++;
			getConfigLock.number++;
			return $http.get(
					'/api/config/' + ip + '/' + port
				).then(function(response) {
					if (id == getConfigLock.id - 1) {
						self.data.config = response.data.result;
						if (self.data.config.voltage_adjust === '--avalon4-automatic-voltage')
							self.data.config.autoAdjust = true;
						else
							self.data.config.autoAdjust = false;
					}
					if (--getConfigLock.number === 0)
						getConfigLock.id = 0;
				}, function(errResponse) {
					console.error(
						'Error fetching config of ' + ip + ':' + port
					);
					if (id === getConfigLock.id - 1)
						self.data.config = null;
					if (--getConfigLock.number === 0)
						getConfigLock.id = 0;
				});
		}

		function setLED(data) {
			return $http.post('/api/led', data);
		}
	}
})();
