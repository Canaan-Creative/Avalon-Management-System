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

		exec: {
			nvd3: {
				/*jshint multistr: true */
				cmd: '\
mkdir -p tmp && \
cd tmp && \
git clone https://github.com/novus/nvd3 && \
cd nvd3 && \
patch -p1 < ../../patches/nvd3-interactive-tooltip-valueFomatter.patch && \
npm install && \
grunt production'
			}
		},

		copy: {
			main: {
				files: [{
					expand: true,
					flatten: true,
					src: [
						'bower_components/**/*.min.js',
						'tmp/nvd3/build/nv.d3.min.js',
						'!bower_components/nvd3/**/*.js',
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
						'tmp/nvd3/build/nv.d3.min.css',
						'!bower_components/nvd3/**/*.css',
						'!bower_components/angular-material/angular-material.layouts.min.css',
						'!bower_components/angular-material/modules/**/*.css'
					],
					dest: 'lib/css/'
				}]
			}
		},

		uglify: {
			build: {
				files: {
					'dist/ams.min.js': ['dist/ams.js']
				},
				options:{
					mangle: false
				}
			}
		},

		cssmin: {
			build: {
				files: {
					'dist/ams.min.css': 'app/styles/ams.css'
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
					src: ['dist/ams.min.js', 'dist/ams.min.css']
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
			full: {
				src: ['dist/ams.js']
			},
			lib: {
				src: ['lib']
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
					'app/app.route.js',
					'app/**/*.js',
					'tmp/*.js'
				],
				dest: 'dist/ams.js'
			}
		},

		jshint: {
			all: ['Gruntfile.js', 'app/*.js', 'app/**/*.js']
		}
	});

	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-concat');
	grunt.loadNpmTasks('grunt-contrib-uglify');
	grunt.loadNpmTasks('grunt-contrib-cssmin');
	grunt.loadNpmTasks('grunt-contrib-copy');
	grunt.loadNpmTasks('grunt-html2js');
	grunt.loadNpmTasks('grunt-bower-task');
	grunt.loadNpmTasks('grunt-exec');
	grunt.loadNpmTasks('grunt-banner');

	grunt.registerTask('prereq', [
		'clean:temp',
		'clean:lib',
		'bower',
		'exec:nvd3',
		'copy',
		'clean:temp',
	]);
	grunt.registerTask('build', [
		'jshint',
		'html2js:build',
		'concat:build',
		'uglify:build',
		'cssmin:build',
		'usebanner:build',
		'clean:temp',
		'clean:full'
	]);
};
