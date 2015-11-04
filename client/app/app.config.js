(function (){
	'use strict';

	angular
		.module('ams')
		.config(config);

	config.$inject = ['$mdThemingProvider'];

	function config($mdThemingProvider) {
		$mdThemingProvider
			.theme('default')
			.primaryPalette('blue')
			.accentPalette('light-blue')
			.warnPalette('red')
			.backgroundPalette('grey');
	}
})();
