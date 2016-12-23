Build
-----
* Install required packages:

	```
	sudo apt-get install simple-cdd
	sudo apt-get install npm
	sudo ln -s /usr/bin/nodejs /usr/bin/node
	sudo npm install -g grunt-cli jshint
	```

* Create `private.conf`:

	Special characters in root and ams password should be backslash-escaped.

	MySQL root password should only contain alphabets and numbers.

* Copy customed `ams.conf` to `extras/root/etc/`

* Build:

	```
	./build
	```
