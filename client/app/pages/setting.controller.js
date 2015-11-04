(function() {
	'use strict';

	angular
		.module('ams')
		.controller('SettingController', SettingController);

	SettingController.$inject = ['ShareService', 'APIService'];

	function SettingController(share, api) {
		/* jshint validthis: true */
		var vm = this;

		vm.status = share.status.setting;
		vm.data = api.data;

		share.status.main.title = "Setting";
		share.status.main.subTitle = false;
	}
})();
