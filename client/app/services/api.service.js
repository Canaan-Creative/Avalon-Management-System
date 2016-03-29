/*
 Copyright (C) 2015-2016  DING Changchang (of Canaan Creative)

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
		.service('APIService', APIService);

	APIService.$inject = ['$http'];

	function APIService($http) {
		/* jshint validthis: true */
		var self = this;

		self.data = {};
		self.getShortlog = getShortlog;
		self.getNodes = getNodes;
		self.getStatus = getStatus;
		self.getSummary = getSummary;
		self.getFarmMap = getFarmMap;
		self.getIssue = getIssue;
		self.getConfig = getConfig;
		self.getAliverate = getAliverate;
		self.getFarmHashrate = getFarmHashrate;
		self.getNodeHashrate = getNodeHashrate;
		self.setLED = setLED;
		self.updateNodes = updateNodes;

		var getStatusLock = {
			summary: {number: 0, id: 0},
			pool: {number: 0, id: 0},
			device: {number: 0, id: 0},
			module: {number: 0, id: 0},
		};
		var getConfigLock = {
			number: 0,
			id: 0
		};

		function getShortlog() {
			return $http.get('/api/shortlog').then(
				function(response) {
					self.data.shortlog = response.data.result;
				}, function(errResponse) {
					self.data.shortlog = null;
					console.error('Error fetching nodes');
				});
		}

		function getNodes() {
			return $http.get('/api/nodes').then(
				function(response) {
					self.data.nodes = response.data.result;
				}, function(errResponse) {
					self.data.nodes = null;
					console.error('Error fetching nodes');
				});
		}

		function getStatus(name, time, ip, port) {
			var id = getStatusLock[name].id++;
			getStatusLock[name].number++;
			return $http.get(
					'/api/status/' + name + '/' + time + '/' + ip + '/' + port
				).then(function(response) {
					if (id === getStatusLock[name].id - 1)
						self.data[name] = response.data.result;
					if (--getStatusLock[name].number === 0)
						getStatusLock[name].id = 0;
				}, function(errResponse) {
					console.error(
						'Error fetching ' + name + ' of ' +
							ip + ':' + port + ' at ' + time
					);
					if (id === getStatusLock[name].id - 1)
						self.data[name] = null;
					if (--getStatusLock[name].number === 0)
						getStatusLock[name].id = 0;
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

		function getFarmMap(time) {
			return $http.get('/api/farmmap/' + time).then(
				function(response) {
					self.data.farmMap = response.data.result;
				}, function(errResponse) {
					self.data.farmMap = null;
					console.error('Error fetching farmmap');
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

		function updateNodes(nodes) {
			return $http.post('/api/update_nodes', {nodes: nodes});
		}
	}
})();
