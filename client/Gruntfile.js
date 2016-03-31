module.exports = function(grunt) {
'use strict';

	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),

		bower: {
			install: {
				options: {
					install: true,
					copy: false
				}
			}
		},

		copy: {
			main: {
				files: [{
					expand: true,
					flatten: true,
					src: [
						'bower_components/**/*.min.js',
						'!bower_components/angular-material/angular-material.layouts.min.js',
						'!bower_components/angular-messages/*.js',
						'!bower_components/angular-material/modules/**/*.js'
					],
					dest: 'lib/js/'
				}, {
					expand: true,
					flatten: true,
					src: [
						'bower_components/**/*.min.css',
						'!bower_components/angular-material/angular-material.layouts.min.css',
						'!bower_components/angular-material/modules/**/*.css'
					],
					dest: 'lib/css/'
				}]
			},
			debug: {
				files: [{
					expand: true,
					flatten: true,
					src: ['tmp/ams.js'],
					dest: 'lib/js/'
				}, {
					expand: true,
					flatten: true,
					src: ['app/styles/ams.css'],
					dest: 'lib/css/'
				}]
			}
		},

		uglify: {
			build: {
				files: {
					'lib/js/ams.min.js': ['tmp/ams.js']
				},
				options:{
					mangle: false
				}
			}
		},

		cssmin: {
			build: {
				files: {
					'lib/css/ams.min.css': 'app/styles/ams.css'
				}
			}
		},

		usebanner: {
			build: {
				options: {
					position: 'top',
					banner:
						'/*\n' +
						' AMS Client\n' +
						' (c) 2015-2016  DING Changchang (of Canaan Creative)\n' +
						' License: GPLv3\n' +
						'*/',
				},
				files: {
					src: ['lib/js/ams.min.js', 'lib/css/ams.min.css']
				}
			}
		},

		html2js: {
			options: {
				base: '',
				module: 'templates',
				singleModule: true,
				useStrict: true,
				htmlmin: {
					collapseBooleanAttributes: true,
					collapseWhitespace: true,
					removeAttributeQuotes: true,
					removeComments: true,
					removeEmptyAttributes: true,
					removeRedundantAttributes: true,
					removeScriptTypeAttributes: true,
					removeStyleLinkTypeAttributes: true
				}
			},
			build: {
				src: ['app/**/*.html'],
				dest: 'tmp/templates.js'
			}
		},

		clean: {
			temp: {
				src: ['tmp']
			},
			lib: {
				src: ['lib']
			},
			dist: {
				src: ['dist']
			},
			bower: {
				src: ['bower_components']
			},
			npm: {
				src: ['node_modules']
			},
			ams: {
				src: ['lib/js/ams.js', 'lib/js/ams.min.js', 'lib/css/ams.css', 'lib/css/ams.min.css']
			}
		},

		concat: {
			options: {
				separator: ';'
			},
			build: {
				src: [
					'app/app.module.js',
					'app/app.config.js',
					'app/app.state.js',
					'app/**/*.js',
					'tmp/*.js'
				],
				dest: 'tmp/ams.js'
			}
		},

		jshint: {
			all: ['Gruntfile.js', 'app/*.js', 'app/**/*.js']
		},

		compress: {
			main: {
				options: {
					archive: 'dist/ams-client-<%= pkg.version %>.tar.gz'
				},
				files: [
					{src: ['./index.html', './lib/**', './asset/**'], dest: 'ams-client/'}
				],
			}
		}
	});

	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-concat');
	grunt.loadNpmTasks('grunt-contrib-uglify');
	grunt.loadNpmTasks('grunt-contrib-cssmin');
	grunt.loadNpmTasks('grunt-contrib-copy');
	grunt.loadNpmTasks('grunt-contrib-compress');
	grunt.loadNpmTasks('grunt-html2js');
	grunt.loadNpmTasks('grunt-bower-task');
	grunt.loadNpmTasks('grunt-banner');

	grunt.registerTask('prereq', [
		'clean:temp',
		'clean:lib',
		'bower',
		'copy',
		'clean:temp',
	]);
	grunt.registerTask('build', [
		'jshint',
		'clean:ams',
		'html2js:build',
		'concat:build',
		'uglify:build',
		'cssmin:build',
		'usebanner:build',
		'clean:temp',
		'clean:dist',
		'compress',
	]);
	grunt.registerTask('debug', [
		'jshint',
		'clean:ams',
		'html2js:build',
		'concat:build',
		'copy:debug',
		'clean:temp',
		'clean:dist',
	]);
	grunt.registerTask('distclean', [
		'clean:npm',
		'clean:bower',
		'clean:lib',
		'clean:temp',
		'clean:dist',
	]);
};
